"""Explain the original missed event using saved, verified warning decisions."""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.demo_service import verify_manifest
from src.warning_evaluation import warning_state

def main():
    source=ROOT/'results/warnings_colab'
    verify_manifest(source)
    output=ROOT/'results/revision_diagnostics'
    output.mkdir(parents=True,exist_ok=True)
    events=pd.read_csv(source/'antarex_event_outcomes.csv')
    missed=events[events['split'].eq('test') & events['method'].eq('lstm_growth') & events['eligible'] & ~events['detected']]
    assert len(missed)==1
    event=missed.iloc[0]
    frame=pd.read_csv(source/'antarex_test_warnings.csv.gz')
    threshold=json.loads((source/'selection_freeze.json').read_text())['selected']['lstm_growth']['threshold_pp_per_minute']
    inside=frame[frame['origin_timestamp'].ge(event.start)&frame['origin_timestamp'].lt(event.end)]
    assert len(inside)==47
    assert not inside['lstm_growth_warning'].any()
    assert not (inside['lstm_forecast_growth_pp_per_minute']>=threshold).any()
    trend=events[events['split'].eq('test') & events['method'].eq('trend_only') & events['episode_id'].eq(event.episode_id)].iloc[0]
    result={'event_id':int(event.episode_id),'start_unix':int(event.start),'end_unix_exclusive':int(event.end),
        'start_utc':datetime.fromtimestamp(event.start,timezone.utc).isoformat(),
        'duration_seconds':int(event.end-event.start),'low_intensity':bool(event.low_intensity),
        'eligible_origins':len(inside),'confirmed_label_source':'Antarex recorded injected-leak interval',
        'threshold_pp_per_minute':threshold,
        'max_observed_growth_pp_per_minute':float(inside.observed_growth_pp_per_minute.max()),
        'max_forecast_growth_pp_per_minute':float(inside.lstm_forecast_growth_pp_per_minute.max()),
        'max_joint_score_pp_per_minute':float(inside.lstm_growth_score.max()),
        'forecast_growth_qualifying_origins':int((inside.lstm_forecast_growth_pp_per_minute>=threshold).sum()),
        'lstm_warning_origins':int(inside.lstm_growth_warning.sum()),
        'trend_warning_origins':int(inside.trend_only_warning.sum()),
        'trend_first_alarm':int(trend.first_alarm_start),'trend_delay_seconds':float(trend.delay_seconds),
        'memory_pressure_range_percentage_points':[float(inside.memory_pressure_at_origin.min()*100),float(inside.memory_pressure_at_origin.max()*100)],
        'mechanism':'Forecast-growth condition never reaches 0.4 pp/min, so the conjunctive score never qualifies; confirmation length is not the primary cause.',
        'limitation':'Aggregate telemetry cannot establish the allocation-level cause of this forecast error; injection-active labels do not require monotonic system memory.'}
    (output/'missed_event.json').write_text(json.dumps(result,indent=2)+'\n')
    segment=frame[frame.origin_timestamp.between(event.start-120,event.end+120)].copy()
    segment.to_csv(output/'missed_event_window.csv',index=False)
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'legend.fontsize':8,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,1,figsize=(4.8,3.35),sharex=True,layout='constrained')
    x=(segment.origin_timestamp-event.start)/60
    axes[0].plot(x,segment.memory_pressure_at_origin*100,color='#243b53',label='Observed at origin')
    axes[0].plot(x,segment.lstm_forecast*100,'--',color='#b23a48',label='LSTM, 60 s ahead')
    axes[0].set_ylabel('Pressure (% RAM)')
    axes[0].set_ylim(1,8.5)
    axes[0].legend(loc='upper left',ncol=1)
    axes[1].plot(x,segment.observed_growth_pp_per_minute,color='#243b53',label='Observed growth')
    axes[1].plot(x,segment.lstm_forecast_growth_pp_per_minute,'--',color='#b23a48',label='Forecast growth')
    axes[1].axhline(threshold,color='black',linestyle=':',label='LSTM threshold (0.4)')
    axes[1].set_ylabel('Growth (pp RAM/min)')
    axes[1].set_xlabel('Minutes from injection start')
    axes[1].legend(loc='lower left',ncol=1)
    for ax in axes:
        ax.axvspan(0,(event.end-event.start)/60,color='gray',alpha=.12,hatch='//',label='Injected leak active')
        ax.grid(alpha=.18)
    figures=ROOT/'paper/spin2027/figures'
    figures.mkdir(parents=True,exist_ok=True)
    fig.savefig(figures/'missed_event.pdf',bbox_inches='tight')
    fig.savefig(figures/'missed_event.png',dpi=240,bbox_inches='tight')
    plt.close(fig)
    candidates=pd.read_csv(source/'validation_candidates.csv')
    arima=candidates[candidates.method.eq('arima_growth')]
    assert arima['tp'].eq(0).all()
    val=pd.read_csv(source/'antarex_validation_warnings.csv.gz')
    detail={'arima_validation_candidates':arima[['threshold_pp_per_minute','tp','fp','f1']].replace({np.nan:None}).to_dict('records'),
        'max_arima_forecast_growth_pp_per_minute':float(val.arima_forecast_growth_pp_per_minute.max()),
        'maximum_joint_growth_score_pp_per_minute':float(val.arima_growth_score.max()),
        'smallest_positive_candidate_threshold':.01,
        'explanation':'All candidates have zero true-positive warning timestamps; the disabled option wins the recorded F1/false-positive/threshold tie-break.'}
    (output/'arima_disabled.json').write_text(json.dumps(detail,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
    print(json.dumps(detail,indent=2))

if __name__=='__main__': main()
