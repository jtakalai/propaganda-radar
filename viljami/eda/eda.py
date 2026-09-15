import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


pd.set_option("display.width", 120)
pd.set_option("display.max_columns", None)

DATA = Path(__file__).resolve().parent.parent / "data"
FIGURES = Path(__file__).resolve().parent / "figures"
FIGURES.mkdir(exist_ok=True)

# --- palette (fixed order, not cycled - see propaganda-radar dataviz notes) ---
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
SURFACE = "#fcfcfb"

LABEL_COLORS = {
    "vilifying_opponents": "#2a78d6",  # blue
    "vilifying_neighbours": "#eb6834",  # orange
    "personality_cult": "#1baf7a",  # aqua
    "vilifying_eu": "#eda100",  # yellow
    "nothing": INK_MUTED,  # neutral - it's the non-event class
}
LABEL_ORDER = [
    "vilifying_opponents",
    "vilifying_neighbours",
    "personality_cult",
    "vilifying_eu",
    "nothing",
]

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRIDLINE,
        "axes.labelcolor": INK_SECONDARY,
        "text.color": INK,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK_SECONDARY,
        "grid.color": GRIDLINE,
        "font.family": "DejaVu Sans",  # covers Serbian Latin diacritics (š č ć ž đ)
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def colors_for(labels):
    return [LABEL_COLORS.get(l, INK_MUTED) for l in labels]


# --- load ---
crta = pd.read_csv(DATA / "crta_examples.csv", parse_dates=["date"])
labels = pd.read_csv(DATA / "labels.csv", parse_dates=["date"])

print("=" * 60)
print("LOAD")
print("=" * 60)
print(
    f"crta_examples.csv : {len(crta)} outlet-rows, {crta['cluster_id'].nunique()} distinct headlines"
)
print(
    f"labels.csv        : {len(labels)} rows (manual RSS labelling, all Kurir so far)"
)
print(
    f"date range (crta)   : {crta['date'].min().date()} .. {crta['date'].max().date()}"
)
print(
    f"date range (labels) : {labels['date'].min().date()} .. {labels['date'].max().date()}"
)


def class_balance():
    crta_by_cluster = crta.drop_duplicates("cluster_id")
    print("\n" + "=" * 60)
    print("1. CLASS BALANCE")
    print("=" * 60)

    print(
        "\ncrta_examples.csv, by distinct headline (not outlet-row, so repeats don't inflate this):"
    )
    print(crta_by_cluster["label"].value_counts())

    print(
        "\nlabels.csv (n is tiny - 1 outlet, 1 week - not representative of base rate yet):"
    )
    print(labels["label"].value_counts())

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, (title, counts) in zip(
        axes,
        [
            (
                "CRTA examples\n(by distinct headline)",
                crta_by_cluster["label"].value_counts(),
            ),
            ("Our labels.csv", labels["label"].value_counts()),
        ],
    ):
        counts = counts.reindex([l for l in LABEL_ORDER if l in counts.index])
        ax.bar(counts.index, counts.values, color=colors_for(counts.index))
        ax.set_title(title, color=INK, fontsize=11)
        ax.tick_params(axis="x", rotation=30)
        for tick in ax.get_xticklabels():
            tick.set_ha("right")
        ax.grid(axis="y", linewidth=0.6)
        ax.set_axisbelow(True)
    fig.tight_layout()
    plt.show()


def near_duplicate_leakage():
    print("\n" + "=" * 60)
    print("2. NEAR-DUPLICATE LEAKAGE (CRTA examples)")
    print("=" * 60)

    cluster_sizes = crta.groupby("cluster_id").size()
    multi = (cluster_sizes > 1).sum()
    print(
        f"{multi}/{len(cluster_sizes)} headlines ({multi / len(cluster_sizes):.0%}) ran in >1 outlet the same day"
    )
    print(
        f"mean outlets per headline: {cluster_sizes.mean():.2f}, max: {cluster_sizes.max()}"
    )
    print("cluster size distribution:")
    print(cluster_sizes.value_counts().sort_index())

    fig, ax = plt.subplots(figsize=(6, 4))
    vc = cluster_sizes.value_counts().sort_index()
    ax.bar(vc.index.astype(str), vc.values, color=LABEL_COLORS["vilifying_opponents"])
    ax.set_xlabel("outlets carrying the same headline")
    ax.set_ylabel("number of headlines")
    ax.set_title(
        "Cluster size: leakage if split by row, not by story", color=INK, fontsize=11
    )
    ax.grid(axis="y", linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    plt.show()


def outlet_label_crosstab():
    print("\n" + "=" * 60)
    print("3. OUTLET x LABEL (outlet-as-confound check)")
    print("=" * 60)

    # normalise CRTA's inconsistent outlet casing/punctuation (Alo vs Alo!, etc.)
    def norm_outlet(o):
        o = o.strip().rstrip("!").strip()
        return o[:1].upper() + o[1:].lower() if o else o

    crta["outlet_norm"] = crta["outlet"].map(norm_outlet)
    crosstab = pd.crosstab(crta["outlet_norm"], crta["label"])
    crosstab = crosstab.reindex(
        columns=[l for l in LABEL_ORDER if l in crosstab.columns]
    )
    crosstab = crosstab.loc[crosstab.sum(axis=1).sort_values(ascending=False).index]
    print(crosstab)

    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(crosstab.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(crosstab.columns)))
    ax.set_xticklabels(crosstab.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(crosstab.index)))
    ax.set_yticklabels(crosstab.index)
    for i in range(crosstab.shape[0]):
        for j in range(crosstab.shape[1]):
            v = crosstab.values[i, j]
            if v:
                ax.text(
                    j,
                    i,
                    str(v),
                    ha="center",
                    va="center",
                    color="white" if v > crosstab.values.max() / 2 else INK,
                    fontsize=8,
                )
    ax.set_title("Outlet x label counts (CRTA examples)", color=INK, fontsize=11)
    fig.colorbar(im, ax=ax, shrink=0.8, label="count")
    fig.tight_layout()
    plt.show()


