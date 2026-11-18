from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from core.interpretation_contract import (InterpretationError, InterpretationConfigurationError,
    build_interpretation_request, load_interpretation_schema, parse_interpretation_arguments)
from core.interpretation_compiler import compile_interpretation

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "specs/001-mvp-stabilization/contracts/interpretation-v1.examples.json").read_text(encoding="utf-8"))


def wire(args):
    args = dict(args)
    if args.get("time_max") is None:
        args.pop("time_max", None)
    return args


class InterpretationContractTests(unittest.TestCase):
    def compile_case(self, row):
        return compile_interpretation(parse_interpretation_arguments(
            json.dumps(row["interpretation"], ensure_ascii=False), row["user_message"]))

    def test_all_35_design_cases_compile_to_existing_expected_without_mutation(self):
        before = deepcopy(DATA)
        for row in DATA["valid"]:
            with self.subTest(case=row["id"]):
                result = self.compile_case(row)
                self.assertEqual(result.action, "search" if row["expected_action"] == "tool" else "no_search")
                self.assertEqual(result.arguments, wire(row["expected"]) if "expected" in row else None)
        self.assertEqual(DATA, before)

    def test_every_invalid_design_interpretation_is_rejected_before_compilation(self):
        for row in DATA["invalid"]:
            with self.subTest(case=row["id"]), self.assertRaises(InterpretationError):
                self.compile_case(row)

    def test_duplicate_keys_non_objects_and_invalid_json_are_rejected(self):
        for row in DATA["malformed_json"]:
            with self.subTest(case=row["id"]), self.assertRaises(InterpretationError):
                parse_interpretation_arguments(row["raw_arguments"], "Podaj przepis")
        for raw in (None, "null", '{"contract_version":"IR-1","request_kind":"recipe","facts":[NaN]}',
                    '{"contract_version":"IR-1","request_kind":"recipe","facts":[{"kind":"category","kind":"diet","value":"vegan","status":"required","source":"wegański"}]}'):
            with self.subTest(raw=raw), self.assertRaises(InterpretationError):
                parse_interpretation_arguments(raw, "wegański")

    def test_fact_order_and_duplicates_do_not_change_compilation(self):
        for row in DATA["valid"]:
            changed = deepcopy(row)
            facts = changed["interpretation"]["facts"]
            changed["interpretation"]["facts"] = list(reversed(facts)) + deepcopy(facts)
            with self.subTest(case=row["id"]):
                self.assertEqual(self.compile_case(changed), self.compile_case(row))

    def test_an_invalid_duplicate_is_not_removed_before_validation(self):
        row = deepcopy(next(row for row in DATA["valid"] if row["interpretation"]["facts"]))
        duplicate = dict(row["interpretation"]["facts"][0], source="not from the user")
        row["interpretation"]["facts"].append(duplicate)
        with self.assertRaises(InterpretationError):
            self.compile_case(row)

    def test_added_unsupported_requirement_stops_every_otherwise_searchable_case(self):
        for row in DATA["valid"]:
            if row["expected_action"] != "tool":
                continue
            changed = deepcopy(row)
            changed["user_message"] += ", bez mleka"
            changed["interpretation"]["facts"].append(dict(kind="unsupported", value="exclusion",
                status="required", source="bez mleka"))
            with self.subTest(case=row["id"]):
                result = self.compile_case(changed)
                self.assertEqual(result.action, "no_search")
                self.assertIsNone(result.arguments)

    def test_semantic_omissions_and_wrong_labels_are_not_repaired_using_query_keywords(self):
        for row in DATA["known_limitations"]:
            with self.subTest(case=row["id"]):
                result = self.compile_case(row)
                self.assertEqual(result.arguments, wire(row["illustrative_compiler_result"]))
                self.assertNotEqual(result.arguments, wire(row["gold_expected"]))

    def test_missing_malformed_assets_fail_before_request_construction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing"
            with self.assertRaises(InterpretationConfigurationError):
                load_interpretation_schema(path)
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(InterpretationConfigurationError):
                load_interpretation_schema(path)
            with self.assertRaises(InterpretationConfigurationError):
                build_interpretation_request("Kolacja", "Winiary", prompt_path=path)
            with self.assertRaises(InterpretationConfigurationError):
                build_interpretation_request("Kolacja", "Winiary", prompt_path=path.with_name("absent"))

    def test_request_schema_is_the_single_source_and_each_request_is_independent(self):
        request = build_interpretation_request("CONTROLLED", "Winiary")
        self.assertEqual(request["tools"][0]["function"]["parameters"], load_interpretation_schema())
        request["tools"][0]["function"]["parameters"]["properties"].clear()
        self.assertTrue(build_interpretation_request("CONTROLLED", "Winiary")["tools"][0]["function"]["parameters"]["properties"])
        self.assertEqual(build_interpretation_request("OTHER", "Winiary")["messages"][1]["content"], "OTHER")

    def test_contract_and_compiler_import_without_sdk_database_or_application(self):
        script = "import sys; import core.interpretation_contract; import core.interpretation_compiler; assert not any(n in sys.modules for n in ('openai','sqlalchemy','main'))"
        subprocess.run([sys.executable, "-c", script], cwd=ROOT, check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
