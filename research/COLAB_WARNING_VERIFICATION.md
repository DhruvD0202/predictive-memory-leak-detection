# Colab warning verification — 10 September 2026

The user's saved warning-results ZIP passed independent verification. **No notebook rerun is needed.** The Colab thresholds, every warning decision, classification results and event outcomes match the local warning experiment. The verified Colab outputs are preserved separately in [results/warnings_colab](../results/warnings_colab); the initial local run remains in `results/warnings`.

Use this complete Colab run for warning tables and figures in the paper, alongside the already-verified Colab forecasting results. No thresholds or models were changed during verification.

## Verified Antarex test results

There are **31,032 scored test origins**: 1,933 leak-active and 29,099 non-leak, including other injected faults. Point precision, recall and F1 below are fractions and are not adjusted by filling detected event intervals.

| Rule | Precision | Point recall | Point F1 | False alarm starts per observed non-leak hour | Events detected |
|---|---:|---:|---:|---:|---:|
| Trend only | 0.802028 | 0.859286 | 0.829670 | 2.127908 | 35 / 35 |
| ARIMA + trend | Undefined | 0.000000 | 0.000000 | 0.000000 | 0 / 35 |
| LSTM + trend | 0.847601 | 0.466115 | 0.601469 | 1.039211 | 34 / 35 |
| Always off control | Undefined | 0.000000 | 0.000000 | 0.000000 | 0 / 35 |

The LSTM-assisted rule produces fewer false alarms and has higher precision, but the trend-only rule catches more leak-active samples and has higher F1. Better LSTM forecasting RMSE therefore does not establish better warning performance under every measure.

Thresholds remain **0.8 pp/min for trend only** and **0.4 pp/min for LSTM + trend**, selected from validation F1. The ARIMA-assisted rule selected the disabled option because every fixed-grid candidate generated no validation warnings. Its undefined precision is expected and is not a missing computation. This finding is limited to the chosen ARIMA forecast-growth rule and candidate grid.

All 35 test events were fully covered and eligible. Trend only detected 35, with median delay **30 seconds**; LSTM + trend detected 34, with median delay **31 seconds** and one missed event. Delay summaries include detected events only. A detection requires a new alarm start inside the recorded leak interval; an alarm already active before onset does not earn a fresh detection.

Sources: [point metrics](../results/warnings_colab/antarex_point_metrics.csv), [event metrics](../results/warnings_colab/antarex_event_metrics.csv) and [per-event outcomes](../results/warnings_colab/antarex_event_outcomes.csv). These are delays after injection starts, not lead times before memory exhaustion.

## What was checked

- Verified the size and SHA-256 hash of all **20 result files**, with duplicate-entry and extraction-path checks.
- Rechecked the exact preprocessing and forecasting ZIPs and the extracted source files used to reconstruct the results.
- Checked the fixed protocol/settings and input provenance, regenerated validation candidate scores and reproduced the selected thresholds.
- Rebuilt every source-based score, warning timeline, point metric, event outcome and descriptive Westermo table. The original Colab integrity report was preserved unchanged.
- Independently reconstructed **402,364 warning decisions** and alarm starts using a separate vectorized three-sample formulation.
- Independently checked **264 per-event outcomes**, including eligibility, first alarm time, exact delay and missed-event handling.
- Independently recalculated **100,591 least-squares slopes**. The maximum numerical difference was approximately 4.27 × 10⁻¹⁴ pp/min.
- Reconstructed confusion counts, precision, recall, F1 and false-alarm-start rates; confirmed all warning decisions and the classification/event tables agree with the local run. The maximum numeric difference across the loaded Colab/local timeline tables was zero.
- Verified the plotted timeline values. All three PNG figures decoded and all three companion PDFs have valid PDF headers. The warning timeline and comparison chart were visually inspected.
- Confirmed every extracted result still matches the archive after verification.

The selection metadata is consistent with validation selection preceding warning test scoring. Artifact checks do not independently prove the historical order of an interactive notebook session. No new experiment, training or parameter adjustment was performed.

Detailed audit: [colab_warning_verification.json](../results/verification/colab_warning_verification.json).

## Saved figures and runtime

- [Warning timeline](../results/warnings_colab/antarex_warning_timeline.png).
- [Point and event comparison](../results/warnings_colab/antarex_warning_comparison.png).
- [Confusion matrices](../results/warnings_colab/antarex_confusion_matrices.png).

The Colab run reports Python 3.13.15, NumPy 2.1.3, pandas 2.2.3 and matplotlib 3.10.0. Its experiment function took **12.924 seconds** for offline table reads, calibration, scoring and plotting. This excludes input unpacking, model inference, final verification and ZIP creation; it is neither total interactive notebook time nor deployment-monitoring overhead.

Westermo retains unknown leak labels. The descriptive transfer matches the local run: no alarms on systems 1 and 2, and one trend-only alarm start on system 3. No Westermo leak precision/recall or false-alarm interpretation is justified. See [descriptive alarm counts](../results/warnings_colab/westermo_descriptive_alarms.csv).

## Provenance and next checkpoint

Verified archive: [review2_warning_results_colab.zip](../data/packages/review2_warning_results_colab.zip), **6,695,498 bytes**.

SHA-256: `76b169d3807ce0fcd5577c6f20cb94d9d4b78c819cc0fecdc32f1df80bdd6fc5`.

Warning input bundle SHA-256: `22201607ad3e0778e38dbc8ed5f688a608a1a7fb3aa37f648448527e94b8199b`.

The dataset-validation and working experimental-showcase requirements are now complete for the documented pilot, including verified Colab preprocessing, baselines, LSTM and initial warning evaluation. **The paper draft is the remaining core requirement for the 75% milestone.** Begin the next separate stage with the Introduction, then proceed section by section using Review 1 and the verified results.

The paper must retain the limitations: one controlled-leak block, three Westermo systems, one LSTM seed, correlated overlapping windows, validation-calibrated warning thresholds, no labeled Westermo leaks and no memory-exhaustion outcomes. Broader evaluation, ablations, uncertainty estimates and deployment remain post-milestone work. The complete warning method and literature grounding are recorded in [WARNING_PROTOCOL.md](WARNING_PROTOCOL.md).
