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

    tokens = re.findall(r"\w+", normalized_name)
    suffixes = {"sos": "(?:u|em|ie)?", "przyprawa": "(?:a|ę|y|ie|ą)",
                "pomidorowy": "(?:y|ego|ym)", "ziołowy": "(?:y|ej|ą|ego|ym)"}
    patterns = []
    for token in tokens:
        stem = token[:-1] if token in ("przyprawa", "pomidorowy", "ziołowy") else token
        if token.endswith("owa"):
            patterns.append(re.escape(token[:-1]) + "(?:a|ej|ą)")
        else:
            patterns.append(re.escape(stem) + suffixes.get(token, ""))
    return bool(patterns) and bool(re.search(r"\b" + r"\s+".join(patterns) + r"\b", normalized_response))


def recipe_section(response: str, title: str, all_titles: list[str]) -> str:
    title_match = re.search(re.escape(title), response, re.IGNORECASE)
    if not title_match:
        return ""

    next_positions = []
    for other_title in all_titles:
        if other_title == title:
            continue
        match = re.search(re.escape(other_title), response[title_match.end():], re.IGNORECASE)
        if match:
            next_positions.append(title_match.end() + match.start())

    end = min(next_positions) if next_positions else len(response)
    return response[title_match.start():end]


def check_recipe_headings(response: str, recipe_titles: list[str], errors: list[str]) -> None:
    section_headings = ("składniki", "przygotowanie", "wartości odżywcze", "makro")
    for heading in re.findall(r"(?m)^#{2,3}\s+(.+?)\s*$", response):
        cleaned = re.sub(r"^\d+[.)]\s*", "", heading).strip(" *")
        if normalized_text(cleaned) in section_headings:
            continue
        if not any(normalized_text(title) == normalized_text(cleaned) for title in recipe_titles):
            errors.append(f"unknown recipe heading: {cleaned}")


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
        numeric = r"(?<![\d.,])(\d+(?:[.,]\d+)?)(?![\d.,])"
        claim_patterns = [rf"{numeric}\s*kcal\b"] if label == "kcal" else [
            rf"{label_pattern}\s*[:=]\s*{numeric}\s*g\b",
            rf"{numeric}\s*g\s*{label_pattern}\b",
        ]
        claims = [float(match.replace(",", ".")) for pattern in claim_patterns
                  for match in re.findall(pattern, plain_response, re.IGNORECASE)]
        if any(claim != value for claim in claims):
            errors.append(f"unexpected {label} value for {title}")

    if not recipe.get("ingredients") and re.search(
        r"(?im)^\s*#{0,4}\s*\*{0,2}składniki\s*:?[\*]{0,2}\s*$",
        response,
    ):
        errors.append(f"invented ingredient list for {title}")

    if not recipe.get("steps_pl") and re.search(
        r"(?im)^\s*#{0,4}\s*\*{0,2}przygotowanie\s*:?[\*]{0,2}\s*$",
        response,
    ):
        errors.append(f"invented preparation section for {title}")

    servings_match = re.search(r"(?:porcje|porcji)\s*[:=-]?\s*(\d+)", plain_response, re.IGNORECASE)
    if servings_match and int(servings_match.group(1)) != recipe["servings"]:
        errors.append(f"changed servings for {title}: {servings_match.group(1)}")


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
        recipe_titles = [recipe["title_pl"] for recipe in recommendations]
        check_recipe_headings(response, recipe_titles, errors)
        for recipe in recommendations:
            section = recipe_section(response, recipe["title_pl"], recipe_titles)
            _check_recipe_details(recipe, section, errors)
            allowed_names = [item["name_pl"] for item in recipe.get("ingredients", [])]
            allowed_names += [item["name_pl"] for item in recipe.get("used_skus", [])]
            ingredient_block = re.search(
                r"(?ims)^\s*(?:#{1,6}\s*)?\*{0,2}składniki\s*:?\*{0,2}\s*\n(.*?)(?=\n\s*(?:#{1,6}\s|\*\*|---)|\Z)", section)
            if ingredient_block:
                for item in re.findall(r"(?m)^\s*[-*]\s+(.+)$", ingredient_block.group(1)):
                    item = re.sub(r"\b" + re.escape(brand_name) + r"\b", "", item, flags=re.IGNORECASE).strip()
                    item = re.sub(r"\s*[-:(]?\s*\d+(?:[.,]\d+)?\s*g\)?\s*$", "", item).strip()
                    if not any(sku_is_mentioned(name, item) for name in allowed_names):
                        errors.append(f"unknown ingredient for {recipe['title_pl']}: {item}")
            for product in re.findall(r"\b" + re.escape(brand_name) + r"\s+([^.!\n]+)", section, re.IGNORECASE):
                if not any(sku_is_mentioned(sku["name_pl"], product) for sku in recipe.get("used_skus", [])):
                    errors.append(f"unknown branded product for {recipe['title_pl']}: {product.strip()}")

            for sku in recipe.get("used_skus", []):
                sku_name = clean_sku_name(sku["name_pl"])
                if not sku_is_mentioned(sku_name, section):
                    errors.append(f"missing promoted SKU: {sku_name}")
                if normalized_text(brand_name) not in normalized_text(section):
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
