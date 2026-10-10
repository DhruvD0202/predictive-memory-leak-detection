"""Create a complete two-column LaTeX project from the checked manuscript.

Uses only Python's standard library. The existing manuscript/PDF and figure
sources are not modified. Compile main.tex with XeLaTeX or pdfLaTeX; references
are embedded, so BibTeX, shell escape and external downloads are not required
by the document itself.
"""

from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper/Predictive_Memory_Leak_Detection_Draft.md"
PROJECT = ROOT / "paper/overleaf"
ZIP = ROOT / "output/latex/Predictive_Memory_Leak_Detection_Overleaf.zip"

PREAMBLE = r"""% Complete two-column manuscript; upload this project ZIP to Overleaf.
% Main document: main.tex. Recommended compiler: XeLaTeX.
% References are embedded below; no BibTeX or shell escape is required.
\documentclass[10pt,a4paper,twocolumn]{article}
\usepackage[margin=16mm,top=18mm,bottom=19mm,columnsep=7mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{booktabs,tabularx,array}
\usepackage[font=small,labelfont=bf,labelsep=period]{caption}
\usepackage{titlesec}
\usepackage{cite}
\usepackage{placeins}
\usepackage{stfloats}
\usepackage{balance}
\usepackage{xurl}
\usepackage[hidelinks,breaklinks=true]{hyperref}
\graphicspath{{figures/}}
\newcolumntype{L}[1]{>{\hsize=#1\hsize\linewidth=\hsize\raggedright\arraybackslash}X}
\newcolumntype{R}[1]{>{\hsize=#1\hsize\linewidth=\hsize\raggedleft\arraybackslash}X}
\titleformat{\section}{\normalfont\large\bfseries}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\normalfont\normalsize\bfseries}{\thesubsection}{0.5em}{}
\titlespacing*{\section}{0pt}{2.2ex plus 0.5ex minus 0.3ex}{1ex}
\titlespacing*{\subsection}{0pt}{1.6ex plus 0.4ex minus 0.3ex}{0.6ex}
\setlength{\parindent}{1em}
\setlength{\parskip}{0pt}
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{12pt plus 2pt minus 2pt}
\setlength{\floatsep}{8pt plus 2pt minus 2pt}
\setlength{\dblfloatsep}{10pt plus 2pt minus 2pt}
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{5}
\setcounter{dbltopnumber}{2}
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.06}
\renewcommand{\floatpagefraction}{0.75}
\renewcommand{\dbltopfraction}{0.92}
\renewcommand{\dblfloatpagefraction}{0.75}
\setlength{\emergencystretch}{1.5em}
\raggedbottom
\pagestyle{plain}
"""


def escape(text):
    text = re.sub(r'"([^"]+)"', r"``\1''", text)
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
                    "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(c, c) for c in text)


def inline(text):
    """Preserve source citations and links as functional LaTeX commands."""
    pattern = re.compile(
        r"\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)"
        r"|\[(\d{1,2})\](?:-\[(\d{1,2})\])?"
        r"|\b10\^-12\b|\b1e-6\b")
    output, cursor = [], 0
    for match in pattern.finditer(text):
        output.append(escape(text[cursor:match.start()]))
        label, url, first, last = match.groups()
        if url:
            output.append(r"\url{" + url + "}" if label == url else
                          r"\href{" + url + "}{" + escape(label) + "}")
        elif first:
            numbers = range(int(first), int(last or first) + 1)
            output.append(r"\cite{" + ",".join(f"ref{n}" for n in numbers) + "}")
        else:
            output.append(r"$10^{-12}$" if match.group() == "10^-12" else r"$10^{-6}$")
        cursor = match.end()
    output.append(escape(text[cursor:]))
    return "".join(output)


