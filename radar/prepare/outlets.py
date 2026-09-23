"""Canonical outlet names, looked up on the normalised spelling."""

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
    """Canonical spelling, or the name unchanged if we haven't seen it before."""
    key = normalise(name).strip().rstrip("!").strip()
    return _CANONICAL.get(key, name.strip())
