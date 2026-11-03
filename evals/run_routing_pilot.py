"""Frozen routing comparison profiles; preparation never changes the active prompt."""
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
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
from evals.run_llm_eval import load_cases
from evals.run_routing_eval import evaluate_case
from evals.run_routing_experiment import (SOURCES, DATASETS, digest, write_json, now, group_summary)

VARIANTS = ('V0', 'V2')
CASES = 'evals/routing_pilot_cases.json'
BUDGET = .50
OUTPUT_LIMIT = 512
PROFILES = {
    'pilot': dict(variants=('V0', 'V2'), modes=('raw',), calls=120),
    't014': dict(variants=('V0', 'V3'), modes=('raw', 'application'), calls=216),
    't015': dict(variants=('V0', 'V4'), modes=('raw', 'application'), calls=216),
}
T015_TARGETS = ('intent_004', 'intent_010', 'intent_032')


def campaign_schedule(profile):
    variants = PROFILES[profile]['variants']
    schedule = [(r, v, mode) for r, order in [(1, variants), (2, variants[::-1]), (3, variants)]
                for v in order for mode in PROFILES[profile]['modes']]
    return [item[:2] for item in schedule] if profile == 'pilot' else schedule


def configuration(profile):
    return dict(model='gpt-4o-mini', temperature=.1, tool_choice='auto',
        parallel_tool_calls=False, max_completion_tokens=OUTPUT_LIMIT, max_retries=0,
        timeout=30, endpoint='https://api.openai.com/v1', modes=list(PROFILES[profile]['modes']))


def cost_reservation(kwargs):
    # Conservative proxy, not an exact tokenizer or a provider billing limit.
    input_proxy = len(json.dumps(kwargs, ensure_ascii=False).encode('utf-8')) + 2000
    return input_proxy * .15 / 1e6 + OUTPUT_LIMIT * .60 / 1e6


def request(prompt, case):
    return dict(model='gpt-4o-mini', messages=[dict(role='system', content=prompt),
        dict(role='user', content=case['user_message'])], tools=RECIPE_TOOLS,
        tool_choice='auto', parallel_tool_calls=False, temperature=.1, max_completion_tokens=OUTPUT_LIMIT)


def prepare(directory, profile='pilot'):
    config = PROFILES[profile]
    cases = load_cases(ROOT / CASES)
    if len(cases) != 20 or sum(c.get('expected_action', 'tool') == 'tool' for c in cases) != 14:
        raise ValueError('Pilot requires 14 supported and 6 no-tool cases')
    source_cases = {c['id']: c for name in DATASETS for c in load_cases(ROOT / name)}
    if any(case != source_cases.get(case['id']) for case in cases):
        raise ValueError('Pilot labels differ from development inputs')
    directory.mkdir(parents=True, exist_ok=False)
    prompts = {v: (ROOT / 'evals/routing_prompts' / (v + '.txt')).read_text(encoding='utf-8') for v in config['variants']}
    for v, text in prompts.items():
        (directory / (v + '.txt')).write_text(text, encoding='utf-8')
    guarded = lambda c: mentions_unsupported_allergy(c['user_message']) or mentions_unsupported_exclusion(c['user_message'])
    planned_calls = 3 * sum(1 for _ in prompts for mode in config['modes'] for case in cases
                            if mode == 'raw' or not guarded(case))
    if planned_calls != config['calls']:
        raise ValueError('Profile call count differs from frozen scope')
    reservation = 3 * sum(cost_reservation(request(prompt, case)) for prompt in prompts.values()
                          for mode in config['modes'] for case in cases if mode == 'raw' or not guarded(case))
    if reservation > BUDGET:
        raise ValueError('Estimated full pilot exceeds budget')
    files = tuple(SOURCES) + tuple(DATASETS) + (CASES, 'evals/run_routing_pilot.py') + tuple(
        'evals/routing_prompts/' + v + '.txt' for v in config['variants'])
    if profile == 't014':
        files += ('evals/routing_prompts/V2.txt',)
    elif profile == 't015':
        files += ('evals/routing_prompts/V3.txt',)
    manifest = dict(prepared_at_utc=now(), status='prepared', profile=profile,
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip(),
        files={p: digest(ROOT / p) for p in files}, prompts=prompts,
        prompt_hashes={v: digest(directory / (v + '.txt')) for v in config['variants']}, cases=cases,
        configuration=configuration(profile), schedule=campaign_schedule(profile),
        planned_calls=planned_calls, planned_evaluations=20*3*len(prompts)*len(config['modes']),
        actual_calls=0, reserved_usd=0,
        budget_guard_usd=BUDGET, estimated_max_output_cost_usd=reservation,
        pricing_source='https://developers.openai.com/api/docs/models/gpt-4o-mini', pricing_checked_on='2026-11-03',
        cost_limit_note='Local conservative reservation guard, excludes taxes and other account usage; not a billing guarantee')
    if profile == 't015':
        manifest['selection_rule'] = 'T015-v1'
    write_json(directory / 'manifest.json', manifest)
    return manifest


