"""Markdown -> paper-style HTML (centred title and authors, indented abstract, serif, justified). Print with headless Chrome."""
import sys, re, markdown
src, out = sys.argv[1], sys.argv[2]
body = markdown.markdown(open(src).read(), extensions=['tables', 'sane_lists'])
body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" ?/?></p>', r'<figure><img alt="\1" src="\2"></figure>', body)
body = re.sub(r'<p><strong>((?:Figure|Table) [^<]*)</strong>', r'<p class="caption"><strong>\1</strong>', body)
# front matter: everything before the Abstract heading
i = body.index('<h2>Abstract</h2>'); front, rest = body[:i], body[i:]
front = front.replace('<hr />', '')
ps = re.findall(r'<p>(.*?)</p>', front, flags=re.S); h1 = re.search(r'<h1>.*?</h1>', front, flags=re.S).group(0)
front = f'<header class="front">{h1}<div class="authors">' + ''.join(f'<div>{p}</div>' for p in ps[:-1]) + f'</div><div class="version">{ps[-1]}</div></header>'
m = re.match(r'<h2>Abstract</h2>\s*<p>(.*?)</p>', rest, flags=re.S)
rest = f'<div class="abstract"><p><strong>Abstract.</strong>&nbsp; {m.group(1)}</p></div>' + rest[m.end():]
rest = rest.replace('<hr />', '')
rest = rest.replace('<h2>References</h2>', '<h2 class="refs">References</h2>')
css = """
@page { size: A4; margin: 25mm 25mm 24mm 25mm; @bottom-center { content: counter(page); font-family: "STIX Two Text", "Times New Roman", serif; font-size: 9.5pt; } }
* { box-sizing: border-box; }
html { hyphens: auto; }
body { font-family: "STIX Two Text", "Times New Roman", Times, serif; color: #000; font-size: 10.6pt; line-height: 1.36; margin: 0; text-align: justify; }
header.front { text-align: center; margin: 14mm 0 9mm; }
h1 { font-size: 17.5pt; font-weight: 700; line-height: 1.22; margin: 0 0 7mm; text-align: center; hyphens: none; }
.authors { font-size: 11.5pt; line-height: 1.45; } .authors div + div { margin-top: 2.2mm; } .version { font-size: 9.2pt; margin-top: 3.5mm; }
.abstract { margin: 0 13mm 8mm; font-size: 10pt; line-height: 1.33; }
h2 { font-size: 12.6pt; font-weight: 700; margin: 6.5mm 0 2.4mm; text-align: left; break-after: avoid; hyphens: none; }
h3 { font-size: 10.8pt; font-weight: 700; margin: 4.2mm 0 1.6mm; text-align: left; break-after: avoid; hyphens: none; }
p { margin: 0 0 2.1mm; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 2.4mm; padding-left: 6mm; } li { margin-bottom: 1mm; }
a { color: #000; text-decoration: none; word-break: break-all; }
code { font-family: Menlo, monospace; font-size: 8.6pt; }
table { border-collapse: collapse; margin: 3mm auto 1.5mm; font-size: 9.2pt; line-height: 1.28; break-inside: avoid; text-align: left; width: 100%; border-top: 0.9pt solid #000; border-bottom: 0.9pt solid #000; }
th { font-weight: 700; border-bottom: 0.5pt solid #000; padding: 1.3mm 3mm 1.3mm 0; vertical-align: bottom; }
td { padding: 1.1mm 3mm 1.1mm 0; vertical-align: top; }
figure { margin: 4mm 0 1.5mm; text-align: center; break-inside: avoid; break-after: avoid; } figure img { max-width: 100%; max-height: 78mm; }
p.caption { font-size: 9.2pt; line-height: 1.3; margin: 0 4mm 4mm; }
h2.refs + ol { font-size: 8.9pt; line-height: 1.3; text-align: left; hyphens: none; } h2.refs + ol li { margin-bottom: 1.2mm; }
h2.refs + ol + p { font-size: 8.4pt; }
"""
open(out, 'w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Is the Map All You Need?</title><style>{css}</style></head><body>{front}{rest}</body></html>')
