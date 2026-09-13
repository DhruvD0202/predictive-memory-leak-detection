"""Read-only experiment replay and opt-in local telemetry collection."""
from __future__ import annotations

import csv
from collections import deque
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import threading
import time
import uuid
import zipfile

DATASETS = {'antarex_mono': ('Antarex mono', 5, 60),
            'westermo_1': ('Westermo 1', 30, 300),
            'westermo_2': ('Westermo 2', 30, 300),
            'westermo_3': ('Westermo 3', 30, 300)}
METHODS = ('persistence', 'linear_trend', 'arima', 'lstm')
RULES = ('trend_only', 'arima_growth', 'lstm_growth', 'always_off')
PREP_SHA256 = '287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2'


def prepared_manifest(package):
    with Path(package).open('rb') as handle:
        if hashlib.file_digest(handle, 'sha256').hexdigest() != PREP_SHA256:
            raise ValueError('Use the verified review2_preprocessed_colab.zip package')
    with zipfile.ZipFile(package) as archive:
        return json.loads(archive.read('MANIFEST.json'))


def prepare_inputs(package, root):
    manifest = prepared_manifest(package)
    destination = (Path(root) / 'data/demo_inputs/prepared').resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package) as archive:
        for item in manifest['files']:
            path = (destination / item['entry']).resolve()
            if not path.is_relative_to(destination):
                raise ValueError('Invalid prepared archive path')
            content = archive.read(item['entry'])
            if len(content) != item['bytes'] or hashlib.sha256(content).hexdigest() != item['sha256']:
                raise ValueError('Invalid prepared archive content')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (destination / 'MANIFEST.json').write_bytes(archive.read('MANIFEST.json'))
    return destination


