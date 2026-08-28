"""Deterministic flashcards.html builder -- 'Sprachgarten' visual language.

Builds a rolling flashcards.html directly from vocab_master.csv's
date_last_used column -- no LLM call, so it's fast, free, and immune to
truncation. Shows every entry used within the last WINDOW_DAYS days,
newest first by default, with client-side sort (chronological / by
category) and colour-coded category filter chips. Badges/filters are
keyed off the 'subtype' column (see classify_subtypes.py); the seven
category colours live in site_theme.py and are shared with index.html
and about.html.
"""
import csv
import html
import json
from datetime import datetime

from site_theme import (
    CHIP_CSS,
    GOOGLE_FONTS_LINKS,
    HEADER_CSS,
    NAV_TOGGLE_JS,
    SUBTYPE_ORDER,
    TOKENS_CSS,
    chip_slug,
    render_header,
)

WINDOW_DAYS = 7
DEFAULT_SUBTYPE = "Wortschatz"


def collect_recent_entries(csv_path, today, window_days=WINDOW_DAYS):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    recent = []
    for row in rows:
        ds = row["date_last_used"].strip()
        if not ds:
            continue
        try:
            d = datetime.strptime(ds, "%Y-%m-%d").date()
        except ValueError:
            continue
        age = (today - d).days
        if age < 0:
            continue  # ignore bogus future dates
        if window_days is None or age < window_days:
            recent.append((d, row))

    def subtype_of(row):
        return row.get("subtype") if row.get("subtype") in SUBTYPE_ORDER else DEFAULT_SUBTYPE

    recent.sort(
        key=lambda pair: (
            -pair[0].toordinal(),  # newest date first
            SUBTYPE_ORDER.index(subtype_of(pair[1])),
            pair[1]["german"].lower(),
        )
    )
    return recent


def days_ago_label(d, today):
    n = (today - d).days
    if n <= 0:
        return "heute"
    if n == 1:
        return "gestern"
    return f"vor {n} Tagen"


def render_card(index, entry_date, row, today):
    subtype = row.get("subtype") if row.get("subtype") in SUBTYPE_ORDER else DEFAULT_SUBTYPE
    slug = chip_slug(subtype)
    german = html.escape(row["german"])
    english = html.escape(row["english"])
    example_de = html.escape(row["example_de"]) if row["example_de"] else ""
    example_en = html.escape(row["example_en"]) if row["example_en"] else ""
    date_tag = days_ago_label(entry_date, today)

    example_html = ""
    if example_de or example_en:
        parts = ['<div class="ex">']
        if example_de:
            parts.append(f'<p class="de"><span class="tag-de">DE</span>{example_de}</p>')
        if example_en:
            parts.append(f'<p class="en"><span class="tag-de">EN</span>{example_en}</p>')
        parts.append("</div>")
        example_html = "".join(parts)

    return f"""  <label class="card" data-id="{index}" data-type="{html.escape(subtype)}" data-date="{entry_date.isoformat()}">
    <input type="checkbox">
    <div class="inner">
      <div class="face front">
        <span class="chip chip--{slug}">{html.escape(subtype)}</span>
        <span class="term">{german}</span>
        <span class="date-tag">{date_tag}</span>
        <span class="hint">Klicken zum Umdrehen</span>
      </div>
      <div class="face back">
        <div class="en-meaning">{english}</div>
        {example_html}
      </div>
    </div>
  </label>"""


