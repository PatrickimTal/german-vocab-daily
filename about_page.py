"""about.html builder. Static content -- run once (or whenever the copy
changes), not part of the daily generate.py pipeline.
"""
from site_theme import CHIP_CSS, GOOGLE_FONTS_LINKS, HEADER_CSS, NAV_TOGGLE_JS, TOKENS_CSS, render_header

PAGE_CSS = (
    TOKENS_CSS
    + HEADER_CSS
    + CHIP_CSS
    + """
.about {
  max-width: 640px;
  margin: 0 auto;
  padding: 8px var(--pad-x) 40px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.about h1 {
  font-family: var(--font-serif);
  font-weight: 400;
  font-size: 34px;
  line-height: 1.1;
  color: var(--ink);
  margin: 0;
}
.about p { font-size: 16px; color: var(--ink-body); margin: 0; }
.about .chip-legend { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.about .panel {
  background: var(--panel-bg); border-radius: var(--r-md);
  padding: 18px 20px; font-size: 14px; color: var(--ink-muted);
}
.about .panel a { color: var(--blue-text); }
@media (min-width: 640px) {
  .about { padding-top: 16px; }
  .about h1 { font-size: 42px; }
}
"""
)


def build_about_html():
    header_html = render_header(root_prefix="")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Über das Projekt – Deutscher Wortschatz</title>
{GOOGLE_FONTS_LINKS}
<style>
{PAGE_CSS}
</style>
</head>
<body>
{header_html}

<main id="main" class="about">
  <h1>Über das Projekt</h1>
  <p>Deutscher Wortschatz – Täglich generiert jeden Tag automatisch einen neuen
  C1-Lesetext im Feuilleton-Stil und wählt dafür 20 Vokabeln aus einer
  handkuratierten Liste aus – gewichtet zugunsten der Wörter, die am längsten
  nicht mehr vorkamen. Die Karteikarten der letzten sieben Tage und ein
  vollständiges Archiv aller bisher verwendeten Vokabeln stehen jederzeit zum
  Wiederholen bereit.</p>
  <p>Jede Vokabel gehört zu einer von sieben Kategorien, farblich codiert und
  auf Karten, Filtern und im Archiv konsistent verwendet:</p>
  <div class="chip-legend">
    <span class="chip chip--verb-praep">Verb + Präp.</span>
    <span class="chip chip--verb-kasus">Verb + Kasus</span>
    <span class="chip chip--redemittel">Redemittel</span>
    <span class="chip chip--nomen-praep">Nomen + Präp.</span>
    <span class="chip chip--adjektiv-praep">Adjektiv + Präp.</span>
    <span class="chip chip--redewendung">Redewendung</span>
    <span class="chip chip--wortschatz">Wortschatz</span>
  </div>
  <p class="panel">Lesetext und Vokabelauswahl werden mit der Claude API
  generiert; Karteikarten, Archiv und diese Seite werden deterministisch aus
  der Vokabelliste gebaut. Quellcode: <a href="https://github.com/PatrickimTal/german-vocab-daily">github.com/PatrickimTal/german-vocab-daily</a>.</p>
</main>

<footer class="site-footer">Automatisch generiert · German Vocab Daily</footer>

<script>
{NAV_TOGGLE_JS}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    with open("about.html", "w", encoding="utf-8") as f:
        f.write(build_about_html())
    print("Wrote about.html")