def read_csv(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def finite(value):
    if value in ('', None):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def typed_row(row):
    result = {}
    for key, value in row.items():
        if value in ('True', 'False'):
            result[key] = value == 'True'
        else:
            try:
                result[key] = finite(value)
            except (ValueError, TypeError):
                result[key] = value
    return result


def json_bytes(value):
    return json.dumps(value, allow_nan=False, separators=(',', ':')).encode('utf-8')


def verify_manifest(folder):
    folder = Path(folder).resolve()
    manifest = json.loads((folder / 'MANIFEST.json').read_text(encoding='utf-8'))
    seen = set()
    for item in manifest['files']:
        path = (folder / item['entry']).resolve()
        if not path.is_relative_to(folder) or item['entry'] in seen:
            raise ValueError('Invalid result manifest entry')
        seen.add(item['entry'])
        with path.open('rb') as handle:
            digest = hashlib.file_digest(handle, 'sha256').hexdigest()
        if path.stat().st_size != item['bytes'] or digest != item['sha256']:
            raise ValueError('Result integrity check failed: ' + item['entry'])
    return len(seen)


class ReplayRepository:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.forecasts = self.root / 'results/lstm_colab'
        self.warnings = self.root / 'results/warnings_colab'
        self.verified_files = verify_manifest(self.forecasts) + verify_manifest(self.warnings)
        self.metrics = [typed_row(r) for r in read_csv(self.forecasts / 'metrics.csv') if r['split'] == 'test']
        self.point_metrics = [typed_row(r) for r in read_csv(self.warnings / 'antarex_point_metrics.csv') if r['split'] == 'test']
        self.event_metrics = [typed_row(r) for r in read_csv(self.warnings / 'antarex_event_metrics.csv') if r['split'] == 'test']
        self.thresholds = json.loads((self.warnings / 'selection_freeze.json').read_text())['selected']
        self.records = {}
        self.predictions = {}
        self.models = {}
        self.lock = threading.RLock()
        self.prepared = next((p for p in [self.root / 'data/demo_inputs/prepared', self.root / 'data/lstm_inputs/prepared',
                                           self.root / 'data/warning_inputs/prepared']
                              if (p / 'preprocessing_summary.json').exists()), None)
        for dataset in DATASETS:
            warning_name = 'antarex' if dataset == 'antarex_mono' else dataset
            warnings = [typed_row(r) for r in read_csv(self.warnings / f'{warning_name}_test_warnings.csv.gz')]
            predictions = [typed_row(r) for r in read_csv(self.forecasts / dataset / 'test_predictions.csv.gz')]
            if len(warnings) != len(predictions) or not warnings:
                raise ValueError('Forecast/warning coverage differs: ' + dataset)
            cadence, horizon = DATASETS[dataset][1:]
            previous = None
            for w, p in zip(warnings, predictions):
                if w['origin_timestamp'] != p['origin_timestamp'] or w['target_timestamp'] != p['target_timestamp']:
                    raise ValueError('Forecast/warning alignment differs: ' + dataset)
                if p['target_timestamp'] - p['origin_timestamp'] != horizon:
                    raise ValueError('Unexpected forecast horizon')
                if previous is not None and w['origin_timestamp'] <= previous:
                    raise ValueError('Timestamps are not increasing')
                previous = w['origin_timestamp']
                if dataset != 'antarex_mono' and (w['label_known'] or w['leak_active'] is not None):
                    raise ValueError('Westermo must remain unlabeled')
                for model in ('arima', 'lstm'):
                    if not math.isclose(w[model + '_forecast'], p[model], abs_tol=1e-12):
                        raise ValueError('Forecast values differ')
            self.records[dataset], self.predictions[dataset] = warnings, predictions

    def metadata(self):
        datasets = []
        for name, (title, cadence, horizon) in DATASETS.items():
            records = self.records[name]
            first_leak = next((i for i, r in enumerate(records) if r['leak_active'] == 1), None)
            datasets.append({'id': name, 'title': title, 'cadence': cadence, 'horizon': horizon,
                             'count': len(records), 'first_leak_index': first_leak,
                             'start': records[0]['origin_timestamp'], 'end': records[-1]['origin_timestamp'],
                             'features': json.loads((self.forecasts / name / 'configuration.json').read_text())['feature_names']})
        return {'datasets': datasets, 'verified_files': self.verified_files,
                'forecast_metrics': self.metrics, 'warning_metrics': self.point_metrics,
                'event_metrics': self.event_metrics, 'thresholds': self.thresholds,
                'inference_available': self.prepared is not None,
                'source': 'Verified Colab test recordings', 'exhaustion_evaluated': False}

    def bounds(self, dataset, index, window):
        if dataset not in DATASETS:
            raise ValueError('Unknown recording')
        if not 0 <= index < len(self.records[dataset]) or not 2 <= window <= 720:
            raise ValueError('Replay index/window outside allowed range')
        return max(0, index - window + 1), index + 1

    def replay(self, dataset, index, window=360):
        start, end = self.bounds(dataset, index, window)
        rows, predictions = self.records[dataset], self.predictions[dataset]
        current = rows[index]
        past = [{'t': r['origin_timestamp'], 'memory': r['memory_pressure_at_origin'],
                 'leak': r['leak_active'] if r['label_known'] else None,
                 'trend_warning': r['trend_only_warning'], 'lstm_warning': r['lstm_growth_warning']}
                for r in rows[start:end]]
        issued = [{'origin': p['origin_timestamp'], 'target': p['target_timestamp'],
                   **{m: p[m] for m in METHODS}} for p in predictions[start:end]]
        alarms = []
        for rule in RULES:
            alarms.extend([{'t': r['origin_timestamp'], 'rule': rule,
                            'recorded_leak': r['leak_active'] if r['label_known'] else None}
                           for r in rows[:end] if r[rule + '_alarm_start']][-20:])
        alarms.sort(key=lambda item: item['t'], reverse=True)
        # Future actual values and future labels are deliberately absent from this API.
        return {'dataset': dataset, 'index': index, 'count': len(rows), 'current': current,
                'observations': past, 'forecasts': issued, 'alarms': alarms,
                'cadence': DATASETS[dataset][1], 'horizon': DATASETS[dataset][2]}

    def export(self, dataset, index, window):
        start, end = self.bounds(dataset, index, window)
        output = io.StringIO(newline='')
        fields = list(self.records[dataset][0]) + ['persistence_forecast', 'linear_trend_forecast']
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row, pred in zip(self.records[dataset][start:end], self.predictions[dataset][start:end]):
            writer.writerow({**row, 'persistence_forecast': pred['persistence'], 'linear_trend_forecast': pred['linear_trend']})
        return output.getvalue().encode('utf-8')

    def infer(self, dataset, index):
        self.bounds(dataset, index, 2)
        started = time.perf_counter()
        if self.prepared is None:
            raise ValueError('Restore the verified preprocessing package first; see README.')
        import numpy as np
        import torch
        from .lstm_forecasting import MemoryLSTM, gather_history
        with self.lock:
            if dataset not in self.models:
                selected = json.loads((self.forecasts / dataset / 'selected_model.json').read_text())
                config = selected['configuration']
                with np.load(self.prepared / dataset / 'model_arrays.npz', allow_pickle=False) as z:
                    features = z['features'].copy()
                    names = z['feature_names'].tolist()
                if names != config['feature_names']:
                    raise ValueError('Input feature order differs from model configuration')
                manifest = prepared_manifest(self.root / 'data/packages/review2_preprocessed_colab.zip') if not (self.prepared / 'MANIFEST.json').exists() else json.loads((self.prepared / 'MANIFEST.json').read_text())
                item = next(r for r in manifest['files'] if r['entry'] == dataset + '/model_arrays.npz')
                with (self.prepared / dataset / 'model_arrays.npz').open('rb') as handle:
                    if hashlib.file_digest(handle, 'sha256').hexdigest() != item['sha256']:
                        raise ValueError('Prepared arrays failed integrity check')
                torch.set_num_threads(2)
                model = MemoryLSTM(len(names), config['settings']['hidden_units']).eval()
                model.load_state_dict(torch.load(self.forecasts / dataset / 'best_weights.pt', map_location='cpu', weights_only=True))
                self.models[dataset] = (model, features, config)
            model, features, config = self.models[dataset]
            origin = int(self.records[dataset][index]['origin_index'])
            with torch.inference_mode():
                value = float(model(torch.from_numpy(gather_history(features, [origin], config['history_steps']))).item())
            prediction = min(1., max(0., value * config['target_std'] + config['target_mean']))
        expected = self.predictions[dataset][index]['lstm']
        difference = abs(prediction - expected)
        return {'prediction': prediction, 'saved_prediction': expected, 'absolute_difference_fraction': difference,
                'matches_saved': difference <= 1e-6, 'elapsed_ms': (time.perf_counter() - started) * 1000,
                'timing_scope': 'request model load (if needed), history assembly and inference; excludes HTTP/browser',
                'history_steps': config['history_steps'], 'origin_index': origin}


class GrowthDetector:
    """Exploratory live rule; actual sample times, past-only inputs, no leak labels."""
    def __init__(self, threshold=.8, cadence=5., history=12, consecutive=3):
        if not math.isfinite(threshold) or threshold <= 0 or cadence <= 0 or history < 2 or consecutive < 1:
            raise ValueError('Invalid growth detector settings')
        self.threshold, self.cadence = threshold, cadence
        self.history, self.consecutive = history, consecutive
        self.samples = deque(maxlen=history)
        self.run = 0
        self.active = False

    def update(self, timestamp, memory):
        if not math.isfinite(timestamp) or not math.isfinite(memory) or not 0 <= memory <= 1:
            raise ValueError('Invalid telemetry sample')
        if self.samples and timestamp <= self.samples[-1][0]:
            raise ValueError('Telemetry time must increase')
        gap = bool(self.samples and timestamp - self.samples[-1][0] > self.cadence * 2.5)
        previous = self.active and not gap
        if gap:
            self.samples.clear()
            self.run = 0
        self.samples.append((timestamp, memory))
        slope = None
        if len(self.samples) == self.history:
            x = [(t - self.samples[0][0]) / 60 for t, _ in self.samples]
            y = [m * 100 for _, m in self.samples]
            xm, ym = sum(x) / len(x), sum(y) / len(y)
            slope = sum((a-xm)*(b-ym) for a,b in zip(x,y)) / sum((a-xm)**2 for a in x)
        self.run = self.run + 1 if slope is not None and slope >= self.threshold else 0
        self.active = self.run >= self.consecutive
        return {'growth_pp_per_minute': slope, 'warning': self.active,
                'alarm_start': self.active and not previous, 'ready': slope is not None,
                'samples_until_ready': max(0, self.history-len(self.samples)),
                'persistence_60s': memory,
                'linear_trend_60s': min(1., max(0., memory + slope/100)) if slope is not None else None}


class SystemSampler:
    def __init__(self):
        import psutil
        self.psutil = psutil
        self.previous = None
        psutil.cpu_percent(interval=None)

    def sample(self):
        p = self.psutil
        now, monotonic = time.time(), time.monotonic()
        memory, swap = p.virtual_memory(), p.swap_memory()
        try:
            disk = p.disk_io_counters()
        except (OSError, p.Error):
            disk = None
        counters = {'disk_read_bytes': disk.read_bytes if disk else None,
                    'disk_write_bytes': disk.write_bytes if disk else None,
                    'page_faults': None, 'major_page_faults': None}
        if platform.system() == 'Linux':
            try:
                fields = dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
                counters['page_faults'] = int(fields['pgfault'])
                counters['major_page_faults'] = int(fields['pgmajfault'])
            except (OSError, KeyError, ValueError):
                pass
        rates = {}
        for key, current in counters.items():
            previous = self.previous[1].get(key) if self.previous else None
            dt = monotonic-self.previous[0] if self.previous else 0
            rates[key + '_per_second'] = (current-previous)/dt if current is not None and previous is not None and current >= previous and dt > 0 else None
        cpu = p.cpu_percent(interval=None)
        result = {'timestamp': now, 'monotonic_seconds': monotonic,
                  'memory_pressure': 1-memory.available/memory.total, 'total_memory_bytes': memory.total,
                  'available_memory_bytes': memory.available, 'cpu_percent': cpu if self.previous else None,
                  'swap_used_bytes': swap.used, **rates}
        self.previous = (monotonic, counters)
        return result


class LiveMonitor:
    def __init__(self, root, cadence=5., max_samples=720):
        self.root, self.cadence, self.max_samples = Path(root), cadence, max_samples
        self.lock = threading.RLock()
        self.rows = []
        self.thread = None
        self.stop_event = threading.Event()
        self.error = None
        self.session = None
        self.threshold = .8

    def start(self, threshold=.8):
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise ValueError('A live session is already running')
            if not math.isfinite(threshold) or not .001 <= threshold <= 100:
                raise ValueError('Growth threshold must be between 0.001 and 100 pp/min')
            sampler = SystemSampler()
            detector = GrowthDetector(threshold, self.cadence)
            self.rows, self.error, self.threshold = [], None, threshold
            self.stop_event.clear()
            self.session = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
            self.folder = self.root / 'results/live' / self.session
            self.folder.mkdir(parents=True, exist_ok=False)
            self.thread = threading.Thread(target=self._run, args=(sampler, detector), daemon=True)
            self.thread.start()
        return self.snapshot()

    def _run(self, sampler, detector):
        try:
            with (self.folder / 'telemetry.csv').open('w', encoding='utf-8', newline='') as handle:
                writer = None
                while not self.stop_event.is_set() and len(self.rows) < self.max_samples:
                    tick = time.monotonic()
                    row = sampler.sample()
                    row.update(detector.update(row['monotonic_seconds'], row['memory_pressure']))
                    if writer is None:
                        writer = csv.DictWriter(handle, fieldnames=list(row))
                        writer.writeheader()
                    writer.writerow(row)
                    handle.flush()
                    with self.lock:
                        self.rows.append(row)
                    self.stop_event.wait(max(0, self.cadence-(time.monotonic()-tick)))
        except Exception as exc:
            with self.lock:
                self.error = str(exc)
        finally:
            with self.lock:
                summary = {'session': self.session, 'platform': platform.system(), 'samples': len(self.rows),
                           'cadence_seconds': self.cadence, 'threshold_pp_per_minute': self.threshold,
                           'leak_labels_available': False, 'lstm_applied': False, 'error': self.error,
                           'rule': '12 past samples, least-squares growth, 3 consecutive qualifying observations',
                           'scope': 'exploratory local monitoring; not a calibrated leak detector'}
            (self.folder / 'summary.json').write_bytes(json_bytes(summary))

    def stop(self):
        self.stop_event.set()
        thread = self.thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout=10)
        return self.snapshot()

    def snapshot(self):
        with self.lock:
            return {'running': bool(self.thread and self.thread.is_alive()), 'session': self.session,
                    'rows': list(self.rows), 'error': self.error, 'cadence': self.cadence,
                    'threshold': self.threshold, 'max_samples': self.max_samples,
                    'platform': platform.system(), 'label_known': False}

    def export(self):
        with self.lock:
            if not self.rows:
                raise ValueError('No live samples to export')
            out = io.StringIO(newline='')
            writer = csv.DictWriter(out, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)
            return out.getvalue().encode('utf-8')
