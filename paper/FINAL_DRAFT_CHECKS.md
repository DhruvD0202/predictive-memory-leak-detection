# Complete draft checks

Checked: 15 September 2026.

All substantive manuscript writing is complete. The remaining front-page input is the author names in order and institutional affiliation; the author line is omitted until supplied. No venue-specific format was requested.

## Deliverables

- [Editable manuscript](Predictive_Memory_Leak_Detection_Draft.md).
- [Checked PDF](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf): 25 pages with 11 section bookmarks.
- [Abstract preview](../output/pdf/Abstract_preview.png) and [Conclusion preview](../output/pdf/Conclusion_preview.png).
- Five figures, nine tables and 36 distinct references, each cited in the manuscript.

## Completed writing

| Part | PDF pages |
|---|---|
| Title, Abstract and six keywords | 1 |
| 1. Introduction | 2 |
| 2. Literature Survey | 3-5 |
| 3. Research Gap; 4. Problem Statement | 6-7 |
| 5. Proposed Methodology, including verified architecture | 8-12 |
| 6. Experimental Setup | 13-15 |
| 7. Preliminary Results and Discussion | 16-19 |
| 8. Limitations and Future Work | 20-21 |
| 9. Conclusion | 22 |
| References | 23-25 |

The 237-word Abstract and 230-word Conclusion summarize the executed pilot. Section 7 remains titled Preliminary Results because the available evidence is a development pilot; this is not an unfinished writing section. Table 9 marks additional studies as pending.

## Verification performed

- Checked summary metrics and rounded values against saved Colab forecasting and warning tables, including the Antarex 19.78% relative RMSE reduction. The text retains ARIMA's lower Westermo MAE and the trend-only rule's higher recall/F1 and event coverage.
- Rechecked the size and SHA-256 of all 56 original forecasting and 20 warning result files against their manifests. All 76 passed and remain unchanged. No model, threshold or experiment was rerun for this drafting step.
- Confirmed sections 1-8 and the full bibliography are unchanged from the preceding checkpoint. No unfinished-section placeholders remain.
- Confirmed citations cover exactly references 1-36, and all 36 PDF reference links match the Markdown bibliography. The external-source audit remains dated 14 September; this final check does not imply a new external review or full-text reading of every reference.
- Confirmed five sequential figure captions, nine sequential table captions and all five figure files. Captions remain with their figures/tables; each reference remains on one page.
- Rendered the 25-page PDF. The 22 unchanged body-page regions match the previously inspected PDF pixel for pixel, excluding updated footers. Visually inspected the Abstract, relocated Introduction and Conclusion; checked every page number/footer and all 11 section bookmarks.
- Refreshed the saved page previews to match the completed PDF.

Detailed provenance is in [DRAFTING_NOTES.md](DRAFTING_NOTES.md), [RESULTS_EVIDENCE.md](RESULTS_EVIDENCE.md), [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md) and [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md).

## Evidence boundary

Completion applies to the manuscript text. The user's three requirements for the 75% review milestone are covered by the audited pilot datasets, executed pipeline and supported draft. Repeated seeds, feature/model ablations, independent labeled validation, observed memory-exhaustion outcomes and validated live LSTM deployment remain future research. The draft does not claim universally superior LSTM warnings, confirmed Westermo leak detection, production readiness or publication acceptance.
