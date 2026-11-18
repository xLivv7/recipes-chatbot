"""Prepare T021 offline. No SDK client, database, credentials, or execution mode.

The resulting manifest is a reviewable plan, not permission or an executor
for paid requests. Historical comparison runners are deliberately unchanged.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.llm_tools import RECIPE_TOOLS
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
from core.tool_call_validation import ToolArgumentsError, parse_recipe_tool_arguments

DIAGNOSTICS = "evals/routing_v5_cases.json"
LEGACY = "evals/routing_pilot_cases.json"
DEVELOPMENT = ("evals/intent_cases.json", "evals/routing_cases.json", "evals/application_routing_cases.json")
SPEC = "specs/001-mvp-stabilization/spec.md"
FROZEN_FILES = ("main.py", "core/llm_tools.py", "core/llm_response_validation.py", "core/recommendation_preferences.py",
    "core/request_safety.py", "core/tool_call_validation.py", "evals/run_llm_eval.py",
    "core/response_renderer.py", "core/recommendation_normalization.py", "core/recommendation_errors.py",
    "evals/run_routing_eval.py", "evals/prepare_routing_v5.py",
    "evals/routing_prompts/V4.txt", "evals/routing_prompts/V5.txt", LEGACY, DIAGNOSTICS,
    *DEVELOPMENT, SPEC, "specs/001-mvp-stabilization/plan.md",
    "specs/001-mvp-stabilization/acceptance.md", "specs/001-mvp-stabilization/tasks.md")
EDITS = (
    ("Wykluczenie mięsa oznacza diet=vegetarian także dla deseru; nie ustawiaj none na podstawie przypuszczenia, że dana kategoria zwykle nie zawiera mięsa.",
     "Samo wykluczenie mięsa domyślnie oznacza diet=vegetarian także dla deseru, z uwzględnieniem jawnej diety lub doprecyzowania ryb; nie ustawiaj none na podstawie przypuszczenia, że dana kategoria zwykle nie zawiera mięsa."),
    ("DIETA: bez mięsa oznacza vegetarian; vegan wyklucza produkty zwierzęce; pescetarian dopuszcza ryby, ale nie wymaga ich.",
     "DIETA: samo „bez mięsa” oznacza domyślnie vegetarian; wykluczenie mięsa z dopuszczeniem lub żądaniem ryby oznacza pescetarian, a jawne „wegańskie bez mięsa” vegan. Doprecyzowanie nie znosi jawnej diety vegetarian/vegan; żądanie wykluczonego przez nią składnika jest sprzecznością. Vegan wyklucza produkty zwierzęce; pescetarian dopuszcza ryby, ale nie wymaga ich."),
)
INTRO = ("PRZYKŁADY: poniżej opisano decyzję dla każdego zapytania. Narzędzie: get_recommendations oznacza jedno rzeczywiste wywołanie z pełnymi argumentami. Narzędzie: brak wywołania i Argumenty: nie dotyczy oznaczają zakończenie bez tool_calls, nie nowe narzędzie ani tekst do wypisania. Komunikat użytkownikowi tworzy aplikacja; brak wywołania nie wymaga tekstowego uzasadnienia ani pytania. Nie zwracaj tego opisu jako wiadomości.")
DEMO_RULES = (
    ("ROU-12", "ROU-17"), ("ROU-12", "ROU-14"), ("ROU-12", "ROU-14"),
    ("ROU-13", "ROU-17"), ("ROU-14",), ("ROU-14",), ("ROU-14",),
    ("ROU-17",), ("ROU-17",), ("ROU-17",), ("ROU-17",), ("ROU-17",), ("ROU-17",),
    ("ROU-07", "NTO-01"), ("NTO-01", "NTO-03"), ("ROU-13", "ROU-16", "NTO-01"),
    ("NTO-01",), ("NTO-01", "NTO-08"),
)
TARGETS = ("intent_004", "intent_010", "intent_032",
           *(f"v5_diag_{i:03d}" for i in range(1, 8)))
CONFIGURATION = dict(model="gpt-4o-mini", temperature=0.1, tool_choice="auto",
    parallel_tool_calls=False, max_completion_tokens=512, max_retries=0, timeout=30,
    endpoint="https://api.openai.com/v1", modes=["raw", "application"])
PRICING = dict(input_usd_per_million=0.15, output_usd_per_million=0.60,
    checked_on="2026-11-17", source="https://developers.openai.com/api/docs/models/gpt-4o-mini",
    note="Standard text rates, no caching; excludes taxes and other account use. Recheck before execution.")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def query_key(query):
    return " ".join(re.sub(r"[^\w\s]", " ", query.casefold()).split())


def wire_args(expected):
    result = dict(expected)
    if result.get("time_max") is None:
        result.pop("time_max", None)
    return result


def load_cases(path):
    cases = read_json(path)
    if not isinstance(cases, list):
        raise ValueError("Expected a list of cases")
    seen = set()
    fields = set(RECIPE_TOOLS[0]["function"]["parameters"]["properties"])
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
            raise ValueError("Missing case id")
        if case["id"] in seen:
            raise ValueError("Duplicate case id")
        seen.add(case["id"])
        if not isinstance(case.get("user_message"), str) or not case["user_message"].strip():
            raise ValueError("Missing standalone query")
        action = case.get("expected_action", "tool")
        if action == "tool":
            expected = case.get("expected")
            if not isinstance(expected, dict) or set(expected) != fields:
                raise ValueError("Expected full canonical arguments, including time_max")
            parse_recipe_tool_arguments(json.dumps(wire_args(expected)))
        elif action != "no_tool" or "expected" in case:
            raise ValueError("Invalid action or arguments attached to no_tool")
    return cases


def split_prompt(prompt):
    head, rest = prompt.split("\nZapytanie: ", 1)
    body, tail = ("Zapytanie: " + rest).split("\nDla obsługiwanej prośby użyj kanału", 1)
    return head, body, "Dla obsługiwanej prośby użyj kanału" + tail


def parse_examples(prompt):
    _, body, _ = split_prompt(prompt)
    lines = body.splitlines()
    if len(lines) % 3:
        raise ValueError("Each example must have query/tool/arguments lines")
    result = []
    for offset in range(0, len(lines), 3):
        values = []
        for line, prefix in zip(lines[offset:offset+3], ("Zapytanie: ", "Narzędzie: ", "Argumenty: ")):
            if not line.startswith(prefix) or not line[len(prefix):].strip():
                raise ValueError("Invalid V4-style example")
            values.append(line[len(prefix):])
        query, tool, arguments = values
        if tool == "get_recommendations":
            args = parse_recipe_tool_arguments(arguments)
        elif tool == "brak wywołania" and arguments == "nie dotyczy":
            args = None
        else:
            raise ValueError("No synthetic no_tool tool or refusal arguments")
        result.append(dict(id=f"D5-{len(result)+1:02d}", query=query,
                           action="tool" if args is not None else "no_tool", arguments=args))
    if len({query_key(row["query"]) for row in result}) != len(result):
        raise ValueError("Duplicate demonstration")
    return result


def validate_prompt(baseline, candidate):
    head, _, tail = split_prompt(baseline)
    candidate_head, _, candidate_tail = split_prompt(candidate)
    for old, new in EDITS:
        if head.count(old) != 1:
            raise ValueError("V4 base differs from the specified instruction edits")
        head = head.replace(old, new)
    head = head[:head.index("PRZYKŁADY:")] + INTRO
    if candidate_head != head or candidate_tail != tail:
        raise ValueError("V5 changed instructions outside the approved scope")
    examples = parse_examples(candidate)
    if len(examples) != len(DEMO_RULES) or sum(e["action"] == "tool" for e in examples) != 14:
        raise ValueError("Expected 18 demonstrations: 14 tool and 4 no_tool")
    # Pairs change only the documented distinction; a legal extra fish is still an error here.
    pairs = ((0, 1, "diet", "vegetarian", "pescetarian"),
             (1, 2, "protein_preference", "none", "fish"),
             (4, 5, "protein_preference", "fish", "meat"),
             (7, 8, "time_max", None, 18), (9, 10, "time_max", 30, 40))
    for left, right, field, first, second in pairs:
        a, b = dict(examples[left]["arguments"]), dict(examples[right]["arguments"])
        if a.pop(field, None) != first or b.pop(field, None) != second or a != b:
            raise ValueError(f"Invalid contrast {left+1}/{right+1}: {field}")
    for example, rules in zip(examples, DEMO_RULES):
        example["rules"] = list(rules)
    return examples


def validate_separation(examples, cases, development):
    ids = [row["id"] for row in cases]
    if len(set(ids)) != len(ids):
        raise ValueError("Case id collision between cohorts")
    demo_queries = {query_key(row["query"]) for row in examples}
    evaluation_queries = {query_key(row["user_message"]) for row in [*cases, *development]}
    if demo_queries & evaluation_queries:
        raise ValueError("Demonstration leaked into diagnostic/development queries")


def guard(case):
    query = case["user_message"]
    return mentions_unsupported_allergy(query) or mentions_unsupported_exclusion(query)


def guard_audit(development, spec):
    rows = [deepcopy(case) for case in development if case["id"] in ("guard_005", "guard_006")]
    for line in spec.splitlines():
        if not line.startswith("| DP-"):
            continue
        cid, query, action, diet, protein, _ = [cell.strip() for cell in line.strip("|").split("|")]
        if cid not in ("DP-02", "DP-03", "DP-22"):
            continue
        if action != "tool":
            raise ValueError("False preflight block was relabelled")
        rows.append(dict(id=cid, user_message=query, expected_action="tool",
            expected=dict(diet=diet, protein_preference=protein, restrictions=[],
                          nutrition_goal="standard", category="kolacja", time_max=None, top_n=3)))
    if len(rows) != 5 or any(row.get("expected_action", "tool") != "tool" for row in rows):
        raise ValueError("Expected all five known false-block probes")
    return [dict(row, preflight_blocked=guard(row)) for row in rows]


def request(prompt, case):
    return dict(model=CONFIGURATION["model"],
        messages=[dict(role="system", content=prompt), dict(role="user", content=case["user_message"])],
        tools=RECIPE_TOOLS, tool_choice="auto", parallel_tool_calls=False,
        temperature=0.1, max_completion_tokens=512)


def build_preparation(root=ROOT):
    prompts = {v: (root / f"evals/routing_prompts/{v}.txt").read_text(encoding="utf-8") for v in ("V4", "V5")}
    examples = validate_prompt(prompts["V4"], prompts["V5"])
    development = [case for name in DEVELOPMENT for case in load_cases(root / name)]
    source = {case["id"]: case for case in development}
    legacy, diagnostic = load_cases(root / LEGACY), load_cases(root / DIAGNOSTICS)
    if len(legacy) != 20 or any(row != source.get(row["id"]) for row in legacy):
        raise ValueError("Historical pilot changed or differs from its source cases")
    if len(diagnostic) != 12 or any(row["id"] in source for row in diagnostic):
        raise ValueError("Expected 12 new diagnostic ids")
    cases = legacy + diagnostic
    validate_separation(examples, cases, development)
    spec = (root / SPEC).read_text(encoding="utf-8")
    known_rules = set(re.findall(r"^\| ((?:ROU|NTO)-\d+) \|", spec, re.M))
    if any(not set(row.get("rules", ())) <= known_rules for row in [*examples, *diagnostic]):
        raise ValueError("Unknown requirement in coverage mapping")
    audit = guard_audit(development, spec)
    if {row["id"] for row in audit} & {row["id"] for row in cases}:
        raise ValueError("Guard audit must be reported separately, without duplicate scores")
    if not set(TARGETS) <= {row["id"] for row in cases}:
        raise ValueError("Missing mandatory semantic target")
    matrix = []
    properties = RECIPE_TOOLS[0]["function"]["parameters"]["properties"]
    for diet in properties["diet"]["enum"]:
        for protein in properties["protein_preference"]["enum"]:
            args = dict(diet=diet, protein_preference=protein, restrictions=[],
                        nutrition_goal="standard", category="kolacja", top_n=3)
            try:
                parse_recipe_tool_arguments(json.dumps(args))
                accepted = True
            except ToolArgumentsError:
                accepted = False
            matrix.append(dict(diet=diet, protein_preference=protein, accepted=accepted))
    schedule = [(attempt, variant, mode) for attempt in (1, 2, 3)
                for variant in (("V5", "V4") if attempt == 2 else ("V4", "V5"))
                for mode in ("raw", "application")]
    calls_per_round = dict(raw=len(cases), application=sum(not guard(row) for row in cases))
    planned_calls = 6 * sum(calls_per_round.values())
    reservation = 0.0
    for _, variant, mode in schedule:
        for case in cases:
            if mode == "application" and guard(case):
                continue
            proxy = len(json.dumps(request(prompts[variant], case), ensure_ascii=False).encode("utf-8")) + 2000
            reservation += (proxy * PRICING["input_usd_per_million"] + 512 * PRICING["output_usd_per_million"]) / 1e6
    checks = dict(examples=examples, valid_tool_examples=14, no_tool_examples=4,
        compatibility_matrix=matrix, legacy_cases=len(legacy), new_cases=len(diagnostic),
        total_cases=len(cases), supported_cases=sum(row.get("expected_action", "tool") == "tool" for row in cases),
        false_blocks_in_measurement=[row["id"] for row in cases if guard(row) and row.get("expected_action", "tool") == "tool"],
        guard_audit_cases=len(audit), guard_audit_false_blocks=sum(row["preflight_blocked"] for row in audit),
        query_separation="normalized queries disjoint; no holdout query inspected")
    manifest = dict(status="offline_prepared", selection_rule="T017-v1", execution_enabled=False,
        approved_budget_usd=None, actual_api_calls=0, actual_database_calls=0,
        configuration=CONFIGURATION, schedule=schedule, semantic_targets=list(TARGETS),
        cohort_ids=dict(regression=[row["id"] for row in legacy], diagnostics=[row["id"] for row in diagnostic],
                        offline_guard_audit=[row["id"] for row in audit]),
        planned_evaluations=len(cases) * len(schedule), planned_api_calls=planned_calls,
        calls_per_variant_per_round=calls_per_round,
        estimated_reservation_usd=reservation, pricing=PRICING,
        cost_note="UTF-8 request bytes + 2000 is an input proxy, not a tokenizer or a billing limit. Output reserve uses 512 tokens; ignores caching. No spending authorised.",
        model_status=dict(documentation="deprecated", checked_on="2026-11-17", source=PRICING["source"],
                          availability_tested=False, preserve_requested_model=True),
        application_status=dict(T022_marked_complete=bool(re.search(r"^- \[x\] \*\*T022\b",
            (root / "specs/001-mvp-stabilization/tasks.md").read_text(encoding="utf-8"), re.M)),
            note="Task state is a declaration, not implementation proof. Re-freeze after any application or runner changes."),
        source_hashes={name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in FROZEN_FILES},
        prompt_hashes={v: hashlib.sha256(text.encode("utf-8")).hexdigest() for v, text in prompts.items()},
        schema_sha256=hashlib.sha256(json.dumps(RECIPE_TOOLS, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        limitations=["No executable paid comparison implemented by this preparer.",
            "Old T016 measurements are not a simultaneous control for V5.",
            "Guard audit stays visible outside the small model-comparison denominator; no MVP acceptance.",
            "Changes concern the entire example set plus the approved instruction edits, not one demonstration."])
    return manifest, checks, prompts, cases, audit


def prepare(directory, root=ROOT):
    manifest, checks, prompts, cases, audit = build_preparation(root)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for name in FROZEN_FILES:
        target = directory / "frozen_inputs" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / name).read_bytes())
    for variant, prompt in prompts.items():
        (directory / f"{variant}.txt").write_text(prompt, encoding="utf-8")
    manifest["prepared_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    manifest["working_tree"] = subprocess.check_output(["git", "status", "--short"], cwd=root, text=True)
    write_json(directory / "manifest.json", manifest)
    write_json(directory / "checks.json", checks)
    write_json(directory / "cases.json", cases)
    write_json(directory / "guard_audit.json", audit)
    write_json(directory / "tool_schema.json", RECIPE_TOOLS)
    (directory / "V4_V5.diff").write_text("".join(difflib.unified_diff(
        prompts["V4"].splitlines(keepends=True), prompts["V5"].splitlines(keepends=True),
        fromfile="V4.txt", tofile="V5.txt")), encoding="utf-8")
    return manifest, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Validate only; no files or requests")
    action.add_argument("--output", type=Path, help="Create a new offline preparation directory")
    args = parser.parse_args()
    manifest, checks = (build_preparation()[:2] if args.check else prepare(args.output))
    print(json.dumps(dict(status=manifest["status"], examples=len(checks["examples"]),
        cases=checks["total_cases"], supported_cases=checks["supported_cases"],
        planned_evaluations=manifest["planned_evaluations"], planned_api_calls=manifest["planned_api_calls"],
        guard_audit_false_blocks=checks["guard_audit_false_blocks"],
        estimated_reservation_usd=manifest["estimated_reservation_usd"],
        actual_api_calls=0, execution_enabled=False), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
