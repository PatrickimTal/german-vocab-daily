"""Deterministic flashcards.html builder.

Builds a rolling flashcards.html directly from vocab_master.csv's
date_last_used column -- no LLM call, so it's fast, free, and immune to
truncation. Shows every entry used within the last WINDOW_DAYS days,
newest first by default, with client-side sort (chronological / by
subtype) and subtype filter checkboxes. Badges/filters are keyed off the
'subtype' column (see classify_subtypes.py) rather than the coarse
'type' column.
"""
import csv
import html
import json
from datetime import datetime

WINDOW_DAYS = 7
DEFAULT_SUBTYPE = "Wortschatz"

SUBTYPE_ORDER = [
    "Verb + Präp.",
    "Verb + Kasus",
    "Redemittel",
    "Nomen + Präp.",
    "Adjektiv + Präp.",
    "Redewendung",
    "Wortschatz",
]
SUBTYPE_BADGE_CLASS = {
    "Verb + Präp.": "b-verbprep",
    "Verb + Kasus": "b-verbkasus",
    "Redemittel": "b-redemittel",
    "Nomen + Präp.": "b-nounprep",
    "Adjektiv + Präp.": "b-adjprep",
    "Redewendung": "b-redewendung",
    "Wortschatz": "b-wortschatz",
}


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
    badge_class = SUBTYPE_BADGE_CLASS[subtype]
    badge_label = subtype
    german = html.escape(row["german"])
    english = html.escape(row["english"])
    example_de = html.escape(row["example_de"]) if row["example_de"] else ""
    example_en = html.escape(row["example_en"]) if row["example_en"] else ""
    date_tag = days_ago_label(entry_date, today)

    example_html = ""
    if example_de or example_en:
        parts = ['<div class="ex">']
        if example_de:
            parts.append(f'<p class="de"><span class="label">DE</span>{example_de}</p>')
        if example_en:
            parts.append(f'<p class="en"><span class="label">EN</span>{example_en}</p>')
        parts.append("</div>")
        example_html = "".join(parts)

    return f"""  <label class="card" data-id="{index}" data-type="{html.escape(subtype)}" data-date="{entry_date.isoformat()}">
    <input type="checkbox">
    <div class="inner">
      <div class="face front">
        <span class="badge {badge_class}">{badge_label}</span>
        <span class="term">{german}</span>
        <span class="date-tag">{date_tag}</span>
        <span class="hint">tap to reveal</span>
      </div>
      <div class="face back">
        <div class="en-meaning">{english}</div>
        {example_html}
      </div>
    </div>
  </label>"""


