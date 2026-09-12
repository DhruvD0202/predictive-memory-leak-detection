# Initial multivariate LSTM protocol — 9 September 2026

Written before LSTM training or evaluation. This checkpoint covers LSTM forecasting and its comparison with the verified baselines. Warning classification and paper drafting remain later stages.

## Architecture and prediction target

Use one independent model for each existing recording: Antarex mono and Westermo systems 1–3. Do not pool unrelated timelines. Each sample contains the existing 60 observations and all training-selected standardized features: seven for Antarex, eight for Westermo 1/3 and seven for Westermo 2. No label, timestamp or event identifier is an input.

The network is a **single, unidirectional, 32-unit LSTM**, followed by a linear layer from its last hidden output to one future memory-pressure value. Hidden state resets for every window. No residual shortcut, bidirectional layer, dropout or extra hidden layer is used in this initial model. Predict the target standardized with the already-fitted training memory-pressure mean and standard deviation; reverse that transformation for scoring.

Use the existing horizons: 60 seconds for Antarex and 300 seconds for each Westermo system. Preserve the exact validation/test origins used by the baselines. No new data preparation or scaler fitting is performed.

## Training budget, selected before results

- PyTorch implementation; use an available GPU automatically, otherwise CPU. Limit CPU worker threads to two. No paid runtime is required by the implementation.
- Fixed seed 42 for initialization and training-window shuffling, independently reset for each recording. Record actual framework/device versions. A single seed is a pilot result, not a robustness study.
- Train on every **12th eligible training origin for Antarex** and every **4th for Westermo**, in chronological index order before shuffling. This limits CPU cost and redundant overlapping samples. The baselines' fitted training segments are documented separately; their training subsets are not claimed to be identical to the LSTM's. Validation and test use every existing eligible origin.
- Batch size 64, Adam with learning rate 0.001, mean squared error on standardized targets and gradient-norm clipping at 1.0.
- At most 20 epochs. Evaluate full validation RMSE after each epoch, using predictions clipped to [0,1] in physical memory-pressure units, as for the baselines.
- Save the checkpoint with the strictly lowest observed validation RMSE. Stop after four consecutive epochs with no new minimum. No minimum-epoch rule, extra learning-rate search or automatic retraining after observing test errors.
- Use deterministic algorithms where supported and seed the random generators. Reset hidden state per window. Shuffling already-separated training windows does not alter the chronological partition boundaries.

Batch gathering uses the compact feature arrays and window indices rather than allocating every overlapping sequence in memory. Save a checkpoint, optimizer/RNG state and history after each epoch so an interrupted run can resume with the same data and configuration. Completed training checkpoints may be reused only when their input hashes/configuration match.

## Validation and test separation

Train/select all four models before opening baseline test results or scoring LSTM test forecasts. Save the selected weight hashes, epochs and configuration in a selection-freeze record. Parameters, feature choices and stopping decisions must not use test labels or errors. The baseline test scores were already reported in the previous stage; they must not be used to tune this model.

At each held-out origin, the model may use actual observations through that origin. It cannot consume any later observation within the forecast horizon. This is rolling short-horizon forecasting. Save both raw and [0,1]-clipped forecasts and report clipping counts.

Compare measured MAE/RMSE with all three saved baselines at the same validation/test origins, independently per recording. Report errors as fractions and percentage points of total RAM. Lower regression error is not leak-warning classification accuracy.

Use the same predetermined illustrative test intervals as the baseline experiment and add LSTM forecasts; also plot training/validation curves and per-recording error comparisons. Do not select visual intervals by which model looks best. Descriptive Antarex errors grouped by active-leak status at the origin are permitted, but they are not precision/recall.

## Verification and limits

Check window-to-target indexing, hidden-state isolation, exclusion of label columns, training-only targets/scalers, checkpoint reload equivalence, loss/gradient behaviour and saved metric reconstruction. Record the actual training origin counts and each selected epoch. Keep the first completed protocol run even if its results are worse than persistence or ARIMA.

There is no guarantee that the LSTM will outperform the baselines. No full seed study, ablation, hybrid ARIMA-LSTM, Mann-Kendall significance analysis or deployment-overhead assessment is part of this checkpoint. Existing Antarex data do not demonstrate memory exhaustion; Westermo has no confirmed leak labels.

## Grounding

Review 1 reference [3], [Assi, Fahad and Al-Sarray (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), motivates comparing statistical forecasting with LSTM; its model performance is not reused as this project's evidence. The implementation follows primary [PyTorch LSTM documentation](https://docs.pytorch.org/docs/2.8/generated/torch.nn.LSTM.html) and [reproducibility guidance](https://docs.pytorch.org/docs/2.8/notes/randomness.html). Seeding and deterministic settings improve repeatability but do not guarantee bit-identical training across framework versions, CPU and GPU.
