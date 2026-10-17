"""Independently audit saved seed/feature experiments without retraining them."""
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.lstm_forecasting import MemoryLSTM

def digest(path):
    with path.open('rb') as handle: return hashlib.file_digest(handle,'sha256').hexdigest()

def equal(actual, expected):
    np.testing.assert_allclose(actual,expected,rtol=1e-9,atol=1e-10,equal_nan=True)

def flags(scores,times,threshold,cadence):
    qualifies=np.zeros(len(times),dtype=bool) if threshold is None else np.asarray(scores)>=threshold
    active=np.zeros(len(times),dtype=bool)
    active[2:]=qualifies[2:] & qualifies[1:-1] & qualifies[:-2] & (np.diff(times)[1:]==cadence) & (np.diff(times)[:-1]==cadence)
    starts=active & ~np.r_[False,active[:-1] & (np.diff(times)==cadence)]
    return active,starts

def counts(truth,active,starts,cadence):
    truth=np.asarray(truth,dtype=bool)
    tp=int(sum(truth & active)); fp=int(sum(~truth & active))
    fn=int(sum(truth & ~active)); tn=int(sum(~truth & ~active))
    return dict(tp=tp,fp=fp,fn=fn,tn=tn,
        precision=tp/(tp+fp) if tp+fp else np.nan,recall=tp/(tp+fn),
        f1=2*tp/(2*tp+fp+fn),false_alarm_starts=int(sum(starts & ~truth)),
        false_alarm_starts_per_non_leak_hour=sum(starts & ~truth)/((fp+tn)*cadence/3600),
        false_positive_exposure_minutes=fp*cadence/60)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/revision_20261016')
    parser.add_argument('--source',type=Path,default=ROOT/'data/revision_inputs')
    args=parser.parse_args()
    output=args.output; source=args.source
    manifest=json.loads((output/'MANIFEST.json').read_text())
    for item in manifest['files']:
        path=output/item['path']
        assert path.stat().st_size==item['bytes'] and digest(path)==item['sha256'],path
    protocol=json.loads((output/'protocol.json').read_text())
    assert digest(ROOT/'research/REVISION_PROTOCOL_20261016.md')==protocol['protocol_sha256']
    for name,key in [('scripts/run_revision_study.py','runner_sha256'),('src/lstm_forecasting.py','training_implementation_sha256'),('src/warning_evaluation.py','warning_implementation_sha256')]:
        assert digest(ROOT/name)==protocol[key]
    assert protocol['seeds']==[7,21,42,84,123]
    models=json.loads((output/'selection_freeze.json').read_text())['models']
    assert len(models)==40 and manifest['models']==40
    metrics=pd.read_csv(output/'forecast_runs.csv')
    points=pd.read_csv(output/'warning_point_runs.csv')
    event_table=pd.read_csv(output/'warning_event_outcomes.csv')
    events=pd.read_csv(output/'warning_event_runs.csv')
    infos=json.loads((source/'prepared/preprocessing_summary.json').read_text())['datasets']
    torch.set_num_threads(2)
    total_origins=0; inference_checks=0; warning_checks=0
    for info in infos:
        name=info['dataset']; base=source/'prepared'/name
        with np.load(base/'model_arrays.npz',allow_pickle=False) as archive:
            arrays={k:archive[k] for k in archive.files}
        windows=pd.read_csv(base/'forecast_windows.csv.gz')
        reference_training=None
        for selected in [m for m in models if m['dataset']==name]:
            variant,seed=selected['variant'],selected['seed']
            dest=output/name/variant/f'seed_{seed}'
            config=json.loads((dest/'configuration.json').read_text())
            frozen=json.loads((dest/'selected_model.json').read_text())
            history=pd.read_csv(dest/'training_history.csv')
            assert frozen['best_epoch']==int(history.loc[history.validation_rmse_fraction.idxmin(),'epoch'])
            assert digest(dest/'best_weights.pt')==selected['weight_sha256']==frozen['best_weight_sha256']
            training=np.load(dest/'training_origins.npy',allow_pickle=False)
            stride=12 if name=='antarex_mono' else 4
            np.testing.assert_array_equal(training,windows.loc[windows.split.eq('train'),'origin_index'].to_numpy()[::stride])
            if reference_training is None: reference_training=training
            np.testing.assert_array_equal(training,reference_training)
            assert not config['test_used_for_selection'] and config['settings']['seed']==seed
            assert config['feature_names']==(['memory_pressure'] if variant=='memory_only' else info['feature_names'])
            indexes=[info['feature_names'].index(f) for f in config['feature_names']]
            features=arrays['features'][:,indexes]
            model=MemoryLSTM(len(indexes),32)
            model.load_state_dict(torch.load(dest/'best_weights.pt',map_location='cpu',weights_only=True)); model.eval()
            assert sum(p.numel() for p in model.parameters())==selected['parameter_count']
            for split in ['validation','test']:
                w=windows[windows.split.eq(split)]
                frame=pd.read_csv(dest/f'{split}_predictions.csv.gz')
                b=pd.read_csv(source/'baselines'/name/f'{split}_predictions.csv.gz')
                for col in ['origin_index','target_index','origin_timestamp','target_timestamp']:
                    np.testing.assert_array_equal(frame[col],w[col]); np.testing.assert_array_equal(frame[col],b[col])
                o=frame.origin_index.to_numpy(dtype=int); target=frame.target_index.to_numpy(dtype=int)
                equal(frame.actual,arrays['target_memory_pressure'][target]); equal(frame.actual,b.actual)
                equal(frame.lstm,np.clip(frame.lstm_raw,0,1))
                for pos in [0,len(frame)//2,len(frame)-1]:
                    x=torch.from_numpy(np.ascontiguousarray(features[o[pos]-59:o[pos]+1][None],dtype=np.float32))
                    with torch.inference_mode(): raw=float(model(x).item())*config['target_std']+config['target_mean']
                    assert abs(raw-frame.lstm_raw.iloc[pos])<1e-6
                    inference_checks+=1
                group=metrics[(metrics.dataset==name)&(metrics.variant==variant)&(metrics.seed==seed)&(metrics.split==split)].set_index('model')
                for method in ['persistence','linear_trend','arima','lstm']:
                    pred=frame.lstm if method=='lstm' else b[method]
                    error=np.asarray(pred)-frame.actual.to_numpy()
                    equal(group.loc[method,'mae_percentage_points'],100*np.mean(np.abs(error)))
                    equal(group.loc[method,'rmse_percentage_points'],100*np.sqrt(np.mean(error**2)))
                total_origins+=len(frame)
                if name!='antarex_mono': continue
                sf=pd.read_csv(dest/f'{split}_warnings.csv.gz')
                times=frame.origin_timestamp.to_numpy(dtype=np.int64); cadence=info['cadence_seconds']
                y=arrays['target_memory_pressure'].astype(np.float64)
                x=np.arange(12)*cadence/60; centered=x-x.mean()
                recent=np.array([y[k-11:k+1] for k in o])
                slope=100*np.sum((recent-recent.mean(axis=1)[:,None])*centered,axis=1)/sum(centered**2)
                q=(frame.lstm.to_numpy()-y[o])*100/(info['forecast_horizon_seconds']/60)
                equal(sf.observed_growth_pp_per_minute,slope)
                equal(sf.lstm_growth_score,np.minimum(slope,q))
                equal(sf.leak_active,arrays['leak_active'][o])
                selection=json.loads((dest/'warning_selection_freeze.json').read_text())['selected']
                for method,sel in selection.items():
                    score=np.zeros(len(frame)) if method=='always_off' else sf[method+'_score'].to_numpy()
                    active,starts=flags(score,times,sel['threshold_pp_per_minute'],cadence)
                    np.testing.assert_array_equal(active,sf[method+'_warning']); np.testing.assert_array_equal(starts,sf[method+'_alarm_start'])
                    expected=counts(sf.leak_active,active,starts,cadence)
                    recorded=points[(points.variant==variant)&(points.seed==seed)&(points.split==split)&(points.method==method)].iloc[0]
                    for key,value in expected.items(): equal(recorded[key],value)
                    if split=='validation':
                        grid=[None] if method=='always_off' else [.01,.025,.05,.1,.2,.4,.8,1.6,3.2,None]
                        choices=[]
                        for threshold in grid:
                            a,s=flags(score,times,threshold,cadence); c=counts(sf.leak_active,a,s,cadence)
                            choices.append((-c['f1'],c['fp'],-(threshold if threshold is not None else float('inf')),threshold))
                        assert min(choices,key=lambda row:row[:3])[3]==sel['threshold_pp_per_minute']
                    episodes=pd.read_csv(base/'leak_episodes.csv')
                    rows=event_table[(event_table.variant==variant)&(event_table.seed==seed)&(event_table.split==split)&(event_table.method==method)]
                    delays=[]; eligible_count=0
                    for row in rows.itertuples():
                        original=episodes.loc[episodes.episode_id.eq(row.episode_id)].iloc[0]
                        assert original.start==row.start and original.end==row.end
                        left,right=np.searchsorted(times,[row.start,row.end])
                        eligible=(left>0 and right>left and row.start>=times[0] and row.end<=times[-1]+cadence and times[left]-row.start<cadence and row.end-times[right-1]<=cadence and np.all(np.diff(times[left-1:right])==cadence))
                        assert eligible==row.eligible
                        if not eligible: continue
                        eligible_count+=1
                        hits=times[left:right][starts[left:right]]
                        assert bool(len(hits))==row.detected
                        if len(hits):
                            delay=hits[0]-row.start; equal(delay,row.delay_seconds); delays.append(delay)
                    recorded_event=events[(events.variant==variant)&(events.seed==seed)&(events.split==split)&(events.method==method)].iloc[0]
                    assert recorded_event.eligible_events==eligible_count and recorded_event.detected_events==len(delays)
                    equal(recorded_event.median_delay_seconds_detected_only,np.median(delays) if delays else np.nan)
                    equal(recorded_event.p90_delay_seconds_detected_only,np.quantile(delays,.9) if delays else np.nan)
                    warning_checks+=1
    summary=pd.read_csv(output/'forecast_summary.csv')
    for row in summary.itertuples():
        group=metrics[(metrics.dataset==row.dataset)&(metrics.variant==row.variant)&(metrics.split=='test')&(metrics.model=='lstm')]
        assert len(group)==5
        for col in ['mae_percentage_points','rmse_percentage_points']:
            equal(getattr(row,col+'_mean'),group[col].mean()); equal(getattr(row,col+'_sd'),group[col].std(ddof=1))
    ws=pd.read_csv(output/'warning_summary.csv')
    joint=points.merge(events,on=['dataset','variant','seed','split','method'],validate='one_to_one')
    for row in ws.itertuples():
        group=joint[(joint.variant==row.variant)&(joint.method==row.method)&(joint.split=='test')]
        for key in ['precision','recall','f1','false_alarm_starts','false_alarm_starts_per_non_leak_hour','missed_events','median_delay_seconds_detected_only']:
            equal(getattr(row,key+'_mean'),group[key].mean()); equal(getattr(row,key+'_sd'),group[key].std(ddof=1))
    report={'all_checks_passed':True,'models_verified':len(models),'manifest_files_verified':len(manifest['files']),
        'validation_and_test_forecast_rows_verified':total_origins,'fresh_weight_inferences_checked':inference_checks,
        'warning_partition_method_checks':warning_checks,'seed_summary_checks':True,
        'checks':'Hashes, configuration/protocol freeze, checkpoint selection, identical origins, direct model inference, error recomputation, independent warning confirmation/threshold selection, confusion counts, event recognition/delay and summaries.'}
    dest=ROOT/'results/revision_diagnostics/revision_integrity_checks.json'
    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
