"""Text normalisation shared by every rung of the model ladder.

Serbian headlines come in Cyrillic, Latin, or a mix of both. `normalise` maps
all of them to one form: lowercase Latin with diacritics folded (č ć -> c,
š -> s, ž -> z, đ -> dj), so "ВУЧИЋ", "Vučić" and "Vucic" compare equal.
"""

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
