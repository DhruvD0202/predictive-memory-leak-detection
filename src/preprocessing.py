"""Causal, reproducible preprocessing for the Review 2 pilot. No models are trained."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import zipfile

import numpy as np
import pandas as pd

PACKAGE_SHA256 = '06df79379df958405ab3d3486dea3e81dff2eb6fa26e53b4cf6ea634210db75e'
SPLIT_NAMES = ('train', 'validation', 'test')
ANTAREX_UNITS = {
    'memory_pressure': 'fraction: 1 - MemAvailable / MemTotal',
    'anonymous_memory_gib': 'GiB from AnonPages (KiB)',
    'committed_memory_gib': 'GiB from Committed_AS (KiB), not necessarily resident',
    'cpu_busy_fraction': 'fraction of CPU ticks; excludes idle and iowait',
    'cpu_iowait_fraction': 'fraction of CPU ticks',
    'page_faults_per_second': 'faults/s, including major and minor faults',
    'major_page_faults_per_second': 'major faults/s',
    'swap_used_gib': 'GiB from SwapTotal - SwapFree',
    'swap_in_pages_per_second': 'pages/s',
    'swap_out_pages_per_second': 'pages/s',
    'disk_read_bytes_per_second': 'bytes/s from sector differences, 512 bytes/sector',
    'disk_write_bytes_per_second': 'bytes/s from sector differences, 512 bytes/sector',
}
WESTERMO_UNITS = {
    'memory_pressure': 'fraction: 1 - sys-mem-available / sys-mem-total',
    'swap_used_gib': 'GiB',
    'cpu_user_rate': 'publisher aggregate CPU user-time rate; not normalized percent',
    'cpu_system_rate': 'publisher aggregate CPU system-time rate',
    'cpu_iowait_rate': 'publisher aggregate CPU iowait rate',
    'disk_read_bytes_per_second': 'publisher disk-bytes-read rate, bytes/s',
    'disk_write_bytes_per_second': 'publisher disk-bytes-written rate, bytes/s',
    'load_1m': 'publisher one-minute load average',
}

def dump_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')

def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open('rb') as src:
        while block := src.read(4 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()

def unpack_verified(package: Path, destination: Path):
    if sha256_file(package) != PACKAGE_SHA256:
        raise ValueError('Pilot ZIP checksum differs from the validated release.')
    destination.mkdir(parents=True, exist_ok=True)
    destination = destination.resolve()
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read('MANIFEST.json'))
        for item in manifest['files']:
            path = (destination / item['entry']).resolve()
            if not path.is_relative_to(destination):
                raise ValueError('Unsafe archive entry')
            if path.exists() and sha256_file(path) == item['sha256']:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with archive.open(item['entry']) as source, path.open('wb') as output:
                while block := source.read(4 * 1024 * 1024):
                    output.write(block)
                    digest.update(block)
            if path.stat().st_size != item['bytes'] or digest.hexdigest() != item['sha256']:
                raise ValueError(f'Content verification failed: {item["entry"]}')
    return destination

def align_past(stream: pd.DataFrame, grid: np.ndarray, tolerance=2.1):
    """Select only past observations, with a bounded age; never join by row index."""
    if stream['#Time'].duplicated().any() or not stream['#Time'].is_monotonic_increasing:
        raise ValueError('Telemetry timestamps must be unique and increasing')
    right = stream.rename(columns={'#Time': 'source_time'}).copy()
    right['source_time'] = right['source_time'].astype(float)
    aligned = pd.merge_asof(pd.DataFrame({'timestamp': grid.astype(float)}), right,
                            left_on='timestamp', right_on='source_time',
                            direction='backward', tolerance=tolerance)
    age = aligned['timestamp'] - aligned['source_time']
    assert age.dropna().between(0, tolerance + 1e-8).all()
    return aligned

def counter_rates(aligned: pd.DataFrame, columns, max_elapsed=7.2):
    elapsed = aligned['source_time'].diff()
    differences = aligned[list(columns)].diff()
    invalid_time = (elapsed <= 0) | (elapsed > max_elapsed) | elapsed.isna()
    differences = differences.mask(differences < 0)
    return differences.div(elapsed, axis=0).mask(invalid_time, axis=0)

def reconstruct_episodes(events: pd.DataFrame):
    leak = events['args'].str.contains('/leak ', regex=False)
    starts = events[leak & events['type'].eq('status_start')]
    ends = events[leak & events['type'].eq('status_end')]
    paired = starts.merge(ends, on='seqNum', suffixes=('_start', '_end'), validate='one_to_one')
    if len(paired) != len(starts) or len(paired) != len(ends):
        raise ValueError('Unpaired leak event')
    result = pd.DataFrame({
        'episode_id': paired['seqNum'].astype(int),
        'start': paired['timestamp_start'].astype(int),
        'end': paired['timestamp_end'].astype(int),
        'low_intensity': paired['args_start'].str.endswith(' l'),
    }).sort_values('start').reset_index(drop=True)
    if not (result['end'] > result['start']).all():
        raise ValueError('Invalid leak duration')
    if (result['start'].iloc[1:].to_numpy() < result['end'].iloc[:-1].to_numpy()).any():
        raise ValueError('Overlapping leak intervals require a different label representation')
    return result

def build_antarex(source: Path):
    base = source / 'antarex/CPU-MEM_mono'
    labels = pd.read_csv(next(base.glob('labels_*.csv')), sep=';', keep_default_na=False)
    events = pd.read_csv(next(base.glob('injection-*.csv')), sep=';', keep_default_na=False)
    episodes = reconstruct_episodes(events)
    start, end = int(labels['#Time'].min()), int(labels['#Time'].max())
    grid = np.arange(((start + 4)//5)*5, (end//5)*5+1, 5, dtype=np.int64)
    specs = {
        'meminfo': ['MemTotal', 'MemAvailable', 'AnonPages', 'Committed_AS', 'SwapTotal', 'SwapFree'],
        'vmstat': ['pgfault', 'pgmajfault', 'pswpin', 'pswpout'],
        'procstat': ['user', 'nice', 'sys', 'idle', 'iowait', 'irq', 'softirq', 'steal'],
        'procdiskstats': ['sect_read#sdc1', 'sect_written#sdc1'],
    }
    aligned, quality = {}, {}
    for name, cols in specs.items():
        raw = pd.read_csv(base / f'{name}.csv', usecols=['#Time'] + cols)
        a = align_past(raw, grid)
        age = a['timestamp'] - a['source_time']
        quality[name] = {'raw_rows': len(raw), 'unmatched_grid_rows': int(age.isna().sum()),
                         'max_observation_age_seconds': float(age.max())}
        aligned[name] = a
        del raw
    mem, vm, cpu, disk = (aligned[k] for k in specs)
    features = pd.DataFrame({'timestamp': grid})
    features['memory_pressure'] = 1 - mem['MemAvailable'] / mem['MemTotal']
    features['anonymous_memory_gib'] = mem['AnonPages'] / (1024**2)
    features['committed_memory_gib'] = mem['Committed_AS'] / (1024**2)
    cpu_delta = cpu[specs['procstat']].diff()
    cpu_elapsed = cpu['source_time'].diff()
    bad_cpu = ((cpu_delta < 0).any(axis=1) | cpu_delta.isna().any(axis=1)
               | (cpu_elapsed <= 0) | (cpu_elapsed > 7.2))
    cpu_delta.loc[bad_cpu, :] = np.nan
    total_ticks = cpu_delta.sum(axis=1, min_count=len(specs['procstat']))
    features['cpu_busy_fraction'] = 1 - (cpu_delta['idle'] + cpu_delta['iowait']) / total_ticks
    features['cpu_iowait_fraction'] = cpu_delta['iowait'] / total_ticks
    rates = counter_rates(vm, specs['vmstat'])
    for source_name, output_name in [('pgfault', 'page_faults_per_second'), ('pgmajfault', 'major_page_faults_per_second'),
                                     ('pswpin', 'swap_in_pages_per_second'), ('pswpout', 'swap_out_pages_per_second')]:
        features[output_name] = rates[source_name]
    features['swap_used_gib'] = (mem['SwapTotal'] - mem['SwapFree']) / (1024**2)
    disk_rates = counter_rates(disk, specs['procdiskstats']) * 512
    features['disk_read_bytes_per_second'] = disk_rates['sect_read#sdc1']
    features['disk_write_bytes_per_second'] = disk_rates['sect_written#sdc1']
    features = features[['timestamp'] + list(ANTAREX_UNITS)]
    exact_labels = labels.set_index('#Time').reindex(grid)
    if exact_labels['#Fault'].isna().any():
        raise ValueError('Grid lies outside label coverage')
    features['fault_type'] = exact_labels['#Fault'].to_numpy()
    features['leak_active'] = features['fault_type'].str.startswith('leak').astype(np.int8)
    features['episode_id'] = -1
    for row in episodes.itertuples(index=False):
        features.loc[(grid >= row.start) & (grid < row.end), 'episode_id'] = row.episode_id
    if not np.array_equal(features['episode_id'].ge(0).to_numpy(), features['leak_active'].eq(1).to_numpy()):
        raise ValueError('Event-to-label disagreement on aligned grid')
    features['label_known'] = True
    features['source_available'] = np.logical_and.reduce([a['source_time'].notna().to_numpy() for a in aligned.values()])
    return features, episodes, quality

def build_westermo(source: Path, system: int):
    d = pd.read_csv(source / f'westermo/system-{system}.csv')
    if d['timestamp'].duplicated().any() or not d['timestamp'].is_monotonic_increasing:
        raise ValueError('Westermo timestamps must be unique and increasing')
    grid = np.arange(int(d['timestamp'].min()), int(d['timestamp'].max())+1, 30, dtype=np.int64)
    if not np.isin(d['timestamp'], grid).all():
        raise ValueError('Unexpected Westermo cadence')
    d = d.set_index('timestamp').reindex(grid)
    f = pd.DataFrame({'timestamp': grid})
    f['memory_pressure'] = (1-d['sys-mem-available']/d['sys-mem-total']).to_numpy()
    f['swap_used_gib'] = ((d['sys-mem-swap-total']-d['sys-mem-swap-free'])/(1024**3)).to_numpy()
    mappings = {'cpu-user':'cpu_user_rate', 'cpu-system':'cpu_system_rate', 'cpu-iowait':'cpu_iowait_rate',
                'disk-bytes-read':'disk_read_bytes_per_second', 'disk-bytes-written':'disk_write_bytes_per_second', 'load-1m':'load_1m'}
    for old,new in mappings.items():
        f[new] = d[old].to_numpy()
    f['fault_type'] = 'unlabeled'
    f['leak_active'] = np.nan
    f['episode_id'] = -1
    f['label_known'] = False
    f['source_available'] = d['sys-mem-total'].notna().to_numpy()
    if 'server-up' in d:
        f['source_available'] &= d['server-up'].gt(0).to_numpy()
    return f, {'missing_or_unavailable_grid_rows': int((~f['source_available']).sum()),
               'rule': 'No filling. Original gaps split the model sequences.'}

def partition_codes(timestamps):
    t = np.asarray(timestamps, dtype=np.int64)
    # Fixed fractions of the recorded time extent, independent of labels and model errors.
    limits = [float(t[0] + .7*(t[-1]-t[0]+1)), float(t[0] + .85*(t[-1]-t[0]+1))]
    return np.searchsorted(limits, t, side='right').astype(np.int8), limits

def build_window_index(timestamps, valid, split, history_steps, horizon_steps, cadence):
    t = np.asarray(timestamps)
    valid = np.asarray(valid, dtype=bool)
    split = np.asarray(split)
    new_segment = np.ones(len(t), dtype=bool)
    new_segment[1:] = ((np.diff(t) != cadence) | (split[1:] != split[:-1]) | ~valid[:-1] | ~valid[1:])
    segments = np.cumsum(new_segment).astype(np.int32)-1
    segments[~valid] = -1
    groups = []
    bounds = np.r_[0, np.where(new_segment[1:])[0]+1, len(t)]
    for a,b in zip(bounds[:-1],bounds[1:]):
        if not valid[a] or b-a < history_steps+horizon_steps:
            continue
        origins = np.arange(a+history_steps-1, b-horizon_steps, dtype=np.int64)
        groups.append(pd.DataFrame({'history_start_index':origins-history_steps+1,'origin_index':origins,
                                    'target_index':origins+horizon_steps,'split_code':split[origins],
                                    'segment_id':segments[origins]}))
    if not groups:
        raise ValueError('No complete windows remain')
    windows = pd.concat(groups, ignore_index=True)
    return windows, segments

def fit_scaler(features: pd.DataFrame, candidate_names, training_mask):
    train = features.loc[training_mask, candidate_names]
    if len(train) < 100 or not np.isfinite(train.to_numpy()).all():
        raise ValueError('Insufficient finite training observations')
    means = train.mean()
    scales = train.std(ddof=0)
    selected = [name for name in candidate_names if scales[name] > 1e-12]
    if 'memory_pressure' not in selected:
        raise ValueError('The memory target is constant in training')
    return {'fit_partition':'train','training_rows':len(train),'features':selected,
            'removed_training_constant_features':[name for name in candidate_names if name not in selected],
            'mean':{name:float(means[name]) for name in selected},
            'std':{name:float(scales[name]) for name in selected}}

def export_dataset(frame, name, destination, units, cadence, history_steps, horizon_steps, quality, episodes=None):
    destination.mkdir(parents=True, exist_ok=True)
    candidates = list(units)
    frame = frame.copy()
    split, limits = partition_codes(frame['timestamp'])
    valid = np.isfinite(frame[candidates].to_numpy()).all(axis=1) & frame['source_available'].to_numpy()
    valid &= frame['memory_pressure'].between(0,1).to_numpy()
    for c in candidates:
        valid &= frame[c].ge(0).to_numpy()
    if 'cpu_busy_fraction' in frame:
        valid &= frame['cpu_busy_fraction'].between(0,1).to_numpy() & frame['cpu_iowait_fraction'].between(0,1).to_numpy()
    # Rate features at partition boundaries could depend on a previous partition.
    if name.startswith('antarex'):
        valid[np.r_[True, np.diff(split) != 0]] = False
    scaler = fit_scaler(frame, candidates, valid & (split==0))
    windows, segments = build_window_index(frame['timestamp'],valid,split,history_steps,horizon_steps,cadence)
    frame['split'] = np.asarray(SPLIT_NAMES)[split]
    frame['valid_for_model'] = valid
    frame['segment_id'] = segments
    windows['origin_timestamp'] = frame['timestamp'].to_numpy()[windows['origin_index']]
    windows['target_timestamp'] = frame['timestamp'].to_numpy()[windows['target_index']]
    windows['split'] = np.asarray(SPLIT_NAMES)[windows['split_code']]
    # All history, intervening future rows and target stay in the same valid segment.
    h,o,z = (windows[c].to_numpy() for c in ['history_start_index','origin_index','target_index'])
    assert (segments[h] == segments[z]).all() and (segments[o] >= 0).all()
    assert (split[h] == split[z]).all()
    assert (windows['target_timestamp']-windows['origin_timestamp']).eq(cadence*horizon_steps).all()
    selected = scaler['features']
    standardized = ((frame[selected]-pd.Series(scaler['mean']))/pd.Series(scaler['std'])).to_numpy(dtype=np.float32,copy=True)
    standardized[~valid] = np.nan
    assert np.isfinite(standardized[valid]).all()
    # Dense rolling windows are deliberately not allocated. The index file is used in batches.
    np.savez_compressed(destination/'model_arrays.npz',features=standardized,
                        feature_names=np.asarray(selected),target_memory_pressure=frame['memory_pressure'].to_numpy(dtype=np.float32),
                        timestamps=frame['timestamp'].to_numpy(dtype=np.int64),valid=valid,split_code=split,
                        leak_active=frame['leak_active'].to_numpy(dtype=np.float32),label_known=frame['label_known'].to_numpy(dtype=bool))
    frame.to_csv(destination/'features.csv.gz',index=False,compression='gzip')
    windows.to_csv(destination/'forecast_windows.csv.gz',index=False,compression='gzip')
    dump_json(destination/'scaler.json',scaler)
    dump_json(destination/'feature_dictionary.json',units)
    if episodes is not None:
        episodes.to_csv(destination/'leak_episodes.csv',index=False)
    summary = {'dataset':name,'grid_rows':len(frame),'valid_rows':int(valid.sum()),'invalid_rows':int((~valid).sum()),
               'cadence_seconds':cadence,'history_steps':history_steps,'horizon_steps':horizon_steps,
               'forecast_horizon_seconds':cadence*horizon_steps,'feature_names':selected,
               'removed_training_constant_features':scaler['removed_training_constant_features'],
               'split_time_boundaries':limits,'window_counts':{s:int(windows['split'].eq(s).sum()) for s in SPLIT_NAMES},
               'valid_row_counts':{s:int((valid & (split==i)).sum()) for i,s in enumerate(SPLIT_NAMES)},
               'labeled_leak_origin_counts':{s:int(frame['leak_active'].iloc[windows.loc[windows['split'].eq(s),'origin_index']].eq(1).sum()) for s in SPLIT_NAMES} if frame['label_known'].any() else None,
               'scaled_feature_array_bytes':standardized.nbytes,'quality':quality,
               'label_policy':'active injected leak at origin; not a future onset/exhaustion label' if frame['label_known'].any() else 'unlabeled; no leak precision/recall available',
               'model_training_performed':False}
    dump_json(destination/'summary.json',summary)
    print(name,summary['window_counts'],'features:',len(selected),flush=True)
    return summary

def run(source: Path, output: Path):
    output.mkdir(parents=True,exist_ok=True)
    frame,episodes,quality = build_antarex(source)
    summaries=[export_dataset(frame,'antarex_mono',output/'antarex_mono',ANTAREX_UNITS,5,60,12,quality,episodes)]
    del frame
    for system in [1,2,3]:
        frame,quality=build_westermo(source,system)
        summaries.append(export_dataset(frame,f'westermo_{system}',output/f'westermo_{system}',WESTERMO_UNITS,30,60,10,quality))
    result={'stage':'preprocessing only','datasets':summaries,
            'raw_package_sha256':PACKAGE_SHA256,'models_trained':0,
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},
            'important_limit':'Antarex mono has inactive swap, constant monitored disk I/O and no 80% memory-pressure crossing. Westermo has no confirmed leak labels.'}
    dump_json(output/'preprocessing_summary.json',result)
    return result

def verify_outputs(output: Path):
    """Reopen the saved model inputs and validate the entire window intervals."""
    summary = json.loads((output/'preprocessing_summary.json').read_text(encoding='utf-8'))
    checks = []
    for info in summary['datasets']:
        base = output/info['dataset']
        scaler = json.loads((base/'scaler.json').read_text(encoding='utf-8'))
        with np.load(base/'model_arrays.npz', allow_pickle=False) as arrays:
            x, valid, split = arrays['features'], arrays['valid'], arrays['split_code']
            t = arrays['timestamps']
            assert x.shape == (info['grid_rows'], len(info['feature_names']))
            assert arrays['feature_names'].tolist() == scaler['features'] == info['feature_names']
            assert not set(scaler['features']) & {'leak_active','fault_type','episode_id','timestamp','label_known'}
            assert np.isfinite(x[valid]).all() and np.isnan(x[~valid]).all()
            train = x[valid & (split == 0)].astype(np.float64)
            assert np.allclose(train.mean(axis=0), 0, atol=1e-6)
            assert np.allclose(train.std(axis=0), 1, atol=1e-6)
            windows = pd.read_csv(base/'forecast_windows.csv.gz')
            h,o,z = (windows[c].to_numpy() for c in ['history_start_index','origin_index','target_index'])
            invalid_prefix = np.r_[0, np.cumsum(~valid)]
            assert (invalid_prefix[z+1]-invalid_prefix[h] == 0).all()
            assert (split[h] == split[z]).all()
            assert (t[z]-t[h] == (info['history_steps']-1+info['horizon_steps'])*info['cadence_seconds']).all()
            assert (t[z]-t[o] == info['forecast_horizon_seconds']).all()
            assert (o-h+1 == info['history_steps']).all()
            if info['dataset'].startswith('westermo'):
                assert not arrays['label_known'].any() and np.isnan(arrays['leak_active']).all()
            else:
                assert arrays['label_known'].all()
                assert np.isin(arrays['leak_active'], [0,1]).all()
            checks.append({'dataset':info['dataset'],'saved_arrays_verified':True,
                           'complete_windows_checked':len(windows),'training_standardization_verified':True})
    dump_json(output/'integrity_checks.json',checks)
    return checks


def package_outputs(output: Path, package: Path):
    entries = sorted(p for p in output.rglob('*') if p.is_file())
    manifest = {'stage':'preprocessing only','raw_package_sha256':PACKAGE_SHA256,
                'files':[{'entry':p.relative_to(output).as_posix(),'bytes':p.stat().st_size,
                          'sha256':sha256_file(p)} for p in entries]}
    package.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_STORED) as archive:
        for p in entries:
            archive.write(p,p.relative_to(output).as_posix())
        archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(package) as archive:
        for item in manifest['files']:
            assert hashlib.sha256(archive.read(item['entry'])).hexdigest() == item['sha256']
    receipt={'package':package.name,'bytes':package.stat().st_size,'sha256':sha256_file(package),
             'every_entry_verified':True}
    dump_json(package.with_suffix('.manifest.json'),receipt)
    return receipt


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(unpack_verified(args.package,args.source),args.output)
    verify_outputs(args.output)
