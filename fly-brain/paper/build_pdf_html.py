import sys, re, markdown
src, out = sys.argv[1], sys.argv[2]
md = open(src).read()
body = markdown.markdown(md, extensions=['tables', 'sane_lists'])
body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" ?/?></p>', r'<figure><img alt="\1" src="\2"></figure>', body)
css = """
@page { size: A4; margin: 22mm 20mm 22mm 20mm; }
:root { --fg:#0a0a0a; --muted:#5c5a52; --border:#c4c1b3; --accent:#0034ff; }
* { box-sizing: border-box; }
body { font-family: "Geist", "Helvetica Neue", Helvetica, Arial, sans-serif; color: var(--fg); font-size: 10.2pt; line-height: 1.5; margin: 0; }
h1 { font-weight: 300; font-size: 21pt; line-height: 1.2; margin: 0 0 10pt; letter-spacing: -0.01em; }
h2 { font-weight: 500; font-size: 13pt; margin: 20pt 0 6pt; padding-top: 8pt; border-top: 1px solid var(--border); break-after: avoid; }
h3 { font-weight: 600; font-size: 10.6pt; margin: 14pt 0 4pt; break-after: avoid; }
p { margin: 0 0 7pt; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 7pt; padding-left: 16pt; } li { margin-bottom: 3pt; }
a { color: var(--fg); text-decoration: none; word-break: break-all; }
code { font-family: "Geist Mono", Menlo, monospace; font-size: 8.8pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 8pt; font-size: 8.9pt; break-inside: avoid; }
th, td { border-bottom: 1px solid var(--border); padding: 4pt 6pt 4pt 0; text-align: left; vertical-align: top; }
th { font-weight: 600; border-bottom: 1px solid var(--fg); }
figure { margin: 10pt 0 4pt; text-align: center; break-inside: avoid; } figure img { max-width: 100%; max-height: 82mm; }
hr { display: none; }
h2 + ol { font-size: 8.6pt; line-height: 1.4; }
"""
open(out, 'w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>A wiring-only baseline for a whole-brain fly simulation</title><style>{css}</style></head><body>{body}</body></html>')
