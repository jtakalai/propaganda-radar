"""Label headlines with an LLM instead of by hand - a real, shareable version
of the ad-hoc "read each headline in chat and pick a category" process this
project has been using. Shells out to the `claude` CLI (Claude Code) for
structured output, so it rides on whatever Claude Code login you already
have - no ANTHROPIC_API_KEY, no separate billing setup. Anyone on the team
with `claude` installed and logged in can run this as-is.

    python llm_label.py                    # label everything still unlabelled
    python llm_label.py --limit 20         # just the first 20 (still costs real money - try small first)
    python llm_label.py --batch-size 20    # headlines per `claude` call (default 15) - bigger batches are cheaper per headline

Safe to re-run: only touches rows where label == "". To relabel rows already
labelled by this script (to compare a prompt/model change against the old
run), pass --relabel and it'll only touch rows whose labelled_by == "claude-code".

Writes label + comment (reasoning and the full probability breakdown, for
transparency into what the AI did) + labelled_by="claude-code", same shape
as a human correcting a row through the dashboard.

Cost note: each `claude` call reports its own spend; this script sums and
prints it as it goes, and --max-budget-usd caps what any single call may
spend (default 0.50) so a bad batch can't run away.
"""

import argparse
import json
import subprocess

from store import DEFAULT_DATA_PATH, CsvStore

LABELS = [
    "vilifying_opponents",
    "vilifying_neighbours",
    "personality_cult",
    "vilifying_eu",
    "nothing",
]

SYSTEM_PROMPT = """You classify Serbian news headlines for CRTA's
manipulation-narrative categories (crta.plus):

1. vilifying_opponents - discrediting opposition, protesters, the student blockade movement
2. vilifying_neighbours - Croatia, Montenegro, Kosovo framed as hostile to Serbs
3. personality_cult - Vucic as indispensable / heroic
4. vilifying_eu - EU and the West as hostile or hypocritical
5. nothing - none of the above

Headlines are often multi-label in spirit (e.g. discrediting an opposition
figure by tying them to a neighbouring country) - split probability mass
across categories when a headline genuinely fits more than one, instead of
forcing all weight onto a single label. Most real headlines are "nothing" -
don't over-call manipulation.

For each numbered headline, return one classification object with that same
id, a probability per category (they don't need to sum to 1), and one short
sentence of reasoning for the top category."""

SCHEMA = {
    "type": "object",
    "properties": {
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "probabilities": {
                        "type": "object",
                        "properties": {label: {"type": "number"} for label in LABELS},
                        "required": LABELS,
                    },
                    "reasoning": {"type": "string"},
                },
                "required": ["id", "probabilities", "reasoning"],
            },
        }
    },
    "required": ["classifications"],
}


def classify_batch(headlines: list[str], max_budget_usd: float) -> tuple[list[dict], float]:
    """Returns (classifications in input order, dollars spent on this call)."""
    prompt = "\n".join(f"{i}. {h}" for i, h in enumerate(headlines, 1))
    proc = subprocess.run(
        [
            "claude", "-p", prompt,
            "--system-prompt", SYSTEM_PROMPT,
            "--json-schema", json.dumps(SCHEMA),
            "--output-format", "json",
            "--max-budget-usd", str(max_budget_usd),
        ],
        capture_output=True, text=True, check=True,
    )
    result = json.loads(proc.stdout)
    if result.get("is_error"):
        raise RuntimeError(result.get("result", "unknown claude error"))
    by_id = {c["id"]: c for c in result["structured_output"]["classifications"]}
    ordered = [by_id[i] for i in range(1, len(headlines) + 1) if i in by_id]
    return ordered, result["total_cost_usd"]


def format_comment(reasoning: str, probs: dict[str, float]) -> str:
    breakdown = ", ".join(f"{k}={v:.2f}" for k, v in sorted(probs.items(), key=lambda kv: -kv[1]))
    return f"(LLM) {reasoning} [{breakdown}]"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=None, help="only label the first N matching rows")
    parser.add_argument("--batch-size", type=int, default=15, help="headlines per claude call (default 15)")
    parser.add_argument("--max-budget-usd", type=float, default=0.50, help="cap per claude call (default 0.50)")
    parser.add_argument(
        "--relabel", action="store_true",
        help="also relabel rows already labelled by this script (default: only label rows with label=='')",
    )
    args = parser.parse_args()

    store = CsvStore(DEFAULT_DATA_PATH)
    df = store.load()
    todo = df[df["labelled_by"] == "claude-code"] if args.relabel else df[df["label"] == ""]
    if args.limit:
        todo = todo.head(args.limit)

    if todo.empty:
        print("nothing to label")
        return

    print(f"labelling {len(todo)} headlines via claude CLI, batches of {args.batch_size} ...")
    rows = list(todo.iterrows())
    total_cost = 0.0
    labelled = 0

    for start in range(0, len(rows), args.batch_size):
        batch = rows[start:start + args.batch_size]
        headlines = [row["headline"] for _, row in batch]
        try:
            classifications, cost = classify_batch(headlines, args.max_budget_usd)
        except (subprocess.CalledProcessError, RuntimeError, KeyError, json.JSONDecodeError) as e:
            print(f"  ! batch at {start} failed ({e}), skipping {len(batch)} headlines")
            continue

        total_cost += cost
        for (_, row), c in zip(batch, classifications):
            probs = c["probabilities"]
            label = max(probs, key=probs.get)
            store.set_label(row["url"], label, labelled_by="claude-code", comment=format_comment(c["reasoning"], probs))
            labelled += 1
            print(f"  [{labelled}/{len(rows)}] {label} - {row['headline'][:60]}")

        print(f"  batch cost: ${cost:.4f}  (running total: ${total_cost:.4f})")

    print(f"done - labelled {labelled}/{len(rows)}, total spend ${total_cost:.4f}")


if __name__ == "__main__":
    main()
