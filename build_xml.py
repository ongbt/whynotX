#!/usr/bin/env python3
"""Extract structured slide XML from HTML presentation deck."""
import re, sys

with open("/home/bengt/hermes_workspace/why-not-christianity/why-not-christianity-slides-old.html") as f:
    RAW = f.read()

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def ents(s):
    for a, b in [('&mdash;','\u2014'),('&ndash;','\u2013'),('&ldquo;','\u201c'),
                 ('&rdquo;','\u201d'),('&lsquo;','\u2018'),('&rsquo;','\u2019'),
                 ('&hellip;','\u2026'),('&amp;','&'),('&nbsp;',' '),('&lt;','<'),
                 ('&gt;','>'),('&bull;','\u2022'),('&quot;','"'),('&#39;','\''),('&#x27;','\'')]:
        s = s.replace(a, b)
    return s

def strip_attrs(s):
    return re.sub(r'\s(style|data-anim|data-anim-target|data-deploy)="[^"]*"', '', s)

# HTML -> CommonMark
def inline_md(html):
    html = ents(html); html = strip_attrs(html)
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'</?b>', '**', html); html = re.sub(r'</?strong>', '**', html)
    html = re.sub(r'</?i>', '*', html); html = re.sub(r'</?em>', '*', html)
    html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL)
    html = re.sub(r'</?(?:span|code|sup|sub|u|s|q|th|td|tr|table)[^>]*>', '', html)
    html = re.sub(r'<img[^>]*>', '', html); html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'[ \t]+', ' ', html); html = re.sub(r'\n[ \t]+', '\n', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()

def block_md(html):
    html = ents(html); html = strip_attrs(html)
    html = re.sub(r'<br\s*/?>', '\n', html)
    for tag in ('p','h4','h3','h2','div'):
        html = re.sub(f'<{tag}[^>]*>(.*?)</{tag}>', r'\1\n\n', html, flags=re.DOTALL)
    html = re.sub(r'<ol>(.*?)</ol>', lambda m: _li(m.group(1),True), html, flags=re.DOTALL)
    html = re.sub(r'<ul>(.*?)</ul>', lambda m: _li(m.group(1),False), html, flags=re.DOTALL)
    html = re.sub(r'</?b>', '**', html); html = re.sub(r'</?strong>', '**', html)
    html = re.sub(r'</?i>', '*', html); html = re.sub(r'</?em>', '*', html)
    html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL)
    html = re.sub(r'</?(?:span|code|sup|sub|u|s|q|th|td|tr|table)[^>]*>', '', html)
    html = re.sub(r'<img[^>]*>', '', html); html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'[ \t]+', ' ', html); html = re.sub(r'\n[ \t]+', '\n', html)
    html = re.sub(r'\n{4,}', '\n\n\n', html)
    return html.strip()

def _li(inner, ordered):
    items = re.findall(r'<li>(.*?)</li>', inner, re.DOTALL)
    out = []
    for i, item in enumerate(items):
        prefix = f"{i+1}. " if ordered else "- "
        out.append(prefix + inline_md(item))
    return '\n'.join(out) + '\n\n'

def card_type(inner):
    """Determine card type from heading text and content heuristics."""
    h4_m = re.search(r'<h4[^>]*>(.*?)</h4>', inner, re.DOTALL)
    heading = h4_m.group(1) if h4_m else ''
    htext = re.sub(r'<[^>]+>', '', heading).strip().lower()
    if htext in ('the claim',):
        return 'claim'
    if htext in ('the response', 'what this means'):
        return 'response'
    if 'the bottom line' in inner.lower() or 'the verdict' in inner.lower():
        return 'conclusion'
    return 'info'

# ── Parse cards from a slide ─────────────────────────────────
CARD_RE = re.compile(r'<(div|li)\s+class="([^"]*(?:\bcard\b(?:-\w+)?)[^"]*)"[^>]*>')

def extract_cards(section_html):
    """Return list of (inner_html, type_string)."""
    html = re.sub(r'<div class="notes"[^>]*>.*?</div>', '', section_html, flags=re.DOTALL)
    html = re.sub(r'<div class="version-badge[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<img[^>]*>', '', html)
    
    cards = []
    pos = 0
    while pos < len(html):
        m = CARD_RE.search(html, pos)
        if not m:
            break
        tag = m.group(1)  # 'div' or 'li'
        classes = m.group(2)
        close_tag = f'</{tag}>'
        depth = 1
        i = m.end()
        while i < len(html):
            if html[i:i+len(close_tag)] == close_tag:
                depth -= 1
                if depth == 0:
                    end = i + len(close_tag)
                    break
                i += len(close_tag)
            elif html[i] == '<' and i+4 < len(html):
                rest = html[i+1:i+6]
                if rest[:4] in ('div ', 'div>', 'div\t') or rest[:3] in ('li>',) or rest[:3] == 'li ' or rest[:3] == 'li\t':
                    depth += 1
                    i += 5 if rest[:3] in ('div',) else 3
                else:
                    i += 1
            else:
                i += 1
        else:
            break
        
        inner = html[m.end():end-len(close_tag)]
        if 'fail-card' in classes:
            pos = end
            continue
        ctype = card_type(inner)
        cards.append((inner, ctype))
        pos = end
    
    # Also grab fail-card, comp-col, prophecy-card
    for pat, ct in [(r'<div class="fail-card[^"]*"[^>]*>(.*?)</div>','fail'),
                     (r'<div class="comp-col[^"]*"[^>]*>(.*?)</div>','comparison'),
                     (r'<div class="prophecy-card[^"]*"[^>]*>(.*?)</div>','prophecy')]:
        for m in re.finditer(pat, html, re.DOTALL):
            cards.append((m.group(1), ct))
    
    return cards

