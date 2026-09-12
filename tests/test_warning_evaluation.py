import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import warning_evaluation as w


class WarningTests(unittest.TestCase):
    def test_causal_growth_and_forecast_units(self):
        y = .1 + np.arange(100) * .001
        origins = np.array([11, 12, 20])
        arima = y[origins] + .012
        lstm = y[origins] + .006
        scores = w.warning_scores(y, origins, arima, lstm, cadence=5, horizon=60)
        np.testing.assert_allclose(scores['trend_only_score'], 1.2, atol=1e-12)
        np.testing.assert_allclose(scores['arima_growth_score'], 1.2, atol=1e-12)
        np.testing.assert_allclose(scores['lstm_growth_score'], .6, atol=1e-12)
        poisoned = y.copy()
        poisoned[origins.max() + 1:] = 999
        for key, value in scores.items():
            np.testing.assert_array_equal(value, w.warning_scores(poisoned, origins, arima, lstm, 5, 60)[key])
        west = w.warning_scores(y, origins, arima, lstm, 30, 300)
        np.testing.assert_allclose(west['lstm_growth_score'], .12, atol=1e-12)

    def test_confirmation_gap_reset_and_no_retroactive_fill(self):
        times = [0, 5, 10, 15, 20, 30, 35, 40, 45]
        score = [1, 1, 1, 0, 1, 1, 1, 1, 0]
        active = w.warning_state(score, times, .5, 5, 3)
        np.testing.assert_array_equal(active, [False, False, True, False, False, False, False, True, False])
        np.testing.assert_array_equal(w.alarm_starts(active, times, 5), active)
        np.testing.assert_array_equal(w.warning_state(score, times, None, 5), np.zeros(9, dtype=bool))

    def test_confusion_and_undefined_ratios(self):
        result = w.point_metrics([0, 1, 1, 0, 0], [0, 1, 0, 1, 1], np.arange(5) * 5, 5)
        self.assertEqual([result[k] for k in ['tp', 'fp', 'tn', 'fn']], [1, 2, 1, 1])
        self.assertAlmostEqual(result['precision'], 1/3)
        self.assertEqual(result['recall'], .5)
        self.assertEqual(result['f1'], .4)
        self.assertEqual(result['false_alarm_starts'], 1)
        self.assertEqual(result['false_alarm_starts_per_non_leak_hour'], 240)
        off = w.point_metrics([0, 1], [0, 0], [0, 5], 5)
        self.assertIsNone(off['precision'])
        self.assertEqual(off['recall'], 0)
        self.assertEqual(off['f1'], 0)
        empty_positive = w.point_metrics([0, 0], [0, 0], [0, 5], 5)
        self.assertIsNone(empty_positive['f1'])
        with self.assertRaises(AssertionError):
            w.point_metrics([np.nan, np.nan], [0, 0], [0, 5], 5)

    def test_exact_event_boundaries_delay_and_preexisting_alarm(self):
        times = np.arange(0, 70, 5)
        episodes = pd.DataFrame({'episode_id': [1, 2, 3], 'start': [11, 31, 46], 'end': [26, 41, 61], 'low_intensity': [False] * 3})
        active = np.isin(times, [15, 20, 25, 30, 35, 40, 50, 55])
        result, table = w.event_metrics(episodes, times, active, 5)
        self.assertEqual(result['eligible_events'], 3)
        self.assertEqual(result['detected_events'], 2)
        self.assertEqual(table['detected'].tolist(), [True, False, True])
        self.assertEqual(table['delay_seconds'].dropna().tolist(), [4, 4])
        self.assertEqual(result['missed_events'], 1)
        self.assertEqual(result['median_delay_seconds_detected_only'], 4)
        at_end = pd.DataFrame({'episode_id': [1], 'start': [10], 'end': [20], 'low_intensity': [False]})
        result, _ = w.event_metrics(at_end, times, times == 20, 5)
        self.assertEqual(result['detected_events'], 0)

    def test_event_coverage_exclusions_and_never_alarm(self):
        times = np.array([0, 5, 10, 15, 25, 30, 35, 40, 45, 50])
        episodes = pd.DataFrame({'episode_id': [1, 2, 3, 4], 'start': [0, 11, 31, 46],
                                 'end': [8, 28, 44, 59], 'low_intensity': [False] * 4})
        result, table = w.event_metrics(episodes, times, np.zeros(len(times), dtype=bool), 5)
        self.assertEqual(result['eligible_events'], 1)
        self.assertEqual(result['excluded_events'], 3)
        self.assertEqual(result['event_recall'], 0)
        self.assertIsNone(result['median_delay_seconds_detected_only'])
        self.assertEqual(table['exclusion_reason'].tolist(), ['boundary_or_no_origin_coverage', 'coverage_gap', '', 'boundary_or_no_origin_coverage'])

    def test_selection_uses_validation_only_and_matches_known_optimum(self):
        y = .1 + np.arange(150) * .001
        origins = np.arange(11, 41)
        future_arima, future_lstm = y[origins] + .012, y[origins] + .006
        labels = np.r_[np.zeros(10), np.ones(20)]
        def validation(values):
            scores = w.warning_scores(values, origins, future_arima, future_lstm, 5, 60)
            return pd.DataFrame({'origin_timestamp': origins * 5, 'leak_active': labels, 'label_known': True, **scores})
        selected, candidates = w.select_thresholds(validation(y), 5)
        poisoned = y.copy()
        poisoned[50:] = 500
        repeated, _ = w.select_thresholds(validation(poisoned), 5)
        self.assertEqual(selected, repeated)
        self.assertEqual(len(candidates), 31)
        self.assertEqual(selected['lstm_growth']['threshold_pp_per_minute'], .4)
        self.assertIsNone(selected['always_off']['threshold_pp_per_minute'])
        for method in w.METHODS[:3]:
            rows = candidates[candidates['method'].eq(method)]
            self.assertEqual(selected[method]['validation_f1'], rows['f1'].max())

    def test_unlabeled_transfer_never_invents_classification_metrics(self):
        frame = pd.DataFrame({'origin_timestamp': np.arange(6) * 30, 'leak_active': np.nan, 'label_known': False})
        for method in w.METHODS:
            frame[method + '_warning'] = [False, False, True, True, False, True]
        table = w.describe_unlabeled(frame, 'westermo_fixture', 30)
        self.assertEqual(table['alarm_starts'].tolist(), [2] * 4)
        self.assertFalse(table['leak_labels_available'].any())
        self.assertFalse({'precision', 'recall', 'false_alarm_starts'} & set(table.columns))


if __name__ == '__main__':
    unittest.main()
