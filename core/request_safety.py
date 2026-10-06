"""Conservative preflight for allergy-related requests outside catalog scope."""

import re


_ALLERGY_MENTION = re.compile(
    r"\b(?:\w*(?:alerg|allerg)\w*|uczul\w*|anafilak\w*|anaphyla\w*)\b",
    re.IGNORECASE,
)


def mentions_unsupported_allergy(user_message: str) -> bool:
    """Block mentions, including negations; do not infer an allergy diagnosis.

    This lexical policy is intentionally not a complete language classifier.
    No supported restriction is a replacement for an allergy request.
    """
    return bool(_ALLERGY_MENTION.search(user_message))
