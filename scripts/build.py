#!/usr/bin/env python3
"""Build the pages of understory.mengyahh.com that are written in Markdown.

    python scripts/build.py

content/about.md                  ->  about.html
content/portfolio/<slug>.md       ->  portfolio/<slug>/index.html      (files starting with "_" are drafts and are skipped)

index.html (the home page with the products) is still written by hand in HTML.
See content/README.md for how to write the Markdown files. Stdlib only.
"""
import glob
import html
import os
import re

import mdlite as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://understory.mengyahh.com'
esc = html.escape

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600'
         '&family=Karla:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')

NAV_JS = '''<script>
(function () {
  var nav = document.getElementById('menu');
  var menuBtn = document.querySelector('.menu-btn');
  var subBtns = Array.prototype.slice.call(document.querySelectorAll('.sub-btn'));

  function closeSubs(except) {
    subBtns.forEach(function (b) {
      var sub = document.getElementById(b.getAttribute('aria-controls'));
      if (sub === except) return;
      sub.classList.remove('open');
      b.setAttribute('aria-expanded', 'false');
    });
  }
  menuBtn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  subBtns.forEach(function (b) {
    var sub = document.getElementById(b.getAttribute('aria-controls'));
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      closeSubs(sub);
      var open = sub.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-sub')) closeSubs();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeSubs(); nav.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); }
  });
  nav.addEventListener('click', function (e) {              // picking a link closes the menus
    if (e.target.closest('a')) {
      closeSubs();
      nav.classList.remove('open');
      menuBtn.setAttribute('aria-expanded', 'false');
    }
  });
})();
</script>'''

COPY_JS = '''<script>
  document.getElementById('copy').addEventListener('click', function () {
    var btn = this, text = document.getElementById('addr').textContent;
    function done(msg) { btn.textContent = msg; setTimeout(function () { btn.textContent = '複製 email'; }, 1800); }
    function fallback() {
      var r = document.createRange(); r.selectNodeContents(document.getElementById('addr'));
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); done('已選取，請按複製');
    }
    try {
      navigator.clipboard.writeText(text).then(function () { done('已複製'); }, fallback);
    } catch (e) { fallback(); }
  });
</script>'''


def nav_html(base, current):
    about = f'<a href="{base}about.html"' + (' aria-current="page"' if current == 'about' else '') + '>關於</a>'
    contact = '#contact' if current == 'about' else f'{base}about.html#contact'
    return f'''<nav class="topbar">
  <div class="wrap">
    <p class="wordmark"><a href="{base}index.html">under<span>story</span></a></p>
    <button type="button" class="menu-btn" aria-expanded="false" aria-controls="menu">選單</button>
    <ul class="topnav" id="menu">
      <li class="has-sub">
        <button type="button" class="sub-btn" aria-expanded="false" aria-haspopup="true" aria-controls="sub-appsheet">AppSheet<span class="caret" aria-hidden="true">▾</span></button>
        <ul class="sub" id="sub-appsheet">
          <li><a href="{base}index.html#freelance">自由工作者套件</a></li>
          <li><a href="{base}index.html#poultry">白肉雞飼養紀錄系統</a></li>
          <li><span class="soon">個案管理系統<em>準備中</em></span></li>
          <li><span class="soon">AppSheet 介紹<em>準備中</em></span></li>
        </ul>
      </li>
      <li><span class="soon">活動企劃<em>準備中</em></span></li>
      <li><span class="soon">挖掘在地<em>準備中</em></span></li>
      <li>{about}</li>
      <li><a href="{contact}">聯絡</a></li>
    </ul>
  </div>
</nav>'''


def page(*, base, title, desc, url, body, current=None, body_class='', og_image=None, extra_js=''):
    og = f'<meta property="og:image" content="{esc(og_image)}">\n' if og_image else ''
    cls = f' class="{body_class}"' if body_class else ''
    return f'''<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Understory">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
{og}<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{base}assets/site.css">
{FONTS}
</head>
<body{cls}>
{nav_html(base, current)}

{body}

<footer>
  <div class="wrap"><p>Understory · works by mengyahh</p></div>
</footer>

{NAV_JS}

{COPY_JS}
{extra_js}</body>
</html>
'''


# ------------------------------------------------------------------ about.md blocks

def section(sid, kicker, inner, style=''):
    st = f' style="{style}"' if style else ''
    return (f'<section class="block" id="{sid}"{st}>\n  <div class="wrap">\n    <p class="kicker">{M.esc(kicker)}</p>\n{inner}\n  </div>\n</section>\n')


