import re

with open("/home/bengt/hermes_workspace/why-not-christianity-slides.html", "r") as f:
    html = f.read()

# Extract all <section class="slide"> elements with their data-title and content
slide_pattern = re.compile(
    r'<section class="slide[^"]*"[^>]*data-title="([^"]*)"[^>]*>(.*?)</section>',
    re.DOTALL
)
slides = slide_pattern.findall(html)

def strip_html_tags(text):
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def extract_notes(section_html):
    m = re.search(r'<div class="notes"[^>]*>(.*?)</div>', section_html, re.DOTALL)
    if m:
        return strip_html_tags(m.group(1))
    return ""

def extract_content(section_html):
    """Extract readable text, stripping HTML but keeping paragraph structure"""
    # Remove notes divs and version badges
    content = re.sub(r'<div class="notes"[^>]*>.*?</div>', '', section_html, flags=re.DOTALL)
    content = re.sub(r'<div class="version-badge"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<img[^>]*>', '', content)
    content = re.sub(r' style="[^"]*"', '', content)
    content = re.sub(r' data-anim="[^"]*"', '', content)
    content = re.sub(r' data-anim-target="[^"]*"', '', content)
    
    # Block elements -> newline
    content = re.sub(r'</?(?:p|div|section|h[1-4]|li|ol|ul|table|tr|th|td|blockquote|pre)[^>]*>', '\n', content)
    # Inline elements -> just strip
    content = re.sub(r'</?(?:span|b|i|em|strong|code|a|br|sup|sub|q|u|s)[^>]*>', '', content)
    
    # Decode entities
    content = content.replace('&mdash;', '—').replace('&ndash;', '–')
    content = content.replace('&ldquo;', '"').replace('&rdquo;', '"')
    content = content.replace('&lsquo;', "'").replace('&rsquo;', "'")
    content = content.replace('&amp;', '&')
    content = content.replace('&hellip;', '...')
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&lt;', '<').replace('&gt;', '>')
    
    # Clean whitespace
    content = re.sub(r'[ \t]+\n', '\n', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<presentation>')
lines.append('  <title>Why I Do Not Believe Christianity Is True</title>')
lines.append('  <version>v69</version>')
lines.append(f'  <slide_count>{len(slides)}</slide_count>')

for num, (title, section_html) in enumerate(slides, 1):
    notes = extract_notes(section_html)
    content_text = extract_content(section_html)
    
    lines.append(f'  <slide id="{num}" title="{escape_xml(title)}">')
    
    # Split into paragraphs
    paras = [p.strip() for p in content_text.split('\n') if p.strip()]
    if paras:
        lines.append('    <content>')
        for p in paras:
            lines.append(f'      <p>{escape_xml(p)}</p>')
        lines.append('    </content>')
    
    if notes:
        lines.append(f'    <notes>{escape_xml(notes)}</notes>')
    
    lines.append('  </slide>')

lines.append('</presentation>')

output = '\n'.join(lines)

with open("/home/bengt/hermes_workspace/why-not-christianity-slides.xml", "w") as f:
    f.write(output)

print(f"Slides extracted: {len(slides)}")
print(f"Output: {len(output)} chars")
print(f"File: /home/bengt/hermes_workspace/why-not-christianity-slides.xml")