def summarize_pilot(rows, profile='pilot'):
    if profile == 't014':
        return summarize_t014(rows)
    if profile == 't015':
        return summarize_t015(rows)
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


def pair_observations(rows, profile):
    ids = {c['id'] for c in load_cases(ROOT / CASES)}
    expected = {(r, v, mode, cid) for r, v, mode in campaign_schedule(profile) for cid in ids}
    observed = {(r['attempt'], r['variant'], r['mode'], r['id']) for r in rows}
    if len(rows) != 240 or observed != expected:
        raise ValueError('Incomplete, duplicate or unexpected pair results')
    labels = {c['id']: c for c in load_cases(ROOT / CASES)}
    if any(r['user_message'] != labels[r['id']]['user_message'] or
           r['expected'] != labels[r['id']].get('expected') or
           r['expected_action'] != labels[r['id']].get('expected_action', 'tool') for r in rows):
        raise ValueError('Result labels changed')
    summaries = {v: {mode: group_summary([r for r in rows if r['variant'] == v and r['mode'] == mode])
                    for mode in PROFILES[profile]['modes']} for v in PROFILES[profile]['variants']}
    models = {r['response_model'] for r in rows if r['api_calls']}
    valid = (len(models) == 1 and None not in models
             and not any(r['failure_stage'] == 'api' or r.get('finish_reason') == 'length' for r in rows))
    return summaries, models, valid


def summarize_t014(rows):
    summaries, models, valid = pair_observations(rows, 't014')
    baseline, candidate = summaries['V0'], summaries['V3']
    regressions = {mode: [cid for cid, value in baseline[mode]['case_stability'].items()
                  if value['passed'] == 3 and candidate[mode]['case_stability'][cid]['passed'] == 0]
                  for mode in PROFILES['t014']['modes']}
    qualifies = (valid and all(candidate[m]['no_tool'] == dict(passed=18,total=18) for m in ('raw','application'))
        and candidate['raw']['passed'] > baseline['raw']['passed']
        and candidate['raw']['stable_cases'] >= baseline['raw']['stable_cases']
        and candidate['application']['passed'] >= baseline['application']['passed']
        and not any(regressions.values()))
    return dict(complete=True, valid_comparison=valid, variants=summaries,
        candidate='V3' if qualifies else 'V0', candidate_qualifies=qualifies,
        new_persistent_regressions=regressions, resolved_models=sorted(m for m in models if m),
        active_prompt_changed=False, scope='development_iteration_not_MVP_acceptance',
        raw_failures_blocked_in_application=[dict(variant=r['variant'], attempt=r['attempt'], id=r['id'])
            for r in rows if r['mode']=='raw' and not r['passed'] and any(a['mode']=='application' and
                a['variant']==r['variant'] and a['attempt']==r['attempt'] and a['id']==r['id'] and
                a['guard'] is not None and a['passed'] for a in rows)])


def summarize_t015(rows):
    summaries, models, valid = pair_observations(rows, 't015')
    modes = PROFILES['t015']['modes']
    baseline, candidate = summaries['V0'], summaries['V4']
    regressions = {mode: [dict(id=cid, baseline_passed=value['passed'],
                              candidate_passed=candidate[mode]['case_stability'][cid]['passed'])
                         for cid, value in baseline[mode]['case_stability'].items()
                         if candidate[mode]['case_stability'][cid]['passed'] < value['passed']]
                   for mode in modes}
    target_results = {v: {mode: {cid: summaries[v][mode]['case_stability'][cid]
                                for cid in T015_TARGETS} for mode in modes}
                      for v in PROFILES['t015']['variants']}
    semantic_dispatches = {v: [dict(id=r['id'], attempt=r['attempt'], expected=r['expected'], actual=r['actual'])
                              for r in rows if r['variant'] == v and r['mode'] == 'application'
                              and r['expected_action'] == 'tool' and r['backend_calls'] > 0
                              and r['semantics_correct'] is False]
                           for v in PROFILES['t015']['variants']}
    app = candidate['application']
    conditions = dict(
        valid_comparison=valid,
        no_tool_all=all(candidate[m]['no_tool'] == dict(passed=18, total=18) for m in modes),
        targets_all=all(target_results['V4'][m][cid]['passed'] == 3 for m in modes for cid in T015_TARGETS),
        scores_improve=all(candidate[m]['passed'] > baseline[m]['passed'] for m in modes),
        stability_not_worse=all(candidate[m]['stable_cases'] >= baseline[m]['stable_cases'] for m in modes),
        application_accuracy=app['passed'] * 10 >= app['total'] * 9,
        supported_accuracy=app['supported']['passed'] * 10 >= app['supported']['total'] * 9,
        application_stability=app['stable_cases'] * 100 >= app['case_count'] * 85,
        no_case_regression=not any(regressions.values()),
        no_semantic_dispatch=not semantic_dispatches['V4'])
    qualifies = all(conditions.values())
    return dict(complete=True, valid_comparison=valid, variants=summaries,
        rule='T015-v1', candidate='V4' if qualifies else 'V0', candidate_qualifies=qualifies,
        conditions=conditions, case_regressions=regressions, target_cases=target_results,
        semantic_dispatch_errors=semantic_dispatches,
        resolved_models=sorted(m for m in models if m), active_prompt_changed=False,
        scope='development_iteration_not_MVP_acceptance',
        raw_failures_blocked_in_application=[dict(variant=r['variant'], attempt=r['attempt'], id=r['id'])
            for r in rows if r['mode'] == 'raw' and not r['passed'] and any(a['mode'] == 'application'
                and a['variant'] == r['variant'] and a['attempt'] == r['attempt'] and a['id'] == r['id']
                and a['guard'] is not None and a['passed'] for a in rows)])


