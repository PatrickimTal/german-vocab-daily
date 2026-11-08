"""Shared design tokens for the 'Sprachgarten' visual language.

Source: design handoff "Deutscher Wortschatz - Taeglich, landing page
(direction 2b)" (Claude Design, Wortschatz Landing 2b.dc.html + reference/).
Single source of truth for colors/fonts/category chips so index.html,
flashcards.html, archive/flashcards.html, and about.html stay visually
consistent.
"""

GOOGLE_FONTS_LINKS = (
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700'
    "&family=Libre+Baskerville:wght@400;700&family=IBM+Plex+Mono:wght@400;500"
    '&display=swap" rel="stylesheet">'
)

TOKENS_CSS = """
:root {
  --site-green: #e9fae9;
  --page-bg: #fff;
  --card-bg: rgba(255, 255, 255, 0.85);
  --card-bg-hover: rgba(255, 255, 255, 0.97);
  --panel-bg: rgba(255, 255, 255, 0.62);
  --panel-bg-hover: rgba(255, 255, 255, 0.82);

  --ink: #082310;
  --ink-body: #304635;
  --ink-muted: #4b614f;
  --ink-faint: #617865;

  --blue: #0077c7;
  --blue-hover: #0061b0;
  --blue-text: #006eb8;
  --article: #c56c00;

  --border: #8ab091;
  --rule: #dce9de;
  --underline: #a8c7ad;

  --chip-verb-praep-bg: #cdecff;      --chip-verb-praep-fg: #004e95;
  --chip-verb-kasus-bg: #c2f2f8;      --chip-verb-kasus-fg: #005565;
  --chip-redemittel-bg: #f0e4ff;      --chip-redemittel-fg: #603b93;
  --chip-nomen-praep-bg: #c4f2cc;     --chip-nomen-praep-fg: #005222;
  --chip-adjektiv-praep-bg: #ffe1ac;  --chip-adjektiv-praep-fg: #7b4300;
  --chip-redewendung-bg: #ffd9d7;     --chip-redewendung-fg: #9a2733;
  --chip-wortschatz-bg: #dce9de;      --chip-wortschatz-fg: #384e3c;

  --font-serif: 'Libre Baskerville', Georgia, serif;
  --font-sans: 'Sora', system-ui, -apple-system, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, monospace;

  --r-sm: 4px;
  --r-md: 12px;
  --r-lg: 14px;
  --r-pill: 999px;
  --shadow-card: 0 12px 30px rgba(30, 70, 45, 0.1);

  --pad-x: 22px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--page-bg);
  color: var(--ink-body);
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

a { color: var(--blue-text); text-decoration: none; }
a:hover { color: var(--blue-hover); }

.skip { position: absolute; left: -9999px; }
.skip:focus { left: 12px; top: 12px; background: #fff; padding: 10px 14px; border-radius: var(--r-md); z-index: 100; }

:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; }

.site-footer {
  padding: 34px var(--pad-x);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-faint);
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
"""

# --- shared header/nav (brand + links + mobile hamburger) -----------------

HEADER_CSS = """
.site-bar {
  background: var(--blue-text);
  border-bottom: 1px solid var(--blue-text);
  box-shadow: 0 2px 12px rgba(30, 70, 45, 0.06);
}
.site-bar { margin-bottom: 26px; }
.site-bar :focus-visible { outline-color: #fff; }
.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px var(--pad-x);
}
.brand { display: flex; }
.brand__logo { display: block; height: 40px; width: auto; max-width: none; }
.nav { display: none; }
.nav-toggle {
  width: 44px; height: 44px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  background: none; border: 1px solid rgba(255, 255, 255, 0.6); border-radius: var(--r-md); cursor: pointer;
  transition: border-color 150ms ease;
}
.nav-toggle span { width: 18px; height: 1.5px; background: #fff; }
.nav-toggle:hover, .nav-toggle[aria-expanded="true"] { border-color: #fff; }
.mobile-nav { display: flex; flex-direction: column; padding: 4px var(--pad-x) 12px; gap: 2px; }
.mobile-nav a {
  min-height: 48px; display: flex; align-items: center;
  padding: 0 12px; margin: 0 -12px;
  color: #fff; font-size: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  transition: box-shadow 150ms ease;
}
.mobile-nav[hidden] { display: none; }
.mobile-nav a:hover, .mobile-nav a:active { color: #fff; box-shadow: inset 0 0 0 1px #fff; }
.mobile-nav .nav__current {
  min-height: 48px; display: flex; align-items: center;
  padding: 0 12px; margin: 0 -12px; font-size: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}
/* current page: inverted white pill with blue text */
.nav__current { background: #fff; color: var(--blue-text); cursor: default; }
@media (min-width: 640px) {
  .nav-toggle, .mobile-nav { display: none !important; }
  .nav { display: flex; align-items: center; gap: 8px; font-size: 15px; }
  .nav a {
    padding: 9px 16px;
    border: 1px solid transparent;
    border-radius: var(--r-pill);
    color: #fff;
    transition: border-color 150ms ease;
  }
  /* hover: text stays white, a white outline appears */
  .nav a:hover { border-color: #fff; color: #fff; }
  .nav .nav__current {
    padding: 9px 16px; border: 1px solid #fff; border-radius: var(--r-pill);
  }
  .brand__logo { height: 48px; }
  .site-header { padding: 18px var(--pad-x); }
  .site-bar { margin-bottom: 34px; --pad-x: 44px; }
}
@media (min-width: 1024px) {
  .site-header { max-width: 1280px; margin-inline: auto; }
  .site-bar { margin-bottom: 44px; --pad-x: 52px; }
}
"""

