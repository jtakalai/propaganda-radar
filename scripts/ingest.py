"""Load data/raw/ into the canonical store (data/processed/headlines.csv).

Entrypoint only - the code lives in radar/prepare/ingest.py.
"""

from radar.prepare.ingest import main

if __name__ == "__main__":
    main()
