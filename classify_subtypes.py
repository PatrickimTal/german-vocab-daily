#!/usr/bin/env python3
"""One-time (re-runnable) enrichment: add a 'subtype' column to
vocab_master.csv with a finer-grained grammatical/functional category for
every entry.

- verb_prep / noun_prep rows get a deterministic subtype matching their type.
- 'other' rows that already carry an unambiguous note ("adjective +
  preposition" or "governs case, no preposition") get a deterministic
  subtype too.
- The remaining 'other' rows are classified by the Anthropic API into
  Wortschatz / Redewendung / Redemittel (see SYSTEM_PROMPT below).

Safe to re-run: rows that already have a non-empty subtype are left as-is
unless --force is passed.
"""
import argparse
import csv
import json

import anthropic

MODEL = "claude-opus-5"
CSV_PATH_DEFAULT = "vocab_master.csv"
BATCH_SIZE = 35

DETERMINISTIC_TYPE_SUBTYPE = {
    "verb_prep": "Verb + Präp.",
    "noun_prep": "Nomen + Präp.",
}

LLM_CATEGORIES = ["Wortschatz", "Redewendung", "Redemittel"]

SYSTEM_PROMPT = """You are classifying German vocabulary entries by grammatical/functional \
subtype for a C1 learner's flashcard app. For each numbered entry, choose exactly one \
subtype from:

- "Wortschatz": a general vocabulary item -- a single word (noun, verb, adjective, adverb) \
or short descriptive phrase whose meaning is literal/compositional, with no fixed \
idiomatic or collocational pattern.
- "Redewendung": a fixed idiomatic expression whose overall meaning is figurative and \
cannot be derived literally from its individual words (idioms, sayings, proverbs). \
Example: "über den Tisch ziehen" (to dupe someone) -- literally "to pull [someone] over \
the table."
- "Redemittel": a fixed verb + noun/object collocation (a "support verb construction") \
where the combination is conventionally fixed but the meaning stays close to \
literal/compositional. Example: "eine Entscheidung treffen" (to make a decision), \
"einen Fehler beheben" (to fix a mistake), "ein Zimmer buchen" (to book a room).

Classify strictly by the entry's own meaning and structure -- ignore register (slang, \
vulgar, colloquial) or dialect notes; those don't affect subtype. Respond with exactly \
one classification per entry, in the same order given, echoing the german field back \
unchanged."""


def deterministic_subtype(row):
    if row["type"] in DETERMINISTIC_TYPE_SUBTYPE:
        return DETERMINISTIC_TYPE_SUBTYPE[row["type"]]
    notes = row["notes"].lower()
    if "adjective + preposition" in notes:
        return "Adjektiv + Präp."
    if "governs case, no preposition" in notes:
        return "Verb + Kasus"
    return None


def build_batch_prompt(batch):
    lines = [
        f"Classify all {len(batch)} entries below. Return exactly {len(batch)} "
        f"classifications in the 'classifications' array, one per entry, in the same order.\n"
    ]
    for i, row in enumerate(batch, 1):
        example = row["example_de"] or "(no example)"
        lines.append(
            f"{i}. german: {row['german']} | english: {row['english']} | example: {example}"
        )
    return "\n".join(lines)


def classify_batch(client, batch):
    schema = {
        "type": "object",
        "properties": {
            "classifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "german": {"type": "string"},
                        "subtype": {"type": "string", "enum": LLM_CATEGORIES},
                    },
                    "required": ["german", "subtype"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["classifications"],
        "additionalProperties": False,
    }

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_batch_prompt(batch)}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    classifications = data["classifications"]

    if len(classifications) != len(batch):
        raise RuntimeError(
            f"Expected {len(batch)} classifications, got {len(classifications)}"
        )

    results = []
    for row, item in zip(batch, classifications):
        if item["german"] != row["german"]:
            print(
                f"  warning: echoed german mismatch — expected {row['german']!r}, "
                f"got {item['german']!r} (using positional match anyway)"
            )
        results.append(item["subtype"])
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default=CSV_PATH_DEFAULT)
    parser.add_argument(
        "--force", action="store_true", help="Reclassify rows that already have a subtype"
    )
    args = parser.parse_args()

    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if "subtype" not in fieldnames:
        fieldnames = fieldnames + ["subtype"]
    for row in rows:
        row.setdefault("subtype", "")

    to_classify = []
    for row in rows:
        if row["subtype"] and not args.force:
            continue
        subtype = deterministic_subtype(row)
        if subtype is not None:
            row["subtype"] = subtype
        else:
            to_classify.append(row)

    print(f"{len(to_classify)} entries need LLM classification "
          f"({len(rows) - len(to_classify)} resolved deterministically)")

    if to_classify:
        client = anthropic.Anthropic()
        try:
            for start in range(0, len(to_classify), BATCH_SIZE):
                batch = to_classify[start : start + BATCH_SIZE]
                print(f"Classifying {start + 1}-{start + len(batch)} of {len(to_classify)}...")
                subtypes = classify_batch(client, batch)
                for row, subtype in zip(batch, subtypes):
                    row["subtype"] = subtype
        except anthropic.RateLimitError as e:
            retry_after = e.response.headers.get("retry-after", "unknown")
            raise SystemExit(f"Rate limited; retry after {retry_after}s") from e
        except anthropic.APIStatusError as e:
            raise SystemExit(f"API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise SystemExit(f"Network error calling Anthropic API: {e}") from e

    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for row in rows:
        counts[row["subtype"]] = counts.get(row["subtype"], 0) + 1
    print(f"\nWrote subtype column for {len(rows)} rows in {args.csv}:")
    for subtype, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {subtype}: {count}")


if __name__ == "__main__":
    main()
