from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import build_system_prompt


DEFAULT_CASES_PATH = Path(__file__).with_name("final_answer_cases.json")
DEFAULT_REPORT_PATH = Path(__file__).with_name("final_answer_eval_report.json")
POLISH_MARKERS = ("przepis", "porcj", "min", "kcal", "biał", "białko", "polecam", "wynik")


def normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def number_pattern(value: int | float) -> str:
    normalized = f"{float(value):.1f}".rstrip("0").rstrip(".")
    return re.escape(normalized).replace(r"\.", r"[.,]")


def clean_sku_name(name: str) -> str:
    return name.split("(", 1)[0].strip()


def sku_is_mentioned(name: str, response: str) -> bool:
    normalized_name = normalized_text(clean_sku_name(name))
    normalized_response = normalized_text(response)
    if normalized_name in normalized_response:
        return True

    tokens = [token for token in re.findall(r"\w+", normalized_name) if len(token) >= 3]
    return bool(tokens) and all(token[: min(6, len(token))] in normalized_response for token in tokens)


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
        if not isinstance(case.get("tool_result"), dict):
            raise ValueError(f"{case_id} is missing object 'tool_result'.")
        if not isinstance(case.get("expected"), dict):
            raise ValueError(f"{case_id} is missing object 'expected'.")

    return cases


def build_messages(case: dict[str, Any], brand_name: str) -> list[dict[str, Any]]:
    tool_call_id = "eval_tool_call_1"
    return [
        {"role": "system", "content": build_system_prompt(brand_name)},
        {"role": "user", "content": case["user_message"]},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {"name": "get_recommendations", "arguments": "{}"},
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": "get_recommendations",
            "content": json.dumps(case["tool_result"], ensure_ascii=False),
        },
    ]


def generate_final_answer(client: OpenAI, model: str, case: dict[str, Any], brand_name: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=build_messages(case, brand_name),
        temperature=0,
    )
    return response.choices[0].message.content or ""


def _check_recipe_details(recipe: dict[str, Any], response: str, errors: list[str]) -> None:
    title = recipe["title_pl"]
    if normalized_text(title) not in normalized_text(response):
        errors.append(f"missing recipe title: {title}")

    time_min = recipe["time_min"]
    if not re.search(rf"\b{number_pattern(time_min)}\s*min", response, re.IGNORECASE):
        errors.append(f"missing or changed time_min for {title}: {time_min}")

    nutrition = recipe["nutrition_per_serving"]
    plain_response = re.sub(r"[*_`]", "", response)
    expected_values = {
        "kcal": (nutrition["kcal"], r"kcal"),
        "protein": (nutrition["protein"], r"(?:białko|\bB\b)"),
        "fat": (nutrition["fat"], r"(?:tłuszcz|\bT\b)"),
        "carbs": (nutrition["carbs"], r"(?:węglowodan\w*|\bW\b)"),
    }
    for label, (value, label_pattern) in expected_values.items():
        value_pattern = number_pattern(value)
        patterns = (
            rf"{value_pattern}\s*(?:g\s*)?{label_pattern}",
            rf"{label_pattern}\s*[:=-]?\s*{value_pattern}\s*g?",
        )
        if not any(re.search(pattern, plain_response, re.IGNORECASE) for pattern in patterns):
            errors.append(f"missing or changed {label} per serving for {title}: {value}")

    if not recipe.get("ingredients") and re.search(
        r"(?im)^\s*#{0,4}\s*\*{0,2}składniki\s*:?[\*]{0,2}\s*$",
        response,
    ):
        errors.append(f"invented ingredient list for {title}")


def score_case(case: dict[str, Any], response: str, brand_name: str) -> dict[str, Any]:
    expected = case["expected"]
    recommendations = case["tool_result"].get("recommendations", [])
    errors: list[str] = []
    warnings: list[str] = []

    if not response.strip():
        errors.append("empty response")
        return {"passed": False, "errors": errors, "warnings": warnings}

    if re.search(r"https?://|www\.", response, re.IGNORECASE):
        errors.append("response contains a URL")

    for phrase in expected.get("forbidden_terms", []):
        if normalized_text(phrase) in normalized_text(response):
            errors.append(f"forbidden claim or product: {phrase}")

    if expected.get("expect_no_results"):
        no_result_patterns = ("nie znalaz", "nie znalezion", "brak wynik", "nie ma.*propozycji")
        if not any(re.search(pattern, response, re.IGNORECASE) for pattern in no_result_patterns):
            errors.append("missing explicit no-results message")
        if recommendations:
            errors.append("no-results case contains recommendations in tool payload")
    else:
        if not recommendations:
            errors.append("case without recommendations must set expect_no_results")
        for recipe in recommendations:
            _check_recipe_details(recipe, response, errors)

            for sku in recipe.get("used_skus", []):
                sku_name = clean_sku_name(sku["name_pl"])
                if not sku_is_mentioned(sku_name, response):
                    errors.append(f"missing promoted SKU: {sku_name}")
                if normalized_text(brand_name) not in normalized_text(response):
                    errors.append(f"missing brand name for promoted SKU: {brand_name}")

    if not any(marker in normalized_text(response) for marker in POLISH_MARKERS):
        warnings.append("response needs manual Polish-language review")

    return {"passed": not errors, "errors": errors, "warnings": warnings}


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    passed = sum(result["passed"] for result in results)
    warnings = sum(bool(result["warnings"]) for result in results)
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "cases_with_warnings": warnings,
    }


def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    load_dotenv()
    cases = load_cases(args.cases)
    if args.limit:
        cases = cases[: args.limit]

    if args.dry_run:
        return {"dry_run": True, "summary": {"total": len(cases)}, "results": []}

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    results = []
    for case in cases:
        try:
            response = generate_final_answer(client, args.model, case, args.brand_name)
            result = score_case(case, response, args.brand_name)
            results.append({"id": case["id"], "user_message": case["user_message"], "response": response, **result})
        except Exception as exc:
            results.append({
                "id": case["id"],
                "user_message": case["user_message"],
                "response": None,
                "passed": False,
                "errors": [str(exc)],
                "warnings": [],
            })

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
        print(f"Dry run OK. Loaded {summary['total']} final-answer eval cases.")
        return

    print("LLM final-answer eval")
    print("=" * 40)
    print(f"Model: {report['model']}")
    print(f"Cases: {summary['total']}")
    print(f"Passed: {summary['passed']}/{summary['total']} ({summary['pass_rate']:.1%})")
    print(f"Cases with manual-review warnings: {summary['cases_with_warnings']}")
    for result in report["results"]:
        if not result["passed"]:
            print(f"  - {result['id']}: {'; '.join(result['errors'])}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate final LLM answers against controlled backend payloads.")
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
