"""Compile validated IR-1 facts to the existing recommendation boundary."""
from dataclasses import dataclass
import json

from core.interpretation_contract import Interpretation
from core.tool_call_validation import parse_recipe_tool_arguments


@dataclass(frozen=True)
class Compilation:
    action: str
    arguments: dict | None = None


def compile_interpretation(interpretation: Interpretation) -> Compilation:
    if not isinstance(interpretation, Interpretation):
        raise TypeError("Compile a validated Interpretation")
    facts = {(fact.kind, fact.value, fact.status) for fact in interpretation.facts}
    no_search = Compilation("no_search")
    if any(kind == "unsupported" and (value == "allergy" or status == "required")
           for kind, value, status in facts):
        return no_search
    if interpretation.request_kind != "recipe":
        return no_search
    if any((kind, value, "waived") in facts for kind, value, status in facts if status == "required"):
        return no_search
    required = {}
    for kind, value, status in facts:
        if status == "required":
            required.setdefault(kind, set()).add(value)
    if any(len(required.get(kind, ())) > 1 for kind in
           ("diet", "category", "nutrition_goal", "result_count", "time_limit", "protein")):
        return no_search
    exclusions = required.get("exclusion", set())
    protein = next(iter(required.get("protein", ())), "none")
    if protein in exclusions or "fish" in exclusions and "meat" not in exclusions:
        return no_search
    explicit_diet = next(iter(required.get("diet", ())), None)
    if explicit_diet == "pescetarian" and "fish" in exclusions:
        return no_search
    if explicit_diet is not None:
        diet = explicit_diet
    elif "meat" in exclusions:
        fish_permitted = ("protein", "fish", "permitted") in facts
        diet = ("vegetarian" if "fish" in exclusions else
                "pescetarian" if protein == "fish" or fish_permitted else "vegetarian")
    else:
        diet = "none"
    if ((diet in {"vegetarian", "vegan"} and protein != "none")
            or diet == "pescetarian" and protein == "meat"):
        return no_search
    args = dict(diet=diet, protein_preference=protein,
                restrictions=[restriction for value, restriction in
                    (("gluten", "gluten_free"), ("lactose", "lactose_free")) if value in exclusions],
                nutrition_goal=next(iter(required.get("nutrition_goal", ())), "standard"),
                category=next(iter(required.get("category", ())), "kolacja"),
                top_n=next(iter(required.get("result_count", ())), 3))
    time_limit = next(iter(required.get("time_limit", ())), None)
    if time_limit is not None:
        args["time_max"] = time_limit
    elif "quick" in required:
        args["time_max"] = 30
    # This is the same final boundary as legacy; never repair its result.
    return Compilation("search", parse_recipe_tool_arguments(json.dumps(args, ensure_ascii=False)))
