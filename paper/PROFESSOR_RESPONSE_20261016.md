# Response to the professor's comments

Revision: 16 October 2026. Manuscript: **Memory-Pressure Forecasting and Growth-Based Warnings: An Empirical Study**. Section references below use the new SPIN version. This is an author-review record, not a message sent to the professor.

| No. | Change and evidence | Remaining boundary |
|---|---|---|
| 1 | Title now describes memory-pressure forecasting and growth-based warnings. | It does not promise general memory-leak diagnosis. |
| 2 | Abstract distinguishes numerical forecast error, timestamp warnings and injected-event recognition; reports original and repeated-run findings. | Pre-exhaustion warning has not been validated. |
| 3 | A short, explicit research-gap paragraph ends Section 2. | It states the unresolved empirical question, not an unsupported claim that no related approach exists. |
| 4 | Background is shortened; the literature table compares observation level, purpose and relevant evidence boundaries. | This remains a focused narrative survey, not an exhaustive systematic review. |
| 5 | Introduction states three empirical contributions: matched forecast/warning evaluation, repeated feature ablation, and a score-level missed-event explanation. | No new LSTM architecture or production diagnosis is claimed. |
| 6 | Algorithm 1 shows preparation, model/threshold selection, causal forecast and warning generation, and the separate live branch. | Incompatible Windows inputs do not receive an archived LSTM prediction. |
| 7 | Introduction and data section explain why high usage is not a leak. Antarex labels identify controlled injected-leak intervals. | No process-allocation measurements or natural-leak ground truth were added; diagnostic claims were removed. |
| 8 | Abstract, results and conclusion explicitly distinguish post-injection recognition from pre-exhaustion lead time. | Exhaustion trials remain future work; the audited block peaks near 42.24% pressure. |
| 9 | Results compare timestamp precision/recall/F1, missed complete events, false alarm starts, exposure and recognition delay. | Lower average forecast error need not satisfy a thresholded growth rule. |
| 10 | Discussion links the near persistence/ARIMA tie to small no-drift coefficients, explains RMSE/MAE differences, and interprets feature/seed effects. | Explanations are bounded by observed scores; allocation-level causes are not inferred. |
| 11 | Five seeds (7, 21, 42, 84, 123), two LSTM variants and four recordings were run under a fixed protocol; all runs are summarized with sample SD. | No additional labeled recording was acquired; fixed reused holdouts are not independent confirmation. |
| 12 | A memory-only LSTM uses the same input variable as persistence, linear trend and ARIMA; its windows/settings match the multivariate LSTM. | Parameter count and statistical fitting differ; feature importance is not individually isolated. |
| 13 | Figures are regenerated as readable vector plots; captions, units, legends, abbreviations and timing alignment are explicit. Tables use the official single-column width. | Final rendered-page checks are listed separately. |
| 14 | Westermo is repeatedly identified as unlabeled for memory leaks. | Its forecast errors cannot prove real-leak detection. |
| 15 | All 40 implementation tests passed. A separate benchmark measures replay assembly, fresh model inference and resident memory. A live attempt failed before collecting any samples because performance counters were inaccessible; the user chose to document the limitation. | Live timing, CPU overhead and detection accuracy remain unvalidated. Replay timings exclude browser/network latency and are not production-overhead estimates. |
| 16 | Data section explains controlled injections versus industrial workload, exact recording selection and available features. Cadences and 60/300-second horizons are stated. | Horizons are preset pilot settings, not optimized warning lead times; recordings are not directly compared at the same physical horizon. |
| 17 | Threshold grid, validation-F1 selection and tie-breaks are specified; three-reading confirmation is identified as a fixed heuristic. The original ARIMA rule produced no confirmed validation warnings and was disabled by the tie-break. | No claim that ARIMA generally cannot warn; confirmation duration was not optimized. |
| 18 | Metric definitions explain typical versus large-error-sensitive measures, timestamp precision/recall/F1, false starts/exposure, event recall and detected-only delay. | Event recognition does not retroactively count every timestamp as correct. |
| 19 | Original missed event **1534**, starting 19 May 2018 at 22:00:14 UTC, is examined. Maximum forecast growth was about 0.216 pp/min, below 0.4; trend-only warned after 56 s. | This establishes the failed decision gate, not the underlying allocation-level cause. |
| 20 | Methods list dropped constant features and retained feature counts. Repeated memory-only/multivariate results test the retained group. | They do not show that every retained feature helps, or that inactive disk/swap features are generally useless. |
| 21 | Source, settings, weights, manifests and evaluation scripts are retained; reproduction instructions and an anonymous code supplement accompany this revision. | The repository is private. Required data packages and reviewer access must be arranged separately; public access is not falsely claimed. |
| 22 | Conclusion separates demonstrated forecast/warning tradeoffs from unproven diagnosis, exhaustion and deployment claims; specifies next experiments. | Draft completion is not completion of every proposed research extension. |
| 23 | 36 cited works remain. Publisher metadata and prior primary-source audit support the narrowly scoped claims. The supplied Springer class and bibliography style format references. | Some sources were checked through abstracts/metadata rather than full text; that scope is documented. |

## Format adjustment

SPIN 2027 asks for an anonymous, single-column Springer submission of 8–15 pages, without page numbers. The revised submission PDF therefore omits the names/registration numbers present in the earlier author copy. Earlier PDFs remain available and are not silently overwritten. See `SPIN2027_REVISION_NOTES.md` for official links and disclosure requirements.
