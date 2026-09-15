# Paper drafting record

Updated: 15 September 2026.

These are editorial and evidence notes, not paper content.

## Format and current scope

The user resumed drafting, specified no template or page limit, and requested progress updates and previews. On 15 September, the user asked to complete the draft in full. All substantive manuscript writing is now present: Abstract/Keywords, sections 1-9 and the bibliography. Conclusion was written from the supported findings, followed by the Abstract and final consistency checks. Sections 1-8 and the bibliography were preserved at this final checkpoint. The bibliography contains 36 distinct works, all cited in the manuscript, meeting the requested 30+ references. The format is a readable single-column draft with numbered citations; author metadata remains to be supplied.

- Editable source: [Predictive_Memory_Leak_Detection_Draft.md](Predictive_Memory_Leak_Detection_Draft.md).
- Checked preview: [PDF](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf).
- Reference verification and Review 1 corrections: [REFERENCE_AUDIT.md](REFERENCE_AUDIT.md). This records reading scope and distinguishes preprints, publications, books and dataset records.
- Preview builder: [build_paper_preview.py](../scripts/build_paper_preview.py), requiring ReportLab 4.4.9. Run `python scripts/build_paper_preview.py` in an environment containing that dependency. The builder reads the Markdown source and makes the PDF; do not edit PDF text independently.
- Figure 1 is saved in [PNG](figures/pipeline_overview.png) and editable [SVG](figures/pipeline_overview.svg). Its [figure builder](../scripts/build_methodology_figure.py) uses Matplotlib, available in the project's existing `.venv-baseline`. That environment generated the figure; the bundled document runtime built and rendered the paper PDF. No new dependency was installed.
- Figure 2 is the [verified architecture](figures/system_architecture_verified.png). The [architecture review](ARCHITECTURE_REVIEW.md) records the original screenshot, implementation checks, corrected connections and edit provenance. The archived and live paths are separate; live telemetry does not use the saved LSTM.
- Figures 3-5 show forecasts, learning curves and warnings from unchanged Colab result tables. Their [builder](../scripts/build_results_figures.py) uses the existing Matplotlib environment and checks all 76 original result files before plotting. The [results evidence record](RESULTS_EVIDENCE.md) maps every new table, figure and finding to its sources.
- The deliverables are editable Markdown and a visually checked PDF. A Word file is not supplied because the bundled Windows runtime has no LibreOffice renderer for the required visual verification workflow.
- Author names/order and affiliation have not been supplied. The author line is omitted, and no personal details are inferred. No submission venue or venue-specific format was requested.
- The [final draft checks](FINAL_DRAFT_CHECKS.md) record completed writing, validation and remaining author metadata.

## Preview checks

The twenty-five-page PDF was rendered and checked. Abstract/Keywords is on page 1, Introduction on page 2, Literature Survey on pages 3-5, Research Gap and Problem Statement on pages 6-7, the original Methodology subsections on pages 8-11, Architecture on page 12, Experimental Setup on pages 13-15, Preliminary Results and Discussion on pages 16-19, Limitations and Future Work on pages 20-21, Conclusion on page 22, and References on pages 23-25.

All five figures and nine tables retain their captions, and each reference stays on one page. All 36 works remain cited and all 36 PDF reference links match the source. Eleven PDF bookmarks cover Abstract, sections 1-9 and References. The 22 unchanged body-page regions match the previously inspected PDF pixel for pixel, with footers excluded from that comparison; all page numbers and updated footers were checked separately. The new Abstract, relocated Introduction and new Conclusion pages were visually inspected. Table 9 is a plan, not another experimental result. All page previews were refreshed, including the new [Abstract](../output/pdf/Abstract_preview.png) and [Conclusion](../output/pdf/Conclusion_preview.png).

## Section checkpoints

| Section | Status |
|---|---|
| Introduction | Approved by the user; body text preserved |
| Literature Survey | Approved by the user; body text preserved |
| Research Gap and Problem Statement | Approved by the user; body text preserved |
| Proposed Methodology | Accepted for continued drafting, including verified architecture Figure 2; body preserved |
| Experimental Setup | Accepted for continued drafting; six subsections and four tables; body preserved |
| Preliminary Results and Discussion | Accepted for continued drafting; five subsections, four result tables and three figures checked against complete Colab outputs; body preserved |
| Limitations and Future Work | Complete; four subsections and Table 9; completed evidence separated from pending extensions; body preserved |
| Conclusion | Complete; 230 words, bounded by executed experiments and checked against saved results |
| Abstract and Keywords | Complete; 237-word abstract written last, six keywords; summary metrics checked against saved results |
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

