#!/usr/bin/env python3
"""Build the pages of understory.mengyahh.com that are written in Markdown.

    python scripts/build.py

content/about.md                  ->  about.html
content/portfolio/<slug>.md       ->  portfolio/<slug>/index.html      (files starting with "_" are drafts and are skipped)
content/products/<slug>.md        ->  products/<slug>/index.html
content/appsheet.md               ->  products/index.html   (AppSheet introduction + a card for every product)

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

LANGS = ['zh', 'en', 'ja']
HTML_LANG = {'zh': 'zh-Hant-TW', 'en': 'en', 'ja': 'ja'}
LANG_NAME = {'zh': '中文', 'en': 'EN', 'ja': '日本語'}

# Texts that belong to the site frame (navigation, buttons, back links). Page content lives in the Markdown files.
STRINGS = {
    'zh': {'menu': '選單', 'appsheet_menu': '展開 AppSheet 選單', 'freelance': '自由工作者套件', 'poultry': '白肉雞養殖紀錄系統',
           'custom': '客製化系統開發', 'case': '個案管理系統', 'events': '活動企劃', 'topics': '議題推廣', 'about': '關於',
           'contact': '聯絡', 'soon': '準備中', 'back_products': '← 回到 AppSheet 管理系統', 'back_home': '← 回到首頁',
           'copy': '複製 email', 'copied': '已複製', 'selected': '已選取，請按複製', 'lang_label': '語言'},
    'en': {'menu': 'Menu', 'appsheet_menu': 'Open the AppSheet menu', 'freelance': 'Freelancer Toolkit', 'poultry': 'Broiler Farm Records',
           'custom': 'Custom Systems', 'case': 'Case Management', 'events': 'Event Planning', 'topics': 'Issue Outreach', 'about': 'About',
           'contact': 'Contact', 'soon': 'Soon', 'back_products': '← Back to AppSheet systems', 'back_home': '← Back to home',
           'copy': 'Copy email', 'copied': 'Copied', 'selected': 'Selected, press copy', 'lang_label': 'Language'},
    'ja': {'menu': 'メニュー', 'appsheet_menu': 'AppSheet メニューを開く', 'freelance': 'フリーランス向けツール', 'poultry': 'ブロイラー飼育記録システム',
           'custom': 'カスタムシステム開発', 'case': 'ケース管理システム', 'events': 'イベント企画', 'topics': '課題発信', 'about': 'About',
           'contact': 'お問い合わせ', 'soon': '準備中', 'back_products': '← AppSheet システム一覧へ', 'back_home': '← ホームへ',
           'copy': 'メールをコピー', 'copied': 'コピーしました', 'selected': '選択しました。コピーしてください', 'lang_label': '言語'},
}

# current language (set by set_lang): 'zh' pages live at the site root, the others under /en/ and /ja/
LANG, L, S, CONTENT, LANG_DIR = 'zh', '/', STRINGS['zh'], None, ''


def set_lang(lang):
    global LANG, L, S, CONTENT, LANG_DIR
    LANG, S = lang, STRINGS[lang]
    L = '/' if lang == 'zh' else f'/{lang}/'
    LANG_DIR = '' if lang == 'zh' else lang
    CONTENT = os.path.join(ROOT, 'content') if lang == 'zh' else os.path.join(ROOT, 'content', lang)


def content_path(*parts, lang=None):
    base = os.path.join(ROOT, 'content') if (lang or LANG) == 'zh' else os.path.join(ROOT, 'content', lang or LANG)
    return os.path.join(base, *parts)


def out_path(*parts):
    return os.path.join(ROOT, LANG_DIR, *parts)


def fonts(lang):
    extra = '&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@500;600;700' if lang == 'ja' else ''
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700'
            f'&family=Karla:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500{extra}&display=swap">')


def page_exists(lang, key):
    """Does this page have a version in that language? key: home | about | products | product:<slug> | portfolio"""
    if key == 'home':
        return os.path.isfile(content_path('index.md', lang=lang))
    if key == 'about':
        return os.path.isfile(content_path('about.md', lang=lang))
    if key == 'products':
        return os.path.isfile(content_path('appsheet.md', lang=lang))
    if key.startswith('product:'):
        return os.path.isfile(content_path('products', key.split(':', 1)[1] + '.md', lang=lang))
    return lang == 'zh'


def page_url(lang, key):
    r = '/' if lang == 'zh' else f'/{lang}/'
    if key == 'home':
        return r
    if key == 'about':
        return r + 'about.html'
    if key == 'products':
        return r + 'products/'
    if key.startswith('product:'):
        return r + 'products/' + key.split(':', 1)[1] + '/'
    return r


def alternates(key):
    """{lang: url} for the language switcher: the same page where it exists, otherwise that language's home page."""
    return {l: (page_url(l, key) if page_exists(l, key) else page_url(l, 'home')) for l in LANGS}, \
           {l: page_url(l, key) for l in LANGS if page_exists(l, key)}


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
    function done(msg) { btn.textContent = msg; setTimeout(function () { btn.textContent = '@@COPY@@'; }, 1800); }
    function fallback() {
      var r = document.createRange(); r.selectNodeContents(document.getElementById('addr'));
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); done('@@SELECTED@@');
    }
    try {
      navigator.clipboard.writeText(text).then(function () { done('@@COPIED@@'); }, fallback);
    } catch (e) { fallback(); }
  });
