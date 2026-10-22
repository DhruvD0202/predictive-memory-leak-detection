# Architecture, manuscript format and reference checks

Checked on 22 October 2026 for the latest author-requested manuscript copy in `paper/spin2027_no_disclosure/`.

## Changes made

- Added a monochrome vector architecture diagram at the start of Section 3, with a cross-reference, explanatory caption and alternative text. It is Figure 1 on page 4; the two existing result plots are now Figures 2 and 3.
- The diagram follows the implemented archived workflow: causal preparation, chronological partitions, training-only scaling, forecasts, observed growth, warning rules and separate evaluation. Only ARIMA and LSTM forecasts assist warning rules. The caption identifies the disabled original ARIMA rule and Westermo's lack of leak labels. The adjacent text identifies live sampling as a separate exploratory path.
- Added the competing-interests declaration confirmed by the user for all three authors, using the official template's 9-point `credits` environment before the references.
- Removed one forced page break before the prototype subsection. No font sizes or margins were reduced to fit the diagram. The manuscript now has 15 pages.
- Corrected BibTeX spacing so the existing given names retain both initials for K. S. Trivedi in ref9 and G. Peter Zhang in ref29. Standardized capitalization in the ASPLOS and POPL proceedings titles, rendered book editions as “4th” and “3rd,” and used an en dash for a journal issue range.
- The author's four supplied wording replacements, the abstract, all experimental numbers and both existing plots are preserved. No experiment was rerun for this layout revision.

## Full-paper check

- **15 pages; 36 references; 3 figures; 6 tables; 1 algorithm; 2 numbered equations.**
- Single-column anonymous initial-submission layout, with no author identifiers, page numbers or old final-draft/date banners.
- The supplied `llncs.cls` and `splncs04.bst` are byte-identical to the previously acquired official Springer template package. Class text dimensions and font sizes are unchanged. The existing Times-compatible text/math font setup is retained.
- All 15 pages were rendered and visually inspected, including the complete reference list. No clipped content, overlapping labels, broken tables or unreadable figure captions were found. Diagram labels are 8.2–8.6 points at the intended printed size; it is a vector PDF with embedded fonts.
- Table captions are above their tables and figure captions below their figures. Cross-references update automatically. Legends, axes, units and warning/forecast distinctions remain explained.
- All 11 font resources are embedded. The build has no overfull boxes, missing-character messages, unresolved citations or unresolved references. Nonfatal font-request and underfull diagnostics remain; the build is not described as warning-free.
- The complete Overleaf package was checked for exact membership, CRC, file sizes and SHA-256 hashes, then extracted and compiled separately. The package build has the same 15-page extracted text as the delivered PDF. This is a local build verification, not a claim of uploading a project to Overleaf.

## Reference-format check

- All 36 bibliography keys are unique, every entry is cited, and every citation resolves to a bibliography entry. There are no unused references or placeholder citation markers.
- The official `splncs04` bibliography style supplies numbered references in alphabetical order. Springer permits numbered citations with an alphabetized list; numbering need not follow first appearance.
- Required identifying fields were checked by entry type: author, title, year, journal/proceedings/publisher as applicable, and pages/article identifiers for journal entries. The retained online NeurIPS entry identifies its proceedings volume and official paper URL without an invented page range.
- All 32 recorded DOI strings are unique and syntactically valid. The other four entries have source URLs. This is not a claim that every DOI was freshly resolved over the network on this date.
- Long author lists retain the first six names followed by “et al.”; book editions, page ranges, issue ranges, venue names and DOI/URL rendering were inspected in the final PDF.
- The Antarex citations remain [22,24,23] and the Westermo citation remains [29]. The bibliography contains the same 36 works as before.
- This revision checks formatting and citation matching. The prior bibliographic and claim-support audit remains in `SPIN2027_CITATION_MAP.md`; not every subscription full text has been read.

## Instruction sources and remaining submission limits

The [SPIN submission guidelines](https://conferences.amity.edu/SPIN2027/Paper-Submission-Guidelines.aspx), verified on 16 October 2026, specified anonymous initial submission, Springer single-column format, 8–15 pages and no page numbers. Attempts to retrieve that page again on 22 October failed through the web reader and local HTTPS connection; no changed conference-specific requirement is asserted. Confirm the current submission portal before uploading.

The [Springer engineering-proceedings instructions](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/26362278/data/v2) were successfully rechecked on 22 October. They cover captions, numbering, references, alternative text and the competing-interests declaration. The official package and provenance are recorded in `SPIN2027_REVISION_NOTES.md`.

The prior user instruction to omit AI-assistance disclosures remains in effect. This copy therefore does **not** satisfy the AI-disclosure guidance previously checked in the [Springer author instructions](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/53830640/data/v3). The new competing-interests statement does not replace that disclosure. Formatting checks do not establish full submission-policy compliance, acceptance, a plagiarism score or an AI-detector score.

The repository remains private and no reviewer-access route, conference upload or email submission has been performed by this revision. The authors must approve the final text and arrange the required supplementary access before submission.

Machine-readable checks and final artifact hashes are in `SPIN2027_NO_DISCLOSURE_CHECKS.json`.
