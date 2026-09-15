# Review 2 progress

Last updated: 15 September 2026

## Confirmed decisions

- Review date: 16 September 2026.
- Compute target: Google Colab, free tier. GPU availability is not assumed.
- User-approved datasets: Antarex paired with Westermo.
- Workflow: validate data, review the architecture, then build preprocessing, baselines, LSTM, evaluation and visualizations incrementally. Draft the paper section by section using only completed experiments.
- The user completed preprocessing, baselines, four small multivariate LSTMs and initial warning evaluation in free Colab. All four stages' saved outputs have been independently verified. On 10 September, the warning-result archive reproduced all 402,364 decisions and 264 event outcomes, matching the local experiment. Paper drafting was then the remaining core milestone requirement; its required coverage is now present.
- On 13 September, the user paused the learning walkthrough and chose to finish the implementation while keeping paper drafting paused at that time.
- On 14 September, the user resumed paper drafting, specified no template or page limit, and requested updates and previews at each step. Sections 1-7, including the checked architecture and verified results, have been accepted for continued drafting. On 15 September, Limitations and Future Work was added with four subsections and a table that explicitly marks all extensions as pending. All 36 distinct references remain cited. Continue section by section; the learning walkthrough remains paused.

## Repository workflow

- GitHub repository: [DhruvD0202/predictive-memory-leak-detection](https://github.com/DhruvD0202/predictive-memory-leak-detection), private, with `main` as the default branch. The local remote was updated to this renamed repository on 12 September 2026.
- On 12 September, the user authorized ongoing repository updates during project work. For each agreed project step, make the necessary changes, run appropriate checks, commit the intended files with a meaningful message, and push them to GitHub without requesting permission again for routine updates.
- Check the working tree and remote changes before starting each step. Preserve collaborator edits, resolve conflicts before pushing, and do not force-push or overwrite shared history. Report any authentication or repository-rule blocker.
- Keep large datasets, generated data archives and local environments outside ordinary Git commits, following `.gitignore`. Data archives belong in separately maintained release assets.
- Continue the user's step-by-step workflow; this authorization does not schedule background work or skip review checkpoints. Paper drafting is now active.

## Milestone status

| Requirement for the 75% review | Evidence and status |
|---|---|
| Datasets identified and validated | Pilot data acquired and audited: complete Antarex CPU-MEM_mono block, selected required metric streams; all 19 Westermo CSVs. Limitations documented in DATA_VALIDATION.md. Antarex multi-core telemetry remains unacquired. |
| Working preprocessing, trained model and demonstrable results | Complete for the documented pilot and verified in free Colab: preprocessing, three forecasting baselines, four LSTMs, MAE/RMSE, initial warning precision/recall/F1, false alarms, event outcomes/delays and figures. |
| Research paper draft through supported preliminary results | Draft coverage complete for the requested milestone. Sections 1-7 accepted for continued drafting; Section 8 Limitations and Future Work added for review. Conclusion and Abstract/Keywords remain pending for the complete paper. |

The user's defined 75% review scope is now evidenced across all three requirements for the documented pilot. This is milestone coverage, not a measured percentage of all possible research work. Section 8 remains at the user-preview checkpoint; the full paper and broader evaluation are not complete.

## Runnable prototype — 13 September

The experimental implementation now has a local browser dashboard. Start it with `.\.venv-baseline\Scripts\python.exe app.py` from the project folder; see the [launch and demonstration guide](../README.md).

- Replay all 69,559 saved test forecast origins across four recordings, with playback controls, actual/forecast comparison, selectable warning rules, alarm history and CSV export. Observed values and labels stop at the cursor; future actual values are absent from the replay API.
- Execute each saved LSTM on demand using the matching 60-observation input history. The verified prepared arrays and trained weights are used; this is separate from archived prediction playback.
- View the full verified forecasting and warning metrics and saved learning curves.
- Collect local Windows/Linux telemetry on demand with a bounded session, CSV export and exploratory trend warnings. Linux-specific features are not invented on Windows; the archived LSTM is not applied to incompatible live features. Live detection accuracy and transfer to a new machine remain unvalidated.
- Startup validates 76 original result files. The complete 40-test suite passed; representative first/middle/last model predictions on all four recordings matched the saved results. See [implementation verification](IMPLEMENTATION_VERIFICATION.md).

This completes the monitoring/replay implementation checkpoint. Broader scientific evaluation, validated live LSTM transfer and the paper remain separate outstanding work. It does not establish 100% research completion or production readiness.

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

On 12 September, the professor's request for intermediate results was addressed with a [Review 2 demonstration guide](../reviews/Review2_Intermediate_Results.md). It assembles existing verified preparation counts, baseline errors, a learning curve, forecasts and warning outcomes, with source links and a suggested 6-8 minute demonstration. This is review material, not a new experiment or a drafted research-paper section.

The user's warning run is verified; see [COLAB_WARNING_VERIFICATION.md](COLAB_WARNING_VERIFICATION.md). No rerun or further notebook upload is needed for this checkpoint. Use the complete verified Colab forecasting and warning runs for paper tables and figures; preserve the earlier local experiments separately.

The verified Colab warning experiment gives trend-only F1 0.829670 versus LSTM-assisted F1 0.601469. LSTM-assisted precision is higher (0.847601 versus 0.802028), with fewer false alarm starts per non-leak hour (1.039211 versus 2.127908), but lower point recall. Trend-only detects 35/35 eligible test events and LSTM-assisted 34/35. These are recognition results after injection starts, not warnings before exhaustion. Westermo remains unlabeled and supports only descriptive alarm counts.

All 20 Colab warning-result files passed integrity checks; all 402,364 warning decisions and 264 event outcomes passed independent reconstruction. Verified archive: `data/packages/review2_warning_results_colab.zip`, SHA-256 `76b169d3807ce0fcd5577c6f20cb94d9d4b78c819cc0fecdc32f1df80bdd6fc5`. Its unchanged extracted files are in `results/warnings_colab`.

The [paper draft](../paper/Predictive_Memory_Leak_Detection_Draft.md) and [PDF preview](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf) now contain sections 1-8. Architecture remains on page 11, Experimental Setup on pages 12-14, and Preliminary Results and Discussion on pages 15-18. Limitations and Future Work occupies pages 19-20, documenting scope, validation independence, comparison limits, warning semantics and deployment requirements. Table 9 marks every proposed extension as pending. Earlier sections and results are unchanged; rendered pages 2-18 match the checked results PDF exactly. All 36 references remain cited on pages 21-23. Evidence maps and checkpoints are in [DRAFTING_NOTES.md](../paper/DRAFTING_NOTES.md).

Next, incorporate feedback on Limitations and Future Work, then draft Conclusion and finally Abstract/Keywords at separate checkpoints. The user-defined milestone draft coverage is present; repeated-seed studies, ablations, independent labeled evaluation, exhaustion outcomes and validated live deployment remain later research work.
