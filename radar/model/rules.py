"""Rung 1: keyword and entity rules.

A rule fires when all of its patterns match the normalised headline. Patterns
are written in normalised form and anchored at the word start, so inflected
forms match (blokader -> blokaderi, blokaderima).
"""

import re
from dataclasses import dataclass

from radar.prepare.normalise import normalise


@dataclass(frozen=True)
class Rule:
    name: str
    label: str
    patterns: tuple[re.Pattern, ...]

    def matches(self, normalised_headline: str) -> bool:
        return all(p.search(normalised_headline) for p in self.patterns)


def _rule(label: str, name: str, *patterns: str) -> Rule:
    for p in patterns:
        assert normalise(p) == p, f"write patterns in normalised form: {p!r}"
    return Rule(name, label, tuple(re.compile(p) for p in patterns))


NEIGHBOUR = r"\b(hrvat|zagreb|pristin|kurti|albanc|crnogor|crna gora|podgoric)"
HOSTILITY = r"\b(napad|napada|teror|mrznj|pretn|prete|progon|represij|ugnjet|zavera|krad|agresi|neprijatelj)"

RULES = [
    _rule("vilifying_opponents", "blokaderi", r"\bblokader"),
    _rule("vilifying_opponents", "tzv. studentska lista", r"\b(tzv|takozvan)\b.{0,20}\bstudentsk"),
    _rule("vilifying_opponents", "obojena revolucija", r"\bobojen\w* revolucij"),
    _rule("vilifying_opponents", "plenumasi", r"\bplenum"),
    _rule("vilifying_neighbours", "neighbour + hostility", NEIGHBOUR, HOSTILITY),
    _rule("vilifying_neighbours", "ustase", r"\bustas"),
    _rule("vilifying_neighbours", "anti-Serb", r"\b(antisrpsk|srbomrs)"),
    _rule("personality_cult", "Vucic + praise", r"\bvucic", r"\b(velicin|herojs|mastermajnd|lavovski|neprepoznatljiv)"),
    _rule("vilifying_eu", "Picula / EP delegation", r"\b(picul|evroparlamentar)"),
    _rule("vilifying_eu", "West + hypocrisy", r"\bzapad", r"\b(licemer|dvostruk|demoniz|mejnstrim)"),
]


def fired_rules(headline: str) -> list[Rule]:
    normalised = normalise(headline)
    return [rule for rule in RULES if rule.matches(normalised)]
