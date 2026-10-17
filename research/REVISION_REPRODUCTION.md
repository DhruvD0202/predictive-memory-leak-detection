# Reproduce the October seed/feature study

The revision adds 40 trained models on the same four recordings. It does not replace the original September results or add independent labels. Read `REVISION_PROTOCOL_20261016.md` before interpreting the results.

## Materials and access

- Code: `src/preprocessing.py`, `src/baselines.py`, `src/lstm_forecasting.py`, `src/warning_evaluation.py`; four ordered notebooks; dashboard source and tests.
- New execution: `scripts/run_revision_study.py`; independent audit: `scripts/verify_revision_study.py`.
- Diagnostic: `scripts/analyze_revision_evidence.py`; prototype measurement: `scripts/benchmark_revision_demo.py`; paper figure/table generation: `scripts/write_spin_results.py`.
- Recorded settings: `results/revision_20261016/protocol.json`, each run's `configuration.json`, `selected_model.json`, validation warning selection and training history. Selected weights are retained. The protocol specifies seeds 7, 21, 42, 84 and 123, both feature variants, and all selection rules.
- Results: per-run and summarized CSVs, `selection_freeze.json`, integrity report and checksummed full-result archive. Large per-origin forecasts, warning arrays and origin indices are kept in the separate archive rather than ordinary Git history. Last optimizer checkpoints are resumability aids, excluded from the result manifest; they are not needed to verify the selected weights.

The repository is private. The anonymous code supplement is a local handoff artifact, not a public release or a submission upload. Required input packages must be supplied separately. There is no claim that a fresh download of code alone contains the raw datasets. Public sources are [Antarex](https://zenodo.org/records/2553224) and [Westermo at the audited commit](https://github.com/westermo/test-system-performance-dataset/tree/47e0ccdc10c30e86327d6eb828ed48d164469fd4); both require CC BY 4.0 attribution.

## Environment

The completed run used Python 3.12.14, NumPy 2.3.5, pandas 3.0.1, Matplotlib 3.10.8 and PyTorch 2.8.0+cpu with two Torch threads. The benchmark used psutil 7.2.2. Runtime metadata is saved with each model. Different Torch versions/devices may change fitted weights even with the same seed.

From the project root, create a dedicated environment, then install:

```powershell
py -3.12 -m venv .venv-revision
.\.venv-revision\Scripts\python.exe -m pip install -r requirements-revision.txt
.\.venv-revision\Scripts\python.exe -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
```

## Required input

Place `review2_lstm_inputs.zip` in `data/packages/`. Expected SHA-256:

```
208c3b38ffbd7564e95f7452e0a3d203b1d4734858383e43cf602093ef7a1222
```

It contains the verified prepared package and original deterministic baseline results. Expected nested hashes are `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2` and `2b242a47288ea5db25ddd4d79de2069980ef1dc462fea157580e67ec19c01ba3`. Extraction checks archive membership, byte counts and hashes. Do not rename an arbitrary ZIP to pass it off as this input.

For a full rebuild from raw telemetry, run notebooks 01 through 04 with the input packages listed in the main README. The fixed-hash seed study intentionally consumes the audited preparation; a genuinely changed dataset needs a separately documented protocol and provenance.

## Train and independently verify

Use a new output directory so the completed study remains untouched:

```powershell
.\.venv-revision\Scripts\python.exe scripts/run_revision_study.py --output results/revision_reproduction
.\.venv-revision\Scripts\python.exe scripts/verify_revision_study.py --output results/revision_reproduction
```

The runner trains all 40 models before computing new test scores. Each model selects its checkpoint using validation RMSE; each Antarex warning selects its threshold using validation labels. The same completed directory can resume an interrupted training run with its optimizer checkpoints and matching environment/configuration. Do not alter a frozen protocol or reuse that directory for a different experiment. The audit recomputes metrics and warning/event decisions, checks identical forecast origins and verifies representative direct inference from every selected model. Its report is written under `results/revision_diagnostics/` and will describe the most recently audited run; preserve the supplied report before using that path for a new experiment.

To verify the **supplied** study rather than retrain, place the full-result ZIP and its JSON receipt in `data/packages/`, alongside the matching input package, then run:

```powershell
.\.venv-revision\Scripts\python.exe scripts/restore_revision_results.py
.\.venv-revision\Scripts\python.exe scripts/verify_revision_study.py
```

Restoration verifies the archive SHA-256, all file sizes/hashes and safe paths, refuses to overwrite different files, and unpacks the audited input package. A code-only supplement deliberately lacks the bulk per-origin files required for this option.

## Original diagnostics and prototype

```powershell
.\.venv-revision\Scripts\python.exe scripts/analyze_revision_evidence.py
.\.venv-revision\Scripts\python.exe scripts/benchmark_revision_demo.py --skip-live
.\.venv-revision\Scripts\python.exe -m unittest discover -s tests -v
```

The benchmark measures 100 replay/JSON requests and 101 first/warm inference requests per recording in one local process. It needs the prepared data recognized by the dashboard (see the main README); source result files are verified before use. Inference time excludes browser rendering and HTTP transport. RSS includes replay data, libraries and loaded models. Keep measurements separate from model accuracy.

The attempted live run on 16 October collected zero samples because Windows performance-counter access failed in the restricted environment. The user chose to document this limitation. Therefore the delivered manuscript reports **no successful live timing, CPU-overhead, natural-leak accuracy or exhaustion trial**. A future user-initiated run without `--skip-live` performs a bounded 36-sample collection without injecting a leak; even a successful collection would not establish detection accuracy.

## Interpretation

The matched ablation preserves the multivariate coverage mask, history and forecast horizon, so memory-only does not gain extra samples. Parameter count decreases when inputs are removed; this is not an equal-parameter ablation. Means/SD are across five training seeds on reused holdouts. The original Colab seed-42 scores remain separate. New results must not be presented as new-machine validation, causal feature importance or proof of pre-exhaustion warning.
