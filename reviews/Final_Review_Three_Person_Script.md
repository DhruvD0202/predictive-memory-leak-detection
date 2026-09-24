# Final review: three-person speaking guide

Project: **Predictive Memory Leak Detection Using Time Series Analysis**

Review: **16 September 2026**. Prepared: 15 September 2026.

Confirmed presentation time: **10-12 minutes, excluding questions**. Aim for 11 minutes, including the demonstration. Use Person 1, Person 2 and Person 3 as roles and assign your names during rehearsal. The person most comfortable operating the dashboard should take Person 3.

All claims and scores below come from the completed project and verified Colab outputs. Page numbers refer to the current 27-page manuscript with 46 references. Presentation time includes pointing to figures, explaining the displayed example and operating the dashboard; do not try to stretch the spoken paragraphs alone to fill each slot.

| Speaker | Time | Responsibility | What to show |
|---|---|---|---|
| Person 1 | 0:00-3:00 | Problem, research question, dataset choice and preprocessing | Project title; paper page 14, dataset table |
| Person 2 | 3:00-7:00 | Architecture, baselines, LSTM, training progress and forecasting results | Architecture page 13; forecasting table page 17; forecast and learning-curve figures page 18 |
| Person 3 | 7:00-11:00 | Warning evaluation, 90-second replay demo, limitations and conclusion | Warning table page 19; local dashboard |

## Person 1: why the project matters and how the data were prepared

**Your message:** We study whether forecasting memory growth improves warnings, using real telemetry with clear limits on its labels.

**Say:**

Good morning. Our project is titled Predictive Memory Leak Detection Using Time Series Analysis. A memory leak happens when a program retains allocated memory that it no longer needs. Over time, that can reduce available memory and affect performance. However, rising memory usage can also come from normal workload changes or caching, so a rise alone does not prove a leak.

Our main research question is: do better forecasts of future memory usage also give better leak warnings? We evaluate these separately. Earlier work already studies software aging, forecasting and leak detection. Our contribution is a reproducible comparison of forecasting models and warning rules on the selected datasets, supported by an experimental dashboard.

We selected Antarex because it contains real system measurements collected during controlled fault injection, including labeled memory-leak intervals. We paired it with Westermo, which contains industrial test-system measurements. We modeled one Antarex recording and three Westermo systems separately. Westermo has no confirmed leak labels, so it supports forecasting evaluation but cannot establish leak-detection accuracy.

Our target is one minus available memory divided by total RAM. It represents memory pressure in terms of availability, rather than the probability of a leak. We prepared the time-series measurements, derived rates from counters where appropriate, and excluded unusable constant features. Each recording was divided chronologically into 70 percent training, 15 percent validation and 15 percent testing. Scaling used training data only, and input windows do not cross split boundaries or data gaps.

Each prediction uses 60 past observations. Antarex is sampled every five seconds and forecasts 60 seconds ahead. Westermo is sampled every 30 seconds and forecasts five minutes ahead.

**Point to the dataset table:** Identify Antarex's labeled role and Westermo's unlabeled role. Explain that these are separate recordings, not one merged timeline. Pause briefly so the reviewer can read the horizons.

**Handoff:** With the data prepared, I will hand over to Person 2 to explain the forecasting models and their results.

## Person 2: how forecasting works and what it achieved

**Your message:** Simple benchmarks are essential, and the LSTM improves RMSE without being best on every measure.

**Say:**

The main experimental path in our architecture takes prepared telemetry, forms history windows, generates forecasts and passes those forecasts to the warning evaluator. The live-monitoring path is separate from this archived experiment. We compare four forecasting methods on matching test origins.

Persistence predicts that the future value will equal the latest observed value. Local linear trend projects recent growth forward. The restricted ARIMA baseline models patterns in changes to the memory series. These provide reference points for deciding whether a learned model adds value.

Our neural model has one LSTM layer with 32 hidden units and a linear output layer. It uses multiple telemetry features and is trained separately for each recording. We kept the configuration small enough for free Colab, and the saved experiments ran on CPU. This is a practical pilot configuration; we have not established that it is optimal.

Training used validation error to select the saved checkpoint. For Antarex, epoch eight was selected, and training stopped at epoch twelve after four epochs without a new validation improvement. The test set did not select the checkpoint.

