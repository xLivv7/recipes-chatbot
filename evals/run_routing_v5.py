"""T023: frozen V4/V5 comparison. Execution requires the approved plan hash and budget."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import sys
import time
from types import SimpleNamespace
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.llm_response_validation import RESPONSE_VALIDATION_VERSION
from evals.prepare_routing_v5 import (CONFIGURATION, FROZEN_FILES, PRICING, TARGETS,
    build_preparation, guard, prepare as prepare_inputs, read_json, request, wire_args)

RULE = "T017-v1"
BUDGET_USD = 1.0
SAVE_RETRY_DELAYS = (.05, .1, .2, .4, .8)
EXTRA_SOURCES = ("evals/run_routing_v5.py", "requirements.txt")
ARTIFACTS = ("manifest.json", "checks.json", "cases.json", "guard_audit.json", "tool_schema.json",
             "V4.txt", "V5.txt", "V4_V5.diff", "payloads.json", "schedule.json", "model_access.json")


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def value_digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Windows readers/sync clients can briefly deny replacement of an open file.
    # Retry only the local commit; the caller has not sent its next API request.
    for attempt in range(len(SAVE_RETRY_DELAYS) + 1):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == len(SAVE_RETRY_DELAYS):
                raise
            time.sleep(SAVE_RETRY_DELAYS[attempt])


def runtime_versions():
    result = dict(python=platform.python_version())
    for name in ("openai", "sqlalchemy", "httpx"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def reservation(payload):
    proxy = len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) + 2000
    return (proxy * PRICING["input_usd_per_million"] + 512 * PRICING["output_usd_per_million"]) / 1e6


def approval_rule():
    return dict(name=RULE, no_tool_required_per_mode=21,
        targets=list(TARGETS), target_successes=3, application_min_passed=87,
        application_supported_min_passed=68, application_min_stable=28,
        no_case_regression=True, no_semantic_dispatch=True,
        fewer_unrequested_fish_in_both_modes=True, no_lost_fish_increase=True)


def prepare(directory, model_access, root=ROOT):
    if (model_access.get("status") != "visible" or model_access.get("returned_model") != CONFIGURATION["model"]
            or model_access.get("method") != "GET" or model_access.get("generation_requests") != 0):
        raise ValueError("Model metadata visibility must be confirmed without generation")
    directory = Path(directory)
    base, _ = prepare_inputs(directory, root)
    cases = read_json(directory / "cases.json")
    payloads, schedule = {}, []
    for variant in ("V4", "V5"):
        prompt = (directory / f"{variant}.txt").read_text(encoding="utf-8")
        for case in cases:
            payloads[f"{variant}/{case['id']}"] = request(prompt, case)
    for attempt, variant, mode in base["schedule"]:
        for case in cases:
            schedule.append(dict(attempt=attempt, variant=variant, mode=mode, id=case["id"],
                requires_api=mode == "raw" or not guard(case), payload=f"{variant}/{case['id']}"))
    save(directory / "payloads.json", payloads)
    save(directory / "schedule.json", schedule)
    save(directory / "model_access.json", model_access)
    sources = dict(base["source_hashes"])
    for name in EXTRA_SOURCES:
        sources[name] = digest(root / name)
        target = directory / "frozen_inputs" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / name).read_bytes())
    estimated = sum(reservation(payloads[slot["payload"]]) for slot in schedule if slot["requires_api"])
    if estimated > BUDGET_USD:
        raise ValueError("Estimated reservation exceeds the proposed budget; revise before approval")
    plan = dict(task="T023", plan_version=1, rule=approval_rule(), created_at_utc=now(),
        configuration=CONFIGURATION, response_validation_version=RESPONSE_VALIDATION_VERSION,
        source_hashes=sources, artifact_hashes={name: digest(directory / name) for name in ARTIFACTS},
        runtime_versions=runtime_versions(), planned_evaluations=len(schedule),
        planned_api_calls=sum(slot["requires_api"] for slot in schedule),
        estimated_reservation_usd=estimated, budget_guard_usd=BUDGET_USD, pricing=PRICING,
        cost_note=base["cost_note"], execution_requires_explicit_approval=True,
        stop_on="first API error or response_failure_reason; no retry or selective resume",
        scope="development_diagnostic_with_stubbed_lookup_not_MVP_acceptance",
        active_prompt="V0", git_commit=base["git_commit"])
    save(directory / "plan.json", plan)
    save(directory / "state.json", dict(status="prepared", actual_api_calls=0, reserved_usd=0.0,
        completed_evaluations=0, reservations=[], approved_plan_sha256=None, approved_budget_usd=None))
    return plan


def validate_frozen(directory, root=ROOT):
    directory = Path(directory)
    plan = read_json(directory / "plan.json")
    if (plan.get("task") != "T023" or plan.get("plan_version") != 1 or plan.get("rule") != approval_rule()
            or plan.get("configuration") != CONFIGURATION or plan.get("pricing") != PRICING
            or plan.get("budget_guard_usd") != BUDGET_USD
            or plan.get("response_validation_version") != RESPONSE_VALIDATION_VERSION):
        raise ValueError("Frozen configuration, rule, pricing or budget changed")
    if set(plan["source_hashes"]) != set(FROZEN_FILES + EXTRA_SOURCES) or set(plan["artifact_hashes"]) != set(ARTIFACTS):
        raise ValueError("Frozen source/artifact scope changed")
    for name, expected in plan["source_hashes"].items():
        if digest(root / name) != expected or digest(directory / "frozen_inputs" / name) != expected:
            raise ValueError("Frozen source changed: " + name)
    for name, expected in plan["artifact_hashes"].items():
        if digest(directory / name) != expected:
            raise ValueError("Frozen artifact changed: " + name)
    if plan["runtime_versions"] != runtime_versions():
        raise ValueError("Runtime changed; prepare a new comparison before approval")
    current, _, prompts, cases, _ = build_preparation(root)
    payloads = read_json(directory / "payloads.json")
    expected_payloads = {f"{variant}/{case['id']}": request(prompts[variant], case)
                         for variant in ("V4", "V5") for case in cases}
    schedule = [dict(attempt=a, variant=v, mode=m, id=case["id"],
                    requires_api=m == "raw" or not guard(case), payload=f"{v}/{case['id']}")
                for a, v, m in current["schedule"] for case in cases]
    if (read_json(directory / "cases.json") != cases or payloads != expected_payloads
            or read_json(directory / "schedule.json") != schedule
            or plan["planned_evaluations"] != len(schedule)
            or plan["planned_api_calls"] != sum(slot["requires_api"] for slot in schedule)):
        raise ValueError("Frozen queries, labels, payloads or schedule changed")
    estimated = sum(reservation(payloads[slot["payload"]]) for slot in schedule if slot["requires_api"])
    if not math.isclose(estimated, plan["estimated_reservation_usd"], rel_tol=0, abs_tol=1e-12) or estimated > BUDGET_USD:
        raise ValueError("Frozen cost reservation changed")
    return plan, cases, payloads, schedule


def canonical_args(args):
    if args is None:
        return None
    return dict(args, restrictions=sorted(args.get("restrictions", [])), time_max=args.get("time_max"))


def comparison(rows, plan, cases):
    expected_keys = {(a, v, m, case["id"]) for a in (1, 2, 3)
                     for v in ("V4", "V5") for m in ("raw", "application") for case in cases}
    keys = [(row["attempt"], row["variant"], row["mode"], row["id"]) for row in rows]
    if len(keys) != len(expected_keys) or set(keys) != expected_keys:
        raise ValueError("Incomplete, duplicate or unexpected observations")
    labels = {case["id"]: case for case in cases}
    for row in rows:
        label = labels[row["id"]]
        if (row["user_message"] != label["user_message"] or row["expected"] != label.get("expected")
                or row["expected_action"] != label.get("expected_action", "tool")
                or row.get("response_validation_version") != RESPONSE_VALIDATION_VERSION):
            raise ValueError("Labels or response validation version changed")
        expects_request = row["mode"] == "raw" or not guard(label)
        if row["api_calls"] != int(expects_request):
            raise ValueError("Request count differs from the frozen schedule")
    models = {row["response_model"] for row in rows if row["api_calls"]}
    valid = (len(models) == 1 and None not in models
             and not any(row["failure_stage"] == "api" or row.get("response_failure_reason")
                         or row.get("finish_reason") == "length" for row in rows))

    def summarize(group):
        def score(selected):
            return dict(passed=sum(row["passed"] for row in selected), total=len(selected))
        per_case = {cid: sum(row["passed"] for row in group if row["id"] == cid) for cid in labels}
        supported = [row for row in group if row["expected_action"] == "tool"]
        fields = {field: score([dict(passed=row["field_results"][field]) for row in group
                               if row["field_results"][field] is not None])
                  for field in ("diet", "protein_preference", "restrictions", "nutrition_goal", "category", "time_max", "top_n")}
        return dict(passed=sum(row["passed"] for row in group), total=len(group),
            supported=score(supported), no_tool=score([row for row in group if row["expected_action"] == "no_tool"]),
            case_successes=per_case, stable_cases=sum(value == 3 for value in per_case.values()), field_accuracy=fields,
            failures_by_stage=dict(Counter(row["failure_stage"] for row in group if row["failure_stage"])),
            api_calls=sum(row["api_calls"] for row in group), backend_calls=sum(row["backend_calls"] for row in group),
            correct_guards=sum(bool(row["guard"]) and row["expected_action"] == "no_tool" for row in group),
            false_guards=sum(bool(row["guard"]) and row["expected_action"] == "tool" for row in group),
            unrequested_fish=sum(row["expected_action"] == "tool" and row["expected"]["protein_preference"] == "none"
                                 and (row["actual"] or {}).get("protein_preference") == "fish" for row in group),
            lost_explicit_fish=sum(row["expected_action"] == "tool" and row["expected"]["protein_preference"] == "fish"
                                  and (row["actual"] or {}).get("protein_preference") != "fish" for row in group),
            usage={field: sum((row.get("usage") or {}).get(field) or 0 for row in group)
                   for field in ("prompt_tokens", "completion_tokens", "total_tokens")})

    summaries = {variant: {mode: summarize([row for row in rows if row["variant"] == variant and row["mode"] == mode])
                           for mode in ("raw", "application")} for variant in ("V4", "V5")}
    regressions = {mode: [dict(id=cid, V4=summaries["V4"][mode]["case_successes"][cid],
                              V5=summaries["V5"][mode]["case_successes"][cid]) for cid in labels
                         if summaries["V5"][mode]["case_successes"][cid] < summaries["V4"][mode]["case_successes"][cid]]
                   for mode in ("raw", "application")}
    dispatch_errors = {variant: [dict(id=row["id"], attempt=row["attempt"], expected=row["expected"], actual=row["actual"])
        for row in rows if row["variant"] == variant and row["mode"] == "application" and row["backend_calls"]
        and (row["expected_action"] != "tool" or canonical_args(row["actual"]) != canonical_args(row["expected"]))]
        for variant in ("V4", "V5")}
    v5, v4 = summaries["V5"], summaries["V4"]
    app = v5["application"]
    conditions = dict(valid_comparison=valid,
        no_tool_all=all(v5[mode]["no_tool"] == dict(passed=21, total=21) for mode in v5),
        targets_all=all(v5[mode]["case_successes"][cid] == 3 for mode in v5 for cid in TARGETS),
        no_case_regression=not any(regressions.values()), no_semantic_dispatch=not dispatch_errors["V5"],
        application_accuracy=app["passed"] * 10 >= app["total"] * 9,
        supported_accuracy=app["supported"]["passed"] * 10 >= app["supported"]["total"] * 9,
        application_stability=app["stable_cases"] * 100 >= len(cases) * 85,
        fish_errors_decrease=all(v5[m]["unrequested_fish"] < v4[m]["unrequested_fish"] for m in v5),
        no_fish_loss_increase=all(v5[m]["lost_explicit_fish"] <= v4[m]["lost_explicit_fish"] for m in v5))
    usage = {field: sum((row.get("usage") or {}).get(field) or 0 for row in rows)
             for field in ("prompt_tokens", "completion_tokens", "total_tokens")}
    return dict(complete=True, rule=RULE, valid_comparison=valid, conditions=conditions,
        candidate="V5" if all(conditions.values()) else None, candidate_qualifies=all(conditions.values()),
        variants=summaries, case_regressions=regressions, semantic_dispatch_errors=dispatch_errors,
        resolved_models=sorted(value for value in models if value), usage=usage,
        usage_cost_no_cache_usd=(usage["prompt_tokens"] * PRICING["input_usd_per_million"]
                                 + usage["completion_tokens"] * PRICING["output_usd_per_million"]) / 1e6,
        active_prompt_changed=False, keep_active_prompt="V0", total_evaluations=len(rows),
        api_calls=sum(row["api_calls"] for row in rows), response_validation_version=RESPONSE_VALIDATION_VERSION)


class CampaignStopped(RuntimeError):
    pass


def audit_guards(probes):
    """Check frozen preflight outcomes; released probes have no model score."""

    def denied(**kwargs):
        raise CampaignStopped("guard_audit_reached_model")

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=denied)))
    results = []
    for probe in probes:
        blocked = guard(probe)
        if type(probe.get("preflight_blocked")) is not bool or blocked != probe["preflight_blocked"]:
            raise CampaignStopped("guard_audit_changed")
        if blocked:
            from evals.run_routing_eval import evaluate_case
            row = evaluate_case(probe, "application", client)
            if row["api_calls"] or row["backend_calls"] or row["failure_stage"] != "preflight" or row["passed"]:
                raise CampaignStopped("guard_audit_changed")
        else:
            # A successful preflight does not predict the model's next decision.
            row = dict(id=probe["id"], user_message=probe["user_message"],
                expected_action=probe.get("expected_action", "tool"), expected=probe.get("expected"),
                guard=None, failure_stage=None, api_calls=0, backend_calls=0,
                model_action=None, model_decision_correct=None, decision_correct=None,
                semantics_correct=None, passed=None)
        results.append(dict(row, preflight_blocked=blocked, preflight_passed=not blocked,
                            evaluation_scope="preflight_only"))
    return results


class BudgetedClient:
    def __init__(self, client, directory, plan, state, payloads, schedule):
        self.client, self.directory, self.plan, self.state = client, directory, plan, state
        self.payloads = payloads
        self.slots = [slot for slot in schedule if slot["requires_api"]]
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        kwargs["max_completion_tokens"] = 512
        index = self.state["actual_api_calls"]
        if index >= self.plan["planned_api_calls"]:
            raise CampaignStopped("request_limit")
        slot = self.slots[index]
        if canonical(kwargs) != canonical(self.payloads[slot["payload"]]):
            raise CampaignStopped("payload_mismatch")
        reserve = reservation(kwargs)
        if self.state["reserved_usd"] + reserve > self.plan["budget_guard_usd"]:
            raise CampaignStopped("reservation_limit")
        self.state["actual_api_calls"] += 1
        self.state["reserved_usd"] += reserve
        self.state["reservations"].append(dict(attempt=slot["attempt"], variant=slot["variant"],
            mode=slot["mode"], id=slot["id"], payload_sha256=value_digest(kwargs), reserved_usd=reserve))
        save(self.directory / "state.json", self.state)
        return self.client.chat.completions.create(**kwargs)


def execute(directory, approved_plan_sha256=None, approved_budget_usd=None, client_factory=None):
    directory = Path(directory)
    plan, cases, payloads, schedule = validate_frozen(directory)
    if (approved_plan_sha256 != digest(directory / "plan.json") or type(approved_budget_usd) not in (int, float)
            or not math.isfinite(approved_budget_usd) or approved_budget_usd != plan["budget_guard_usd"]):
        raise ValueError("Explicit approval must match the exact plan hash and proposed budget")
    state = read_json(directory / "state.json")
    if state["status"] != "prepared" or state["actual_api_calls"] or (directory / "results.json").exists():
        raise ValueError("Campaign already started; no selective resume")
    from evals.run_routing_eval import evaluate_case
    guard_results = audit_guards(read_json(directory / "guard_audit.json"))
    mock = client_factory is not None
    if client_factory is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        client_factory = OpenAI
    client = client_factory(base_url=CONFIGURATION["endpoint"], max_retries=0, timeout=30)
    state.update(status="running", approved_plan_sha256=approved_plan_sha256,
                 approved_budget_usd=approved_budget_usd, started_at_utc=now(), execution_kind="mock" if mock else "live")
    save(directory / "state.json", state)
    save(directory / "guard_audit_results.json", guard_results)
    budgeted = BudgetedClient(client, directory, plan, state, payloads, schedule)
    labels = {case["id"]: case for case in cases}
    rows = []
    group_rows = []
    group_key = None
    (directory / "groups").mkdir()
    try:
        for slot in schedule:
            key = (slot["attempt"], slot["variant"], slot["mode"])
            if key != group_key:
                group_key, group_rows = key, []
            prompt = payloads[slot["payload"]]["messages"][0]["content"]
            row = dict(evaluate_case(labels[slot["id"]], slot["mode"], budgeted,
                                    model=CONFIGURATION["model"], system_prompt=prompt),
                       attempt=slot["attempt"], variant=slot["variant"], mode=slot["mode"])
            rows.append(row)
            group_rows.append(row)
            group_file = directory / "groups" / f"round{key[0]}_{key[1]}_{key[2]}.json"
            save(group_file, dict(round=key[0], variant=key[1], mode=key[2], results=group_rows,
                                 complete=len(group_rows) == len(cases), execution_kind=state["execution_kind"]))
            state["completed_evaluations"] = len(rows)
            save(directory / "state.json", state)
            if row["failure_stage"] == "api" or row.get("response_failure_reason"):
                raise CampaignStopped(row.get("response_failure_reason") or "api_error")
            if len(group_rows) == len(cases):
                print(f"round={key[0]} {key[1]}/{key[2]}: {len(rows)}/{len(schedule)} evaluations; requests={state['actual_api_calls']}", flush=True)
        report = comparison(rows, plan, cases)
        report.update(execution_kind=state["execution_kind"], is_model_measurement=not mock,
                      plan_sha256=approved_plan_sha256, guard_audit=guard_results)
        save(directory / "comparison.json", report)
        save(directory / "results.json", dict(complete=True, execution_kind=state["execution_kind"], results=rows))
        state.update(status="complete", completed_at_utc=now())
        return report
    except BaseException as error:
        state.update(status="incomplete", stop_reason=str(error) if isinstance(error, CampaignStopped) else type(error).__name__)
        save(directory / "results.json", dict(complete=False, execution_kind=state["execution_kind"], results=rows))
        raise
    finally:
        save(directory / "state.json", state)
        close = getattr(client, "close", None)
        if close:
            close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-access", type=Path)
    parser.add_argument("--approved-plan-sha256")
    parser.add_argument("--approved-budget-usd", type=float)
    args = parser.parse_args()
    if args.prepare:
        if args.model_access is None:
            parser.error("--prepare requires the metadata-only --model-access evidence")
        report = prepare(args.output, read_json(args.model_access))
        print(json.dumps(dict(plan_sha256=digest(args.output / "plan.json"),
            planned_api_calls=report["planned_api_calls"], planned_evaluations=report["planned_evaluations"],
            estimated_reservation_usd=report["estimated_reservation_usd"],
            proposed_budget_usd=report["budget_guard_usd"], actual_api_calls=0), indent=2))
    else:
        report = execute(args.output, args.approved_plan_sha256, args.approved_budget_usd)
        print(json.dumps(dict(complete=report["complete"], candidate=report["candidate"],
                              conditions=report["conditions"]), indent=2))


if __name__ == "__main__":
    main()
