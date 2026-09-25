#!/usr/bin/env python3
"""Build the portfolio pages of understory.mengyahh.com from data/portfolio.json.

    python scripts/build_portfolio.py

Writes portfolio/<slug>/index.html for every entry in "groups" and assets/portfolio.css.
"groups" are shown; "parked" entries are kept in the data file but not built (put them back into "groups" with a slug to show them).
The top navigation, colours and fonts are taken from about.html so that all pages stay consistent. Stdlib only.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://understory.mengyahh.com'
MAIN = 'https://mengyahh.com'
EMAIL = 'mengyahh@gmail.com'
esc = html.escape

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600'
         '&family=Karla:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')

PF_CSS = '''
  /* portfolio pages */
  .wrap { max-width: 980px; }
  .hero h1 { max-width: 24em; }
  .eyebrow a { color: inherit; text-decoration: none; }
  .eyebrow a:hover { text-decoration: underline; }
  section.pf { padding-block: 12px 24px; }
  .pf-row { display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 0 36px; padding-block: 34px; border-bottom: 1px solid var(--border); }
  .pf-row:last-child { border-bottom: 0; }
  .pf-info h2 { font-family: "Karla", "Noto Sans TC", sans-serif; font-size: 17px; font-weight: 700; color: var(--moss); margin: 0 0 8px; letter-spacing: 0; }
  .pf-info p { margin: 0 0 8px; font-size: 14px; line-height: 1.75; color: var(--ink-soft); }
  .pf-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; align-items: start; }
  .pf-grid.c1 { grid-template-columns: minmax(0, 460px); }
  .pf-grid.c2, .pf-grid.wide { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .pf-item { margin: 0; min-width: 0; }
  .pf-item > a, .pf-item > .yt { display: block; position: relative; overflow: hidden; border-radius: 4px; border: 1px solid var(--border-strong); background: var(--surface); }
  .pf-item img { display: block; width: 100%; height: auto; transition: transform .35s ease; }
  .pf-item > a:hover img { transform: scale(1.03); }
  .pf-item > a.ph { cursor: zoom-in; }
  .pf-item > a.out { cursor: alias; }
  .pf-item figcaption { margin-top: 8px; font-size: 13px; line-height: 1.65; color: var(--ink-soft); }
  .yt { width: 100%; padding: 0; cursor: pointer; font: inherit; aspect-ratio: 16 / 9; }
  .yt img { height: 100%; object-fit: cover; }
  .yt iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
  .yt-play { position: absolute; left: 50%; top: 50%; width: 60px; height: 60px; margin: -30px 0 0 -30px; border-radius: 50%; background: rgba(20, 24, 15, 0.62); border: 2px solid rgba(255, 255, 255, 0.9); transition: background .2s ease; }
  .yt-play::after { content: ""; position: absolute; left: 23px; top: 17px; border-style: solid; border-width: 12px 0 12px 20px; border-color: transparent transparent transparent #fff; }
  .yt:hover .yt-play { background: color-mix(in srgb, var(--moss) 90%, transparent); }
  .back { margin: 26px 0 0; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 13px; }
  .back a { text-decoration: none; border-bottom: 1px solid var(--border-strong); padding-bottom: 2px; }
  .back a:hover { border-color: var(--moss); }
  @media (max-width: 760px) {
    .pf-row { grid-template-columns: minmax(0, 1fr); gap: 14px 0; }
    .pf-grid, .pf-grid.c3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .pf-grid.c1, .pf-grid.wide { grid-template-columns: minmax(0, 1fr); }
  }
  @media (prefers-reduced-motion: reduce) { .pf-item img, .yt-play { transition: none; } .pf-item > a:hover img { transform: none; } }

  /* photo viewer (opened by assets/js/lightbox.js) */
  dialog.lb { border: 0; padding: 0; background: transparent; max-width: 100vw; max-height: 100vh; width: 100vw; height: 100vh; }
  dialog.lb::backdrop { background: rgba(12, 14, 9, 0.95); }
  .lb-inner { position: relative; width: 100%; height: 100%; display: grid; place-items: center; padding: 56px 12px 64px; }
  .lb img { max-width: min(100%, 1280px); max-height: calc(100vh - 130px); max-height: calc(100dvh - 130px); width: auto; height: auto; object-fit: contain; border-radius: 3px; box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5); }
  .lb-cap { position: absolute; left: 0; right: 0; bottom: 14px; text-align: center; color: #e8e6dc; font-size: 14px; padding: 0 60px; }
  .lb-cap .mono { color: #b6b9a8; font-size: 12.5px; margin-left: 8px; }
  .lb button { position: absolute; width: 44px; height: 44px; border-radius: 50%; border: 1px solid rgba(255, 255, 255, 0.28); background: rgba(0, 0, 0, 0.35); color: #fff; font-size: 22px; line-height: 1; cursor: pointer; display: grid; place-items: center; }
  .lb button:hover { background: rgba(255, 255, 255, 0.16); }
  .lb button:focus-visible { outline: 2px solid #fff; }
  .lb .x { top: 10px; right: 10px; }
  .lb .prev { left: 10px; top: 50%; transform: translateY(-50%); }
  .lb .next { right: 10px; top: 50%; transform: translateY(-50%); }
  @media (max-width: 640px) { .lb .prev { left: 4px; } .lb .next { right: 4px; } }
'''


def about_parts():
    """Colours, base rules, top navigation and footer, copied from about.html so the pages match."""
    a = open(os.path.join(ROOT, 'about.html'), encoding='utf-8').read()
    style = re.search(r'<style>\n(  :root \{.*?)</style>', a, re.S).group(1)
    head = style[:style.index('  section.block {')]                      # tokens, base, nav, eyebrow, hero
    footer = re.search(r'  footer \{.*?\n  footer p \{[^\n]*\n', style, re.S).group(0)
    nav = re.search(r'<nav class="topbar">.*?</nav>', a, re.S).group(0)
    nav_js = re.search(r'<script>\n\(function \(\) \{\n  var nav = document.getElementById\(\'menu\'\);.*?</script>', a, re.S).group(0)
    # the navigation lives one page-level deeper here: /portfolio/<slug>/
    nav = nav.replace('href="index.html', 'href="../../index.html').replace('href="about.html"', 'href="../../about.html"')
    nav = nav.replace(' aria-current="page"', '').replace('href="#contact"', 'href="../../about.html#contact"')
    return head, footer, nav, nav_js


def resolve(s, base):
    return s.replace('@ASSET/', f'{base}assets/').replace('@SITE/', MAIN + '/').replace('@BLOG/', MAIN + '/blog/')


def cover(g):
    for r in g['rows']:
        for m in r['media']:
            return (m['poster'] if m['type'] == 'video' else m['src'])
    return None


def rows_html(g, gi, base):
    rows = []
    for ri, r in enumerate(g['rows']):
        has_video = any(m['type'] == 'video' for m in r['media'])
        cls = 'wide' if has_video else {1: 'c1', 2: 'c2'}.get(len(r['media']), 'c3')
        gid = f'pf-{gi}-{ri}'
        items = []
        for i, m in enumerate(r['media'], 1):
            cap = f'<figcaption>{resolve(m["caption"], base)}</figcaption>' if m.get('caption') else ''
            if m['type'] == 'video':
                items.append(f'<figure class="pf-item"><button type="button" class="yt" data-yt="{esc(m["yt"])}" aria-label="播放影片：{esc(r["label"])}">'
                             f'<img src="{base}assets/{m["poster"]}" width="{m["w"]}" height="{m["h"]}" alt="" loading="lazy" decoding="async">'
                             f'<span class="yt-play" aria-hidden="true"></span></button>{cap}</figure>')
            elif m.get('href'):
                items.append(f'<figure class="pf-item"><a class="out" href="{esc(m["href"])}" target="_blank" rel="noopener">'
                             f'<img src="{base}assets/{m["thumb"]}" width="{m["w"]}" height="{m["h"]}" alt="{esc(r["label"])}：作品 {i}" loading="lazy" decoding="async"></a>{cap}</figure>')
            else:
                alt = f'{r["label"]}：作品 {i}'
                items.append(f'<figure class="pf-item"><a class="ph" href="{base}assets/{m["src"]}" data-group="{gid}" data-title="{esc(r["label"])}" data-alt="{esc(alt)}">'
                             f'<img src="{base}assets/{m["thumb"]}" width="{m["w"]}" height="{m["h"]}" alt="{esc(alt)}" loading="lazy" decoding="async"></a>{cap}</figure>')
        desc = ''.join(f'<p>{resolve(d, base)}</p>' for d in r['desc'])
        rows.append(f'<article class="pf-row"><div class="pf-info"><h2>{esc(r["label"])}</h2>{desc}</div>'
                    f'<div class="pf-grid {cls}">{"".join(items)}</div></article>')
    return ''.join(rows)


def page(g, gi, nav, nav_js):
    base = '../../'
    url = f'{SITE}/portfolio/{g["slug"]}/'
    labels = '、'.join(r['label'] for r in g['rows'])
    desc = f'{g["title"]}：{labels}。Understory 的作品。'
    img = cover(g)
    og = f'<meta property="og:image" content="{SITE}/assets/{img}">' if img else ''
    return f'''<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(g["title"])} | Understory</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Understory">
<meta property="og:title" content="{esc(g["title"])} | Understory">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
{og}
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{base}assets/portfolio.css">
{FONTS}
</head>
<body>
{nav}

<header class="hero">
  <div class="wrap">
    <p class="eyebrow"><a href="{base}about.html#projects">作品集</a></p>
    <h1>{esc(g["title"])}</h1>
    <p class="lede">{esc(labels)}</p>
  </div>
</header>

<section class="pf">
  <div class="wrap">
    {rows_html(g, gi, base)}
    <p class="back"><a href="{base}about.html#projects">← 回到做過的專案</a></p>
  </div>
</section>

<section class="contact" id="contact">
  <div class="wrap">
    <h2>先來聊聊吧</h2>
    <p class="lead">說說你遇到的狀況，我們再一起決定要做什麼。</p>
    <div class="mailbox"><span class="addr">{EMAIL}</span> <a href="mailto:{EMAIL}">寄信 →</a></div>
  </div>
</section>

<footer>
  <div class="wrap"><p>Understory · works by mengyahh</p></div>
</footer>

{nav_js}
<script src="{base}assets/js/lightbox.js" defer></script>
<script src="{base}assets/js/yt.js" defer></script>
</body>
</html>
'''


CONTACT_CSS = '''
  .contact { padding-block: 52px 44px; }
  .contact h2 { font-size: 25px; margin: 0 0 10px; }
  .contact .lead { margin: 0 0 18px; color: var(--ink-soft); font-size: 15px; max-width: 58ch; }
  .mailbox { display: inline-flex; align-items: center; gap: 14px; flex-wrap: wrap; padding: 12px 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; }
  .mailbox .addr { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 15px; user-select: all; }
  .mailbox a { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 13px; }
'''


def main():
    data = json.load(open(os.path.join(ROOT, 'data', 'portfolio.json'), encoding='utf-8'))
    head, footer, nav, nav_js = about_parts()
    css = head.rstrip() + '\n' + PF_CSS + CONTACT_CSS + footer
    with open(os.path.join(ROOT, 'assets', 'portfolio.css'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    for gi, g in enumerate(data['groups']):
        out = os.path.join(ROOT, 'portfolio', g['slug'], 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(page(g, gi, nav, nav_js))
        print('wrote', os.path.relpath(out, ROOT))


if __name__ == '__main__':
    main()
