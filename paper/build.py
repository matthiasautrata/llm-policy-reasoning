"""Typeset PAPER.md as paper/whitepaper.pdf (pandoc + XeLaTeX).
  python paper/build.py
PAPER.md stays plain GitHub Markdown; this script lifts its title block and abstract into
pandoc metadata so the PDF gets a proper title page layout.
"""
import pathlib, re, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
md = (ROOT / "PAPER.md").read_text()
title = re.search(r"^# (.+)$", md, re.M)[1]
subtitle = re.search(r"^\*\*(.+)\*\*$", md, re.M)[1]
byline = re.search(r"^(.+ · .+)$", md, re.M)[1].split(" · ")
abstract = re.search(r"## Abstract\n\n(.+?)\n\n## ", md, re.S)[1]
body = md[md.index("## 1 "):]
body = re.sub(r"^(#+) \d+(\.\d+)? ", r"\1 ", body, flags=re.M)       # LaTeX numbers the sections
body = re.sub(r"^## (Reproducibility|References)$", r"## \1 {-}", body, flags=re.M)
# "*Table N. caption*" above a table -> pandoc caption after it (kept with the table, numbered by LaTeX)
body = re.sub(r"^\*Table \d+\. (.+)\*\n\n((?:\|.*\n)+)", lambda m: "\\needspace{12\\baselineskip}\n\n" + m[2] + "\n: " + m[1] + "\n", body, flags=re.M)

esc = lambda s: s.replace('"', '\\"')
meta = f'''---
title: "{esc(title)}"
subtitle: "{esc(subtitle)}"
author: "{esc(byline[0])}"
date: "{esc(' · '.join(byline[1:]))}"
abstract: |
{chr(10).join('  ' + l for l in abstract.splitlines())}
documentclass: article
classoption: [10pt]
geometry: [margin=2.3cm]
fontfamily: iftex          # suppress the template's lmodern.sty; fonts come from fontspec below
mainfont: TeX Gyre Pagella
sansfont: TeX Gyre Heros
monofont: Latin Modern Mono
linestretch: 1.08
numbersections: true
colorlinks: true
linkcolor: "[HTML]{{2A78D6}}"
urlcolor: "[HTML]{{2A78D6}}"
header-includes: |
  ```{{=latex}}
  \\usepackage{{booktabs}}\\usepackage{{needspace}}
  \\usepackage[font=small,labelfont=bf]{{caption}}
  \\usepackage{{titlesec}}
  \\titleformat*{{\\section}}{{\\large\\bfseries\\sffamily}}
  \\titleformat*{{\\subsection}}{{\\normalsize\\bfseries\\sffamily}}
  \\renewcommand{{\\abstractname}}{{\\sffamily Abstract}}
  \\usepackage{{fancyhdr}}\\pagestyle{{fancy}}\\fancyhf{{}}
  \\fancyhead[L]{{\\small\\sffamily Rules in Context}}\\fancyhead[R]{{\\small\\sffamily Technical report, September 2026}}
  \\fancyfoot[C]{{\\small\\thepage}}\\renewcommand{{\\headrulewidth}}{{0.4pt}}
  ```
---

'''
with tempfile.TemporaryDirectory() as d:
    src = pathlib.Path(d, "paper.md"); src.write_text(meta + body)
    subprocess.run(["pandoc", str(src), "-o", str(ROOT / "paper/whitepaper.pdf"), "--pdf-engine=xelatex",
                    f"--resource-path={ROOT}", "-f", "markdown+implicit_figures", "--shift-heading-level-by=-1"], check=True)
print("paper/whitepaper.pdf written")
