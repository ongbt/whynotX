#!/usr/bin/env python3
"""Generate Why Not Christianity slide deck."""

import xml.etree.ElementTree as ET
import re, os, subprocess
from html import escape
from datetime import datetime

XML_PATH = '/mnt/c/Users/bengt/hermes_workspace/why-not-christianity-slides.xml'
OUTPUT_PATH = '/home/bengt/hermes_workspace/why-not-christianity.html'

# Themes: verdict-dark (darker) + dracula for argumentation deck
THEME_NAMES = ['theme-verdict-dark', 'theme-dracula']
THEME_PATHS = [
    '/home/bengt/.hermes/skills/html-ppt/assets/themes/verdict-dark.css',
    '/home/bengt/.hermes/skills/html-ppt/assets/themes/dracula.css',
]

HTML_PPT_DIR = '/home/bengt/.hermes/skills/html-ppt'
BASE_CSS = f'{HTML_PPT_DIR}/assets/base.css'
ANIM_CSS = f'{HTML_PPT_DIR}/assets/animations/animations.css'
FONTS_CSS = f'{HTML_PPT_DIR}/assets/fonts.css'
RUNTIME_JS = f'{HTML_PPT_DIR}/assets/runtime.js'

# ─── Helpers ───

def norm(t):
    t = t.replace('\u2018', "'").replace('\u2019', "'")
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    t = t.replace('\u2013', '--').replace('\u2014', '--')
    return t

def fmt(t):
    t = norm(t)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escape(t))

def read(path):
    return subprocess.run(['cat', path], capture_output=True, text=True).stdout

# ─── Parse XML ───

tree = ET.parse(XML_PATH)
root = tree.getroot()
slides = root.findall('slide')

# Skip cover slide (id=1) and duplicate help slides (id=88,89,90)
skip_ids = {'1', '88', '89', '90'}
data_slides = [s for s in slides if s.get('id') not in skip_ids]

# ─── Cover ───

ts = subprocess.run(
    'TZ=Asia/Singapore date "+%B %d, %Y · %H:%M SGT"',
    capture_output=True, text=True, shell=True
).stdout.strip()

ver = root.findtext('version', 'v1')
VERSION_STR = f'{ver} · {ts}'
COVER_KICKER = 'A Reasoned Examination'
COVER_TITLE = 'Why I Do Not Believe<br>Christianity Is True'
COVER_LEDE = 'An evidence-based look at the claims of Christianity through the lenses of science, history, Jesus, morality, scripture, and philosophy.'

