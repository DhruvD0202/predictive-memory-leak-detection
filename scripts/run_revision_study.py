"""Matched five-seed feature ablation; keeps September experiments untouched."""
from pathlib import Path
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import torch
from src import lstm_forecasting as lf
from src import warning_evaluation as we

SEEDS = [7, 21, 42, 84, 123]
VARIANTS = ['multivariate', 'memory_only']


def variant_data(arrays, info, variant):
    arrays, info = dict(arrays), copy.deepcopy(info)
    if variant == 'memory_only':
        index = info['feature_names'].index('memory_pressure')
        arrays['features'] = np.ascontiguousarray(arrays['features'][:, index:index+1])
        arrays['feature_names'] = np.array(['memory_pressure'])
        info['feature_names'] = ['memory_pressure']
    assert arrays['features'].shape[1] == len(info['feature_names'])
    return arrays, info


def warning_frame(arrays, info, w, pred):
    origins = w['origin_index'].to_numpy(dtype=np.int64)
    frame = w[['origin_index', 'target_index', 'origin_timestamp', 'target_timestamp']].copy()
    frame['leak_active'] = arrays['leak_active'][origins]
    frame['label_known'] = arrays['label_known'][origins]
    for key, value in we.warning_scores(arrays['target_memory_pressure'], origins,
            pred['arima'], pred['lstm'], info['cadence_seconds'], info['forecast_horizon_seconds']).items():
        frame[key] = value
    return frame


