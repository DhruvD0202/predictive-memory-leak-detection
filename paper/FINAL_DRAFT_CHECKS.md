# Final draft checks

Checked: 24 September 2026 (author finalization); substantive manuscript and reference checks: 15 September 2026.

All substantive manuscript writing is complete. The final draft includes Dhruv Dudeja (24BCE0968), Ayush Bhatt (24BDS0180) and Bs srivallabha (24BCE0457), exactly as supplied and in that order. The first page and page footers identify Final draft | 24 September 2026. No affiliation was supplied, and no venue-specific format was requested.

## Deliverables

- [Editable manuscript](Predictive_Memory_Leak_Detection_Draft.md).
- [Checked PDF](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf): 27 pages with 11 section bookmarks.
- [Abstract preview](../output/pdf/Abstract_preview.png) and [Conclusion preview](../output/pdf/Conclusion_preview.png).
- Five figures, nine tables and 46 distinct references, each cited in the manuscript.
- [Ten IEEE/ACM additions](REFERENCE_ADDITIONS.md), integrated into the survey and verified within the documented reading scope.

## Completed writing

| Part | PDF pages |
|---|---|
| Title, Abstract and six keywords | 1 |
| 1. Introduction | 2 |
| 2. Literature Survey | 3-6 |
| 3. Research Gap; 4. Problem Statement | 7-8 |
| 5. Proposed Methodology, including verified architecture | 9-13 |
| 6. Experimental Setup | 14-16 |
| 7. Preliminary Results and Discussion | 17-20 |
| 8. Limitations and Future Work | 21-22 |
| 9. Conclusion | 23 |
| References | 24-27 |

The 237-word Abstract and 230-word Conclusion summarize the executed pilot. Section 7 remains titled Preliminary Results because the available evidence is a development pilot; this is not an unfinished writing section. Table 9 marks additional studies as pending.

## Verification performed on 15 September 2026

- Checked summary metrics and rounded values against saved Colab forecasting and warning tables, including the Antarex 19.78% relative RMSE reduction. The text retains ARIMA's lower Westermo MAE and the trend-only rule's higher recall/F1 and event coverage.
- Rechecked the size and SHA-256 of all 56 original forecasting and 20 warning result files against their manifests. All 76 passed and remain unchanged. No model, threshold or experiment was rerun for this drafting step.
- Confirmed that substantive changes are confined to six Literature Survey paragraphs and ten bibliography entries. Earlier paragraph content, the Abstract/Keywords, sections 1 and 3-9, all experimental numbers and the original 36 bibliographic entries are preserved, allowing for reference renumbering. No unfinished-section placeholders remain.
- Confirmed citations cover exactly references 1-46 in first-appearance order, and all 46 PDF reference links match the Markdown bibliography. Updated the reference numbers in the evidence maps while preserving explicit original Review 1 numbering. Original works were externally checked on 14 September and the ten additions on 15 September; neither audit implies full-text reading of every reference.
- Confirmed five sequential figure captions, nine sequential table captions and all five figure files. Captions remain with their figures/tables; each reference remains on one page.
- Rendered the 27-page PDF. Twelve page bodies match the preceding checked PDF pixel for pixel, excluding page-number footers. Visually inspected all 15 changed page bodies, including the four survey pages and four bibliography pages. Checked every page number/footer and all 11 section bookmarks.
- Refreshed the saved page previews to match the completed PDF.

Detailed provenance is in [DRAFTING_NOTES.md](DRAFTING_NOTES.md), [RESULTS_EVIDENCE.md](RESULTS_EVIDENCE.md), [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md) and [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md).

## Author finalization on 24 September 2026

- Added the exact three author names and registration numbers in the user-supplied order, beneath the title and in PDF author metadata. No affiliation was inferred.
- Changed the document subtitle and all page footers to Final draft | 24 September 2026. The existing manuscript and PDF paths remain stable for repository links.
- Rebuilt the PDF from its updated Markdown source. Confirmed 27 pages and all 11 unchanged bookmark destinations.
- Compared extracted text page by page with the preceding PDF, excluding only the new byline and changed status/date. All substantive text, results, 46 references, five figures and nine tables remain unchanged; PDF links also match page by page.
- Rendered all 27 pages and compared their page bodies with the preceding PDF. Pages 2-27 match pixel for pixel when the updated footer is excluded. Visually inspected the changed first page, final reference page and representative footer strips; no overlap or clipping was found.
- Refreshed the saved page previews to match the final draft. No model training, warning recalibration or experiment rerun was performed for this author update.

## Evidence boundary

Completion applies to the manuscript text. The user's three requirements for the 75% review milestone are covered by the audited pilot datasets, executed pipeline and supported draft. Repeated seeds, feature/model ablations, independent labeled validation, observed memory-exhaustion outcomes and validated live LSTM deployment remain future research. The draft does not claim universally superior LSTM warnings, confirmed Westermo leak detection, production readiness or publication acceptance.