</script>'''


def nav_html(current, alts):
    about = f'<a href="{L}about.html"' + (' aria-current="page"' if current == 'about' else '') + f'>{S["about"]}</a>'
    contact = '#contact' if current in ('about', 'home') else f'{L}about.html#contact'
    switch = ' · '.join(
        (f'<a href="{alts[l]}" hreflang="{HTML_LANG[l]}" lang="{HTML_LANG[l]}"' + (' aria-current="true"' if l == LANG else '') + f'>{LANG_NAME[l]}</a>') for l in LANGS)
    return f'''<nav class="topbar">
  <div class="wrap">
    <p class="wordmark"><a href="{L}">under<span>story</span></a></p>
    <button type="button" class="menu-btn" aria-expanded="false" aria-controls="menu">{S["menu"]}</button>
    <ul class="topnav" id="menu">
      <li class="has-sub">
        <a href="{L}products/">AppSheet</a><button type="button" class="sub-btn" aria-label="{S["appsheet_menu"]}" aria-expanded="false" aria-haspopup="true" aria-controls="sub-appsheet"><span class="caret" aria-hidden="true">▾</span></button>
        <ul class="sub" id="sub-appsheet">
          <li><a href="{L}products/freelance/">{S["freelance"]}</a></li>
          <li><a href="{L}products/poultry/">{S["poultry"]}</a></li>
          <li><a href="{L}products/custom/">{S["custom"]}</a></li>
          <li><span class="soon">{S["case"]}<em>{S["soon"]}</em></span></li>
        </ul>
      </li>
      <li><span class="soon">{S["events"]}<em>{S["soon"]}</em></span></li>
      <li><span class="soon">{S["topics"]}<em>{S["soon"]}</em></span></li>
      <li>{about}</li>
      <li><a href="{contact}">{S["contact"]}</a></li>
      <li class="langs" aria-label="{S["lang_label"]}">{switch}</li>
    </ul>
  </div>
</nav>'''


def local_links(body):
    """Links written in the Markdown files are relative to the language folder: /en/ for English, / for Chinese."""
    def fix(m):
        u = m.group(2)
        if re.match(r'(https?:|mailto:|#|/|tel:)', u):
            return m.group(0)
        return f'{m.group(1)}{L}{u}"'
    return re.sub(r'(href=")([^"]+)"', fix, body)


def page(*, title, desc, path_key, body, current=None, body_class='', og_image=None, extra_js='', css='site', url_path=None):
    """One complete HTML page. path_key says which page this is (for the language switcher and hreflang)."""
    alts, existing = alternates(path_key)
    url = SITE + (url_path if url_path else page_url(LANG, path_key))
    og = f'<meta property="og:image" content="{esc(og_image)}">\n' if og_image else ''
    cls = f' class="{body_class}"' if body_class else ''
    hreflang = ''.join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{SITE}{u}">\n' for l, u in existing.items())
    if 'zh' in existing:
        hreflang += f'<link rel="alternate" hreflang="x-default" href="{SITE}{existing["zh"]}">\n'
    hreflang = hreflang if len(existing) > 1 else ''
    copy_js = COPY_JS.replace('@@COPY@@', S['copy']).replace('@@COPIED@@', S['copied']).replace('@@SELECTED@@', S['selected']) if 'id="copy"' in body else ''
    return f'''<!doctype html>
