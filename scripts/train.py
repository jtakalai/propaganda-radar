from radar.config import RUNG2
from radar.model.dataset import labelled
from radar.model.tfidf import train
from radar.store import CsvStore


def main():
    df = labelled(CsvStore().load())
    train(df["headline"], df["label"])
    print(f"fitted on {len(df)} labelled rows -> {RUNG2}")


if __name__ == "__main__":
    main()