def table_latex(block, number, caption):
    rows = [[c.strip() for c in row.strip().strip("|").split("|")]
            for row in block.splitlines()]
    alignments = rows.pop(1)
    ncols = len(rows[0])
    assert all(len(row) == ncols for row in rows)
    wide = number == 9
    environment = "table*" if wide else "table"
    # Relative widths sum to the number of X columns, as required by tabularx.
    weights = {
        1: [1.15, 1.02, 1.02, 0.57, 1.24],
        2: [1.28, 1.02, 0.96, 0.90, 0.84],
        3: [1.08, 0.65, 0.85, 1.42],
        4: [0.90, 0.94, 1.16],
        5: [1.20, 0.95, 0.95, 0.95, 0.95],
        6: [1.20, 0.95, 0.95, 0.95, 0.95],
        7: [1.24, 0.94, 0.94, 0.94, 0.94],
        8: [1.15, 0.98, 0.57, 1.10, 1.20],
        9: [0.75, 0.70, 1.55],
    }[number]
    assert abs(sum(weights) - ncols) < 1e-8
    specs = "".join(("R" if a.endswith(":") else "L") + "{" + str(w) + "}"
                    for a, w in zip(alignments, weights))
    out = [f"\\begin{{{environment}}}[tbp]", r"\centering",
           r"\caption{" + inline(caption) + "}", f"\\label{{tab:{number}}}",
           r"\fontsize{8.5}{10.2}\selectfont", r"\setlength{\tabcolsep}{2.4pt}",
           r"\renewcommand{\arraystretch}{1.17}",
           r"\begin{tabularx}{\linewidth}{@{}" + specs + "@{}}", r"\toprule"]
    for i, row in enumerate(rows):
        cells = [inline(c) for c in row]
        if i == 0:
            cells = [r"\textbf{" + c + "}" for c in cells]
        out.append(" & ".join(cells) + r" \\")
        if i == 0:
            out.append(r"\midrule")
    out.extend([r"\bottomrule", r"\end{tabularx}", f"\\end{{{environment}}}"])
    return "\n".join(out)


