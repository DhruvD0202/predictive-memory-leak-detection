# Preprocessing checkpoint — 8 September 2026

The pilot preprocessing is implemented and executed. **No forecasting model has been trained, no accuracy numbers have been produced, and the 75% milestone has not yet been reached.** This document records data preparation results, not a paper's model-results section.

Follow-up on 8 September: the user reported successful integrity checks in Colab and saved `data/packages/review2_preprocessed_colab.zip`. All 27 files in that package were independently verified before the baseline experiment. The execution details below describe the earlier local preprocessing checkpoint; see [BASELINE_RESULTS.md](BASELINE_RESULTS.md) for subsequent progress.

## Deliverables

- [Self-contained Colab notebook](../notebooks/01_preprocessing_colab.ipynb), with real outputs from a local CPU execution.
- [Validated raw pilot ZIP](../data/packages/review2_pilot_raw.zip): 214,243,161 bytes, approximately 214 MB. It expands to approximately 1.88 GB.
- [Prepared model inputs](../data/packages/review2_preprocessed.zip): 22,801,333 bytes, approximately 23 MB. Every packaged file was reopened and its SHA-256 checked.
- [Machine-readable processing summary](../data/processed/preprocessing_summary.json) and [saved-data integrity checks](../data/processed/integrity_checks.json).
- [Reusable implementation](../src/preprocessing.py) and [seven integrity tests](../tests/test_preprocessing.py).

In Google Colab, upload the notebook, keep the CPU runtime, run its cells in order and select the raw ZIP when prompted. The last cell downloads the prepared input package. Save that download because runtime files are temporary. The prepared ZIP already delivered here can be used directly for the forthcoming baseline experiment; repeating preprocessing is useful for reproduction, not required to produce another identical input table.

The six computational notebook cells ran successfully under local Windows CPU execution, using Python 3.12.14, NumPy 2.3.5 and pandas 3.0.1. The recorded execution took 38.61 seconds with the previously verified raw extraction already on disk. **This is neither a Colab benchmark nor a monitoring-overhead measurement.** The Google Colab upload/download branch has not been executed in the user's account.

## Fixed pilot settings

These are declared initial defaults, not hyperparameters selected from test performance.

| Setting | Antarex CPU-MEM_mono | Westermo systems 1–3 |
|---|---|---|
| Sampling grid | 5 seconds | Native 30 seconds |
| History | 60 observations, approximately 5 minutes | 60 observations, approximately 30 minutes |
| Forecast target | 60 seconds ahead, 12 steps | 5 minutes ahead, 10 steps |
| Target quantity | `1 - available_memory / total_memory` | Same definition |
| Partitions | Chronological 70% / 15% / 15% | Same fractions, separately per system |
| Leak labels | Recorded active injected leak intervals | Unknown; not assigned negative labels |

Sixty observations span 59 sampling intervals between their first and last timestamps: 295 seconds for Antarex and 1,770 seconds for Westermo. The history descriptions above are approximate. The forecast horizon is measured from the last input timestamp to the target timestamp.

Antarex streams are aligned by timestamps, using the most recent observation at or before a grid timestamp. Maximum permitted observation age is 2.1 seconds; the largest age encountered was approximately 2.006 seconds. There were no unmatched grid rows. Each rate uses differences of cumulative counters divided by the actual elapsed measurement time. Counter resets or invalid elapsed intervals invalidate the affected sequence. CPU fractions use non-overlapping tick categories; guest counters are excluded to avoid double counting.

Westermo's published CPU and disk rates are retained directly. They are not differenced again, and aggregate CPU rates are not mislabeled as percentages. Missing grid rows are left missing, with no interpolation or forward filling. Independent machines remain independent recordings.

## Actual output counts

| Recording | Grid rows | Valid rows | Input features | Training windows | Validation windows | Test windows |
|---|---:|---:|---:|---:|---:|---:|
| Antarex mono | 207,361 | 207,358 | 7 | 145,081 | 31,032 | 31,032 |
| Westermo 1 | 86,401 | 85,749 | 8 | 59,691 | 12,891 | 12,891 |
| Westermo 2 | 86,401 | 86,393 | 7 | 60,412 | 12,891 | 12,745 |
| Westermo 3 | 86,401 | 86,401 | 8 | 60,412 | 12,891 | 12,891 |

There are **464,860 complete forecasting windows** in total. Overlapping windows are correlated and must not be described as independent experimental trials.

Antarex excludes the first rate-dependent row of each of its three partitions. Westermo systems 1 and 2 preserve 652 and 8 missing grid observations, respectively; system 3 has none. Additional potential windows are excluded wherever a complete history and forecast horizon do not fit inside one valid segment and one partition. No sequence bridges a split boundary or a data gap.

