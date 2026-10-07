"""Row filters shared by training and evaluation."""

def labelled(df):
    return df[df["label"] != ""].copy()
