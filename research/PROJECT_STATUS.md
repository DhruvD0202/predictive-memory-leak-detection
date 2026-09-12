# Review 2 progress

Last updated: 12 September 2026

## Confirmed decisions

- Review date: 16 September 2026.
- Compute target: Google Colab, free tier. GPU availability is not assumed.
- User-approved datasets: Antarex paired with Westermo.
- Workflow: validate data, review the architecture, then build preprocessing, baselines, LSTM, evaluation and visualizations incrementally. Draft the paper section by section using only completed experiments.
- The user completed preprocessing, baselines, four small multivariate LSTMs and initial warning evaluation in free Colab. All four stages' saved outputs have been independently verified. On 10 September, the warning-result archive reproduced all 402,364 decisions and 264 event outcomes, matching the local experiment. The research-paper draft is the remaining core milestone requirement.

## Repository workflow

- GitHub repository: [DhruvD0202/predictive-memory-leak-detection](https://github.com/DhruvD0202/predictive-memory-leak-detection), private, with `main` as the default branch. The local remote was updated to this renamed repository on 12 September 2026.
- On 12 September, the user authorized ongoing repository updates during project work. For each agreed project step, make the necessary changes, run appropriate checks, commit the intended files with a meaningful message, and push them to GitHub without requesting permission again for routine updates.
- Check the working tree and remote changes before starting each step. Preserve collaborator edits, resolve conflicts before pushing, and do not force-push or overwrite shared history. Report any authentication or repository-rule blocker.
- Keep large datasets, generated data archives and local environments outside ordinary Git commits, following `.gitignore`. Data archives belong in separately maintained release assets.
- Continue the user's step-by-step workflow; this authorization does not schedule background work or skip review checkpoints. Paper drafting remains the next research step.

## Milestone status

| Requirement for the 75% review | Evidence and status |
|---|---|
| Datasets identified and validated | Pilot data acquired and audited: complete Antarex CPU-MEM_mono block, selected required metric streams; all 19 Westermo CSVs. Limitations documented in DATA_VALIDATION.md. Antarex multi-core telemetry remains unacquired. |
| Working preprocessing, trained model and demonstrable results | Complete for the documented pilot and verified in free Colab: preprocessing, three forecasting baselines, four LSTMs, MAE/RMSE, initial warning precision/recall/F1, false alarms, event outcomes/delays and figures. |
| Research paper draft through supported preliminary results | Pending. Review 1 is the starting material; verified Colab forecasting and warning scores/figures are available for supported preliminary-results drafting. No new paper sections have been written. |

No overall percentage is assigned: the three requirements have no agreed weighting, and data preparation alone does not establish 75% completion.

## Proposed working schedule

These are planning targets, not scheduled automated actions or promises of future autonomous work.

| Date | Target |
|---|---|
| 7 September | Dataset validation and architecture review |
| 8 September | Colab preprocessing notebook and documented feature/label mapping |
| 9 September | Persistence and statistical baseline; first actual-versus-predicted chart |
| 10-11 September | Small LSTM and fair comparison on the same chronological splits |
| 12 September | Warning evaluation, timing measurements, figures and saved outputs |
| 13-14 September | Draft paper sections supported by the executed experiments |
| 15 September | Reproduction check, review presentation material and contingency buffer |
| 16 September | Review |

## Initial defaults used for preprocessing

- Start with Antarex CPU-MEM_mono; keep multi-core expansion for later validation.
- Use Westermo as a separate workload-forecasting experiment, initially systems 1-3 in numerical order. Do not concatenate the two sources or manufacture a joint multivariate timeline.
- Antarex: 5-second samples, 60 past observations (approximately 5 minutes), 60-second forecast horizon. Westermo: 30-second samples, 60 observations, 5-minute forecast horizon. These are initial defaults, not tuned optima.
- Distinguish forecasting and leak detection from pre-exhaustion warning: the audited Antarex block has no memory-pressure threshold crossing at 80%, inactive swap and constant monitored disk counters.

## Next checkpoint

The user's warning run is verified; see [COLAB_WARNING_VERIFICATION.md](COLAB_WARNING_VERIFICATION.md). No rerun or further notebook upload is needed for this checkpoint. Use the complete verified Colab forecasting and warning runs for paper tables and figures; preserve the earlier local experiments separately.

The verified Colab warning experiment gives trend-only F1 0.829670 versus LSTM-assisted F1 0.601469. LSTM-assisted precision is higher (0.847601 versus 0.802028), with fewer false alarm starts per non-leak hour (1.039211 versus 2.127908), but lower point recall. Trend-only detects 35/35 eligible test events and LSTM-assisted 34/35. These are recognition results after injection starts, not warnings before exhaustion. Westermo remains unlabeled and supports only descriptive alarm counts.

All 20 Colab warning-result files passed integrity checks; all 402,364 warning decisions and 264 event outcomes passed independent reconstruction. Verified archive: `data/packages/review2_warning_results_colab.zip`, SHA-256 `76b169d3807ce0fcd5577c6f20cb94d9d4b78c819cc0fecdc32f1df80bdd6fc5`. Its unchanged extracted files are in `results/warnings_colab`.

Next, draft the paper section by section, starting with the Introduction. Confirm any required college template or page limit; otherwise use a conventional academic research-paper structure with numbered citations. The 75% milestone remains incomplete because the paper draft is pending; broader evaluation and deployment are later work.
