"""T027: frozen V4/IR-1 diagnostic; one SDK response, two dependent evaluations.

Preparation needs no credentials or catalog. Execution requires approval of
the exact plan hash and budget. No lookup, production switch or selective resume.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.interpretation_contract import (CLIENT_CONFIGURATION, MODEL_CONFIGURATION,
    build_interpretation_request, parse_interpretation_arguments)
from core.interpretation_compiler import compile_interpretation
from core.llm_response_validation import RESPONSE_VALIDATION_VERSION, response_failure_reason
from core.llm_tools import RECIPE_TOOLS
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
from core.tool_call_validation import ToolArgumentsError, parse_recipe_tool_arguments
from evals.prepare_interpretation_v1 import source_paths
from evals.run_routing_v5 import canonical, digest, runtime_versions, save, value_digest

RULE = "IR1-D1"
BUDGET_USD = 0.50
RESOLVED_MODELS = ("gpt-4o-mini", "gpt-4o-mini-2024-07-18")
FIELDS = ("diet", "protein_preference", "restrictions", "nutrition_goal", "category", "time_max", "top_n")
TARGETS = ("intent_003", "intent_004", "intent_032", "v5_diag_004")
GOLD = "specs/001-mvp-stabilization/contracts/interpretation-v1.examples.json"
CASE_SOURCES = ("evals/intent_cases.json", "evals/routing_cases.json", "evals/routing_v5_cases.json")
ARTIFACTS = ("cases.json", "payloads.json", "schedule.json", "model_access.json", "annotation_review.json")
PRICING = dict(input_usd_per_million=0.15, output_usd_per_million=0.60, checked_on="2026-11-18",
    source="https://developers.openai.com/api/docs/models/gpt-4o-mini",
    note="Standard text rates, without caching, taxes or other account use. Byte proxy is an estimate, not a billing guarantee.")
REVIEW_NOTES = {
    "intent_003": "Cel high_protein nie oznacza wymaganego mięsa ani ryby.",
    "intent_004": "Wykluczenie mięsa w deserze wyprowadza vegetarian lokalnie.",
    "intent_015": "Lekka, dieta, kategoria i pół godziny są osobnymi faktami.",
    "intent_025": "Quick i vegan; brak kategorii nie oznacza zależności od historii.",
    "intent_032": "Cztery propozycje i pescetarian nie wymagają fish.",
    "v5_diag_004": "Na wieczór oznacza kolację; wykluczenie mięsa i jawnie wymagana ryba pozostają osobne.",
    "v5_diag_008": "Fit i gluten nie tworzą limitu czasu; lunch jest kategorią.",
    "v5_diag_009": "Jak diag_008, z osobnym jawnym limitem 22 minut.",
    "v5_diag_010": "Bezlaktozowe i quick, ale jawne 50 minut ma pierwszeństwo.",
    "routing_005": "Pytanie o stolicę jest other, bez faktów i wyszukiwania.",
    "routing_006": "Jawny vegan i wymagane mięso to konflikt zachowany w faktach.",
    "v5_diag_012": "Bezmleczny jest nieobsługiwanym wykluczeniem; nie zastępować lactose/vegan.",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rule():
    return dict(name=RULE, primary_scope="raw_interpretation_and_compilation", complete_observations=72,
        one_resolved_model=True, API_and_metadata_errors=0, no_tool_required=9, tool_minimum=25,
        tool_total=27, stable_cases_minimum=11, cases_total=12, targets=list(TARGETS), target_successes=3,
        IR_protocol_and_validation_errors=0, incorrect_dispatches=0, no_case_regression=True,
        more_correct_tool_trials_than_V4=True, application_replay_is_dependent=True, deployment_allowed=False)


def frozen_sources(root=ROOT):
    return sorted(set(source_paths(root)) | set(CASE_SOURCES) | {
        "evals/run_interpretation_diagnostic.py", "tests/test_interpretation_diagnostic.py",
        "evals/run_routing_v5.py", "evals/prepare_routing_v5.py", "evals/routing_prompts/V4.txt"})


def canonical_args(args):
    if args is None:
        return None
    return dict(args, restrictions=sorted(args.get("restrictions", [])), time_max=args.get("time_max"))


def guard(query):
    return ("allergy" if mentions_unsupported_allergy(query) else
            "exclusion" if mentions_unsupported_exclusion(query) else None)


def build_inputs(root=ROOT):
    fixture = read(root / GOLD)
    originals = {row["id"]: row for name in CASE_SOURCES for row in read(root / name)}
    annotations = {row["source_case_id"]: row for row in fixture["valid"] if "source_case_id" in row}
    cases, payloads = [], {}
    prompt = (root / "evals/routing_prompts/V4.txt").read_text(encoding="utf-8").replace("{{brand_name}}", "Winiary")
    for case_id in fixture["diagnostic_ids"]:
        row, source = annotations[case_id], originals[case_id]
        if (row["user_message"] != source["user_message"] or row["expected_action"] != source.get("expected_action", "tool")
                or row.get("expected") != source.get("expected")):
            raise ValueError("Existing query or backend label changed: " + case_id)
        interpretation = parse_interpretation_arguments(json.dumps(row["interpretation"], ensure_ascii=False), row["user_message"])
        compiled = compile_interpretation(interpretation)
        if ((compiled.action == "search") != (row["expected_action"] == "tool")
                or canonical_args(compiled.arguments) != canonical_args(row.get("expected"))):
            raise ValueError("Fact annotation does not reproduce the existing label: " + case_id)
        case = dict(id=case_id, user_message=row["user_message"], expected_action=row["expected_action"],
            expected=row.get("expected"), interpretation=row["interpretation"], preflight_guard=guard(row["user_message"]))
        cases.append(case)
        payloads["V4/" + case_id] = dict(MODEL_CONFIGURATION,
            messages=[dict(role="system", content=prompt), dict(role="user", content=case["user_message"])],
            tools=deepcopy(RECIPE_TOOLS), tool_choice="auto")
        payloads["IR1/" + case_id] = build_interpretation_request(case["user_message"], "Winiary")
    if len(cases) != 12 or set(annotations) != set(REVIEW_NOTES) or sum(c["expected_action"] == "tool" for c in cases) != 9:
        raise ValueError("Diagnostic subset changed")
    schedule = [dict(attempt=attempt, variant=variant, id=case["id"], payload=variant + "/" + case["id"])
        for attempt, variants in ((1, ("V4", "IR1")), (2, ("IR1", "V4")), (3, ("V4", "IR1")))
        for variant in variants for case in cases]
    review = dict(status="reviewed_offline", reviewer="Codex", model_results_used=False,
        source=GOLD, backend_labels_unchanged=True, source_span_policy="Exact substring required; fact scoring compares kind/value/status, not identical span boundaries.",
        notes=REVIEW_NOTES, limitations="Technical and semantic review, not independent annotation or holdout validation.")
    return cases, payloads, schedule, review


def reservation(payload):
    # Same conservative proxy as T023, recalculated for each NEW 1024-token payload.
    proxy = len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) + 2000
    return (proxy * PRICING["input_usd_per_million"] + payload["max_completion_tokens"] * PRICING["output_usd_per_million"]) / 1e6


def validate_access(access):
    if (access.get("status") != "visible" or access.get("returned_model") != MODEL_CONFIGURATION["model"]
            or access.get("method") != "GET" or access.get("metadata_requests") != 1 or access.get("generation_requests") != 0):
        raise ValueError("Fresh model visibility receipt required")
    checked = datetime.fromisoformat(access["checked_at_utc"])
    if checked.tzinfo is None or not 0 <= (datetime.now(timezone.utc) - checked).total_seconds() < 86400:
        raise ValueError("Model visibility receipt must be less than 24 hours old")


def check_model(output):
    if Path(output).exists():
        raise ValueError("Do not overwrite a model visibility receipt")
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv()
    with OpenAI(**CLIENT_CONFIGURATION) as client:
        model = client.models.retrieve(MODEL_CONFIGURATION["model"])
    receipt = dict(status="visible", returned_model=model.id, method="GET", metadata_requests=1,
                   generation_requests=0, checked_at_utc=now())
    validate_access(receipt)
    save(Path(output), receipt)
    return receipt


def prepare(directory, access, root=ROOT):
    validate_access(access)
    cases, payloads, schedule, review = build_inputs(root)
    estimate = sum(reservation(payloads[slot["payload"]]) for slot in schedule)
    if estimate > BUDGET_USD:
        raise ValueError("Recalculate the plan before requesting approval: reservation exceeds budget")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for name, value in zip(ARTIFACTS, (cases, payloads, schedule, access, review)):
        save(directory / name, value)
    sources = frozen_sources(root)
    hashes = {name: digest(root / name) for name in sources}
    for name in sources:
        destination = directory / "frozen_inputs" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((root / name).read_bytes())
    plan = dict(task="T027", plan_version=1, rule=rule(), created_at_utc=now(), pricing=PRICING,
        client_configuration=CLIENT_CONFIGURATION, model_configuration=MODEL_CONFIGURATION,
        allowed_resolved_models=list(RESOLVED_MODELS), response_validation_version=RESPONSE_VALIDATION_VERSION,
        interpretation_contract_version="IR-1", source_hashes=hashes,
        artifact_hashes={name: digest(directory / name) for name in ARTIFACTS}, runtime_versions=runtime_versions(),
        planned_api_calls=72, unique_queries=12, raw_observations=72, dependent_application_replays=72,
        estimated_reservation_usd=estimate, budget_guard_usd=BUDGET_USD, execution_requires_explicit_approval=True,
        application_replay="Same response and frozen preflight; simulated dispatch, zero actual catalog/backend calls and zero additional SDK requests.",
        stop_on="First API/T022 metadata failure or unapproved resolved model; no retry or selective resume.",
        active_mode="legacy", active_prompt="V0", model_quality_measured=False,
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip())
    save(directory / "plan.json", plan)
    save(directory / "state.json", dict(status="prepared", reserved_requests=0, api_attempts=0,
        responses_received=0, completed_observations=0, reserved_usd=0.0, reservations=[],
        approved_plan_sha256=None, approved_budget_usd=None))
    return plan


def validate_frozen(directory, root=ROOT):
    directory = Path(directory)
    plan = read(directory / "plan.json")
    exact = dict(task="T027", plan_version=1, rule=rule(), pricing=PRICING,
        client_configuration=CLIENT_CONFIGURATION, model_configuration=MODEL_CONFIGURATION,
        allowed_resolved_models=list(RESOLVED_MODELS), response_validation_version=RESPONSE_VALIDATION_VERSION,
        interpretation_contract_version="IR-1", planned_api_calls=72, unique_queries=12,
        raw_observations=72, dependent_application_replays=72, budget_guard_usd=BUDGET_USD,
        execution_requires_explicit_approval=True, active_mode="legacy", active_prompt="V0", model_quality_measured=False)
    if any(plan.get(key) != value for key, value in exact.items()):
        raise ValueError("Frozen rule or configuration changed")
    if set(plan["source_hashes"]) != set(frozen_sources(root)) or set(plan["artifact_hashes"]) != set(ARTIFACTS):
        raise ValueError("Frozen source/artifact scope changed")
    for name, expected in plan["source_hashes"].items():
        if digest(root / name) != expected or digest(directory / "frozen_inputs" / name) != expected:
            raise ValueError("Frozen source changed: " + name)
    for name, expected in plan["artifact_hashes"].items():
        if digest(directory / name) != expected:
            raise ValueError("Frozen artifact changed: " + name)
    if plan["runtime_versions"] != runtime_versions():
        raise ValueError("Runtime changed")
    cases, payloads, schedule, review = build_inputs(root)
    for name, expected in zip(("cases.json", "payloads.json", "schedule.json", "annotation_review.json"), (cases, payloads, schedule, review)):
        if read(directory / name) != expected:
            raise ValueError("Frozen input semantics changed: " + name)
    validate_access(read(directory / "model_access.json"))
    estimate = sum(reservation(payloads[slot["payload"]]) for slot in schedule)
    if not math.isclose(plan["estimated_reservation_usd"], estimate, rel_tol=0, abs_tol=1e-12) or estimate > BUDGET_USD:
        raise ValueError("Frozen reservation changed")
    return plan, cases, payloads, schedule


def namespace(value):
    if isinstance(value, dict):
        return NS(**{key: namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return [namespace(item) for item in value]
    return value


def serialize_response(response):
    if hasattr(response, "model_dump"):
        value = response.model_dump(mode="json")
    else:
        value = json.loads(json.dumps(response, default=lambda item: vars(item)))
    value["_request_id"] = getattr(response, "_request_id", None)
    return value


def legacy_decode(response):
    result = dict(effective_action="error", actual=None, failure_stage=None, response_failure_reason=None,
        protocol_valid=False, validation_status="not_attempted", interpretation_tool_calls=0, tool_call_count=None, model_action=None)
    choices = getattr(response, "choices", None)
    if not choices or getattr(choices[0], "message", None) is None:
        return dict(result, failure_stage="protocol", response_failure_reason="empty_choices" if not choices else None)
    failure = response_failure_reason(response)
    if failure:
        return dict(result, failure_stage="protocol", response_failure_reason=failure)
    calls = getattr(choices[0].message, "tool_calls", None) or []
    if isinstance(calls, (list, tuple)):
        result.update(tool_call_count=len(calls), model_action="tool" if calls else "no_tool")
    if not isinstance(calls, (list, tuple)) or (calls and (len(calls) != 1 or getattr(getattr(calls[0], "function", None), "name", None) != "get_recommendations")):
        return dict(result, failure_stage="protocol")
    if not calls:
        return dict(result, effective_action="no_tool", protocol_valid=True, model_action="no_tool")
    try:
        args = parse_recipe_tool_arguments(getattr(calls[0].function, "arguments", None))
    except ToolArgumentsError:
        return dict(result, failure_stage="arguments", protocol_valid=True, validation_status="error", model_action="tool")
    return dict(result, effective_action="tool", actual=args, protocol_valid=True, validation_status="valid", model_action="tool")


def score(outcome, case):
    action = outcome["effective_action"]
    fields = {field: None for field in FIELDS}
    decision = None if action == "error" else action == case["expected_action"]
    semantics = None
    if action == "tool" and case["expected_action"] == "tool":
        actual, expected = canonical_args(outcome["actual"]), canonical_args(case["expected"])
        fields = {field: actual[field] == expected[field] for field in FIELDS}
        semantics = all(fields.values())
    stage = outcome.get("failure_stage")
    if stage is None and decision is False:
        stage = "decision"
    if stage is None and semantics is False:
        stage = "semantics"
    return dict(outcome, failure_stage=stage, decision_correct=decision, semantics_correct=semantics,
        field_results=fields, passed=stage is None and decision is True)


def fact_score(interpretation, gold):
    if interpretation is None:
        return dict(request_kind_correct=None, signature_exact=None, missing=None, spurious=None)
    def signatures(value):
        return {(f["kind"], f["value"], f["status"]) for f in value["facts"]}
    actual, expected = signatures(interpretation), signatures(gold)
    return dict(request_kind_correct=interpretation["request_kind"] == gold["request_kind"],
        signature_exact=actual == expected, missing=sorted(expected - actual), spurious=sorted(actual - expected))


def observation(slot, case, response_value=None, api_error=None):
    response = namespace(response_value) if response_value is not None else None
    interpretation = None
    if api_error:
        outcome = dict(effective_action="error", actual=None, failure_stage="api", response_failure_reason=None,
                       protocol_valid=None, validation_status="not_attempted", interpretation_tool_calls=0, tool_call_count=None, model_action=None)
    elif slot["variant"] == "V4":
        outcome = legacy_decode(response)
    else:
        from core.interpretation_adapter import decode_interpretation_response
        decoded = decode_interpretation_response(response, case["user_message"])
        trace = decoded.diagnostics
        interpretation = trace.get("interpretation")
        outcome = dict(effective_action=trace["effective_action"], actual=decoded.arguments,
            failure_stage=trace["failure_stage"], response_failure_reason=trace["response_failure_reason"],
            protocol_valid=trace["failure_stage"] not in ("protocol", "api"), validation_status=trace["validation_status"],
            interpretation_tool_calls=trace["interpretation_tool_calls"], tool_call_count=trace["tool_call_count"], model_action=None)
    raw = score(outcome, case)
    replay_guard = guard(case["user_message"])
    replay_outcome = (dict(effective_action="no_tool", actual=None, failure_stage=None,
        response_failure_reason=None, protocol_valid=None, validation_status="not_attempted",
        interpretation_tool_calls=0, tool_call_count=None, model_action=None) if replay_guard else outcome)
    replay = dict(score(replay_outcome, case), guard=replay_guard, real_api_calls=0, actual_backend_calls=0,
                  simulated_backend_calls=int(not replay_guard and outcome["effective_action"] == "tool"))
    usage = getattr(response, "usage", None)
    choices = getattr(response, "choices", None)
    return dict(attempt=slot["attempt"], variant=slot["variant"], id=case["id"], user_message=case["user_message"],
        expected_action=case["expected_action"], expected=case["expected"], api_calls=1,
        response_model=getattr(response, "model", None), request_id=getattr(response, "_request_id", None),
        finish_reason=getattr(choices[0], "finish_reason", None) if choices else None,
        response_validation_version=RESPONSE_VALIDATION_VERSION, interpretation_contract_version="IR-1" if slot["variant"] == "IR1" else None,
        usage={key: getattr(usage, key, None) for key in ("prompt_tokens", "completion_tokens", "total_tokens")},
        raw=raw, application_replay=replay, interpretation=interpretation,
        facts=fact_score(interpretation, case["interpretation"]) if slot["variant"] == "IR1" else None,
        provider_response=response_value, api_error=api_error)


def summarize(rows, scope):
    def count(group):
        return dict(passed=sum(row[scope]["passed"] for row in group), total=len(group))
    return dict(**count(rows), tool=count([r for r in rows if r["expected_action"] == "tool"]),
        no_tool=count([r for r in rows if r["expected_action"] == "no_tool"]),
        per_case={cid: sum(r[scope]["passed"] for r in rows if r["id"] == cid) for cid in dict.fromkeys(r["id"] for r in rows)},
        stable_cases=sum(all(r[scope]["passed"] for r in rows if r["id"] == cid) for cid in {r["id"] for r in rows}),
        failures_by_stage=dict(Counter(r[scope]["failure_stage"] for r in rows if r[scope]["failure_stage"])),
        field_accuracy_conditional={field: dict(passed=sum(r[scope]["field_results"][field] is True for r in rows),
            total=sum(r[scope]["field_results"][field] is not None for r in rows)) for field in FIELDS},
        incorrect_dispatches=[dict(id=r["id"], attempt=r["attempt"], actual=r[scope]["actual"], expected=r["expected"])
            for r in rows if r[scope]["effective_action"] == "tool" and not r[scope]["passed"]])


def comparison(rows, cases, schedule):
    labels = {case["id"]: case for case in cases}
    keys = [(r["attempt"], r["variant"], r["id"]) for r in rows]
    expected = [(s["attempt"], s["variant"], s["id"]) for s in schedule]
    if len(keys) != 72 or keys != expected or len(set(keys)) != 72:
        raise ValueError("Incomplete, duplicate or out-of-order observations")
    # Recompute scores from preserved provider responses, never trust edited success flags.
    for row, slot in zip(rows, schedule):
        if canonical(row) != canonical(observation(slot, labels[slot["id"]], row["provider_response"], row["api_error"])):
            raise ValueError("Observation differs from the preserved response or frozen labels")
    models = {r["response_model"] for r in rows}
    valid = len(models) == 1 and models <= set(RESOLVED_MODELS) and not any(r["api_error"] or r["raw"]["response_failure_reason"] for r in rows)
    summaries = {v: {scope: summarize([r for r in rows if r["variant"] == v], scope)
        for scope in ("raw", "application_replay")} for v in ("V4", "IR1")}
    a, b = summaries["V4"]["raw"], summaries["IR1"]["raw"]
    regressions = [cid for cid in labels if b["per_case"][cid] < a["per_case"][cid]]
    conditions = dict(valid_complete_measurement=valid, no_tool_all=b["no_tool"] == dict(passed=9, total=9),
        tool_accuracy=b["tool"]["passed"] >= 25, stable_cases=b["stable_cases"] >= 11,
        targets_all=all(b["per_case"][cid] == 3 for cid in TARGETS), no_case_regression=not regressions,
        more_correct_tool_trials=b["tool"]["passed"] > a["tool"]["passed"],
        no_IR_protocol_or_validation_errors=not any(r["raw"]["failure_stage"] in ("protocol", "interpretation") for r in rows if r["variant"] == "IR1"),
        no_incorrect_dispatches=not b["incorrect_dispatches"] and not summaries["IR1"]["application_replay"]["incorrect_dispatches"])
    usage_complete = all(type(r["usage"][key]) is int and r["usage"][key] >= 0 for r in rows for key in r["usage"])
    usage = {key: sum(r["usage"][key] or 0 for r in rows) for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
    return dict(complete=True, rule=RULE, primary_scope="raw", conditions=conditions,
        candidate_qualifies=all(conditions.values()), diagnostic_candidate="IR1" if all(conditions.values()) else None,
        variants=summaries, per_case_regressions=regressions, resolved_models=sorted(m for m in models if m),
        fact_evaluations=[dict(id=r["id"], attempt=r["attempt"], **r["facts"]) for r in rows if r["variant"] == "IR1"],
        all_failures=[r for r in rows if not r["raw"]["passed"]], usage=usage, usage_complete=usage_complete,
        reference_usage_cost_no_cache_usd=(usage["prompt_tokens"] * PRICING["input_usd_per_million"] + usage["completion_tokens"] * PRICING["output_usd_per_million"]) / 1e6 if usage_complete else None,
        observed_sdk_calls=72, dependent_application_replays=72, actual_backend_calls=0,
        keep_active_mode="legacy", keep_active_prompt="V0", deployment_allowed=False, ACC_accepted=False)


class CampaignStopped(RuntimeError):
    pass


def execute(directory, approved_plan_sha256=None, approved_budget_usd=None, client_factory=None):
    directory = Path(directory)
    plan, cases, payloads, schedule = validate_frozen(directory)
    if (approved_plan_sha256 != digest(directory / "plan.json") or type(approved_budget_usd) not in (int, float)
            or not math.isfinite(approved_budget_usd) or approved_budget_usd != BUDGET_USD):
        raise ValueError("Approval must match the exact plan hash and budget")
    state = read(directory / "state.json")
    if state != dict(status="prepared", reserved_requests=0, api_attempts=0, responses_received=0,
        completed_observations=0, reserved_usd=0.0, reservations=[], approved_plan_sha256=None, approved_budget_usd=None) or (directory / "results.json").exists():
        raise ValueError("Campaign already started; no selective resume")
    mock = client_factory is not None
    from openai import APIError, OpenAI
    if not mock:
        from dotenv import load_dotenv
        load_dotenv()
        client_factory = OpenAI
    state.update(status="running", execution_kind="mock" if mock else "live", approved_plan_sha256=approved_plan_sha256,
                 approved_budget_usd=approved_budget_usd, started_at_utc=now())
    save(directory / "state.json", state)
    rows, client = [], None
    labels = {case["id"]: case for case in cases}
    try:
        client = client_factory(**CLIENT_CONFIGURATION)
        for slot in schedule:
            payload = deepcopy(payloads[slot["payload"]])
            if state["reserved_requests"] >= plan["planned_api_calls"]:
                raise CampaignStopped("request_limit")
            reserve = reservation(payload)
            if state["reserved_usd"] + reserve > BUDGET_USD:
                raise CampaignStopped("reservation_limit")
            state["reserved_requests"] += 1
            state["reserved_usd"] += reserve
            state["reservations"].append(dict(slot, payload_sha256=value_digest(payload), reserved_usd=reserve))
            save(directory / "state.json", state)  # Commit reservation BEFORE a request; failed I/O sends nothing.
            state["api_attempts"] += 1
            try:
                response = client.chat.completions.create(**payload)
                state["responses_received"] += 1
                row = observation(slot, labels[slot["id"]], serialize_response(response))
            except APIError as error:
                row = observation(slot, labels[slot["id"]], api_error=type(error).__name__)
            rows.append(row)
            state["completed_observations"] = len(rows)
            save(directory / "results.json", dict(complete=False, execution_kind=state["execution_kind"], is_model_measurement=not mock, results=rows))
            save(directory / "state.json", state)
            if row["api_error"] or row["raw"]["response_failure_reason"]:
                raise CampaignStopped(row["api_error"] or row["raw"]["response_failure_reason"])
            if row["response_model"] not in RESOLVED_MODELS or len({r["response_model"] for r in rows}) != 1:
                raise CampaignStopped("resolved_model_mismatch")
            if len(rows) % 12 == 0:
                print(f"round={slot['attempt']} {slot['variant']}: {len(rows)}/72 SDK observations", flush=True)
        report = comparison(rows, cases, schedule)
        report.update(execution_kind=state["execution_kind"], is_model_measurement=not mock,
                      actual_model_requests=0 if mock else state["api_attempts"], plan_sha256=approved_plan_sha256)
        save(directory / "comparison.json", report)
        save(directory / "results.json", dict(complete=True, execution_kind=state["execution_kind"], is_model_measurement=not mock, results=rows))
        state.update(status="complete", completed_at_utc=now())
        return report
    except BaseException as error:
        state.update(status="incomplete", stop_reason=str(error) if isinstance(error, CampaignStopped) else type(error).__name__)
        save(directory / "results.json", dict(complete=False, execution_kind=state["execution_kind"], is_model_measurement=not mock, results=rows))
        raise
    finally:
        save(directory / "state.json", state)
        if client is not None:
            client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-model", action="store_true")
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model-access", type=Path)
    parser.add_argument("--approved-plan-sha256")
    parser.add_argument("--approved-budget-usd", type=float)
    args = parser.parse_args()
    if args.check_model:
        result = check_model(args.output)
    elif args.prepare:
        if args.model_access is None:
            parser.error("--prepare requires --model-access")
        result = prepare(args.output, read(args.model_access))
    else:
        result = execute(args.output, args.approved_plan_sha256, args.approved_budget_usd)
    print(json.dumps({key: result[key] for key in ("status", "planned_api_calls", "estimated_reservation_usd", "budget_guard_usd", "candidate_qualifies") if key in result}, indent=2))


if __name__ == "__main__":
    main()
