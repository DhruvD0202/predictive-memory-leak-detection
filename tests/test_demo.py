"""Behavioral checks for causal replay, local monitoring and the dashboard API."""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import make_server
from src.demo_service import GrowthDetector, LiveMonitor, ReplayRepository, json_bytes, typed_row, verify_manifest


class GrowthTests(unittest.TestCase):
    def test_confirmation_and_immediate_clear(self):
        d = GrowthDetector(.8)
        rows = [d.update(i*5, .2+i/1200) for i in range(14)]
        self.assertTrue(all(not r['warning'] for r in rows[:13]))
        self.assertTrue(rows[13]['warning'])
        self.assertTrue(rows[13]['alarm_start'])
        self.assertAlmostEqual(rows[13]['growth_pp_per_minute'], 1.)
        self.assertFalse(d.update(70, .1)['warning'])

    def test_gap_resets_history_and_confirmation(self):
        d = GrowthDetector(.8)
        for i in range(14):
            d.update(i*5, .2+i/1200)
        r = d.update(100, .3)
        self.assertFalse(r['ready'])
        self.assertFalse(r['warning'])
        self.assertEqual(r['samples_until_ready'], 11)

    def test_actual_time_units_and_flat_series(self):
        d = GrowthDetector(.8)
        for i in range(14):
            t = i*5 + (i % 2)*.2
            r = d.update(t, .3+t/6000)
        self.assertAlmostEqual(r['growth_pp_per_minute'], 1.)
        flat = GrowthDetector(.8)
        for i in range(30):
            r = flat.update(i*5, .4)
        self.assertFalse(r['warning'])
        self.assertAlmostEqual(r['linear_trend_60s'], .4)

    def test_invalid_samples_and_settings(self):
        for value in [0, float('nan'), float('inf'), -1]:
            with self.assertRaises(ValueError):
                GrowthDetector(value)
        d = GrowthDetector()
        d.update(10, .1)
        for timestamp, value in [(10,.1),(9,.1),(15,1.5),(15,float('nan'))]:
            with self.assertRaises(ValueError):
                d.update(timestamp,value)

    def test_unknown_values_serialize_as_null(self):
        result = typed_row({'leak_active':'nan','label_known':'False','value':'','dataset':'westermo_1'})
        self.assertIsNone(result['leak_active'])
        self.assertFalse(result['label_known'])
        self.assertNotIn(b'NaN',json_bytes(result))


class FakeSampler:
    def __init__(self):
        self.i = 0

    def sample(self):
        self.i += 1
        return {'timestamp':time.time(), 'monotonic_seconds':time.monotonic(), 'memory_pressure':.2}


class LiveTests(unittest.TestCase):
    def test_session_is_bounded_exportable_and_stoppable(self):
        with tempfile.TemporaryDirectory() as folder, patch('src.demo_service.SystemSampler',FakeSampler):
            live = LiveMonitor(folder,cadence=.01,max_samples=4)
            live.start(.8)
            live.thread.join(timeout=5)
            snapshot = live.snapshot()
            self.assertFalse(snapshot['running'])
            self.assertEqual(len(snapshot['rows']),4)
            self.assertEqual(len(list(csv.DictReader(io.StringIO(live.export().decode())))),4)
            self.assertTrue((live.folder/'summary.json').exists())
            self.assertFalse(json.loads((live.folder/'summary.json').read_text())['leak_labels_available'])
            live.start(.8)
            with self.assertRaises(ValueError):
                live.start(.8)
            live.stop()
            self.assertFalse(live.snapshot()['running'])

    def test_collection_failures_are_reported(self):
        class BrokenSampler(FakeSampler):
            def sample(self):
                raise OSError('collector unavailable')
        with tempfile.TemporaryDirectory() as folder, patch('src.demo_service.SystemSampler',BrokenSampler):
            live=LiveMonitor(folder)
            live.start()
            live.thread.join(timeout=5)
            self.assertEqual(live.snapshot()['error'],'collector unavailable')


class ReplayAndHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = ReplayRepository(ROOT)
        cls.temporary = tempfile.TemporaryDirectory()
        cls.server = make_server(ROOT,0,cls.repo,LiveMonitor(cls.temporary.name,cadence=.01,max_samples=3))
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.metadata = cls.get('/api/metadata')

    @classmethod
    def tearDownClass(cls):
        cls.server.monitor.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temporary.cleanup()

    @classmethod
    def get(cls,path):
        with urlopen(cls.url+path,timeout=30) as r:
            return json.load(r)

    def post(self,path,body,headers=None):
        request = Request(self.url+path,data=json_bytes(body),headers=headers or {'Content-Type':'application/json','X-Demo-Token':self.metadata['token']})
        return urlopen(request,timeout=30)

    def test_all_recordings_and_source_integrity(self):
        self.assertEqual(self.repo.verified_files,76)
        self.assertEqual(sum(len(r) for r in self.repo.records.values()),69559)
        for name, rows in self.repo.records.items():
            first = self.repo.replay(name,0)
            last = self.repo.replay(name,len(rows)-1)
            self.assertEqual(len(first['observations']),1)
            self.assertEqual(last['index'],len(rows)-1)
            if name!='antarex_mono':
                self.assertTrue(all(p['leak'] is None for p in last['observations']))

    def test_future_truth_never_enters_replay_response(self):
        before = self.repo.replay('antarex_mono',10)
        source = self.repo.records['antarex_mono'][11]
        copy = dict(source)
        try:
            source['memory_pressure_at_origin']=.99
            source['leak_active']=1
            after=self.repo.replay('antarex_mono',10)
            self.assertEqual(before,after)
        finally:
            source.update(copy)
        now = before['current']['origin_timestamp']
        self.assertTrue(all(p['t']<=now for p in before['observations']))
        self.assertTrue(all(p['origin']<=now for p in before['forecasts']))
        self.assertTrue(any(p['target']>now for p in before['forecasts']))
        self.assertTrue(all('actual' not in p for p in before['forecasts']))

    def test_window_export_matches_displayed_origins(self):
        replay=self.repo.replay('antarex_mono',100,30)
        rows=list(csv.DictReader(io.StringIO(self.repo.export('antarex_mono',100,30).decode())))
        self.assertEqual(len(rows),30)
        self.assertEqual([float(r['origin_timestamp']) for r in rows],[p['t'] for p in replay['observations']])
        self.assertNotIn('actual',rows[0])

    def test_http_limits_path_allowlist_and_local_mutations(self):
        for path in ['/api/replay?index=-1','/api/replay?dataset=bad','/api/replay?window=10000','/api/replay?index=NaN']:
            with self.assertRaises(HTTPError) as e:
                self.get(path)
            self.assertEqual(e.exception.code,400)
        with self.assertRaises(HTTPError) as e:
            self.get('/research/PROJECT_STATUS.md')
        self.assertEqual(e.exception.code,404)
        with self.assertRaises(HTTPError) as e:
            self.post('/api/live/start',{}, {'Content-Type':'application/json'})
        self.assertEqual(e.exception.code,403)
        with self.assertRaises(HTTPError) as e:
            self.post('/api/live/start',{}, {'Content-Type':'application/json','X-Demo-Token':self.metadata['token'],'Origin':'https://example.org'})
        self.assertEqual(e.exception.code,403)
        with patch('src.demo_service.SystemSampler',FakeSampler):
            with self.post('/api/live/start',{'threshold':.8}) as response:
                self.assertIn('session',json.load(response))
            with self.post('/api/live/stop',{}) as response:
                self.assertFalse(json.load(response)['running'])

    def test_integrity_failure_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            (p/'sample').write_bytes(b'changed')
            (p/'MANIFEST.json').write_text(json.dumps({'files':[{'entry':'sample','bytes':7,'sha256':'0'*64}]}))
            with self.assertRaises(ValueError):
                verify_manifest(p)


if __name__=='__main__':
    unittest.main()
