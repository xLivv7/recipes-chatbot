"""Freeze the T026 candidate offline. This module cannot execute a paid campaign."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from core.interpretation_contract import CLIENT_CONFIGURATION, CONTRACT_VERSION, build_interpretation_request


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_paths(root=ROOT):
    spec = "specs/001-mvp-stabilization/"
    return sorted({"main.py", "requirements.txt", "evals/prepare_interpretation_v1.py",
        "core/prompts/IR1.txt", *(str(path.relative_to(root)).replace("\\", "/") for path in (root / "core").rglob("*.py")),
        *(spec + name for name in ("spec.md", "plan.md", "tasks.md", "acceptance.md", "interpretation-contract.md",
                                   "contracts/interpretation-v1.schema.json", "contracts/interpretation-v1.examples.json"))})


def prepare(directory, root=ROOT):
    directory = Path(directory)
    spec = "specs/001-mvp-stabilization/"
    sources = source_paths(root)
    request = build_interpretation_request("CONTROLLED_QUERY_PLACEHOLDER", "Winiary",
        schema_path=root / spec / "contracts/interpretation-v1.schema.json", prompt_path=root / "core/prompts/IR1.txt")
    hashes = {name: digest(root / name) for name in sources}
    directory.mkdir(parents=True, exist_ok=False)
    for name in sources:
        destination = directory / "frozen_inputs" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((root / name).read_bytes())
    configuration = dict(CLIENT_CONFIGURATION, **{key: request[key] for key in
        ("model", "temperature", "parallel_tool_calls", "max_completion_tokens", "tool_choice")})
    save(directory / "configuration.json", configuration)
    save(directory / "schema.json", request["tools"][0]["function"]["parameters"])
    (directory / "IR1.txt").write_text(request["messages"][0]["content"], encoding="utf-8")
    save(directory / "request_template.json", request)
    manifest = dict(task="T026", contract_version=CONTRACT_VERSION, status="offline_prepared",
        execution_enabled=False, not_a_campaign_plan=True, actual_api_calls=0, actual_database_calls=0,
        approved_budget_usd=None, cost_estimated=False, active_mode="legacy", active_prompt="V0",
        model_quality_measured=False, source_hashes=hashes,
        artifact_hashes={name: digest(directory / name) for name in ("configuration.json", "schema.json", "IR1.txt", "request_template.json")},
        runtime=dict(python=platform.python_version(), openai=importlib.metadata.version("openai")),
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
        working_tree=subprocess.check_output(["git", "status", "--short"], cwd=root).decode(),
        limitations=["Not a model measurement, not production qualification.",
                     "T027 requires fresh control payloads, label review, cost estimate and explicit approval."])
    save(directory / "manifest.json", manifest)
    return manifest


def validate_preparation(directory, root=ROOT):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("task") != "T026" or manifest.get("contract_version") != CONTRACT_VERSION
            or manifest.get("execution_enabled") is not False or manifest.get("not_a_campaign_plan") is not True
            or manifest.get("actual_api_calls") != 0 or manifest.get("actual_database_calls") != 0
            or manifest.get("approved_budget_usd") is not None or manifest.get("model_quality_measured") is not False
            or set(manifest["source_hashes"]) != set(source_paths(root))
            or set(manifest["artifact_hashes"]) != {"configuration.json", "schema.json", "IR1.txt", "request_template.json"}):
        raise ValueError("Invalid offline candidate manifest")
    for name, expected in manifest["source_hashes"].items():
        if digest(root / name) != expected or digest(directory / "frozen_inputs" / name) != expected:
            raise ValueError("Candidate source changed: " + name)
    for name, expected in manifest["artifact_hashes"].items():
        if digest(directory / name) != expected:
            raise ValueError("Candidate artifact changed: " + name)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = prepare(args.output)
    print(json.dumps(dict(status=manifest["status"], source_files=len(manifest["source_hashes"]),
                          execution_enabled=False, actual_api_calls=0), indent=2))


if __name__ == "__main__":
    main()