def main():
    source = SOURCE.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", source.strip())
    title = blocks[0].removeprefix("# ")
    authors = blocks[1].removeprefix("Authors: ").split("; ")
    abstract = blocks[blocks.index("## Abstract") + 1]
    keywords = next(b.removeprefix("Keywords: ") for b in blocks if b.startswith("Keywords: "))
    out = [PREAMBLE, r"\hypersetup{pdftitle={" + escape(title) + "},pdfauthor={" +
           escape("; ".join(authors)) + "}}", r"\begin{document}", r"\twocolumn[{",
           r"\begin{center}", r"{\LARGE\bfseries " + escape(title) + r"\par}", r"\vspace{8pt}"]
    for author in authors:
        name, identifier = re.fullmatch(r"(.+) \(([^)]+)\)", author).groups()
        out.extend([r"\begin{minipage}[t]{0.32\textwidth}\centering",
                    escape(name) + r"\\[2pt]{\small " + escape(identifier) + "}",
                    r"\end{minipage}%"])
    out.extend([r"\end{center}", r"\vspace{3pt}",
                r"\noindent\textbf{Abstract.} " + inline(abstract) + r"\par",
                r"\vspace{5pt}\noindent\textit{Keywords: " + escape(keywords) + r"}\par",
                r"\vspace{12pt}", "}]", ""])
    i = next(n for n, b in enumerate(blocks) if b.startswith("## 1. "))
    figures, tables, paragraphs, references = [], [], [], []
    while i < len(blocks):
        block = blocks[i]
        if block == "<!-- pagebreak -->":
            i += 1
            continue
        if block == "## References":
            out.extend([r"\FloatBarrier", r"\balance", r"\begin{thebibliography}{99}",
                        r"\small", r"\setlength{\itemsep}{3pt}",
                        r"\interlinepenalty=10000"])
            for entry in blocks[i+1:]:
                match = re.fullmatch(r"\[(\d+)\] (.+)", entry, re.DOTALL)
                assert match, entry[:100]
                number, content = match.groups()
                out.append(r"\bibitem{ref" + number + "} " + inline(content))
                references.append(entry)
            out.append(r"\end{thebibliography}")
            break
        if block.startswith("### "):
            heading = re.sub(r"^### \d+\.\d+ ", "", block)
            out.append(r"\subsection{" + escape(heading) + "}")
        elif block.startswith("## "):
            heading = re.sub(r"^## \d+\. ", "", block)
            out.append(r"\section{" + escape(heading) + "}")
        elif re.match(r"Table \d+\. ", block):
            number, caption = re.fullmatch(r"Table (\d+)\. (.+)", block).groups()
            table = blocks[i+1]
            assert table.startswith("|")
            out.append(table_latex(table, int(number), caption))
            tables.append({"number": int(number), "source": table, "caption": block})
            i += 1
        elif block.startswith("!["):
            _, filename = re.fullmatch(r"!\[([^\]]+)\]\(([^)]+)\)", block).groups()
            number, caption = re.fullmatch(r"Figure (\d+)\. (.+)", blocks[i+1]).groups()
            figures.append({"number": int(number), "source": filename, "caption": blocks[i+1]})
            out.extend([r"\begin{figure*}[tbp]", r"\centering",
                        r"\includegraphics[width=\textwidth,keepaspectratio]{" + Path(filename).name + "}",
                        r"\caption{" + inline(caption) + "}", f"\\label{{fig:{number}}}",
                        r"\end{figure*}"])
            i += 1
        else:
            assert not block.startswith(("#", "|", ">")), block[:100]
            assert not re.match(r"Figure \d+\. ", block), block[:100]
            out.append(inline(block))
            paragraphs.append(block)
        out.append("")
        i += 1
    out.append(r"\end{document}")
    assert len(references) == 46 and len(figures) == 5 and len(tables) == 9
    PROJECT.mkdir(parents=True, exist_ok=True)
    (PROJECT / "figures").mkdir(exist_ok=True)
    (PROJECT / "main.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
    files = [PROJECT / "main.tex"]
    for figure in figures:
        original = SOURCE.parent / figure["source"]
        target = PROJECT / "figures" / original.name
        shutil.copyfile(original, target)
        assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
        files.append(target)
    readme = """Predictive Memory Leak Detection Using Time Series Analysis
Two-column LaTeX project

1. In Overleaf, choose New Project > Upload Project and upload the ZIP.
2. Select main.tex as the Main document and XeLaTeX as the compiler.
3. Recompile. No BibTeX, external bibliography, shell escape or manual image
   upload is needed: all 46 references and all five figures are included.

The complete text comes from the checked 8 October manuscript. This is a
generic A4 two-column article, not a claim of compliance with a particular
journal's template. Author names and registration numbers are preserved.

Body text uses two columns. All figures span both columns to keep labels
legible. Tables 1-8 use one column; the text-heavy Table 9 spans both columns.
LaTeX places floats near their discussion, so exact page breaks may vary with
the selected TeX Live release. The document contains page numbers but no
draft/date label. No experimental results or reference entries were changed.

Edit main.tex directly in Overleaf. References are in thebibliography at its
end; edit those entries there. The figures/ folder must remain beside main.tex.

Overleaf upload guide:
https://www.overleaf.com/learn/latex/Kb/Uploading_a_project
"""
    (PROJECT / "README.txt").write_text(readme, encoding="utf-8")
    files.append(PROJECT / "README.txt")
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for path in files:
            package.write(path, path.relative_to(PROJECT).as_posix())
    manifest = {"source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                "paragraphs": len(paragraphs), "references": len(references),
                "figures": figures, "tables": tables,
                "zip_sha256": hashlib.sha256(ZIP.read_bytes()).hexdigest(),
                "files": [{"path": str(p.relative_to(PROJECT)).replace("\\", "/"),
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    (PROJECT.parent / "overleaf_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Created {PROJECT.relative_to(ROOT)}/main.tex and {ZIP.relative_to(ROOT)}")
    print(f"Preserved {len(paragraphs)} body paragraphs, 46 references, five figures and nine tables.")


if __name__ == "__main__":
    main()
