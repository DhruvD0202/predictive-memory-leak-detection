"""Build a portable notebook without requiring notebook tooling locally."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'src/preprocessing.py').read_text(encoding='utf-8')
embedded=source.split("\nif __name__ == '__main__':")[0]
cells=[]
def md(text):
    cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(keepends=True)})
def code(text):
    cells.append({'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],
                  'source':text.splitlines(keepends=True)})

md('''# Predictive Memory Leak Detection — 01: Preprocessing

**Review: 16 September 2026. Compute target: free Google Colab, CPU sufficient for this stage.**

This notebook prepares real Antarex and Westermo telemetry. It does **not** train a model or report forecasting accuracy. The next notebook will run the baseline experiment.

## Run in Colab
1. Open this notebook in [Google Colab](https://colab.research.google.com/) using **File → Upload notebook**.
2. Leave the runtime on CPU. Run the cells in order, or use **Runtime → Run all**.
3. When prompted, select `review2_pilot_raw.zip` (214 MB) from the delivered project. Upload only that ZIP. No extra source-code files are needed.
4. Wait for the four dataset summaries and integrity checks. The last cell downloads `review2_preprocessed.zip`; save it for the baseline stage. Colab runtime storage is temporary.

The raw ZIP expands to approximately 1.88 GB. The notebook reads only selected columns and saves window indices instead of allocating all overlapping input sequences at once. No GPU or paid plan is required by the implementation; actual free-tier availability remains subject to Colab.

## Scope and explicit defaults
- Antarex: selected RAM/CPU/page-fault/swap/disk streams from the recovered CPU-MEM_mono archive, five-second grid, 60 past observations (about five minutes), and a target 60 seconds ahead.
- Westermo: systems 1–3, selected in numerical order before model results; separate recordings at 30 seconds, 60 past observations (about 30 minutes), target five minutes ahead.
- Chronological 70%/15%/15% partitions. Windows never cross split boundaries or data gaps. Scaling and constant-feature removal use training rows only.
- The target is `1 - available_memory / total_memory`, an OS-level memory-pressure fraction. It is not process RSS.
- Antarex swap is unused and the monitored disk partition has constant counters. These features remain in the audit table and are removed from model inputs when constant in training.
- Westermo has no confirmed leak labels. It supports forecasting evaluation, not leak precision/recall.
- The audited Antarex recording does not reach 80% memory pressure. It cannot demonstrate lead time before memory exhaustion.

## Sources and methodological context
- [Antarex, Zenodo record 2553224](https://zenodo.org/records/2553224), CC BY 4.0. The selected nested archive was verified against ZIP member sizes/CRCs; the full 1.63 GB outer ZIP was not completely downloaded or MD5-verified. The delivered subset has its own verified SHA-256 manifest.
- [Westermo test-system-performance-dataset](https://github.com/westermo/test-system-performance-dataset/tree/47e0ccdc10c30e86327d6eb828ed48d164469fd4), CC BY 4.0. Source files were checked against the pinned Git objects.
- Review 1 reference [3], [Assi et al. (2022), Box–Jenkins and LSTM](https://doi.org/10.22075/ijnaa.2022.26974.3505), grounds the planned statistical-versus-LSTM comparison. Its performance figures are not our results.
- Review 1 reference [13], [Jindal et al. (2021)](https://arxiv.org/abs/2106.08938), grounds a later trend-based warning comparison. Mann–Kendall and hybrid models are not implemented here.
''')
md('''## 1. Select the working folder and raw ZIP
The upload stays in your own Colab runtime. The exact validated ZIP is checked before extraction in the processing cell.''')
code('''import importlib.util
from pathlib import Path

try:
    IN_COLAB = importlib.util.find_spec('google.colab') is not None
except ModuleNotFoundError:
    IN_COLAB = False

if IN_COLAB:
    WORK = Path('/content/memory_leak_project')
    RAW_PACKAGE = Path('/content/review2_pilot_raw.zip')
    if not RAW_PACKAGE.exists():
        from google.colab import files
        uploaded = files.upload()
        if 'review2_pilot_raw.zip' not in uploaded:
            raise FileNotFoundError('Select the supplied review2_pilot_raw.zip, then rerun this cell.')
        RAW_PACKAGE.write_bytes(uploaded['review2_pilot_raw.zip'])
        del uploaded
else:
    WORK = Path.cwd().resolve()
    if not (WORK/'data/packages/review2_pilot_raw.zip').exists() and (WORK.parent/'data/packages/review2_pilot_raw.zip').exists():
        WORK = WORK.parent
    RAW_PACKAGE = WORK/'data/packages/review2_pilot_raw.zip'
    if not RAW_PACKAGE.exists():
        raise FileNotFoundError('Run locally from the supplied project folder, or upload the notebook to Colab.')

SOURCE = WORK/'data/pilot_source'
OUTPUT = WORK/'data/processed'
PROCESSED_PACKAGE = WORK/'data/packages/review2_preprocessed.zip'
print('Environment:', 'Colab' if IN_COLAB else 'local Python')
print('Raw ZIP:', RAW_PACKAGE)
''')
md('''## 2. Load the preprocessing implementation
This cell contains the same implementation as `src/preprocessing.py`; no separate upload is necessary. Antarex joins use the most recent observation **at or before** each grid timestamp, with a maximum age of 2.1 seconds. Counters become rates using actual elapsed times; resets, stale observations and invalid values invalidate the affected sequences. Westermo rates are used directly. Missing Westermo samples are never filled.

Injection commands and fault labels are ground truth only. They are excluded from the explicit feature lists.''')
code(embedded)
md('''## 3. Verify the raw files and prepare the four recordings
This is the main processing cell. Existing extracted files are reused only if their hashes match. Outputs include readable feature tables, compact arrays, window indices, training-only scalers, feature units, leak intervals and summaries.''')
code('''source_folder = unpack_verified(RAW_PACKAGE, SOURCE)
summary = run(source_folder, OUTPUT)
print('Models trained:', summary['models_trained'])
print('Runtime versions:', summary['runtime'])
''')
md('''## 4. Review the actual processing counts
These counts describe model inputs, **not** model performance. Invalid rows remain visible in the feature tables and are excluded from model windows. Westermo labels stay unknown rather than being assigned a negative leak label.''')
code('''overview = pd.DataFrame([{
    'dataset': d['dataset'], 'grid_rows': d['grid_rows'],
    'valid_rows': d['valid_rows'], 'features': len(d['feature_names']),
    'train_windows': d['window_counts']['train'],
    'validation_windows': d['window_counts']['validation'],
    'test_windows': d['window_counts']['test'],
    'forecast_seconds': d['forecast_horizon_seconds'],
} for d in summary['datasets']])
display(overview)
for d in summary['datasets']:
    print(d['dataset'], 'removed training constants:', d['removed_training_constant_features'])
''')
md('''## 5. Reopen and check the saved model inputs
Verify every complete input-to-target interval, partition membership, training standardization, feature whitelist and unknown-label policy. Stop here if any assertion fails; do not train on unchecked outputs.''')
code('''checks = verify_outputs(OUTPUT)
display(pd.DataFrame(checks))
print('All saved-data integrity checks passed. No model was trained.')
''')
md('''## 6. Save the next stage's input package
The ZIP contains processed data and a per-file hash manifest. Its checksum can vary between fresh runs because compressed table headers contain creation times; per-run contents are checked before delivery. Antarex and Westermo remain in separate folders.

For a future forecast origin `o`, use feature rows `history_start_index` through `o`, inclusive; the regression target is the **unscaled** `target_memory_pressure[target_index]`. Labels are stored separately and must never enter the feature tensor. Use the supplied window partitions unchanged when comparing baselines and LSTM.''')
code('''receipt = package_outputs(OUTPUT, PROCESSED_PACKAGE)
print(receipt)
if IN_COLAB:
    from google.colab import files
    files.download(str(PROCESSED_PACKAGE))
''')
md('''## Checkpoint
After this notebook succeeds, dataset preparation is complete for the pilot. Trained baselines, LSTM, quantitative forecast/warning evaluation, scientific plots and the supported paper draft remain pending. The 75% milestone has not yet been reached.
''')

nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
    'language_info':{'name':'python','version':'3'},'colab':{'name':'01_preprocessing_colab.ipynb','provenance':[]},
    'preprocessing_source_sha256':hashlib.sha256(source.encode()).hexdigest()},'nbformat':4,'nbformat_minor':5}
for i,cell in enumerate(cells):
    cell['id']=f'preprocess-{i:02d}'
(ROOT/'notebooks').mkdir(exist_ok=True)
(ROOT/'notebooks/01_preprocessing_colab.ipynb').write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
print('Created notebooks/01_preprocessing_colab.ipynb')
