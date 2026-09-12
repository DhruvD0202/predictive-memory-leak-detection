import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'src/lstm_forecasting.py').read_text(encoding='utf-8')
protocol=(ROOT/'research/LSTM_PROTOCOL.md').read_text(encoding='utf-8')
cells=[]
def md(value): cells.append({'cell_type':'markdown','metadata':{},'source':value.splitlines(keepends=True)})
def code(value): cells.append({'cell_type':'code','metadata':{},'source':value.splitlines(keepends=True),'outputs':[],'execution_count':None})

md('''# Predictive Memory Leak Detection — 03: Multivariate LSTM

This notebook trains one small LSTM per recording and compares it with your verified statistical baselines. It uses real measured results; it does not assume that LSTM will win.

## What to do
1. Upload **this notebook** to Colab. CPU works; an available GPU is also supported. No paid runtime is required by the code.
2. Run the cells in order. When prompted, upload **`review2_lstm_inputs.zip`**, approximately 29 MB. This new package already contains your prepared data and baseline results, so there is only one upload.
3. The notebook trains four models and prints progress after each epoch. Let the training cell finish before running the result cells.
4. Review the measured scores, charts and final integrity message.
5. Save the downloaded **`review2_lstm_results.zip`** as `review2_lstm_results_colab.zip` in your project's `data/packages` folder. Also retain a copy of the executed notebook.

## Architecture and fixed pilot choices
**60 past observations × available system features → one 32-unit LSTM → one linear output → future memory pressure.** The hidden state resets for every input window. The inputs contain no fault labels or future data.

- Seven input features for Antarex and Westermo 2; eight for Westermo 1/3. Each recording has its own model.
- The exact existing time splits and prediction horizons remain: 60 seconds for Antarex; five minutes for Westermo.
- Seed 42, Adam learning rate 0.001, batches of 64, gradient clipping at norm 1, maximum 20 epochs.
- Training uses every 12th Antarex window and every 4th Westermo window to limit CPU cost. Full validation and test windows are retained.
- Select the lowest validation-RMSE checkpoint; stop after four epochs without a new minimum. All models finish selection before test scoring.
- Targets use the existing training-only memory-pressure scaler. Score forecasts after reversing scaling and applying the same [0,1] clipping rule as the baselines.
- No test-driven parameter search, residual shortcut, dropout or additional hidden layers are used in this initial run.

The small model, spacing and one-seed run are a declared pilot scope, not a tuned optimum or a full robustness study. GPU and CPU results need not be bit-identical even with fixed seeds; each run saves its versions, weights and predictions.

## References
Review 1 reference [3], [Assi et al. (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), motivates the statistical/LSTM comparison. Implementation follows the primary [PyTorch LSTM documentation](https://docs.pytorch.org/docs/2.8/generated/torch.nn.LSTM.html) and [reproducibility guidance](https://docs.pytorch.org/docs/2.8/notes/randomness.html). All experiment numbers below come from this notebook's execution.
''')
md('''## 1. Prepare the runtime
The notebook uses Colab's available PyTorch installation, including GPU support when present. If PyTorch is missing, a CPU version is installed. Existing plotting/numerical packages are retained and their loaded versions are recorded.''')
code('''import importlib.util
from pathlib import Path
import subprocess
import sys

if importlib.util.find_spec('torch') is None:
    subprocess.check_call([sys.executable,'-m','pip','install','--quiet','torch==2.8.0',
                           '--index-url','https://download.pytorch.org/whl/cpu'])
missing=[name for name in ['numpy','pandas','matplotlib','PIL'] if importlib.util.find_spec(name) is None]
if missing:
    packages=[('pillow' if name=='PIL' else name) for name in missing]
    subprocess.check_call([sys.executable,'-m','pip','install','--quiet',*packages])
print('Dependencies are ready.')
''')
md('''## 2. Upload the LSTM input package and choose checkpoint storage
Leave the optional Drive setting off for a straightforward run. Checkpoints are saved after every epoch; rerunning in the same runtime resumes them. **To retain checkpoints across Colab runtime resets**, enable the Drive option before training and authorize your own Drive connection. Otherwise, download the final results before the runtime ends. Changing devices/framework versions midway through a resumed run requires a separate output folder or the original configuration.''')
code('''USE_GOOGLE_DRIVE = False #@param {type:"boolean"}

try:
    IN_COLAB=importlib.util.find_spec('google.colab') is not None
except ModuleNotFoundError:
    IN_COLAB=False
if IN_COLAB:
    WORK=Path('/content/memory_leak_lstm')
    INPUT_PACKAGE=Path('/content/review2_lstm_inputs.zip')
    if not INPUT_PACKAGE.exists():
        from google.colab import files
        uploaded=files.upload()
        if 'review2_lstm_inputs.zip' not in uploaded:
            raise FileNotFoundError('Select review2_lstm_inputs.zip and rerun this cell.')
        INPUT_PACKAGE.write_bytes(uploaded['review2_lstm_inputs.zip'])
        del uploaded
    if USE_GOOGLE_DRIVE:
        from google.colab import drive
        drive.mount('/content/drive')
        SAVED=Path('/content/drive/MyDrive/MemoryLeak_Review2_LSTM')
    else:
        SAVED=WORK
else:
    WORK=Path.cwd().resolve()
    if not (WORK/'data/packages/review2_lstm_inputs.zip').exists() and (WORK.parent/'data/packages/review2_lstm_inputs.zip').exists():
        WORK=WORK.parent
    INPUT_PACKAGE=WORK/'data/packages/review2_lstm_inputs.zip'
    SAVED=WORK
SOURCE=WORK/'data/lstm_inputs'
OUTPUT=SAVED/'results/lstm'
RESULT_PACKAGE=SAVED/'data/packages/review2_lstm_results.zip'
print('Input:',INPUT_PACKAGE)
print('Checkpoint/output folder:',OUTPUT)
''')
md('''## 3. Load the complete LSTM implementation
No other source files need uploading. The code includes input-manifest verification, causal windows, checkpoint saving, validation-based selection, forecast comparisons and scientific figures. The project tests check future-data isolation, hidden-state isolation, optimization, weight reloads and interrupted-run resumption.''')
code(source)
md('''## 4. Verify the source packages and train the four models
This cell prints progress after each epoch. The training score is an online average measured while weights are being updated; validation uses the fixed weights at the end of the epoch. Those curves need not coincide.

The test partition is scored only after all four checkpoints are selected and frozen. An LSTM result worse than the baselines remains a valid finding; do not change settings based on its test score.''')
code('''source_folder,input_receipt=unpack_inputs(INPUT_PACKAGE,SOURCE)
summary=run_experiment(source_folder,OUTPUT,input_receipt,device_choice='auto')
print('Actual runtime:',summary['runtime'])
print('Classification metrics computed:',summary['classification_metrics_computed'])
''')
md('''## 5. Review measured errors and selected epochs
MAE/RMSE are in **percentage points of total RAM**, not accuracy percentages. The table preserves every baseline, even if the new model performs worse. Each recording has a different workload; compare methods within a recording.''')
code('''metrics=pd.read_csv(OUTPUT/'metrics.csv')
display(metrics[metrics['split'].eq('test')][['dataset','model','n','mae_percentage_points','rmse_percentage_points','clipped_forecasts']])
display(pd.DataFrame([{'dataset':d['dataset'],'epochs_run':d['epochs_run'],'selected_epoch':d['best_epoch'],
                      'training_windows':d['training_origin_count'],'input_features':len(d['feature_names']),
                      'parameters':d['parameter_count']} for d in summary['datasets']]))
''')
md('''## 6. Inspect the figures
These use the same illustrative target-time intervals as the baseline notebook. Red shaded regions mark recorded injected leaks; they are not generated warnings. Full-period error scores and the active-leak error breakdown are saved separately.''')
code('''from PIL import Image
figures=['test_error_comparison.png','antarex_mono/learning_curve.png','antarex_mono/first_test_30min.png',
         'westermo_1/learning_curve.png','westermo_1/first_test_day.png']
for relative in figures:
    with Image.open(OUTPUT/relative) as picture:
        display(picture)
''')
md('''## 7. Reload saved weights, verify predictions and download the results
This recomputes the LSTM's forecasts from the saved checkpoints, checks the reported errors and confirms that selected model files are unchanged. The download contains model weights, resumable checkpoints, training history, parameters, forecasts, figures and a hash manifest.''')
code('''checks=verify_results(SOURCE,OUTPUT,device_choice='auto')
print(checks)
receipt=package_results(OUTPUT,RESULT_PACKAGE)
print(receipt)
if IN_COLAB:
    from google.colab import files
    files.download(str(RESULT_PACKAGE))
''')
md('''## Checkpoint
The initial LSTM forecasting comparison is complete once the checks pass. Leak-warning precision/recall and detection delay, broader seed/ablation studies, and the research-paper draft remain separate later stages. The available data do not demonstrate warning lead time before memory exhaustion.
''')
for i,c in enumerate(cells): c['id']=f'lstm-{i:02d}'
nb={'nbformat':4,'nbformat_minor':5,'cells':cells,'metadata':{
    'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python'},
    'colab':{'name':'03_lstm_colab.ipynb','provenance':[]},
    'lstm_source_sha256':hashlib.sha256(source.encode()).hexdigest(),
    'protocol_sha256':hashlib.sha256(protocol.encode()).hexdigest()}}
(ROOT/'notebooks/03_lstm_colab.ipynb').write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
print('Created notebooks/03_lstm_colab.ipynb')
