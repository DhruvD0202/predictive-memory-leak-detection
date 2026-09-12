# Baseline experiment — 8 September 2026

The first forecasting experiment is complete. Persistence, local linear trend and fitted ARIMA baselines have been evaluated on the verified Antarex/Westermo pilot. **This establishes a working forecasting pipeline, not reliable leak warnings or memory-exhaustion prediction.** LSTM and paper drafting remain later stages.

Follow-up, 8 September: the user completed this notebook in Colab and supplied the results ZIP. Independent verification passed; see [COLAB_BASELINE_VERIFICATION.md](COLAB_BASELINE_VERIFICATION.md). The instructions and local execution details below are retained for reproduction; the user does not need to repeat the baseline run.

## What to run in Colab

1. Open [02_baselines_colab.ipynb](../notebooks/02_baselines_colab.ipynb) in Colab and retain the CPU runtime.
2. Run the cells in order. Upload `review2_preprocessed_colab.zip` from `data/packages` when prompted (approximately 23 MB).
3. Review the error table, charts and final integrity message.
4. Save the downloaded ZIP in `data/packages` as `review2_baseline_results_colab.zip`, and retain the executed notebook.

The notebook is self-contained. It ran successfully on the local CPU using the user's actual Colab-preprocessed ZIP and was subsequently reproduced in the user's Colab environment. The [locally generated results ZIP](../data/packages/review2_baseline_results.zip) is approximately 6.2 MB; the verified [Colab results ZIP](../data/packages/review2_baseline_results_colab.zip) is approximately 6.1 MB.

## Protocol and selected settings

The [protocol](BASELINE_PROTOCOL.md) was written before calculating model results. Existing time partitions and eligible origins were preserved. Settings were selected on validation RMSE and saved for all four recordings before test scoring. The [selection freeze](../results/baselines/selection_freeze.json) records hashes of those settings, which were checked again afterward.

All baselines use past memory pressure only. At each forecast origin, observations through that timestamp are available, including earlier held-out observations. No future observations enter the forecast, and coefficients are never refitted on validation or test. This evaluates repeated short-horizon forecasts, not one forecast of the entire held-out recording from its beginning. A predefined rule clips every model's forecasts to [0,1]; raw forecasts are retained too.

| Recording | Horizon | Trend history | ARIMA order, no drift | ARIMA training rows | Test origins per model |
|---|---|---|---|---:|---:|
| Antarex mono | 60 seconds | 12 observations | (3,1,0) | 145,152 | 31,032 |
| Westermo 1 | 300 seconds | 60 observations | (5,1,0) | 53,188 | 12,891 |
| Westermo 2 | 300 seconds | 30 observations | (5,1,0) | 60,481 | 12,745 |
| Westermo 3 | 300 seconds | 30 observations | (5,1,0) | 60,481 | 12,891 |

Trend history was chosen from 12/30/60 observations and AR order from 1/3/5, with d=1 and q=0 fixed. Each ARIMA candidate used the complete longest contiguous training segment; Westermo 1's gap was not joined. This is a restricted preliminary ARIMA family, not an exhaustive seasonal/order search or complete Box-Jenkins diagnostic study. All twelve fits succeeded; notices concerned expected differencing before Yule-Walker estimation.

ARIMA was selected by validation RMSE for all four recordings. Full validation scores and parameters are in the result package.

## Measured test errors

Both columns are **percentage points of total RAM**: fractional memory-pressure errors multiplied by 100. Lower is better. These are not accuracy percentages; do not report `100 - error` as accuracy.

| Recording | Model | MAE | RMSE |
|---|---|---:|---:|
| Antarex mono | Persistence | 0.361399 | 1.516596 |
| Antarex mono | Linear trend | 0.377387 | 1.743690 |
| Antarex mono | ARIMA | 0.362521 | 1.516401 |
| Westermo 1 | Persistence | 0.094208 | 0.363477 |
| Westermo 1 | Linear trend | 0.145035 | 0.375828 |
| Westermo 1 | ARIMA | 0.092984 | 0.317915 |
| Westermo 2 | Persistence | 0.108831 | 0.316791 |
| Westermo 2 | Linear trend | 0.143653 | 0.348487 |
| Westermo 2 | ARIMA | 0.104707 | 0.291166 |
| Westermo 3 | Persistence | 0.240245 | 0.715420 |
| Westermo 3 | Linear trend | 0.328811 | 0.818381 |
| Westermo 3 | ARIMA | 0.229737 | 0.658167 |

Source: [metrics.csv](../results/baselines/metrics.csv), independently recomputed from saved predictions. There are 69,559 test origins per baseline across the four recordings. Their horizons and workloads differ, so no pooled cross-dataset accuracy is reported.