## Research Gap and Problem Statement evidence map

The complete four-page Review 1 report was re-read for this checkpoint. The original motivation is retained, while claims that existing methods only detect leaks after abnormal behavior, that the model estimates leak probability, and that low monitoring overhead or crash prevention is demonstrated are not carried into the current evidence claims.

| Passage | Grounding and limits |
|---|---|
| Section 3: empirical evaluation question | Existing paper references [1], [2], [8] and [15] establish relevant prior work. References [31]-[34] ground the distinction between forecast errors, point decisions and events. No exhaustive absence-of-prior-work or algorithmic novelty claim is made. |
| Section 3: dataset roles | `research/DATA_VALIDATION.md`, `research/PREPROCESSING_RESULTS.md` and references [3]-[6]. Antarex has injection labels; the Westermo pilot has unknown leak status. |
| Section 4.1: target, inputs and horizons | `research/BASELINE_PROTOCOL.md`, `research/LSTM_PROTOCOL.md` and `research/WARNING_PROTOCOL.md`. Warning inputs are causal; validation labels calibrate thresholds, so the overall procedure is not wholly unsupervised. |
| RQ1: forecast comparison | Baseline and LSTM protocols use matching held-out origins; the baseline inputs are univariate and LSTM inputs multivariate. This is not an ablation isolating the effect of additional features. |
| RQ2: warning comparison | Warning protocol specifies point precision/recall/F1, non-leak exposure, event eligibility, new alarm starts and detected-event delay. Results must retain missed-event counts and the denominator definitions. |
| RQ3: Westermo behavior | Warning thresholds transfer unchanged; forecasting models are fitted independently per recording. Without labels, alarm counts are descriptive. |
| Scope and original objectives | No observed 80% pressure crossing in the audited Antarex block; runtime timings do not establish continuous-monitoring overhead. The replay implementation is supported by `research/IMPLEMENTATION_VERIFICATION.md`. Research questions summarize the recorded pilot protocol, not a preregistration. |

Jindal, RESIN and Westermo primary publication records were rechecked on 14 September 2026 for the limited claims reused here. No new references or experimental results were added at that checkpoint.

## Proposed Methodology evidence map

| Subsection | Implementation and evidence checked |
|---|---|
| 5.1 Pipeline | Separate recording and model paths in `src/preprocessing.py`, `src/baselines.py`, `src/lstm_forecasting.py` and `src/warning_evaluation.py`; complete verified Colab runs are the result sources. Figure 1 is an explanatory diagram, not a new result. |
| 5.2 Causal preparation | `align_past`, `counter_rates`, `build_antarex`, `build_westermo` and `reconstruct_episodes`. Bounded backward alignment, rate units, unknown labels and gaps are preserved. |
| 5.3 Splits and windows | `partition_codes`, `fit_scaler`, `build_window_index` and `export_dataset`. Fractions apply to time extent; the first Antarex row of each split is invalidated. Feature filtering uses training population standard deviation. Complete future coverage affects offline eligibility, not prediction inputs. |
| 5.4 Baselines | `linear_forecast`, `arima_forecast`, `longest_training_segment`, `fit_arima`, `select_settings` and the baseline protocol. Local line coefficients are recomputed per origin; ARIMA coefficients are fixed after training. The restricted estimator operates on first differences. |
| 5.5 LSTM | `MemoryLSTM`, `train_recording`, `should_stop`, prediction routines and the LSTM protocol. One 32-unit layer, reset states, standardized target, spaced training origins, fixed configuration and validation-selected weights. Training subsets are not asserted identical across methods. |
| 5.6 Warnings | `warning_scores`, `warning_state`, `select_thresholds` and the warning protocol. Minimum growth score, three consecutive origins, threshold grid, disabled option, validation calibration and unchanged Westermo thresholds. |
| 5.7 Evaluation | Error functions, `point_metrics`, `alarm_starts`, `event_metrics` and `describe_unlabeled`. Origin/target times, non-leak exposure, full event coverage, new-start detection, detected-only delay and unlabeled Westermo counts are explicit. |
| 5.8 Evidence and prototype | Colab LSTM/warning verification reports, implementation verification and the warning protocol's staged-development disclosure. No independent confirmation or live Windows LSTM transfer is claimed. |