def headline_length_by_label():
    print("\n" + "=" * 60)
    print("4. HEADLINE LENGTH BY LABEL")
    print("=" * 60)

    crta_by_cluster = crta.drop_duplicates("cluster_id")
    crta_by_cluster["n_words"] = crta_by_cluster["headline"].str.split().str.len()
    print(
        crta_by_cluster.groupby("label")["n_words"].describe()[
            ["count", "mean", "min", "max"]
        ]
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    data_by_label = [
        crta_by_cluster.loc[crta_by_cluster["label"] == l, "n_words"].values
        for l in LABEL_ORDER
        if l in crta_by_cluster["label"].unique()
    ]
    present_labels = [l for l in LABEL_ORDER if l in crta_by_cluster["label"].unique()]
    bp = ax.boxplot(data_by_label, tick_labels=present_labels, patch_artist=True)
    for patch, l in zip(bp["boxes"], present_labels):
        patch.set_facecolor(LABEL_COLORS[l])
        patch.set_alpha(0.7)
    for median in bp["medians"]:
        median.set_color(INK)
    ax.set_ylabel("words per headline")
    ax.tick_params(axis="x", rotation=20)
    ax.set_title("Headline length by category (CRTA examples)", color=INK, fontsize=11)
    ax.grid(axis="y", linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    plt.show()


def script_check():
    print("\n" + "=" * 60)
    print("5. SCRIPT CHECK (Cyrillic vs Latin, diacritics)")
    print("=" * 60)

    CYRILLIC_RE = re.compile(r"[Ѐ-ӿ]")
    DIACRITIC_RE = re.compile(r"[šđčćžŠĐČĆŽ]")
    crta_by_cluster = crta.drop_duplicates("cluster_id")
    all_headlines = pd.concat([crta_by_cluster["headline"], labels["headline"]])
    n_cyrillic = all_headlines.apply(lambda h: bool(CYRILLIC_RE.search(h))).sum()
    n_diacritic = all_headlines.apply(lambda h: bool(DIACRITIC_RE.search(h))).sum()
    print(f"{n_cyrillic}/{len(all_headlines)} headlines contain any Cyrillic character")
    print(
        f"{n_diacritic}/{len(all_headlines)} headlines contain a Latin diacritic (š đ č ć ž)"
    )
    print("-> everything we have so far is Latin script. Don't assume that holds once")
    print("   RSS feeds from Cyrillic-first outlets (e.g. Politika, RTS) are added.")


def top_words_per_category():
    print("\n" + "=" * 60)
    print("6. TOP WORDS PER CATEGORY (crude - no stemming, small stopword list)")
    print("=" * 60)

    crta_by_cluster = crta.drop_duplicates("cluster_id")
    STOPWORDS = set(
        """
        i u na za se je da su sa od do ne ali kao sto što će ce koji koja koje
        ovaj ova ovo biti bio bila su iz pre posle ka o a ili pa te no nego
        kako gde kada dok mu joj im ih ga je li se ce će samo već vec sve svih
        svoj svoja svoje ono ona on oni njegov njena njihov jer bez pod nad
        kod uz preko posebno godine godina dana meseca
        """.split()
    )

    def tokens(headline):
        words = re.findall(r"[A-Za-zČčĆćĐđŠšŽž]+", headline.lower())
        return [w for w in words if w not in STOPWORDS and len(w) > 2]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, label in zip(
        axes,
        [
            "vilifying_opponents",
            "vilifying_neighbours",
            "personality_cult",
            "vilifying_eu",
        ],
    ):
        subset = crta_by_cluster.loc[crta_by_cluster["label"] == label, "headline"]
        counter = Counter(w for h in subset for w in tokens(h))
        top = counter.most_common(10)
        print(f"\n{label} (n={len(subset)}):")
        for word, n in top:
            print(f"  {n:3d}  {word}")
        if top:
            words, counts = zip(*reversed(top))
            ax.barh(words, counts, color=LABEL_COLORS[label])
        ax.set_title(label, fontsize=9, color=INK)
        ax.tick_params(labelsize=8)
    fig.suptitle(
        "Top words per category (CRTA examples, stopwords removed)",
        color=INK,
        fontsize=11,
    )
    fig.tight_layout()
    plt.show()


def main():
    class_balance()
    near_duplicate_leakage()
    outlet_label_crosstab()
    headline_length_by_label()
    script_check()
    top_words_per_category()


if __name__ == "__main__":
    main()