PAGE_CSS = (
    TOKENS_CSS
    + HEADER_CSS
    + CHIP_CSS
    + """
.page-header{max-width:960px;margin:0 auto 1rem;text-align:center;padding:0 var(--pad-x);}
.page-header h1{
  margin:0.2rem 0;font-family:var(--font-serif);font-weight:400;
  font-size:2rem;color:var(--ink);
}
.page-header .subtitle{margin:0;font-size:0.85rem;color:var(--ink-faint);font-family:var(--font-mono);}

.controls{
  position:sticky;top:0;z-index:10;
  max-width:960px;margin:0 auto 1.2rem;
  background:rgba(233,250,233,0.92);
  backdrop-filter:blur(6px);
  border:1px solid var(--rule);
  border-radius:var(--r-md);
  padding:0.7rem 0.9rem;
  display:flex;flex-wrap:wrap;gap:0.6rem 1rem;align-items:center;
}
.ctrl-label{font-size:0.78rem;color:var(--ink-faint);margin-right:0.3rem;}
.sort-group,.filter-group{display:flex;align-items:center;flex-wrap:wrap;gap:0.4rem;}
.sort-btn{
  background:var(--panel-bg);color:var(--ink-body);border:1px solid var(--border);
  border-radius:var(--r-pill);padding:0.3rem 0.8rem;font-size:0.8rem;cursor:pointer;
  font-family:var(--font-sans);
}
.sort-btn.active{background:var(--blue);color:#f7fcff;border-color:var(--blue);font-weight:600;}
.count-line{margin-left:auto;font-size:0.78rem;color:var(--ink-faint);font-family:var(--font-mono);}

.filter-chip{
  position:relative;cursor:pointer;opacity:0.55;
  transition:opacity 150ms ease, box-shadow 150ms ease;
}
.filter-chip input{
  position:absolute;opacity:0;width:1px;height:1px;
}
.filter-chip:has(input:checked){opacity:1;box-shadow:inset 0 0 0 1.5px currentColor;}
.filter-chip:focus-within{outline:2px solid var(--blue);outline-offset:2px;}

#cardGrid{
  max-width:960px;margin:0 auto;padding:0 var(--pad-x) 2rem;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:0.9rem;
}

.card{display:block;cursor:pointer;perspective:1200px;}
.card input{display:none;}
.card .inner{
  position:relative;width:100%;min-height:180px;
  transition:transform 0.5s;transform-style:preserve-3d;
}
.card input:checked ~ .inner{transform:rotateY(180deg);}
.face{
  position:absolute;inset:0;
  border-radius:var(--r-lg);padding:1rem;
  backface-visibility:hidden;
  display:flex;flex-direction:column;
  background:var(--card-bg);
  box-shadow:var(--shadow-card);
}
.front{color:var(--ink);}
.back{
  color:var(--ink-body);
  transform:rotateY(180deg);justify-content:center;
}

.chip{align-self:flex-start;margin-bottom:0.5rem;}

.term{font-family:var(--font-serif);font-size:1.3rem;line-height:1.2;color:var(--ink);flex:1;}
.date-tag{font-family:var(--font-mono);font-size:0.68rem;color:var(--ink-faint);margin-top:0.4rem;}
.hint{font-size:0.7rem;color:var(--ink-faint);margin-top:0.2rem;}

.en-meaning{font-weight:600;font-size:1.05rem;margin-bottom:0.5rem;text-align:center;color:var(--ink);}
.ex p{margin:0.25rem 0;font-size:0.82rem;line-height:1.35;color:var(--ink-muted);}
.ex .tag-de{
  font-family:var(--font-mono);font-weight:700;font-size:0.62rem;
  padding:1px 5px;margin-right:0.4rem;border-radius:var(--r-sm);
  background:var(--rule);color:var(--ink-body);
}

@media (min-width: 640px){
  .page-header, .controls, #cardGrid { padding-left: var(--pad-x); padding-right: var(--pad-x); }
}
"""
)

