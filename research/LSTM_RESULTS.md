# Initial multivariate LSTM results — 9 September 2026

**Update, 9 September:** the user's free-Colab run is now complete and independently verified. See [COLAB_LSTM_VERIFICATION.md](COLAB_LSTM_VERIFICATION.md) for its measured results and checks. Use that complete run for the next experimental stage and paper tables. The tables below retain the initial local run; they are not the Colab measurements. The Colab handoff below has been completed and does not need repeating.

The first LSTM forecasting experiment has been trained, evaluated and checked locally. Four independent LSTMs were compared with the verified Colab baselines. **LSTM has lower test RMSE on all four pilot recordings, but ARIMA has lower test MAE on all three Westermo systems.** This is a mixed, single-seed forecasting result, not a demonstrated leak-warning system or a completed paper draft.

## User handoff

1. Upload [03_lstm_colab.ipynb](../notebooks/03_lstm_colab.ipynb) as a separate notebook in Colab. CPU is sufficient for the implemented pilot; an available GPU is also supported by the code.
2. Run the cells in order and upload [review2_lstm_inputs.zip](../data/packages/review2_lstm_inputs.zip) when prompted. This **28.9 MB** package contains both verified input ZIPs, so no other upload is needed.
3. Let the training cell finish, inspect the scores/charts and check that the final integrity result reports `all_checks_passed: True`.
4. Save the downloaded ZIP in the project's `data/packages` folder as `review2_lstm_results_colab.zip`. Keep the executed notebook too.

The [local results package](../data/packages/review2_lstm_results.zip) is approximately **8.2 MB**. Both the local and the user's hosted Colab CPU runs are now verified; the CUDA path remains unverified. Training can differ across devices/framework versions, so the Colab results are preserved and evaluated as their own recorded run.

Each epoch saves training progress. Rerunning in the same runtime resumes it. To preserve progress across a Colab runtime reset, enable the notebook's optional Google Drive setting before training; otherwise download the final ZIP before runtime storage disappears.

## Fixed architecture and experiment scope

The [LSTM protocol](LSTM_PROTOCOL.md) was written before training. Each model receives 60 past observations of the already-selected multivariate features, passes them through a single unidirectional 32-unit LSTM and a linear output layer, and predicts one future memory-pressure value. Hidden state resets per window. No fault labels, event identifiers or future measurements enter the network.

Targets use the existing training-only memory-pressure mean and standard deviation. Reverse scaling before scoring, then clip to [0,1], as for all baselines. Use the exact existing validation/test origins and horizons. Training uses regularly spaced eligible windows to reduce CPU cost; the LSTM training subset and the baselines' documented fitted segments are not claimed to be identical.

Fixed settings: seed 42; Adam, learning rate 0.001; batch size 64; gradient-norm clipping at 1; maximum 20 epochs; checkpoint selected by lowest full-validation RMSE; stop after four epochs without a new minimum. There was no hyperparameter search or retraining based on test performance.

| Recording | Features | Parameters | Training windows | Training stride | Epochs run | Selected epoch | Forecast horizon |
|---|---:|---:|---:|---:|---:|---:|---|
| Antarex mono | 7 | 5,281 | 12,091 | 12 | 12 | 8 | 60 seconds |
| Westermo 1 | 8 | 5,409 | 14,923 | 4 | 14 | 10 | 300 seconds |
| Westermo 2 | 7 | 5,281 | 15,103 | 4 | 20 | 19 | 300 seconds |
| Westermo 3 | 8 | 5,409 | 15,103 | 4 | 17 | 13 | 300 seconds |

Three models stopped by validation patience. Westermo 2 reached the declared epoch limit. All selected checkpoints were frozen before test scoring. Validation and test include every existing eligible window, rather than the spaced training subset.

## Measured test comparison

MAE and RMSE are **percentage points of total RAM**, not classification accuracy percentages. The full table including persistence and trend is in [metrics.csv](../results/lstm/metrics.csv).

| Recording | Test origins | ARIMA MAE | LSTM MAE | ARIMA RMSE | LSTM RMSE | Relative RMSE reduction vs ARIMA |
|---|---:|---:|---:|---:|---:|---:|
| Antarex mono | 31,032 | 0.362521 | 0.357980 | 1.516401 | 1.215839 | 19.82% |
| Westermo 1 | 12,891 | 0.092984 | 0.099499 | 0.317915 | 0.295990 | 6.90% |
| Westermo 2 | 12,745 | 0.104707 | 0.119738 | 0.291166 | 0.261231 | 10.28% |
| Westermo 3 | 12,891 | 0.229737 | 0.251230 | 0.658167 | 0.608003 | 7.62% |

On Antarex, LSTM reduces RMSE appreciably in this pilot while only slightly reducing MAE. On Westermo, lower RMSE comes with higher MAE than ARIMA. RMSE gives larger errors more weight, so reporting both is necessary. The outcome is not uniform superiority across error measures.

These percentages describe observed changes in RMSE on these recordings. They are not significance estimates or improvements in leak-warning accuracy. A single seed and overlapping windows do not justify such claims. The comparison changes both model family and input feature set; an ablation is needed to isolate the contribution of CPU/page-fault/other features.

## Antarex forecast errors during active leak origins

The following grouping uses the recorded label at the forecast origin. A leak can end before the target timestamp.

