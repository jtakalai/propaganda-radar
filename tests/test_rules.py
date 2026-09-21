"""Rung 1 fires on normalised text, so a rule has to match a headline
whatever script it arrives in, and has to survive Serbian inflection.
"""

from radar.model.classifier import predict
from radar.model.rules import fired_rules


def test_blokaderi_fires_across_inflections():
    for headline in ["BLOKADERI ponovo", "blokaderima poručio", "Блокадери blokiraju"]:
        assert [r.name for r in fired_rules(headline)] == ["blokaderi"]


def test_two_pattern_rule_needs_both_patterns():
    # NEIGHBOUR alone is not enough - hostility has to be there too
    assert fired_rules("Hrvatska otvorila novu deonicu autoputa") == []
    assert [r.label for r in fired_rules("Hrvatska pretnja srpskom narodu")] == ["vilifying_neighbours"]


def test_neutral_headline_is_nothing():
    label, confidence, probs = predict("Spoljnotrgovinski deficit u junu 4,7 milijardi dolara")
    assert label == "nothing"
    assert probs["nothing"] == 1.0


def test_probabilities_cover_every_label():
    from radar.config import LABELS

    assert set(predict("BLOKADERI ponovo")[2]) == set(LABELS)
