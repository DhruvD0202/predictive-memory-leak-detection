"""Verify the user's warning ZIP without changing the archived experiment."""
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import warning_evaluation as w

PACKAGE = ROOT / 'data/packages/review2_warning_results_colab.zip'
DEST = ROOT / 'results/warnings_colab'
SOURCE = ROOT / 'data/warning_inputs'
AUDIT = ROOT / 'results/verification/colab_warning_verification.json'


def verify_manifest(archive):
    names = archive.namelist()
    manifest = json.loads(archive.read('MANIFEST.json'))
    entries = [f['entry'] for f in manifest['files']]
    assert len(names) == len(set(names)) and len(entries) == len(set(entries))
    assert set(names) == set(entries) | {'MANIFEST.json'}
    for item in manifest['files']:
        assert (DEST / item['entry']).resolve().is_relative_to(DEST.resolve())
        data = archive.read(item['entry'])
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    return manifest


# Recheck the original input ZIPs and the exact extracted inputs used below.
for name, digest, subdir in [('review2_preprocessed_colab.zip', w.PREP_SHA256, 'prepared'),
                             ('review2_lstm_results_colab.zip', w.FORECAST_SHA256, 'forecasts')]:
    path = ROOT / 'data/packages' / name
    assert w.file_sha256(path) == digest
    with zipfile.ZipFile(path) as archive:
        source_manifest = verify_manifest(archive)
        for item in source_manifest['files']:
            assert w.file_sha256(SOURCE / subdir / item['entry']) == item['sha256']

with zipfile.ZipFile(PACKAGE) as archive:
    manifest = verify_manifest(archive)
    assert manifest['protocol_version'] == w.PROTOCOL_VERSION
    assert manifest['prepared_package_sha256'] == w.PREP_SHA256
    assert manifest['forecast_package_sha256'] == w.FORECAST_SHA256
    assert set(archive.namelist()) == {p.relative_to(ROOT / 'results/warnings').as_posix()
                                      for p in (ROOT / 'results/warnings').rglob('*') if p.is_file()} | {'MANIFEST.json'}
    DEST.mkdir(parents=True, exist_ok=True)
    for name in archive.namelist():
        path = (DEST / name).resolve()
        assert path.is_relative_to(DEST.resolve())
        data = archive.read(name)
        if path.exists():
            assert path.read_bytes() == data, 'Existing extracted result differs: ' + name
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

freeze = w.read_json(DEST / 'selection_freeze.json')
summary = w.read_json(DEST / 'experiment_summary.json')
reported_checks = w.read_json(DEST / 'result_integrity_checks.json')
local_freeze = w.read_json(ROOT / 'results/warnings/selection_freeze.json')
assert summary['settings'] == freeze['settings'] == w.SETTINGS
assert summary['protocol_version'] == freeze['protocol_version'] == w.PROTOCOL_VERSION
assert summary['input_provenance'] == freeze['input_provenance'] == local_freeze['input_provenance']
assert summary['input_provenance']['combined_package_sha256'] == w.file_sha256(ROOT / 'data/packages/review2_warning_inputs.zip')
assert summary['input_provenance']['protocol_sha256'] == w.file_sha256(ROOT / 'research/WARNING_PROTOCOL.md')
assert freeze['selection_partition'] == 'antarex_validation'
assert freeze['selected'] == local_freeze['selected']
assert freeze['test_warning_evaluation_started'] is False
assert datetime.fromisoformat(freeze['completed_utc']) < datetime.fromisoformat(summary['completed_utc'])
for flag in ['model_retraining_performed', 'warning_test_tuning_performed', 'westermo_leak_metrics_computed',
             'memory_exhaustion_evaluated', 'paper_draft_written']:
    assert summary[flag] is False
assert reported_checks['all_checks_passed'] is True