On the Antarex test set, persistence and ARIMA both have RMSE of about 1.516 percentage points of total RAM. The LSTM reaches about 1.216, a 19.78 percent relative reduction in RMSE compared with ARIMA. This percentage describes error reduction, not leak-detection accuracy. RMSE gives greater weight to large prediction errors. For example, a prediction of 40 percent memory pressure when the measured value is 41 percent has an error of one percentage point.

The actual-versus-predicted chart illustrates where the model follows memory changes and where it misses abrupt changes. Each Antarex forecast uses observations ending 60 seconds before its target time. The table summarizes the complete test set, not just this displayed interval.

The LSTM has lower RMSE on all four recordings, but ARIMA has lower MAE on all three Westermo systems. Therefore, the LSTM's advantage depends on which error measure we consider.

**Point to the figures:** First identify actual memory and forecast curves. Point out an imperfectly predicted rise or fall, then show the selected epoch on the learning curve. Explain one example rather than reading every value in the tables.

**Handoff:** Better forecasting is only one part of the problem. Person 3 will explain whether it produced better warnings and demonstrate the system.

## Person 3: warning results, demonstration and conclusion

**Your message:** The LSTM-assisted rule is more selective, while the trend-only rule covers more of the labeled leak activity.

**Say before the demo:**

We evaluated warning behavior separately from forecast error. The trend-only rule checks recent observed memory growth. The forecast-assisted rules additionally require predicted growth. Each rule requires three consecutive qualifying observations, and its threshold was selected on validation data and frozen before test scoring.

Our main result is a trade-off. LSTM assistance increases precision and reduces false alarm starts from about 2.13 to 1.04 per observed non-leak hour. However, trend-only warnings have higher recall and F1. Trend-only recognizes all 35 eligible test events, while LSTM assistance recognizes 34. Recognizing an event at least once is different from warning throughout its duration.

I will now demonstrate these behaviors using the saved Antarex experiment.

**Run the 90-second demonstration below, using its short speaking lines.**

**Say after the demo:**

We have completed the experimental pipeline, saved models, forecasting and warning evaluation, the local prototype and the manuscript text with 46 references. Our strongest conclusion is that better forecast RMSE does not automatically mean better leak warnings. The preferred warning rule depends on the desired balance between coverage and false alarms.

These results concern controlled injected leaks in a single-seed pilot. We have not demonstrated warnings before memory exhaustion or prevention of crashes. Broader labeled evaluation, repeated seeds, ablations and validated live LSTM deployment remain future work. Thank you; we are ready for questions.

### Person 3's 90-second demonstration

Have the dashboard open before the review. Keep the saved chart available as a fallback. The main replay uses archived predictions; the separate model button performs fresh inference on archived inputs.

| Approximate time | Action | Say |
|---|---|---|
| 0-15 seconds | Open **Experiment replay**, select Antarex and choose **First injected leak**. | This is recorded telemetry from a controlled experiment. The injection label is ground truth from the dataset, separate from the warning produced by our rule. |
| 15-40 seconds | Choose **Play replay** at 120x, then pause during a rising-memory interval. | The replay reveals measured values as time advances. Forecasts can extend ahead of the cursor, but future measured values are not revealed early. |
| 40-65 seconds | Compare **Trend only** and **LSTM + trend**. Point to the warning bands. | These rules can issue different warnings from the same history. The full-test table quantifies their precision and coverage; this interval is an illustration. |
| 65-90 seconds | Choose **Run saved LSTM**, using the already prepared input package. | This runs the saved model on the matching 60-observation input and compares its output with the archived prediction. |

If the model check completes and reports a match, point to that result. If it does not complete promptly, return to the saved results and explain exactly what is available; do not claim an inference check passed unless the displayed result confirms it. Avoid waiting on a new training run during the presentation.

The live monitor is optional if the professor specifically asks for it. Explain that it collects this machine's telemetry and uses an exploratory trend rule; it does not apply the Antarex LSTM to incompatible Windows features. A live warning is not a confirmed leak. The core demonstration fits the time limit without a live-collection warm-up.

## Likely reviewer questions and who answers

