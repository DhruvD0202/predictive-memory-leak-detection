# Professor-requested revision protocol

Fixed on 16 October 2026 before the new training runs.

This revision addresses the professor's 23 comments. New runs supplement rather than replace the verified September Colab artifacts. They reuse the existing temporal holdouts, which have already been inspected, so they measure development-set sensitivity rather than independent external confirmation.

## Matched seed and feature study

- Recordings: Antarex mono and Westermo systems 1, 2 and 3, unchanged.
- Seeds: 7, 21, 42, 84, 123, all reported; no best-test-seed selection.
- Variants: original retained multivariate features; memory_pressure alone.
- Train each variant from scratch on the same local CPU/runtime. Do not pool September Colab seed 42 with the new local runs.
- Preserve the original train/validation/test partitions, all eligible forecast origins, training strides (12 Antarex, 4 Westermo), 60-observation histories, horizon and train-only scalers. The memory-only variant preserves the original coverage mask, preventing extra training/evaluation samples from confounding the feature comparison.
- Preserve one 32-unit LSTM, Adam 0.001, batch 64, gradient clipping 1.0, maximum 20 epochs and patience 4. Removing inputs also reduces parameter count, so the ablation compares feature configurations at fixed hidden width, not exactly equal parameter counts.
- Select every checkpoint with validation RMSE; freeze all selected weights before computing new test metrics. Use the existing nine-threshold grid plus disabled option to calibrate each new Antarex warning rule on validation labels. Freeze these choices before new warning test scores.
- Report each run, mean, sample standard deviation, min/max and paired seed differences. Report every seed's warning precision, recall, F1, false alarms, missed events and detected-event delay. Do not use seed variation as a confidence interval over new workloads.
- Persistence, linear trend and restricted ARIMA remain deterministic, memory-only comparisons on exactly the same test origins. The memory-only LSTM now matches their input variable; fitting procedures and training sample use still differ.
- No additional labeled recording is presumed available. Existing labels are controlled injection intervals, not independently confirmed production leaks or process-level allocation evidence.

## Other evidence

Inspect the original LSTM-missed test event from saved origin-level scores and evaluate whether its forecast-growth, observed-growth or confirmation conditions prevented an alarm. Do not invent a leak cause from aggregate telemetry.

Benchmark replay and saved-model inference on the current machine; perform a short, bounded live telemetry smoke test without intentionally exhausting RAM. Separate latency/resource measurements from detection validity. Existing software checks and a short live test cannot establish production overhead or leak-detection accuracy.

## Manuscript and format

Use the SPIN 2027 initial-submission requirements checked on 16 October: Springer single-column template, 8-15 pages, anonymized manuscript, no page numbers. Preserve the prior named two-column and single-column drafts. Shorten background, add a related-work comparison and a direct end-of-review gap paragraph, pseudocode, metric definitions, explicit contributions, and an item-by-item response record. Retain at least 30 relevant, supported references.

The current Springer guidance calls for a first-page AI-assistance note and a fuller disclosure. Describe the actual assistance without claiming that the authors have already endorsed this new revision. Author review remains required before submission. No AI-detector or plagiarism-system score is promised or fabricated.
