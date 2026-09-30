from radar.prepare.normalise import normalise


def labelled(df):
    return df[df["label"] != ""].copy()


def groups(df) -> list[str]:
    return [
        cluster or normalise(headline)
        for cluster, headline in zip(df["cluster_id"], df["headline"])
    ]
