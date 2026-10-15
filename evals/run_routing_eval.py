"""Separated raw-model and application routing evaluation, without recipe lookup."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from openai import APIError, OpenAI

import main as application
from core.llm_tools import RECIPE_TOOLS
from core.tool_call_validation import ToolArgumentsError, parse_recipe_tool_arguments
from evals.run_llm_eval import (DEFAULT_CASES_PATH, DEFAULT_ROUTING_CASES_PATH,
                               FIELDS, load_cases, request_intent_response, score_case)

GUARD_CASES_PATH = Path(__file__).with_name("application_routing_cases.json")
HOLDOUT_CASES_PATH = Path(__file__).with_name("holdout_cases_v1.json")


def observe_response(response):
    observation = {"model_action": None, "tool_call_count": None, "raw_tool_calls": [],
                   "protocol_valid": None, "arguments_valid": None, "actual": None,
                   "no_tool_content": None, "no_tool_refusal": None, "finish_reason": None,
                   "failure_stage": None}
    if not response.choices:
        return {**observation, "protocol_valid": False, "failure_stage": "protocol"}
    calls = response.choices[0].message.tool_calls or []
    observation["finish_reason"] = getattr(response.choices[0], "finish_reason", None)
    if not calls:
        observation["no_tool_content"] = getattr(response.choices[0].message, "content", None)
        observation["no_tool_refusal"] = getattr(response.choices[0].message, "refusal", None)
    observation.update(model_action="tool" if calls else "no_tool", tool_call_count=len(calls),
                       raw_tool_calls=[{"name": call.function.name,
                                        "arguments": call.function.arguments} for call in calls])
    if calls and (len(calls) != 1 or calls[0].function.name != "get_recommendations"):
        return {**observation, "protocol_valid": False, "failure_stage": "protocol"}
    observation["protocol_valid"] = True
    if calls:
        try:
            observation["actual"] = parse_recipe_tool_arguments(calls[0].function.arguments)
            observation["arguments_valid"] = True
        except ToolArgumentsError as exc:
            observation.update(arguments_valid=False, failure_stage="arguments", error=str(exc))
    return observation


def evaluate_case(case, mode, client, model="gpt-4o-mini", brand_name="Winiary"):
    responses, backend_args, api_errors = [], [], []
    api_calls = 0

    def capture(**kwargs):
        nonlocal api_calls
        api_calls += 1
        try:
            response = client.chat.completions.create(**kwargs)
        except APIError as exc:
            api_errors.append(type(exc).__name__)
            raise
        responses.append(response)
        return response

    def backend_stub(args):
        backend_args.append(args)
        return {"query": {}, "recommendations": []}

    proxy = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=capture)))
    guard = None
    app_response = None
    try:
        if mode == "raw":
            request_intent_response(proxy, model, case["user_message"], brand_name)
        elif mode == "application":
            # Execute the actual guards, tool validation and dispatch, stopping
            # before database access. Do not reimplement application routing.
            with patch.object(application, "client", proxy), patch.object(
                    application, "run_recommendation_tool", side_effect=backend_stub):
                app_response = application.chat_with_bot(case["user_message"], brand_name)
            if app_response == application.UNSUPPORTED_ALLERGY_RESPONSE:
                guard = "allergy"
            elif app_response == application.UNSUPPORTED_EXCLUSION_RESPONSE:
                guard = "exclusion"
        else:
            raise ValueError("Unknown evaluation mode.")
    except APIError:
        pass

    observation = {"model_action": None, "tool_call_count": None, "raw_tool_calls": [],
                   "protocol_valid": None, "arguments_valid": None, "actual": None,
                   "no_tool_content": None, "no_tool_refusal": None, "finish_reason": None,
                   "failure_stage": None}
    if api_errors:
        observation.update(failure_stage="api", error=api_errors[0])
    elif responses:
        observation = observe_response(responses[0])
    elif guard is None:
        raise RuntimeError("Evaluation produced neither guard, API failure nor response.")

    if guard:
        effective_action = "no_tool"
    elif observation["failure_stage"]:
        effective_action = "error"
    else:
        effective_action = observation["model_action"]
    if mode == "application":
        if bool(backend_args) != (effective_action == "tool"):
            raise RuntimeError("Observed application dispatch differs from diagnostic routing.")
        if backend_args and backend_args != [observation["actual"]]:
            raise RuntimeError("Application changed or repeated tool arguments.")

    expected_action = case.get("expected_action", "tool")
    decision_correct = effective_action == expected_action if effective_action != "error" else None
    model_decision_correct = (observation["model_action"] == expected_action
                              if observation["model_action"] is not None else None)
    fields = {field: None for field in FIELDS}
    semantics_correct = None
    if expected_action == "tool" and observation["arguments_valid"] is True:
        scored = score_case(case["expected"], observation["actual"])
        fields, semantics_correct = scored["field_results"], scored["passed"]
    stage = observation["failure_stage"]
    if stage is None and decision_correct is False:
        stage = "preflight" if guard else "decision"
    if stage is None and semantics_correct is False:
        stage = "semantics"
    return {"id": case["id"], "user_message": case["user_message"],
            "expected_action": expected_action, "expected": case.get("expected"),
            **observation, "failure_stage": stage, "guard": guard,
            "effective_action": effective_action, "decision_correct": decision_correct,
            "model_decision_correct": model_decision_correct, "semantics_correct": semantics_correct,
            "field_results": fields, "api_calls": api_calls, "backend_calls": len(backend_args),
            "response_model": getattr(responses[0], "model", None) if responses else None,
            "request_id": getattr(responses[0], "_request_id", None) if responses else None,
            "passed": stage is None and decision_correct is True}


def metric(values):
    applicable = [value for value in values if value is not None]
    passed = sum(value is True for value in applicable)
    return {"passed": passed, "total": len(applicable),
            "accuracy": passed / len(applicable) if applicable else None}


def summarize(results):
    by_case = {}
    by_attempt = {}
    for row in results:
        by_case.setdefault(row["id"], []).append(row)
        by_attempt.setdefault(row.get("attempt", 1), []).append(row)
    stability = {}
    for case_id, trials in by_case.items():
        successes = sum(row["passed"] for row in trials)
        stability[case_id] = {"passed": successes, "total": len(trials),
                              "failure_type": "none" if successes == len(trials) else
                              "persistent" if successes == 0 else "intermittent",
                              "failure_stages": sorted({row["failure_stage"] for row in trials if row["failure_stage"]})}
    return {"total": len(results), "passed": sum(row["passed"] for row in results),
            "failed": sum(not row["passed"] for row in results),
            "api_calls": sum(row["api_calls"] for row in results),
            "guarded_cases": sum(row["guard"] is not None for row in results),
            "failures_by_stage": dict(Counter(row["failure_stage"] for row in results if row["failure_stage"])),
            "metrics": {key: metric(row[key] for row in results) for key in (
                "decision_correct", "model_decision_correct", "protocol_valid",
                "arguments_valid", "semantics_correct")},
            "field_accuracy_conditional": {
                field: metric(row["field_results"][field] for row in results) for field in FIELDS},
            "case_count": len(by_case), "stable_cases": sum(item["failure_type"] == "none" for item in stability.values()),
            "case_stability": stability,
            "attempts": {str(attempt): {"passed": sum(row["passed"] for row in rows), "total": len(rows)}
                         for attempt, rows in by_attempt.items()}}


def run_eval(args):
    paths = [HOLDOUT_CASES_PATH] if getattr(args, "holdout", False) else [args.cases, args.routing_cases, args.guard_cases]
    repeats = getattr(args, "repeats", 1)
    if repeats < 1:
        raise ValueError("Repeats must be positive.")
    cases = [case for path in paths for case in load_cases(path)]
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate ids across datasets.")
    if args.limit:
        cases = cases[:args.limit]
    # Application currently fixes this model; do not silently compare a different one.
    if args.mode == "application" and args.model != "gpt-4o-mini":
        raise ValueError("Application mode requires its configured model gpt-4o-mini.")
    report = {"schema_version": 3, "evaluation_kind": f"separated_{args.mode}_routing",
              "dataset_role": "holdout_v1" if getattr(args, "holdout", False) else "regression",
              "repeats": repeats,
              "scope": "routing_only_with_stubbed_recommendation_tool",
              "mode": args.mode, "dry_run": args.dry_run,
              "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "model": args.model, "temperature": 0.1, "parallel_tool_calls": False,
              "system_prompt": application.build_system_prompt(args.brand_name),
              "tool_schema": RECIPE_TOOLS, "brand_name": args.brand_name,
              "dataset_files": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                                for path in paths],
              "source_files": {name: hashlib.sha256((PROJECT_ROOT / name).read_bytes()).hexdigest()
                               for name in ("main.py", "core/request_safety.py", "core/tool_call_validation.py",
                                            "evals/run_llm_eval.py", "evals/run_routing_eval.py")},
              "results": []}
    if args.dry_run:
        # No API client or application call: guards can be planned locally.
        from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
        guarded = sum(mentions_unsupported_allergy(c["user_message"]) or
                      mentions_unsupported_exclusion(c["user_message"]) for c in cases)
        report["summary"] = {"total": len(cases) * repeats, "planned_api_calls":
                             (len(cases) - guarded if args.mode == "application" else len(cases)) * repeats}
        return report
    load_dotenv()
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    for attempt in range(1, repeats + 1):
        for index, case in enumerate(cases, 1):
            result = evaluate_case(case, args.mode, client, args.model, args.brand_name)
            report["results"].append({**result, "attempt": attempt})
            output = getattr(args, "output", None)
            if output:
                report["summary"] = summarize(report["results"])
                report["complete"] = False
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            if index == 1 or index % 10 == 0 or index == len(cases):
                print(f"{args.mode} attempt {attempt}/{repeats}: {index}/{len(cases)}", flush=True)
    report["summary"] = summarize(report["results"])
    report["complete"] = True
    report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    if getattr(args, "output", None):
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Expected a positive number.")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("raw", "application"), required=True)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--routing-cases", type=Path, default=DEFAULT_ROUTING_CASES_PATH)
    parser.add_argument("--guard-cases", type=Path, default=GUARD_CASES_PATH)
    parser.add_argument("--holdout", action="store_true", help="Use only frozen holdout v1, without development cases.")
    parser.add_argument("--repeats", type=positive_int, default=1)
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--brand-name", default="Winiary")
    parser.add_argument("--limit", type=positive_int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output is None:
        suffix = "holdout" if args.holdout else "routing"
        args.output = Path(__file__).with_name(f"{args.mode}_{suffix}_eval_report.json")
    report = run_eval(args)
    print(f"Routing eval mode: {args.mode}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if not args.dry_run:
        output = args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if args.dry_run or report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
