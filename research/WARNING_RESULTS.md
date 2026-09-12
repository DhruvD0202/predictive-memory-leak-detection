# Initial leak-warning results — 9 September 2026

**Update, 10 September:** the user's Colab warning run is complete and independently verified. Its selected thresholds, warning decisions, point metrics and event outcomes match this local experiment. See [COLAB_WARNING_VERIFICATION.md](COLAB_WARNING_VERIFICATION.md). The upload/save instructions below have been completed and do not need repeating. Use the complete verified Colab run in `results/warnings_colab` for paper tables and figures.

The warning notebook has been implemented, executed locally on the user's verified Colab inputs, and independently checked. **LSTM-assisted warnings have higher point precision and fewer false alarms, but trend-only warnings have higher recall and F1.** Better forecasting RMSE did not translate into uniformly better warning performance under the fixed rule.

This is an initial controlled-leak experiment. It detects ongoing injected leaks; it does not demonstrate prediction before injection, memory exhaustion, crash prevention or production reliability. The user's warning-stage Colab reproduction is now verified; paper drafting is the next checkpoint.

## User action

1. Upload [04_leak_warning_colab.ipynb](../notebooks/04_leak_warning_colab.ipynb) as a new, separate notebook in Colab. The ordinary CPU runtime is sufficient.
2. Run the cells in order. Upload [review2_warning_inputs.zip](../data/packages/review2_warning_inputs.zip) when prompted. This approximately **31 MB** bundle already contains the verified preprocessed data and all saved forecasts; no training is performed.
3. Inspect the scores, event counts and figures. Check that the final cell reports `all_checks_passed: True`.
4. Save the downloaded `review2_warning_results.zip` as **`review2_warning_results_colab.zip`** in the project's `data/packages` folder. Keep the executed notebook too.

Do not change thresholds after seeing test results. The observed trade-off and the inactive ARIMA-assisted rule are retained findings, not reasons to tune on test data. Empty precision/delay cells for an inactive rule are expected and mean undefined.

## Fixed warning rule and calibration

The [warning protocol](WARNING_PROTOCOL.md) was saved before warning scores and thresholds were computed. At each Antarex origin, estimate memory growth from the last 12 observations, spanning 55 seconds. For an assisted rule, also calculate growth from the current memory pressure to the saved 60-second-ahead forecast. The score is the smaller of observed and predicted growth. Trend-only uses observed growth alone.

Both growth measures use percentage points of total RAM per minute. A warning begins on the third consecutive qualifying 5-second observation, 10 seconds after the first qualifying observation, and ends as soon as the condition fails. Counts reset at gaps and split boundaries. The warning is timestamped at the forecast origin; no future actual measurement enters it.

| Rule | Validation-selected threshold (pp/min) | Validation point F1 |
|---|---:|---:|
| Trend only | 0.8 | 0.801020 |
| ARIMA + trend | Disabled | 0.000000 |
| LSTM + trend | 0.4 | 0.573933 |
| Always off control | Disabled by definition | 0.000000 |

Threshold selection maximized validation point F1 over nine fixed positive thresholds plus a disabled option, breaking ties by fewer false-positive samples and then the higher threshold. All ARIMA-assisted candidates produced zero warnings on validation, so the specified tie rule selected disabled. This demonstrates a limitation of this forecast-growth conjunction and candidate grid with the fitted ARIMA; it is not a general finding that ARIMA cannot detect leaks.

Sources: [validation candidates](../results/warnings/validation_candidates.csv) and [frozen selection](../results/warnings/selection_freeze.json). Calibration is supervised through validation leak labels. The validation period had also been used for forecast selection, and forecasting test errors were viewed in earlier stages; this is a pilot development experiment, not a fresh external test set.

## Antarex point results

The test scoring population contains **31,032 origins**, including **1,933 leak-active** and **29,099 non-leak** origins. It covers approximately **43.1 observed hours**, of which **40.415278 hours** are non-leak exposure. The non-leak group includes other injected faults.

| Rule | TP | FP | TN | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Trend only | 1,661 | 410 | 28,689 | 272 | 0.802028 | 0.859286 | 0.829670 |
| ARIMA + trend | 0 | 0 | 29,099 | 1,933 | Undefined | 0.000000 | 0.000000 |
| LSTM + trend | 901 | 162 | 28,937 | 1,032 | 0.847601 | 0.466115 | 0.601469 |
| Always off | 0 | 0 | 29,099 | 1,933 | Undefined | 0.000000 | 0.000000 |

These are unadjusted sample-level scores. Detecting part of an event does not turn its missed samples into true positives.

| Active rule | False alarm starts | False alarm starts per observed non-leak hour | Non-leak false-positive fraction | False-positive exposure minutes |
|---|---:|---:|---:|---:|
| Trend only | 86 | 2.127908 | 0.014090 | 34.166667 |
| LSTM + trend | 42 | 1.039211 | 0.005567 | 13.500000 |

An alarm start is an off-to-on transition, with a reset at a coverage gap. A start outside a recorded leak is counted as false for this specific target. False-positive exposure includes alarm activity after a leak ends, even when it produces no new alarm start. Exposure is estimated as sample count × cadence; it is not the full raw recording duration.

Source: [antarex_point_metrics.csv](../results/warnings/antarex_point_metrics.csv). The LSTM conjunction is more selective: it produces fewer false positives but also stops warning during many leak-active samples. This explains how its point recall can be low even when it recognizes most events at least once.

## Event recognition and delay