<html lang="{HTML_LANG[LANG]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{hreflang}<meta property="og:type" content="website">
<meta property="og:site_name" content="Understory">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
{og}<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/{css}.css">
{fonts(LANG)}
</head>
<body{cls}>
{nav_html(current, alts)}

{local_links(body)}

<footer>
  <div class="wrap"><p>Understory · works by mengyahh</p></div>
</footer>

{NAV_JS}

{copy_js}
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
        dl = ''.join(f'<dt>{M.inline(a)}</dt><dd>' + ''.join(f'<span>{M.inline(x.strip())}</span>' for x in re.split(r'[、,，]\s*', b)) + '</dd>' for a, b in in_tools['items'])
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
            cur['tags'] = ''.join(f'<span>{M.inline(x.strip())}</span>' for x in re.split(r'[、,，]\s*', raw.replace('\n', '')) if x.strip())
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


# ------------------------------------------------------------------ products/<slug>.md

def r_features(args, body):
    items = []
    for kind, raw in M.blocks(body):
        if kind == 'h3':
            items.append({'title': M.heading_text(raw), 'text': ''})
        elif kind == 'p' and items:
            items[-1]['text'] = raw
    cells = ''.join(f'      <div class="feature">\n        <h3>{M.inline(i["title"])}</h3>\n        <p>{M.inline(i["text"])}</p>\n      </div>\n' for i in items)
    return f'    <div class="feature-grid">\n{cells}    </div>\n'


def screenshot_src(src):
    if LANG != 'zh':
        cand = f'screenshots/{LANG}/{os.path.basename(src)}'
        if os.path.isfile(os.path.join(ROOT, cand)):
            return '/' + cand
    return '/' + src


def r_screens(args, body):
    shots, note, after = [], '', False
    for kind, raw in M.blocks(body):
        if kind == 'img':
            m = M.IMG.match(raw)
            alt, src, cap = m.groups()
            shots.append(f'        <div class="screen-shot">\n          <img src="{screenshot_src(src)}" alt="{M.esc(alt)}">\n          <p>{M.inline(cap or "")}</p>\n        </div>\n')
        elif kind == 'hr':
            after = True
        elif kind == 'p' and after:
            note = f'      <p class="chart-caption">{M.inline(raw)}</p>\n'
    return (f'    <div class="screens-block">\n      <p class="chart-title">{M.inline(args)}</p>\n      <div class="screens-grid">\n{"".join(shots)}'
            f'      </div>\n{note}    </div>\n')


def r_note(args, body):
    return f'    <p class="reference-note">{M.inline(body.strip())}</p>\n'


def r_callout(args, body):
    paras, links = [], []
    for kind, raw in M.blocks(body):
        if kind == 'p':
            paras.append(M.inline(raw))
        elif kind == 'ul':
            for item in M.list_items(raw):
                m = re.match(r'^\[([^\]]+)\]\(([^)\s]+)\)$', item)
                if not m:
                    raise SystemExit(f'::: callout buttons must look like "- [文字](網址)" (got "{item[:30]}")')
                links.append((m.group(1), m.group(2)))
    cls = 'callout open' if args.strip() == 'open' else 'callout'
    btns = ''.join(f'<a class="cta-btn{"" if i == 0 else " secondary"}" href="{u}"{"" if u.startswith("mailto:") else " target=\"_blank\" rel=\"noopener\""}>{M.esc(t)}</a>\n        '
                   for i, (t, u) in enumerate(links))
    cta = f'\n      <div class="cta-row">\n        {btns.rstrip()}\n      </div>' if links else ''
    return f'    <div class="{cls}">\n      {"<br><br>".join(paras)}{cta}\n    </div>\n'


