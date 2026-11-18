"""IR-1 assets and validation. No SDK, application, catalog or environment access."""
from dataclasses import dataclass
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "specs/001-mvp-stabilization/contracts/interpretation-v1.schema.json"
PROMPT_PATH = Path(__file__).with_name("prompts") / "IR1.txt"
CONTRACT_VERSION = "IR-1"
TOOL_NAME = "submit_recipe_interpretation"
CLIENT_CONFIGURATION = dict(base_url="https://api.openai.com/v1", max_retries=0, timeout=30)
MODEL_CONFIGURATION = dict(model="gpt-4o-mini", temperature=0.1, parallel_tool_calls=False,
                           max_completion_tokens=1024)
FACT_KINDS = {"diet", "exclusion", "protein", "nutrition_goal", "category", "time_limit",
              "quick", "result_count", "unsupported"}


class InterpretationError(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


class InterpretationConfigurationError(RuntimeError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class Fact:
    kind: str
    value: str | int
    status: str
    source: str


@dataclass(frozen=True)
class Interpretation:
    request_kind: str
    facts: tuple[Fact, ...]
    contract_version: str = CONTRACT_VERSION


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InterpretationError("duplicate_json_key")
        result[key] = value
    return result


def _invalid_constant(value):
    raise InterpretationError("invalid_json")


def _valid_schema(node):
    if not isinstance(node, dict):
        return False
    if "anyOf" in node:
        branches = node["anyOf"]
        return (set(node) == {"anyOf"} and isinstance(branches, list) and bool(branches)
                and all(_valid_schema(branch) for branch in branches))
    kind = node.get("type")
    if kind == "object":
        properties, required = node.get("properties"), node.get("required")
        return (set(node) == {"type", "properties", "required", "additionalProperties"}
                and node["additionalProperties"] is False and isinstance(properties, dict)
                and isinstance(required, list) and all(isinstance(key, str) for key in required)
                and len(required) == len(set(required)) and set(required) == set(properties)
                and all(_valid_schema(child) for child in properties.values()))
    if kind == "array":
        return set(node) == {"type", "items"} and _valid_schema(node["items"])
    if kind == "integer":
        return set(node) == {"type"}
    if kind == "string":
        return (set(node) <= {"type", "enum"} and
                ("enum" not in node or isinstance(node["enum"], list) and bool(node["enum"])
                 and all(isinstance(value, str) for value in node["enum"])))
    return False


def load_interpretation_schema(path=None):
    try:
        schema = json.loads(Path(path or SCHEMA_PATH).read_text(encoding="utf-8"),
                            object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise InterpretationConfigurationError("unreadable_ir_schema") from exc
    if not _valid_schema(schema) or schema.get("type") != "object":
        raise InterpretationConfigurationError("invalid_ir_schema")
    properties = schema["properties"]
    if (set(properties) != {"contract_version", "request_kind", "facts"}
            or properties["contract_version"].get("enum") != [CONTRACT_VERSION]
            or properties["facts"].get("type") != "array"):
        raise InterpretationConfigurationError("invalid_ir_schema")
    branches = properties["facts"]["items"].get("anyOf", [])
    tags = []
    for branch in branches:
        fields = branch.get("properties", {})
        tag = fields.get("kind", {}).get("enum", [])
        if set(fields) != {"kind", "value", "status", "source"} or len(tag) != 1:
            raise InterpretationConfigurationError("invalid_ir_schema")
        tags.extend(tag)
    if len(tags) != len(FACT_KINDS) or set(tags) != FACT_KINDS:
        raise InterpretationConfigurationError("invalid_ir_schema")
    return schema


def _matches(value, schema):
    if "anyOf" in schema:
        return any(_matches(value, branch) for branch in schema["anyOf"])
    kind = schema["type"]
    if kind == "object":
        return (isinstance(value, dict) and set(value) == set(schema["properties"])
                and all(_matches(item, schema["properties"][key]) for key, item in value.items()))
    if kind == "array":
        return isinstance(value, list) and all(_matches(item, schema["items"]) for item in value)
    if kind == "integer":
        return type(value) is int
    return isinstance(value, str) and ("enum" not in schema or value in schema["enum"])


def parse_interpretation_arguments(raw, user_message, schema=None):
    if not isinstance(user_message, str):
        raise TypeError("user_message must be text")
    if not isinstance(raw, str):
        raise InterpretationError("expected_json_text")
    try:
        value = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (ValueError, RecursionError) as exc:
        if isinstance(exc, InterpretationError):
            raise
        raise InterpretationError("invalid_json") from exc
    schema = load_interpretation_schema() if schema is None else schema
    if not _matches(value, schema):
        raise InterpretationError("invalid_interpretation_shape")
    facts = []
    for item in value["facts"]:
        if not item["source"].strip() or item["source"] not in user_message:
            raise InterpretationError("invalid_fact_source")
        if item["kind"] in {"time_limit", "result_count"} and item["value"] <= 0:
            raise InterpretationError("nonpositive_fact_value")
        facts.append(Fact(**item))
    return Interpretation(value["request_kind"], tuple(facts), value["contract_version"])


def build_interpretation_request(user_message, brand_name, *, schema_path=None, prompt_path=None):
    schema = load_interpretation_schema(schema_path)
    try:
        prompt = Path(prompt_path or PROMPT_PATH).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InterpretationConfigurationError("unreadable_ir_prompt") from exc
    if not prompt.strip() or "{{brand_name}}" not in prompt:
        raise InterpretationConfigurationError("invalid_ir_prompt")
    return dict(MODEL_CONFIGURATION,
        messages=[dict(role="system", content=prompt.replace("{{brand_name}}", brand_name)),
                  dict(role="user", content=user_message)],
        tools=[dict(type="function", function=dict(name=TOOL_NAME,
            description="Przekazuje fakty z zapytania do walidacji; nie wyszukuje przepisów.",
            strict=True, parameters=schema))],
        tool_choice=dict(type="function", function=dict(name=TOOL_NAME)))
