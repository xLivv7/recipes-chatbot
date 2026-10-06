"""Offline exact-output evaluation of the current deterministic renderer."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.response_renderer import ResponsePayloadError, render_recommendations

DEFAULT_CASES_PATH = Path(__file__).with_name("renderer_cases.json")
DEFAULT_REPORT_PATH = Path(__file__).with_name("renderer_eval_report.json")


def run_eval(path, brand_name="Winiary"):
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("Expected non-empty case list.")
    ids = set()
    results = []
    for case in cases:
        if not case.get("id") or case["id"] in ids:
            raise ValueError("Missing or duplicate case id.")
        ids.add(case["id"])
        if ("expected_response" in case) == (case.get("expected_error") is True):
            raise ValueError("Specify exactly one expected response or error.")
        try:
            response = render_recommendations(case["tool_result"], brand_name)
            passed = response == case.get("expected_response")
            results.append({"id": case["id"], "passed": passed, "response": response})
        except ResponsePayloadError as exc:
            results.append({"id": case["id"], "passed": case.get("expected_error") is True,
                            "error": str(exc)})
    passed = sum(result["passed"] for result in results)
    return {"evaluation_kind": "offline_renderer_exact_output", "api_calls": 0,
            "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed},
            "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    report = run_eval(args.cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(f"Offline renderer eval: {summary['passed']}/{summary['total']}; API calls: 0")
    for result in report["results"]:
        if not result["passed"]:
            print(f"Failed: {result['id']}")
    return int(bool(summary["failed"]))


if __name__ == "__main__":
    raise SystemExit(main())
