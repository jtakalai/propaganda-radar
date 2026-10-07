def labelled(df):
    return df[df["label"] != ""].copy()