# Run the project reconstruction, capturing its audit instead of overwriting
# the user's original result_integrity_checks.json.
captured = []
original_dump = w.dump_json
def capture_audit(path, value):
    assert Path(path) == DEST / 'result_integrity_checks.json'
    captured.append(value)
w.dump_json = capture_audit
try:
    recomputed = w.verify_results(SOURCE, DEST)
finally:
    w.dump_json = original_dump
assert captured == [recomputed] and recomputed == reported_checks
print('Source-based warning, metric, selection and event reconstruction passed.', flush=True)

points = pd.read_csv(DEST / 'antarex_point_metrics.csv')
events = pd.read_csv(DEST / 'antarex_event_outcomes.csv')
count = event_count = 0
max_slope_difference = max_colab_local_difference = 0.
records = []
for name, split in [('antarex_mono', 'validation'), ('antarex_mono', 'test'),
                    ('westermo_1', 'test'), ('westermo_2', 'test'), ('westermo_3', 'test')]:
    prefix = 'antarex' if name == 'antarex_mono' else name
    filename = prefix + '_' + split + '_warnings.csv.gz'
    frame = pd.read_csv(DEST / filename)
    local = pd.read_csv(ROOT / 'results/warnings' / filename)
    pd.testing.assert_frame_equal(frame, local, check_exact=False, rtol=1e-10, atol=1e-12)
    numeric = frame.select_dtypes(include=['number']).columns
    differences = np.abs(frame[numeric].to_numpy() - local[numeric].to_numpy())
    max_colab_local_difference = max(max_colab_local_difference, float(np.nanmax(differences)))
    info = w.read_json(SOURCE / 'prepared' / name / 'summary.json')
    cadence = info['cadence_seconds']
    times = frame['origin_timestamp'].to_numpy(dtype=np.int64)
    origins = frame['origin_index'].to_numpy(dtype=np.int64)
    with np.load(SOURCE / 'prepared' / name / 'model_arrays.npz', allow_pickle=False) as arrays:
        y = arrays['target_memory_pressure'].astype(np.float64)
    past = y[origins[:, None] - np.arange(11, -1, -1)]
    slope = np.polynomial.polynomial.polyfit(np.arange(12) * cadence / 60, past.T, 1)[1] * 100
    np.testing.assert_allclose(slope, frame['observed_growth_pp_per_minute'], rtol=1e-9, atol=1e-11)
    max_slope_difference = max(max_slope_difference, float(np.max(np.abs(slope - frame['observed_growth_pp_per_minute']))))
    contiguous = (np.diff(times)[1:] == cadence) & (np.diff(times)[:-1] == cadence)
    for method in w.METHODS:
        threshold = freeze['selected'][method]['threshold_pp_per_minute']
        if threshold is None:
            expected = np.zeros(len(times), dtype=bool)
        else:
            condition = frame[method + '_score'].to_numpy() >= threshold
            expected = np.r_[False, False, condition[:-2] & condition[1:-1] & condition[2:] & contiguous]
        np.testing.assert_array_equal(expected, frame[method + '_warning'])
        starts = expected & np.r_[True, (~expected[:-1]) | (np.diff(times) != cadence)]
        np.testing.assert_array_equal(starts, frame[method + '_alarm_start'])
        np.testing.assert_array_equal(expected, local[method + '_warning'])
        count += len(frame)
        if name == 'antarex_mono':
            truth = frame['leak_active'].to_numpy().astype(bool)
            tn, fp, fn, tp = np.bincount(2 * truth.astype(int) + expected.astype(int), minlength=4)
            row = points[(points['split'] == split) & (points['method'] == method)].iloc[0]
            np.testing.assert_array_equal([tn, fp, fn, tp], row[['tn', 'fp', 'fn', 'tp']].to_numpy(dtype=int))
            for metric, numerator, denominator in [('precision', tp, tp + fp), ('recall', tp, tp + fn), ('f1', 2 * tp, 2 * tp + fp + fn)]:
                if denominator:
                    np.testing.assert_allclose(row[metric], numerator / denominator, rtol=1e-10, atol=1e-12)
                else:
                    assert pd.isna(row[metric])
            false_starts = int((starts & ~truth).sum())
            assert false_starts == row['false_alarm_starts']
            np.testing.assert_allclose(false_starts / ((tn + fp) * cadence / 3600), row['false_alarm_starts_per_non_leak_hour'], rtol=1e-10, atol=1e-12)
            for event in events[(events['split'] == split) & (events['method'] == method)].itertuples(index=False):
                first_grid = times[0] + int(np.ceil((event.start - times[0]) / cadence)) * cadence
                needed = np.arange(first_grid - cadence, event.end, cadence)
                eligible = event.start >= times[0] and event.end <= times[-1] + cadence and len(needed) > 1 and np.isin(needed, times).all()
                assert event.eligible == eligible
                if eligible:
                    hits = times[starts & (times >= event.start) & (times < event.end)]
                    assert event.detected == bool(len(hits))
                    if len(hits):
                        assert event.first_alarm_start == hits[0] and event.delay_seconds == hits[0] - event.start
                    else:
                        assert pd.isna(event.first_alarm_start) and pd.isna(event.delay_seconds)
                event_count += 1
        else:
            assert not frame['label_known'].any() and frame['leak_active'].isna().all()
    records.append({'dataset': name, 'split': split, 'origins': len(frame), 'warning_decisions_match_local': True,
                    'warning_states_and_alarm_starts_independently_reconstructed': True})