PAGE_JS = (
    NAV_TOGGLE_JS
    + """
(function(){
  var grid = document.getElementById('cardGrid');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
  var sortDateBtn = document.getElementById('sortDateBtn');
  var sortTypeBtn = document.getElementById('sortTypeBtn');
  var typeOrder = __SUBTYPE_ORDER_JSON__;
  var visibleCountEl = document.getElementById('visibleCount');

  function sortCards(mode){
    var sorted = cards.slice().sort(function(a, b){
      if(mode === 'type'){
        var ta = typeOrder.indexOf(a.dataset.type);
        var tb = typeOrder.indexOf(b.dataset.type);
        if(ta !== tb) return ta - tb;
      }
      if(a.dataset.date !== b.dataset.date){
        return a.dataset.date < b.dataset.date ? 1 : -1;
      }
      return a.querySelector('.term').textContent.localeCompare(
        b.querySelector('.term').textContent, 'de'
      );
    });
    sorted.forEach(function(card){ grid.appendChild(card); });
    sortDateBtn.classList.toggle('active', mode === 'date');
    sortTypeBtn.classList.toggle('active', mode === 'type');
  }

  function applyFilter(){
    var checked = {};
    document.querySelectorAll('.type-filter:checked').forEach(function(cb){
      checked[cb.value] = true;
    });
    var visible = 0;
    cards.forEach(function(card){
      var show = !!checked[card.dataset.type];
      card.style.display = show ? '' : 'none';
      if(show) visible++;
    });
    visibleCountEl.textContent = visible;
  }

  sortDateBtn.addEventListener('click', function(){ sortCards('date'); });
  sortTypeBtn.addEventListener('click', function(){ sortCards('type'); });
  document.querySelectorAll('.type-filter').forEach(function(cb){
    cb.addEventListener('change', applyFilter);
  });

  sortCards('date');
  applyFilter();
})();
"""
)


def build_flashcards_html(
    csv_path,
    today,
    window_days=WINDOW_DAYS,
    page_title="Wortschatz-Karteikarten – C1",
    scope_label=None,
    root_prefix="",
):
    recent = collect_recent_entries(csv_path, today, window_days=window_days)
    if not recent:
        scope = f"the last {window_days} days" if window_days else "the archive"
        raise RuntimeError(f"No vocabulary entries found for {scope} -- nothing to build.")

    cards_html = "\n".join(
        render_card(i, d, row, today) for i, (d, row) in enumerate(recent)
    )
    oldest_date, newest_date = recent[-1][0], recent[0][0]
    if oldest_date != newest_date:
        date_range = f"{oldest_date.strftime('%d.%m.')}–{newest_date.strftime('%d.%m.%Y')}"
    else:
        date_range = newest_date.strftime("%d.%m.%Y")
    count = len(recent)
    if scope_label is None:
        scope_label = (
            f"Vokabeln der letzten {window_days} Tage" if window_days else "Alle bisher verwendeten Vokabeln"
        )

    filter_chips_html = "\n".join(
        f'    <label class="filter-chip chip chip--{chip_slug(st)}">'
        f'<input type="checkbox" class="type-filter" value="{html.escape(st)}" checked> {html.escape(st)}</label>'
        for st in SUBTYPE_ORDER
    )
    page_js = PAGE_JS.replace(
        "__SUBTYPE_ORDER_JSON__", json.dumps(SUBTYPE_ORDER, ensure_ascii=False)
    )
    header_html = render_header(root_prefix=root_prefix)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
{GOOGLE_FONTS_LINKS}
<style>
{PAGE_CSS}
</style>
</head>
<body>
{header_html}

<main id="main">
<header class="page-header">
  <h1>Wortschatz-Karteikarten</h1>
  <p class="subtitle">{html.escape(scope_label)} · {date_range} · {count} Karten insgesamt</p>
</header>

<div class="controls">
  <div class="sort-group">
    <span class="ctrl-label">Sortieren:</span>
    <button id="sortDateBtn" class="sort-btn active" data-sort="date" type="button">Chronologisch</button>
    <button id="sortTypeBtn" class="sort-btn" data-sort="type" type="button">Nach Kategorie</button>
  </div>
  <div class="filter-group">
    <span class="ctrl-label">Filter:</span>
{filter_chips_html}
  </div>
  <div class="count-line"><span id="visibleCount">{count}</span> / {count} Karten sichtbar</div>
</div>

<div id="cardGrid">
{cards_html}
</div>
</main>

<footer class="site-footer">Klicken oder tippen zum Umdrehen · viel Erfolg beim Lernen!</footer>

<script>
{page_js}
</script>
</body>
</html>
"""
