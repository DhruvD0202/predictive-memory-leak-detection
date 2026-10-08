# Review 2 progress

Last updated: 8 October 2026

## Confirmed decisions

- Review date: 16 September 2026.
- Compute target: Google Colab, free tier. GPU availability is not assumed.
- User-approved datasets: Antarex paired with Westermo.
- Workflow: validate data, review the architecture, then build preprocessing, baselines, LSTM, evaluation and visualizations incrementally. Draft the paper section by section using only completed experiments.
- The user completed preprocessing, baselines, four small multivariate LSTMs and initial warning evaluation in free Colab. All four stages' saved outputs have been independently verified. On 10 September, the warning-result archive reproduced all 402,364 decisions and 264 event outcomes, matching the local experiment. Paper drafting was then the remaining core milestone requirement; its required coverage is now present.
- On 13 September, the user paused the learning walkthrough and chose to finish the implementation while keeping paper drafting paused at that time.
- On 14 September, the user resumed paper drafting, specified no template or page limit, and requested updates and previews. On 15 September, the complete manuscript text was finished, followed by the user's request for more reputable IEEE/ACM references. The expanded draft includes Abstract/Keywords, sections 1-9, five figures, nine tables and 46 distinct references, all cited. Ten new IEEE/ACM works are integrated into the survey. The revised PDF has 27 pages. The author line was omitted at that checkpoint; the three supplied authors were added in the final draft on 24 September. The learning walkthrough remains paused.

## Repository workflow

