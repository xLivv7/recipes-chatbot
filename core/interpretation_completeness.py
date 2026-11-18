"""CMP-1 checks a proposed search against the explicit cues in the current message."""
from dataclasses import dataclass
import re
import unicodedata

from core.interpretation_compiler import Compilation
from core.interpretation_contract import Interpretation


POLICY_VERSION = "CMP-1"
_CATEGORIES = {
    "śniadanie": "śniadanie śniadania śniadaniu śniadań",
    "lunch": "lunch lunchu lunche lunchów",
    "obiad": "obiad obiadu obiadów obiady",
    "kolacja": "kolacja kolację kolacji kolacje",
    "deser": "deser deseru desery deserów",
    "przekąska": "przekąska przekąskę przekąski przekąsek",
}
_GOALS = {
    "low_kcal": ("lekki", "lekka", "lekkie", "lekką", "fit", "niskokaloryczny",
                 "niskokaloryczna", "niskokaloryczne", "niskokaloryczną", "mało kalorii", "na redukcję"),
    "high_protein": ("dużo białka", "z dużą ilością białka", "wysokobiałkowy",
                     "wysokobiałkowa", "wysokobiałkowe"),
    "keto": ("keto", "ketogeniczny", "ketogeniczna", "ketogeniczne"),
}
_EXCLUSIONS = {
    "meat": ("bez mięsa",), "fish": ("bez ryb",),
    "gluten": ("bez glutenu", "bezglutenowy", "bezglutenowa", "bezglutenowe"),
    "lactose": ("bez laktozy", "bezlaktozowy", "bezlaktozowa", "bezlaktozowe"),
}
_MILK = ("bez mleka", "bez nabiału", "bezmleczny", "bezmleczna", "bezmleczne")
_PROTEIN = {
    ("meat", "required"): ("z mięsem",),
    ("fish", "required"): ("z rybą", "z rybami", "koniecznie rybne", "koniecznie rybny", "koniecznie rybna"),
    ("fish", "permitted"): ("ryby mogą być", "ryby są dozwolone"),
}
_WAIVERS = ("nie musi być", "nie muszą być")
_AMBIGUOUS = (("nie", "musi", "byc"), ("nie", "musza", "byc"),
              ("nie", "chce"), ("nie",), ("bez",), ("zamiast",))
# Consume only paired quotes. An apostrophe inside a word is punctuation.
_TOKENS = re.compile(
    r"""(?P<quote>"[^"]*"|„[^”“]*[”“]|“[^”]*”|«[^»]*»|‘[^’]*’|(?<!\w)'[^']*'(?!\w))"""
    r"|(?P<word>[\w\u0300-\u036f]+)|[^\s]"
)


def _fold(word):
    decomposed = unicodedata.normalize("NFD", word.casefold().replace("ł", "l"))
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _vocabulary():
    phrases = {}

    def add(rule, kind, value, status, forms, *, waivable=False):
        for form in forms:
            phrases[tuple(_fold(form).split())] = (rule, kind, value, status)
            if waivable:
                for prefix in _WAIVERS:
                    words = tuple(_fold(f"{prefix} {form}").split())
                    phrases[words] = (rule, kind, value, "waived")

    for value, forms in _CATEGORIES.items():
        add("CMP-CAT", "category", value, "required", forms.split(), waivable=True)
    for value, forms in _GOALS.items():
        add("CMP-GOAL", "nutrition_goal", value, "required", forms, waivable=True)
    for value, forms in _EXCLUSIONS.items():
        add("CMP-EXCL", "exclusion", value, "required", forms, waivable=True)
    add("CMP-EXCL", "unsupported", "exclusion", "required", _MILK, waivable=True)
    for (value, status), forms in _PROTEIN.items():
        add("CMP-PROT", "protein", value, status, forms)
    add("CMP-PROT", "protein", "fish", "waived", [f"{prefix} z rybą" for prefix in _WAIVERS])
    return phrases


_PHRASES = _vocabulary()
_MAX_WORDS = max(map(len, _PHRASES))


@dataclass(frozen=True)
class Finding:
    rule_id: str
    source: str
    reason: str
    expected_signature: tuple | None


@dataclass(frozen=True)
class Coverage:
    status: str
    checked_rules: tuple
    findings: tuple
    policy_version: str = POLICY_VERSION

    @property
    def block_search(self):
        return self.status in ("inconsistent", "unresolved")


def _clauses(text):
    """Keep original offsets. Punctuation and quoted material separate scopes."""
    clause = []
    for token in _TOKENS.finditer(text):
        if token.lastgroup == "word":
            clause.append(token)
            continue
        if clause:
            yield clause
            clause = []
    if clause:
        yield clause


def _matches(words):
    """Yield non-overlapping longest phrases with local operator scope."""
    pos = 0
    while pos < len(words):
        for size in range(min(_MAX_WORDS, len(words) - pos), 0, -1):
            entry = _PHRASES.get(words[pos:pos + size])
            if entry:
                start = pos
                for prefix in _AMBIGUOUS:
                    if pos >= len(prefix) and words[pos - len(prefix):pos] == prefix:
                        start -= len(prefix)
                        break
                yield start, pos + size, entry, start != pos
                pos += size
                break
        else:
            pos += 1


def _clause_checks(text, tokens):
    words = tuple(_fold(token.group()) for token in tokens)
    # Compare the two arms of each alternative within this clause only.
    matches = list(_matches(words))
    by_start = {match[0]: match for match in matches}
    arms = [[]]
    for pos, word in enumerate(words):
        if word in ("lub", "albo"):
            arms.append([])
        elif pos in by_start:
            arms[-1].append(by_start[pos])
    alternatives = {}
    for first, second in zip(arms, arms[1:]):
        shared = {m[2][0] for m in first} & {m[2][0] for m in second}
        for rule in shared:
            group = [m for m in first + second if m[2][0] == rule]
            span = (group[0][0], group[-1][1])
            alternatives.update((m[0], span) for m in group)
    for start, end, (rule, kind, value, status), ambiguous in matches:
        signature = None if ambiguous or start in alternatives else (kind, value, status)
        start, end = alternatives.get(start, (start, end))
        source = text[tokens[start].start():tokens[end - 1].end()]
        yield rule, source, signature


def check_completeness(text: str, interpretation: Interpretation, proposed: Compilation) -> Coverage:
    if proposed.action == "no_search":
        return Coverage("not_applicable", (), ())
    if proposed.action != "search":
        raise ValueError("Expected a compiled search or no_search")
    facts = {(fact.kind, fact.value, fact.status) for fact in interpretation.facts}
    rules, findings = set(), []
    for clause in _clauses(text):
        for rule, source, signature in _clause_checks(text, clause):
            rules.add(rule)
            if signature not in facts:
                reason = "missing_fact" if signature else "unresolved_scope"
                findings.append(Finding(rule, source, reason, signature))
    if any(item.reason == "unresolved_scope" for item in findings):
        status = "unresolved"
    elif findings:
        status = "inconsistent"
    else:
        status = "consistent" if rules else "no_supported_cues"
    return Coverage(status, tuple(sorted(rules)), tuple(dict.fromkeys(findings)))