All **35 test leak events** that intersect the scored interval have complete coverage and a covered observation before onset; **none are excluded**. The validation period similarly has 31 eligible events. A test event earns detection only from a new alarm start during its exact [start, end) interval. An alarm already active before onset earns no fresh detection.

| Rule | Detected / eligible | Missed | Event recall | Median delay, detected events only | 90th-percentile delay, detected events only |
|---|---:|---:|---:|---:|---:|
| Trend only | 35 / 35 | 0 | 1.000000 | 30.0 s | 56.0 s |
| ARIMA + trend | 0 / 35 | 35 | 0.000000 | Undefined | Undefined |
| LSTM + trend | 34 / 35 | 1 | 0.971429 | 31.0 s | 45.7 s |
| Always off | 0 / 35 | 35 | 0.000000 | Undefined | Undefined |

Delay is measured from exact injection onset, not from a future exhaustion event. It includes sampling resolution and the confirmation rule. The methods' delay summaries cover different detected-event sets; the lower LSTM 90th percentile alone cannot establish faster detection overall. The missed LSTM event remains in the outcome table with no numerical delay.

Sources: [event metrics](../results/warnings/antarex_event_metrics.csv) and [all per-event outcomes](../results/warnings/antarex_event_outcomes.csv). Point recall and event recall answer different questions; no combined event F1 is reported.

## Westermo descriptive transfer

The frozen Antarex thresholds were applied unchanged at Westermo's native cadence, using 12 past observations spanning 330 seconds and a 300-second forecast. Three qualifying samples span 60 seconds. This transfer changes the workload and temporal context and is exploratory.

No rule generated a warning on Westermo 1 or 2. On Westermo 3, trend-only produced one warning-active sample and one alarm start; the LSTM-assisted, disabled ARIMA-assisted and always-off rules produced none. Scored exposure was 107.425 hours on systems 1 and 3 and 106.208333 hours on system 2.

These counts cannot be interpreted as false-alarm performance, proof of healthy operation, or successful leak detection because Westermo has no confirmed leak labels. Source: [westermo_descriptive_alarms.csv](../results/warnings/westermo_descriptive_alarms.csv).

## Figures and verification

- [Warning timeline](../results/warnings/antarex_warning_timeline.png): the first 30 minutes of eligible Antarex test origins, with recorded injection shaded separately from warning bands.
- [Point and event comparison](../results/warnings/antarex_warning_comparison.png).
- [Confusion matrices](../results/warnings/antarex_confusion_matrices.png).

All three figures were visually inspected and have PDF counterparts. The timeline's plotted rows are saved in CSV form. The interval was fixed by position, not selected for high warning performance.

Seven focused tests passed, covering causal units/indexing, confirmation and gap resets, exact confusion counts and undefined ratios, event timing/boundaries, no credit for pre-existing alarms, incomplete event coverage, validation selection and preservation of unknown Westermo labels. The finalized eight-cell notebook then executed successfully on local CPU in **11.8 seconds**. Its experiment function took approximately **7.03 seconds**, including table reads, calibration, scoring and plotting. This excludes model inference and is not end-to-end monitoring overhead or a Colab runtime guarantee.

Notebook checks reconstructed **402,364 warning decisions**, validation selection, confusion counts and event outcomes. A separate audit independently reconstructed the same decisions using a three-sample Boolean formulation, checked **264 per-event outcomes**, and recalculated **100,591 least-squares slopes** using a polynomial-fit implementation. The largest slope difference was approximately 4.27 × 10⁻¹⁴ pp/min. All **20 result files** match the ZIP manifest.

During notebook validation, CSV serialization exposed a float32/float64 representation mismatch. Output values were standardized to float64; no scoring settings changed. Warning bands were also adjusted to display isolated active samples correctly. The original threshold selection and all five candidate/metric/event CSV files remain byte-identical to the first evaluation. Evidence: [first execution](../results/verification/warning_first_execution.json), [notebook integrity checks](../results/warnings/result_integrity_checks.json), and [independent output audit](../results/verification/warning_output_verification.json).

## Provenance and remaining work

Local runtime: Python 3.12.14, NumPy 2.3.5, pandas 3.0.1 and matplotlib 3.10.8. Inputs are the complete verified Colab preprocessing and LSTM-result packages; no forecasting model was retrained.

Warning input ZIP: **30,911,150 bytes**, SHA-256 `22201607ad3e0778e38dbc8ed5f688a608a1a7fb3aa37f648448527e94b8199b`.

[Local warning result ZIP](../data/packages/review2_warning_results.zip): **6,677,468 bytes**, SHA-256 `2247ef36633cef4e12c6c0338d23c9380e92e0e27247a5e965728df765f082a3`.

The pipeline now has measured forecasting and initial warning results, all reproduced and verified in the user's Colab. The next checkpoint is the research-paper draft, written section by section. The 75% milestone remains incomplete while that draft is pending. Full evaluation, additional seeds/workloads, uncertainty analysis, feature ablations, actual exhaustion outcomes, autocorrelation-aware trend tests, hybrid models and deployment remain later work.

Methodological grounding: Review 1 reference [13], [Jindal et al. (2021)](https://arxiv.org/abs/2106.08938), motivates memory-trend comparison; [Kim et al. (AAAI 2022)](https://doi.org/10.1609/aaai.v36i7.20680) motivates avoiding inflated point-adjusted scores. The exact slope/forecast warning is this project's pilot heuristic, not a reproduction of either paper's algorithm or numerical findings.
