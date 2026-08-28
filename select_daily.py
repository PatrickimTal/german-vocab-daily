#!/usr/bin/env python3
"""Pick today's vocab selection from vocab_master.csv, weighted toward
entries that have been used least and longest ago, and write it to today.json.
"""
import argparse
import csv
import json
import random
from datetime import date, datetime

CSV_PATH_DEFAULT = "vocab_master.csv"
OUTPUT_PATH_DEFAULT = "today.json"
NEVER_USED_DAYS = 36500  # ~100 years; puts never-used entries at the front of the queue

QUOTA = {
    "verb_prep": 5,
    "noun_prep": 3,
    "other": 12,
}


def days_since(date_str, today):
    if not date_str.strip():
        return NEVER_USED_DAYS
    try:
        last_used = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return NEVER_USED_DAYS
    return max((today - last_used).days, 0)


def weight_for(row, today):
    times_used = int(row["times_used"] or 0)
    recency = days_since(row["date_last_used"], today)
    return (recency + 1) / (times_used + 1)


def weighted_sample_without_replacement(rows, k, today):
    """Efraimidis-Spirakis weighted reservoir sampling, no replacement."""
    if k >= len(rows):
        return list(rows)
    keyed = []
    for row in rows:
        w = weight_for(row, today)
        key = random.random() ** (1.0 / w)
        keyed.append((key, row))
    keyed.sort(key=lambda pair: pair[0], reverse=True)
    return [row for _, row in keyed[:k]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default=CSV_PATH_DEFAULT)
    parser.add_argument("--out", default=OUTPUT_PATH_DEFAULT)
    args = parser.parse_args()

    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    by_type = {t: [] for t in QUOTA}
    for row in rows:
        if row["type"] in by_type:
            by_type[row["type"]].append(row)

    today = date.today()
    selection = []
    for vocab_type, quota in QUOTA.items():
        pool = by_type[vocab_type]
        if len(pool) < quota:
            raise ValueError(
                f"Not enough '{vocab_type}' entries: need {quota}, have {len(pool)}"
            )
        selection.extend(weighted_sample_without_replacement(pool, quota, today))

    payload = {
        "date": today.isoformat(),
        "entries": selection,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Selected {len(selection)} entries -> {args.out}")
    for vocab_type in QUOTA:
        count = sum(1 for e in selection if e["type"] == vocab_type)
        print(f"  {vocab_type}: {count}")


if __name__ == "__main__":
    main()
