"""Build the Cognito guide as a landing page plus one page per chapter, from the doc markdown.

Usage: build_multi.py DOC_MD TEMPLATE_HTML OUT_DIR
  TEMPLATE_HTML: the existing single-page post (supplies head, CSS, hero, diagram, sources footer)
  OUT_DIR: repo's posts/ directory; writes cognito-explained.html and cognito/<slug>.html
"""
import html
import os
import re
import sys

import markdown

MD, TEMPLATE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(MD, encoding="utf-8").read()
tpl = open(TEMPLATE, encoding="utf-8").read()

CHAPTERS = [
    # (slug, part, title, description, [section ids])
    ("basics", 1, "The basics", "Authentication vs authorization, identity providers, tokens, JWTs, OAuth and IAM, then how Cognito's pieces fit together.",
     ["start-here-the-basic-ideas-in-plain-words", "the-big-picture"]),
    ("pools", 1, "User Pools and Identity Pools", "What each pool does, how they chain together, and how one User Pool serves both people and apps.",
     ["user-pools-and-identity-pools", "one-user-pool-two-kinds-of-callers-people-and-apps"]),
    ("clients-and-pkce", 1, "Clients, secrets and PKCE", "Client IDs and secrets, the four app client types (web app, SPA, mobile, machine-to-machine), and how PKCE protects apps that can't keep a secret.",
     ["client-ids-and-client-secrets", "the-four-types-of-app-clients", "pkce-protecting-logins-for-apps-that-can-t-keep-a-secret"]),
    ("identity-providers", 1, "Google, Facebook and other identity providers", "Federation, trust chains, the two sets of client IDs, and the credentials Google and Facebook give Cognito and AgentCore.",
     ["how-a-user-pool-works-with-other-identity-providers", "how-identity-providers-trust-each-other",
      "the-confusing-part-two-sets-of-client-ids", "two-ways-to-bring-in-google-or-any-idp",
      "google-facebook-and-other-providers-the-credentials-behind-t"]),
    ("tokens-and-scopes", 1, "Tokens, scopes and resource servers", "What is inside ID, access and refresh tokens, how resource servers and custom scopes work, and where every claim comes from.",
     ["what-is-inside-a-token-claims-and-scopes", "resource-servers-and-custom-scopes-how-they-work", "defining-claims-and-scopes-in-depth"]),
    ("identity-pools", 1, "Identity Pools and AWS credentials", "How an Identity Pool turns a login into temporary AWS credentials, its providers, flows and guest access, and how it picks IAM roles.",
     ["identity-pools-in-depth-from-a-login-to-aws-credentials", "iam-roles-and-identity-pools"]),
    ("access-control", 1, "How Cognito controls what a signed-in user can access", "Every layer that decides what a signed-in user can do, and who enforces each one.",
     ["how-cognito-controls-what-a-signed-in-user-can-access"]),
    ("callbacks", 1, "Callback URLs and callback servers", "Why logins come back through the browser, why OAuth uses a code, and what a callback server implements.",
     ["callback-urls-and-callback-servers"]),
    ("token-safety", 2, "Logging out, storing and checking tokens", "Revoking access, where to keep tokens safely, and a worked example of validating them in your API.",
     ["logging-out-and-cancelling-tokens", "where-to-keep-tokens-in-a-browser-or-app", "checking-tokens-in-your-api-a-worked-example"]),
    ("building-login", 2, "Building the login experience", "Managed login vs your own screens, Lambda triggers, and choosing an API Gateway authorizer.",
     ["cognito-s-login-page-vs-building-your-own-screens", "lambda-triggers-customizing-each-step", "choosing-an-api-gateway-authorizer"]),
    ("users", 2, "Moving and linking users", "Migrating users from an existing system, and avoiding duplicate accounts with account linking.",
     ["moving-existing-users-into-cognito", "account-linking-avoiding-duplicate-users"]),
    ("architecture", 2, "Architecture, regions and pricing", "Multi-tenancy, Cognito vs IAM Identity Center, regional outages, and pricing tiers and limits.",
     ["apps-with-many-customer-companies-multi-tenancy", "user-pool-vs-iam-identity-center-vs-iam-users",
      "regions-outages-and-backups", "pricing-tiers-and-limits"]),
    ("agentcore", 2, "Where AgentCore Identity fits next to Cognito", "How AI agents use Cognito for inbound access and AgentCore Identity for the services they call.",
     ["where-agentcore-identity-fits-next-to-cognito"]),
    ("glossary", 3, "Glossary", "One-line definitions of every term used in the guide.", ["glossary"]),
]
PART_NAMES = {1: "Part 1 · How it fits", 2: "Part 2 · When you build", 3: "Reference"}

