"""Landing page (index.html) builder.

Scans archive/readings/*.html (one file per day, named YYYY-MM-DD.html)
to build a dated reading archive list, and links out to the current
flashcards deck and the all-time flashcards archive.
"""
import html
import os
import re
from datetime import datetime

READINGS_ARCHIVE_DIR = "archive/readings"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)

PAGE_CSS = """
:root{
  --bg:#0f172a;
  --panel:#1e293b;
  --accent:#38bdf8;
  --text-light:#e2e8f0;
  --muted:#94a3b8;
}
*{box-sizing:border-box;}
body{
  margin:0;
  padding:1.2rem 0.9rem 3rem;
  background:var(--bg);
  color:var(--text-light);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}
header{max-width:760px;margin:0 auto 1.5rem;text-align:center;}
h1{margin:0.2rem 0;font-size:1.7rem;}
.subtitle{margin:0;font-size:0.85rem;color:var(--muted);}

.quick-links{
  max-width:760px;margin:0 auto 2rem;
  display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:0.8rem;
}
.tile{
  display:flex;flex-direction:column;gap:0.2rem;
  background:var(--panel);border:1px solid #334155;border-radius:14px;
  padding:1rem;text-decoration:none;color:var(--text-light);
  transition:border-color 0.15s;
}
.tile:hover{border-color:var(--accent);}
.tile-emoji{font-size:1.4rem;}
.tile-title{font-weight:600;font-size:1rem;}
.tile-sub{font-size:0.78rem;color:var(--muted);}

.archive-section{max-width:760px;margin:0 auto 2rem;}
.archive-section h2{font-size:1.1rem;border-bottom:1px solid #334155;padding-bottom:0.4rem;}
.archive-list{list-style:none;margin:0;padding:0;}
.archive-list li{
  display:flex;gap:0.8rem;align-items:baseline;
  padding:0.55rem 0;border-bottom:1px solid #1e293b;
}
.archive-date{
  flex:0 0 auto;font-variant-numeric:tabular-nums;
  color:var(--muted);font-size:0.82rem;min-width:5.5rem;
}
.archive-list a{color:var(--text-light);text-decoration:none;font-size:0.92rem;}
.archive-list a:hover{color:var(--accent);text-decoration:underline;}
.empty-note{color:var(--muted);font-size:0.85rem;font-style:italic;}

footer{max-width:760px;margin:2rem auto 0;text-align:center;font-size:0.75rem;color:var(--muted);}
"""


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


def build_index_html(today, reading_archive):
    if reading_archive:
        archive_items = "\n".join(
            f'    <li><span class="archive-date">{d.strftime("%d.%m.%Y")}</span>'
            f'<a href="{html.escape(href)}">{html.escape(title)}</a></li>'
            for d, title, href in reading_archive
        )
    else:
        archive_items = '    <li class="empty-note">Noch keine archivierten Lesetexte.</li>'

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deutscher Wortschatz – Täglich</title>
<style>
{PAGE_CSS}
</style>
</head>
<body>

<header>
  <h1>Deutscher Wortschatz – Täglich</h1>
  <p class="subtitle">Stand: {today.strftime("%d.%m.%Y")} &middot; {len(reading_archive)} Lesetexte im Archiv</p>
</header>

<section class="quick-links">
  <a class="tile" href="reading.html">
    <span class="tile-emoji">📖</span>
    <span class="tile-title">Heutiger Lesetext</span>
    <span class="tile-sub">Neuester C1-Artikel</span>
  </a>
  <a class="tile" href="flashcards.html">
    <span class="tile-emoji">🗂️</span>
    <span class="tile-title">Karteikarten</span>
    <span class="tile-sub">Letzte 7 Tage</span>
  </a>
  <a class="tile" href="archive/flashcards.html">
    <span class="tile-emoji">📚</span>
    <span class="tile-title">Karteikarten-Archiv</span>
    <span class="tile-sub">Alle bisherigen Vokabeln</span>
  </a>
</section>

<section class="archive-section">
  <h2>Lesetext-Archiv</h2>
  <ul class="archive-list">
{archive_items}
  </ul>
</section>

<footer>Automatisch generiert &middot; German Vocab Daily</footer>

</body>
</html>
"""