- GitHub repository: [DhruvD0202/predictive-memory-leak-detection](https://github.com/DhruvD0202/predictive-memory-leak-detection), private, with `main` as the default branch. The local remote was updated to this renamed repository on 12 September 2026.
- On 12 September, the user authorized ongoing repository updates during project work. For each agreed project step, make the necessary changes, run appropriate checks, commit the intended files with a meaningful message, and push them to GitHub without requesting permission again for routine updates.
- Check the working tree and remote changes before starting each step. Preserve collaborator edits, resolve conflicts before pushing, and do not force-push or overwrite shared history. Report any authentication or repository-rule blocker.
- Keep large datasets, generated data archives and local environments outside ordinary Git commits, following `.gitignore`. Data archives belong in separately maintained release assets.
- Continue the user's requested workflow; this authorization does not schedule background work. The latest request authorized finishing the full paper draft with progress updates and previews.

## Milestone status

| Requirement for the 75% review | Evidence and status |
|---|---|
| Datasets identified and validated | Pilot data acquired and audited: complete Antarex CPU-MEM_mono block, selected required metric streams; all 19 Westermo CSVs. Limitations documented in DATA_VALIDATION.md. Antarex multi-core telemetry remains unacquired. |
| Working preprocessing, trained model and demonstrable results | Complete for the documented pilot and verified in free Colab: preprocessing, three forecasting baselines, four LSTMs, MAE/RMSE, initial warning precision/recall/F1, false alarms, event outcomes/delays and figures. |
| Research paper draft through supported preliminary results | Final draft available: Abstract/Keywords, sections 1-9, verified results, architecture and 46 references. The three supplied authors and registration numbers were added on 24 September. Unperformed research is explicitly marked as future work. |

The user's defined 75% review scope is evidenced across all three requirements for the documented pilot. All manuscript sections are now drafted and checked. This is completion of the draft content and milestone coverage, not a measured percentage of all possible research work; broader evaluation remains future work.

## Runnable prototype — 13 September

The experimental implementation now has a local browser dashboard. Start it with `.\.venv-baseline\Scripts\python.exe app.py` from the project folder; see the [launch and demonstration guide](../README.md).

- Replay all 69,559 saved test forecast origins across four recordings, with playback controls, actual/forecast comparison, selectable warning rules, alarm history and CSV export. Observed values and labels stop at the cursor; future actual values are absent from the replay API.
- Execute each saved LSTM on demand using the matching 60-observation input history. The verified prepared arrays and trained weights are used; this is separate from archived prediction playback.
- View the full verified forecasting and warning metrics and saved learning curves.
- Collect local Windows/Linux telemetry on demand with a bounded session, CSV export and exploratory trend warnings. Linux-specific features are not invented on Windows; the archived LSTM is not applied to incompatible live features. Live detection accuracy and transfer to a new machine remain unvalidated.
- Startup validates 76 original result files. The complete 40-test suite passed; representative first/middle/last model predictions on all four recordings matched the saved results. See [implementation verification](IMPLEMENTATION_VERIFICATION.md).

This completes the monitoring/replay implementation checkpoint. The paper text was subsequently completed on 15 September. Broader scientific evaluation and validated live LSTM transfer remain outstanding research work. Neither the prototype nor the completed draft establishes 100% research completion or production readiness.

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

## Review handoff

For the user's final review on 16 September, the confirmed presentation slot is 10-12 minutes excluding questions. The [three-person speaking guide](../reviews/Final_Review_Three_Person_Script.md) targets 11 minutes: Person 1 handles the problem/data/preprocessing, Person 2 handles models and forecasting results, and Person 3 handles warnings, the replay demo and the conclusion. It includes handoffs, a 90-second demo, a results card and reviewer questions. Preparing this guide did not run a new experiment or demonstration.

On 12 September, the professor's request for intermediate results was addressed with a [Review 2 demonstration guide](../reviews/Review2_Intermediate_Results.md). It assembles existing verified preparation counts, baseline errors, a learning curve, forecasts and warning outcomes, with source links and a suggested 6-8 minute demonstration. This is review material, not a new experiment or a drafted research-paper section.

The user's warning run is verified; see [COLAB_WARNING_VERIFICATION.md](COLAB_WARNING_VERIFICATION.md). No rerun or further notebook upload is needed for this checkpoint. Use the complete verified Colab forecasting and warning runs for paper tables and figures; preserve the earlier local experiments separately.

The verified Colab warning experiment gives trend-only F1 0.829670 versus LSTM-assisted F1 0.601469. LSTM-assisted precision is higher (0.847601 versus 0.802028), with fewer false alarm starts per non-leak hour (1.039211 versus 2.127908), but lower point recall. Trend-only detects 35/35 eligible test events and LSTM-assisted 34/35. These are recognition results after injection starts, not warnings before exhaustion. Westermo remains unlabeled and supports only descriptive alarm counts.

All 20 Colab warning-result files passed integrity checks; all 402,364 warning decisions and 264 event outcomes passed independent reconstruction. Verified archive: `data/packages/review2_warning_results_colab.zip`, SHA-256 `76b169d3807ce0fcd5577c6f20cb94d9d4b78c819cc0fecdc32f1df80bdd6fc5`. Its unchanged extracted files are in `results/warnings_colab`.

The [complete paper draft](../paper/Predictive_Memory_Leak_Detection_Draft.md) and [27-page PDF](../output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf) contain Abstract/Keywords and sections 1-9. The expanded Literature Survey is on pages 3-6, Architecture on page 13, Experimental Setup on pages 14-16, Preliminary Results and Discussion on pages 17-20, Limitations and Future Work on pages 21-22, Conclusion on page 23, and the 46 cited references on pages 24-27. Table 9 marks all proposed extensions as pending. The [ten additions](../paper/REFERENCE_ADDITIONS.md) comprise six IEEE-published and four ACM-published works; Google Scholar access was unavailable and is not claimed as a completed search. The literature update preserves all experimental findings and original result files. See [final draft checks](../paper/FINAL_DRAFT_CHECKS.md) and [drafting notes](../paper/DRAFTING_NOTES.md).

On 24 September, the user supplied Dhruv Dudeja (24BCE0968), Ayush Bhatt (24BDS0180) and Bs srivallabha (24BCE0457), in that order, and requested the final draft. Those exact names and registration numbers appear on the first page and in PDF author metadata. That subtitle and its matching page-footer text were removed on 8 October at the user's request; page numbers remain. Affiliation was not supplied and is omitted. No new notebook run is required to support the reported pilot results. Repeated-seed studies, ablations, independent labeled evaluation, exhaustion outcomes and validated live deployment remain later research work, as stated in the final draft.


## Journal preparation - 8 October

The user intends to submit to a college journal and reported no template or AI-use policy when asked. The current PDF omits the draft/date label on every page and retains page numbering and the exact supplied authors. A focused clarity edit revised the Abstract, Introduction and Conclusion, plus review-milestone wording in Sections 7.5 and 8.4. The 27-page manuscript retains all 46 references, five figures, nine tables and experimental findings. No AI-detector score was measured or promised, no manuscript was uploaded to an external checker, and journal-specific compliance or acceptance is not established. See the 8 October checks in [FINAL_DRAFT_CHECKS.md](../paper/FINAL_DRAFT_CHECKS.md).
