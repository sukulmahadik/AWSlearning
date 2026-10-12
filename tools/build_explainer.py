"""Build an "<Topic>, Explained" guide: a landing page plus one page per chapter, from a Claude Doc export.

Usage:
    python3 tools/build_explainer.py tools/topics/<topic>.py DOC_MD posts/

The topic config module defines (see tools/topics/cognito.py for a full example):
    SLUG           folder for chapter pages, e.g. "cognito" -> posts/cognito/<chapter>.html
    LANDING        landing page file name, e.g. "cognito-explained.html"
    TITLE          guide title, e.g. "Cognito, Explained"
    DESCRIPTION    meta description for the landing page
    HERO_HTML      the landing hero <header class="hero">...</header>; "%%META%%" is replaced by
                   "N chapters · about M minutes in all"
    LEAD_HTML      the lead paragraph(s) shown under the hero on the landing page
    PART1_INTRO    one sentence under the Part 1 heading on the landing page
    CHAPTERS       [(slug, part, title, description, [h2 section ids])], part 1, 2 or 3 (3 = Reference)
    DIAGRAMS       [(placeholder_regex, figure_html, caption_regex_or_None)]: replaces a doc embed placeholder
                   line with an inline figure; caption_regex picks the paragraph that becomes its caption
    SOURCES_HTML   footer HTML, or None to build it from a "Sources" section in the doc
    EXTRA_CSS      optional topic-specific CSS (string, may be empty)
    STYLE_TEMPLATE path of the HTML file whose <head> supplies fonts and the shared CSS
"""
import html
import importlib.util
import os
import re
import sys

import markdown

CFG_PATH, MD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("topic", CFG_PATH)
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)

src = open(MD, encoding="utf-8").read()
style_tpl = open(cfg.STYLE_TEMPLATE, encoding="utf-8").read()
CHAPTERS = cfg.CHAPTERS
PART_NAMES = {1: "Part 1 · How it fits", 2: "Part 2 · When you build", 3: "Reference"}
DISCLAIMER = "<p>Views are my own and do not represent my employer.</p>"

# ---------- markdown -> html ----------
lines = src.split("\n")
assert lines[0].startswith("# "), "expected the doc title on the first line"
fixed, in_code = [], False
for ln in lines[3:]:  # skip title, blank line, byline
    if ln.startswith("```"):
        in_code = not in_code
    elif not in_code and re.match(r"^  \S", ln):
        ln = "  " + ln  # export nests lists by 2 spaces; python-markdown needs 4
    fixed.append(ln)
body_md = "\n".join(fixed)

figures = []
for i, (placeholder, figure_html, caption_re) in enumerate(getattr(cfg, "DIAGRAMS", [])):
    token = f"DIAGRAMPLACEHOLDER{i}"
    body_md, n = re.subn(rf"^.*{placeholder}.*$", token, body_md, count=1, flags=re.M)
    assert n == 1, f"diagram placeholder not found: {placeholder}"
    fig = figure_html
    if caption_re:
        m = re.search(caption_re, body_md, flags=re.M)
        assert m, f"diagram caption not found: {caption_re}"
        body_md = body_md.replace(m.group(0), "", 1)
        fig = re.sub(r"<figcaption>.*?</figcaption>", lambda _: f"<figcaption>{m.group(1)}</figcaption>", fig, flags=re.S)
    figures.append((token, fig))

out = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")
for token, fig in figures:
    out = out.replace(f"<p>{token}</p>", fig)


def slug(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60].rstrip("-")


def wrap_table(m):
    t = m.group(0)
    cols = len(re.findall(r"<th", t.split("</tr>")[0]))
    return f'<div class="{"table-wrap wide" if cols >= 3 else "table-wrap"}">{t}</div>'


out = re.sub(r"<table>.*?</table>", wrap_table, out, flags=re.S)
out = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener">', out)

# "Part 2" heading + its first paragraph become landing-page copy.
part2 = re.search(r"<h2>(Part 2[^<]*)</h2>\s*<p>(.*?)</p>", out, flags=re.S)
part2_intro = part2.group(2) if part2 else ""
if part2:
    out = out.replace(part2.group(0), "")

pieces = re.split(r"(<h2>.*?</h2>)", out)
sections = {}
for i in range(1, len(pieces), 2):
    title = re.match(r"<h2>(.*?)</h2>", pieces[i]).group(1)
    sections[slug(title)] = (title, pieces[i + 1].strip())

# Sources: from config, or from a "Sources" section in the doc.
if cfg.SOURCES_HTML is not None:
    sources = cfg.SOURCES_HTML
else:
    _, sources_body = sections.pop("sources")
    sources = f'<footer class="sources">\n      <p><strong>Sources</strong></p>\n      {sources_body}\n      {DISCLAIMER}\n    </footer>'

all_ids = [s for c in CHAPTERS for s in c[4]]
missing = set(sections) ^ set(all_ids)
assert not missing, f"chapter map out of sync with doc: {sorted(missing)}"