NAV_LINKS = [
    ("reading.html", "Lesetext"),
    ("flashcards.html", "Karteikarten"),
    ("about.html", "Über das Projekt"),
    ("index.html", "Home"),
]


def render_header(active_href=None, root_prefix=""):
    def href(path):
        return f"{root_prefix}{path}"

    def link_html(path, label, indent):
        # The current page is shown as a static blue pill, not a link.
        if path == active_href:
            return f'{indent}<span class="nav__current" aria-current="page">{label}</span>'
        return f'{indent}<a href="{href(path)}">{label}</a>'

    desktop_links = "\n".join(link_html(p, l, "    ") for p, l in NAV_LINKS)
    mobile_links = "\n".join(link_html(p, l, "  ") for p, l in NAV_LINKS)

    return f"""<a class="skip" href="#main">Zum Inhalt springen</a>

<div class="site-bar">
<header class="site-header">
  <a class="brand" href="{href('index.html')}">
    <img class="brand__logo" src="{href('wortschatz_logo_white.png')}" width="521" height="112" alt="Täglicher Deutscher Wortschatz C1">
  </a>
  <nav class="nav" aria-label="Hauptnavigation">
{desktop_links}
  </nav>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Menü öffnen">
    <span></span><span></span><span></span>
  </button>
</header>

<nav class="mobile-nav" id="mobile-nav" hidden aria-label="Hauptnavigation, mobil">
{mobile_links}
</nav>
</div>"""


# --- header for the AI-generated reading pages --------------------------
# Those pages bring their own CSS, so the header's tokens are scoped to
# .site-bar instead of :root and a few resets guard against the page's
# generic element styles. Blocks are wrapped in marker comments so the
# injection is idempotent (re-running replaces, never duplicates).

import re as _re

_MARK = "site-header"
_MARKED_RE = _re.compile(r"\n<!-- %s -->.*?<!-- /%s -->" % (_MARK, _MARK), _re.S)
_OLD_BACK_NAV_RE = _re.compile(r"\n?<p style=\"[^\"]*\"><a href=\"[^\"]*index\.html\"[^>]*>← Startseite</a></p>\n?")
# Reading date spliced into the article's meta line (inline, so it has its
# own marker instead of the comment-delimited blocks).
_TITLE_BLOCK_RE = _re.compile(
    r"<!-- %s -->\n<p class=\"site-page-title\">[^<]*</p>\n<!-- /%s -->\n" % (_MARK, _MARK))
_DATE_SPAN_RE = _re.compile(r'<span class="site-date">.*?</span>', _re.S)
_H1_RE = _re.compile(r"<h1[\s>]", _re.I)
_KICKER_BEFORE_RE = _re.compile(
    r'<(p|div)\b[^>]*class="[^"]*\bkicker\b[^"]*"[^>]*>(?:(?!</?\1\b).)*</\1>\s*$', _re.S | _re.I)
