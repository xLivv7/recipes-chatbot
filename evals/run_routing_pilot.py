"""Small frozen raw-only V0/V2 pilot with bounded output and estimated spend."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openai import OpenAI
from core.llm_tools import RECIPE_TOOLS
from evals.run_llm_eval import load_cases
from evals.run_routing_eval import evaluate_case
from evals.run_routing_experiment import (SOURCES, DATASETS, digest, write_json, now, group_summary)

VARIANTS = ('V0', 'V2')
CASES = 'evals/routing_pilot_cases.json'
BUDGET = .50
OUTPUT_LIMIT = 512


def cost_reservation(kwargs):
    # Conservative proxy, not an exact tokenizer or a provider billing limit.
    input_proxy = len(json.dumps(kwargs, ensure_ascii=False).encode('utf-8')) + 2000
    return input_proxy * .15 / 1e6 + OUTPUT_LIMIT * .60 / 1e6


def request(prompt, case):
    return dict(model='gpt-4o-mini', messages=[dict(role='system', content=prompt),
        dict(role='user', content=case['user_message'])], tools=RECIPE_TOOLS,
        tool_choice='auto', parallel_tool_calls=False, temperature=.1, max_completion_tokens=OUTPUT_LIMIT)


def prepare(directory):
    cases = load_cases(ROOT / CASES)
    if len(cases) != 20 or sum(c.get('expected_action', 'tool') == 'tool' for c in cases) != 14:
        raise ValueError('Pilot requires 14 supported and 6 no-tool cases')
    source_cases = {c['id']: c for name in DATASETS for c in load_cases(ROOT / name)}
    if any(case != source_cases.get(case['id']) for case in cases):
        raise ValueError('Pilot labels differ from development inputs')
    directory.mkdir(parents=True, exist_ok=False)
    prompts = {v: (ROOT / 'evals/routing_prompts' / (v + '.txt')).read_text(encoding='utf-8') for v in VARIANTS}
    for v, text in prompts.items():
        (directory / (v + '.txt')).write_text(text, encoding='utf-8')
    reservation = 3 * sum(cost_reservation(request(prompt, case)) for prompt in prompts.values() for case in cases)
    if reservation > BUDGET:
        raise ValueError('Estimated full pilot exceeds budget')
    files = tuple(SOURCES) + tuple(DATASETS) + (CASES, 'evals/run_routing_pilot.py',
        'evals/routing_prompts/V0.txt', 'evals/routing_prompts/V2.txt')
    manifest = dict(prepared_at_utc=now(), status='prepared',
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip(),
        files={p: digest(ROOT / p) for p in files}, prompts=prompts,
        prompt_hashes={v: digest(directory / (v + '.txt')) for v in VARIANTS}, cases=cases,
        configuration=dict(model='gpt-4o-mini', temperature=.1, tool_choice='auto',
            parallel_tool_calls=False, max_completion_tokens=OUTPUT_LIMIT, max_retries=0, timeout=30,
            endpoint='https://api.openai.com/v1', mode='raw'),
        schedule=[(r, v) for r, order in [(1, ('V0','V2')), (2, ('V2','V0')), (3, ('V0','V2'))] for v in order],
        planned_calls=120, actual_calls=0, reserved_usd=0,
        budget_guard_usd=BUDGET, estimated_max_output_cost_usd=reservation,
        pricing_source='https://developers.openai.com/api/docs/models/gpt-4o-mini', pricing_checked_on='2026-11-03',
        cost_limit_note='Local conservative reservation guard, excludes taxes and other account usage; not a billing guarantee')
    write_json(directory / 'manifest.json', manifest)
    return manifest


def summarize_pilot(rows):
    if len(rows) != 120 or len({(r['attempt'], r['variant'], r['id']) for r in rows}) != 120:
        raise ValueError('Incomplete or duplicate pilot results')
    expected_ids = {c['id'] for c in load_cases(ROOT / CASES)}
    if any({r['id'] for r in rows if r['attempt'] == n and r['variant'] == v} != expected_ids
           for n in (1, 2, 3) for v in VARIANTS):
        raise ValueError('Wrong cases in round')
    summaries = {v: group_summary([r for r in rows if r['variant'] == v]) for v in VARIANTS}
    models = {r['response_model'] for r in rows}
    valid = None not in models and len(models) == 1 and not any(r['failure_stage'] == 'api' for r in rows)
    eligible = [v for v in VARIANTS if valid and summaries[v]['no_tool'] == dict(passed=18, total=18)]
    winner = max(eligible, key=lambda v: (summaries[v]['passed'], summaries[v]['stable_cases'], v == 'V0')) if eligible else None
    return dict(complete=True, valid_comparison=valid, variants=summaries, candidate=winner,
        resolved_models=sorted(m for m in models if m), active_prompt_changed=False,
        scope='targeted_development_diagnostic_not_MVP_acceptance',
        truncated_responses=sum(r.get('finish_reason') == 'length' for r in rows))


class BudgetedClient:
    def __init__(self, client, manifest, directory):
        self.client, self.manifest, self.directory = client, manifest, directory
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        kwargs['max_completion_tokens'] = OUTPUT_LIMIT
        reserved = cost_reservation(kwargs)
        if self.manifest['actual_calls'] >= 120 or self.manifest['reserved_usd'] + reserved > BUDGET:
            raise RuntimeError('Pilot reservation budget or call limit reached')
        self.manifest['actual_calls'] += 1
        self.manifest['reserved_usd'] += reserved
        # Persist reservation before any request, including failures and timeouts.
        write_json(self.directory / 'manifest.json', self.manifest)
        return self.client.chat.completions.create(**kwargs)


def execute(directory):
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'prepared' or (directory / 'results.json').exists():
        raise ValueError('Pilot already started; do not selectively resume')
    if manifest['cases'] != load_cases(ROOT / CASES):
        raise ValueError('Manifest cases changed')
    expected_schedule = [[r, v] for r, order in [(1, ('V0','V2')), (2, ('V2','V0')), (3, ('V0','V2'))] for v in order]
    if manifest['schedule'] != expected_schedule:
        raise ValueError('Manifest schedule changed')
    for path, expected in manifest['files'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Frozen input changed: ' + path)
    for variant in VARIANTS:
        if digest(directory / (variant + '.txt')) != manifest['prompt_hashes'][variant]:
            raise ValueError('Frozen prompt changed')
        if (directory / (variant + '.txt')).read_text(encoding='utf-8') != manifest['prompts'][variant]:
            raise ValueError('Manifest prompt differs')
    if manifest['budget_guard_usd'] != BUDGET or manifest['planned_calls'] != 120:
        raise ValueError('Pilot limits changed')
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), base_url='https://api.openai.com/v1',
                    max_retries=0, timeout=30)
    budgeted = BudgetedClient(client, manifest, directory)
    manifest.update(status='running', started_at_utc=now())
    rows = []
    try:
        for round_no, variant in manifest['schedule']:
            for index, case in enumerate(manifest['cases'], 1):
                row = dict(evaluate_case(case, 'raw', budgeted, system_prompt=manifest['prompts'][variant]),
                           variant=variant, attempt=round_no)
                if row['finish_reason'] == 'length':
                    row.update(passed=False, failure_stage='completion_limit')
                rows.append(row)
                write_json(directory / 'results.json', dict(complete=False, results=rows))
                if index % 5 == 0:
                    print(f'round={round_no} {variant}: {index}/20; calls={manifest["actual_calls"]}', flush=True)
                if row['failure_stage'] == 'api':
                    raise RuntimeError('API failure: ' + row.get('error', 'unknown'))
        summary = summarize_pilot(rows)
        write_json(directory / 'comparison.json', summary)
        write_json(directory / 'results.json', dict(complete=True, results=rows))
        manifest.update(status='complete', completed_at_utc=now())
        return summary
    except Exception as error:
        manifest.update(status='incomplete', stop_reason=str(error)
                        if str(error).startswith('API failure:') else type(error).__name__)
        raise
    finally:
        write_json(directory / 'manifest.json', manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--dry-run', action='store_true')
    modes.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    report = prepare(args.output) if args.dry_run else execute(args.output)
    print(json.dumps({k:v for k,v in report.items() if k in
        ('planned_calls', 'budget_guard_usd', 'estimated_max_output_cost_usd', 'candidate', 'valid_comparison')}, indent=2))


if __name__ == '__main__':
    main()
