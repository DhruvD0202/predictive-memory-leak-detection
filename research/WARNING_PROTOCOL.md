# Forecast-assisted leak-warning protocol — 9 September 2026

Defined before computing warning scores or selecting thresholds. This is the next experimental stage; it reuses the complete verified Colab forecasts and does not train or tune forecasting models. Earlier forecasting test errors and example plots have already been inspected. The warning thresholds will use validation labels only, with a selection record written before warning test scores are calculated. This is a pilot development split, not a new external test set.

## Question and scope

Does adding an existing 60-second-ahead memory forecast to a recent-growth rule help recognize ongoing injected leaks in Antarex? Compare a trend-only warning, an ARIMA-assisted warning and an LSTM-assisted warning. Keep an always-off control to expose class imbalance and undefined precision. These rules indicate leak-like growth; they do not prove root cause.

The Antarex pilot has no observed 80% memory-pressure crossing. The target is recognition after leak injection starts, not prediction of randomly scheduled onset, time before exhaustion, or crash prevention. Westermo is a separate, unlabeled alarm-transfer illustration, with no leak precision/recall or false-alarm claims.

## Fixed input and architecture

Use `review2_preprocessed_colab.zip` (SHA-256 `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2`) and `review2_lstm_results_colab.zip` (SHA-256 `42cd2d51f29a06d2f6a0912a8b787d343898b11ac3ac55c4b397264743c1a7bf`). Retain both nested packages unchanged in a new warning-input bundle with a manifest. Use all existing validation/test forecast origins; no labels or future actual values enter a score.

At origin t, let y(t) be memory pressure as a fraction of total RAM. Fit a least-squares slope using the most recent **12 observations including t**. Convert it into percentage points of total RAM per minute, g(t). Antarex's observations are 5 seconds apart, so this history spans 55 seconds. No regression significance or Mann–Kendall p-value is claimed.

For forecast method m, let f_m(t) be its saved, clipped prediction at t+h. Define q_m(t) = 100 × (f_m(t) − y(t)) / (h/60), also in percentage points per minute.

- Trend-only score: g(t).
- ARIMA-assisted score: min(g(t), q_ARIMA(t)).
- LSTM-assisted score: min(g(t), q_LSTM(t)).
- Always-off: never warn; no fitted threshold.

Thus an assisted score exceeds a positive threshold only when both recent observed growth and forecast growth exceed it. A warning is active starting at the **third consecutive eligible origin** whose score is at least the threshold; it stops immediately when the condition fails. Three Antarex samples span 10 seconds from the first qualifying sample to the first warning. There is no retrospective filling, cooldown, hysteresis or merging of alarms. Reset consecutive counts at split boundaries and gaps. Resetting does not use event labels.

Warning timestamps are forecast **origins**, not target timestamps. Labels are consulted only by calibration and evaluation. Existing forecast-window eligibility excludes split edges and gaps, so coverage and event exclusions must be reported.

## Threshold selection

Independently for each of the three scoring rules, evaluate the fixed grid **0.01, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2** percentage points per minute, plus a disabled candidate. History length and consecutive count are fixed, not searched. Select the highest unadjusted, origin-level validation F1. Break ties by fewer false-positive origins and then the higher threshold (disabled sorts highest).

Save every candidate's validation confusion counts, precision, recall and F1. Freeze all selected thresholds, input hashes and settings before computing test warnings. No manual threshold changes or extra runs based on test results. This is supervised validation calibration, not an unsupervised end-to-end detector. The validation partition was also used for earlier forecast selection; this limits the independence of the development process.

## Antarex point metrics

Ground truth is whether injection is active at origin t, using the exact half-open interval [start, end). Report TP, FP, TN and FN; precision = TP/(TP+FP), recall = TP/(TP+FN), and F1 = 2TP/(2TP+FP+FN). Do not convert a whole leak interval into true positives when one warning occurs. Undefined ratios are saved as null/blank and shown as undefined; if leaks exist but no warnings occur, recall and F1 are zero and precision is undefined.

