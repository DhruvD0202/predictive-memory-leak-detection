"""Data-integrity checks that protect the later forecasting experiment."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import preprocessing as prep


class PreprocessingIntegrityTests(unittest.TestCase):
    def test_future_observation_cannot_change_already_available_inputs(self):
        source = pd.DataFrame({'#Time': [0., 4., 6., 10.], 'value': [1., 2., 3., 4.]})
        before = prep.align_past(source, np.array([5., 8., 9.]))
        source.loc[source['#Time'] > 5, 'value'] = 1000000.
        after = prep.align_past(source, np.array([5., 8., 9.]))
        self.assertEqual(before.loc[0, 'value'], 2.)
        self.assertEqual(before.loc[0, 'value'], after.loc[0, 'value'])
        self.assertTrue(np.isnan(before.loc[2, 'value']))  # stale at nine seconds

    def test_counter_resets_repeated_readings_and_long_gaps_are_invalid(self):
        d = pd.DataFrame({'source_time': [0., 5., 10., 10., 30., 35.],
                          'counter': [100., 150., 2., 2., 200., 225.]})
        rate = prep.counter_rates(d, ['counter'])['counter']
        np.testing.assert_allclose(rate.to_numpy(), [np.nan, 10., np.nan, np.nan, np.nan, 5.], equal_nan=True)

    def test_windows_never_bridge_invalid_rows_or_partition_boundaries(self):
        t = np.arange(240) * 5
        valid = np.ones(240, dtype=bool)
        valid[80:85] = False
        split = np.repeat([0, 1, 2], 80)
        windows, _ = prep.build_window_index(t, valid, split, 8, 4, 5)
        self.assertEqual(set(windows['split_code']), {0, 1, 2})
        for row in windows.itertuples(index=False):
            interval = slice(row.history_start_index, row.target_index + 1)
            self.assertTrue(valid[interval].all())
            self.assertEqual(len(np.unique(split[interval])), 1)
            self.assertEqual(row.origin_index-row.history_start_index+1, 8)
            self.assertEqual(t[row.target_index]-t[row.origin_index], 20)

    def test_missing_timestamps_split_sequences_even_when_values_are_valid(self):
        t = np.r_[np.arange(40)*5, 1000+np.arange(40)*5]
        windows, _ = prep.build_window_index(t, np.ones(80, dtype=bool), np.zeros(80), 8, 4, 5)
        self.assertFalse(((windows['history_start_index'] < 40) & (windows['target_index'] >= 40)).any())

    def test_scaling_and_feature_selection_ignore_future_and_labels(self):
        d = pd.DataFrame({'memory_pressure': np.linspace(.1, .9, 200),
                          'constant_metric': np.ones(200), 'leak_active': np.arange(200) % 2})
        training = np.arange(200) < 140
        candidates = ['memory_pressure', 'constant_metric']
        before = prep.fit_scaler(d, candidates, training)
        d.loc[~training, 'memory_pressure'] = 1e20
        d.loc[~training, 'constant_metric'] = 1e20
        d['leak_active'] = 1e20
        self.assertEqual(before, prep.fit_scaler(d, candidates, training))
        self.assertEqual(before['features'], ['memory_pressure'])
        self.assertEqual(before['removed_training_constant_features'], ['constant_metric'])

    def test_event_pairs_preserve_start_and_end_times(self):
        events = pd.DataFrame({'timestamp': [10, 30, 50, 80],
                               'type': ['status_start', 'status_end']*2,
                               'args': ['/tools/leak l']*2 + ['/tools/leak']*2,
                               'seqNum': [1, 1, 2, 2]})
        # Real source commands include arguments after the executable name.
        events.loc[2:, 'args'] = '/tools/leak normal'
        episodes = prep.reconstruct_episodes(events)
        self.assertEqual(episodes[['start', 'end']].values.tolist(), [[10, 30], [50, 80]])
        self.assertEqual(episodes['low_intensity'].tolist(), [True, False])
        broken = events.iloc[:-1]
        with self.assertRaisesRegex(ValueError, 'Unpaired'):
            prep.reconstruct_episodes(broken)

    def test_saved_arrays_round_trip_with_missing_data_and_unknown_labels(self):
        d = pd.DataFrame({'timestamp':np.arange(600)*30,
                          'memory_pressure':np.linspace(.1,.8,600),
                          'source_available':True,'leak_active':np.nan,'label_known':False})
        d.loc[200, 'source_available'] = False
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            info = prep.export_dataset(d,'westermo_fixture',output/'westermo_fixture',
                                       {'memory_pressure':'fraction'},30,8,4,{})
            prep.dump_json(output/'preprocessing_summary.json',{'datasets':[info]})
            checks = prep.verify_outputs(output)
            self.assertTrue(checks[0]['saved_arrays_verified'])
            self.assertEqual(info['invalid_rows'],1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