_META_RE = _re.compile(r'(<(p|div)\b[^>]*class="[^"]*\bmeta\b[^"]*"[^>]*>)(.*?)(</\2>)', _re.S | _re.I)
# "330 Wörter", "Wortzahl: 337", "Wörter: 341", "Wortzahl: ca. 310 Wörter"
_WORDCOUNT_RE = _re.compile(r"(?:Wortzahl|Wörter)\s*:\s*(?:ca\.\s*)?\d+(?:\s*Wörter)?|\d+\s*Wörter")
_SEP_RE = _re.compile(r"(?:\s|&nbsp;)*[·|](?:\s|&nbsp;)*")


def _scoped_header_css():
    tokens = TOKENS_CSS[TOKENS_CSS.index("{") + 1 : TOKENS_CSS.index("}")]
    return (
        ".site-bar {" + tokens + "\n  font-family: var(--font-sans); font-size: 16px; line-height: 1.55;\n"
        "  -webkit-font-smoothing: antialiased; text-align: left;\n}\n"
        ".site-bar *, .site-bar *::before, .site-bar *::after { box-sizing: border-box; }\n"
        ".site-bar header, .site-bar nav { margin: 0; border: 0; max-width: none; }\n"
        ".site-bar a { text-decoration: none; border-bottom: 0; }\n"
        ".skip { position: absolute; left: -9999px; }\n"
        ".skip:focus { left: 12px; top: 12px; background: #fff; padding: 10px 14px; border-radius: 12px; z-index: 100; }\n"
        + HEADER_CSS
        # the reading page's own top padding provides the gap below the bar
        + "\n.site-bar { margin-bottom: 0; }\n"
        # white page; "Lesetext" title styled like the about page's <h1>
        "html body { background: #fff; }\n"
        "html body p.site-page-title {\n"
        "  font-family: 'Libre Baskerville', Georgia, serif; font-weight: 400; font-style: normal;\n"
        "  font-size: 34px; line-height: 1.1; letter-spacing: normal; text-transform: none;\n"
        "  color: #082310; margin: 0 0 18px; padding: 0; border: 0; background: none;\n"
        "}\n"
        "@media (min-width: 640px) { html body p.site-page-title { font-size: 42px; } }\n"
        "@media (min-width: 640px) { .site-bar { --pad-x: 44px; } }\n"
        "@media (min-width: 1024px) { .site-bar { --pad-x: 52px; } }\n"
    )


# The reading pages pad <body> differently from day to day. Cancel that
# padding around the bar (so it spans the full width at the very top) and
# set the gap to the first line of the article to match the homepage.
_FIT_BAR_JS = """
(function () {
  var bar = document.querySelector('.site-bar');
  if (!bar) return;
  function firstTextTop() {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (bar.contains(n) || !n.nodeValue.trim()) return NodeFilter.FILTER_SKIP;
        var p = n.parentElement;
        if (!p || p.closest('script,style,.skip') || !p.offsetParent) return NodeFilter.FILTER_SKIP;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n = w.nextNode();
    if (!n) return null;
    var r = document.createRange(); r.selectNodeContents(n);
    return r.getBoundingClientRect().top;
  }
  function fit() {
    var cs = getComputedStyle(document.body);
    bar.style.marginTop = '-' + cs.paddingTop;
    bar.style.marginLeft = '-' + cs.paddingLeft;
    bar.style.marginRight = '-' + cs.paddingRight;
    bar.style.marginBottom = '0px';
    var w = window.innerWidth, target = w >= 1024 ? 44 : (w >= 640 ? 34 : 26);
    var top = firstTextTop();
    if (top === null) return;
    var gap = top - bar.getBoundingClientRect().bottom;
    bar.style.marginBottom = (target - gap) + 'px';
  }
  fit();
  window.addEventListener('load', fit);
  window.addEventListener('resize', fit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
})();
"""


def _add_reading_date(s, reading_date):
    """Put the reading's date next to the word count in its meta line."""
    stamp = reading_date.strftime("%d.%m.%Y")
    m = _META_RE.search(s)
    if not m:  # no meta line: give the date its own line under the headline
        h1_end = s.lower().find("</h1>")
        if h1_end < 0:
            return s
        h1_end += len("</h1>")
        return s[:h1_end] + f'\n<p><span class="site-date">{stamp}</span></p>' + s[h1_end:]
    inner = m.group(3)
    sep_m = _SEP_RE.search(inner)
    sep = sep_m.group(0) if sep_m else " · "
    span = f'<span class="site-date">{sep}{stamp}</span>'
    wc = _WORDCOUNT_RE.search(inner)
    at = wc.end() if wc else len(inner.rstrip())
    inner = inner[:at] + span + inner[at:]
    return s[: m.start(3)] + inner + s[m.end(3):]


