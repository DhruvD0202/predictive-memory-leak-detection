# Minimal experimental pipeline proposed for review

Status: proposed on 7 September 2026; preprocessing and statistical baselines executed on 8 September; LSTM forecasting and initial warning evaluation executed on 9 September. See [PREPROCESSING_RESULTS.md](PREPROCESSING_RESULTS.md), [BASELINE_RESULTS.md](BASELINE_RESULTS.md), [COLAB_LSTM_VERIFICATION.md](COLAB_LSTM_VERIFICATION.md) and [WARNING_RESULTS.md](WARNING_RESULTS.md). Compute target: free Google Colab with a CPU fallback.

Update, 10 September: preprocessing, baselines, LSTM and the fixed warning experiment have all been reproduced and verified in the user's Colab. Paper drafting is the next stage. The original proposal below records the intended sequence; the implemented warning rule and evaluation definitions are in [WARNING_PROTOCOL.md](WARNING_PROTOCOL.md), and the completed Colab verification is in [COLAB_WARNING_VERIFICATION.md](COLAB_WARNING_VERIFICATION.md).

## Experimental roles

1. **Antarex CPU-MEM_mono:** primary controlled-leak dataset, with RAM/CPU/page-fault signals and independently recorded leak intervals. Retain metadata describing the unavailable variation in swap and disk I/O.
2. **Westermo:** separate real-workload memory-forecasting experiment. Start with systems 1-3 in numerical order, selected before modeling results. Process each system independently. Additional systems and transfer studies can follow later.

The two sources will not be merged row-by-row or treated as one continuous recording. Westermo will not be assigned leak-free labels merely because no labels are supplied.

## Proposed stages

| Stage | Concrete output |
|---|---|
| Preprocessing | A reproducible Colab notebook; selected feature tables; timestamp/units dictionary; chronological splits; label alignment checks |
| Baseline | Persistence and a simple trend forecast, followed by an ARIMA comparison on the same target/horizons; measured MAE/RMSE |
| LSTM | A small single-layer multivariate LSTM, initially 32 units, with validation-based early stopping and saved weights |
| Evaluation | Untouched-test forecast errors; forecast-assisted leak-warning precision/recall/F1, event detection delay and non-leak alarm rates on Antarex; runtime and memory observations |
| Visualization | Actual-versus-predicted memory on an explicitly identified test interval, error comparison and labeled leak-warning timeline |

## Initial settings to review

These are explicit defaults, not tuned choices or experimentally established optima.

- **Antarex:** 5-second grid, 5-minute past history, 60-second-ahead memory forecast. That is 60 input steps and a forecast target 12 steps ahead. Use multiple steps of the predicted path only if needed for the warning rule; apply the same horizons to baselines.
- **Westermo:** retain its native 30-second granularity. Start with 30 minutes of history and a 5-minute horizon, reporting those results separately from Antarex.
- **Memory target:** memory pressure, `1 - available/total`. Also report error in GiB for a fixed-capacity host when appropriate. Call this OS-level memory pressure, not process RSS or proof of a leak.
- **Split:** 70% training, 15% validation, 15% test in time order for each independent recording. Split before constructing windows. Keep each window's complete history and target inside its assigned partition and exclude windows crossing gaps or label coverage boundaries.
- **Scaling and feature removal:** fit using training data only. Retain information on excluded constant or missing metrics in the report.
- **Training budget:** small batches and at most 20 initial epochs, with early stopping. Use a spaced selection of training origins if necessary for CPU execution, while evaluating at the declared cadence. Save outputs so progress survives a Colab runtime reset.

## Preprocessing choices that must be verified

- Align Antarex streams by actual timestamps using only readings available at each forecast origin. Do not join by row number or interpolate with future values.
- Convert cumulative page-fault and CPU counters into rates with their actual elapsed times. Detect resets and invalid intervals. Use already-computed Westermo rates directly.
- Preserve the first-class distinction among leak, other injected faults and no recorded injected fault.
- Exclude label columns, injection commands, future event times and experiment phase identifiers from model inputs. Event logs are ground truth only.
- Treat long Westermo gaps as separate segments. Any filling must be bounded, causal and reported.
- Keep raw files immutable and reuse saved provenance/checksums.

## Meaning of the warning result

Forecasting a future memory trajectory and recognizing an ongoing injected leak are different evaluations.

The initial warning can combine predicted sustained memory growth with a past-only trend check. Its thresholds must be chosen on training/validation data and frozen before test evaluation. Evaluate against the recorded leak intervals and measure detection delay from injection onset. Generic anomaly accuracy and leak accuracy must not be conflated.

The audited Antarex block does not reach 80% memory pressure. Therefore, no numerical claim about time before exhaustion or crash prevention will be made from it. Predicting the randomly scheduled leak onset before any precursor exists is also not a valid target. Pre-exhaustion lead time requires additional suitable recordings and remains pending.

A Mann-Kendall trend check is a possible supporting baseline, not a leak label generator. Because OS time series can be serially correlated, an uncorrected significance test must not be treated as reliable without checking its assumptions. Final inclusion and settings will be decided during the baseline step.

## Methodological grounding

- Review 1 reference [3]: M. J. Assi, A. A. Fahad and B. Al-Sarray, *Time series forecast modeling for the Windows operating system performance using Box-Jenkins and LSTM models*, IJNAA 13(2), 2121-2131, 2022. [DOI](https://doi.org/10.22075/ijnaa.2022.26974.3505). Supports a statistical-versus-LSTM comparison; its fitted order and reported errors must not be reused as results for Antarex.
- Review 1 reference [13]: Jindal et al., *Memory Leak Detection Algorithms in the Cloud-based Infrastructure*, 2021. [Paper](https://arxiv.org/abs/2106.08938), [implementation](https://github.com/ansjin/memory_leak_detection). Supports trend-based memory warning as a comparator; the public code is distinct from the paper's full private evaluation dataset.
- Review 1 references [6]-[7] motivate a trend-test investigation, but primary Mann-Kendall references and an autocorrelation treatment must be established before the method is adopted in the paper.
- Review 1 reference [12] motivates software-aging forecasting. Reference [9] and other hybrid-model bibliography entries still require metadata verification before use. A hybrid ARIMA-LSTM is a later extension, not a prerequisite for this review.

## Work pending after the initial 75% showcase

- Antarex multi-core validation and evaluation across workloads.
- Additional data with actual critical-memory outcomes and varying swap/disk behavior under labeled leaks.
- Ablations measuring the contribution of CPU/page faults and, where supported, swap/disk I/O.
- Multiple seeds, uncertainty analysis, broader parameter comparisons and hybrid models.
- End-to-end monitoring overhead and deployment tests. Offline inference timing alone cannot establish low production monitoring overhead.
- Final paper results and conclusion, updated only when corresponding experiments exist.

Colab resource availability varies; free GPU access is not assumed. [Official Colab FAQ](https://research.google.com/colaboratory/faq.html).