def build_slide(elem):
    stype = elem.get('type', '')
    title_attr = elem.get('title', '')
    ke = elem.find('kicker')
    te = elem.find('title')
    se = elem.find('subtitle')
    be = elem.find('body')
    ne = elem.find('notes')

    kt = ke.text.strip() if ke is not None and ke.text else ''
    rt = te.text.strip() if te is not None and te.text else title_attr
    st = se.text.strip() if se is not None and se.text else ''
    nt = ne.text.strip() if ne is not None and ne.text else ''
    title = ' '.join(rt.split()) if rt else title_attr

    parts = []

    if stype in ('section', 'end'):
        parts.append('<div class="center" style="flex-direction:column;text-align:center;flex:1">')
        if kt: parts.append(f'<p class="kicker mb-m">{fmt(kt)}</p>')
        parts.append(f'<h2 class="h2" data-anim="fade-up" style="margin-bottom:0">{fmt(title)}</h2>')
        if st: parts.append(f'<p class="lede mt-m" style="max-width:50ch;margin-left:auto;margin-right:auto">{fmt(st)}</p>')
        parts.append('</div>')
    else:
        if kt: parts.append(f'<p class="kicker mb-s">{fmt(kt)}</p>')
        if title: parts.append(f'<h2 class="h2" data-anim="fade-up">{fmt(title)}</h2>')
        if st: parts.append(f'<p class="lede mb-m">{fmt(st)}</p>')

    if be is not None and stype not in ('section', 'end'):
        parts.append('<div style="display:flex;flex-direction:column;gap:20px;flex:1;min-height:0">')
        first_sec = True
        for sec in be.findall('section'):
            sci = sec.find('title')
            cards = sec.findall('card')
            sec_type = sec.get('type', 'main')
            if not first_sec:
                parts.append('<div style="height:1px;background:var(--border);margin:6px 0 2px"></div>')
            first_sec = False

            if sci is not None and sci.text:
                sct = sci.text.strip()
                if sec_type == 'intro':
                    parts.append(f'<h4 class="h4" style="margin-bottom:2px;font-size:15px;border-left:3px solid var(--accent,#3b6cff);padding-left:10px">{fmt(sct)}</h4>')
                elif sec_type == 'outro':
                    parts.append(f'<h4 class="h4" style="margin-bottom:2px;font-size:15px;color:var(--text-2);font-style:italic">{fmt(sct)}</h4>')
                else:
                    parts.append(f'<h4 class="h4" style="margin-bottom:2px;font-size:15px">{fmt(sct)}</h4>')

            grid_style = 'display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px'
            if sec_type == 'intro':
                grid_style += ';border-left:3px solid var(--accent,#3b6cff);padding-left:14px'
            elif sec_type == 'outro':
                grid_style += ';background:var(--surface-2);border-radius:var(--radius-sm);padding:14px 18px'
            parts.append(f'<div style="{grid_style}">')

            for card in cards:
                ct = card.find('title')
                cc = card.find('content')
                ct_text = ct.text.strip() if ct is not None and ct.text else ''
                cc_text = cc.text.strip() if cc is not None and cc.text else ''
                verdict = card.get('verdict', '')
                vs = ''
                if verdict == 'good': vs = ' border-left:3px solid var(--good,#2da44e);padding-left:14px'
                elif verdict == 'bad': vs = ' border-left:3px solid var(--bad,#cf222e);padding-left:14px'
                cp = []
                if ct_text: cp.append(f'<h4 class="h4" style="margin-bottom:4px;font-size:14px">{fmt(ct_text)}</h4>')
                paras = [p.strip() for p in cc_text.split('\n\n') if p.strip()]
                for para in paras:
                    lines = [l.strip() for l in para.split('\n') if l.strip()]
                    bullet_lines = [l for l in lines if l.startswith('- ')]
                    if bullet_lines and len(bullet_lines) == len(lines):
                        cp.append('<ul>')
                        for l in lines:
                            cp.append(f'<li>{fmt(l[2:])}</li>')
                        cp.append('</ul>')
                    else:
                        for line in lines:
                            if line.startswith('- '):
                                cp.append(f'<li>{fmt(line[2:])}</li>')
                            elif not any(c.isalpha() for c in line) and len(line) < 8:
                                cp.append(f'<div style="font-size:28px;margin-bottom:2px;line-height:1">{escape(line)}</div>')
                            else:
                                cp.append(f'<p class="dim" style="margin:0 0 4px;font-size:13px;line-height:1.55">{fmt(line)}</p>')
                parts.append(f'<div class="card" data-anim="fade-up" style="padding:14px 18px{vs}">{"".join(cp)}</div>')
            parts.append('</div>')
        parts.append('</div>')

    return '\n'.join(parts), fmt(nt) if nt else ''

# ─── Patches JS ───