Primary [statsmodels ARIMA fit documentation](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.fit.html), [PyTorch LSTM documentation](https://docs.pytorch.org/docs/2.8/generated/torch.nn.LSTM.html) and [Kim et al.'s publisher record](https://ojs.aaai.org/index.php/AAAI/article/view/20680) were rechecked on 14 September 2026. Source code determines the actual implementation choices. Documentation versions are not substituted for recorded Colab environment versions. No models, thresholds or saved experimental outputs were changed.

## Architecture and Experimental Setup evidence map

Checked on 15 September 2026. The original architecture was reviewed before a corrected version was included. Experimental values were read directly from the complete Colab archives and unchanged extracted outputs; no experiment was rerun.

| Passage | Evidence and limits |
|---|---|
| 5.9 and Figure 2 | `src/preprocessing.py`, `src/baselines.py`, `src/lstm_forecasting.py`, `src/warning_evaluation.py` and `src/demo_service.py`; detailed corrections in `ARCHITECTURE_REVIEW.md`. The live monitor uses raw memory history, a trend rule and simple forecasts; saved LSTM inference requires matching archived features. |
| 6.1 Provenance | `research/DATA_VALIDATION.md`, the Antarex metadata and nested-member CRC/size audit, and the pinned Westermo acquisition manifest. Full outer Antarex MD5 verification is not claimed. |
| 6.2 Tables 1-2 and features | `preprocessing_summary.json` inside `data/packages/review2_preprocessed_colab.zip`; LSTM `experiment_summary.json` and per-recording `configuration.json`; baseline per-recording `frozen_settings.json` inside its Colab ZIP for contiguous training lengths. Valid rows and eligible windows are distinct. |
| 6.3 Table 3 and training settings | Baseline `experiment_summary.json` in `data/packages/review2_baseline_results_colab.zip`; `results/lstm_colab/experiment_summary.json`, selected checkpoints and configurations. Selected and executed epochs are distinct; model selection uses validation data. |
| 6.4 Warning cohort | Preprocessing label counts, `results/warnings_colab/selection_freeze.json` and the verified warning report. The 35 eligible test events are a denominator, not a new reported detection score. Westermo has no confirmed labels. |
| 6.5 Table 4 | Runtime dictionaries in all four Colab stage summaries. CPU architecture and thread count were captured for LSTM; CPU model and assigned RAM were not. Recorded Matplotlib 3.10.0 differs from the baseline cell's requested 3.10.8. |
| 6.6 Artifacts | The shared prepared-package SHA-256 is `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2`; baseline, LSTM and warning summaries record that identity. Result manifests and verification reports preserve the separation from earlier local experiments. |

The four setup tables match their saved source records. References [3]-[6] supply dataset attribution already audited on 14 September; no new external sources were added in that checkpoint.

## Preliminary Results and Discussion evidence map

The complete [RESULTS_EVIDENCE.md](RESULTS_EVIDENCE.md) maps Section 7 to original metrics, forecast tables, training history, warning decisions and event outcomes. LSTM lowers test RMSE on all four recordings, while ARIMA has lower MAE on Westermo. Warning results preserve the higher LSTM-assisted precision and lower false-alarm rate alongside lower point recall/F1 and one missed event. Delay summaries include detected events only, and Westermo counts remain descriptive. Earlier result files and selection settings are unchanged.

The user-defined 75% milestone has evidence for all three requested components: audited pilot datasets, an executed and verified experimental pipeline, and a draft through supported preliminary results. The manuscript text is now complete; broader research evaluation remains future work.

## Limitations and Future Work evidence map

| Subsection | Grounding and claim boundary |
|---|---|
| 8.1 Dataset and target | Dataset audit, preprocessing records and original references [3]-[6]. One controlled-leak block, three modeled Westermo systems, incomplete metric variation, unknown Westermo labels and no observed exhaustion constrain the target claims. |
| 8.2 Design and comparison | LSTM and warning protocols, staged-development disclosure, fixed configurations and references [27]-[30]. One seed, correlated windows, reused validation, earlier test inspection, unequal feature sets and restricted baselines are explicit. Proposed remedies are not reported as completed experiments. |
| 8.3 Warning and deployment | Warning protocol, point/event evaluation and implementation verification, with references [32]-[34]. Delays exclude missed events; the live monitor is exploratory and does not establish LSTM transfer, overhead or crash prevention. |
| 8.4 Pending studies | Table 9 proposes broader data/seed evaluation, ablations, warning studies, exhaustion outcomes and compatible live validation. Every row is marked pending. Mann-Kendall/Sen and hybrid forecasting remain possible later comparisons grounded in existing references [20]-[26]. |

No experiment, model, threshold or numerical result changed in the limitations checkpoint. No new external reference was added. Conclusion, Abstract/Keywords and final manuscript checks have now been completed.

## Abstract and Conclusion evidence map

| Summary claim | Grounding and limits |
|---|---|
| Pipeline, datasets and prototype | Sections 5-6 and the implementation verification record. Archived saved-model inference is distinguished from exploratory live telemetry; live LSTM transfer is not claimed. |
| Antarex forecast improvement | `results/lstm_colab/metrics.csv`: test LSTM RMSE 1.2163989439 versus ARIMA 1.5164008261 percentage points of RAM, a 19.78% relative reduction. Abstract values use four decimal places; Conclusion uses six. |
| Cross-recording comparison | The same test metric table: LSTM has lower RMSE than all three baselines on each of four recordings; ARIMA has lower MAE on all three Westermo systems. These are single-seed pilot comparisons. |
| Warning trade-off | `results/warnings_colab/antarex_point_metrics.csv` and `antarex_event_metrics.csv`: LSTM assistance increases precision and reduces false alarm starts, but decreases recall/F1 and recognizes 34 rather than 35 of 35 eligible test events. |
| Claim boundary and next research | Section 8 and Table 9: controlled injections, unknown Westermo labels, development-test exposure and absent exhaustion/live-transfer evidence. Independent labeled evaluation, ablations and compatible live validation remain unperformed. |

All 76 original Colab result files were rechecked against their manifests at the final checkpoint and remain unchanged. The manuscript contains no unfinished section placeholders. Author names/order and affiliation are the only outstanding front-page details. Completion of the draft does not establish 100% scientific validation or publication acceptance.

## Verified external sources

Checked on 14 September 2026. Numeric references are local to this paper draft, not the original report numbering. The entries below record the first Introduction checkpoint; the complete 36-work audit is in REFERENCE_AUDIT.md.

1. [Jindal et al., arXiv](https://arxiv.org/abs/2106.08938): exact title, six authors, 2021, and memory-utilization-based detection approach checked.
2. Assi et al.: the local publisher PDF supplies title, three authors, journal, volume 13(2), pages 2121-2131, 2022, and DOI 10.22075/ijnaa.2022.26974.3505. Do not infer its results describe our experiment.
3. [Antarex record](https://zenodo.org/records/2553224): saved publisher metadata and dataset Readme checked; distinguish original publication date from repository creation date.
4. [FINJ institutional publication record](https://cris.unibo.it/handle/11585/668910): six authors, published workshop proceedings in 2019, volume 11339, pages 800-812 and DOI checked. The workshop title contains 2018; this is not the publication year used here.
5. [Online Fault Classification, arXiv](https://arxiv.org/abs/1810.11208): six authors, original submission 26 October 2018 and revised version 11 July 2019; identifies injected-fault data and Euro-Par 2019 acceptance. This draft cites the identified arXiv version, not an unverified publisher record.
6. [Westermo, arXiv](https://arxiv.org/abs/2311.14510): Per Erik Strandberg and Yosh Marklund, 24 November 2023; real performance measurements on 19 test systems, twice per minute over a month. The experiments use three of those systems.

## Guardrails for future revisions

- Use `results/lstm_colab` and `results/warnings_colab`, with their verification reports, for quantitative claims; preserve earlier local runs as separate experiments.
- Do not claim Mann-Kendall testing or a hybrid ARIMA-LSTM was implemented. They may be discussed as literature or future work if accurately sourced.
- Better LSTM RMSE is not evidence of universally better warnings: the verified trend-only rule has higher Antarex recall/F1, and the LSTM-assisted rule has higher precision with fewer false alarm starts.
- Warning delays are measured after injection starts and, where summarized, among detected eligible events. Do not label them pre-exhaustion lead times.
- Single-seed results, restricted ARIMA settings, feature availability, controlled injections and unlabeled Westermo data limit generalization. Repeated seeds, ablations, broader labeled tests, pre-exhaustion evaluation and validated live LSTM transfer remain unperformed.
