# Baseline protocol — fixed before model results

Date: 8 September 2026. Stage: baseline forecasting only. Compute target: free Colab CPU.

## Inputs and evaluation

Use the user's successful Colab output, `data/packages/review2_preprocessed_colab.zip`, SHA-256 `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2`. Verify every entry against its manifest. Preserve the four separate recordings and their supplied 70/15/15 time splits, valid windows and horizons. Antarex predicts 60 seconds ahead; Westermo predicts 300 seconds ahead. All methods receive the same forecast origins and at most the supplied 60-observation history.

The target is the unscaled memory-pressure fraction stored in the prepared arrays. Models in this stage are univariate memory baselines. CPU/page-fault and other multivariate features are reserved for the LSTM stage; no superiority of multivariate models is assumed.

Use rolling-origin forecasts: a forecast may use actual measurements available through its own origin, including earlier observations in the validation/test period. It must not use any measurement after that origin. Parameters are fitted on training data only and never refitted on validation or test data. This evaluates repeated short-horizon monitoring forecasts, not one forecast of the entire held-out recording from its beginning.

## Three baseline families

1. **Persistence:** future memory equals the most recently observed value.
2. **Local linear trend:** least-squares line through the last 12, 30 or 60 memory observations, extrapolated to the target horizon. Choose the history length by validation RMSE only, breaking exact ties in favour of the shorter history.
3. **ARIMA(p,1,0), no drift:** candidates p = 1, 3, 5. First differences are modeled by a low-order autoregression. Fit with statsmodels' Yule-Walker estimator on the longest contiguous valid training segment (earliest segment in a length tie). Do not concatenate across gaps. Use the complete selected segment; record its time bounds and size. Choose p by validation RMSE, breaking exact ties in favour of the smaller order. This is a deliberately restricted ARIMA baseline; q > 0, drift, seasonal terms, exhaustive order search and formal Box-Jenkins diagnostics remain later work.

The pure autoregressive model permits efficient, exact recursive mean forecasts from its last p observed differences. Validate that implementation against statsmodels forecasts before using it. No future residuals, states or observed differences may enter the recursive horizon.

Clip all baseline forecasts to [0,1], the physical range of the declared target. Save raw forecasts and clipping counts as well. This common rule is fixed before evaluation and must also apply in a later fair model comparison.

## Selection and reporting

Fit all candidates on training data, select settings within each family on validation RMSE, and save the selected settings before evaluating the test partition. Identify the strongest baseline family by validation RMSE, not by test results. Report MAE and RMSE for every selected baseline on every recording, with counts and units. Multiply fractional errors by 100 to report **percentage points of total RAM**; do not present them as classification accuracy percentages.

Save every validation/test origin, target, actual value and forecast. For Antarex, also give descriptive forecast-error breakdowns by whether a leak is active at the origin. These are not warning-classification precision/recall, and an active injected leak is not proof that the machine is near exhaustion.

Predetermined figures: (a) the first 30 minutes of eligible Antarex test target times; (b) a 30-minute view around the first eligible test leak onset, identified by ground-truth time rather than forecast error; (c) the first 24 hours of eligible Westermo-1 test target times; (d) per-recording MAE/RMSE comparison. Place predictions at **target timestamps**, not origin timestamps. Mark recorded leak intervals as context only. These are illustrative windows; metrics use all valid held-out origins.

Overlapping windows are correlated. Do not claim statistical significance from treating them as independent observations. Save timing as local implementation timing only; it is not deployment-monitoring overhead or a Colab performance guarantee. Inspect no test errors for tuning this step or subsequent LSTM settings.

## Methodological grounding

Review 1 reference [3], [Assi, Fahad and Al-Sarray (2022)](https://doi.org/10.22075/ijnaa.2022.26974.3505), motivates comparing Box-Jenkins/statistical forecasting with LSTM. Its model orders and reported errors are not results for this dataset.

The chosen estimator and ARIMA specification follow the primary [statsmodels 0.14.6 ARIMA documentation](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.html) and [fit-method documentation](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.arima.model.ARIMA.fit.html). The rolling-origin distinction follows the library's [forecasting example](https://www.statsmodels.org/v0.12.2/examples/notebooks/generated/statespace_forecasting.html). This protocol does not yet implement Mann-Kendall, hybrid ARIMA-LSTM, warning classification or paper drafting.
