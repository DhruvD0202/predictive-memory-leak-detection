# Predictive Memory Leak Detection Using Time Series Analysis

A reproducible research prototype with a local dashboard, four Colab notebooks, saved forecasting models, verified preliminary leak-warning results and a complete manuscript draft of the documented pilot study.

## Final paper draft

The [editable draft](paper/Predictive_Memory_Leak_Detection_Draft.md) contains Abstract/Keywords, sections 1-9 and 46 distinct references, all cited in the text. Ten [IEEE/ACM additions](paper/REFERENCE_ADDITIONS.md) strengthen the Literature Survey. The checked [27-page PDF](output/pdf/Predictive_Memory_Leak_Detection_Draft.pdf) includes five figures, nine tables and section bookmarks. Abstract/Keywords is on page 1, Introduction on page 2, Literature Survey on pages 3-6, Research Gap and Problem Statement on pages 7-8, Methodology on pages 9-13, Experimental Setup on pages 14-16, Preliminary Results and Discussion on pages 17-20, Limitations and Future Work on pages 21-22, Conclusion on page 23, and references on pages 24-27.

View the [expanded Literature Survey](output/pdf/Literature_Survey_preview.png), [Abstract](output/pdf/Abstract_preview.png), [forecast figures](output/pdf/Forecast_Results_preview.png), [warning results](output/pdf/Warning_Results_preview.png) or [Conclusion](output/pdf/Conclusion_preview.png). The [final draft checks](paper/FINAL_DRAFT_CHECKS.md) summarize completion and validation. The manuscript includes Dhruv Dudeja (24BCE0968), Ayush Bhatt (24BDS0180) and Bs srivallabha (24BCE0457), in the supplied order. On 8 October, the draft/date label was removed and the Abstract, Introduction and Conclusion were edited for clarity; experimental findings remain unchanged. The [results evidence record](paper/RESULTS_EVIDENCE.md) links findings to complete Colab runs, including unfavorable outcomes. See [drafting notes](paper/DRAFTING_NOTES.md) and the [reference audit](paper/REFERENCE_AUDIT.md) for evidence maps and source verification. Unperformed studies remain explicitly marked as future work.

## Run the dashboard on the existing project computer

Open this project folder in VS Code, choose **Terminal > New Terminal**, then run:

```powershell
.\.venv-baseline\Scripts\python.exe app.py
```

The dashboard opens at **http://127.0.0.1:8765**. Keep the terminal open. Press **Ctrl+C** in that terminal to stop the server and any active telemetry session. Alternatively, run `./start_demo.ps1` if PowerShell allows local scripts.

If the port is occupied, use `app.py --port 8766`. Add `--no-browser` to start without opening a tab. The server binds only to this computer's loopback interface.

## What the application does

| View | Function |
|---|---|
| Experiment replay | Navigate every saved test origin in Antarex mono and Westermo 1-3. Play, pause, scrub, restart, jump before the first recorded leak, compare four forecasts, select a warning rule, inspect alarm starts and export the visible window. |
| Run saved LSTM | Execute the saved model on the exact 60-observation history at the replay cursor. Compare the fresh prediction with its archived Colab forecast. Requires the prepared input package. |
| Live monitor | Opt-in measurement of this computer's RAM, CPU, swap and disk rates every 5 seconds. Show recent memory growth, a 60-second linear forecast and exploratory growth warnings. Export the session. |
| Results & evidence | Full-test MAE/RMSE, warning precision/recall/F1, false-alarm rates, event outcomes, learning curves and saved figures. |

Replay checks the hashes and sizes of all 76 source result files at startup. It uses archived Colab predictions for responsive playback; the separate model button executes the weights on demand. Observed memory and injection shading stop at the replay cursor. Forecasts issued at or before that cursor may extend into the future. Future measured memory is never sent in a replay response.

The available test recordings contain 69,559 forecast origins in total. The warning rules and thresholds remain those selected in the original experiment. Selecting a rule in the dashboard does not recalibrate it.

## A short demonstration

1. Open **Experiment replay**. The initial view shows the first approximately 30 minutes of Antarex test data.
2. Choose **First injected leak**, then **Play replay** at 120x. This starts approximately one minute before the first recorded injection and reveals observations as playback advances.
3. Pause during a rising-memory interval. Compare **LSTM + trend** with **Trend only**. Recorded injection and predicted warnings are labeled separately.
4. Choose **Run saved LSTM**. A successful check reports a match within a tolerance of `1e-6` in memory-pressure fraction. The displayed request time can include imports and first model load; it is not a deployment benchmark.
5. Switch to a Westermo recording. Its leak labels remain unknown. Forecasts are available, while leak precision/recall is not claimed.
6. Open **Results & evidence** for full-test metrics, then **Live monitor** to collect this machine's measurements.
7. In live mode, allow about 55 seconds for 12 samples. Three qualifying estimates are required for a warning, so the earliest confirmed warning from a fresh session is about 65 seconds. Stop monitoring and export the CSV.

For the 16 September review, use the [three-person speaking guide](reviews/Final_Review_Three_Person_Script.md): an 11-minute split, speaking lines, a 90-second demo and likely reviewer questions. The [intermediate-results guide](reviews/Review2_Intermediate_Results.md) provides additional stage-by-stage evidence.

## Fresh clone setup

