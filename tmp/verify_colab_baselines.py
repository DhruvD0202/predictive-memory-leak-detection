"""Independently verify the user's Colab baseline result against source inputs."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import baselines as base

colab=ROOT/'data/packages/review2_baseline_results_colab.zip'
local=ROOT/'data/packages/review2_baseline_results.zip'
inputs=ROOT/'data/packages/review2_preprocessed_colab.zip'
audit_dir=ROOT/'results/verification'
audit_dir.mkdir(parents=True,exist_ok=True)

def j(archive,name): return json.loads(archive.read(name))
def csv(archive,name):
    return pd.read_csv(io.BytesIO(archive.read(name)),compression='gzip' if name.endswith('.gz') else None)

def checked_manifest(archive):
    names=archive.namelist()
    assert len(names)==len(set(names)), 'Duplicate archive entries'
    manifest=j(archive,'MANIFEST.json')
    entries=[x['entry'] for x in manifest['files']]
    assert len(entries)==len(set(entries))
    assert set(names)==set(entries)|{'MANIFEST.json'}
    for item in manifest['files']:
        content=archive.read(item['entry'])
        assert len(content)==item['bytes'],item['entry']
        assert hashlib.sha256(content).hexdigest()==item['sha256'],item['entry']
    return manifest

assert base.sha256(inputs)==base.INPUT_SHA256
records=[]
forecast_values=0
max_prediction_difference=0.
max_formula_difference=0.
max_metric_difference=0.
max_parameter_difference=0.
with zipfile.ZipFile(colab) as z,zipfile.ZipFile(local) as l,zipfile.ZipFile(inputs) as src:
    manifest=checked_manifest(z)
    local_manifest=checked_manifest(l)
    source_manifest=checked_manifest(src)
    assert manifest['input_package_sha256']==base.INPUT_SHA256
    assert set(x['entry'] for x in manifest['files'])==set(x['entry'] for x in local_manifest['files'])
    summary=j(z,'experiment_summary.json')
    local_summary=j(l,'experiment_summary.json')
    freeze=j(z,'selection_freeze.json')
    assert summary['input_package_sha256']==freeze['input_sha256']==base.INPUT_SHA256
    assert freeze['test_evaluation_started'] is False
    assert datetime.fromisoformat(freeze['completed_utc'])<datetime.fromisoformat(summary['completed_utc'])
    assert not summary['classification_metrics_computed'] and not summary['lstm_trained']
    metrics=csv(z,'metrics.csv')
    local_metrics=csv(l,'metrics.csv')
    keys=['dataset','split','model']
    assert len(metrics)==24 and not metrics.duplicated(keys).any()
    measured_columns=['mae_fraction','rmse_fraction','mae_percentage_points','rmse_percentage_points']
    a=metrics.set_index(keys).sort_index()
    b=local_metrics.set_index(keys).sort_index()
    pd.testing.assert_index_equal(a.index,b.index)
    assert (a['n']==b['n']).all() and (a['clipped_forecasts']==b['clipped_forecasts']).all()
    np.testing.assert_allclose(a[measured_columns],b[measured_columns],rtol=1e-10,atol=1e-12)
    max_metric_difference=float(np.max(np.abs(a[measured_columns].to_numpy()-b[measured_columns].to_numpy())))
    prep=j(src,'preprocessing_summary.json')
    assert [d['dataset'] for d in summary['datasets']]==[d['dataset'] for d in prep['datasets']]
    for info in prep['datasets']:
        name=info['dataset']
        frozen=j(z,name+'/frozen_settings.json')
        reference=j(l,name+'/frozen_settings.json')
        assert hashlib.sha256(z.read(name+'/frozen_settings.json')).hexdigest()==freeze['settings_files'][name]
        for key in ['selected_settings','best_family_by_validation_rmse','training_segment','input_checks',
                    'selection_partition','fit_partition','test_used_for_selection']:
            assert frozen[key]==reference[key],(name,key)
        for p,fit in frozen['fits'].items():
            np.testing.assert_allclose(fit['coefficients'],reference['fits'][p]['coefficients'],rtol=1e-10,atol=1e-12)
            max_parameter_difference=max(max_parameter_difference,float(np.max(np.abs(np.asarray(fit['coefficients'])-reference['fits'][p]['coefficients']))))
        candidates=csv(z,name+'/validation_candidates.csv')
        for family in ['linear_trend','arima']:
            ranked=candidates[candidates.family.eq(family)].sort_values(['rmse_fraction','setting'])
            assert int(ranked.iloc[0]['setting'])==frozen['selected_settings'][family]
        with np.load(io.BytesIO(src.read(name+'/model_arrays.npz')),allow_pickle=False) as arrays:
            y=arrays['target_memory_pressure'].astype(np.float64)
            t,valid,split=arrays['timestamps'],arrays['valid'],arrays['split_code']
            labels=arrays['leak_active']
        w=csv(src,name+'/forecast_windows.csv.gz')
        for partition,code in [('validation',1),('test',2)]:
            pred=csv(z,name+'/'+partition+'_predictions.csv.gz')
            local_pred=csv(l,name+'/'+partition+'_predictions.csv.gz')
            expected=w[w['split'].eq(partition)]
            index_columns=['origin_index','target_index','origin_timestamp','target_timestamp']
            np.testing.assert_array_equal(pred[index_columns],expected[index_columns])
            np.testing.assert_array_equal(pred[index_columns],local_pred[index_columns])
            o=pred['origin_index'].to_numpy(); target=pred['target_index'].to_numpy()
            np.testing.assert_allclose(pred['actual'],y[target],rtol=0,atol=1e-15)
            np.testing.assert_allclose(pred['leak_active_at_origin'],labels[o],equal_nan=True)
            np.testing.assert_allclose(pred['leak_active_at_target'],labels[target],equal_nan=True)
            assert (split[o]==code).all() and (split[target]==code).all()
            assert valid[o].all() and valid[target].all()
            raw={'persistence':y[o],
                 'linear_trend':base.linear_forecast(y,o,frozen['selected_settings']['linear_trend'],info['horizon_steps']),
                 'arima':base.arima_forecast(y,o,frozen['fits'][str(frozen['selected_settings']['arima'])]['coefficients'],info['horizon_steps'])}
            for model in base.MODELS:
                np.testing.assert_allclose(pred[model+'_raw'],raw[model],rtol=1e-10,atol=1e-12)
                np.testing.assert_allclose(pred[model],np.clip(raw[model],0,1),rtol=1e-10,atol=1e-12)
                np.testing.assert_allclose(pred[model],local_pred[model],rtol=1e-10,atol=1e-12)
                max_prediction_difference=max(max_prediction_difference,float(np.max(np.abs(pred[model]-local_pred[model]))))
                max_formula_difference=max(max_formula_difference,float(np.max(np.abs(pred[model+'_raw']-raw[model]))))
                score=base.errors(pred['actual'],pred[model])
                stored=a.loc[(name,partition,model)]
                for key in measured_columns:
                    np.testing.assert_allclose(score[key],stored[key],rtol=1e-10,atol=1e-12)
                assert len(pred)==stored['n']
                assert int(((raw[model]<0)|(raw[model]>1)).sum())==stored['clipped_forecasts']
                forecast_values+=len(pred)
        records.append({'dataset':name,'settings_match':True,'all_validation_test_origins_match':True,
                        'predictions_recomputed_from_source_memory':True,
                        'test_origins_per_model':int(info['window_counts']['test'])})
    figures=[]
    for item in manifest['files']:
        entry=item['entry']
        if entry.endswith('.png'):
            with Image.open(io.BytesIO(z.read(entry))) as im:
                im.verify()
            path=audit_dir/'colab_figures'/entry
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(z.read(entry))
            figures.append(entry)
    assert len(figures)==4
    audit={'verification_completed_utc':datetime.now(timezone.utc).isoformat(),
           'colab_package':str(colab.relative_to(ROOT)),'colab_package_sha256':base.sha256(colab),
           'all_checks_passed':True,'verified_result_files':len(manifest['files']),
           'input_package_sha256':base.INPUT_SHA256,'forecast_values_independently_checked':forecast_values,
           'metric_rows_checked':len(metrics),'datasets':records,
           'max_abs_colab_local_prediction_difference_fraction':max_prediction_difference,
           'max_abs_raw_forecast_formula_difference_fraction':max_formula_difference,
           'max_abs_metric_difference_across_reported_columns':max_metric_difference,
           'max_abs_ar_coefficient_difference':max_parameter_difference,
           'numerical_tolerance':{'rtol':1e-10,'atol':1e-12},
           'colab_runtime':summary['runtime'],'local_runtime':local_summary['runtime'],
           'colab_experiment_seconds':summary['elapsed_seconds'],'valid_png_figures':figures,
           'scope':'Baseline reproduction only; no new model training or performance tuning.'}
    base.dump_json(audit_dir/'colab_baseline_verification.json',audit)
print(json.dumps(audit,indent=2))