def card_info(inner):
    """Return (title_md, content_md)."""
    m = re.search(r'<h4[^>]*>(.*?)</h4>', inner, re.DOTALL)
    if m:
        return inline_md(m.group(1)), block_md(inner.replace(m.group(0), ''))
    return '', block_md(inner)

# ── Slide detection ──────────────────────────────────────────
SLIDE_RE = re.compile(
    r'<section class="slide([^"]*)"[^>]*data-title="([^"]*)"[^>]*>(.*?)</section>', re.DOTALL
)

def is_sec_div(cls, inner):
    return 'tc' in cls and 'center' in cls

# ── Build XML ────────────────────────────────────────────────
def build():
    slides = SLIDE_RE.findall(RAW)
    L = []
    L.append('<?xml version="1.0" encoding="UTF-8"?>')
    L.append('<presentation>')
    L.append('  <title>Why I Do Not Believe Christianity Is True</title>')
    L.append('  <version>v69</version>')
    L.append(f'  <slide_count>{len(SLIDE_RE.findall(RAW))}</slide_count>')

    slide_count = 0
    for idx, (cls, dt, section_html) in enumerate(slides, 1):
        slide_count += 1
        title_attr = dt.strip()
        is_end = (title_attr == "Thanks")
        is_sec = is_sec_div(cls, section_html) and not is_end
        
        ta = ''
        if is_sec: ta = ' type="section"'
        elif is_end: ta = ' type="end"'
        
        L.append(f'  <slide id="{idx}" title="{esc(title_attr)}"{ta}>')
        
        # kicker
        kick = ''
        m = re.search(r'<p class="[^"]*?\bkicker\b[^"]*"[^>]*>(.*?)</p>', section_html, re.DOTALL)
        if m:
            kick = inline_md(m.group(1))
        else:
            m = re.search(r'<p class="[^"]*?section-number[^"]*"[^>]*>(.*?)</p>', section_html, re.DOTALL)
            if m:
                kick = inline_md(m.group(1))
        if kick:
            L.append(f'    <kicker>{esc(kick)}</kicker>')
        
        # title
        slide_title = ''
        m = re.search(r'<h1 class="[^"]*?\bh1\b[^"]*"[^>]*>(.*?)</h1>', section_html, re.DOTALL)
        if not m:
            m = re.search(r'<h2 class="[^"]*?\bh2\b[^"]*"[^>]*>(.*?)</h2>', section_html, re.DOTALL)
        if m:
            slide_title = inline_md(m.group(1))
        if slide_title:
            L.append(f'    <title>{esc(slide_title)}</title>')
        
        # subtitle
        sub = ''
        m = re.search(r'<p class="[^"]*?\blede\b[^"]*"[^>]*>(.*?)</p>', section_html, re.DOTALL)
        if m:
            sub = inline_md(m.group(1))
        if sub:
            L.append(f'    <subtitle>{esc(sub)}</subtitle>')
        
        # body — cards grouped by section type heuristics
        if not is_sec and not is_end:
            cards = extract_cards(section_html)
            if cards:
                intro = []
                main = []
                outro = []
                for inner, ct in cards:
                    if ct == 'conclusion':
                        outro.append((inner, ct))
                    elif ct in ('claim', 'response'):
                        intro.append((inner, ct))
                    else:
                        main.append((inner, ct))
                
                if intro or main or outro:
                    L.append('    <body>')
                    
                    if intro:
                        st = ''
                        if len(intro) == 1:
                            st, _ = card_info(intro[0][0])
                        L.append('      <section type="intro">')
                        if st:
                            L.append(f'        <title>{esc(st)}</title>')
                        for inner, ct in intro:
                            ct_, cc = card_info(inner)
                            L.append('        <card>')
                            if ct_ and ct_ != st:
                                L.append(f'          <title>{esc(ct_)}</title>')
                            if cc:
                                L.append(f'          <content>{esc(cc)}</content>')
                            L.append('        </card>')
                        L.append('      </section>')
                    
                    if main:
                        L.append('      <section type="main">')
                        for inner, ct in main:
                            ct_, cc = card_info(inner)
                            L.append('        <card>')
                            if ct_:
                                L.append(f'          <title>{esc(ct_)}</title>')
                            if cc:
                                L.append(f'          <content>{esc(cc)}</content>')
                            L.append('        </card>')
                        L.append('      </section>')
                    
                    if outro:
                        L.append('      <section type="outro">')
                        for inner, ct in outro:
                            ct_, cc = card_info(inner)
                            L.append('        <card>')
                            if ct_:
                                L.append(f'          <title>{esc(ct_)}</title>')
                            if cc:
                                L.append(f'          <content>{esc(cc)}</content>')
                            L.append('        </card>')
                        L.append('      </section>')
                    
                    L.append('    </body>')
        
        # notes
        notes = ''
        m = re.search(r'<div class="notes"[^>]*>(.*?)</div>', section_html, re.DOTALL)
        if m:
            notes = block_md(m.group(1))
        if notes:
            L.append(f'    <notes>{esc(notes)}</notes>')
        
        L.append('  </slide>')
    
    L.append('</presentation>')
    return '\n'.join(L)

# ── Run ──────────────────────────────────────────────────────
xml = build()
slide_count = xml.count('<slide ')
with open('/home/bengt/hermes_workspace/why-not-christianity/why-not-christianity-slides.xml', 'w') as f:
    f.write(xml)
print(f"Slides: {slide_count}")
print(f"XML: {len(xml)} chars")
