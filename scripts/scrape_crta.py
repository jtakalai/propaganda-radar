"""Re-scrape CRTA's published example headlines into data/raw/.

Entrypoint only - the code lives in radar/collect/crta.py.
"""

from radar.collect.crta import main

if __name__ == "__main__":
    main()