def words(h):
    return len(re.sub(r"<[^>]+>", " ", h).split())


def chapter_minutes(c):
    return max(1, round(sum(words(sections[s][1]) for s in c[4]) / 200))


total_minutes = sum(chapter_minutes(c) for c in CHAPTERS)
n_chapters = len([c for c in CHAPTERS if c[1] != 3])

# ---------- shared page pieces ----------
head = style_tpl.split("</head>")[0]
head = re.sub(r"^<!doctype html>.*?<head>\n", "", head, flags=re.S)

SHARED_CSS = """
<style>
/* Chapter navigation */
.crumbs { font-family: var(--display); font-size: 0.9rem; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.crumbs a { color: var(--muted); text-decoration: none; }
.crumbs a:hover { color: var(--accent); }
.chapter-hero { grid-column: 1 / -1; display: grid; gap: 14px; border-bottom: 1px solid var(--rule); padding-bottom: 28px; }
.chapter-hero h1 { font-size: clamp(2rem, 4.6vw, 3.2rem); }
.chapter-hero .dek { font-size: 1.15rem; }
article > h2:first-child { margin-top: 0; border-top: none; padding-top: 0; }
nav.toc .home { font-weight: 700; color: var(--fg); text-decoration: none; display: block; margin-bottom: 6px; }
nav.toc li.current > a { color: var(--accent); font-weight: 700; }
nav.toc li.current ul { list-style: none; padding: 4px 0 6px 14px; margin: 0; border-left: 2px solid var(--accent-soft); display: grid; gap: 2px; }
nav.toc li.current ul a { font-size: 0.84rem; }
nav.toc .num { font-family: var(--mono); font-size: 0.72rem; color: var(--muted); margin-right: 6px; }
.pager { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 64px; }
.pager a { display: grid; gap: 4px; padding: 16px 20px; border: 1px solid var(--rule); border-radius: 10px; background: var(--surface); text-decoration: none; color: var(--fg); }
.pager a:hover { border-color: var(--accent); }
.pager a.next { text-align: right; }
.pager .dir { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
.pager .t { font-family: var(--display); font-weight: 700; font-size: 1.05rem; color: var(--accent); }
/* Landing page */
.page.landing { grid-template-columns: minmax(0, 1fr); }
.page.landing article { max-width: none; }
.page.landing article > ul.cards { max-width: none; }
.part-head { font-family: var(--mono); font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); margin: 48px 0 6px; padding-top: 20px; border-top: 2px solid var(--fg); }
.part-intro { color: var(--muted); max-width: 78ch; margin: 0 0 20px; }
.cards { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 16px; }
.cards li { margin: 0; }
.cards a { display: grid; gap: 8px; height: 100%; padding: 20px 22px; border: 1px solid var(--rule); border-radius: 12px; background: var(--surface); color: var(--fg); text-decoration: none; transition: border-color .15s, transform .15s; }
.cards a:hover { border-color: var(--accent); }
@media (prefers-reduced-motion: no-preference) { .cards a:hover { transform: translateY(-2px); } }
.cards .num { font-family: var(--mono); font-size: 0.78rem; color: var(--accent); }
.cards .t { font-family: var(--display); font-weight: 700; font-size: 1.25rem; line-height: 1.2; }
.cards .d { color: var(--muted); font-size: 1rem; line-height: 1.55; }
.cards .m { font-family: var(--mono); font-size: 0.75rem; color: var(--muted); margin-top: auto; }
</style>
"""