| Model | Active-leak origins | MAE (percentage points) | RMSE (percentage points) |
|---|---:|---:|---:|
| Persistence | 1,933 | 3.918828 | 5.750546 |
| Linear trend | 1,933 | 2.942583 | 6.486998 |
| ARIMA | 1,933 | 3.925664 | 5.750059 |
| LSTM | 1,933 | 2.996998 | 4.515189 |

LSTM has lower active-leak RMSE than the other tested methods; linear trend still has slightly lower active-leak MAE. On the remaining Antarex origins, LSTM also has higher MAE than ARIMA, even though its RMSE is lower. The other-origin group includes other injected faults and must not be called uniformly healthy.

Source: [test_forecast_errors_by_leak_state.csv](../results/lstm/antarex_mono/test_forecast_errors_by_leak_state.csv). These are regression-error groups, not precision/recall. No warning thresholds, F1 scores or event detection delays were computed in this stage.

## Figures and saved artifacts

- [Test error comparison](../results/lstm/test_error_comparison.png), including all four methods.
- [Antarex actual versus predicted memory](../results/lstm/antarex_mono/first_test_30min.png), using the same first test interval as the baseline.
- [Antarex learning curve](../results/lstm/antarex_mono/learning_curve.png).
- [Westermo 1 actual versus predicted memory](../results/lstm/westermo_1/first_test_day.png).

Eight PNG figures and corresponding PDFs are saved: four learning curves, three forecast-interval plots and one comparison chart. Every PNG decoded successfully; the four linked figures were visually inspected. Each time-series figure has its plotted values in CSV form. Intervals were inherited from the baseline protocol, not chosen by LSTM error. Forecast lines appear at their target timestamps; shading shows recorded injected leaks, not generated warnings.

Training curves report an online training-batch average while weights change; validation curves use fixed weights at each epoch end. The two also cover different periods, so a lower validation curve is not by itself evidence of a bug or data leakage.

Each recording includes `best_weights.pt`, a resumable `last_checkpoint.pt`, configuration, exact training-origin indices, training history, selected-model metadata and validation/test predictions. The result ZIP also contains all baseline scores, integrity evidence and a per-file manifest.

## Verification and execution provenance

Seven focused tests passed: past-only indexing, hidden-state isolation, weight reloads, learning on a small test fixture, validation-only stopping, exact interrupted-run resumption and invariance of training/selection to changed test values. Test-fixture results are not used as research performance numbers.

Real-data verification reloaded every selected checkpoint and regenerated all LSTM validation/test forecasts. Across LSTM and the three baselines, **557,056 saved forecast values** were checked and metrics reconstructed. The largest saved-weight reload difference was approximately 9.89 × 10⁻¹⁷ in memory-pressure fraction. Weight/selection hashes stayed unchanged. See [result_integrity_checks.json](../results/lstm/result_integrity_checks.json).

A restart test found that one saved history value needed conversion from a NumPy scalar to a standard numeric value for safe checkpoint loading. This serialization issue was fixed, and existing checkpoints were normalized without changing selected weights. The finalized notebook then resumed the completed checkpoints, rechecked predictions and produced an exactly identical metrics CSV. No extra training epochs or test-driven model adjustments were made. Evidence is retained in `results/verification/lstm_first_execution.json` and `lstm_checkpoint_compatibility_fix.json`.

The initial full local notebook execution took **175.59 seconds** on CPU, including verification, training, evaluation, plotting and packaging. The final checkpoint-resumption verification took **28.35 seconds**. The final notebook's execution metadata refers to that verification pass; cumulative per-model training times remain in the experiment summary. These are local observations, not a Colab runtime guarantee or deployment-monitoring overhead.

Runtime: Python 3.12.14, NumPy 2.3.5, pandas 3.0.1, PyTorch 2.8.0+cpu and matplotlib 3.10.8, using two CPU threads. Deterministic algorithms and seed 42 were enabled. CPU/GPU/framework differences can still affect fresh training outcomes.

Input bundle SHA-256: `208c3b38ffbd7564e95f7452e0a3d203b1d4734858383e43cf602093ef7a1222`.

Final local result ZIP SHA-256: `d661eb4e9acf2ef931099ef9330fc3962e44226439fc654685d95fe7b6371bae`. Every archived entry was reopened and matched its hash. Rerun ZIP bytes can differ because of timestamps and runtime fields.

## Limits and next checkpoint

This is a single-seed pilot with spaced training origins, one small architecture and a restricted ARIMA comparator. No statistical-significance, broad generalization, ablation or production-overhead claim follows from it. Antarex's selected block has no observed 80% memory-pressure crossing; Westermo has no confirmed leak labels. Forecast improvements do not establish warning lead time before exhaustion or crash prevention.

The user's Colab run has now been checked. The next checkpoint is forecast-assisted leak-warning evaluation on Antarex, with thresholds selected from training/validation data and frozen before test scoring. Westermo can support descriptive alarm counts but not real-leak precision/recall. The research-paper draft remains a separate subsequent stage, using only the experiments actually completed.

Methodological grounding remains Review 1 reference [3], [Assi et al. (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), plus the primary [PyTorch LSTM](https://docs.pytorch.org/docs/2.8/generated/torch.nn.LSTM.html) and [reproducibility](https://docs.pytorch.org/docs/2.8/notes/randomness.html) documentation. Prior publications' reported numbers are not reused as this project's results.
