# Architecture design review

Reviewed: 15 September 2026.

The user supplied an architecture screenshot and asked for correctness checking before inclusion in the paper. The screenshot was checked against the actual preprocessing, baseline, LSTM, warning and demo implementations. Its overall component groups are useful, but several labels and connections required correction. The original is preserved as [architecture_user_original.png](figures/architecture_user_original.png). The reviewed revision is [system_architecture_verified.png](figures/system_architecture_verified.png), now Figure 2 in the draft. Figure 1 remains the simpler pipeline overview.

| Original element | Correction in the paper architecture | Implementation evidence |
|---|---|---|
| Live psutil input enters the same scaling/windowing/model chain | Separate archived-experiment and exploratory-live panels; no live connection to saved LSTM models | `src/demo_service.py`: `ReplayRepository`, archived model inference, `GrowthDetector`, `LiveMonitor` |
| MinMax / Z-score scaling | Training-only z-score scaling after chronological partitioning | `src/preprocessing.py`: `partition_codes`, `fit_scaler`, `export_dataset` |
| Generic memory, CPU, disk and page-fault inputs | Recording-specific features; no fabricated Westermo page faults or informative Antarex disk/swap claim | Preprocessing feature dictionaries and `results/lstm_colab/*/configuration.json` |
| 60 steps always means five minutes | 60 observations; actual history spans are 295 seconds for Antarex and 1,770 seconds for Westermo, stated in Section 6 | Saved preprocessing summaries |
| Three forecast model boxes | Four predictors: persistence, local linear trend, restricted ARIMA and LSTM | `src/baselines.py`, `src/lstm_forecasting.py` |
| Generic ARIMA | ARIMA(p,1,0), no drift | `src/baselines.py`: `fit_arima` |
| 60-second forecasts for every source | Antarex 60 seconds; Westermo 300 seconds | Saved horizon configuration |
| Three warning rules | Preserve trend-only, ARIMA-assisted and LSTM-assisted rules; add always-off control | `src/warning_evaluation.py` |
| Three samples in a row | Retain three consecutive qualifying samples; text in Section 5 specifies gaps and split resets | `warning_state`; live `GrowthDetector.update` |
| Precision/recall/F1 as generic system outputs | Antarex labeled metrics only; Westermo descriptive counts; separate MAE/RMSE path | `point_metrics`, `event_metrics`, `describe_unlabeled` |
| Alarm means “Leak Detected!” | Exploratory or leak-like-growth warning; no root-cause confirmation | Warning protocol and live monitor semantics |
| Dense dark screenshot and literal newline escapes | Print-oriented white background, readable text and actual line breaks | Visual review of the revised figure and paper rendering |

The revised warning branch takes both observed history and forecast outputs. Only ARIMA and LSTM forecasts are used by the assisted rules; the specific rule labels and figure caption clarify this. Validation labels calibrate Antarex thresholds, and test labels score warnings; labels are not predictor inputs. The diagram is a high-level architecture, so window validity rules, threshold grids and event definitions remain in Section 5.

The built-in image-generation tool revised the supplied bitmap. An initial revision incorrectly routed forecast-error evaluation into warning metrics; a second edit corrected that connection before paper inclusion. The final image's words and arrows were visually reviewed against the implementation. Original and revised files are preserved separately; no experiment or application code was changed. The [saved edit prompts](figures/architecture_edit_prompts.txt) document the two built-in edits.
