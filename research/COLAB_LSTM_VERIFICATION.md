# Colab LSTM verification — 9 September 2026

The user's saved Colab LSTM run passed independent artifact, model-inference and metric checks. **No rerun is needed.** All four selected models, their validation/test forecasts and the original result files are preserved in [results/lstm_colab](../results/lstm_colab). The initial local experiment remains separately preserved in `results/lstm`.

Use this complete Colab run for subsequent warning evaluation and paper tables, consistent with the project's free-Colab compute target. Do not combine whichever individual scores look better from the local and Colab runs. The earlier [LSTM_RESULTS.md](LSTM_RESULTS.md) remains a record of the initial local experiment.

## Verified test results

Errors below are **percentage points of total RAM**, not accuracy percentages. Validation selected the saved epoch; these test scores did not select it.

| Recording | Test origins | ARIMA MAE | Colab LSTM MAE | ARIMA RMSE | Colab LSTM RMSE | Relative RMSE reduction vs ARIMA |
|---|---:|---:|---:|---:|---:|---:|
| Antarex mono | 31,032 | 0.362521 | 0.358119 | 1.516401 | 1.216399 | 19.78% |
| Westermo 1 | 12,891 | 0.092984 | 0.099499 | 0.317915 | 0.295990 | 6.90% |
| Westermo 2 | 12,745 | 0.104707 | 0.116579 | 0.291166 | 0.257544 | 11.55% |
| Westermo 3 | 12,891 | 0.229737 | 0.251230 | 0.658167 | 0.608003 | 7.62% |

Source: [Colab metrics.csv](../results/lstm_colab/metrics.csv), including validation scores and all three baselines. These are descriptive results from a single seed on four pilot recordings. LSTM has lower RMSE than ARIMA on all four; ARIMA has lower MAE on all three Westermo recordings. The comparison therefore does not support uniform superiority across error measures, statistical significance, or an improvement in leak-warning accuracy.

## Training and environment

| Recording | Training windows | Epochs run | Selected epoch | Stop reason |
|---|---:|---:|---:|---|
| Antarex mono | 12,091 | 12 | 8 | Four epochs without a new validation minimum |
| Westermo 1 | 14,923 | 14 | 10 | Four epochs without a new validation minimum |
| Westermo 2 | 15,103 | 20 | 20 | Declared 20-epoch limit |
| Westermo 3 | 15,103 | 17 | 13 | Four epochs without a new validation minimum |

The saved configurations match the [fixed LSTM protocol](LSTM_PROTOCOL.md): 60 observations, one unidirectional 32-unit LSTM, existing training-only scalers, seed 42, batch size 64, Adam at 0.001, and validation-based checkpoint selection. The original spaced training-origin indices and full validation/test windows match the verified preprocessing package. Labels are not model inputs.

Colab reports Python 3.13.15, NumPy 2.1.3, pandas 2.2.3, PyTorch 2.11.0+cpu and matplotlib 3.10.0, with two CPU threads and deterministic algorithms enabled. The recorded experiment function took **291.55 seconds** (about 4.9 minutes); this is not the whole interactive notebook session or deployment-monitoring overhead. GPU execution was not exercised.

The original local run used PyTorch 2.8.0+cpu. Fresh training results differ slightly: Westermo 2 selected epoch 20 in Colab versus 19 locally, and its test RMSE is 0.257544 versus 0.261231 percentage points. Antarex test RMSE is 1.216399 versus 1.215839. These differences did not trigger retraining or test-based tuning. All four Colab checkpoints successfully load and reproduce their own predictions locally.

## Checks performed

- Checked the sizes and SHA-256 hashes of **all 56 result files** against the ZIP manifest; rejected unexpected or duplicate entries and verified extraction paths.
- Verified the exact original preprocessing and baseline package hashes and every extracted source file used for inference.
- Checked configurations, feature order, training scalers, training-origin indices, chronological windows and forecast horizons against the approved protocol and inputs.
- Safely loaded all four selected weight files and all four resumable checkpoints. Checked configuration hashes, recorded histories, lowest-validation-RMSE epoch and stopping-rule consistency. Weight and selected-model hashes match the selection record.
- Regenerated **all 139,264 LSTM validation/test predictions** from the user's saved weights. The largest difference from the saved values was approximately **9.89 × 10⁻¹⁷** in memory-pressure fraction, below the notebook's existing tolerance.
- Checked actual values and leak labels against preprocessing, confirmed baseline columns were unchanged, and reconstructed **all 32 aggregate metric rows**. Across all four forecasting methods, **557,056 saved forecast values** were checked. The largest metric discrepancy was approximately 2.63 × 10⁻¹⁵ across the reported numeric error columns.
- Recomputed all eight Antarex metric rows grouped by leak state. Verified all three plotted time-series tables against the complete predictions and the original baseline intervals.
- All eight PNG figures decoded successfully; eight companion PDFs are present. The comparison chart and first Antarex test-interval chart were visually inspected and are readable.
- Confirmed every extracted result file still matches the archive after verification; the user's original integrity report was preserved unchanged.

Saved selection metadata is consistent with validation-only selection preceding test evaluation. Checking artifacts cannot independently prove the historical order of an interactive session. No training, model adjustment, or warning evaluation was performed during this verification.

Detailed evidence: [colab_lstm_verification.json](../results/verification/colab_lstm_verification.json).

## Review-ready figures

- [Actual versus predicted Antarex memory pressure](../results/lstm_colab/antarex_mono/first_test_30min.png).
- [Test MAE and RMSE comparison](../results/lstm_colab/test_error_comparison.png).
- [Westermo 1 actual versus predicted memory pressure](../results/lstm_colab/westermo_1/first_test_day.png).
- [Antarex learning curve](../results/lstm_colab/antarex_mono/learning_curve.png).

The time-series intervals are inherited from the baseline experiment. Shading represents recorded leak injection; it does not represent predicted warnings. Online training-batch curves and fixed-weight validation curves describe different periods and evaluation conditions.

## Provenance and next checkpoint

Verified archive: [review2_lstm_results_colab.zip](../data/packages/review2_lstm_results_colab.zip), **8,105,266 bytes**.

SHA-256: `42cd2d51f29a06d2f6a0912a8b787d343898b11ac3ac55c4b397264743c1a7bf`.

Input bundle SHA-256: `208c3b38ffbd7564e95f7452e0a3d203b1d4734858383e43cf602093ef7a1222`.

Preprocessing and baseline input SHA-256 hashes are retained in the audit JSON and experiment summary. All results in this report are derived from the verified Colab archive.

The dataset and working forecasting-showcase requirements are satisfied for the documented pilot. **The 75% review milestone is not yet complete:** the research-paper draft remains pending, and the next experimental step is forecast-assisted leak-warning evaluation. That step should define its warning rule and evaluation protocol before implementation, choose thresholds using training/validation data and freeze them before test scoring.

Antarex can support evaluation against injected leak events. Its audited pilot has no observed 80% memory-pressure crossing, so these experiments cannot demonstrate warning lead time before exhaustion. Westermo lacks confirmed leak labels; its alarms can be described, but real-leak precision/recall cannot be calculated. Full evaluation, ablations and deployment claims remain later work.