PATCHES_JS = """/* Remove broken theme-link */
document.querySelector('#theme-link')?.remove();
/* Touch swipe + tap (debounced) */
(function(){var _tn=0;var _mdX=-1,_mdY=-1;var xS=0,yS=0,sl=Array.from((document.querySelector('.deck')||document.body).querySelectorAll('.slide'));
document.addEventListener('touchstart',function(e){if(e.touches.length!==1)return;xS=e.touches[0].clientX;yS=e.touches[0].clientY;_tn=0;},{passive:true});
document.addEventListener('touchend',function(e){if(e.changedTouches.length!==1)return;var x=e.changedTouches[0].clientX,y=e.changedTouches[0].clientY,dx=x-xS,dy=y-yS,adx=Math.abs(dx),ady=Math.abs(dy);if(adx>40&&adx>ady*1.5){_tn=1;go(dx<0?1:-1);return;}},{passive:true});
document.addEventListener('mousedown',function(e){_mdX=e.clientX;_mdY=e.clientY;},true);
document.addEventListener('click',function(e){var t=e.target;if(_tn){_tn=0;return;}if(t.closest('button')||t.closest('a')||t.closest('.overview')||t.closest('.notes')||t.closest('.slide-number')||t.closest('.bar'))return;if(_mdX>=0&&(Math.abs(e.clientX-_mdX)>8||Math.abs(e.clientY-_mdY)>8)){_mdX=-1;return;}_mdX=-1;var r=document.querySelector('.deck')||document.body,rect=r.getBoundingClientRect(),x=e.clientX-rect.left;if(x>0)go(x>rect.width*0.5?1:-1);});})();
/* Theme toggle (inlined CSS) */
(function(){var h=document.documentElement,n=(h.getAttribute('data-themes')||'').split(',').map(function(s){return s.trim();}).filter(Boolean);if(n.length<2)return;var ti=0;window._ct=function(){ti=(ti+1)%n.length;h.className=n[ti]+' is-active';h.setAttribute('data-theme',n[ti].replace('theme-',''));try{(new BroadcastChannel('html-ppt-presenter-'+location.pathname)).postMessage({type:'theme',name:n[ti]});}catch(e){}};
document.addEventListener('keydown',function(e){if((e.key==='t'||e.key==='T')&&!e.metaKey&&!e.ctrlKey&&!e.altKey){if(window._ct){e.preventDefault();window._ct();}}});})();
/* Expose go() globally (400ms debounce) */
(function(){var dk=document.querySelector('.deck');if(!dk)return;var sl=Array.from(dk.querySelectorAll('.slide'));if(!sl.length)return;var _gd=0;window.go=function(n){var nw=Date.now();if(nw-_gd<400)return;_gd=nw;var cur=sl.indexOf(document.querySelector('.slide.is-active'));n=cur+n;n=Math.max(0,Math.min(sl.length-1,n));
sl.forEach(function(s,i){s.classList.toggle('is-active',i===n);s.classList.toggle('is-prev',i<n);});
var ne=document.querySelector('.slide-number');if(ne)ne.setAttribute('data-current',n+1);
var bf=document.querySelector('.progress-bar span');if(bf)bf.style.width=((n+1)/sl.length*100)+'%';
history.replaceState(null,'','#/'+(n+1));
sl[n].querySelectorAll('[data-anim]').forEach(function(el){var a=el.getAttribute('data-anim');el.classList.remove('anim-'+a);void el.offsetWidth;el.classList.add('anim-'+a);});
var no=sl[n].querySelector('.notes, aside.notes, .speaker-notes');var ne2=document.querySelector('.notes-overlay');if(ne2)ne2.innerHTML=no?no.innerHTML:'';
try{(new BroadcastChannel('html-ppt-presenter-'+location.pathname)).postMessage({type:'go',idx:n});}catch(e){}};})();"""

# ─── Cover notes ───

cover_notes = ''
for s in slides:
    if s.get('id') == '1':
        ne = s.find('notes')
        if ne is not None and ne.text:
            cover_notes = fmt(ne.text.strip())

cover = f'''    <!-- COVER -->
    <section class="slide is-active" data-title="Cover">
      <div class="version-badge" style="position:absolute;top:20px;right:20px;font-size:14px;color:var(--text-3);font-family:monospace;">{escape(VERSION_STR)}</div>
      <p class="kicker">{escape(COVER_KICKER)}</p>
      <h1 class="h1" style="margin-bottom:0.25em">{COVER_TITLE}</h1>
      <p class="lede" style="max-width:56ch">{escape(COVER_LEDE)}</p>
      <div class="notes">{cover_notes}</div>
    </section>'''

help_slide = '''    <!-- HELP -->
    <section class="slide" data-title="How to Navigate">
      <p class="kicker mb-s">Getting Started</p>
      <h2 class="h2" data-anim="fade-up">How to Navigate</h2>
      <p class="lede mb-m">Use any of these methods to move through the deck.</p>
      <div style="display:flex;flex-direction:column;gap:10px;max-width:500px">
        <div class="card" style="padding:12px 18px"><strong>&larr; &rarr;</strong> or <strong>Space</strong> &mdash; Previous / Next</div>
        <div class="card" style="padding:12px 18px">Tap <strong>left half</strong> or <strong>right half</strong> &mdash; Previous / Next</div>
        <div class="card" style="padding:12px 18px">Swipe <strong>left</strong> or <strong>right</strong> &mdash; Prev / Next</div>
        <div class="card" style="padding:12px 18px"><strong>T</strong> &mdash; Cycle themes</div>
        <div class="card" style="padding:12px 18px"><strong>F</strong> &mdash; Fullscreen</div>
        <div class="card" style="padding:12px 18px"><strong>O</strong> &mdash; Overview grid</div>
        <div class="card" style="padding:12px 18px"><strong>S</strong> &mdash; Presenter mode</div>
        <div class="card" style="padding:12px 18px"><strong>N</strong> &mdash; Notes drawer</div>
        <div class="card" style="padding:12px 18px"><strong>&#x2302;</strong> (footer) &mdash; Back to first slide</div>
      </div>
    </section>'''