FLASHCARDS_CSS = """
:root{
  --bg:#0f172a;
  --card-front:#1e293b;
  --card-back:#f8fafc;
  --accent:#38bdf8;
  --accent-dark:#0369a1;
  --text-light:#e2e8f0;
  --text-dark:#1e293b;
  --green:#4ade80;
  --amber:#fbbf24;
  --teal:#2dd4bf;
  --pink:#f472b6;
  --violet:#a78bfa;
  --orange:#fb923c;
}
*{box-sizing:border-box;}
body{
  margin:0;
  padding:1rem 0.8rem 3rem;
  background:var(--bg);
  color:var(--text-light);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}
.back-nav{max-width:960px;margin:0 auto 0.5rem;font-size:0.85rem;}
.back-nav a{color:var(--accent);text-decoration:none;}
.back-nav a:hover{text-decoration:underline;}
header{max-width:960px;margin:0 auto 1rem;text-align:center;}
h1{margin:0.2rem 0;font-size:1.6rem;}
.subtitle{margin:0;font-size:0.85rem;color:#94a3b8;}

.controls{
  position:sticky;top:0;z-index:10;
  max-width:960px;margin:0 auto 1.2rem;
  background:rgba(15,23,42,0.92);
  backdrop-filter:blur(6px);
  border:1px solid #1e293b;
  border-radius:12px;
  padding:0.7rem 0.9rem;
  display:flex;flex-wrap:wrap;gap:0.6rem 1rem;align-items:center;
}
.ctrl-label{font-size:0.78rem;color:#94a3b8;margin-right:0.3rem;}
.sort-group,.filter-group{display:flex;align-items:center;flex-wrap:wrap;gap:0.4rem;}
.sort-btn{
  background:#1e293b;color:var(--text-light);border:1px solid #334155;
  border-radius:999px;padding:0.3rem 0.8rem;font-size:0.8rem;cursor:pointer;
}
.sort-btn.active{background:var(--accent);color:#0f172a;border-color:var(--accent);font-weight:600;}
.filter-chip{
  display:inline-flex;align-items:center;gap:0.3rem;
  background:#1e293b;border:1px solid #334155;border-radius:999px;
  padding:0.25rem 0.7rem;font-size:0.78rem;cursor:pointer;
}
.filter-chip input{accent-color:var(--accent);}
.count-line{margin-left:auto;font-size:0.78rem;color:#94a3b8;}

main{
  max-width:960px;margin:0 auto;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:0.9rem;
}

.card{display:block;cursor:pointer;perspective:1200px;}
.card input{display:none;}
.card .inner{
  position:relative;width:100%;min-height:170px;
  transition:transform 0.5s;transform-style:preserve-3d;
}
.card input:checked ~ .inner{transform:rotateY(180deg);}
.face{
  position:absolute;inset:0;
  border-radius:14px;padding:0.9rem;
  backface-visibility:hidden;
  display:flex;flex-direction:column;
  box-shadow:0 2px 10px rgba(0,0,0,0.25);
}
.front{background:var(--card-front);color:var(--text-light);}
.back{
  background:var(--card-back);color:var(--text-dark);
  transform:rotateY(180deg);justify-content:center;
}

.badge{
  align-self:flex-start;
  font-size:0.68rem;font-weight:600;
  padding:0.15rem 0.55rem;border-radius:999px;margin-bottom:0.5rem;
}
.b-verbprep{background:rgba(56,189,248,.15);color:var(--accent);}
.b-verbkasus{background:rgba(45,212,191,.15);color:var(--teal);}
.b-redemittel{background:rgba(244,114,182,.15);color:var(--pink);}
.b-nounprep{background:rgba(251,191,36,.15);color:var(--amber);}
.b-adjprep{background:rgba(167,139,250,.15);color:var(--violet);}
.b-redewendung{background:rgba(251,146,60,.15);color:var(--orange);}
.b-wortschatz{background:rgba(74,222,128,.15);color:var(--green);}

.term{font-size:1.05rem;font-weight:600;flex:1;}
.date-tag{font-size:0.68rem;color:#64748b;margin-top:0.4rem;}
.hint{font-size:0.68rem;color:#64748b;margin-top:0.2rem;}

.en-meaning{font-weight:600;font-size:1rem;margin-bottom:0.5rem;text-align:center;}
.ex p{margin:0.25rem 0;font-size:0.8rem;line-height:1.3;}
.ex .label{font-weight:700;font-size:0.65rem;color:var(--accent-dark);margin-right:0.35rem;}

footer{max-width:960px;margin:1.5rem auto 0;text-align:center;font-size:0.75rem;color:#64748b;}
"""

FLASHCARDS_JS = """
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


def build_flashcards_html(
    csv_path,
    today,
    window_days=WINDOW_DAYS,
    page_title="Wortschatz-Karteikarten – C1",
    scope_label=None,
    nav_html="",
):
    recent = collect_recent_entries(csv_path, today, window_days=window_days)
    if not recent:
        scope = "the last {window_days} days" if window_days else "the archive"
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
        f'    <label class="filter-chip"><input type="checkbox" class="type-filter" '
        f'value="{html.escape(st)}" checked> {html.escape(st)}</label>'
        for st in SUBTYPE_ORDER
    )
    flashcards_js = FLASHCARDS_JS.replace(
        "__SUBTYPE_ORDER_JSON__", json.dumps(SUBTYPE_ORDER, ensure_ascii=False)
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<style>
{FLASHCARDS_CSS}
</style>
</head>
<body>
{nav_html}
<header>
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

<main id="cardGrid">
{cards_html}
</main>

<footer>Klicken oder tippen zum Umdrehen &middot; viel Erfolg beim Lernen!</footer>

<script>
{flashcards_js}
</script>
</body>
</html>
"""
