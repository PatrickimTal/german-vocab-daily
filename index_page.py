"""Landing page (index.html) builder -- 'Wortschatz Landing 2b' design.

Recreates the Claude Design handoff (design_handoff_wortschatz_landing/):
hero with the daily promise + a live "Karte des Tages" flashcard, three
entry points, and (adapted for this codebase, not in the original design)
a dated archive of past readings scanned from archive/readings/*.html.
"""
import html
import os
import re
from datetime import datetime

from site_theme import (
    CHIP_CSS,
    GOOGLE_FONTS_LINKS,
    HEADER_CSS,
    NAV_TOGGLE_JS,
    TOKENS_CSS,
    chip_slug,
    render_header,
)

READINGS_ARCHIVE_DIR = "archive/readings"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
ARTICLE_RE = re.compile(r"^(der|die|das)\s+(.+)$")
TRAILING_PAREN_RE = re.compile(r"\s*\([^)]*\)\s*$")

PAGE_CSS = (
    TOKENS_CSS
    + HEADER_CSS
    + CHIP_CSS
    + """
/* ---------- hero ---------- */

.hero {
  display: flex;
  flex-direction: column;
  gap: 26px;
  padding: 0 var(--pad-x);
}
.hero__copy { display: flex; flex-direction: column; gap: 16px; }
.hero__title {
  margin: 0;
  font-family: var(--font-serif);
  font-weight: 400;
  font-size: 38px;
  line-height: 1.08;
  letter-spacing: -0.01em;
  color: var(--ink);
}
.hero__kicker {
  margin: -8px 0 0;
  font-size: 12px;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--blue-text);
}
.hero__lede { margin: 0; font-size: 16px; color: var(--ink-body); }
.hero__actions { display: flex; flex-direction: column; gap: 14px; }

.btn {
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--r-pill);
  font-family: var(--font-sans);
  font-size: 16px;
  transition: background 150ms ease, color 150ms ease;
}
.btn--primary { min-height: 52px; background: var(--blue); color: #f7fcff; font-weight: 600; }
.btn--primary:hover { background: var(--blue-hover); color: #f7fcff; }
.btn--ghost { min-height: 48px; border: 1px solid var(--border); color: var(--ink-body); font-size: 15px; }
.btn--ghost:hover { background: rgba(255, 255, 255, 0.6); color: var(--ink-body); }

.stand {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.04em;
  color: var(--ink-faint);
}

/* ---------- card of the day ---------- */

.hero__card { display: flex; flex-direction: column; gap: 10px; }
.eyebrow {
  margin: 0;
  font-family: var(--font-mono);
  font-weight: 400;
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink-faint);
}
.flashcard {
  display: flex; flex-direction: column; gap: 13px;
  width: 100%; padding: 22px; text-align: left;
  background: var(--card-bg); border: 0; border-radius: var(--r-lg);
  box-shadow: var(--shadow-card); cursor: pointer;
  font-family: inherit;
  transition: background 150ms ease;
}
.flashcard:hover { background: var(--card-bg-hover); }
.flashcard__top { display: flex; align-items: center; justify-content: space-between; }
.flashcard__age { font-family: var(--font-mono); font-size: 10px; color: var(--ink-faint); }
.flashcard__term {
  font-family: var(--font-serif);
  font-size: 30px;
  line-height: 1.15;
  color: var(--ink);
}
.article { color: var(--article); }
.flashcard__back {
  display: flex; flex-direction: column; gap: 9px;
  border-top: 1px solid var(--rule); padding-top: 13px;
}
.flashcard__gloss { font-size: 17px; color: var(--ink-body); }
.flashcard__example { font-size: 14px; color: var(--ink-muted); }
.tag-de {
  font-family: var(--font-mono); font-size: 10px;
  padding: 2px 5px; margin-right: 7px;
  border-radius: var(--r-sm); background: var(--rule); color: var(--ink-body);
}
.flashcard[aria-expanded="false"] .flashcard__back { display: none; }
.flashcard[aria-expanded="true"] .flashcard__hint { display: none; }
.flashcard__hint { font-size: 14px; color: var(--ink-faint); }

/* ---------- entries ---------- */

.entries {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  padding: 26px var(--pad-x) 0;
}
.entry {
  display: flex; flex-direction: column; justify-content: center; gap: 3px;
  min-height: 48px; padding: 16px 18px;
  background: var(--panel-bg); border-radius: var(--r-md);
  transition: background 150ms ease;
}
.entry:hover { background: var(--panel-bg-hover); }
.entry__title { font-size: 15px; font-weight: 600; color: var(--ink); }
.entry__meta { font-size: 13px; color: var(--ink-muted); }

/* ---------- reading archive (adapted; not in the original design) ---------- */

.archive-section { padding: 30px var(--pad-x) 0; }
.archive-section h2 {
  font-family: var(--font-sans); font-size: 14px; font-weight: 600;
  color: var(--ink); margin: 0 0 12px;
}
.archive-list { list-style: none; margin: 0; padding: 0; }
.archive-list li {
  display: flex; gap: 14px; align-items: baseline;
  padding: 10px 0; border-bottom: 1px solid var(--rule);
}
.archive-date {
  flex: 0 0 auto; font-family: var(--font-mono); font-size: 11px;
  color: var(--ink-faint); min-width: 5.2rem;
}
.archive-list a { color: var(--ink-body); font-size: 14px; }
.archive-list a:hover { color: var(--blue-hover); text-decoration: underline; }
.empty-note { color: var(--ink-faint); font-size: 13px; font-style: italic; }

/* ---------- tablet ---------- */

@media (min-width: 640px) {
  :root { --pad-x: 44px; }
  .hero { padding: 34px var(--pad-x) 0; gap: 34px; }
  .hero__copy { gap: 20px; }
  .hero__title { font-size: 52px; line-height: 1.06; }
  .hero__kicker { font-size: 13px; letter-spacing: 0.1em; }
  .hero__lede { font-size: 18px; max-width: 52ch; }
  .hero__actions { flex-direction: row; align-items: center; gap: 20px; }
  .btn--primary { min-height: 0; padding: 16px 28px; }
  .btn--ghost {
    min-height: 0; padding: 0 0 2px; border: 0;
    border-bottom: 1px solid var(--underline); border-radius: 0; color: var(--ink-muted);
  }
  .btn--ghost:hover { background: none; }
  .stand { font-size: 12px; }
  .eyebrow { font-size: 11px; }
  .flashcard { padding: 26px 28px; gap: 14px; }
  .flashcard__term { font-size: 38px; }
  .flashcard__back { gap: 10px; padding-top: 14px; }
  .flashcard__gloss { font-size: 18px; }
  .flashcard__example { font-size: 15px; }
  .tag-de { font-size: 11px; padding: 2px 6px; margin-right: 8px; }
  .entries { grid-template-columns: repeat(3, 1fr); gap: 14px; padding-top: 34px; }
  .entry { padding: 18px 20px; }
  .archive-section { max-width: 760px; }
}

/* ---------- desktop ---------- */

@media (min-width: 1024px) {
  :root { --pad-x: 52px; }
  .hero, .entries, .archive-section {
    max-width: 1280px; margin-inline: auto;
  }
  .hero {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 52px;
    align-items: center;
    padding: 8px var(--pad-x) 0;
    min-height: 420px;
  }
  .hero__copy { gap: 22px; }
  .hero__title { font-size: 62px; line-height: 1.05; }
  .hero__kicker { font-size: 14px; }
  .hero__lede { max-width: 36ch; }
  .hero__card { gap: 14px; }
  .flashcard { padding: 30px 32px; gap: 18px; min-height: 280px; }
  .flashcard__term { font-size: 40px; }
  .flashcard__hint { margin-top: auto; }
  .entries { gap: 16px; padding: 30px var(--pad-x) 34px; }
  .entry { padding: 20px 22px; }
  .entry__title { font-size: 16px; }
  .entry__meta { font-size: 14px; }
  .archive-section { padding-top: 8px; max-width: 760px; margin-inline: 0; }
}
"""
)

