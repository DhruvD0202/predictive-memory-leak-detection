# Paper drafting record

Updated: 14 September 2026.

These are editorial and evidence notes, not paper content.

## Format and current scope

The user resumed drafting, specified no template or page limit, and requested progress updates and previews at each step. The Introduction has been approved. The user then requested at least 30+ references and asked to continue. The Literature Survey is now drafted, and the bibliography contains 36 distinct works, all cited in the manuscript. Use a readable single-column draft with numbered citations. The abstract will be written after the supported results and conclusions.

- Editable source: [Predictive_Memory_Leak_Detection_Draft.md](Predictive_Memory_Leak_Detection_Draft.md).
- Checked preview: [PDF](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf).
- Reference verification and Review 1 corrections: [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md). This records reading scope and distinguishes preprints, publications, books and dataset records.
- Preview builder: [build_paper_preview.py](../scripts/build_paper_preview.py), requiring ReportLab 4.4.9. Run `python scripts/build_paper_preview.py` in an environment containing that dependency. The builder reads the Markdown source and makes the PDF; do not edit PDF text independently.
- A Word file is not delivered at this checkpoint: the bundled Windows runtime has no LibreOffice renderer for the required visual verification workflow. Markdown remains editable in VS Code, and PDF is used for visual review.
- Author names, affiliations and a submission venue have not been supplied and are not invented.

## Preview checks

The seven-page PDF was rendered and visually inspected: Introduction on page 1, Literature Survey on pages 2-4 and References on pages 5-7. Each reference stays together on one page. Automated checks confirmed 36 sequential bibliography entries, all 36 cited in the text, and 36 PDF link targets matching the Markdown source. The approved Introduction body is unchanged. The [Literature Survey preview](../output/pdf/Literature_Survey_preview.png) shows page 2; the full PDF contains the entire section. The reference audit records source-access limitations.

## Section checkpoints

| Section | Status |
|---|---|
| Introduction | Approved by the user; body text preserved |
| Literature Survey | Drafted; eight thematic subsections; ready for preview and feedback |
| Research Gap and Problem Statement | Pending; distinguish the original aim from demonstrated scope |
| Proposed Methodology | Pending; describe the implemented pipeline, including restricted ARIMA and warning rules |
| Experimental Setup | Pending; dataset selection, splits, features, configurations and provenance |
| Preliminary Results and Discussion | Pending; use verified complete Colab outputs only |
| Limitations and Future Work | Pending; label unperformed evaluation explicitly |
| Conclusion | Pending; bounded by executed experiments |
| Abstract and Keywords | Pending; write last |
| References | 36 distinct works, all cited; identity, relevance and reading scope audited |

## Introduction evidence map

| Passage | Grounding and limits |
|---|---|
| Telemetry-based leak detection | Paper reference [1]. Original Review 1 reference [13] has been corrected to the source's full title and author list. No claim that all existing detection is reactive or that this is the first forecasting approach. |
| Box-Jenkins versus LSTM comparison | Paper reference [2], corresponding to Review 1 reference [3]. Bibliographic details and comparison checked against the local publisher PDF, `Time series forecast modeling for the Windows operating.pdf`, pp. 1-11. Does not claim our restricted ARIMA reproduces their entire Box-Jenkins procedure. |
| Memory target and model comparison | `research/PREPROCESSING_RESULTS.md`, `BASELINE_PROTOCOL.md`, `LSTM_PROTOCOL.md` and the corresponding implementation. The memory-pressure proxy is `1 - available / total`; it is neither Linux PSI nor a learned leak probability. |
| Temporal validation and warning separation | `research/WARNING_PROTOCOL.md`, `WARNING_RESULTS.md`, `COLAB_WARNING_VERIFICATION.md`. Warning thresholds are selected on validation data. Forecast metrics and leak recognition are separate tasks. |
| Antarex selection | `research/DATA_VALIDATION.md` and `data/metadata/antarex_record_2553224.json`. Reference [3] cites version 1.0 with the metadata publication date 2018-10-10; the repository record was created in January 2019. References [4]-[5] credit the associated injection and classification work. |
| Westermo selection | Reference [6] and the [publisher's repository at the audited commit](https://github.com/westermo/test-system-performance-dataset/tree/47e0ccdc10c30e86327d6eb828ed48d164469fd4). Pilot systems 1-3 were selected in numerical order. They have no confirmed leak labels. |
| Prototype and claim boundaries | `research/IMPLEMENTATION_VERIFICATION.md`, `README.md` and `research/PROJECT_STATUS.md`. Replay is implemented. Recognition follows injection onset; no exhausted-memory outcome or validated crash-prevention claim is available. |

## Verified external sources

Checked on 14 September 2026. Numeric references are local to this paper draft, not the original report numbering. The entries below record the first Introduction checkpoint; the complete 36-work audit is in REFERENCE_AUDIT.md.

1. [Jindal et al., arXiv](https://arxiv.org/abs/2106.08938): exact title, six authors, 2021, and memory-utilization-based detection approach checked.
2. Assi et al.: the local publisher PDF supplies title, three authors, journal, volume 13(2), pages 2121-2131, 2022, and DOI 10.22075/ijnaa.2022.26974.3505. Do not infer its results describe our experiment.
3. [Antarex record](https://zenodo.org/records/2553224): saved publisher metadata and dataset Readme checked; distinguish original publication date from repository creation date.
4. [FINJ institutional publication record](https://cris.unibo.it/handle/11585/668910): six authors, published workshop proceedings in 2019, volume 11339, pages 800-812 and DOI checked. The workshop title contains 2018; this is not the publication year used here.
5. [Online Fault Classification, arXiv](https://arxiv.org/abs/1810.11208): six authors, original submission 26 October 2018 and revised version 11 July 2019; identifies injected-fault data and Euro-Par 2019 acceptance. This draft cites the identified arXiv version, not an unverified publisher record.
6. [Westermo, arXiv](https://arxiv.org/abs/2311.14510): Per Erik Strandberg and Yosh Marklund, 24 November 2023; real performance measurements on 19 test systems, twice per minute over a month. The experiments use three of those systems.

## Guardrails for later sections

- Use `results/lstm_colab` and `results/warnings_colab`, with their verification reports, for quantitative claims; preserve earlier local runs as separate experiments.
- Do not claim Mann-Kendall testing or a hybrid ARIMA-LSTM was implemented. They may be discussed as literature or future work if accurately sourced.
- Better LSTM RMSE is not evidence of universally better warnings: the verified trend-only rule has higher Antarex recall/F1, and the LSTM-assisted rule has higher precision with fewer false alarm starts.
- Warning delays are measured after injection starts and, where summarized, among detected eligible events. Do not label them pre-exhaustion lead times.
- Single-seed results, restricted ARIMA settings, feature availability, controlled injections and unlabeled Westermo data limit generalization. Repeated seeds, ablations, broader labeled tests, pre-exhaustion evaluation and validated live LSTM transfer remain unperformed.
