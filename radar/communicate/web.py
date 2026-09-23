"""Serve the review site: the preview, and the buttons behind it.

    python scripts/serve.py              # http://127.0.0.1:8000
    python scripts/serve.py --port 9000

The store is read on every request, so anything fetched or corrected shows
up on the next refresh. Corrections are saved with labelled_by="site".
"""

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from radar.collect.rss import fetch_new_rows
from radar.config import LABELS, ROOT
from radar.model.classifier import explain
from radar.store import CsvStore

WEB = ROOT / "web"

# The labels a person stood behind. LLM labels are deliberately not here:
# the site shows the model's own prediction for those rows instead.
VERIFIED_BY = {"crta", "hand", "site", "ui"}


def headlines() -> list[dict]:
    df = CsvStore().load()
    rows = []
    for row in df.to_dict("records"):
        verified = row["labelled_by"] in VERIFIED_BY
        category = row["label"] if verified else row["predicted_label"]
        if not category:
            continue
        rows.append(
            {
                "headline": row["headline"],
                "outlet": row["outlet"],
                "date": row["date"],
                "url": row["url"],
                "category": category,
                "verified": verified,
                "words": explain(row["headline"]),
            }
        )
    return rows


def fetch_latest() -> dict:
    return {"added": CsvStore().upsert(fetch_new_rows())}


def save_label(payload: dict) -> dict:
    if payload.get("label") not in LABELS:
        raise ValueError(f"unknown label: {payload.get('label')!r}")
    CsvStore().set_label(payload, payload["label"], labelled_by="site")
    return {"ok": True}


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/api/headlines":
            self.respond({"headlines": headlines(), "writable": True})
        else:
            super().do_GET()

    def do_POST(self):
        routes = {"/api/fetch": lambda _: fetch_latest(), "/api/label": save_label}
        route = routes.get(self.path.split("?")[0])
        if route is None:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or "{}")
        try:
            self.respond(route(payload))
        except Exception as e:
            self.respond({"error": str(e)}, status=400)

    def respond(self, body: dict, status: int = 200):
        encoded = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(WEB)))
    print(f"serving {WEB} on http://127.0.0.1:{args.port}  (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")


if __name__ == "__main__":
    main()
