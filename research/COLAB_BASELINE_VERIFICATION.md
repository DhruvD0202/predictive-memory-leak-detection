# Colab baseline reproduction verified — 8 September 2026

The user completed the baseline notebook in Google Colab and saved `data/packages/review2_baseline_results_colab.zip`. Independent verification passed. No rerun is required for this checkpoint.

## Evidence checked

- All **32 result files** passed byte-size and SHA-256 checks against the archive manifest; there were no duplicate, missing or extra entries.
- The input package checksum matches the previously verified Colab preprocessing output.
- Every validation/test origin, target timestamp and actual memory value matches the prepared source data.
- **417,792 forecast values** were independently recomputed from the source memory series and saved model coefficients, including raw predictions and clipping.
- All **24 metric rows** were recomputed from the saved predictions. Forecast counts and clipping counts agree.
- Model choices, training segments and coefficients match the local reference run. Validation-based choices and the saved selection-freeze hashes agree.
- All four PNG figures decode successfully. The Antarex first-test-interval chart and error-comparison chart were also visually inspected.

The maximum absolute difference between local and Colab predictions is approximately **1.11 × 10⁻¹⁶** in memory-pressure fraction. The maximum difference across reported metric columns is approximately **2.22 × 10⁻¹⁶**. These are negligible floating-point differences and leave all reported rounded results unchanged.

Machine-readable evidence: [colab_baseline_verification.json](../results/verification/colab_baseline_verification.json). The source ZIP is retained unchanged.

## Execution provenance

Colab result ZIP SHA-256: `2b242a47288ea5db25ddd4d79de2069980ef1dc462fea157580e67ec19c01ba3`.

The Colab result records Python 3.13.15, NumPy 2.1.3, pandas 2.2.3, SciPy 1.16.3, statsmodels 0.14.6 and matplotlib 3.10.0. The local reference used different Python/array/plotting versions; both used statsmodels 0.14.6. Colab reported matplotlib 3.10.0 even though the setup cell requested 3.10.8. This discrepancy is recorded explicitly; the validated forecasts and metrics do not require a rerun to change the plotting version. File sizes and ZIP hashes need not be identical across these runs.

The Colab experiment summary records approximately 19.30 seconds for the experiment portion. It does not measure the entire notebook, package upload, dependency installation or deployment-monitoring overhead.

## Completed checkpoint and next stage

Dataset preparation and the statistical forecasting showcase are now reproduced in the user's free Colab environment. The measured conclusions remain those in [BASELINE_RESULTS.md](BASELINE_RESULTS.md): ARIMA and persistence are effectively tied on Antarex; ARIMA has lower forecast errors on the three Westermo pilot systems.

The next development stage is the proposed small multivariate LSTM, using the existing feature arrays, splits, forecast horizons and validation-based stopping. No LSTM training was performed during this verification. Leak-warning evaluation and the research-paper draft are still pending, so the overall 75% milestone is not complete.
