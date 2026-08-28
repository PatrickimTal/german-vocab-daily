#!/usr/bin/env python3
"""Generate reading.html from today.json via the Anthropic API, archive it
under archive/readings/, update vocab_master.csv usage stats, then build
flashcards.html (rolling 7-day deck) and archive/flashcards.html (all-time
archive) deterministically, and regenerate the index.html landing page.
"""
import argparse
import csv
import html as html_module
import json
import os
import re
from datetime import date

import anthropic

from flashcards import build_flashcards_html, collect_recent_entries
from index_page import (
    READINGS_ARCHIVE_DIR,
    build_index_html,
    collect_reading_archive,
    pick_card_of_day,
)
from site_theme import GOOGLE_FONTS_LINKS

MODEL = "claude-opus-5"
TODAY_JSON_DEFAULT = "today.json"
CSV_PATH_DEFAULT = "vocab_master.csv"

HTML_FENCE_RE = re.compile(r"^```(?:html)?\s*|\s*```$", re.MULTILINE)
BODY_OPEN_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)
DL_RE = re.compile(r"<dl[^>]*>.*?</dl>", re.IGNORECASE | re.DOTALL)
SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def strip_fences(text):
    return HTML_FENCE_RE.sub("", text.strip()).strip()


def inject_back_nav(html_text, back_href, label="← Startseite"):
    nav = (
        f'\n<p style="font-family:\'Sora\',system-ui,sans-serif;font-size:0.85rem;'
        f'margin:0.6rem 0 0;"><a href="{back_href}" style="color:#006eb8;">{label}</a></p>\n'
    )
    new_text, count = BODY_OPEN_RE.subn(lambda m: m.group(1) + nav, html_text, count=1)
    return new_text if count else html_text


def approx_word_count(reading_html_text):
    """Word count of the article body, excluding the English-gloss <dl>."""
    text = DL_RE.sub(" ", reading_html_text)
    text = SCRIPT_STYLE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    text = html_module.unescape(text)
    return len(re.findall(r"\S+", text))


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
        "<style> and <script> only, no external resources or CDNs, except the "
        "site's Google Fonts stylesheet (see below) -- no images.\n"
        "- Use every vocabulary item above at least once.\n"
        "- Clean, readable styling that works on a phone-width screen.\n"
        "- Match the rest of the site's visual identity ('Sprachgarten'): "
        "in <head>, include exactly this before your <style> block:\n"
        f"  {GOOGLE_FONTS_LINKS}\n"
        "  Then in CSS use: body background #e9fae9; body text #304635; "
        "headings/headline #082310 in 'Libre Baskerville', Georgia, serif; "
        "body copy and UI text in 'Sora', system-ui, sans-serif; small "
        "caption/meta text (e.g. a word-count line) in 'IBM Plex Mono', "
        "ui-monospace, monospace; links/accent color #0077c7 (hover #0061b0).\n"
        "- Output ONLY the raw HTML document — no markdown code fences, no "
        "commentary before or after it."
    )


TASK_PROMPTS = {
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

    try:
        print("Generating reading.html...")
        reading_html = generate_document(client, system_prompt, "reading.html")
    except anthropic.RateLimitError as e:
        retry_after = e.response.headers.get("retry-after", "unknown")
        raise SystemExit(f"Rate limited; retry after {retry_after}s") from e
    except anthropic.APIStatusError as e:
        raise SystemExit(f"API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise SystemExit(f"Network error calling Anthropic API: {e}") from e

    today = date.today()

    with open("reading.html", "w", encoding="utf-8") as f:
        f.write(inject_back_nav(reading_html, "index.html"))
    print("Wrote reading.html")

    os.makedirs(READINGS_ARCHIVE_DIR, exist_ok=True)
    archive_path = os.path.join(READINGS_ARCHIVE_DIR, f"{today.isoformat()}.html")
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(inject_back_nav(reading_html, "../../index.html"))
    print(f"Archived reading to {archive_path}")

    update_csv(args.csv, entries, today)
    print(f"Updated times_used/date_last_used for {len(entries)} entries in {args.csv}")

    flashcards_html = build_flashcards_html(args.csv, today)
    with open("flashcards.html", "w", encoding="utf-8") as f:
        f.write(flashcards_html)
    print("Wrote flashcards.html (rolling 7-day deck, built from vocab_master.csv)")

    os.makedirs("archive", exist_ok=True)
    flashcards_archive_html = build_flashcards_html(
        args.csv,
        today,
        window_days=None,
        page_title="Wortschatz-Karteikarten – Archiv",
        root_prefix="../",
    )
    with open("archive/flashcards.html", "w", encoding="utf-8") as f:
        f.write(flashcards_archive_html)
    print("Wrote archive/flashcards.html (all-time archive)")

    reading_archive = collect_reading_archive()
    rolling_card_count = len(collect_recent_entries(args.csv, today))
    word_count = approx_word_count(reading_html)
    card_of_day = pick_card_of_day(entries)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_index_html(today, card_of_day, word_count, rolling_card_count, reading_archive))
    print(f"Wrote index.html ({len(reading_archive)} reading(s) in archive)")


if __name__ == "__main__":
    main()