PAGE_JS = (
    NAV_TOGGLE_JS
    + """
document.querySelectorAll('.flashcard').forEach(function (card) {
  card.addEventListener('click', function () {
    card.setAttribute('aria-expanded', card.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
  });
});
"""
)


def _extract_title(html_text):
    match = TITLE_RE.search(html_text)
    return match.group(1).strip() if match else "Lesetext"


def collect_reading_archive(archive_dir=READINGS_ARCHIVE_DIR):
    """Return [(date, title, relative_href), ...] newest first."""
    if not os.path.isdir(archive_dir):
        return []

    entries = []
    for filename in os.listdir(archive_dir):
        if not filename.endswith(".html"):
            continue
        stem = filename[: -len(".html")]
        try:
            d = datetime.strptime(stem, "%Y-%m-%d").date()
        except ValueError:
            continue
        with open(os.path.join(archive_dir, filename), encoding="utf-8") as f:
            title = _extract_title(f.read())
        entries.append((d, title, f"{archive_dir}/{filename}"))

    entries.sort(key=lambda e: e[0], reverse=True)
    return entries


def strip_trailing_annotations(text):
    prev = None
    while prev != text:
        prev = text
        text = TRAILING_PAREN_RE.sub("", text).strip()
    return text


def pick_card_of_day(entries):
    """Prefer a Wortschatz or Nomen + Präp. entry with a visible article
    (der/die/das) so the landing card can show the orange article colour."""

    def candidates(subtype):
        return [
            e
            for e in entries
            if e.get("subtype") == subtype and ARTICLE_RE.match(strip_trailing_annotations(e["german"]))
        ]

    for subtype in ("Wortschatz", "Nomen + Präp."):
        pool = candidates(subtype)
        if pool:
            return pool[0]
    return entries[0]


