from pathlib import Path
import re

import pandas as pd


DATA_PATH = Path(__file__).resolve().parent.parent / "viljami" / "propaganda-radar" / "data" / "data.csv"
STOPWORD_PATH = Path(__file__).resolve().parent / "SSWdictionary.csv"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    data = pd.read_csv(path)
    required = {"headline", "label"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = data.loc[data["headline"].notna() & data["label"].notna()].copy()
    data["headline"] = data["headline"].astype(str).str.strip()
    data["label"] = data["label"].astype(str).str.strip()
    return data.loc[data["headline"].ne("") & data["label"].ne("")].reset_index(drop=True)


def load_stopwords(path: Path = STOPWORD_PATH) -> list[str]:
    dictionary = pd.read_csv(path, header=None, usecols=[0], names=["word"])
    words = dictionary["word"].dropna().astype(str).str.strip()
    tokens = (token for word in words for token in re.findall(r"(?u)\b\w\w+\b", word.lower()))
    return sorted(set(tokens))


def make_groups(data: pd.DataFrame) -> pd.Series:
    if "cluster_id" not in data:
        return pd.Series(data.index.astype(str), index=data.index)

    cluster = data["cluster_id"].astype("string").str.strip()
    return cluster.where(cluster.notna() & cluster.ne(""), "row-" + data.index.astype(str))