def r_hero(args, body):
    lines = body.strip().split('\n')
    eyebrow, rest = lines[0].strip(), '\n'.join(lines[1:])
    bl = M.blocks(rest)
    h1 = next((r for k, r in bl if k == 'h1'), None)
    if not h1:
        raise SystemExit('::: hero needs a "# heading" line')
    title = re.sub(r'\*\*(.+?)\*\*', r'<span class="ask">\1</span>', M.esc(M.heading_text(h1)))
    lede = ''.join(f'<p class="lede">{M.inline(r)}</p>' for k, r in bl if k == 'p')
    return (f'<header class="hero" id="about">\n  <div class="wrap">\n    <p class="eyebrow">{M.esc(eyebrow)}</p>\n'
            f'    <h1>{title}</h1>\n    {lede}\n  </div>\n</header>\n')


def r_skills(args, body):
    h2, intro, cards, fields, tools = '', '', [], '', ''
    state, cur, in_tools = 'head', None, None
    for kind, raw in M.blocks(body):
        if kind == 'h2':
            h2 = f'    <h2>{M.inline(M.heading_text(raw))}</h2>\n'
        elif kind == 'h3':
            cur = {'title': M.heading_text(raw), 'parts': []}
            cards.append(cur)
            state = 'cards'
        elif kind == 'hr':
            state, cur = 'after', None
        elif kind == 'h4':
            in_tools = {'title': M.heading_text(raw), 'items': []}
            state = 'tools'
        elif state == 'head' and kind == 'p':
            intro = f'    <p class="intro">{M.inline(raw)}</p>\n'
        elif state == 'cards' and cur is not None:
            if kind == 'p':
                cur['parts'].append(f'<p>{M.inline(raw)}</p>')
            elif kind == 'quote':
                cur['parts'].append(f'<p class="note">{M.inline(M.quote_text(raw))}</p>')
            elif kind == 'ul':
                dl = ''.join(f'<dt>{M.inline(a)}</dt><dd>{M.inline(b)}</dd>' for a, b in (re.split(r'[：:]', i, maxsplit=1) for i in M.list_items(raw)))
                cur['parts'].append(f'<dl>{dl}</dl>')
        elif state == 'after' and kind == 'p':
            fields = f'    <p class="fields">{M.inline(raw)}</p>\n'
        elif state == 'tools' and kind == 'ul':
            in_tools['items'] = [re.split(r'[：:]', i, maxsplit=1) for i in M.list_items(raw)]
    cards_html = ''.join('      <div class="skill">\n        <h3>%s</h3>\n        %s\n      </div>\n' % (M.inline(c['title']), '\n        '.join(c['parts'])) for c in cards)
    if in_tools:
        dl = ''.join(f'<dt>{M.inline(a)}</dt><dd>' + ''.join(f'<span>{M.inline(x.strip())}</span>' for x in b.split('、')) + '</dd>' for a, b in in_tools['items'])
        tools = f'\n    <div class="tools">\n      <h3>{M.inline(in_tools["title"])}</h3>\n      <dl>{dl}</dl>\n    </div>'
    return h2 + intro + f'    <div class="skills">\n{cards_html}    </div>\n' + fields + tools


def link_arrow(text, url):
    return f'<a class="plink" href="{url}">{text} {"↗" if re.match(r"https?://", url) else "→"}</a>'


def r_projects(args, body):
    h2, intro, items, after = '', '', [], ''
    state, cur = 'head', None
    for kind, raw in M.blocks(body):
        if kind == 'h2':
            h2 = f'    <h2>{M.inline(M.heading_text(raw))}</h2>\n'
        elif kind == 'h3':
            t = M.heading_text(raw)
            m = re.match(r'^(.*?)\s*\[([^\]]+)\]\(([^)\s]+)\)\s*$', t)
            title, link = (m.group(1), link_arrow(M.esc(m.group(2)), m.group(3))) if m else (t, '')
            cur = {'title': title, 'link': link, 'tags': ''}
            items.append(cur)
            state = 'items'
        elif kind == 'hr':
            state, cur = 'after', None
        elif state == 'head' and kind == 'p':
            intro = f'    <p class="intro">{M.inline(raw)}</p>\n'
        elif state == 'items' and kind == 'p' and cur is not None:
            cur['tags'] = ''.join(f'<span>{M.inline(x.strip())}</span>' for x in raw.replace('\n', '').split('、') if x.strip())
        elif state == 'after' and kind == 'p':
            after = f'    <p class="after">{M.inline(raw)}</p>\n'
    lis = ''.join(f'      <li><span class="head"><span class="type">{M.inline(i["title"])}</span>{i["link"]}</span><span class="tags">{i["tags"]}</span></li>\n' for i in items)
    return h2 + intro + f'    <ul class="projects">\n{lis}    </ul>\n' + after