## Features and labels

Antarex's seven selected model inputs are memory pressure, anonymous memory in GiB, committed memory in GiB, CPU busy fraction, CPU iowait fraction, page faults per second and major page faults per second. Committed memory is not necessarily resident memory.

Five candidate inputs are constant in Antarex training and therefore removed from the model feature array: swap usage, swap-in rate, swap-out rate, monitored disk-read rate and monitored disk-write rate. The unscaled feature table retains them for audit. The inspected block has unused swap and constant counters on the monitored disk partition; this does not establish an absence of disk activity elsewhere on the machine.

Westermo systems 1 and 3 retain eight features: memory pressure, swap usage, CPU user/system/iowait rates, disk read/write rates and one-minute load. System 2 retains seven because swap usage is constant in its training partition. Feature removal and scaling use only valid training rows.

The 228 Antarex leak episodes are paired from execution start/end events. Labels use start-inclusive, end-exclusive intervals and agree with the supplied fault labels at every grid timestamp. The valid forecasting origins contain 8,992 / 1,707 / 1,933 active-leak labels in training / validation / test. These are **label counts**, not detected leaks, true positives or performance metrics. Other injected fault types remain identifiable in the feature table for later false-alarm analysis.

Fault types, episode identifiers, commands, event times and future labels never enter the model feature array. Westermo's leak labels remain unknown (`NaN`) and `label_known` remains false. They cannot support real-leak precision/recall without independently established labels.

## Verification completed

Seven focused tests passed, covering future-observation isolation, stale data, counter resets and invalid intervals, missing-timestamp gaps, partition isolation, training-only scaling/selection, event pairing, and saved-array round trips with unknown labels. Some tests cover more than one related condition.

The full notebook then reopened every saved dataset and checked all 464,860 windows, finite valid inputs, missing invalid inputs, feature identities, standardized training means/variances, unknown-label handling and fixed forecast horizons. The final processed ZIP was reopened and every entry's hash matched its manifest. A pandas compatibility issue found during the first run was fixed before the successful execution and covered by the round-trip test.

Each dataset folder contains:

- `features.csv.gz`: unscaled candidate features and explicitly separated audit/label columns.
- `model_arrays.npz`: compact two-dimensional standardized inputs, unscaled memory targets, timestamps, validity, split codes and separately named labels.
- `forecast_windows.csv.gz`: history start, forecast origin and target indices, with split membership.
- `scaler.json`, `feature_dictionary.json` and `summary.json`.
- `leak_episodes.csv` for Antarex only.

Construct future model batches from the supplied window indices; do not allocate all overlapping three-dimensional windows at once. At an origin, the final input row is `origin_index`, and the target is the unscaled memory-pressure value at `target_index`.

## Provenance and remaining limits

Raw package SHA-256: `06df79379df958405ab3d3486dea3e81dff2eb6fa26e53b4cf6ea634210db75e`.

Processed package SHA-256 for this execution: `e2c365a5737cb18f3c0f5b8b97428d195a03201a9b7c821946db69b6c352cd01`.

Compressed table timestamps can change package bytes between reruns; each run generates and verifies its own package manifest. The verified raw package remains the common starting point.

The original sources are [Antarex on Zenodo](https://zenodo.org/records/2553224) and [Westermo at the pinned commit](https://github.com/westermo/test-system-performance-dataset/tree/47e0ccdc10c30e86327d6eb828ed48d164469fd4). Both are published under CC BY 4.0. The selected Antarex nested archive was recovered completely and checked against the publisher ZIP member CRC and size; the full outer ZIP was not completely downloaded or MD5-verified. Details remain in [DATA_VALIDATION.md](DATA_VALIDATION.md).

This Antarex block peaks at approximately 42.24% memory pressure and has deliberately injected faults on a real machine. It does not demonstrate naturally occurring production leaks, impending memory exhaustion, or crash prevention. Westermo supplies a separate real-workload forecasting experiment. Broader labeled swap/disk variation and pre-exhaustion validation remain later work.

## Next checkpoint

Implement persistence, a simple past-only trend forecast and a tractable ARIMA baseline, following the [pipeline proposal](PIPELINE_PROPOSAL.md). Use the same saved origins and horizons when comparing models. Select settings on training/validation data, then report measured MAE/RMSE and an explicitly identified actual-versus-predicted interval. Report held-out results only for frozen settings, and do not adapt later LSTM choices to test errors.

Review 1 reference [3], [Assi et al. (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), grounds the Box–Jenkins/LSTM comparison. No prior paper's reported errors have been reused here. LSTM, warning evaluation, scientific plots and the paper draft remain subsequent checkpoints.
