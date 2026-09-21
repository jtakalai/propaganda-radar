"""Serbian is written in both scripts, often mixed inside one headline.
Everything downstream assumes normalise() collapses that to one form.
"""

from radar.prepare.normalise import normalise


def test_scripts_and_diacritics_agree():
    assert normalise("ВУЧИЋ") == normalise("Vučić") == normalise("Vucic") == "vucic"


def test_multigraph_cyrillic_letters():
    # љ њ џ ђ each expand to more than one Latin character
    assert normalise("Љубав") == "ljubav"
    assert normalise("Њима") == "njima"
    assert normalise("Ђорђе") == "djordje"


def test_mixed_script_headline():
    assert normalise("Блокадери and blokaderi") == "blokaderi and blokaderi"
