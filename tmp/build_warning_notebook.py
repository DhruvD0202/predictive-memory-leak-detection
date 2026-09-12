import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'src/warning_evaluation.py').read_text(encoding='utf-8')
protocol = (ROOT / 'research/WARNING_PROTOCOL.md').read_text(encoding='utf-8')
cells = []


def md(text):
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': text.splitlines(keepends=True)})


def code(text):
    cells.append({'cell_type': 'code', 'metadata': {}, 'source': text.splitlines(keepends=True), 'outputs': [], 'execution_count': None})


md('''# Predictive Memory Leak Detection — 04: Leak-warning evaluation

This notebook evaluates whether your saved forecasts support useful warnings about ongoing injected leaks. **It reuses your verified Colab results; it does not retrain the LSTM. CPU is sufficient.**

## What you need to do
1. Upload this notebook as a **separate notebook** in Colab.
2. Run the cells in order. At the upload prompt, select **`review2_warning_inputs.zip`**, approximately 31 MB. It already contains your verified preprocessed data and LSTM/baseline forecasts.
3. Let the evaluation finish. Inspect the point metrics, event outcomes and warning timeline. There is no requirement that LSTM outperform the simpler rules.
4. Confirm the final check says **`all_checks_passed: True`**.
5. Save the downloaded `review2_warning_results.zip` as **`review2_warning_results_colab.zip`** in the project's `data/packages` folder. Keep the executed notebook too.

## What is a warning?
At each origin, estimate memory growth from the most recent 12 observations. For an assisted rule, also calculate growth from the current value to the saved future forecast. Both must exceed the selected growth threshold for **three consecutive samples**. Compare:

- **Trend only:** recent growth alone.
- **ARIMA + trend:** recent growth and ARIMA forecast growth.
- **LSTM + trend:** recent growth and LSTM forecast growth.
- **Always off:** a control that produces no warnings.

All growth values use percentage points of total RAM per minute. On Antarex, 12 observations span 55 seconds, the forecast horizon is 60 seconds, and three consecutive qualifying observations span 10 seconds. These are fixed pilot settings, not tuned optima.

## How this is scored
Thresholds are selected by the highest **validation** F1 and frozen before scoring test warnings. A point is positive if an injected leak is active at the **warning origin**, not at the forecast target. No whole-event point adjustment is used. [Kim et al. (AAAI 2022)](https://doi.org/10.1609/aaai.v36i7.20680) motivates avoiding inflated scores from that adjustment.

- **Precision:** of warning-active samples, how many coincide with a recorded leak?
- **Recall:** of leak-active samples, how many receive a warning?
- **F1:** the precision/recall balance, derived directly from TP, FP and FN.
- **Event recall:** how many fully observed injected leaks contain a new alarm start?
- **Detection delay:** seconds from exact injection onset to the first new alarm during that leak, reported only for detected events; missed events remain listed.
- **False alarms:** false-positive samples and new alarms outside recorded leaks. These negatives include other injected faults.

An alarm already active before a leak begins does not earn a new event detection. Incomplete events are listed as excluded. Blank/NaN ratios mean **undefined**, not successful detection. For example, always-off precision is undefined while its recall and F1 are zero when leaks exist.

This measures recognition after an injection starts. The pilot contains no memory-exhaustion event, so it does not establish warning lead time before exhaustion. Westermo has no confirmed leak labels; its transferred alarms are descriptive only.

Review 1 reference [13], [Jindal et al. (2021)](https://arxiv.org/abs/2106.08938), grounds the use of memory trends as a comparator. This simple conjunction is our pilot rule, not a reimplementation of Precog. No Mann–Kendall significance result is claimed.
''')
md('''## 1. Prepare the CPU runtime
Only numerical, table and plotting libraries are needed. No GPU or model-training packages are required.''')
code('''from pathlib import Path
import importlib.util
import subprocess
import sys

missing=[name for name in ['numpy','pandas','matplotlib','PIL'] if importlib.util.find_spec(name) is None]
if missing:
    subprocess.check_call([sys.executable,'-m','pip','install','--quiet',*[('pillow' if x=='PIL' else x) for x in missing]])
print('Dependencies ready. This stage uses saved forecasts and does not retrain models.')
''')
md('''## 2. Upload the warning input ZIP
Select **`review2_warning_inputs.zip`**. The raw-data ZIP and model-training input ZIP are not the inputs for this stage. Download the result before Colab's temporary runtime storage disappears.''')
code('''try:
    IN_COLAB=importlib.util.find_spec('google.colab') is not None
except ModuleNotFoundError:
    IN_COLAB=False
if IN_COLAB:
    WORK=Path('/content/memory_leak_warnings')
    INPUT_PACKAGE=Path('/content/review2_warning_inputs.zip')
    if not INPUT_PACKAGE.exists():
        from google.colab import files
        uploaded=files.upload()
        if 'review2_warning_inputs.zip' not in uploaded:
            raise FileNotFoundError('Select review2_warning_inputs.zip, then rerun this cell.')
        INPUT_PACKAGE.write_bytes(uploaded['review2_warning_inputs.zip'])
        del uploaded
else:
    WORK=Path.cwd().resolve()
    if not (WORK/'data/packages/review2_warning_inputs.zip').exists() and (WORK.parent/'data/packages/review2_warning_inputs.zip').exists():
        WORK=WORK.parent
    INPUT_PACKAGE=WORK/'data/packages/review2_warning_inputs.zip'
SOURCE=WORK/'data/warning_inputs'
OUTPUT=WORK/'results/warnings'
RESULT_PACKAGE=WORK/'data/packages/review2_warning_results.zip'
print('Input:',INPUT_PACKAGE)
print('Result folder:',OUTPUT)
''')
md('''## 3. Load the complete evaluation code
No other source files need uploading. It includes safe ZIP verification, past-only score calculation, validation threshold selection, test metrics, event outcomes and plots. The project includes focused tests for timing, gap handling, undefined ratios and event boundaries.''')
code(source)
md('''## 4. Verify inputs and run the fixed experiment
The candidate thresholds are 0.01, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6 and 3.2 percentage points per minute, plus a disabled candidate. Each rule gets its own validation-selected threshold. Ties use fewer false-positive samples, then the higher threshold. A saved selection record is written before test-warning evaluation.

Leave these settings unchanged after viewing test results. A weaker result for the LSTM warning is still valid evidence, even if its forecasting RMSE was better.''')
code('''source_folder,input_receipt=unpack_inputs(INPUT_PACKAGE,SOURCE)
print('Input integrity checks passed:',input_receipt)
summary=run_experiment(source_folder,OUTPUT,input_receipt)
print('Runtime:',summary['runtime'])
print('Offline experiment elapsed seconds:',round(summary['elapsed_seconds'],2))
''')
md('''## 5. Review selected thresholds, classification scores and event delays
Precision/recall/F1 are fractions between 0 and 1. Event delay summaries cover **detected events only**, so always read them alongside detected and missed counts. The complete per-event table is included in the output ZIP.''')
code('''frozen=read_json(OUTPUT/'selection_freeze.json')
display(pd.DataFrame([{'method':LABELS[m],**v} for m,v in frozen['selected'].items()]))
point_results=pd.read_csv(OUTPUT/'antarex_point_metrics.csv')
event_results=pd.read_csv(OUTPUT/'antarex_event_metrics.csv')
display(point_results[point_results['split'].eq('test')][['method','tp','fp','tn','fn','precision','recall','f1','false_alarm_starts_per_non_leak_hour']])
display(event_results[event_results['split'].eq('test')][['method','eligible_events','detected_events','missed_events','excluded_events','event_recall','median_delay_seconds_detected_only','p90_delay_seconds_detected_only']])
print('NaN/blank ratios or delays mean undefined, not zero error or successful detection.')
''')
md('''## 6. Inspect the warning timeline and confusion matrices
The timeline uses the first 30 minutes of eligible test **origins**, fixed before seeing warning performance. Red shading marks recorded injection; colored bands mark actual rule outputs. An unmarked point is not retrospectively converted into a warning just because that event was detected elsewhere.''')
code('''from PIL import Image
for relative in ['antarex_warning_timeline.png','antarex_warning_comparison.png','antarex_confusion_matrices.png']:
    with Image.open(OUTPUT/relative) as picture:
        display(picture)
''')
md('''## 7. Inspect Westermo descriptive alarm transfer
These use the frozen Antarex thresholds without fitting Westermo labels. Westermo's 12 observations span 330 seconds, its forecast horizon is 300 seconds and three qualifying samples span 60 seconds. Workloads and time scales differ. These alarm counts have no confirmed true/false interpretation.''')
code('''display(pd.read_csv(OUTPUT/'westermo_descriptive_alarms.csv'))
print('Westermo leak precision/recall computed:',summary['westermo_leak_metrics_computed'])
''')
md('''## 8. Verify saved outputs and download the result ZIP
This reconstructs warning decisions, validation selection, confusion counts, event outcomes and the plotted values. Download the ZIP only after `all_checks_passed: True`.''')
code('''checks=verify_results(SOURCE,OUTPUT)
print(checks)
receipt=package_results(OUTPUT,RESULT_PACKAGE)
print(receipt)
if IN_COLAB:
    from google.colab import files
    files.download(str(RESULT_PACKAGE))
''')
md('''## Save-and-review checkpoint
Save the download as **`review2_warning_results_colab.zip`** in **`C:/dhruv/VIT/Sem-5/OS/Research_Project/data/packages/`** and keep the executed notebook. Tell the assistant once it is saved so it can verify your Colab output.

The next separate stage is drafting the paper from the verified data, forecasting results and warning results. Full evaluation, ablations, multiple seeds, memory-exhaustion studies and deployment remain later work. This notebook alone does not complete the 75% milestone because the paper draft is still pending.
''')
md('## Full frozen protocol\n\n' + protocol)
for i, cell in enumerate(cells):
    cell['id'] = f'warning-{i:02d}'
notebook = {'nbformat': 4, 'nbformat_minor': 5, 'cells': cells, 'metadata': {
    'kernelspec': {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'},
    'language_info': {'name': 'python'}, 'colab': {'name': '04_leak_warning_colab.ipynb', 'provenance': []},
    'warning_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'protocol_sha256': hashlib.sha256(protocol.encode()).hexdigest()}}
(ROOT / 'notebooks/04_leak_warning_colab.ipynb').write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding='utf-8')
print('Created notebooks/04_leak_warning_colab.ipynb')
