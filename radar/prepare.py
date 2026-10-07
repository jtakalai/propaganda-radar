"""Script normalisation and canonical outlet names."""

import unicodedata

_CYRILLIC_TO_FOLDED_LATIN = str.maketrans(
    {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "dj",
        "е": "e", "ж": "z", "з": "z", "и": "i", "ј": "j", "к": "k",
        "л": "l", "љ": "lj", "м": "m", "н": "n", "њ": "nj", "о": "o",
        "п": "p", "р": "r", "с": "s", "т": "t", "ћ": "c", "у": "u",
        "ф": "f", "х": "h", "ц": "c", "ч": "c", "џ": "dz", "ш": "s",
    }
)  # fmt: skip

_LATIN_FOLD = str.maketrans({"š": "s", "č": "c", "ć": "c", "ž": "z", "đ": "dj"})


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    return text.translate(_CYRILLIC_TO_FOLDED_LATIN).translate(_LATIN_FOLD)


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
    key = normalise(name).strip().rstrip("!").strip()
    return _CANONICAL.get(key, name.strip())
