# Two-column LaTeX version

Prepared: 10 October 2026.

The user requested a two-column version of the manuscript, appropriately sized images and complete LaTeX code for upload to Overleaf. No journal template was supplied. This version uses a generic A4, 10-point, two-column article layout; it does not assert compliance with a particular publisher's style.

## Files

- [Overleaf ZIP](../output/latex/Predictive_Memory_Leak_Detection_Overleaf.zip): a complete project, with `main.tex`, `README.txt` and five images in `figures/`.
- [Editable LaTeX](overleaf/main.tex): complete manuscript and embedded `thebibliography` entries. No separate BibTeX run is needed.
- [Two-column PDF](../output/pdf/Predictive_Memory_Leak_Detection_Two_Column.pdf).
- [Source/package manifest](overleaf_manifest.json): the canonical manuscript hash, table/figure mapping and file checksums.
- [Project builder](../scripts/build_overleaf_project.py): converts the existing checked Markdown into this separate LaTeX version. Rebuilding overwrites generated files in `paper/overleaf`; edit a separate copy or the Overleaf project if maintaining independent LaTeX changes.

## Layout decisions

The title, exact supplied authors and Abstract span the page width; the body and bibliography use two columns. Figures use full-width `figure*` environments with proportional scaling so dense architecture labels and plot legends are readable. Tables 1-8 fit in single-column `table` environments with wrapping headers; the text-heavy Table 9 uses `table*`. Captions stay with their figures or tables. LaTeX floats can appear above or below nearby discussion rather than at the exact position of the source paragraph.

The supplied author names and registration numbers, the absence of a draft/date label, page numbering and all experimental limitations are preserved. The prior single-column PDF and Markdown source remain available.

## Overleaf upload

1. Choose **New Project > Upload Project** and upload the ZIP.
2. Set the main document to **main.tex** and select **XeLaTeX** as the compiler.
3. Recompile. All included figure paths are relative; no local machine paths, manual image uploads or shell escape are required.
4. Edit paragraphs and the bibliography directly in `main.tex`. Keep the `figures/` directory alongside it.

See the official [Overleaf upload guide](https://www.overleaf.com/learn/latex/Kb/Uploading_a_project) and [main-document instructions](https://docs.overleaf.com/getting-started/recompiling-your-project/the-main-document).

## Content and package verification

- All 106 prose paragraphs, including the Abstract, occur in the generated LaTeX after markup conversion.
- All 46 original bibliography entries are included, and each is cited. Numeric citations become linked LaTeX citations; mathematical powers are typeset as superscripts.
- All five figures are copied byte for byte; no plotted data, image content or experimental result is changed.
- All nine table bodies and their captions are carried into the source. Tables use the same numerical values and definitions.
- The ZIP integrity check passes, and all seven members match their corresponding project files. The original single-column source and experimental outputs are not modified.

This is a document-formatting change. No model training, data collection or new scientific evaluation is performed.

## Compiled PDF verification

The complete multi-file project compiled successfully with Tectonic 0.17.0 (XeTeX engine) on 10 October 2026. The final PDF has 14 pages. All 14 pages were rendered with Poppler and visually inspected for readable figures, intact table columns, attached captions, consistent page numbers and clean text flow. References remain whole across page breaks, and the final reference page uses both columns.

PDF text checks confirmed the exact three supplied author names and registration numbers, all five figure captions, all nine table captions, all 46 bibliography numbers and the checked result values. No draft/date label remains. The log has no missing characters, undefined references, LaTeX errors or horizontal overflow. Ordinary underfull-box diagnostics and one 1.543-point vertical box diagnostic remain; visual inspection found no clipping or overlap.

SHA-256 of the compiled PDF: `7d85bb1474a14e091ff21979d5f6fe4780d5bf512da8f77c8a63017ba83685b0`.

SHA-256 of the delivered ZIP: `b7acde7522b4a1122d199c6858d9139b1df72fe78de74059f12c2fd94ca2fa4a`.

Compilation was checked locally; no project was uploaded to the user's Overleaf account. Small page-break differences are possible with a different TeX Live release. The recommended Overleaf compiler is XeLaTeX.
