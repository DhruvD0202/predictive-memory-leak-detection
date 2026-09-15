# Preliminary Results evidence record

Checked: 15 September 2026. This checkpoint adds Section 7 only. No model, threshold, source result, evaluation interval or experimental protocol was changed.

## Sources and interpretation

| Draft element | Source | Check or qualification |
|---|---|---|
| Tables 5-6: complete test RMSE and MAE | `results/lstm_colab/metrics.csv` and all four `test_predictions.csv.gz` files | All 16 test model rows independently recalculated from saved predictions; every displayed value matches six-decimal rounding. The four methods share origins within each recording. |
| Relative RMSE reductions | Same complete test metric rows | Computed as `100 * (ARIMA RMSE - LSTM RMSE) / ARIMA RMSE`: 19.78%, 6.90%, 11.55%, 7.62%. These are relative error reductions, not detection accuracy. |
| Near-tied Antarex persistence/ARIMA | Metric rows plus `antarex_mono/frozen_settings.json` in `data/packages/review2_baseline_results_colab.zip` | RMSE difference rounds to 0.000196 percentage points. Selected ARIMA(3,1,0) coefficients are approximately -0.01121, -0.01024 and -0.01117. The explanation is an interpretation of this restricted fitted model. |
| Origin-label breakdown | `results/lstm_colab/antarex_mono/test_forecast_errors_by_leak_state.csv` | 1,933 leak-active and 29,099 other origins; target timestamps may fall outside the origin's injection state. Non-leak is not equivalent to healthy. |
| Figure 3: actual versus forecast | `results/lstm_colab/antarex_mono/first_test_30min.csv` | All 361 original rows and all four forecasting methods. The baseline-selected interval is unchanged. Horizontal axis uses target time; shading uses target-time labels. |
| Figure 4: learning curve | `results/lstm_colab/antarex_mono/training_history.csv` | Epoch 8 minimizes validation RMSE at 0.9819165357951384; epoch 12 completes four later non-improving epochs. Online training batches and fixed-weight validation have different evaluation conditions. |
| Table 7: point warnings | `results/warnings_colab/antarex_point_metrics.csv` | Test partition only. Undefined precision is retained for inactive rules. New false alarm starts and false-positive exposure are distinct. |
| Table 8: event outcomes | `results/warnings_colab/antarex_event_metrics.csv` | All 35 events eligible; trend detects 35 and LSTM assistance 34. Delay summaries include only detected events and do not establish pre-exhaustion lead time. |
| Figure 5: warning timeline | `results/warnings_colab/antarex_first_test_30min.csv` | Same 361 forecast origins as Figure 3; origin timestamps precede target timestamps by 60 seconds. Bands use saved Boolean decisions; all three warning rules are represented, with the always-off control omitted visually. |
| Westermo counts | `results/warnings_colab/westermo_descriptive_alarms.csv` | No alarms for systems 1-2; one trend-only observation/start on system 3. Unknown labels preclude false-alarm or detection claims. |
| Prototype functionality | `research/IMPLEMENTATION_VERIFICATION.md` and `results/verification/implementation_checks.json` | Existing 40-test result and 12 representative inference checks; not new tests in this drafting checkpoint or evidence of live detection accuracy. |

## Figure generation and preservation

The [figure builder](../scripts/build_results_figures.py) redraws three scientific charts directly from their original result tables using the existing `.venv-baseline` Matplotlib environment. It verifies all 56 forecasting and 20 warning files against the original manifests before plotting. The original figure files remain unchanged. No smoothing, interval reselection or model fitting occurs. PNG and editable SVG copies are stored in `paper/figures`; [results_figure_sources.json](figures/results_figure_sources.json) records input hashes and interval timestamps.

## Results-checkpoint verification

The checks below describe the original results-drafting checkpoint. The completed paper subsequently gained its remaining sections and ten additional IEEE/ACM references. Current page counts and citation checks are in `FINAL_DRAFT_CHECKS.md`; numeric citations in this record use the current manuscript numbering.

- Sections 1-6 and the 36-entry bibliography are unchanged apart from the cover's section range.
- Four new tables match the saved source records, including undefined precision/delays and the missed event.
- All 16 aggregate forecasting test rows were independently recalculated from the complete saved predictions within 1e-10 percentage points of the recorded values.
- At the results checkpoint, the PDF had 21 pages: Section 7 on pages 15-18 and references on pages 19-21. All eight tables and five figures retained their captions; new figure labels were checked for overlap and legibility. Subsequent sections move the references; the current page map is in `DRAFTING_NOTES.md`.
- All 36 works remain cited, with the PDF's 36 reference links matching the Markdown source.

No new external reference was added during the results checkpoint. Existing references [6], [41]-[44] support the already-audited dataset and evaluation concepts; all project numbers come from local experimental records. Single-seed scope, correlated windows, reused validation data, prior forecast-test inspection and unperformed extensions remain explicit. Current section status and later literature additions are recorded in `DRAFTING_NOTES.md`.
