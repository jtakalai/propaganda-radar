"""Canonical outlet names.

CRTA's reports spell the same outlet several ways - "Alo" and "Alo!",
"Srpski telegraf" and "Srpski Telegraf", "Večernje novosti" and "Večernje
Novosti". Left alone that is six outlets where there are three, which
quietly breaks the leave-one-outlet-out check CLAUDE.md calls for: half of
an outlet's rows end up in the training side of the split.

Lookup is on the normalised form, so casing, punctuation and Cyrillic vs
Latin spelling all collapse to one entry.
"""

from radar.prepare.normalise import normalise

_CANONICAL = {
    "alo": "Alo!",
    "b92": "B92",
    "blic": "Blic",
    "informer": "Informer",
    "kurir": "Kurir",
    "politika": "Politika",
    "rts 1": "RTS 1",
    "srpski telegraf": "Srpski Telegraf",
    "tv b92": "TV B92",
    "tv informer": "TV Informer",
    "tv pink": "TV Pink",
    "tv prva": "TV Prva",
    "vecernje novosti": "Večernje Novosti",
}


def canonical_outlet(name: str) -> str:
    """Canonical spelling, or the name unchanged if we haven't seen it before.

    Unknown outlets pass through rather than raising - a new feed shouldn't
    fail to ingest just because nobody has added it to the table yet.
    """
    key = normalise(name).strip().rstrip("!").strip()
    return _CANONICAL.get(key, name.strip())
