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
                      "chce", "sniadanie", "lunch", "obiad", "kolacja", "deser", "przekaska"}
_CLAUSE_PREFIXES = (("ryby", "moga", "byc"), ("ryby", "sa", "dozwolone"),
                    ("nie", "musi", "byc", "z"), ("nie", "musza", "byc", "z"))
_QUICK_MEAL_MODIFIERS = {"szybki", "szybka", "szybkie", "ekspresowy", "ekspresowa", "ekspresowe"}
_MEAL_HEADS = {"sniadanie", "lunch", "obiad", "kolacja", "kolacje", "deser", "przekaska", "przekaske"}
_OPTIONAL_EXCLUSION = re.compile(r"\bnie\s+mus(?:i|za)\s+byc\s*$")
_QUOTE_MARKS = "\"'„”“«»`"


def _plain_polish(value: str) -> str:
    value = value.casefold().replace("\u0142", "l")
    return "".join(char for char in unicodedata.normalize("NFKD", value)
                   if not unicodedata.combining(char))


def _starts_meal_clause(tokens: list[str], index: int) -> bool:
    tail = tokens[index:]
    if not tail:
        return False
    return (tail[0] in _MEAL_HEADS
            or (len(tail) >= 2 and tail[0] in _QUICK_MEAL_MODIFIERS and tail[1] in _MEAL_HEADS))


def _starts_new_clause(tokens: list[str], index: int) -> bool:
    tail = tokens[index:]
    if not tail:
        return False
    return (tail[0] in _NEW_CLAUSE_STARTS
            or any(tuple(tail[:len(prefix)]) == prefix for prefix in _CLAUSE_PREFIXES)
            or _starts_meal_clause(tokens, index))


def mentions_unsupported_exclusion(user_message: str) -> bool:
    """Recognize a limited exclusion grammar, rejecting unsupported clauses.

    Only a local "nie musi/musza byc bez" waives one exclusion head.
    Other negations, quoted optional exclusions and ambiguous lists remain
    conservative. See docs/reference/contracts/unsupported_exclusions_contract.md.
    """
    text = _plain_polish(user_message)
    for word in re.findall(r"\bbez\w+\b", text):
        if not re.fullmatch(r"bez(?:glutenow|laktozow|piecz|wzgled)\w*", word):
            return True
    all_heads = set()
    for match in _EXCLUSION_START.finditer(text):
        tokens = re.findall(r"\w+|[^\w\s]", text[match.end():])
        optional_first_head = (match.group() == "bez"
                               and _OPTIONAL_EXCLUSION.search(text[:match.start()]) is not None
                               and not any(mark in text for mark in _QUOTE_MARKS))
        if match.group() == "bez" and any(
                tuple(tokens[:len(phrase)]) == phrase for phrase in _GENERAL_PHRASES):
            continue
        index = 0
        while True:
            if index >= len(tokens):
                return True
            head = tokens[index]
            optional_head = optional_first_head and index == 0 and head.isalpha()
            if tokens[index:index + 2] == ["produktow", "miesnych"]:
                head = "miesa"
                index += 1
            if head not in _SUPPORTED_HEADS | {"ryb"} and not optional_head:
                return True
            if not optional_head:
                all_heads.add(head)
            index += 1
            # Inspect explicit coordinated exclusions; separate "bez" clauses
            # are checked independently by the outer loop.
            if index < len(tokens) and tokens[index] in _JOINERS:
                joiner = tokens[index]
                index += 1
                if index < len(tokens) and tokens[index] == "bez":
                    break
                if joiner in {"i", "oraz"} and _starts_meal_clause(tokens, index):
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
                if next_index < len(tokens) and not _starts_new_clause(tokens, next_index):
                    index = next_index
                    continue
            break
    return "ryb" in all_heads and "miesa" not in all_heads
