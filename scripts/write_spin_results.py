"""Build the SPIN result tables/plot from audited original and repeated runs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'paper/spin2027'
NAMES=['antarex_mono','westermo_1','westermo_2','westermo_3']
LABELS=['A','W1','W2','W3']
NOTE='Prepared with OpenAI Codex assistance (GPT-6-based, October 2026).'

def pm(row,col,digits=3):
    return f"${row[col+'_mean']:.{digits}f}\\pm{row[col+'_sd']:.{digits}f}$"

def table(caption,label,columns,header,rows):
    return '\n\n'+'\n'.join([r'\begin{table}[htbp]',r'\caption{'+caption+' '+NOTE+'}',r'\label{'+label+'}',
        r'\centering\small',r'\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{@{}'+columns+'@{}}',
        r'\toprule',header+r'\\',r'\midrule',*rows,r'\bottomrule',r'\end{tabular}',r'\end{table}'])+'\n\n'

def main():
    checked=json.loads((ROOT/'results/revision_diagnostics/revision_integrity_checks.json').read_text())
    assert checked['all_checks_passed'] and checked['models_verified']==40
    original=pd.read_csv(ROOT/'results/lstm_colab/metrics.csv')
    original=original[original.split.eq('test')].set_index(['dataset','model'])
    forecast=pd.read_csv(ROOT/'results/revision_20261016/forecast_summary.csv').set_index(['dataset','variant'])
    warning=pd.read_csv(ROOT/'results/revision_20261016/warning_summary.csv').set_index(['variant','method'])
    original_points=pd.read_csv(ROOT/'results/warnings_colab/antarex_point_metrics.csv').query("split == 'test'").set_index('method')
    original_events=pd.read_csv(ROOT/'results/warnings_colab/antarex_event_metrics.csv').query("split == 'test'").set_index('method')
    bench=json.loads((ROOT/'results/revision_diagnostics/prototype_benchmark.json').read_text())
    rows=[]
    for method,label in [('persistence','Persistence'),('linear_trend','Linear trend'),('arima','ARIMA'),('lstm','Original LSTM')]:
        cells=[]
        for name in NAMES:
            row=original.loc[(name,method)]
            cells.append(f"{row.mae_percentage_points:.3f} / {row.rmse_percentage_points:.3f}")
        rows.append(label+' & '+' & '.join(cells)+r'\\')
    old_table=table('Original test forecast errors: MAE / RMSE, in percentage points (pp) of total RAM. A uses 60 s; W1--W3 use 300 s. LSTM is the single Colab seed-42 run.',
        'tab:original_forecast','lrrrr','Model & A & W1 & W2 & W3',rows)
    rows=[]
    for name,label in zip(NAMES,LABELS):
        mem,multi=forecast.loc[(name,'memory_only')],forecast.loc[(name,'multivariate')]
        rows.append(label+' & '+' & '.join([pm(mem,'mae_percentage_points'),pm(multi,'mae_percentage_points'),pm(mem,'rmse_percentage_points'),pm(multi,'rmse_percentage_points')])+r'\\')
    ablation_table=table('Five-seed LSTM test errors: mean $\\pm$ sample SD, in pp. Mem: memory-only; Multi: retained multivariate inputs. All five seeds are included.',
        'tab:ablation','lrrrr',r'Recording & MAE (Mem) & MAE (Multi) & RMSE (Mem) & RMSE (Multi)',rows)
    rows=[]
    for method,label in [('trend_only','Trend only'),('lstm_growth','LSTM + trend'),('arima_growth','ARIMA (off)')]:
        p,e=original_points.loc[method],original_events.loc[method]
        precision='--' if pd.isna(p.precision) else f'{p.precision:.3f}'
        delay='--' if pd.isna(e.median_delay_seconds_detected_only) else f'{e.median_delay_seconds_detected_only:.0f}'
        rows.append(f'{label} & {precision} & {p.recall:.3f} & {p.f1:.3f} & {p.false_alarm_starts:.0f} & {e.missed_events:.0f} & {delay}'+r'\\')
    old_warning=table('Original Antarex test warnings. P/R: timestamp precision/recall; FA: false alarm starts; missed: events missed out of 35; delay: median seconds after injection among detected events only. A dash means undefined.',
        'tab:original_warning','lrrrrrr',r'Rule & P & R & F1 & FA & Missed & Delay (s)',rows)
    rows=[]
    for variant,label in [('multivariate','Multivariate'),('memory_only','Memory-only')]:
        r=warning.loc[(variant,'lstm_growth')]
        rows.append(label+' & '+pm(r,'f1')+' & '+pm(r,'false_alarm_starts_per_non_leak_hour')+f" & {r.missed_events_min:.0f}--{r.missed_events_max:.0f} & "+pm(r,'median_delay_seconds_detected_only',1)+r'\\')
    repeat_warning=table('Repeated LSTM-assisted Antarex warnings. F1 and FA/h are mean $\\pm$ SD; missed is the range out of 35 events. Delay summarizes the five detected-event medians, not pooled events.',
        'tab:repeat_warning','lrrrr',r'Inputs & F1 & FA/h & Missed & Delay (s)',rows)
    # Use the already specified original 30-minute interval, not a best-seed plot.
    frame=pd.read_csv(ROOT/'results/lstm_colab/antarex_mono/first_test_30min.csv')
    start=frame.target_timestamp.iloc[0]; x=(frame.target_timestamp-start)/60
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'legend.fontsize':8,'pdf.fonttype':42})
    fig,ax=plt.subplots(figsize=(4.8,2.35),layout='constrained')
    for key,label,color,style in [('actual','Actual','#172b4d','-'),('persistence','Persistence','#008577',':'),('arima','ARIMA','#7752b8','--'),('lstm','Original LSTM','#c83450','-.')]:
        ax.plot(x,frame[key]*100,label=label,color=color,linestyle=style,lw=1.1)
    ax.set(xlabel=f'Target time: minutes from {int(start)} (Unix s)',ylabel='Memory pressure (% RAM)')
    ax.legend(ncol=2,loc='upper left'); ax.grid(alpha=.2)
    fig.savefig(DEST/'figures/actual_predicted.pdf'); fig.savefig(DEST/'figures/actual_predicted.png',dpi=240); plt.close(fig)
    replay=[r['replay_ms']['median'] for r in bench['recordings']]
    warm=[r['warm_inference_ms']['median'] for r in bench['recordings']]
    warm95=[r['warm_inference_ms']['p95'] for r in bench['recordings']]
    first=bench['recordings'][0]['first_inference_request_ms']/1000
    prototype=(r'\clearpage'+'\n'+r'\subsection{Prototype Checks and Measurement Limits}'+'\n'+
        f"All 40 implementation tests passed, including loopback HTTP endpoints. Startup verified 76 source files covering 69,559 test origins. In a separate in-process benchmark on Windows with {bench['logical_cpus']} logical CPUs and {bench['installed_ram_gib']:.1f} GiB RAM, each recording received 100 replay/JSON requests and 100 warm model requests. Median replay times ranged from {min(replay):.2f} to {max(replay):.2f} ms; median warm inference ranged from {min(warm):.2f} to {max(warm):.2f} ms (95th percentiles {min(warm95):.2f}--{max(warm95):.2f} ms). All 404 first/warm inferences matched archived predictions within $10^{{-6}}$ pressure fraction. The first request, including library/model loading, took {first:.2f} s. Process resident memory increased from {bench['rss_before_repository_mib']:.1f} to {bench['rss_after_all_models_mib']:.1f} MiB; this includes replay data, libraries and four models, not isolated monitoring overhead.\n\n"+
        r"These measurements exclude HTTP transport and browser rendering. The live collector returned a Windows performance-counter error before any samples were recorded. No live timing, CPU-overhead or labeled live-detection result is reported. Longer live trials, missing-counter resilience and controlled overhead measurements remain unvalidated. The optional live mode uses exploratory trend warnings, not the archived Linux LSTM."+'\n')
    results=r'''\subsection{Forecast Accuracy and the Baseline Comparison}
Table~\ref{tab:original_forecast} preserves the original run. On Antarex, LSTM RMSE was 1.216 pp against ARIMA's 1.516 pp, a 19.8\% reduction, while MAE changed only from 0.363 to 0.358 pp. The larger RMSE improvement indicates a stronger effect on large errors than on average absolute error. Across Westermo, the original LSTM reduced RMSE but ARIMA had lower MAE: no method wins under every loss.

The selected Antarex ARIMA$(3,1,0)$ coefficients are approximately $-0.011$, $-0.010$ and $-0.011$. With no drift, forecast increments quickly become small, making its predictions close to persistence; their RMSEs differ by only 0.000196 pp. Linear extrapolation performs worse in all four recordings, consistent with transient slopes not continuing through the forecast horizon. Figure~\ref{fig:forecast} shows the fixed original example interval; full-test scores, rather than that interval, support the comparisons.
'''+old_table+r'''
\begin{figure}[htbp]
\centering\includegraphics[width=\textwidth]{actual_predicted.pdf}
\Description{Actual and predicted memory pressure in percent of RAM over the fixed original first thirty minutes of Antarex test target times.}
\caption{Original Antarex 60-second-ahead rolling forecasts, aligned by target time. Predictions shown at a time were issued 60 s earlier. Persistence and ARIMA nearly overlap. This is the first fixed 30-minute test interval, not a best-case selection. Plot prepared with OpenAI Codex assistance (GPT-6-based, October 2026).}
\label{fig:forecast}
\end{figure}

\subsection{Random Seeds and the Memory-Only Ablation}
The new CPU runs use Python 3.12.14, PyTorch 2.8.0+cpu and two Torch threads. Table~\ref{tab:ablation} keeps them separate from Colab. On Antarex, multivariate mean RMSE is 1.204 pp versus memory-only 1.221 pp. Paired multivariate RMSE is lower in four of five Antarex seeds and all five W1 seeds, but only one W2 seed and no W3 seed. On W2 and W3, extra inputs also increase MAE in every paired seed. Additional telemetry therefore does not consistently improve this fixed model and training budget. The experiment does not isolate which feature helps or harms.

Both LSTM variants have lower mean RMSE than restricted ARIMA on each recording, but all their mean MAEs exceed ARIMA's. Training minimizes squared error, which weights large deviations strongly; lower RMSE with worse MAE is therefore possible. Seed SD describes optimization variability on these recordings, not a confidence interval for other systems. No additional labeled dataset or independent holdout was introduced.
'''+ablation_table+r'''
\subsection{Warnings, Missed Events and Recognition Delay}
There are 1933 leak-active origins among 31,032 Antarex test origins and 35 fully covered injected events. Table~\ref{tab:original_warning} shows that the original LSTM warning improves precision and reduces false alarm starts from 86 to 42, but covers less leak-active time and misses one event. False alarm rates are 2.128/h for trend-only and 1.039/h for LSTM; false-positive exposure is 34.17 and 13.50 min respectively. Their detected-event 90th-percentile delays are 56.0 and 45.7 s. The disabled ARIMA rule is equivalent to always-off and misses all events.

The difference follows from the warning objective. Regression rewards accurate future levels over all origins, whereas the assisted rule demands both observed and forecast growth above a threshold for three readings. A model can predict the level closely while predicting insufficient continued growth. The additional condition suppresses some false alarms and some true warnings; minimizing forecast RMSE does not optimize event recall or warning F1.
'''+old_warning+r'''
Event 1534, a low-intensity injection starting at 22:00:14 UTC on 19 May 2018, demonstrates this mechanism (Fig.~\ref{fig:missed}). During its 236 s and 47 eligible origins, forecast growth peaks at 0.216 pp/min, below the 0.4 threshold. Thus no reading can satisfy the forecast gate, irrespective of the three-reading requirement. Observed growth reaches 0.938 pp/min; trend-only warns after 56 s. Memory pressure spans approximately 3.20--7.17\%. The recorded scores explain the decision failure, not its allocation-level cause.

\begin{figure}[htbp]
\centering\includegraphics[width=\textwidth]{missed_event.pdf}
\Description{Two panels show memory pressure and growth scores around the original missed injection. Forecast growth stays below the warning threshold during the shaded interval.}
\caption{Original missed injected event 1534. Shading marks the recorded injection. Top: current pressure and the forecast issued at the same origin (its target is 60 s later). Bottom: observed and forecast growth; predicted growth remains below the LSTM gate throughout the injection. pp: percentage points of RAM. Plot prepared with OpenAI Codex assistance (GPT-6-based, October 2026).}
\label{fig:missed}
\end{figure}

The seed study weakens a general claim of fewer false alarms (Table~\ref{tab:repeat_warning}). Multivariate precision is $0.758\pm0.112$ and recall $0.461\pm0.010$; memory-only gives $0.648\pm0.071$ and $0.482\pm0.021$. Multivariate false starts range from 43 to 137, compared with the unchanged trend count of 86; memory-only ranges from 126 to 168. Each variant misses zero to two events depending on seed. Trend-only F1 remains 0.830, above every new LSTM-assisted run. The original precision/false-alarm advantage is therefore not stable across all repetitions. Validation selects thresholds separately for each run; forecast training variability and threshold decisions both influence these results.
'''+repeat_warning+'\n'+prototype
    (DEST/'results.tex').write_text(results,encoding='utf-8')
    (DEST/'abstract.tex').write_text(r'''Forecasting rising memory pressure can support monitoring, but accurate forecasts do not by themselves identify memory leaks. We compare persistence, linear trend, restricted ARIMA and a small LSTM on one Antarex fault-injection recording and three Westermo industrial recordings, using chronological splits and 60- or 300-second horizons. Forecast error and growth-warning performance are evaluated separately. In the original Antarex run, LSTM reduces RMSE from ARIMA's 1.516 to 1.216 percentage points of RAM. Its warning rule, however, recognizes 34 of 35 injected events against trend-only's 35, with timestamp recall 0.466 versus 0.859. A matched study of five random seeds and two LSTM input configurations adds 40 runs. Extra features improve mean RMSE on only two of four recordings. Multivariate Antarex warning F1 is $0.571\pm0.031$, below trend-only's 0.830, and false alarm starts range from 43 to 137 against 86. A saved-score analysis explains the original missed event through an unmet forecast-growth threshold. Westermo has no confirmed leak labels and supports forecasting conclusions only. Local replay/inference timings describe prototype functionality; live performance and advance warning before memory exhaustion remain unvalidated.
''',encoding='utf-8')
    print('Wrote evidence-based abstract, result text, four tables and forecast figure.')

if __name__=='__main__': main()
