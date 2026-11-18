"""T029 offline replay of the completed T027 IR-1 observations. Writes JSON to stdout."""
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

from core.interpretation_adapter import decode_interpretation_response
from evals.run_interpretation_diagnostic import namespace, score


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "dokumentacja pracy/2026-11-18_t027/campaign"
INPUT_HASHES = {
    "results.json": "2a7218e2876b254fdde619c97066f1584efc40d38bf3cd88506b9043bca3cda8",
    "cases.json": "bd77a609b085b0f381505e837457d1942ec01d284a5ccb63aee6130b13868c6d",
}


def frozen_input(name):
    data = (CAMPAIGN / name).read_bytes()
    if sha256(data).hexdigest() != INPUT_HASHES[name]:
        raise ValueError(f"T027 input differs from the completed campaign: {name}")
    return json.loads(data)


def offline_application():
    # main loads a catalog and creates a default SDK client at import time.
    # Load its real functions with both external dependencies substituted.
    spec = importlib.util.spec_from_file_location("t029_application", ROOT / "main.py")
    app = importlib.util.module_from_spec(spec)
    catalog = SimpleNamespace(get_recommendations=Mock(side_effect=AssertionError("Unexpected lookup")))
    with patch.dict(sys.modules, {"core.recommendations": catalog}), patch("openai.OpenAI"), patch("dotenv.load_dotenv"):
        spec.loader.exec_module(app)
    return app


def evaluate(trace, args, case):
    return score(dict(effective_action=trace["effective_action"], actual=args,
                      failure_stage=trace["failure_stage"]), case)


def replay():
    cases = {r["id"]: r for r in frozen_input("cases.json")}
    rows = [r for r in frozen_input("results.json")["results"] if r["variant"] == "IR1"]
    app = offline_application()
    observations = []
    for row in rows:
        case = cases[row["id"]]
        text = case["user_message"]
        response = namespace(row["provider_response"])
        raw = decode_interpretation_response(response, text, checked=True)
        raw_score = evaluate(raw.diagnostics, raw.arguments, case)

        client = Mock()
        client.chat.completions.create.return_value = response
        trace = {}
        with patch.object(app, "run_recommendation_tool", return_value={"query": {}, "recommendations": []}) as lookup:
            message = app.chat_with_bot(text, "Winiary", interpretation_mode="facts_checked_v1",
                                        interpretation_client=client, diagnostics=trace)
        args = lookup.call_args.args[0] if lookup.called else None
        application = evaluate(trace, args, case)
        assert trace["backend_calls"] == lookup.call_count == int(application["effective_action"] == "tool")
        assert client.chat.completions.create.call_count == int(trace["guard"] is None)
        if trace["guard"]:
            assert message == app.UNSUPPORTED_EXCLUSION_RESPONSE and not trace["block_search"]
        elif trace["block_search"]:
            assert message == app.INVALID_TOOL_RESPONSE and trace["failure_stage"] == "coverage"
            assert trace["protocol_valid"] and trace["validation_status"] == "valid"
            assert all(value is None for value in application["field_results"].values())
        elif application["effective_action"] == "no_tool":
            assert message == app.NO_TOOL_RESPONSE
        observations.append(dict(id=row["id"], attempt=row["attempt"], raw=raw_score, application=application,
            model_passed=row["raw"]["passed"], facts_exact=row["facts"]["signature_exact"],
            baseline_application_passed=row["application_replay"]["passed"], guard=trace["guard"],
            raw_findings=raw.diagnostics["findings"], application_status=trace["completeness_status"],
            fake_dispatches=lookup.call_count))
    totals = {}
    for scope, baseline in (("raw", "model_passed"), ("application", "baseline_application_passed")):
        stopped = [r for r in observations if r[scope]["failure_stage"] == "coverage"]
        totals[scope] = dict(
            passed=sum(r[scope]["passed"] for r in observations),
            stopped_incorrect=sum(not r[baseline] for r in stopped),
            false_blocks=sum(r[baseline] for r in stopped),
            incorrect_dispatches=sum(r[scope]["effective_action"] == "tool" and not r[scope]["passed"] for r in observations),
            actions=dict(Counter(r[scope]["effective_action"] for r in observations)))
    return dict(policy="CMP-1", input_sha256=INPUT_HASHES, real_model_requests=0, real_backend_calls=0,
                model_passed=sum(r["model_passed"] for r in observations),
                facts_exact=sum(r["facts_exact"] for r in observations),
                preflight=sum(bool(r["guard"]) for r in observations), totals=totals, observations=observations)


if __name__ == "__main__":
    report = replay()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    for scope, passed, stopped in (("raw", 22, 14), ("application", 25, 11)):
        counts = report["totals"][scope]
        if (len(report["observations"]) != 36 or counts["passed"] != passed or
                counts["stopped_incorrect"] != stopped or counts["incorrect_dispatches"] or counts["false_blocks"]):
            raise SystemExit(f"CMP-10 failed in {scope}")