def render_card_of_day(entry):
    german_clean = strip_trailing_annotations(entry["german"])
    match = ARTICLE_RE.match(german_clean)
    if match:
        article, term = match.group(1), match.group(2)
        term_html = f'<span class="article">{html.escape(article)}</span> {html.escape(term)}'
    else:
        term_html = html.escape(german_clean)

    slug = chip_slug(entry.get("subtype", "Wortschatz"))
    subtype = entry.get("subtype", "Wortschatz")
    example_html = ""
    if entry.get("example_de"):
        example_html = (
            f'<span class="flashcard__example"><span class="tag-de">DE</span>'
            f'{html.escape(entry["example_de"])}</span>'
        )

    return f"""    <button class="flashcard" type="button" aria-expanded="true" aria-controls="flashcard-back">
      <span class="flashcard__top">
        <span class="chip chip--{slug}">{html.escape(subtype)}</span>
        <span class="flashcard__age">heute</span>
      </span>
      <span class="flashcard__term">{term_html}</span>
      <span class="flashcard__back" id="flashcard-back">
        <span class="flashcard__gloss">{html.escape(entry["english"])}</span>
        {example_html}
      </span>
      <span class="flashcard__hint">Klicken zum Umdrehen</span>
    </button>"""


def build_index_html(today, card_of_day_entry, reading_word_count, rolling_card_count, reading_archive):
    if reading_archive:
        archive_items = "\n".join(
            f'    <li><span class="archive-date">{d.strftime("%d.%m.%Y")}</span>'
            f'<a href="{html.escape(href)}">{html.escape(title)}</a></li>'
            for d, title, href in reading_archive
        )
    else:
        archive_items = '    <li class="empty-note">Noch keine archivierten Lesetexte.</li>'

    stand_date = today.strftime("%d.%m.%Y")
    stand_line = (
        f'Stand: <time datetime="{today.isoformat()}">{stand_date}</time> · '
        f"{rolling_card_count} Karten · {len(reading_archive)} Lesetext"
        f"{'e' if len(reading_archive) != 1 else ''} im Archiv"
    )

    header_html = render_header(root_prefix="")
    card_html = render_card_of_day(card_of_day_entry)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deutscher Wortschatz – Täglich</title>
{GOOGLE_FONTS_LINKS}
<style>
{PAGE_CSS}
</style>
</head>
<body>
{header_html}

<main id="main" class="hero">
  <div class="hero__copy">
    <h1 class="hero__title">Ein Lesetext. Zwanzig Wörter. Jeden Tag.</h1>
    <p class="hero__kicker">One article, twenty words, every morning</p>
    <p class="hero__lede">Jeden Morgen ein neuer C1-Artikel und die Vokabeln, die darin vorkommen. Als Karteikarten der letzten sieben Tage, dazu das vollständige Archiv.</p>
    <div class="hero__actions">
      <a class="btn btn--primary" href="reading.html">Heutigen Lesetext öffnen</a>
      <a class="btn btn--ghost" href="flashcards.html">Karteikarten der letzten 7 Tage</a>
    </div>
    <p class="stand">{stand_line}</p>
  </div>

  <section class="hero__card" aria-labelledby="card-of-day">
    <h2 class="eyebrow" id="card-of-day">Karte des Tages</h2>
{card_html}
  </section>
</main>

<nav class="entries" aria-label="Bereiche">
  <a class="entry" href="reading.html">
    <span class="entry__title">Heutiger Lesetext</span>
    <span class="entry__meta">Neuester C1-Artikel · rund {reading_word_count} Wörter</span>
  </a>
  <a class="entry" href="flashcards.html">
    <span class="entry__title">Karteikarten</span>
    <span class="entry__meta">Letzte 7 Tage · {rolling_card_count} Karten</span>
  </a>
  <a class="entry" href="archive/flashcards.html">
    <span class="entry__title">Karteikarten-Archiv</span>
    <span class="entry__meta">Alle bisherigen Vokabeln</span>
  </a>
</nav>

<section class="archive-section" aria-label="Lesetext-Archiv">
  <h2>Lesetext-Archiv</h2>
  <ul class="archive-list">
{archive_items}
  </ul>
</section>

<footer class="site-footer">Automatisch generiert · German Vocab Daily</footer>

<script>
{PAGE_JS}
</script>
</body>
</html>
"""
