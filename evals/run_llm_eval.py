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


DEFAULT_CASES_PATH = Path(__file__).with_name("intent_cases.json")
DEFAULT_REPORT_PATH = Path(__file__).with_name("llm_eval_report.json")
FIELDS = ("user_pref", "nutrition_goal", "category", "time_max", "top_n")


def build_eval_system_prompt(brand_name: str) -> str:
    return (
        "Jesteś kulinarnym asystentem. Twoim zadaniem jest pomaganie użytkownikom w znalezieniu "
        "idealnego posiłku. Zawsze używaj narzędzia 'get_recommendations', aby wyszukać przepisy w bazie. "
        "Gdy otrzymasz wyniki z narzędzia, przedstaw je w czytelny, apetyczny sposób w Markdown.\n\n"
        "ZASADY FORMATOWANIA:\n"
        "1. Zawsze podawaj czas przygotowania, kalorie i makro na porcję (kcal | B | T | W).\n"
        "2. Nie zmyślaj przepisów, składników ani wartości odżywczych spoza dostarczonych wyników.\n"
        "3. ZABRONIONE jest generowanie jakichkolwiek linków (URL) w odpowiedzi.\n"
        "4. Jeśli w wynikach w polu 'used_skus' znajdują się produkty, dodaj pod przepisem naturalną poradę. "
        f"WAŻNE: Pracujesz dla marki {brand_name}. Zawsze płynnie dodaj słowo '{brand_name}' "
        "do nazwy promowanego produktu. Zignoruj i usuń techniczne dopiski z nazwy w nawiasach, "
        "takie jak '(butelka)' czy '(słoik)'."
    )


def canonicalize_args(args: dict[str, Any]) -> dict[str, Any]:
    canonical = {field: args.get(field) for field in FIELDS}

    if canonical["user_pref"] == "vege":
        canonical["user_pref"] = "vegetarian"

    if canonical["time_max"] is not None:
        canonical["time_max"] = int(canonical["time_max"])

    if canonical["top_n"] is not None:
        canonical["top_n"] = int(canonical["top_n"])

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

        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(f"{case_id} is missing object 'expected'.")

        missing = set(FIELDS).difference(expected)
        if missing:
            raise ValueError(f"{case_id} expected args are missing: {sorted(missing)}")

    return cases


def extract_tool_args(client: OpenAI, model: str, user_message: str, brand_name: str) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": build_eval_system_prompt(brand_name)},
            {"role": "user", "content": user_message},
        ],
        tools=RECIPE_TOOLS,
        tool_choice={"type": "function", "function": {"name": "get_recommendations"}},
        temperature=0,
    )

    message = response.choices[0].message
    if not message.tool_calls:
        raise ValueError("Model did not call get_recommendations.")

    tool_call = message.tool_calls[0]
    if tool_call.function.name != "get_recommendations":
        raise ValueError(f"Model called unexpected tool: {tool_call.function.name}")

    return json.loads(tool_call.function.arguments)


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
        field_passed = sum(1 for result in results if result["field_results"][field])
        field_accuracy[field] = {
            "passed": field_passed,
            "total": total,
            "accuracy": field_passed / total if total else 0,
        }

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "exact_match_accuracy": passed / total if total else 0,
        "field_accuracy": field_accuracy,
    }


def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    load_dotenv()
    cases = load_cases(args.cases)
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
            scored = score_case(case["expected"], actual)
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
                    "field_results": {field: False for field in FIELDS},
                    "expected": canonicalize_args(case["expected"]),
                    "actual": None,
                    "error": str(exc),
                }
            )

    return {
        "dry_run": False,
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
