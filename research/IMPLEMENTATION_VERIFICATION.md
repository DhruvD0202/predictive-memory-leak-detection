# Monitoring and replay implementation checkpoint

Date: 13 September 2026. The user requested completion of the implementation while keeping paper drafting paused. This document records software verification; it is not a paper section or a new scientific experiment.

## Delivered behavior

The local Python application serves three dashboard views: experiment replay, live monitoring, and results/evidence. The frontend uses local HTML, CSS and JavaScript without external assets or a frontend build service. Replay uses Python standard libraries; local telemetry uses psutil 7.2.2. On-demand inference reuses the existing PyTorch LSTM implementation.

Replay covers 31,032 Antarex test origins and 12,891 / 12,745 / 12,891 origins on Westermo systems 1 / 2 / 3: **69,559 origins** in total. It checks the 56 forecasting and 20 warning-result files against their original manifests. Neither the original models nor recorded predictions, thresholds, labels, metrics or figures were changed.

Playback uses saved forecasts. The separate **Run saved LSTM** action reloads the matching model and evaluates its 60 past observations. The two execution paths are labeled. The graph contains only observed values and recorded injection labels available up to the cursor, together with forecasts already issued. Future actual target values are excluded from replay responses and visible-window CSV exports.

## Automated verification

The complete command `python -m unittest discover -s tests -v` passed **40 tests** in the local environment. This includes the original 28 research integrity tests and 12 added implementation tests covering:

- Required warm-up, consecutive growth confirmation, immediate warning clearing and gap resets.
- Actual-time slope units, flat signals and invalid telemetry values.
- Unknown labels/metrics serialized as JSON null rather than fabricated negatives or zeros.
- Bounded live sessions, duplicate-start rejection, stop/export behavior and collector errors.
- All four replay recordings, boundary positions and invariance to future observed values.
- Export/display agreement, request limits, the static file allowlist and protection of local mutation endpoints.
- Rejection of changed source files.

The command `python scripts/verify_demo.py --model-checks` additionally exercised the first, middle and last test origin in each recording. All **12 saved-model predictions** matched their archived forecasts within `1e-6` in memory-pressure fraction. It also checked that future actual values are absent and Westermo labels remain unknown. All 76 original result files still passed integrity checks afterward.

Detailed results and measured local response-assembly timings: [implementation_checks.json](../results/verification/implementation_checks.json). Timings describe their stated local code paths and do not establish full production monitoring overhead. The representative model checks complement the earlier complete prediction audits; they do not replace them.

## Browser and real telemetry checks

The local dashboard was opened in a browser and the graph layout inspected. Its on-demand Antarex model action returned a forecast identical to the saved value at the checked cursor. Westermo replay displayed unknown leak labels and disabled navigation to injected events. The results page contained all 16 forecasting rows, all four warning rows, and successfully loaded the saved figures.

A real Windows monitoring session collected **55 samples**, passed through trend warm-up, displayed RAM/CPU/swap/disk readings, exported a CSV through the browser, and stopped successfully. System page faults were shown as unavailable. The session's source CSV and stop summary remain under the ignored `results/live/` directory. These unlabeled local observations were not used to calculate leak precision/recall, tune the historical thresholds or retrain any model.

## Practical limits

The live trend rule is exploratory. Its default 0.8 pp/min threshold is a borrowed starting point, not a threshold calibrated on this computer. It uses actual sample times and resets after gaps; it is documented separately from the frozen historical warning experiment.

The Antarex LSTM requires seven specific Linux features. Windows monitoring does not fabricate missing features or apply that model to a different input schema. The dashboard instead demonstrates trained-model inference on the corresponding recorded inputs, and persistence/linear forecasting on current local telemetry. Validated live LSTM deployment needs compatible collection, domain validation and possibly retraining.

Sessions require an explicit start, flush each sample to disk and stop after 720 samples or an explicit stop. Closing the browser does not stop collection. The server listens only on loopback; static resources are explicitly allowlisted, and mutation requests require the local token and an accepted origin/Host. This is a local research server, not a publicly hosted service.

The complete implementation can be demonstrated with [README.md](../README.md). Paper drafting and the learning walkthrough remain paused. Repeated-seed studies, ablations, broader labeled evaluation and memory-exhaustion outcomes remain research extensions.
