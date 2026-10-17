# Final revision checks — 16 October 2026

Final package and Git handoff verification completed on 17 October 2026; the experiments and manuscript revision retain their 16 October identifiers.

Manuscript: **Memory-Pressure Forecasting and Growth-Based Warnings: An Empirical Study**.

The revision is complete for the authors' review. This record verifies the delivered artifacts and describes the remaining scientific and submission limits. It does not certify conference acceptance, originality-detector scores or experiments that were not performed.

## Manuscript and format

- The delivered PDF has **14 pages, 36 references, 6 tables, 2 figures, 1 algorithm and 2 numbered equations**.
- The anonymous initial-submission layout uses the unchanged official Springer `llncs.cls` (2.25) and `splncs04.bst`, default text dimensions and font sizes, one column and no page numbers. See `SPIN2027_REVISION_NOTES.md` for the checked SPIN and publisher instructions.
- Author names, registration numbers and identifying local paths are absent from the PDF text and metadata. Earlier named/two-column versions remain available separately.
- AI assistance is disclosed in a first-page footnote, an end statement and figure/table notes. This does not replace the authors' review and responsibility.
- All 14 final pages were rendered and visually inspected. Figure labels, units, legends and captions are readable; the plots use distinct line styles. No overlaps or clipped content were found. Figure-description text accompanies the source.
- The final compiler log contains no overfull boxes, unresolved citations or missing-character diagnostics. Nonfatal font-request, package-comment encoding and underfull-line diagnostics remain; the rendered output was checked. The build is not described as warning-free.
- Every bibliography item is cited. The supplied Springer style formats the entries; longer author lists are abbreviated to six authors followed by “et al.” in line with the checked engineering-proceedings guidance. Full retrieved metadata is retained separately. Citation verification scope is recorded in `SPIN2027_CITATION_MAP.md`; not every subscription full text was read.
- Machine-readable page/metadata checks are in `SPIN2027_PDF_CHECKS.json`.

## Experiments and numerical audit

- The new fixed-protocol study trained **40 models**: five seeds, two feature sets and four recordings. Original Colab results remain separate and unchanged.
- Independent verification passed for **321 manifested files**, **1,392,640 validation/test forecasts**, **240 fresh inferences from selected weights** and **80 warning partition/method checks**. It also checked checkpoint selection, identical forecast origins, threshold selection, confusion counts, complete-event recognition, delay and seed summaries. See `results/revision_diagnostics/revision_integrity_checks.json`.
- All **40 implementation tests passed**, including local HTTP endpoint tests. These are functional checks, not a live detection or production-load evaluation.
- The memory-only comparison preserves the multivariate eligibility mask and training settings. It changes parameter count. No individual-feature causal contribution is claimed.
- Repeated-run results include unfavorable findings: extra features do not improve every recording, and the original warning false-alarm advantage is not stable across seeds. Fixed reused holdouts do not provide independent new-machine validation.
- The original missed injected event is identified and its failed warning gate is explained using saved scores; no allocation-level root cause is inferred.

## Prototype and untested claims

- The successful local benchmark measured archived replay assembly and saved-model inference. All **404 first/warm inference requests** matched the corresponding saved predictions within the specified tolerance. Timing excludes HTTP transport and browser rendering; resident memory includes loaded data, libraries and models.
- The attempted live collection produced **zero samples** because Windows performance counters were inaccessible in the restricted environment. The unrestricted run was **not executed** after automatic approval review hit a usage limit. This was an approval-service availability failure, not a determination that the benchmark was unsafe. The user chose to document the limitation and finish the revision.
- Consequently, live processing time, CPU overhead, naturally occurring leak detection and advance warning before memory exhaustion remain unvalidated. Westermo has no confirmed memory-leak labels. Antarex evidence concerns controlled injected-leak intervals.

## Handoff verification

- `output/latex/SPIN2027_Overleaf.zip`: **12 payload files plus a manifest**. CRC, exact membership, sizes and SHA-256 checks passed. The ZIP was extracted into a separate directory and independently compiled with Tectonic/XeTeX. The rebuilt PDF has 14 pages and identical extracted text on every page to the delivered PDF. This is a local package-build check, not a claim that a project was uploaded to Overleaf. Select **XeLaTeX** and `main.tex` when uploading it.
- `output/supplement/SPIN2027_Reproducibility_Code.zip`: **329 payload files plus a manifest**. CRC, membership, sizes, SHA-256 and identity-string checks passed. All four notebooks' executable code cells match the originals; outputs and execution counts are cleared, and personal folder prefixes in Markdown are generalized in the supplement only.
- `data/packages/revision_study_results_20261016.zip`: **322 entries**, including the 321 files listed by the study manifest. It retains the full new predictions, warnings, origins, selected weights and settings. Its receipt records size and SHA-256. The restore command was successfully exercised against this archive and matching existing files.
- Input data ZIPs are not in the anonymous code supplement. The full-result ZIP is also separate and excluded from ordinary Git history; its receipt is tracked. `research/REVISION_REPRODUCTION.md` specifies required input hashes, package restoration, environment, training and evaluation instructions.
- Git attributes preserve the exact recorded bytes of frozen study outputs, protocol/code inputs and official template files. A separate export with Windows line-ending conversion enabled passed **187 checksum checks**: 181 tracked study-manifest files, four frozen code/protocol files and two official template files. This prevents automatic newline conversion from invalidating their recorded hashes.

| Delivered file | Bytes | SHA-256 |
|---|---:|---|
| `Memory_Pressure_Forecasting_SPIN2027.pdf` | 122686 | `7c8bbc95468b6c10d6727ca21aecafae58f5afdacbf57a321297113de7c8b45e` |
| `SPIN2027_Overleaf.zip` | 79834 | `6274832d5d7794a9edab3b13c668446092f9c15c3999a2705fb0feec070c4689` |
| `SPIN2027_Reproducibility_Code.zip` | 16049538 | `49fa88267e355499996c731389a99455def580830f7d3a3aa592acdebff6bb66` |
| `revision_study_results_20261016.zip` | 62574325 | `27d5ad576adccdf13924d17b2a5563e802117a0e0c339d8129cf1871cc083f98` |

## Before submission

The authors still need to read and approve the complete manuscript, confirm the portal's current instructions, and arrange anonymous reviewer access to code and required input/result archives. The GitHub repository is private; a local ZIP is not a public release. No conference upload, email submission, copyright transfer, external plagiarism scan or AI-detector test has been performed. No detector score is promised.
