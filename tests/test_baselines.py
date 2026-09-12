import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import baselines as base
from statsmodels.tsa.arima.model import ARIMA


class BaselineIntegrityTests(unittest.TestCase):
    def test_linear_trend_extrapolates_known_line(self):
        y=.1+np.arange(300)*.001
        origins=np.array([100,200])
        for history in base.TREND_HISTORY:
            np.testing.assert_allclose(base.linear_forecast(y,origins,history,12),y[origins+12],atol=1e-12)

    def test_future_data_cannot_change_forecast(self):
        y=np.random.default_rng(7).normal(.3,.01,300)
        origins=np.array([150,151])
        before=[base.linear_forecast(y,origins,60,12),base.arima_forecast(y,origins,[.4,-.1],12)]
        y[152:]=10000
        after=[base.linear_forecast(y,origins,60,12),base.arima_forecast(y,origins,[.4,-.1],12)]
        for first,second in zip(before,after): np.testing.assert_array_equal(first,second)

    def test_recursive_arima_matches_statsmodels(self):
        y=.4+np.cumsum(np.random.default_rng(29).normal(0,.001,150))
        for coefficients in [[.5],[.5,-.2,.1],[.2,.1,-.05,.02,.01]]:
            for origin in [70,120]:
                model=ARIMA(y[origin-59:origin+1]*100,order=(len(coefficients),1,0),trend='n')
                expected=model.filter(np.r_[coefficients,.01]).forecast(12)/100
                actual=base.arima_forecast(y,np.array([origin]),coefficients,12)[0]
                self.assertAlmostEqual(actual,expected[-1],places=10)

    def test_zero_ar_coefficients_equal_persistence(self):
        y=np.random.default_rng(8).uniform(size=200)
        o=np.array([100,150])
        np.testing.assert_array_equal(base.arima_forecast(y,o,[0.,0.,0.],12),y[o])

    def test_training_segment_does_not_bridge_gap_or_include_validation(self):
        t=np.arange(500)*5
        valid=np.ones(500,dtype=bool); valid[160:170]=False
        split=np.r_[np.zeros(350),np.ones(150)]
        self.assertEqual(base.longest_training_segment(t,valid,split,5),(170,350))

    def test_test_values_cannot_change_selected_parameters(self):
        y=.4+np.cumsum(np.random.default_rng(2).normal(0,.001,600))
        o=np.arange(410,460)
        w=pd.DataFrame({'split':'validation','origin_index':o,'target_index':o+12})
        first,candidates_a,fits_a=base.select_settings(y,w,slice(0,400),12)
        y[500:]=1e10
        second,candidates_b,fits_b=base.select_settings(y,w,slice(0,400),12)
        self.assertEqual(first,second)
        self.assertEqual(candidates_a,candidates_b)
        for p in fits_a: self.assertEqual(fits_a[p]['coefficients'],fits_b[p]['coefficients'])

    def test_error_units_are_percentage_points_not_accuracy(self):
        result=base.errors(np.array([.1,.2]),np.array([.2,.4]))
        self.assertAlmostEqual(result['mae_percentage_points'],15)
        self.assertAlmostEqual(result['rmse_percentage_points'],100*np.sqrt(.025))


if __name__=='__main__': unittest.main(verbosity=2)
