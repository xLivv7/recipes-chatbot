from __future__ import annotations

from collections.abc import Iterable


DIETS = ("none", "vegetarian", "vegan", "pescetarian")
PROTEIN_PREFERENCES = ("none", "meat", "fish")
SUPPORTED_RESTRICTIONS = ("gluten_free", "lactose_free")


def validate_preference_contract(
    diet: str,
    protein_preference: str,
    restrictions: Iterable[str] | None,
) -> list[str]:
    if diet not in DIETS:
        raise ValueError(f"Unsupported diet: {diet}")
    if protein_preference not in PROTEIN_PREFERENCES:
        raise ValueError(f"Unsupported protein preference: {protein_preference}")

    normalized_restrictions = []
    for restriction in restrictions or []:
        if not isinstance(restriction, str) or not restriction.strip():
            raise ValueError("Restrictions must be non-empty strings.")
        normalized_restrictions.append(restriction.strip())

    unsupported = sorted(set(normalized_restrictions).difference(SUPPORTED_RESTRICTIONS))
    if unsupported:
        raise ValueError(f"Unsupported restrictions: {unsupported}")

    if diet in {"vegetarian", "vegan"} and protein_preference != "none":
        raise ValueError(f"Diet '{diet}' cannot be combined with protein preference '{protein_preference}'.")
    if diet == "pescetarian" and protein_preference == "meat":
        raise ValueError("Pescetarian diet cannot be combined with meat preference.")

    return list(dict.fromkeys(normalized_restrictions))