data_html = []
for elem in data_slides:
    title_attr = elem.get('title', 'Slide')
    body, notes = build_slide(elem)
    lines = [f'    <section class="slide" data-title="{escape(title_attr)}">']
    for line in body.split('\n'):
        lines.append(f'      {line}')
    if notes:
        lines.append(f'      <div class="notes">{notes}</div>')
    lines.append('    </section>')
    data_html.append('\n'.join(lines))

all_slides = '\n'.join([cover] + data_html + [help_slide])
total = len(data_slides) + 2

# ─── Assets ───

base_css = read(BASE_CSS)
anim_css = read(ANIM_CSS)
fonts_css = read(FONTS_CSS)
runtime_js = read(RUNTIME_JS)

themes_css = []
for name, path in zip(THEME_NAMES, THEME_PATHS):
    css = read(path).replace(':root', f'.{name}:root, .{name}')
    themes_css.append(css)

responsive = '''
.slide { overflow-y: auto !important; padding-bottom: 110px !important; }
.slide::-webkit-scrollbar { width: 6px; }
.slide::-webkit-scrollbar-track { background: transparent; }
.slide::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
.card li, .card ul { font-size: 13px; line-height: 1.55; color: var(--text-2); }
.card ul { margin: 2px 0 4px; padding-left: 18px; }
@media (max-width: 1024px) {
  .slide { padding: 40px 36px 90px !important; }
  .deck-header { top: 12px; left: 18px; right: 18px; }
  .deck-footer { bottom: 12px; left: 18px; right: 18px; }
  h1.title,.h1 { font-size: clamp(28px, 5vw, 40px); }
  h2.title,.h2 { font-size: clamp(22px, 4vw, 30px); }
  .lede { font-size: clamp(13px, 2vw, 16px); }
  .card { padding: 14px 14px 12px !important; }
  .slide div[style*="repeat(auto-fit,minmax(300px,1fr))"] { grid-template-columns: repeat(auto-fit,minmax(240px,1fr)) !important; }
  .mb-l { margin-bottom: 14px !important; }
  .kicker { font-size: 11px; }
  .h4 { font-size: 14px; }
  .dim,.card p,.card li,.card ul { font-size: clamp(11px, 1.6vw, 13px); line-height: 1.5; }
  .card ul { margin: 2px 0 4px; padding-left: 18px; }
}
@media (max-width: 640px) {
  .slide { padding: 28px 18px !important; }
  h1.title,.h1 { font-size: clamp(22px, 7vw, 28px); }
  h2.title,.h2 { font-size: clamp(18px, 5vw, 22px); }
  .card { padding: 10px 12px 10px !important; }
  .card p,.card li,.card ul { font-size: 12px; line-height: 1.4; }
  .kicker { font-size: 10px; letter-spacing: 0.08em; }
  .slide div[style*="repeat(auto-fit,minmax(300px,1fr))"] { grid-template-columns: 1fr !important; }
}
.deck-footer button { background:none; border:none; color:var(--text-3); cursor:pointer; font-size:18px; padding:0 8px 0 0; line-height:1; }
.deck-footer button:hover { color:var(--accent); }
'''

data_themes = ','.join(THEME_NAMES)
first_theme = THEME_NAMES[0]

doc = f'''<!DOCTYPE html>
<html lang="en" class="{first_theme} is-active" data-themes="{data_themes}" data-theme="{first_theme.replace('theme-', '')}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape('Why I Do Not Believe Christianity Is True')}</title>
  <style>
{base_css}
{anim_css}
{fonts_css}
{chr(10).join(themes_css)}
{responsive}
</style>
</head>
<body>
  <div class="deck">

{all_slides}

    <div class="deck-footer">
      <button onclick="go(0)" title="Back to first slide" aria-label="Back to first slide">&#x2302;</button>
      <span class="slide-number" data-current="1" data-total="{total}"></span>
    </div>
  </div>
  <script>
{runtime_js}
  </script>
  <script>
{PATCHES_JS}
  </script>
</body>
</html>'''

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(doc)

size = os.path.getsize(OUTPUT_PATH)
print(f"Written: {OUTPUT_PATH}")
print(f"Size: {size:,} bytes | Slides: {total}")
