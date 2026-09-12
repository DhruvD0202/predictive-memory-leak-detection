"""Audit the saved Colab LSTM run without modifying or retraining its models."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import lstm_forecasting as exp

PACKAGE = ROOT / 'data/packages/review2_lstm_results_colab.zip'
DEST = ROOT / 'results/lstm_colab'
SOURCE = ROOT / 'data/lstm_inputs'
AUDIT = ROOT / 'results/verification/colab_lstm_verification.json'
METHODS = ['persistence', 'linear_trend', 'arima', 'lstm']
SCORES = ['mae_fraction', 'rmse_fraction', 'mae_percentage_points', 'rmse_percentage_points']


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify_archive(archive):
    names = archive.namelist()
    manifest = json.loads(archive.read('MANIFEST.json'))
    entries = [f['entry'] for f in manifest['files']]
    assert len(names) == len(set(names)) and len(entries) == len(set(entries))
    assert set(names) == set(entries) | {'MANIFEST.json'}
    for item in manifest['files']:
        assert (DEST / item['entry']).resolve().is_relative_to(DEST.resolve())
        content = archive.read(item['entry'])
        assert len(content) == item['bytes'], item['entry']
        assert hashlib.sha256(content).hexdigest() == item['sha256'], item['entry']
    return manifest


# Check exact source ZIPs and every already-extracted source file before inference.
for filename, digest, subdir in [
    ('review2_preprocessed_colab.zip', exp.PREP_SHA256, 'prepared'),
    ('review2_baseline_results_colab.zip', exp.BASELINE_SHA256, 'baselines'),
]:
    path = ROOT / 'data/packages' / filename
    assert exp.file_sha256(path) == digest
    with zipfile.ZipFile(path) as archive:
        manifest = verify_archive(archive)
        for item in manifest['files']:
            assert exp.file_sha256(SOURCE / subdir / item['entry']) == item['sha256']

with zipfile.ZipFile(PACKAGE) as archive:
    manifest = verify_archive(archive)
    assert manifest['protocol_version'] == exp.PROTOCOL_VERSION
    assert manifest['prepared_package_sha256'] == exp.PREP_SHA256
    assert manifest['baseline_package_sha256'] == exp.BASELINE_SHA256
    # Preserve local results and all original Colab files, including its own checks.
    DEST.mkdir(parents=True, exist_ok=True)
    for entry in archive.namelist():
        path = (DEST / entry).resolve()
        assert path.is_relative_to(DEST.resolve())
        content = archive.read(entry)
        if path.exists():
            assert path.read_bytes() == content, 'Existing output differs: ' + entry
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

summary = read_json(DEST / 'experiment_summary.json')
freeze = read_json(DEST / 'selection_freeze.json')
reported_checks = read_json(DEST / 'result_integrity_checks.json')
assert summary['settings'] == exp.SETTINGS
assert summary['protocol_version'] == freeze['protocol_version'] == exp.PROTOCOL_VERSION
assert summary['input_provenance']['prepared_package_sha256'] == exp.PREP_SHA256
assert summary['input_provenance']['baseline_package_sha256'] == exp.BASELINE_SHA256
assert summary['input_provenance']['combined_package_sha256'] == exp.file_sha256(ROOT / 'data/packages/review2_lstm_inputs.zip')
assert freeze['test_evaluation_started'] is False
assert datetime.fromisoformat(freeze['completed_utc']) < datetime.fromisoformat(summary['completed_utc'])
assert reported_checks['all_checks_passed'] is True
assert summary['classification_metrics_computed'] is False
assert summary['paper_draft_written'] is False
metrics = pd.read_csv(DEST / 'metrics.csv')
keys = ['dataset', 'split', 'model']
assert len(metrics) == 32 and not metrics.duplicated(keys).any()
indexed_metrics = metrics.set_index(keys).sort_index()
baseline_metrics = pd.read_csv(SOURCE / 'baselines/metrics.csv').set_index(keys).sort_index()
pd.testing.assert_frame_equal(indexed_metrics.loc[baseline_metrics.index], baseline_metrics, check_exact=False, rtol=1e-10, atol=1e-12)

prep = read_json(SOURCE / 'prepared/preprocessing_summary.json')
info_by_name = {d['dataset']: d for d in prep['datasets']}
assert [d['dataset'] for d in summary['datasets']] == list(info_by_name)
assert set(freeze['selected_weight_hashes']) == set(freeze['selected_model_hashes']) == set(info_by_name)
device, verification_runtime = exp.configure_runtime('cpu')
records = []
forecast_values = 0
lstm_values = 0
max_reload_difference = 0.0
max_metric_difference = 0.0
plot_tables_checked = []
group_rows_checked = 0

for record in summary['datasets']:
    name = record['dataset']
    info = info_by_name[name]
    folder = DEST / name
    selected = read_json(folder / 'selected_model.json')
    config = read_json(folder / 'configuration.json')
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    assert selected['configuration'] == config
    assert selected['runtime'] == summary['runtime']
    assert selected['config_hash'] == config_hash
    assert selected['test_used_for_selection'] is False and config['test_used_for_selection'] is False
    local_config = read_json(ROOT / 'results/lstm' / name / 'configuration.json')
    for key in config:
        if key not in {'runtime_device_type', 'runtime_torch_version'}:
            assert config[key] == local_config[key], (name, key)
    assert config['runtime_device_type'] == summary['runtime']['device_type']
    assert config['runtime_torch_version'] == summary['runtime']['torch']
    assert exp.file_sha256(folder / 'best_weights.pt') == selected['best_weight_sha256'] == freeze['selected_weight_hashes'][name]
    assert exp.file_sha256(folder / 'selected_model.json') == freeze['selected_model_hashes'][name]
    arrays, windows = exp.load_recording(SOURCE, info)
    assert config['target_mean'] == arrays['target_mean'] and config['target_std'] == arrays['target_std']
    assert config['feature_names'] == info['feature_names'] == record['feature_names']
    assert config['history_steps'] == info['history_steps']
    assert config['horizon_steps'] == info['horizon_steps']
    assert record['forecast_horizon_seconds'] == info['horizon_steps'] * info['cadence_seconds']
    stride = exp.SETTINGS['antarex_training_stride' if name.startswith('antarex') else 'westermo_training_stride']
    train = windows[windows['split'].eq('train')].iloc[::stride]
    origins = train['origin_index'].to_numpy(dtype=np.int64)
    np.testing.assert_array_equal(np.load(folder / 'training_origins.npy', allow_pickle=False), origins)
    assert config['training_origin_sha256'] == hashlib.sha256(origins.astype('<i8').tobytes()).hexdigest()
    assert len(origins) == config['training_origin_count'] == selected['training_origin_count'] == record['training_origin_count']
    assert selected['training_stride'] == record['training_stride'] == stride
    assert len(windows[windows['split'].eq('validation')]) == selected['validation_origin_count'] == config['validation_origin_count']

    # Safe loading only: no artifact code execution or unrestricted pickle loading.
    weights = torch.load(folder / 'best_weights.pt', map_location='cpu', weights_only=True)
    checkpoint = torch.load(folder / 'last_checkpoint.pt', map_location='cpu', weights_only=True)
    assert checkpoint['config_hash'] == config_hash
    history = pd.read_csv(folder / 'training_history.csv')
    pd.testing.assert_frame_equal(history, pd.DataFrame(checkpoint['history']), check_exact=False, rtol=1e-10, atol=1e-12)
    assert checkpoint['epoch'] == len(history) == selected['epochs_run'] == record['epochs_run']
    np.testing.assert_array_equal(history['epoch'], np.arange(1, len(history) + 1))
    best_row = history.sort_values(['validation_rmse_fraction', 'epoch']).iloc[0]
    assert int(best_row['epoch']) == selected['best_epoch'] == checkpoint['best_epoch'] == record['best_epoch']
    np.testing.assert_allclose(best_row['validation_rmse_fraction'], selected['best_validation_rmse_fraction'], rtol=1e-10, atol=1e-12)
    assert selected['best_validation_rmse_fraction'] == checkpoint['best']
    assert not any(exp.should_stop(checkpoint['history'][:i], exp.SETTINGS['patience']) for i in range(1, len(history)))
    stopped = exp.should_stop(checkpoint['history'], exp.SETTINGS['patience'])
    assert selected['stop_reason'] == ('validation_patience' if stopped else 'max_epochs')
    assert len(history) <= exp.SETTINGS['max_epochs'] and (stopped or len(history) == exp.SETTINGS['max_epochs'])
    np.testing.assert_allclose(history['epoch_seconds'].sum(), selected['training_seconds_including_validation'], rtol=1e-10, atol=1e-12)
    assert checkpoint['cumulative_seconds'] == selected['training_seconds_including_validation'] == record['training_seconds_including_validation']
    model = exp.MemoryLSTM(len(info['feature_names']), exp.SETTINGS['hidden_units']).to(device)
    model.load_state_dict(weights, strict=True)
    assert sum(p.numel() for p in model.parameters()) == selected['parameter_count'] == record['parameter_count']
    if selected['best_epoch'] == len(history):
        for key in weights:
            assert torch.equal(weights[key], checkpoint['model'][key])

    dataset_max_difference = 0.0
    for split in ['validation', 'test']:
        frame = pd.read_csv(folder / (split + '_predictions.csv.gz'))
        baseline = pd.read_csv(SOURCE / 'baselines' / name / (split + '_predictions.csv.gz'))
        pd.testing.assert_frame_equal(frame[baseline.columns], baseline, check_exact=False, rtol=1e-10, atol=1e-12)
        w = windows[windows['split'].eq(split)]
        index_columns = ['origin_index', 'target_index', 'origin_timestamp', 'target_timestamp']
        np.testing.assert_array_equal(frame[index_columns], w[index_columns])
        o = w['origin_index'].to_numpy(dtype=np.int64)
        z = w['target_index'].to_numpy(dtype=np.int64)
        np.testing.assert_allclose(frame['actual'], arrays['target_memory_pressure'][z], rtol=0, atol=1e-15)
        np.testing.assert_allclose(frame['leak_active_at_origin'], arrays['leak_active'][o], rtol=0, atol=0, equal_nan=True)
        np.testing.assert_allclose(frame['leak_active_at_target'], arrays['leak_active'][z], rtol=0, atol=0, equal_nan=True)
        raw = exp.predict_raw(model, arrays, o, info['history_steps'], device, exp.SETTINGS['evaluation_batch_size'])
        # Same tolerance declared in the original notebook; environments differ.
        np.testing.assert_allclose(raw, frame['lstm_raw'], rtol=1e-6, atol=1e-7)
        difference = float(np.max(np.abs(raw - frame['lstm_raw'])))
        dataset_max_difference = max(dataset_max_difference, difference)
        max_reload_difference = max(max_reload_difference, difference)
        lstm_values += len(frame)
        for method in METHODS:
            np.testing.assert_allclose(frame[method], np.clip(frame[method + '_raw'], 0, 1), rtol=0, atol=1e-15)
            calculated = exp.regression_errors(frame['actual'], frame[method])
            stored = indexed_metrics.loc[(name, split, method)]
            assert stored['n'] == calculated['n'] == len(frame)
            assert stored['clipped_forecasts'] == int(((frame[method + '_raw'] < 0) | (frame[method + '_raw'] > 1)).sum())
            for key in SCORES:
                np.testing.assert_allclose(calculated[key], stored[key], rtol=1e-10, atol=1e-12)
                max_metric_difference = max(max_metric_difference, abs(calculated[key] - stored[key]))
            forecast_values += len(frame)
        if split == 'validation':
            np.testing.assert_allclose(exp.regression_errors(frame['actual'], frame['lstm'])['rmse_fraction'], selected['best_validation_rmse_fraction'], rtol=1e-10, atol=1e-12)
        else:
            assert len(frame) == record['test_origins']
            for path in folder.glob('first_test_*.csv'):
                plotted = pd.read_csv(path)
                reference = pd.read_csv(SOURCE / 'baselines' / name / path.name)
                np.testing.assert_array_equal(plotted[index_columns], reference[index_columns])
                expected = frame.set_index('origin_index').loc[plotted['origin_index']].reset_index()
                pd.testing.assert_frame_equal(plotted, expected, check_exact=False, rtol=1e-10, atol=1e-12)
                plot_tables_checked.append(path.relative_to(DEST).as_posix())
            if name == 'antarex_mono':
                groups = pd.read_csv(folder / 'test_forecast_errors_by_leak_state.csv')
                assert len(groups) == 8
                for row in groups.to_dict('records'):
                    flag = 1 if row['group'] == 'leak_active_at_origin' else 0
                    part = frame[frame['leak_active_at_origin'].eq(flag)]
                    calculated = exp.regression_errors(part['actual'], part[row['model']])
                    assert row['n'] == calculated['n']
                    for key in SCORES:
                        np.testing.assert_allclose(row[key], calculated[key], rtol=1e-10, atol=1e-12)
                    group_rows_checked += 1
    records.append({'dataset': name, 'best_epoch': selected['best_epoch'], 'epochs_run': len(history),
                    'training_origins': len(origins), 'test_origins': record['test_origins'],
                    'protocol_configuration_matches': True, 'validation_selection_and_stopping_consistent': True,
                    'resume_checkpoint_safely_loadable': True, 'baseline_columns_unchanged': True,
                    'max_reloaded_forecast_difference_fraction': dataset_max_difference})
    print(name, 'passed', 'reload max difference', dataset_max_difference, flush=True)

figures = []
for path in sorted(DEST.rglob('*.png')):
    with Image.open(path) as im:
        im.verify()
    figures.append(path.relative_to(DEST).as_posix())
assert len(figures) == 8 and len(list(DEST.rglob('*.pdf'))) == 8
assert len(plot_tables_checked) == 3
assert forecast_values == reported_checks['saved_forecast_values_checked'] == 557056
assert lstm_values == 139264

# Describe fresh-training variation rather than requiring local and Colab equality.
local_metrics = pd.read_csv(ROOT / 'results/lstm/metrics.csv').set_index(keys)
comparison = []
for name in info_by_name:
    lstm = indexed_metrics.loc[(name, 'test', 'lstm')]
    arima = indexed_metrics.loc[(name, 'test', 'arima')]
    local_lstm = local_metrics.loc[(name, 'test', 'lstm')]
    comparison.append({'dataset': name, 'colab_lstm_mae_pp': float(lstm['mae_percentage_points']),
                       'colab_lstm_rmse_pp': float(lstm['rmse_percentage_points']),
                       'arima_mae_pp': float(arima['mae_percentage_points']),
                       'arima_rmse_pp': float(arima['rmse_percentage_points']),
                       'relative_rmse_reduction_vs_arima_percent': float(100 * (1 - lstm['rmse_fraction'] / arima['rmse_fraction'])),
                       'local_lstm_mae_pp': float(local_lstm['mae_percentage_points']),
                       'local_lstm_rmse_pp': float(local_lstm['rmse_percentage_points'])})

# Confirm original extracted files were untouched by the independent audit.
for item in manifest['files']:
    assert exp.file_sha256(DEST / item['entry']) == item['sha256']
audit = {'verification_completed_utc': datetime.now(timezone.utc).isoformat(),
         'all_checks_passed': True, 'colab_package': str(PACKAGE.relative_to(ROOT)),
         'colab_package_sha256': exp.file_sha256(PACKAGE), 'colab_package_bytes': PACKAGE.stat().st_size,
         'verified_result_files': len(manifest['files']), 'input_provenance': summary['input_provenance'],
         'forecast_values_checked': forecast_values, 'lstm_forecasts_recomputed_from_saved_weights': lstm_values,
         'metric_rows_recomputed': len(metrics), 'leak_state_metric_rows_recomputed': group_rows_checked,
         'maximum_reload_difference_fraction': max_reload_difference,
         'maximum_metric_difference_across_reported_columns': max_metric_difference,
         'forecast_reload_tolerance': {'rtol': 1e-6, 'atol': 1e-7},
         'metric_tolerance': {'rtol': 1e-10, 'atol': 1e-12},
         'datasets': records, 'test_comparison': comparison,
         'valid_png_figures': figures, 'plot_tables_verified': plot_tables_checked,
         'colab_runtime': summary['runtime'], 'verification_runtime': verification_runtime,
         'colab_experiment_seconds': summary['elapsed_this_run_seconds'],
         'original_integrity_report_preserved': True, 'all_extracted_result_hashes_unchanged': True,
         'scope': 'Artifact consistency and independent inference/scoring; no retraining or warning evaluation. Saved metadata is not an independent audit of historical execution order.'}
exp.dump_json(AUDIT, audit)
print(json.dumps(audit, indent=2), flush=True)