# ---------- markdown -> html (same rules as the single-page build) ----------
lines = src.split("\n")
assert lines[0].startswith("# ")
fixed, in_code = [], False
for ln in lines[3:]:
    if ln.startswith("```"):
        in_code = not in_code
    elif not in_code and re.match(r"^  \S", ln):
        ln = "  " + ln
    fixed.append(ln)
body_md = "\n".join(fixed)
body_md = re.sub(r"^.*embedded content: trust chain.*$", "DIAGRAMPLACEHOLDER", body_md, flags=re.M)
cap_re = re.compile(r"^(Each arrow is a trust relationship with its own registration;.*)$", re.M)
cap = cap_re.search(body_md).group(1)
body_md = cap_re.sub("", body_md, count=1)

out = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"], output_format="html5")
fig = re.search(r"<figure>.*?</figure>", tpl, flags=re.S).group(0)
fig = re.sub(r"<figcaption>.*?</figcaption>", f"<figcaption>{cap}</figcaption>", fig, flags=re.S)
out = re.sub(r"<p>DIAGRAMPLACEHOLDER</p>", fig, out)


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

# Pull out the "Part 2" intro heading + paragraph; it becomes landing-page copy.
part2 = re.search(r"<h2>(Part 2[^<]*)</h2>\s*<p>(.*?)</p>", out, flags=re.S)
part2_intro = part2.group(2)
out = out.replace(part2.group(0), "")

# Split into sections at each h2.
pieces = re.split(r"(<h2>.*?</h2>)", out)
sections, titles = {}, {}
for i in range(1, len(pieces), 2):
    title = re.match(r"<h2>(.*?)</h2>", pieces[i]).group(1)
    sid = slug(title)
    titles[sid] = title
    sections[sid] = (title, pieces[i + 1].strip())

all_ids = [s for c in CHAPTERS for s in c[4]]
missing = set(sections) ^ set(all_ids)
assert not missing, f"chapter map out of sync with doc: {missing}"


def words(h):
    return len(re.sub(r"<[^>]+>", " ", h).split())


# ---------- page pieces from the template ----------
head = tpl.split("</head>")[0]
head = re.sub(r"^<!doctype html>.*?<head>\n", "", head, flags=re.S)
lead = re.search(r'<p class="lead">.*?</p>', tpl, flags=re.S).group(0)
hero = re.search(r'<header class="hero">.*?</header>', tpl, flags=re.S).group(0)
sources = re.search(r'<footer class="sources">.*?</footer>', tpl, flags=re.S).group(0)