DOC_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
"""


def page_head(title, desc):
    h = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, count=1)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', h, count=1)
    extra = getattr(cfg, "EXTRA_CSS", "")
    extra = f"<style>\n{extra}\n</style>\n" if extra.strip() else ""
    return DOC_HEAD + h + SHARED_CSS + extra + "</head>\n<body>\n"


def back_bar(href):
    return (f'<p class="back" style="max-width:1360px;margin:0 auto;padding:16px 20px 0;'
            f"font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:0.9rem\">"
            f'<a href="{href}">&larr; AWS Learning</a></p>\n')


LANDING_FROM_SUB = f"../{cfg.LANDING}"


def sidebar(current):
    items, last_part = [], None
    for n, c in enumerate(CHAPTERS, 1):
        if c[1] != last_part:
            items.append(f'<li class="part">{PART_NAMES[c[1]]}</li>')
            last_part = c[1]
        cls = ' class="current"' if c[0] == current else ""
        num = f'<span class="num">{n:02d}</span>' if c[1] != 3 else ""
        sub = ""
        if c[0] == current and len(c[4]) > 1:
            sub = "<ul>" + "".join(f'<li><a href="#{s}">{sections[s][0]}</a></li>' for s in c[4]) + "</ul>"
        items.append(f'<li{cls}><a href="{c[0]}.html">{num}{c[2]}</a>{sub}</li>')
    return ('<nav class="toc" aria-label="Chapters">\n    <details open>\n      <summary>Chapters</summary>\n'
            f'      <a class="home" href="{LANDING_FROM_SUB}">{cfg.TITLE}</a>\n      <ol>\n        '
            + "\n        ".join(items) + "\n      </ol>\n    </details>\n  </nav>")


os.makedirs(os.path.join(OUT, cfg.SLUG), exist_ok=True)

# ---------- chapter pages ----------
for n, c in enumerate(CHAPTERS, 1):
    cslug, part, title, desc, ids = c
    body = []
    for s in ids:
        t, h = sections[s]
        body.append(f'<h2 id="{s}">{t}</h2>\n{h}' if len(ids) > 1 else f'<span id="{s}"></span>\n{h}')
    prev_c = CHAPTERS[n - 2] if n > 1 else None
    next_c = CHAPTERS[n] if n < len(CHAPTERS) else None
    pager = '<nav class="pager" aria-label="Chapter navigation">'
    pager += (f'<a class="prev" href="{prev_c[0]}.html"><span class="dir">&larr; Previous</span><span class="t">{prev_c[2]}</span></a>'
              if prev_c else f'<a class="prev" href="{LANDING_FROM_SUB}"><span class="dir">&larr; Back to</span><span class="t">All chapters</span></a>')
    pager += (f'<a class="next" href="{next_c[0]}.html"><span class="dir">Next &rarr;</span><span class="t">{next_c[2]}</span></a>'
              if next_c else f'<a class="next" href="{LANDING_FROM_SUB}"><span class="dir">Back to &rarr;</span><span class="t">All chapters</span></a>')
    pager += "</nav>"
    label = f"Chapter {n} of {n_chapters}" if part != 3 else "Reference"
    page = (page_head(f"{title} · {cfg.TITLE}", desc)
            + back_bar("../../")
            + '<div class="page">\n'
            + '  <header class="hero chapter-hero">\n'
            + f'    <div class="crumbs"><a href="{LANDING_FROM_SUB}">{cfg.TITLE}</a><span aria-hidden="true">/</span><span>{PART_NAMES[part]}</span></div>\n'
            + f'    <div class="eyebrow">{label} · about {chapter_minutes(c)} minutes</div>\n'
            + f'    <h1>{title}</h1>\n'
            + f'    <p class="dek">{desc}</p>\n'
            + '  </header>\n\n  '
            + sidebar(cslug)
            + '\n\n  <article>\n'
            + "\n\n".join(body)
            + "\n\n    " + pager
            + "\n\n    " + sources
            + "\n  </article>\n</div>\n</body>\n</html>\n")
    open(os.path.join(OUT, cfg.SLUG, f"{cslug}.html"), "w", encoding="utf-8").write(page)

# ---------- landing page ----------
hero = cfg.HERO_HTML.replace("%%META%%", f"{n_chapters} chapters · about {total_minutes} minutes in all")


def card(n, c):
    num = f"Chapter {n:02d}" if c[1] != 3 else "Reference"
    secs = len(c[4])
    return (f'<li><a href="{cfg.SLUG}/{c[0]}.html"><span class="num">{num}</span><span class="t">{c[2]}</span>'
            f'<span class="d">{c[3]}</span><span class="m">about {chapter_minutes(c)} min'
            f'{" · " + str(secs) + " sections" if secs > 1 else ""}</span></a></li>')


blocks, part_open = [], None
for n, c in enumerate(CHAPTERS, 1):
    if c[1] != part_open:
        if part_open is not None:
            blocks.append("</ul>")
        blocks.append(f'<div class="part-head">{PART_NAMES[c[1]]}</div>')
        if c[1] == 1:
            blocks.append(f'<p class="part-intro">{cfg.PART1_INTRO}</p>')
        elif c[1] == 2 and part2_intro:
            blocks.append(f'<p class="part-intro">{part2_intro}</p>')
        blocks.append('<ul class="cards">')
        part_open = c[1]
    blocks.append(card(n, c))
blocks.append("</ul>")

redirect_map = {s: f"{cfg.SLUG}/{c[0]}.html" for c in CHAPTERS for s in c[4]}
redirect_js = ("<script>(function(){var m=" + repr(redirect_map).replace("'", '"')
               + ";var h=location.hash.slice(1);if(h&&m[h]){location.replace(m[h]+'#'+h);}})();</script>\n")

landing = (page_head(cfg.TITLE, cfg.DESCRIPTION)
           + redirect_js
           + back_bar("../")
           + '<div class="page landing">\n  ' + hero + "\n\n  <article>\n    " + cfg.LEAD_HTML + "\n\n    "
           + "\n    ".join(blocks)
           + "\n\n    " + sources + "\n  </article>\n</div>\n</body>\n</html>\n")
open(os.path.join(OUT, cfg.LANDING), "w", encoding="utf-8").write(landing)

print(f"{cfg.TITLE}: {n_chapters} chapters + reference, about {total_minutes} minutes")
for n, c in enumerate(CHAPTERS, 1):
    print(f"  {n:02d} {c[0]:22s} {chapter_minutes(c):3d} min  {len(c[4])} section(s)")