def r_process(args, body):
    h2, intro, steps, diag, cur = '', '', [], '', None
    state = 'head'
    for kind, raw in M.blocks(body):
        if kind == 'h2':
            h2 = f'    <h2>{M.inline(M.heading_text(raw))}</h2>\n'
        elif kind == 'h3':
            cur = {'title': M.heading_text(raw), 'text': ''}
            steps.append(cur)
            state = 'steps'
        elif kind == 'hr':
            state = 'after'
        elif state == 'head' and kind == 'p':
            intro = f'    <p class="intro">{M.inline(raw)}</p>\n'
        elif state == 'steps' and kind == 'p' and cur is not None:
            cur['text'] = raw
        elif state == 'after' and kind == 'p':
            diag = f'    <p class="diag">{M.inline(raw)}</p>\n'
    lis = ''.join(f'      <li><h3>{M.inline(s["title"])}</h3><p>{M.inline(s["text"])}</p></li>\n' for s in steps)
    return h2 + intro + f'    <ol class="steps">\n{lis}    </ol>\n' + diag


def r_why(args, body):
    h2, lis = '', ''
    for kind, raw in M.blocks(body):
        if kind == 'h2':
            h2 = f'    <h2>{M.inline(M.heading_text(raw))}</h2>\n'
        elif kind == 'ul':
            for item in M.list_items(raw):
                m = re.match(r'^\*\*(.+?)\*\*[：:]\s*(.*)$', item)
                if not m:
                    raise SystemExit(f'::: why items must look like "- **標題**：說明" (got "{item[:30]}")')
                lis += f'      <li><strong>{M.inline(m.group(1))}</strong><span>{M.inline(m.group(2))}</span></li>\n'
    return h2 + f'    <ul class="why">\n{lis}    </ul>\n'


def r_name(args, body):
    ps = ''.join(f'    <p class="name-note">{M.inline(r)}</p>\n' for k, r in M.blocks(body) if k == 'p')
    return ps


def contact_html(body, email):
    h2, lead, links = 'Contact', '', ''
    for kind, raw in M.blocks(body):
        if kind == 'h2':
            h2 = M.inline(M.heading_text(raw))
        elif kind == 'p' and not lead:
            lead = M.inline(raw)
        elif kind == 'ul':
            for item in M.list_items(raw):
                m = re.match(r'^\[([^\]]+)\]\(([^)\s]+)\)$', item)
                if not m:
                    raise SystemExit(f'::: contact links must look like "- [文字](網址)" (got "{item[:30]}")')
                links += f'      <a href="{m.group(2)}">{M.esc(m.group(1))}</a>\n'
    return (f'<section class="contact" id="contact">\n  <div class="wrap">\n    <h2>{h2}</h2>\n    <p class="lead">{lead}</p>\n'
            f'    <div class="mailbox">\n      <span class="addr" id="addr">{M.esc(email)}</span>\n      <button type="button" id="copy">複製 email</button>\n    </div>\n'
            f'    <div class="links">\n{links}    </div>\n  </div>\n</section>\n')


BLOCKS = {'skills': r_skills, 'projects': r_projects, 'process': r_process, 'why': r_why, 'name': r_name}