tables = ['validation_candidates.csv', 'antarex_point_metrics.csv', 'antarex_event_metrics.csv',
          'antarex_event_outcomes.csv', 'westermo_descriptive_alarms.csv']
for filename in tables:
    pd.testing.assert_frame_equal(pd.read_csv(DEST / filename), pd.read_csv(ROOT / 'results/warnings' / filename),
                                  check_exact=False, rtol=1e-10, atol=1e-12)
figures = sorted(p.name for p in DEST.glob('*.png'))
assert len(figures) == 3 and len(list(DEST.glob('*.pdf'))) == 3
for name in figures:
    with Image.open(DEST / name) as picture:
        picture.verify()
for path in DEST.glob('*.pdf'):
    assert path.read_bytes().startswith(b'%PDF')
for item in manifest['files']:
    assert w.file_sha256(DEST / item['entry']) == item['sha256']
assert count == 402364 and event_count == 264
audit = {'verification_completed_utc': datetime.now(timezone.utc).isoformat(), 'all_checks_passed': True,
         'colab_package': str(PACKAGE.relative_to(ROOT)), 'colab_package_sha256': w.file_sha256(PACKAGE),
         'colab_package_bytes': PACKAGE.stat().st_size, 'verified_result_files': len(manifest['files']),
         'input_provenance': summary['input_provenance'], 'project_reconstruction': recomputed,
         'warning_decisions_independently_checked': count, 'event_outcomes_independently_checked': event_count,
         'slopes_independently_recalculated': count // len(w.METHODS),
         'maximum_slope_difference_pp_per_minute': max_slope_difference,
         'maximum_colab_local_numeric_timeline_difference': max_colab_local_difference,
         'selected_thresholds_match_local': True, 'classification_and_event_tables_match_local': True,
         'colab_runtime': summary['runtime'], 'colab_experiment_seconds': summary['elapsed_seconds'],
         'timing_scope': summary['timing_scope'], 'datasets': records, 'valid_png_figures': figures,
         'original_integrity_report_and_all_extracted_files_preserved': True,
         'scope': 'Saved experiment verification, independent reconstruction and cross-runtime comparison. No parameter changes or new experiments. Metadata consistency does not independently prove historical execution order.'}
w.dump_json(AUDIT, audit)
print(json.dumps(audit, indent=2), flush=True)