class BudgetedClient:
    def __init__(self, client, manifest, directory):
        self.client, self.manifest, self.directory = client, manifest, directory
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        kwargs['max_completion_tokens'] = OUTPUT_LIMIT
        reserved = cost_reservation(kwargs)
        limit = PROFILES[self.manifest.get('profile', 'pilot')]['calls']
        if self.manifest['actual_calls'] >= limit or self.manifest['reserved_usd'] + reserved > BUDGET:
            raise RuntimeError('Pilot reservation budget or call limit reached')
        self.manifest['actual_calls'] += 1
        self.manifest['reserved_usd'] += reserved
        # Persist reservation before any request, including failures and timeouts.
        write_json(self.directory / 'manifest.json', self.manifest)
        return self.client.chat.completions.create(**kwargs)


def execute(directory):
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    profile = manifest.get('profile', 'pilot')
    config = PROFILES[profile]
    if manifest['status'] != 'prepared' or (directory / 'results.json').exists():
        raise ValueError('Pilot already started; do not selectively resume')
    if manifest['cases'] != load_cases(ROOT / CASES):
        raise ValueError('Manifest cases changed')
    expected_schedule = [list(item) for item in campaign_schedule(profile)]
    if manifest['schedule'] != expected_schedule:
        raise ValueError('Manifest schedule changed')
    for path, expected in manifest['files'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Frozen input changed: ' + path)
    if manifest['configuration'] != configuration(profile):
        raise ValueError('Manifest configuration changed')
    if profile == 't015' and manifest.get('selection_rule') != 'T015-v1':
        raise ValueError('Manifest selection rule changed')
    for variant in config['variants']:
        if digest(directory / (variant + '.txt')) != manifest['prompt_hashes'][variant]:
            raise ValueError('Frozen prompt changed')
        if (directory / (variant + '.txt')).read_text(encoding='utf-8') != manifest['prompts'][variant]:
            raise ValueError('Manifest prompt differs')
    if manifest['budget_guard_usd'] != BUDGET or manifest['planned_calls'] != config['calls']:
        raise ValueError('Pilot limits changed')
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), base_url='https://api.openai.com/v1',
                    max_retries=0, timeout=30)
    budgeted = BudgetedClient(client, manifest, directory)
    manifest.update(status='running', started_at_utc=now())
    rows = []
    try:
        for item in manifest['schedule']:
            round_no, variant = item[:2]
            mode = item[2] if len(item) == 3 else 'raw'
            for index, case in enumerate(manifest['cases'], 1):
                row = dict(evaluate_case(case, mode, budgeted, system_prompt=manifest['prompts'][variant]),
                           variant=variant, attempt=round_no, mode=mode)
                if row['finish_reason'] == 'length':
                    row.update(passed=False, failure_stage='completion_limit')
                rows.append(row)
                write_json(directory / 'results.json', dict(complete=False, results=rows))
                if index % 5 == 0:
                    print(f'round={round_no} {variant}/{mode}: {index}/20; calls={manifest["actual_calls"]}', flush=True)
                if row['failure_stage'] == 'api':
                    raise RuntimeError('API failure: ' + row.get('error', 'unknown'))
        summary = summarize_pilot(rows, profile)
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
    parser.add_argument('--profile', choices=tuple(PROFILES), default='pilot', help='Used only when preparing a new campaign')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--dry-run', action='store_true')
    modes.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    report = prepare(args.output, args.profile) if args.dry_run else execute(args.output)
    print(json.dumps({k:v for k,v in report.items() if k in
        ('planned_calls', 'budget_guard_usd', 'estimated_max_output_cost_usd', 'candidate', 'valid_comparison')}, indent=2))


if __name__ == '__main__':
    main()