def build_about():
    meta, text = M.split_front(open(os.path.join(ROOT, 'content', 'about.md'), encoding='utf-8').read())
    email = meta.get('email', 'mengyahh@gmail.com')
    parts, contact = [], ''
    for typ, args, body in M.directives(text):
        if typ == 'hero':
            parts.append(r_hero(args, body))
        elif typ == 'contact':
            contact = contact_html(body, email)
            parts.append(contact)
        elif typ in BLOCKS:
            sid = typ
            style = 'border-bottom:none; padding-bottom: 8px;' if typ == 'name' else ''
            parts.append(section(sid, args or typ, BLOCKS[typ](args, body), style))
        else:
            raise SystemExit(f'content/about.md: unknown block "::: {typ}" (known: hero, skills, projects, process, why, name, contact)')
    out = page(base='', title=meta.get('title', '關於 | Understory'), desc=meta.get('description', ''), url=f'{SITE}/about.html',
               body='\n'.join(parts), current='about')
    with open(os.path.join(ROOT, 'about.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('wrote about.html')
    return contact


# ------------------------------------------------------------------ portfolio/<slug>.md

def resolve(s):
    return s.replace('@SITE/', 'https://mengyahh.com/')


def portfolio_rows(body, base, gi, name):
    rows, cur = [], None
    for kind, raw in M.blocks(body):
        if kind == 'h2':
            cur = {'label': M.heading_text(raw), 'desc': [], 'media': []}
            rows.append(cur)
        elif cur is None:
            continue
        elif kind == 'img':
            cur['media'].append(raw)
        elif kind in ('p', 'quote') and not cur['media']:
            cur['desc'].append(raw)
    out = []
    for ri, r in enumerate(rows):
        n = len(r['media'])
        has_video = any('(youtube:' in m for m in r['media'])
        cls = 'wide' if has_video else {1: 'c1', 2: 'c2'}.get(n, 'c3')
        gid, items = f'pf-{gi}-{ri}', []
        for i, raw in enumerate(r['media'], 1):
            lm = M.LINKED_IMG.match(raw)
            if lm:
                alt, src, cap, href = lm.groups()
            else:
                alt, src, cap = M.IMG.match(raw).groups()
                href = None
            figcap = f'<figcaption>{M.inline(resolve(cap))}</figcaption>' if cap else ''
            label = M.esc(r['label'])
            if src.startswith('youtube:'):
                yid = src[len('youtube:'):]
                poster = f'portfolio/yt-{yid}.webp'
                w, h = M.image_size(os.path.join(ROOT, 'assets', poster))
                items.append(f'<figure class="pf-item"><button type="button" class="yt" data-yt="{esc(yid)}" aria-label="播放影片：{esc(r["label"])}">'
                             f'<img src="{base}assets/{poster}" width="{w}" height="{h}" alt="" loading="lazy" decoding="async">'
                             f'<span class="yt-play" aria-hidden="true"></span></button>{figcap}</figure>')
                continue
            full = os.path.join(ROOT, 'assets', src)
            if not os.path.isfile(full):
                raise SystemExit(f'{name}: picture "{src}" not found in assets/')
            thumb = re.sub(r'\.(\w+)$', r'-t.\1', src)
            if not os.path.isfile(os.path.join(ROOT, 'assets', thumb)):
                thumb = src
            w, h = M.image_size(os.path.join(ROOT, 'assets', thumb))
            a = alt or f'{r["label"]}：作品 {i}'
            if href:
                items.append(f'<figure class="pf-item"><a class="out" href="{esc(href)}" target="_blank" rel="noopener">'
                             f'<img src="{base}assets/{thumb}" width="{w}" height="{h}" alt="{esc(a)}" loading="lazy" decoding="async"></a>{figcap}</figure>')
            else:
                items.append(f'<figure class="pf-item"><a class="ph" href="{base}assets/{src}" data-group="{gid}" data-title="{esc(r["label"])}" data-alt="{esc(a)}">'
                             f'<img src="{base}assets/{thumb}" width="{w}" height="{h}" alt="{esc(a)}" loading="lazy" decoding="async"></a>{figcap}</figure>')
        desc = ''.join(f'<p>{M.inline(resolve(d))}</p>' for d in r['desc'])
        out.append(f'<article class="pf-row"><div class="pf-info"><h2>{M.esc(r["label"])}</h2>{desc}</div>'
                   f'<div class="pf-grid {cls}">{"".join(items)}</div></article>')
    return ''.join(out), [r['label'] for r in rows], rows


def build_portfolio(contact):
    made = []
    files = [p for p in sorted(glob.glob(os.path.join(ROOT, 'content', 'portfolio', '*.md'))) if not os.path.basename(p).startswith('_')]
    for gi, path in enumerate(files):
        name = os.path.basename(path)
        slug = os.path.splitext(name)[0]
        meta, body = M.split_front(open(path, encoding='utf-8').read())
        title = meta.get('title') or slug
        base = '../../'
        rows_h, labels, rows = portfolio_rows(body, base, gi, name)
        lab = '、'.join(labels)
        desc = meta.get('description') or f'{title}：{lab}。Understory 的作品。'
        first = re.search(r'!\[[^\]]*\]\(([^)\s"]+)', body)
        img = None
        if first:
            src = first.group(1)
            img = f'{SITE}/assets/portfolio/yt-{src[len("youtube:"):]}.webp' if src.startswith('youtube:') else f'{SITE}/assets/{src}'
        inner = (f'<header class="hero">\n  <div class="wrap">\n    <p class="eyebrow"><a href="{base}about.html#projects">作品集</a></p>\n'
                 f'    <h1>{M.inline(title)}</h1>\n    <p class="lede">{M.esc(lab)}</p>\n  </div>\n</header>\n\n'
                 f'<section class="pf">\n  <div class="wrap">\n    {rows_h}\n    <p class="back"><a href="{base}about.html#projects">← 回到做過的專案</a></p>\n  </div>\n</section>\n\n{contact}')
        js = '<script src="../../assets/js/lightbox.js" defer></script>\n<script src="../../assets/js/yt.js" defer></script>\n'
        out = page(base=base, title=f'{title} | Understory', desc=desc, url=f'{SITE}/portfolio/{slug}/', body=inner,
                   body_class='pf-page', og_image=img, extra_js=js)
        dest = os.path.join(ROOT, 'portfolio', slug, 'index.html')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        made.append(slug)
        print('wrote', os.path.relpath(dest, ROOT))
    return made


if __name__ == '__main__':
    contact = build_about()
    build_portfolio(contact)