Also report warning fraction, non-leak false-positive fraction FP/(FP+TN), false-positive exposure minutes (FP × cadence / 60), and false alarm starts per observed non-leak hour. A new alarm starts when the warning changes from off to on, or starts after a coverage gap. A false alarm start occurs at a labeled non-leak origin. Non-leak exposure is the number of eligible non-leak origins × cadence; it includes other injected faults and is not synonymous with healthy operation. Coverage exposure is a discrete-cadence estimate, not full recording duration. Persistent alarms after a leak ends are penalized by false-positive origins even if no additional alarm starts occur.

## Event detection and delay

Evaluate each recorded leak separately. Include only events with complete eligible-origin coverage during the event and at least one covered sample immediately before onset. List all excluded events intersecting the scored interval and the reason (boundary or gap); ignore events entirely outside it.

Count an eligible event as detected only if a **new alarm starts inside [start, end)**. An alarm already active before onset does not earn a fresh event detection. Delay is the first such alarm-start timestamp minus the exact injection start. Report detected/eligible events, missed events, event recall, and median/90th-percentile delay **among detected events only**. Keep every event outcome in a table; missed events have no numerical delay. These sampled delays include up to one cadence of timing resolution and the rule's confirmation delay. Event recall and point precision are separate statistics and are not combined into an event F1.

## Westermo descriptive transfer

Apply the frozen Antarex thresholds unchanged to Westermo systems 1–3. Keep 12 past observations (spanning 330 seconds), a 300-second forecast horizon and three consecutive samples (60 seconds between first qualifying sample and warning). Express both scores in percentage points per minute as above. This is an exploratory transfer with different workloads and time scales, not a calibrated Westermo leak detector.

Report eligible origins, coverage hours, active-warning fraction, number of alarm starts and starts per observed hour. Labels remain unknown. Do not call an alarm false or infer a leak-free recording.

## Outputs and verification

Produce a self-contained CPU Colab notebook, validation candidate and frozen-threshold tables, origin-level warning timelines, confusion matrices, point metrics, event outcomes and delays, Westermo descriptive counts, provenance and a result ZIP with hashes. Plot the first 30 minutes of eligible Antarex test origins, not an interval selected for high performance. Show recorded injection separately from warning activity. Save plotting values and PNG/PDF figures.

Test causal indexing, current-versus-future label alignment, three-sample confirmation/gap resets, exact confusion counts including undefined precision, half-open event boundaries, boundary exclusions, no credit for pre-existing alarms, and selection invariance to test-value changes. Independently reconstruct saved confusion counts, event outcomes and warning states. Record offline execution time with its scope; this is not a measurement of end-to-end monitoring overhead.

## Methodological grounding and later work

Review 1 reference [13], [Jindal et al., Memory Leak Detection Algorithms in the Cloud-based Infrastructure (2021)](https://arxiv.org/abs/2106.08938), motivates using memory-growth trends as a comparator. This fixed slope/forecast conjunction is our pilot heuristic, not a reproduction of Precog. Review 1 reference [3], [Assi et al. (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), grounds the earlier statistical-versus-LSTM forecasting comparison.

[Kim et al., Towards a Rigorous Evaluation of Time-Series Anomaly Detection, AAAI 2022](https://doi.org/10.1609/aaai.v36i7.20680) identifies inflated scores caused by point adjustment. Accordingly this evaluation keeps original point decisions and reports separate event outcomes without filling detected events. This protocol does not implement that paper's complete benchmark or claim to reproduce its results.

An autocorrelation-aware Mann–Kendall experiment, hybrid ARIMA–LSTM, broader threshold/architecture studies, multiple seeds, uncertainty estimates, memory-exhaustion recordings, and deployment measurements remain later work. Neither a high F1 nor a low forecasting error on this controlled pilot establishes production reliability. Paper drafting follows this experimental checkpoint and uses only completed results.
