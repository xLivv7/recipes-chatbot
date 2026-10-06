from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.llm_tools import RECIPE_TOOLS
from main import build_system_prompt
from core.tool_call_validation import parse_recipe_tool_arguments


DEFAULT_CASES_PATH = Path(__file__).with_name("intent_cases.json")
DEFAULT_REPORT_PATH = Path(__file__).with_name("llm_eval_report.json")
DEFAULT_ROUTING_CASES_PATH = Path(__file__).with_name("routing_cases.json")
FIELDS = (
    "diet",
    "protein_preference",
    "restrictions",
    "nutrition_goal",
    "category",
    "time_max",
    "top_n",
)


def build_eval_system_prompt(brand_name: str) -> str:
    return build_system_prompt(brand_name)


def canonicalize_args(args: dict[str, Any]) -> dict[str, Any]:
    canonical = {field: args.get(field) for field in FIELDS}

    canonical["restrictions"] = sorted(canonical["restrictions"] or [])

    return canonical


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError("Case file must contain a JSON list.")

    seen_ids = set()
    for index, case in enumerate(cases, start=1):
        case_id = case.get("id")
        if not case_id:
            raise ValueError(f"Case #{index} is missing 'id'.")
        if case_id in seen_ids:
            raise ValueError(f"Duplicate case id: {case_id}")
        seen_ids.add(case_id)

        if not case.get("user_message"):
            raise ValueError(f"{case_id} is missing 'user_message'.")

        action = case.get("expected_action", "tool")
        if action not in ("tool", "no_tool"):
            raise ValueError(f"{case_id} has invalid expected_action.")
        if action == "no_tool":
            continue
        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(f"{case_id} is missing object 'expected'.")

        missing = set(FIELDS).difference(expected)
        if missing:
            raise ValueError(f"{case_id} expected args are missing: {sorted(missing)}")
        expected_tool_args = dict(expected)
        if expected_tool_args.get("time_max") is None:
            del expected_tool_args["time_max"]
        parse_recipe_tool_arguments(json.dumps(expected_tool_args))

    return cases


def extract_tool_args(client: OpenAI, model: str, user_message: str, brand_name: str) -> dict[str, Any] | None:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": build_eval_system_prompt(brand_name)},
            {"role": "user", "content": user_message},
        ],
        tools=RECIPE_TOOLS,
        tool_choice="auto",
        temperature=0.1,
    )

    if not response.choices:
        raise ValueError("Empty choices.")
    message = response.choices[0].message
    if not message.tool_calls:
        return None
    if len(message.tool_calls) != 1:
        raise ValueError("Expected exactly one tool call.")

    tool_call = message.tool_calls[0]
    if tool_call.function.name != "get_recommendations":
        raise ValueError(f"Model called unexpected tool: {tool_call.function.name}")

    return parse_recipe_tool_arguments(tool_call.function.arguments)


def score_intent_case(case, actual):
    expects_tool = case.get("expected_action", "tool") == "tool"
    action_correct = expects_tool == (actual is not None)
    if expects_tool and actual is not None:
        result = score_case(case["expected"], actual)
    else:
        result = {"passed": action_correct,
                  "field_results": {field: False if expects_tool else None for field in FIELDS},
                  "expected": case.get("expected"), "actual": actual}
    return {**result, "action_correct": action_correct}


def score_case(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    expected_canonical = canonicalize_args(expected)
    actual_canonical = canonicalize_args(actual)
    field_results = {
        field: expected_canonical[field] == actual_canonical[field]
        for field in FIELDS
    }

    return {
        "passed": all(field_results.values()),
        "field_results": field_results,
        "expected": expected_canonical,
        "actual": actual_canonical,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    field_accuracy = {}

    for field in FIELDS:
        applicable = [result for result in results if result["field_results"][field] is not None]
        field_passed = sum(1 for result in applicable if result["field_results"][field])
        field_accuracy[field] = {
            "passed": field_passed,
            "total": len(applicable),
            "accuracy": field_passed / len(applicable) if applicable else 0,
        }

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "exact_match_accuracy": passed / total if total else 0,
        "field_accuracy": field_accuracy,
        "action_accuracy": sum(result["action_correct"] for result in results) / total if total else 0,
    }


def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    load_dotenv()
    cases = load_cases(args.cases)
    if args.routing_cases:
        cases += load_cases(args.routing_cases)
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate case ids across datasets.")
    if args.limit:
        cases = cases[: args.limit]

    if args.dry_run:
        return {
            "dry_run": True,
            "summary": {"total": len(cases)},
            "results": [],
        }

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    results = []

    for case in cases:
        case_id = case["id"]
        try:
            actual = extract_tool_args(
                client=client,
                model=args.model,
                user_message=case["user_message"],
                brand_name=args.brand_name,
            )
            scored = score_intent_case(case, actual)
            results.append(
                {
                    "id": case_id,
                    "user_message": case["user_message"],
                    **scored,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "id": case_id,
                    "user_message": case["user_message"],
                    "passed": False,
                    "field_results": {field: None if case.get("expected_action") == "no_tool" else False for field in FIELDS},
                    "action_correct": False,
                    "expected": case.get("expected"),
                    "actual": None,
                    "error": str(exc),
                }
            )

    return {
        "dry_run": False,
        "evaluation_kind": "application_intent_routing",
        "temperature": 0.1,
        "system_prompt": build_eval_system_prompt(args.brand_name),
        "model": args.model,
        "brand_name": args.brand_name,
        "summary": summarize(results),
        "results": results,
    }


def print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]

    if report["dry_run"]:
        print(f"Dry run OK. Loaded {summary['total']} intent eval cases.")
        return

    total = summary["total"]
    print("LLM intent eval")
    print("=" * 40)
    print(f"Model: {report['model']}")
    print(f"Cases: {total}")
    print(f"Exact match: {summary['passed']}/{total} ({summary['exact_match_accuracy']:.1%})")
    print(f"Action accuracy: {summary['action_accuracy']:.1%}")
    print()
    print("Field accuracy:")
    for field, result in summary["field_accuracy"].items():
        print(f"  - {field}: {result['passed']}/{result['total']} ({result['accuracy']:.1%})")

    failed = [result for result in report["results"] if not result["passed"]]
    if failed:
        print()
        print("Failed cases:")
        for result in failed:
            print(f"  - {result['id']}: {result['user_message']}")
            if result.get("error"):
                print(f"    error: {result['error']}")
            else:
                print(f"    expected: {result['expected']}")
                print(f"    actual:   {result['actual']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline LLM intent extraction evals.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--routing-cases", type=Path, default=DEFAULT_ROUTING_CASES_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default=os.environ.get("LLM_EVAL_MODEL", "gpt-4o-mini"))
    parser.add_argument("--brand-name", default="Winiary")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_eval(args)
    print_summary(report)

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)

    return 0 if report["dry_run"] or report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