def summarize(frame, keys, columns):
    out = []
    for key, group in frame.groupby(keys, sort=False):
        if not isinstance(key, tuple): key = (key,)
        row = dict(zip(keys, key))
        for col in columns:
            values = pd.to_numeric(group[col], errors='coerce').dropna()
            row.update({col+'_n': len(values), col+'_mean': values.mean(),
                        col+'_sd': values.std(ddof=1), col+'_min': values.min(), col+'_max': values.max()})
        out.append(row)
    return pd.DataFrame(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=ROOT/'data/packages/review2_lstm_inputs.zip')
    parser.add_argument('--input-dir', type=Path, default=ROOT/'data/revision_inputs')
    parser.add_argument('--output', type=Path, default=ROOT/'results/revision_20261016')
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    source, receipt = lf.unpack_inputs(args.package, args.input_dir)
    device, runtime = lf.configure_runtime('cpu')
    infos = json.loads((source/'prepared/preprocessing_summary.json').read_text())['datasets']
    protocol = {'seeds':SEEDS, 'variants':VARIANTS, 'settings':lf.SETTINGS,
        'runtime':runtime, 'input_receipt':receipt,
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'protocol_sha256':lf.file_sha256(ROOT/'research/REVISION_PROTOCOL_20261016.md'),
        'runner_sha256':lf.file_sha256(Path(__file__)),
        'training_implementation_sha256':lf.file_sha256(ROOT/'src/lstm_forecasting.py'),
        'warning_implementation_sha256':lf.file_sha256(ROOT/'src/warning_evaluation.py'),
        'original_holdout_previously_inspected':True, 'additional_labeled_recordings':0}
    # A resumed run must retain all substantive settings and input provenance.
    protocol_path = output/'protocol.json'
    if protocol_path.exists():
        old = json.loads(protocol_path.read_text())
        for k in protocol:
            if k != 'created_utc': assert old[k] == protocol[k], k
    else:
        lf.dump_json(protocol_path, protocol)
    selected = []
    for info in infos:
        original, windows = lf.load_recording(source, info)
        for variant in VARIANTS:
            arrays, adjusted = variant_data(original, info, variant)
            for seed in SEEDS:
                dest = output/info['dataset']/variant/f'seed_{seed}'
                settings = dict(lf.SETTINGS, seed=seed)
                print(f"TRAIN {info['dataset']} {variant} seed {seed}", flush=True)
                model, frozen = lf.train_recording(arrays, windows, adjusted, dest, device, runtime, settings)
                selected.append({'dataset':info['dataset'], 'variant':variant, 'seed':seed,
                    'best_epoch':frozen['best_epoch'], 'epochs_run':frozen['epochs_run'],
                    'parameter_count':frozen['parameter_count'],
                    'training_seconds_including_validation':frozen['training_seconds_including_validation'],
                    'weight_sha256':frozen['best_weight_sha256'],
                    'training_origin_sha256':frozen['configuration']['training_origin_sha256']})
                del model
    freeze = {'completed_utc':datetime.now(timezone.utc).isoformat(),
              'new_test_scoring_started':False, 'models':selected}
    if not (output/'selection_freeze.json').exists(): lf.dump_json(output/'selection_freeze.json',freeze)
    metric_rows, point_rows, event_rows, outcome_frames, candidates = [], [], [], [], []
    for info in infos:
        original, windows = lf.load_recording(source, info)
        for variant in VARIANTS:
            arrays, adjusted = variant_data(original, info, variant)
            for seed in SEEDS:
                tags = {'dataset':info['dataset'], 'variant':variant, 'seed':seed}
                dest = output/info['dataset']/variant/f'seed_{seed}'
                model = lf.MemoryLSTM(len(adjusted['feature_names']), 32).to(device)
                model.load_state_dict(torch.load(dest/'best_weights.pt', map_location=device, weights_only=True))
                thresholds = None
                for split in ['validation', 'test']:
                    w = windows[windows['split'].eq(split)]
                    o,z = (w[c].to_numpy(dtype=np.int64) for c in ['origin_index','target_index'])
                    baseline = pd.read_csv(source/'baselines'/info['dataset']/(split+'_predictions.csv.gz'))
                    np.testing.assert_array_equal(baseline['origin_index'],o)
                    np.testing.assert_array_equal(baseline['target_index'],z)
                    np.testing.assert_allclose(baseline['actual'],arrays['target_memory_pressure'][z],rtol=0,atol=1e-15)
                    raw = lf.predict_raw(model,arrays,o,info['history_steps'],device)
                    pred = baseline.copy()
                    pred['lstm_raw'], pred['lstm'] = raw, np.clip(raw,0,1)
                    pred[['origin_index','target_index','origin_timestamp','target_timestamp','actual','lstm_raw','lstm']].to_csv(dest/(split+'_predictions.csv.gz'),index=False,compression='gzip')
                    for method in ['persistence','linear_trend','arima','lstm']:
                        metric_rows.append({**tags,'split':split,'model':method,**lf.regression_errors(pred['actual'],pred[method])})
                    if info['dataset'] == 'antarex_mono':
                        frame = warning_frame(arrays,info,w,pred)
                        if split == 'validation':
                            thresholds, candidate = we.select_thresholds(frame,info['cadence_seconds'])
                            lf.dump_json(dest/'warning_selection_freeze.json', {'selected':thresholds,
                                'selection_partition':'validation','test_scoring_started':False})
                            candidates.append(candidate.assign(**tags))
                        scored = we.apply_thresholds(frame,thresholds,info['cadence_seconds'])
                        scored.to_csv(dest/(split+'_warnings.csv.gz'),index=False,compression='gzip')
                        episodes = pd.read_csv(source/'prepared'/info['dataset']/'leak_episodes.csv')
                        points, events, outcomes = we.score_antarex(scored,episodes,info['cadence_seconds'],split)
                        point_rows.extend(points.assign(variant=variant,seed=seed).to_dict('records'))
                        event_rows.extend(events.assign(variant=variant,seed=seed).to_dict('records'))
                        outcome_frames.append(outcomes.assign(variant=variant,seed=seed))
                print('SCORED',tags,flush=True)
    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(output/'forecast_runs.csv',index=False)
    pd.DataFrame(selected).to_csv(output/'training_runs.csv',index=False)
    summarize(metrics[metrics['split'].eq('test') & metrics['model'].eq('lstm')],['dataset','variant'],['mae_percentage_points','rmse_percentage_points']).to_csv(output/'forecast_summary.csv',index=False)
    pivot = metrics[metrics['split'].eq('test') & metrics['model'].eq('lstm')].pivot(index=['dataset','seed'],columns='variant',values=['mae_percentage_points','rmse_percentage_points'])
    paired = pd.DataFrame(index=pivot.index)
    for col in ['mae_percentage_points','rmse_percentage_points']:
        paired[col+'_multivariate_minus_memory_only'] = pivot[col]['multivariate']-pivot[col]['memory_only']
    paired.reset_index().to_csv(output/'paired_feature_differences.csv',index=False)
    points,events=pd.DataFrame(point_rows),pd.DataFrame(event_rows)
    points.to_csv(output/'warning_point_runs.csv',index=False)
    events.to_csv(output/'warning_event_runs.csv',index=False)
    pd.concat(outcome_frames,ignore_index=True).to_csv(output/'warning_event_outcomes.csv',index=False)
    pd.concat(candidates,ignore_index=True).to_csv(output/'warning_validation_candidates.csv',index=False)
    joined = points.merge(events,on=['dataset','variant','seed','split','method'],validate='one_to_one')
    summarize(joined[joined['split'].eq('test')],['variant','method'],['precision','recall','f1','false_alarm_starts','false_alarm_starts_per_non_leak_hour','missed_events','median_delay_seconds_detected_only']).to_csv(output/'warning_summary.csv',index=False)
    files = [p for p in sorted(output.rglob('*')) if p.is_file() and p.name not in ['MANIFEST.json','last_checkpoint.pt']]
    lf.dump_json(output/'MANIFEST.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),
        'models':len(selected),'files':[{'path':p.relative_to(output).as_posix(),'bytes':p.stat().st_size,'sha256':lf.file_sha256(p)} for p in files]})
    print('COMPLETE: 40 matched training runs, forecast and warning summaries saved.',flush=True)


if __name__ == '__main__': main()
