import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'src/baselines.py').read_text(encoding='utf-8')
cells=[]
def md(text): cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(keepends=True)})
def code(text): cells.append({'cell_type':'code','metadata':{},'source':text.splitlines(keepends=True),'execution_count':None,'outputs':[]})

md('''# Predictive Memory Leak Detection — 02: Baseline forecasts

This stage trains statistical forecasting baselines and produces **measured MAE/RMSE and actual-versus-predicted charts**. It does not train an LSTM or claim leak-warning classification accuracy.

## Run in free Colab
1. Upload this notebook to Colab and keep the runtime on **CPU**.
2. Run the cells in order. The first cell installs the two required model/plotting packages if needed.
3. When prompted, upload **`review2_preprocessed_colab.zip`**, approximately 23 MB, saved from your successful preprocessing run. Do not upload the 214 MB raw ZIP here.
4. Review the tables, charts and final verification message.
5. Save the downloaded **`review2_baseline_results.zip`**. Keep a copy of this executed notebook too.

## Experiment fixed before results
- Four separate recordings and the existing chronological splits. Antarex forecasts **60 seconds ahead**; Westermo forecasts **five minutes ahead**.
- Persistence predicts the last observed memory value.
- Linear trend fits the last 12, 30 or 60 observations; its history length is selected on validation RMSE.
- ARIMA(p,1,0), without drift, tries p = 1, 3, 5. It uses statsmodels' Yule-Walker estimator on the longest contiguous training segment, without joining across gaps. Its order is selected on validation RMSE. This is a restricted initial ARIMA comparison, not an exhaustive Box-Jenkins analysis.
- All model choices are saved before scoring test forecasts. Coefficients are never refitted on validation/test values. At each new origin, the observed past through that origin is available; the future is not.
- Clip every model's prediction to [0,1]. Raw predictions and clipping counts are also saved.
- Error units are **percentage points of total RAM**, not accuracy percentages. Memory pressure is `1 - available/total`.
- The figures use intervals chosen by time/event rules, not by model performance. Overall scores include every eligible validation/test window. Overlapping windows are not independent trials.

The earlier multivariate features remain ready for LSTM. These first baselines use memory history only. Westermo remains unlabeled; Antarex's injected-leak intervals are context, not demonstrated warnings or exhaustion events.

## Methodological sources
Review 1 reference [3], [Assi et al. (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), motivates the statistical-versus-LSTM comparison. None of its reported errors are reused. The implementation follows the primary [statsmodels ARIMA specification](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.html), [estimator documentation](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.fit.html) and [rolling-origin forecasting example](https://www.statsmodels.org/v0.12.2/examples/notebooks/generated/statespace_forecasting.html).
''')
md('## 1. Prepare the runtime\nA GPU is not used. NumPy and pandas from your environment are retained; their actual versions are recorded in the results.')
code('''import importlib.metadata
import importlib.util
from pathlib import Path
import subprocess
import sys

needed=[]
for package,version in [('statsmodels','0.14.6'),('matplotlib','3.10.8')]:
    try:
        current=importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        current=None
    if current!=version:
        needed.append(f'{package}=={version}')
if needed:
    subprocess.check_call([sys.executable,'-m','pip','install','--quiet',*needed])
print('Model and plotting dependencies are ready.')
''')
md('## 2. Upload the prepared data\nThe SHA-256 and per-file checks below ensure this is the verified Colab preprocessing output for the experiment.')
code('''try:
    IN_COLAB=importlib.util.find_spec('google.colab') is not None
except ModuleNotFoundError:
    IN_COLAB=False
if IN_COLAB:
    WORK=Path('/content/memory_leak_baselines')
    INPUT_PACKAGE=Path('/content/review2_preprocessed_colab.zip')
    if not INPUT_PACKAGE.exists():
        from google.colab import files
        uploaded=files.upload()
        if 'review2_preprocessed_colab.zip' not in uploaded:
            raise FileNotFoundError('Upload review2_preprocessed_colab.zip and rerun this cell.')
        INPUT_PACKAGE.write_bytes(uploaded['review2_preprocessed_colab.zip'])
        del uploaded
else:
    WORK=Path.cwd().resolve()
    if not (WORK/'data/packages/review2_preprocessed_colab.zip').exists() and (WORK.parent/'data/packages/review2_preprocessed_colab.zip').exists():
        WORK=WORK.parent
    INPUT_PACKAGE=WORK/'data/packages/review2_preprocessed_colab.zip'
SOURCE=WORK/'data/baseline_inputs_colab'
OUTPUT=WORK/'results/baselines'
RESULT_PACKAGE=WORK/'data/packages/review2_baseline_results.zip'
print('Environment:', 'Colab' if IN_COLAB else 'local Python')
print('Input:', INPUT_PACKAGE)
''')
md('## 3. Load the self-contained baseline implementation\nThe same source is also supplied as `src/baselines.py`. No other code upload is needed. Its seven focused tests include comparison against statsmodels forecasts and checks that changing future values cannot change a forecast or model selection.')
code(source)
md('## 4. Verify inputs, fit candidates, freeze settings and evaluate\nAll four datasets complete validation-based selection before any test scores are calculated. If a fit or data assertion fails, the experiment stops rather than silently dropping a model.')
code('''source_folder=unpack_inputs(INPUT_PACKAGE,SOURCE)
summary=run_experiment(source_folder,OUTPUT)
print('Runtime versions:',summary['runtime'])
print('LSTM trained:',summary['lstm_trained'])
''')
md('## 5. Inspect measured test errors and frozen choices\nLower MAE/RMSE is better. A 1.0 percentage-point error means a difference equal to 1% of the machine\'s total RAM, not a 99% classification accuracy. The best family below was chosen by validation RMSE, even if another family happens to score better on test.')
code('''metrics=pd.read_csv(OUTPUT/'metrics.csv')
display(metrics[metrics['split'].eq('test')][['dataset','model','n','mae_percentage_points','rmse_percentage_points','clipped_forecasts']])
display(pd.DataFrame([{'dataset':d['dataset'],'trend_history_steps':d['selected_settings']['linear_trend'],
                      'ARIMA_order':str((d['selected_settings']['arima'],1,0)),
                      'best_family_by_validation':d['best_family_by_validation_rmse']} for d in summary['datasets']]))
''')
md('## 6. Inspect the real forecast charts\nPredictions are plotted at their future **target times**. Shading identifies recorded injected-leak intervals; it is not a predicted warning. The first eligible test leak is selected by timestamp, not by whichever example makes a model look best.')
code('''from PIL import Image
for relative in ['test_error_comparison.png','antarex_mono/first_test_30min.png',
                 'antarex_mono/first_test_leak.png','westermo_1/first_test_day.png']:
    figure=OUTPUT/relative
    if figure.exists():
        with Image.open(figure) as picture:
            display(picture)
''')
md('## 7. Verify the saved forecasts and download the evidence\nThis recomputes errors from saved predictions and verifies that the selected settings have not changed. The ZIP includes prediction tables, parameters, validation candidates, measured errors, PNG/PDF figures and a hash manifest.')
code('''checks=verify_results(OUTPUT)
print(checks)
receipt=package_results(OUTPUT,RESULT_PACKAGE)
print(receipt)
if IN_COLAB:
    from google.colab import files
    files.download(str(RESULT_PACKAGE))
''')
md('''## Checkpoint and limitations
You now have a trained statistical baseline and demonstrable forecasting results. Small multivariate LSTM training, leak-warning evaluation and the supported research-paper draft remain later steps. Do not change subsequent model settings in response to these test scores; use the training/validation partitions.

The Antarex pilot contains controlled injections but no observed 80% memory-pressure crossing, so these results do not demonstrate warning lead time before exhaustion. Westermo cannot supply leak precision/recall. No Mann-Kendall significance test, hybrid model, deployment-overhead claim or final paper conclusion is produced in this stage.
''')
for i,c in enumerate(cells): c['id']=f'baseline-{i:02d}'
nb={'nbformat':4,'nbformat_minor':5,'cells':cells,'metadata':{
    'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python'},
    'colab':{'name':'02_baselines_colab.ipynb','provenance':[]},
    'baseline_source_sha256':hashlib.sha256(source.encode()).hexdigest()}}
(ROOT/'notebooks/02_baselines_colab.ipynb').write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
print('Created self-contained baseline notebook.')
