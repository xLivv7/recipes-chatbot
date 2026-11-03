"""Prepare, execute and summarize the frozen T009 development campaign."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openai import OpenAI
from core.llm_tools import RECIPE_TOOLS
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
from core.tool_call_validation import parse_recipe_tool_arguments, ToolArgumentsError
from evals.run_llm_eval import load_cases, score_case
from evals.run_routing_eval import evaluate_case, summarize

VARIANTS = ('V0', 'V1', 'V2')
DATASETS = ('evals/intent_cases.json', 'evals/routing_cases.json', 'evals/application_routing_cases.json')
ACC11_IDS = {'routing_001', 'routing_002', 'routing_003', 'routing_004', 'routing_006',
             'guard_001', 'guard_002', 'guard_003', 'guard_004'}
SOURCES = ('main.py', 'core/llm_tools.py', 'core/request_safety.py', 'core/tool_call_validation.py',
           'evals/run_llm_eval.py', 'evals/run_routing_eval.py', 'evals/run_routing_experiment.py',
           'specs/001-mvp-stabilization/spec.md', 'specs/001-mvp-stabilization/plan.md',
           'specs/001-mvp-stabilization/acceptance.md')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def schedule():
    return [(round_no + 1, variant, mode)
            for round_no in range(3)
            for variant in VARIANTS[round_no:] + VARIANTS[:round_no]
            for mode in ('raw', 'application')]


def load_development_cases():
    cases = [case for name in DATASETS for case in load_cases(ROOT / name)]
    if len(cases) != 76 or len({c['id'] for c in cases}) != 76:
        raise ValueError('T009 requires the fixed 76-case development dataset')
    return cases


def prepare(directory):
    directory.mkdir(parents=True, exist_ok=False)
    cases = load_development_cases()
    prompts = {v: (ROOT / 'evals/routing_prompts' / (v + '.txt')).read_text(encoding='utf-8') for v in VARIANTS}
    guard = lambda c: mentions_unsupported_allergy(c['user_message']) or mentions_unsupported_exclusion(c['user_message'])
    calls_per_round = {'raw': len(cases), 'application': sum(not guard(c) for c in cases)}
    # UTF-8 bytes are a conservative input-text token proxy, not a tokenizer.
    # Add 2k tokens per call for tool/chat serialization overhead, ignore caching.
    input_proxy = 0
    prompt_bytes = {}
    for variant, prompt in prompts.items():
        (directory / (variant + '.txt')).write_text(prompt, encoding='utf-8')
        prompt_bytes[variant] = len(prompt.encode('utf-8'))
        for mode in ('raw', 'application'):
            for case in cases:
                if mode == 'application' and guard(case):
                    continue
                request = dict(messages=[dict(role='system', content=prompt),
                                         dict(role='user', content=case['user_message'])], tools=RECIPE_TOOLS)
                input_proxy += 3 * (len(json.dumps(request, ensure_ascii=False).encode('utf-8')) + 2000)
    calls = 3 * len(VARIANTS) * sum(calls_per_round.values())
    manifest = dict(schema_version=1, prepared_at_utc=now(),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip(),
        files={name: digest(ROOT / name) for name in SOURCES + DATASETS},
        prompt_hashes={v: digest(directory / (v + '.txt')) for v in VARIANTS},
        tool_schema=RECIPE_TOOLS, cases=cases, schedule=schedule(),
        configuration=dict(model='gpt-4o-mini', temperature=0.1, tool_choice='auto',
                           parallel_tool_calls=False, brand_name='Winiary', timeout_seconds=30, max_retries=2),
        environment=dict(python=sys.version, packages={n: importlib.metadata.version(n)
                         for n in ('openai', 'SQLAlchemy', 'pydantic', 'httpx', 'python-dotenv')}),
        plan=dict(evaluations=1368, sdk_calls=calls, calls_per_round=calls_per_round),
        cost_estimate=dict(pricing_source='https://developers.openai.com/api/docs/models/gpt-4o-mini',
            checked_on='2026-11-03', usd_per_million_input=.15, usd_per_million_output=.60,
            method='UTF8 bytes + 2000 input proxy per call; no cache discount; excludes retries/taxes',
            prompt_bytes=prompt_bytes, input_token_proxy=input_proxy,
            usd_proxy_with_500_output_tokens=round(input_proxy * .15 / 1e6 + calls * 500 * .60 / 1e6, 4),
            usd_proxy_with_max_output=round(input_proxy * .15 / 1e6 + calls * 16384 * .60 / 1e6, 4)),
        status='prepared', actual_api_calls=0)
    write_json(directory / 'manifest.json', manifest)
    return manifest


def validate_frozen(directory, manifest):
    if manifest['cases'] != load_development_cases() or manifest['schedule'] != [list(item) for item in schedule()]:
        raise ValueError('Frozen cases or schedule changed')
    expected_config = dict(model='gpt-4o-mini', temperature=0.1, tool_choice='auto',
                           parallel_tool_calls=False, brand_name='Winiary', timeout_seconds=30, max_retries=2)
    if manifest['configuration'] != expected_config:
        raise ValueError('Frozen configuration changed')
    for name, expected in manifest['files'].items():
        if digest(ROOT / name) != expected:
            raise ValueError('Frozen input changed: ' + name)
    for variant, expected in manifest['prompt_hashes'].items():
        if digest(directory / (variant + '.txt')) != expected:
            raise ValueError('Frozen prompt changed: ' + variant)
        if digest(ROOT / 'evals/routing_prompts' / (variant + '.txt')) != expected:
            raise ValueError('Versioned prompt changed: ' + variant)
    if manifest['tool_schema'] != RECIPE_TOOLS:
        raise ValueError('Tool schema changed')


def content_json_matches(row):
    if row['expected_action'] != 'tool' or row['model_action'] != 'no_tool':
        return False
    text = (row.get('no_tool_content') or '').strip()
    match = re.fullmatch(r'```(?:json)?\s*\n?(.*?)\n?```', text, flags=re.DOTALL)
    if match:
        text = match[1].strip()
    try:
        return score_case(row['expected'], parse_recipe_tool_arguments(text))['passed']
    except ToolArgumentsError:
        return False


def group_summary(rows):
    supported = [r for r in rows if r['expected_action'] == 'tool']
    unsupported = [r for r in rows if r['expected_action'] == 'no_tool']
    boundary = [r for r in rows if r['id'] in ACC11_IDS]
    def score(group):
        return dict(passed=sum(r['passed'] for r in group), total=len(group))
    summary = summarize(rows)
    summary.update(supported=score(supported), no_tool=score(unsupported),
        acc11=dict(passed=sum(r['backend_calls'] == 0 and r['passed'] for r in boundary), total=len(boundary)),
        supported_stable=summarize(supported)['stable_cases'],
        false_positive_guards=sum(r['guard'] is not None and r['expected_action'] == 'tool' for r in rows),
        correct_guards=sum(r['guard'] is not None and r['expected_action'] == 'no_tool' for r in rows),
        correct_json_in_wrong_channel=sum(content_json_matches(r) for r in rows),
        usage={k: sum((r.get('usage') or {}).get(k) or 0 for r in rows)
               for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')})
    return summary


def aggregate(directory, manifest):
    all_rows = []
    expected_ids = {c['id'] for c in manifest['cases']}
    labels = {c['id']: c for c in manifest['cases']}
    models = set()
    for round_no, variant, mode in manifest['schedule']:
        path = directory / f'round{round_no}_{variant}_{mode}.json'
        report = json.loads(path.read_text(encoding='utf-8'))
        if not report['complete'] or report['prompt_sha256'] != manifest['prompt_hashes'][variant]:
            raise ValueError('Incomplete group or changed prompt')
        rows = report['results']
        if len(rows) != len(expected_ids) or {r['id'] for r in rows} != expected_ids:
            raise ValueError('Missing or duplicate cases')
        if (report['round'], report['variant'], report['mode']) != (round_no, variant, mode):
            raise ValueError('Wrong group identity')
        if any(r['attempt'] != round_no for r in rows):
            raise ValueError('Wrong global round number')
        if any(r['expected_action'] != labels[r['id']].get('expected_action', 'tool')
               or r['expected'] != labels[r['id']].get('expected') for r in rows):
            raise ValueError('Report labels changed')
        all_rows.extend(dict(r, variant=variant, mode=mode) for r in rows)
        models.update(r['response_model'] for r in rows if r['response_model'])
    comparisons = {}
    for variant in VARIANTS:
        comparisons[variant] = {mode: group_summary([r for r in all_rows if r['variant'] == variant and r['mode'] == mode])
                                for mode in ('raw', 'application')}
    valid = (len(models) == 1 and not any(r['failure_stage'] == 'api' for r in all_rows)
             and all(r['response_model'] for r in all_rows if r['api_calls']))
    eligible = []
    for variant in VARIANTS:
        summary = comparisons[variant]['application']
        qualifies = (valid and summary['passed'] * 10 >= summary['total'] * 9
                     and summary['supported']['passed'] * 10 >= summary['supported']['total'] * 9
                     and summary['stable_cases'] * 100 >= summary['case_count'] * 85
                     and summary['acc11'] == dict(passed=27, total=27))
        comparisons[variant]['qualifies_on_regression'] = qualifies
        if qualifies:
            eligible.append(variant)
    winner = max(eligible, key=lambda v: (comparisons[v]['application']['passed'],
        comparisons[v]['application']['stable_cases'], -VARIANTS.index(v))) if eligible else None
    changes = {}
    baseline = comparisons['V0']['application']['case_stability']
    for variant in ('V1', 'V2'):
        candidate = comparisons[variant]['application']['case_stability']
        changes[variant] = {case_id: dict(baseline=baseline[case_id], candidate=candidate[case_id])
                           for case_id in baseline if baseline[case_id] != candidate[case_id]}
    return dict(complete=True, valid_comparison=valid, resolved_models=sorted(models),
                variants=comparisons, winner=winner, keep_active_prompt='V0',
                per_case_changes=changes, total_evaluations=len(all_rows),
                api_calls=sum(r['api_calls'] for r in all_rows),
                usage={k: sum((r.get('usage') or {}).get(k) or 0 for r in all_rows)
                       for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')})


def execute(directory):
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    validate_frozen(directory, manifest)
    if manifest['status'] != 'prepared' or any(directory.glob('round*.json')):
        raise ValueError('Campaign already started; use a new campaign, do not resume selectively')
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), timeout=30, max_retries=2)
    manifest.update(status='running', started_at_utc=now())
    write_json(directory / 'manifest.json', manifest)
    try:
        for round_no, variant, mode in manifest['schedule']:
            prompt = (directory / (variant + '.txt')).read_text(encoding='utf-8')
            path = directory / f'round{round_no}_{variant}_{mode}.json'
            report = dict(round=round_no, variant=variant, mode=mode, complete=False,
                          prompt_sha256=manifest['prompt_hashes'][variant], results=[])
            write_json(path, report)
            for index, case in enumerate(manifest['cases'], 1):
                row = dict(evaluate_case(case, mode, client, system_prompt=prompt), attempt=round_no)
                report['results'].append(row)
                manifest['actual_api_calls'] += row['api_calls']
                write_json(path, report)
                if index % 10 == 0 or index == len(manifest['cases']):
                    print(f'round={round_no} {variant}/{mode}: {index}/{len(manifest["cases"])}', flush=True)
                if row['failure_stage'] == 'api':
                    raise RuntimeError('API failure: ' + row.get('error', 'unknown'))
            report.update(complete=True, summary=group_summary(report['results']), completed_at_utc=now())
            write_json(path, report)
        summary = aggregate(directory, manifest)
        write_json(directory / 'comparison.json', summary)
        manifest.update(status='complete', completed_at_utc=now())
    except Exception as error:
        manifest.update(status='incomplete', stopped_at_utc=now(), stop_reason=str(error)
                        if str(error).startswith('API failure:') else type(error).__name__)
        raise
    finally:
        write_json(directory / 'manifest.json', manifest)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--dry-run', action='store_true', help='Freeze inputs, estimate calls/cost; no API')
    modes.add_argument('--execute', action='store_true', help='Execute an already prepared campaign')
    args = parser.parse_args()
    report = prepare(args.output) if args.dry_run else execute(args.output)
    print(json.dumps({k: v for k, v in report.items() if k in
        ('plan', 'cost_estimate', 'valid_comparison', 'winner', 'api_calls', 'usage')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
