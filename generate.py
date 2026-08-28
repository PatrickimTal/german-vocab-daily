#!/usr/bin/env python3
"""Generate quiz.html and reading.html from today.json via the Anthropic
API, update vocab_master.csv usage stats, then build flashcards.html
deterministically as a rolling 7-day deck (see flashcards.py).
"""
import argparse
import csv
import json
import re
from datetime import date

import anthropic

from flashcards import build_flashcards_html

MODEL = "claude-opus-5"
TODAY_JSON_DEFAULT = "today.json"
CSV_PATH_DEFAULT = "vocab_master.csv"

HTML_FENCE_RE = re.compile(r"^```(?:html)?\s*|\s*```$", re.MULTILINE)


def strip_fences(text):
    return HTML_FENCE_RE.sub("", text.strip()).strip()


def build_system_prompt(entries):
    lines = []
    for e in entries:
        lines.append(
            f"- [{e['type']}] {e['german']} — {e['english']}"
            f"\n  DE example: {e['example_de'] or '(none)'}"
            f"\n  EN example: {e['example_en'] or '(none)'}"
        )
    vocab_block = "\n".join(lines)
    return (
        "You are a German-language teaching content generator producing "
        "self-study materials for a C1-level learner. Today's vocabulary "
        "selection (verb_prep = verb + fixed preposition, noun_prep = noun "
        "+ fixed preposition, other = general vocabulary/idioms) is:\n\n"
        f"{vocab_block}\n\n"
        "General rules for every deliverable:\n"
        "- Output a single complete, self-contained HTML5 document: inline "
        "<style> and <script> only, no external resources (no CDNs, fonts, "
        "or images).\n"
        "- Use every vocabulary item above at least once.\n"
        "- Clean, readable styling that works on a phone-width screen.\n"
        "- Output ONLY the raw HTML document — no markdown code fences, no "
        "commentary before or after it."
    )


TASK_PROMPTS = {
    "quiz.html": (
        "Build the quiz.html document: an interactive self-check quiz over "
        "today's vocabulary. Mix multiple-choice (German term -> correct "
        "English meaning, with 3 plausible distractors drawn from the other "
        "selected words) and fill-in-the-blank items using the DE example "
        "sentences with the target word/phrase blanked out. Include "
        "client-side JavaScript that scores the quiz and shows the result "
        "when the learner clicks a 'Check answers' button, plus per-question "
        "correct/incorrect feedback."
    ),
    "reading.html": (
        "Build the reading.html document: a single continuous German-language "
        "newspaper-style article, 300 to 400 words, written for a C1-level "
        "learner, in the tone/register of a serious daily newspaper "
        "(e.g. Suddeutsche Zeitung or FAZ feature/opinion piece). Naturally "
        "work in every vocabulary item from today's list — do not force an "
        "artificial list-like sentence structure. Give the article a "
        "headline. Bold (<strong>) each use of a target vocabulary item the "
        "first time it appears. Below the article, include an 'English "
        "gloss' section: a definition list (<dl>) mapping each target German "
        "item to its English meaning, in the order it first appears in the "
        "article. State the word count near the top."
    ),
}


def generate_document(client, system_prompt, filename):
    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": TASK_PROMPTS[filename]}],
    ) as stream:
        response = stream.get_final_message()
    text = next((b.text for b in response.content if b.type == "text"), "")
    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            f"{filename} was truncated at the max_tokens limit — raise max_tokens "
            f"and retry rather than using this partial output."
        )
    if not text.strip():
        raise RuntimeError(f"Empty response for {filename} (stop_reason={response.stop_reason})")
    return strip_fences(text)


def update_csv(csv_path, entries, today):
    used_keys = {(e["type"], e["german"]) for e in entries}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        if (row["type"], row["german"]) in used_keys and row["date_last_used"] != today.isoformat():
            row["times_used"] = str(int(row["times_used"] or 0) + 1)
            row["date_last_used"] = today.isoformat()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", default=TODAY_JSON_DEFAULT)
    parser.add_argument("--csv", default=CSV_PATH_DEFAULT)
    args = parser.parse_args()

    with open(args.selection, encoding="utf-8") as f:
        payload = json.load(f)
    entries = payload["entries"]

    system_prompt = build_system_prompt(entries)
    client = anthropic.Anthropic()

    generated = {}
    try:
        for filename in ("quiz.html", "reading.html"):
            print(f"Generating {filename}...")
            generated[filename] = generate_document(client, system_prompt, filename)
    except anthropic.RateLimitError as e:
        retry_after = e.response.headers.get("retry-after", "unknown")
        raise SystemExit(f"Rate limited; retry after {retry_after}s") from e
    except anthropic.APIStatusError as e:
        raise SystemExit(f"API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise SystemExit(f"Network error calling Anthropic API: {e}") from e

    for filename, html in generated.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Wrote {filename}")

    today = date.today()
    update_csv(args.csv, entries, today)
    print(f"Updated times_used/date_last_used for {len(entries)} entries in {args.csv}")

    flashcards_html = build_flashcards_html(args.csv, today)
    with open("flashcards.html", "w", encoding="utf-8") as f:
        f.write(flashcards_html)
    print("Wrote flashcards.html (rolling 7-day deck, built from vocab_master.csv)")


if __name__ == "__main__":
    main()
