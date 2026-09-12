"""Independent post-run numerical and archive audit; no model or threshold changes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/warnings'
SOURCE = ROOT / 'data/warning_inputs'
METHODS = ['trend_only', 'arima_growth', 'lstm_growth', 'always_off']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


first = json.loads((ROOT / 'results/verification/warning_first_execution.json').read_text())
freeze = json.loads((OUT / 'selection_freeze.json').read_text())
for name, digest in first['metric_file_hashes'].items():
    assert sha(OUT / name) == digest, name
assert first['freeze']['selected'] == freeze['selected']
assert freeze['settings'] == first['freeze']['settings']
summary = json.loads((OUT / 'experiment_summary.json').read_text())
assert datetime.fromisoformat(freeze['completed_utc']) < datetime.fromisoformat(summary['completed_utc'])
assert summary['selection_freeze_sha256'] == sha(OUT / 'selection_freeze.json')
points = pd.read_csv(OUT / 'antarex_point_metrics.csv')
events = pd.read_csv(OUT / 'antarex_event_outcomes.csv')
count = 0
event_count = 0
max_slope_difference = 0.
for name, split in [('antarex_mono', 'validation'), ('antarex_mono', 'test'), ('westermo_1', 'test'), ('westermo_2', 'test'), ('westermo_3', 'test')]:
    prefix = 'antarex' if name == 'antarex_mono' else name
    frame = pd.read_csv(OUT / (prefix + '_' + split + '_warnings.csv.gz'))
    info = json.loads((SOURCE / 'prepared' / name / 'summary.json').read_text())
    cadence = info['cadence_seconds']
    times = frame['origin_timestamp'].to_numpy(dtype=np.int64)
    with np.load(SOURCE / 'prepared' / name / 'model_arrays.npz', allow_pickle=False) as z:
        y = z['target_memory_pressure'].astype(np.float64)
    origins = frame['origin_index'].to_numpy(dtype=np.int64)
    past = y[origins[:, None] - np.arange(11, -1, -1)]
    slope = np.polynomial.polynomial.polyfit(np.arange(12) * cadence / 60, past.T, 1)[1] * 100
    np.testing.assert_allclose(slope, frame['observed_growth_pp_per_minute'], rtol=1e-9, atol=1e-11)
    max_slope_difference = max(max_slope_difference, float(np.max(np.abs(slope - frame['observed_growth_pp_per_minute']))))
    gap_free_triplet = (np.diff(times)[1:] == cadence) & (np.diff(times)[:-1] == cadence)
    for method in METHODS:
        threshold = freeze['selected'][method]['threshold_pp_per_minute']
        if threshold is None:
            expected = np.zeros(len(times), dtype=bool)
        else:
            condition = frame[method + '_score'].to_numpy() >= threshold
            expected = np.r_[False, False, condition[:-2] & condition[1:-1] & condition[2:] & gap_free_triplet]
        np.testing.assert_array_equal(expected, frame[method + '_warning'])
        new_alarm = expected & np.r_[True, (~expected[:-1]) | (np.diff(times) != cadence)]
        np.testing.assert_array_equal(new_alarm, frame[method + '_alarm_start'])
        count += len(frame)
        if name == 'antarex_mono':
            truth = frame['leak_active'].to_numpy().astype(bool)
            counts = np.bincount(2 * truth.astype(int) + expected.astype(int), minlength=4)
            row = points[(points['split'] == split) & (points['method'] == method)].iloc[0]
            np.testing.assert_array_equal(counts, row[['tn', 'fp', 'fn', 'tp']].to_numpy(dtype=int))
            for e in events[(events['split'] == split) & (events['method'] == method)].itertuples(index=False):
                first_grid = times[0] + int(np.ceil((e.start - times[0]) / cadence)) * cadence
                needed = np.arange(first_grid - cadence, e.end, cadence)
                eligible = e.start >= times[0] and e.end <= times[-1] + cadence and len(needed) > 1 and np.isin(needed, times).all()
                assert e.eligible == eligible
                if eligible:
                    hits = times[new_alarm & (times >= e.start) & (times < e.end)]
                    assert e.detected == bool(len(hits))
                    if len(hits):
                        assert e.first_alarm_start == hits[0]
                        assert e.delay_seconds == hits[0] - e.start
                    else:
                        assert pd.isna(e.first_alarm_start) and pd.isna(e.delay_seconds)
                event_count += 1

package = ROOT / 'data/packages/review2_warning_results.zip'
with zipfile.ZipFile(package) as archive:
    manifest = json.loads(archive.read('MANIFEST.json'))
    assert len(archive.namelist()) == len(manifest['files']) + 1
    assert len(archive.namelist()) == len(set(archive.namelist()))
    for item in manifest['files']:
        content = archive.read(item['entry'])
        assert len(content) == item['bytes'] and hashlib.sha256(content).hexdigest() == item['sha256']
        assert sha(OUT / item['entry']) == item['sha256']
pngs = list(OUT.glob('*.png'))
pdfs = list(OUT.glob('*.pdf'))
assert len(pngs) == len(pdfs) == 3
for path in pngs:
    with Image.open(path) as im:
        im.verify()
for path in pdfs:
    assert path.read_bytes().startswith(b'%PDF')
notebook = json.loads((ROOT / 'notebooks/04_leak_warning_colab.ipynb').read_text(encoding='utf-8'))
assert notebook['metadata']['execution_evidence']['all_cells_succeeded']
code_cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
assert len(code_cells) == 8 and all(c['execution_count'] for c in code_cells)
assert hashlib.sha256(''.join(code_cells[2]['source']).encode()).hexdigest() == sha(ROOT / 'src/warning_evaluation.py')
assert notebook['metadata']['protocol_sha256'] == sha(ROOT / 'research/WARNING_PROTOCOL.md')
audit = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'all_checks_passed': True,
         'warning_decisions_independently_reconstructed': count, 'event_outcomes_independently_checked': event_count,
         'least_squares_slopes_independently_recomputed': count // len(METHODS),
         'maximum_slope_difference_pp_per_minute': max_slope_difference,
         'original_thresholds_unchanged': True, 'first_run_metric_and_candidate_files_unchanged': True,
         'verified_result_files': len(manifest['files']), 'all_three_pngs_decode': True, 'three_pdf_headers_valid': True,
         'result_package_sha256': sha(package), 'result_package_bytes': package.stat().st_size,
         'notebook_execution': notebook['metadata']['execution_evidence'],
         'scope': 'Independent vectorized warning confirmation, least-squares slopes, event outcomes, confusion counts and archive audit; no parameter selection or training.'}
(ROOT / 'results/verification/warning_output_verification.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
print(json.dumps(audit, indent=2))