def build_products(contact):
    made = []
    folder = content_path('products')
    if not os.path.isdir(folder):
        return made
    for path in sorted(glob.glob(os.path.join(folder, '*.md'))):
        name = os.path.basename(path)
        if name.startswith('_'):
            continue
        slug = os.path.splitext(name)[0]
        meta, body = M.split_front(open(path, encoding='utf-8').read())
        title = meta.get('title') or slug
        first = body.find(':::')
        intro_text, rest = (body, '') if first < 0 else (body[:first], body[first:])
        intro = ''.join(f'<p>{M.inline(r)}</p>' for k, r in M.blocks(intro_text) if k == 'p')
        parts = []
        for typ, args, dbody in M.directives(rest):
            if typ == 'features':
                parts.append(r_features(args, dbody))
            elif typ == 'screens':
                parts.append(r_screens(args, dbody))
            elif typ == 'note':
                parts.append(r_note(args, dbody))
            elif typ == 'callout':
                parts.append(r_callout(args, dbody))
            else:
                raise SystemExit(f'{name}: unknown block "::: {typ}" (known: features, screens, note, callout)')
        inner = (f'<section class="product">\n  <div class="wrap">\n    <p class="eyebrow">{M.esc(meta.get("eyebrow", ""))}</p>\n'
                 f'    <h1>{M.inline(title)}</h1>\n    <div class="prose">{intro}</div>\n{"".join(parts)}'
                 f'    <p class="back"><a href="{L}products/">{S["back_products"]}</a></p>\n  </div>\n</section>\n\n{contact}')
        out = page(title=f'{title} | Understory', desc=meta.get('description') or title, path_key=f'product:{slug}', body=inner)
        dest = out_path('products', slug, 'index.html')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        made.append(slug)
        print('wrote', os.path.relpath(dest, ROOT))
    return made