def _add_page_title(s, block, title):
    """Insert a page title above the article's kicker/headline."""
    h1 = _H1_RE.search(s)
    if not h1:
        return s
    pos = h1.start()
    kicker = _KICKER_BEFORE_RE.search(s[:pos])
    if kicker:
        pos = kicker.start()
    return s[:pos] + block(f'<p class="site-page-title">{title}</p>').lstrip("\n") + "\n" + s[pos:]


def inject_site_header(html_text, root_prefix="", active_href=None, reading_date=None,
                       page_title="Lesetext"):
    """Put the shared top menu into a standalone (AI-generated) page, plus a
    page title and (when reading_date is given) the date in the meta line."""
    s = strip_site_header(html_text)
    s = _OLD_BACK_NAV_RE.sub("\n", s, count=1)
    def block(body):
        return f"\n<!-- {_MARK} -->\n{body}\n<!-- /{_MARK} -->"

    if page_title:
        s = _add_page_title(s, block, page_title)
    if reading_date is not None:
        s = _add_reading_date(s, reading_date)

    style = block(f"<style>\n{_scoped_header_css()}</style>")
    header = block(render_header(active_href=active_href, root_prefix=root_prefix))
    script = block(f"<script>{NAV_TOGGLE_JS}{_FIT_BAR_JS}</script>")
    s, n_head = _re.subn(r"</head>", lambda m: style + m.group(0), s, count=1, flags=_re.I)
    s, n_body = _re.subn(r"<body[^>]*>", lambda m: m.group(0) + header, s, count=1, flags=_re.I)
    s, _ = _re.subn(r"</body>", lambda m: script + m.group(0), s, count=1, flags=_re.I)
    return s if (n_head and n_body) else html_text


def strip_site_header(html_text):
    s = _DATE_SPAN_RE.sub("", html_text)
    s = _MARKED_RE.sub("", s)
    # page title block (indented, so not preceded by a newline)
    return _TITLE_BLOCK_RE.sub("", s)


NAV_TOGGLE_JS = """
document.querySelectorAll('.nav-toggle').forEach(function (toggle) {
  var panel = document.getElementById(toggle.getAttribute('aria-controls'));
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    toggle.setAttribute('aria-label', open ? 'Menü öffnen' : 'Menü schließen');
    if (panel) panel.hidden = open;
  });
});
"""

# --- category chips ---------------------------------------------------

SUBTYPE_ORDER = [
    "Verb + Präp.",
    "Verb + Kasus",
    "Redemittel",
    "Nomen + Präp.",
    "Adjektiv + Präp.",
    "Redewendung",
    "Wortschatz",
]

SUBTYPE_CHIP_SLUG = {
    "Verb + Präp.": "verb-praep",
    "Verb + Kasus": "verb-kasus",
    "Redemittel": "redemittel",
    "Nomen + Präp.": "nomen-praep",
    "Adjektiv + Präp.": "adjektiv-praep",
    "Redewendung": "redewendung",
    "Wortschatz": "wortschatz",
}

CHIP_CSS = """
.chip {
  display: inline-flex; align-items: center;
  padding: 5px 11px;
  border-radius: var(--r-pill);
  font-size: 12px; font-weight: 600;
  white-space: nowrap;
}
.chip--verb-praep      { background: var(--chip-verb-praep-bg);      color: var(--chip-verb-praep-fg); }
.chip--verb-kasus      { background: var(--chip-verb-kasus-bg);      color: var(--chip-verb-kasus-fg); }
.chip--redemittel      { background: var(--chip-redemittel-bg);      color: var(--chip-redemittel-fg); }
.chip--nomen-praep     { background: var(--chip-nomen-praep-bg);     color: var(--chip-nomen-praep-fg); }
.chip--adjektiv-praep  { background: var(--chip-adjektiv-praep-bg);  color: var(--chip-adjektiv-praep-fg); }
.chip--redewendung     { background: var(--chip-redewendung-bg);     color: var(--chip-redewendung-fg); }
.chip--wortschatz      { background: var(--chip-wortschatz-bg);      color: var(--chip-wortschatz-fg); }
"""


def chip_slug(subtype):
    return SUBTYPE_CHIP_SLUG.get(subtype, "wortschatz")