Python **3.11 or newer** is required for the dashboard. Python 3.12 is the locally tested version. Replay and its result tables use standard Python libraries; live monitoring adds psutil.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-app.txt
.\.venv\Scripts\python.exe app.py
```

For on-demand model inference, also install the forecasting dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lstm.txt
```

Restore `review2_preprocessed_colab.zip` from the saved Colab downloads or your data backup. This is the approximately 23 MB prepared package, not the raw dataset ZIP. Keep it under `data/packages/`, then run:

```powershell
.\.venv\Scripts\python.exe app.py --prepare data/packages/review2_preprocessed_colab.zip
```

The app checks the exact package SHA-256 `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2` before extracting to `data/demo_inputs/prepared`. On the existing computer, the previously verified `data/lstm_inputs/prepared` or `data/warning_inputs/prepared` directories are also recognized. Their arrays are checked before inference. A fresh clone can replay all saved results without the large raw-data archive.

## Live monitoring: method and boundaries

The live target is `1 - available_memory / total_memory`. CPU utilization is a system percentage. Disk throughput uses byte-counter differences over actual elapsed time. Linux system page faults are read from `/proc/vmstat`; unavailable Windows system page-fault metrics remain unknown. Missing metrics are never replaced with invented zeros.

The live rule fits a line to the last 12 memory measurements using actual sample times. Its slope is measured in percentage points of total RAM per minute. Three consecutive estimates meeting the chosen positive threshold produce a warning; failure of the condition clears it. Gaps longer than 2.5 sampling intervals reset the history. The default threshold is 0.8 pp/min, borrowed as an exploratory starting value from the Antarex trend rule. It has **not** been calibrated on this computer.

Live collection does not apply the Antarex LSTM: Windows does not provide all seven required Linux features with matching definitions. Collected data do not have confirmed leak labels. A memory-growth warning is not a confirmed leak, and no warning does not prove healthy operation. Persistence and linear forecasts are saved for later evaluation. Local-model training and labeled live validation require a separate experiment.

Sessions stop automatically after 720 samples (approximately one hour). CSV rows are flushed to disk as they arrive, under `results/live/<session>/telemetry.csv`; normal stop also writes `summary.json`. Local telemetry is excluded from Git. Closing a browser tab does not stop collection; use **Stop monitoring** or stop the server. The app does not allocate leak workloads, kill processes or change system settings.

Telemetry API reference: [psutil documentation](https://psutil.readthedocs.io/en/latest/).

## Reproduce the research pipeline

Run these self-contained notebooks in order using the corresponding saved input packages. Each downloads an output ZIP and integrity report; preserve the downloads outside the temporary Colab runtime.

| Stage | Notebook | Input ZIP |
|---|---|---|
| Preprocessing | [01_preprocessing_colab.ipynb](notebooks/01_preprocessing_colab.ipynb) | `review2_pilot_raw.zip` |
| Baselines | [02_baselines_colab.ipynb](notebooks/02_baselines_colab.ipynb) | `review2_preprocessed_colab.zip` |
| LSTM | [03_lstm_colab.ipynb](notebooks/03_lstm_colab.ipynb) | `review2_lstm_inputs.zip` |
| Warning evaluation | [04_leak_warning_colab.ipynb](notebooks/04_leak_warning_colab.ipynb) | `review2_warning_inputs.zip` |

Implementations are in `src/preprocessing.py`, `src/baselines.py`, `src/lstm_forecasting.py` and `src/warning_evaluation.py`. Protocols and provenance are documented in `research/`. The user's verified result directories are `results/lstm_colab` and `results/warnings_colab`; earlier local runs remain separate. The dashboard does not modify these experiment outputs.

## Verification

On the existing computer:

```powershell
.\.venv-baseline\Scripts\python.exe -m unittest discover -s tests -v
.\.venv-baseline\Scripts\python.exe scripts/verify_demo.py --model-checks
```

A new environment needs both `requirements-baselines.txt` and `requirements-lstm.txt` for the complete research test suite. The demo's tests alone can run with `python -m unittest discover -s tests -p test_demo.py -v`. Omit `--model-checks` to verify replay without PyTorch or prepared arrays.

The verification command checks source integrity, replay boundaries, unknown labels and, when requested, representative first/middle/last LSTM predictions on all four recordings. It writes `results/verification/implementation_checks.json`. These are implementation checks, not new scientific results or substitutes for the earlier complete prediction audits.

## Research status

The verified pilot shows lower LSTM RMSE than ARIMA on four recordings, while the trend-only warning rule has higher Antarex recall/F1 and the LSTM-assisted rule has higher precision with fewer false alarms. Antarex contains controlled injected leaks and no observed 80% memory-pressure crossing. Westermo is unlabeled. The current evidence does not establish warning before memory exhaustion, naturally occurring production-leak accuracy or production monitoring overhead.

The monitoring/replay prototype complements the existing experimental implementation. The full pilot-study manuscript text was completed on 15 September 2026 and finalized with the supplied authors on 24 September. The three user-defined requirements for the 75% review milestone are covered. Repeated seeds, broader labeled evaluation, feature ablations, new-machine LSTM validation and pre-exhaustion experiments remain further research work. See [project status](research/PROJECT_STATUS.md).

Dataset sources: [Antarex / Zenodo 2553224](https://zenodo.org/records/2553224), [Westermo at the audited commit](https://github.com/westermo/test-system-performance-dataset/tree/47e0ccdc10c30e86327d6eb828ed48d164469fd4). Both datasets are published under CC BY 4.0; retain their attribution and provenance when sharing data.