def build_products_index(contact):
    """products/index.html : the AppSheet introduction (content/appsheet.md) plus a card for every product page."""
    if not os.path.isfile(content_path('appsheet.md')):
        return
    meta, body = M.split_front(open(content_path('appsheet.md'), encoding='utf-8').read())
    first = body.find(':::')
    intro_text, rest = (body, '') if first < 0 else (body[:first], body[first:])
    intro = ''.join(f'<p>{M.inline(r)}</p>' for k, r in M.blocks(intro_text) if k == 'p')
    parts = []
    for typ, args, dbody in M.directives(rest):
        if typ == 'points':
            lis = ''.join(f'      <li>{M.inline(i)}</li>\n' for i in M.list_items(dbody.strip()))
            parts.append(f'    <h3 class="points-title">{M.inline(args)}</h3>\n    <ul class="points">\n{lis}    </ul>\n')
        elif typ == 'cards':
            lead = ''.join(f'<p class="lede">{M.inline(r)}</p>' for k, r in M.blocks(dbody) if k == 'p')
            cards = []
            for path in sorted(glob.glob(os.path.join(content_path('products'), '*.md'))):
                name = os.path.basename(path)
                if name.startswith('_'):
                    continue
                pm, _ = M.split_front(open(path, encoding='utf-8').read())
                cards.append((int(pm.get('order', '99')), os.path.splitext(name)[0], pm))
            cells = ''
            for _, slug, pm in sorted(cards, key=lambda c: c[0]):
                chip = f'<span class="status-chip{" open" if pm.get("status_style") == "open" else ""}">{M.esc(pm.get("status", ""))}</span>' if pm.get('status') else ''
                cells += (f'      <a class="teaser" href="{L}products/{slug}/">\n        <p class="tname">{M.inline(pm.get("title", slug))}</p>\n'
                          f'        <p>{M.inline(pm.get("summary", ""))}</p>\n        {chip}\n      </a>\n')
            parts.append(f'    {lead}\n    <div class="teaser-row">\n{cells}    </div>\n')
        else:
            raise SystemExit(f'content/appsheet.md: unknown block "::: {typ}" (known: points, cards)')
    inner = (f'<section class="product">\n  <div class="wrap">\n    <p class="eyebrow">{M.esc(meta.get("eyebrow", "Products"))}</p>\n'
             f'    <h1>{M.inline(meta.get("title", "AppSheet"))}</h1>\n    <div class="prose">{intro}</div>\n{"".join(parts)}'
             f'    <p class="back"><a href="{L}#appsheet">{S["back_home"]}</a></p>\n  </div>\n</section>\n\n{contact}')
    out = page(title=f'{meta.get("title", "AppSheet")} | Understory', desc=meta.get('description', ''), path_key='products', body=inner)
    dest = out_path('products', 'index.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('wrote', os.path.relpath(dest, ROOT))


BLOCKS = {'skills': r_skills, 'projects': r_projects, 'process': r_process, 'why': r_why, 'name': r_name}


def build_about():
    src = content_path('about.md')
    if not os.path.isfile(src):
        return ''
    meta, text = M.split_front(open(src, encoding='utf-8').read())
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
            raise SystemExit(f'{os.path.relpath(src, ROOT)}: unknown block "::: {typ}" (known: hero, skills, projects, process, why, name, contact)')
    out = page(title=meta.get('title', 'About | Understory'), desc=meta.get('description', ''), path_key='about',
               body='\n'.join(parts), current='about')
    dest = out_path('about.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('wrote', os.path.relpath(dest, ROOT))
    return contact


# ------------------------------------------------------------------ index.md (the home page)

def build_home(contact_unused=None):
    src = content_path('index.md')
    if not os.path.isfile(src):
        return
    meta, text = M.split_front(open(src, encoding='utf-8').read())
    parts = []
    for typ, args, body in M.directives(text):
        bl = M.blocks(body)
        if typ == 'hero':
            lines = body.strip().split('\n')
            eyebrow = lines[0].strip()
            bl = M.blocks('\n'.join(lines[1:]))
            h1 = next(r for k, r in bl if k == 'h1')
            lede = ' '.join(M.inline(r) for k, r in bl if k == 'p' and not r.startswith('=>'))
            offer = ''.join(f'      <li><strong>{M.inline(m.group(1))}</strong><span>{M.inline(m.group(2))}</span></li>\n'
                            for k, r in bl if k == 'ul' for i in M.list_items(r) for m in [re.match(r'^\*\*(.+?)\*\*[：:]\s*(.*)$', i)] if m)
            btns = [re.match(r'=>\s*\[([^\]]+)\]\(([^)\s]+)\)', l) for k, r in bl if k == 'p' and r.startswith('=>') for l in r.split('\n')]
            cta = ''.join(f'      <a class="btn{"" if i == 0 else " ghost"}" href="{m.group(2)}">{M.esc(m.group(1))}</a>\n' for i, m in enumerate(b for b in btns if b))
            parts.append(f'<header class="hero">\n  <div class="wrap">\n    <p class="eyebrow">{M.esc(eyebrow)}</p>\n    <h1>{M.inline(M.heading_text(h1))}</h1>\n'
                         f'    <p class="lede">\n      {lede}\n    </p>\n    <ul class="offer">\n{offer}    </ul>\n    <p class="cta">\n{cta}    </p>\n  </div>\n</header>\n')
        elif typ == 'products':
            h2 = next(r for k, r in bl if k == 'h2')
            lede = ' '.join(M.inline(r) for k, r in bl if k == 'p' and not r.startswith('=>'))
            more = next((r for k, r in bl if k == 'p' and r.startswith('=>')), None)
            mm = re.match(r'=>\s*\[([^\]]+)\]\(([^)\s]+)\)', more) if more else None
            cards = []
            for path in sorted(glob.glob(os.path.join(content_path('products'), '*.md'))):
                name = os.path.basename(path)
                if name.startswith('_'):
                    continue
                pm, _ = M.split_front(open(path, encoding='utf-8').read())
                cards.append((int(pm.get('order', '99')), os.path.splitext(name)[0], pm))
            cells = ''
            for _, slug, pm in sorted(cards, key=lambda c: c[0]):
                chip = f'<span class="status-chip{" open" if pm.get("status_style") == "open" else ""}">{M.esc(pm.get("status", ""))}</span>' if pm.get('status') else ''
                cells += (f'      <a class="teaser" href="{L}products/{slug}/">\n        <p class="tname">{M.inline(pm.get("title", slug))}</p>\n'
                          f'        <p>{M.inline(pm.get("summary", ""))}</p>\n        {chip}\n      </a>\n')
            more_html = f'    <p class="more"><a href="{mm.group(2)}">{M.esc(mm.group(1))}</a></p>\n' if mm else ''
            parts.append(f'<section class="prod-intro" id="appsheet">\n  <div class="wrap">\n    <p class="eyebrow">{M.esc(args or "Products")}</p>\n'
                         f'    <h2>{M.inline(M.heading_text(h2))}</h2>\n    <p class="lede">\n      {lede}\n    </p>\n    <div class="teaser-row">\n{cells}    </div>\n{more_html}  </div>\n</section>\n')
        elif typ == 'about':
            h2 = next(r for k, r in bl if k == 'h2')
            ps = ''
            for k, r in bl:
                if k != 'p':
                    continue
                mm = re.match(r'=>\s*\[([^\]]+)\]\(([^)\s]+)\)', r)
                ps += (f'      <p><a href="{mm.group(2)}">{M.esc(mm.group(1))}</a></p>\n' if mm else f'      <p>\n        {M.inline(r)}\n      </p>\n')
            parts.append(f'<section class="about" id="about">\n  <div class="wrap">\n    <h2>{M.inline(M.heading_text(h2))}</h2>\n    <div class="prose">\n{ps}    </div>\n  </div>\n</section>\n')
        elif typ == 'contact':
            h2 = next(r for k, r in bl if k == 'h2')
            p1 = next((r for k, r in bl if k == 'p'), '')
            links = ''.join(f'      <a href="{m.group(2)}">{M.esc(m.group(1))}</a>\n' for k, r in bl if k == 'ul' for i in M.list_items(r) for m in [re.match(r'^\[([^\]]+)\]\(([^)\s]+)\)$', i)] if m)
            parts.append(f'<section class="contact" id="contact">\n  <div class="wrap">\n    <h2>{M.inline(M.heading_text(h2))}</h2>\n    <div class="prose">\n      <p>{M.inline(p1)}</p>\n    </div>\n'
                         f'    <div class="contact-links">\n{links}    </div>\n  </div>\n</section>\n')
        else:
            raise SystemExit(f'{os.path.relpath(src, ROOT)}: unknown block "::: {typ}" (known: hero, products, about, contact)')
    out = page(title=meta.get('title', 'Understory · works by mengyahh'), desc=meta.get('description', ''), path_key='home',
               body='\n'.join(parts), current='home', css='home')
    dest = out_path('index.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('wrote', os.path.relpath(dest, ROOT))


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
        base = '/'
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
        js = '<script src="/assets/js/lightbox.js" defer></script>\n<script src="/assets/js/yt.js" defer></script>\n'
        out = page(title=f'{title} | Understory', desc=desc, path_key='portfolio', url_path=f'/portfolio/{slug}/', body=inner,
                   body_class='pf-page', og_image=img, extra_js=js)
        dest = os.path.join(ROOT, 'portfolio', slug, 'index.html')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        made.append(slug)
        print('wrote', os.path.relpath(dest, ROOT))
    return made


if __name__ == '__main__':
    for lang in LANGS:
        set_lang(lang)
        if lang != 'zh' and not os.path.isdir(CONTENT):
            continue
        print(f'--- {lang}')
        contact = build_about()
        build_home()
        if lang == 'zh':
            build_portfolio(contact)
        build_products(contact)
        build_products_index(contact)
