"""Conservative lexical preflight for requests outside catalog scope."""

import re
import unicodedata


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


_EXCLUSION_START = re.compile(
    r"\b(?:bez|without|wykluczam|wyklucz|unikam|z\s+(?:wykluczeniem|wylaczeniem)"
    r"|nie\s+(?:jem|spozywam|moge\s+(?:jesc|spozywac)))\b"
)
_JOINERS = {"i", "oraz", "ani", "lub", "albo", "/", "+", "&"}
_SUPPORTED_HEADS = {"glutenu", "laktozy", "miesa"}
_GENERAL_PHRASES = (("ograniczen",), ("preferencji",), ("znaczenia",),
                    ("limitu", "czasu"))
_NEW_CLAUSE_STARTS = {"ale", "poprosze", "prosze", "podaj", "znajdz", "na", "do",
                      "sniadanie", "lunch", "obiad", "kolacja", "deser", "przekaska"}


def _plain_polish(value: str) -> str:
    value = value.casefold().replace("\u0142", "l")
    return "".join(char for char in unicodedata.normalize("NFKD", value)
                   if not unicodedata.combining(char))


def mentions_unsupported_exclusion(user_message: str) -> bool:
    """Recognize a limited exclusion grammar, rejecting unsupported clauses.

    Negated unsupported exclusions are deliberately rejected too. This is not
    general parsing: see docs/unsupported_exclusions_contract.md for limits.
    """
    text = _plain_polish(user_message)
    for word in re.findall(r"\bbez\w+\b", text):
        if not re.fullmatch(r"bez(?:glutenow|laktozow|piecz|wzgled)\w*", word):
            return True
    all_heads = set()
    for match in _EXCLUSION_START.finditer(text):
        tokens = re.findall(r"\w+|[^\w\s]", text[match.end():])
        if match.group() == "bez" and any(
                tuple(tokens[:len(phrase)]) == phrase for phrase in _GENERAL_PHRASES):
            continue
        index = 0
        while True:
            if index >= len(tokens):
                return True
            head = tokens[index]
            if tokens[index:index + 2] == ["produktow", "miesnych"]:
                head = "miesa"
                index += 1
            if head not in _SUPPORTED_HEADS | {"ryb"}:
                return True
            all_heads.add(head)
            index += 1
            # Inspect explicit coordinated exclusions; separate "bez" clauses
            # are checked independently by the outer loop.
            if index < len(tokens) and tokens[index] in _JOINERS:
                index += 1
                if index < len(tokens) and tokens[index] == "bez":
                    break
                continue
            if index < len(tokens) and tokens[index] == ",":
                next_index = index + 1
                if next_index < len(tokens) and tokens[next_index] in _JOINERS:
                    next_index += 1
                if next_index < len(tokens) and tokens[next_index] == "bez":
                    break
                # Only explicit new-clause starters end a comma-separated list.
                # Other ambiguous tails are rejected rather than silently lost.
                if next_index < len(tokens) and tokens[next_index] not in _NEW_CLAUSE_STARTS:
                    index = next_index
                    continue
            break
    return "ryb" in all_heads and "miesa" not in all_heads