**Antarex:** ARIMA and persistence are effectively tied. ARIMA's RMSE is only about 0.013% lower in relative terms, while its MAE is slightly higher. This is not evidence of a meaningful or statistically significant improvement. Linear trend performs worse overall on both metrics.

**Westermo:** ARIMA has lower held-out MAE and RMSE than persistence on all three pilot systems. Relative RMSE reductions are approximately 12.53%, 8.09% and 8.00%. These are descriptive results for these recordings, not significance claims, leak-detection performance or demonstrated generalization to all systems.

## Active leaks are harder than aggregate scores suggest

For Antarex, the 1,933 test origins with an active recorded leak have these forecast errors:

| Model | MAE (percentage points) | RMSE (percentage points) |
|---|---:|---:|
| Persistence | 3.918828 | 5.750546 |
| Linear trend | 2.942583 | 6.486998 |
| ARIMA | 3.925664 | 5.750059 |

Grouping uses the label at the forecast origin; a leak may finish before the target. The other 29,099 origins include no recorded injected fault and other fault types. These are forecast-error groups, not classification confusion matrices. Source: [forecast errors by leak state](../results/baselines/antarex_mono/test_forecast_errors_by_leak_state.csv).

Within the active-leak group, trend improves MAE while worsening RMSE. The charts show delayed responses and extrapolation beyond sudden memory drops. Antarex's selected trend required clipping at 595 test origins; the other selected test baselines required none.

No warning threshold, precision, recall, F1 or lead time has been calculated. Antarex has no observed 80% memory-pressure crossing, and Westermo has no confirmed leak labels. These data do not support time-before-exhaustion or crash-prevention claims. Overlapping windows are correlated; no significance claim treats them as independent trials.

## Figures

- [Antarex: first 30 minutes of eligible test forecasts](../results/baselines/antarex_mono/first_test_30min.png).
- [Antarex: fixed interval around the first eligible test leak](../results/baselines/antarex_mono/first_test_leak.png). The chosen onset is the first at least 600 seconds after the first test origin, with room for 1,200 seconds afterward. Nearby leaks inside the view are also shaded.
- [Westermo 1: first day of eligible test forecasts](../results/baselines/westermo_1/first_test_day.png).
- [Test error comparison](../results/baselines/test_error_comparison.png).

All four figures were visually inspected. Each has PNG/PDF versions, and time-series figures include their plotted values in CSV files. Forecasts are placed at target timestamps. Intervals were selected by time/event rules, not forecast error. Shading means recorded injected fault, not predicted warning. Scores use the entire eligible held-out period.

## Reproduction and verification

Input ZIP SHA-256: `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2`. All 27 entries were checked against the manifest. Source provenance and window counts match the validated pilot.

Seven baseline tests passed: straight-line extrapolation, future-value isolation, forecasts against statsmodels, the persistence special case, training-gap isolation, test-value isolation during selection and error units. Full input-window checks passed. Saved predictions were reopened and **417,792 validation/test forecast values** across the three baselines were checked by recomputing their metrics. Selected parameter files stayed unchanged.

The seven notebook code cells completed locally in 12.17 seconds, including extraction, verification, fitting, scoring, plotting and packaging. The experiment portion recorded about 8.52 seconds. These one-run timings are not Colab benchmarks, latency guarantees or monitoring-overhead measurements.

Runtime: Python 3.12.14, NumPy 2.3.5, pandas 3.0.1, SciPy 1.18.1, statsmodels 0.14.6, matplotlib 3.10.8. The user's input was prepared with Python 3.13.15, NumPy 2.1.3 and pandas 2.2.3. Each baseline run records its own versions; small floating-point differences between environments are possible.

Result ZIP SHA-256: `66f98d9dcbf05b4724817837c8b7511ba50b42ae2cb5f8663cb40b24001c5d24`. Every archived file was reopened and matched its manifest. Timestamps and measured runtimes can change ZIP bytes between reruns.

## References and next checkpoint

Progress update, 9 September: the initial multivariate LSTM comparison has now been executed locally; see [LSTM_RESULTS.md](LSTM_RESULTS.md). The paragraph below records the original next-stage plan from this baseline checkpoint.

Review 1 reference [3], [Assi, Fahad and Al-Sarray (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), motivates the statistical-versus-LSTM comparison. This implementation uses the primary [statsmodels ARIMA specification](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.html), [fit-method documentation](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.fit.html) and [rolling-origin forecasting example](https://www.statsmodels.org/v0.12.2/examples/notebooks/generated/statespace_forecasting.html). All numerical results above come from this project's experiment, not prior papers.

Next is the previously proposed small multivariate LSTM, with validation-based stopping and settings fixed before test evaluation. Compare it on the same origins, horizons and clipping rule. Do not tune it to the test errors shown here. Leak-warning evaluation, broader models/ablations and the supported paper draft remain subsequent checkpoints. LSTM superiority is not assumed.