| Owner | Question | Short, honest answer |
|---|---|---|
| Person 1 | Why these two datasets? | Antarex supplies controlled leak labels. Westermo adds industrial workload variation. We use each according to what its evidence supports. |
| Person 1 | Why chronological splits? | We want to forecast later observations from earlier ones. Chronological partitions preserve that direction and keep overlapping windows within their partitions. |
| Person 1 | What is new in this work? | Our contribution is the reproducible pilot comparison and the separate assessment of forecasting and warning trade-offs. We do not claim to have invented LSTM or telemetry-based leak detection. |
| Person 2 | Why are persistence and ARIMA almost tied? | In this fitted no-drift ARIMA configuration, predicted changes are small, so its forecasts stay close to the latest observed value. That finding does not apply to all ARIMA models. |
| Person 2 | Why 32 LSTM units? | It was a small fixed configuration suited to the free-Colab pilot. We used validation for checkpoint selection, but have not done a broad architecture search or repeated-seed study. |
| Person 2 | Is 19.78 percent the model's accuracy? | No. It is the relative reduction in Antarex test RMSE compared with ARIMA. RMSE measures forecast error in percentage points of total RAM. |
| Person 3 | If LSTM has lower F1, why use it? | It offers higher precision and fewer false alarm starts, at the cost of coverage. The experiment exposes that choice; it does not establish a universal winner. |
| Person 3 | How can it detect 34 of 35 events but have recall near 47 percent? | Event detection asks whether a new warning occurs inside an event. Point recall asks how many leak-active timestamps are warned on. Brief warnings can detect many events while covering less of their duration. |
| Person 3 | Why is ARIMA plus trend all zeros? | Every candidate in the fixed validation threshold grid produced no warnings, so the disabled option was selected. Precision is undefined. This is a result of that implemented warning rule and grid. |
| Person 3 | Does this predict crashes or detect real leaks on this laptop? | That is not validated. Our scored events are controlled Antarex injections, and no exhaustion outcome was observed. The laptop monitor is exploratory. |
| Any person | Did you implement Mann-Kendall or hybrid ARIMA-LSTM? | No. We discuss them in the literature and as possible extensions. The implemented predictors are persistence, local linear trend, restricted ARIMA and a separate LSTM. |

## Small results card to keep beside the laptop

| Antarex test measure | Reference method | LSTM or LSTM-assisted method |
|---|---:|---:|
| Forecast RMSE, percentage points of RAM | ARIMA: 1.5164 | LSTM: 1.2164 |
| Relative forecast RMSE reduction versus ARIMA | - | 19.78% |
| Warning precision | Trend: 0.8020 | LSTM + trend: 0.8476 |
| Warning point recall | Trend: 0.8593 | LSTM + trend: 0.4661 |
| Warning point F1 | Trend: 0.8297 | LSTM + trend: 0.6015 |
| False alarm starts per observed non-leak hour | Trend: 2.1279 | LSTM + trend: 1.0392 |
| Eligible events detected | Trend: 35/35 | LSTM + trend: 34/35 |

Non-leak exposure means time outside the labeled leak intervals; it can contain other injected faults. Reported detection delays are after injection onset and exclude missed events. No claim of statistical significance or pre-exhaustion lead time is made.

## Rehearse tonight

1. Assign names to the three roles. Each person should know the shared question, the two datasets and the main forecasting-versus-warning conclusion.
2. Open the paper and start the dashboard before timing the rehearsal. Keep one person operating the laptop throughout to reduce switching delays; Person 3 narrates the demo.
3. Rehearse once with a timer, including figure explanations, handoffs and the demo. Aim to switch at about minute 3 and minute 7 and finish around minute 11.
4. If you run over 12 minutes, omit the detailed epoch discussion and extra Westermo values, and shorten the replay. Retain the main warning trade-off and the scope statement.
5. Keep the PDF and saved figures available locally. No additional Colab training is needed to present the existing results.
6. Before submitting, check the author details on the final manuscript. The three names and registration numbers were added on 24 September 2026 in the user-supplied order; no affiliation was supplied.

## Local evidence and display files

- [Complete manuscript](../paper/Predictive_Memory_Leak_Detection_Draft.md) and [PDF](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf).
- [Architecture](../paper/figures/system_architecture_verified.png), [forecast comparison](../paper/figures/antarex_forecast_results.png), [learning curve](../paper/figures/antarex_training_results.png), [warning timeline](../paper/figures/antarex_warning_results.png).
- [Forecast metrics](../results/lstm_colab/metrics.csv), [point-warning metrics](../results/warnings_colab/antarex_point_metrics.csv), [event outcomes](../results/warnings_colab/antarex_event_metrics.csv).
- [Dashboard setup and controls](../README.md), [LSTM verification](../research/COLAB_LSTM_VERIFICATION.md), [warning verification](../research/COLAB_WARNING_VERIFICATION.md).

This guide was prepared from the saved records; preparing the script did not run a new demonstration or experiment.
