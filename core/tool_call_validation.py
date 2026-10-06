"""Validate the recipe tool boundary without coercing model arguments."""

import json

from core.llm_tools import RECIPE_TOOLS
from core.recommendation_preferences import validate_preference_contract


class ToolArgumentsError(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ToolArgumentsError("Duplicate JSON key.")
        result[key] = value
    return result


def parse_recipe_tool_arguments(raw):
    if not isinstance(raw, str):
        raise ToolArgumentsError("Expected JSON text.")
    try:
        args = json.loads(raw, object_pairs_hook=_unique_object)
    except (ValueError, RecursionError) as exc:
        raise ToolArgumentsError("Invalid JSON arguments.") from exc
    schema = RECIPE_TOOLS[0]["function"]["parameters"]
    properties = schema["properties"]
    if not isinstance(args, dict):
        raise ToolArgumentsError("Expected an argument object.")
    if set(args).difference(properties) or set(schema["required"]).difference(args):
        raise ToolArgumentsError("Unknown or missing arguments.")
    for key, value in args.items():
        field = properties[key]
        if field["type"] == "string":
            if not isinstance(value, str) or value not in field["enum"]:
                raise ToolArgumentsError("Invalid enum value.")
        elif field["type"] == "integer":
            if type(value) is not int or value < field["minimum"]:
                raise ToolArgumentsError("Expected a positive integer.")
        elif field["type"] == "array":
            if (not isinstance(value, list) or len(value) > field["maxItems"]
                    or any(not isinstance(item, str) or item not in field["items"]["enum"] for item in value)
                    or len(set(value)) != len(value)):
                raise ToolArgumentsError("Invalid restrictions list.")
    try:
        validate_preference_contract(args["diet"], args["protein_preference"], args["restrictions"])
    except ValueError as exc:
        raise ToolArgumentsError("Conflicting preferences.") from exc
    return args