EXTRA_CSS = """
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
    return DOC_HEAD + h + EXTRA_CSS + "</head>\n<body>\n"


def back_bar(href):
    return (f'<p class="back" style="max-width:1360px;margin:0 auto;padding:16px 20px 0;'
            f"font-family:'Bricolage Grotesque',system-ui,sans-serif;font-size:0.9rem\">"
            f'<a href="{href}">&larr; AWS Learning</a></p>\n')


def chapter_minutes(c):
    return max(1, round(sum(words(sections[s][1]) for s in c[4]) / 200))


total_minutes = sum(chapter_minutes(c) for c in CHAPTERS)


def sidebar(current=None, from_sub=True):
    pre = "" if from_sub else "cognito/"
    land = "../cognito-explained.html" if from_sub else "#"
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
        items.append(f'<li{cls}><a href="{pre}{c[0]}.html">{num}{c[2]}</a>{sub}</li>')
    return ('<nav class="toc" aria-label="Chapters">\n    <details open>\n      <summary>Chapters</summary>\n'
            f'      <a class="home" href="{land}">Cognito, Explained</a>\n      <ol>\n        '
            + "\n        ".join(items) + "\n      </ol>\n    </details>\n  </nav>")


os.makedirs(os.path.join(OUT, "cognito"), exist_ok=True)

# ---------- chapter pages ----------
for n, c in enumerate(CHAPTERS, 1):
    cslug, part, title, desc, ids = c
    body = []
    for s in ids:
        t, h = sections[s]
        if len(ids) > 1:
            body.append(f'<h2 id="{s}">{t}</h2>\n{h}')
        else:
            body.append(f'<span id="{s}"></span>\n{h}')
    prev_c = CHAPTERS[n - 2] if n > 1 else None
    next_c = CHAPTERS[n] if n < len(CHAPTERS) else None
    pager = '<nav class="pager" aria-label="Chapter navigation">'
    pager += (f'<a class="prev" href="{prev_c[0]}.html"><span class="dir">&larr; Previous</span><span class="t">{prev_c[2]}</span></a>'
              if prev_c else '<a class="prev" href="../cognito-explained.html"><span class="dir">&larr; Back to</span><span class="t">All chapters</span></a>')
    pager += (f'<a class="next" href="{next_c[0]}.html"><span class="dir">Next &rarr;</span><span class="t">{next_c[2]}</span></a>'
              if next_c else '<a class="next" href="../cognito-explained.html"><span class="dir">Back to &rarr;</span><span class="t">All chapters</span></a>')
    pager += "</nav>"
    label = f"Chapter {n} of {len(CHAPTERS) - 1}" if part != 3 else "Reference"
    page = (page_head(f"{title} · Cognito, Explained", desc)
            + back_bar("../../")
            + '<div class="page">\n'
            + '  <header class="hero chapter-hero">\n'
            + f'    <div class="crumbs"><a href="../cognito-explained.html">Cognito, Explained</a><span aria-hidden="true">/</span><span>{PART_NAMES[part]}</span></div>\n'
            + f'    <div class="eyebrow">{label} · about {chapter_minutes(c)} minutes</div>\n'
            + f'    <h1>{title}</h1>\n'
            + f'    <p class="dek">{desc}</p>\n'
            + '  </header>\n\n  '
            + sidebar(current=cslug)
            + '\n\n  <article>\n'
            + "\n\n".join(body)
            + "\n\n    " + pager
            + "\n\n    " + sources
            + "\n  </article>\n</div>\n</body>\n</html>\n")
    open(os.path.join(OUT, "cognito", f"{cslug}.html"), "w", encoding="utf-8").write(page)

# ---------- landing page ----------
hero_l = re.sub(r"about \d+ minutes", f"{len(CHAPTERS) - 1} chapters · about {total_minutes} minutes in all", hero)


def card(n, c):
    num = f"Chapter {n:02d}" if c[1] != 3 else "Reference"
    secs = len(c[4])
    return (f'<li><a href="cognito/{c[0]}.html"><span class="num">{num}</span><span class="t">{c[2]}</span>'
            f'<span class="d">{c[3]}</span><span class="m">about {chapter_minutes(c)} min'
            f'{" · " + str(secs) + " sections" if secs > 1 else ""}</span></a></li>')


blocks, part_open = [], None
for n, c in enumerate(CHAPTERS, 1):
    if c[1] != part_open:
        if part_open is not None:
            blocks.append("</ul>")
        blocks.append(f'<div class="part-head">{PART_NAMES[c[1]]}</div>')
        if c[1] == 1:
            blocks.append('<p class="part-intro">The core ideas, in order. Each chapter builds on the ones before it.</p>')
        elif c[1] == 2:
            blocks.append(f'<p class="part-intro">{part2_intro}</p>')
        blocks.append('<ul class="cards">')
        part_open = c[1]
    blocks.append(card(n, c))
blocks.append("</ul>")

redirect_map = {s: f"cognito/{c[0]}.html" for c in CHAPTERS for s in c[4]}
redirect_js = ("<script>(function(){var m=" + repr(redirect_map).replace("'", '"')
               + ";var h=location.hash.slice(1);if(h&&m[h]){location.replace(m[h]+'#'+h);}})();</script>\n")

landing = (page_head("Cognito, Explained", "A beginner-friendly guide to Amazon Cognito: User Pools, Identity Pools, client IDs, PKCE, tokens and access control, in 12 chapters.")
           + redirect_js
           + back_bar("../")
           + '<div class="page landing">\n  ' + hero_l + "\n\n  <article>\n    " + lead + "\n\n    "
           + "\n    ".join(blocks)
           + "\n\n    " + sources + "\n  </article>\n</div>\n</body>\n</html>\n")
open(os.path.join(OUT, "cognito-explained.html"), "w", encoding="utf-8").write(landing)

print(f"chapters {len(CHAPTERS)}, total minutes {total_minutes}")
for n, c in enumerate(CHAPTERS, 1):
    print(f"  {n:02d} {c[0]:20s} {chapter_minutes(c):3d} min  {len(c[4])} sections")
