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
  --page-bg: #e9fae9;
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
.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px var(--pad-x);
}
.brand { display: flex; flex-direction: column; gap: 1px; color: var(--ink); }
.brand:hover { color: var(--ink); }
.brand__name { font-family: var(--font-serif); font-size: 17px; }
.brand__kicker {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-faint);
}
.nav { display: none; }
.nav-toggle {
  width: 44px; height: 44px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  background: none; border: 1px solid var(--border); border-radius: var(--r-md); cursor: pointer;
}
.nav-toggle span { width: 18px; height: 1.5px; background: var(--ink-body); }
.mobile-nav { display: flex; flex-direction: column; padding: 4px var(--pad-x) 12px; gap: 2px; }
.mobile-nav a {
  min-height: 48px; display: flex; align-items: center;
  color: var(--ink-body); font-size: 16px; border-bottom: 1px solid var(--rule);
}
@media (min-width: 640px) {
  .nav-toggle, .mobile-nav { display: none !important; }
  .nav { display: flex; align-items: center; gap: 24px; font-size: 15px; }
  .nav a { color: var(--ink-body); }
  .nav__about { padding: 10px 20px; border: 1px solid var(--border); border-radius: var(--r-pill); }
  .site-header { padding: 34px var(--pad-x) 0; }
}
@media (min-width: 1024px) {
  .site-header { max-width: 1280px; margin-inline: auto; padding: 24px var(--pad-x); }
}
"""

NAV_LINKS = [
    ("reading.html", "Lesetext"),
    ("flashcards.html", "Karteikarten"),
    ("archive/flashcards.html", "Archiv"),
]


def render_header(active_href=None, root_prefix=""):
    def href(path):
        return f"{root_prefix}{path}"

    def link_html(path, label, css_class=""):
        cls = f' class="{css_class}"' if css_class else ""
        return f'    <a{cls} href="{href(path)}">{label}</a>'

    desktop_links = "\n".join(link_html(p, l) for p, l in NAV_LINKS)
    mobile_links = "\n".join(
        f'  <a href="{href(p)}">{l}</a>' for p, l in NAV_LINKS
    )

    return f"""<a class="skip" href="#main">Zum Inhalt springen</a>

<header class="site-header">
  <a class="brand" href="{href('index.html')}">
    <span class="brand__name">Deutscher Wortschatz</span>
    <span class="brand__kicker">täglich · C1</span>
  </a>
  <nav class="nav" aria-label="Hauptnavigation">
{desktop_links}
    <a class="nav__about" href="{href('about.html')}">Über das Projekt</a>
  </nav>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Menü öffnen">
    <span></span><span></span><span></span>
  </button>
</header>

<nav class="mobile-nav" id="mobile-nav" hidden aria-label="Hauptnavigation, mobil">
{mobile_links}
  <a href="{href('about.html')}">Über das Projekt</a>
</nav>"""


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
