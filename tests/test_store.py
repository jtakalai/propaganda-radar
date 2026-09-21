"""The store's row identity is (url, headline, outlet). The two tests that
matter are the ones that broke when it was url alone: CRTA rows share a
report URL, and the same headline runs in several outlets on one day.
"""

import pytest

from radar.store import CsvStore


@pytest.fixture
def store(tmp_path):
    return CsvStore(tmp_path / "headlines.csv")


def row(headline, outlet, url, **kw):
    return {"headline": headline, "outlet": outlet, "url": url, "label": "", **kw}


def test_same_report_url_different_outlets_both_kept(store):
    added = store.upsert([
        row("Ista vest", "Informer", "https://crta.plus/r/#cluster-1"),
        row("Ista vest", "Kurir", "https://crta.plus/r/#cluster-1"),
    ])
    assert added == 2


def test_reinserting_the_same_row_is_a_no_op(store):
    store.upsert([row("Ista vest", "Kurir", "https://x/1")])
    assert store.upsert([row("Ista vest", "Kurir", "https://x/1")]) == 0


def test_labelling_one_outlet_leaves_the_others_alone(store):
    rows = [
        row("Ista vest", "Informer", "https://crta.plus/r/#cluster-1"),
        row("Ista vest", "Kurir", "https://crta.plus/r/#cluster-1"),
    ]
    store.upsert(rows)
    store.set_label(rows[0], "vilifying_opponents", labelled_by="hand")

    df = store.load()
    assert list(df.set_index("outlet")["label"][["Informer", "Kurir"]]) == ["vilifying_opponents", ""]


def test_outlet_names_are_canonicalised_on_the_way_in(store):
    store.upsert([row("A", "Alo", "https://x/1"), row("B", "alo!", "https://x/2")])
    assert set(store.load()["outlet"]) == {"Alo!"}
