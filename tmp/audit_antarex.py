"""Validate selected OS metric streams and leak labels without model training."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/raw/antarex/CPU-MEM_mono/extracted/results'
SPEC = {
 'meminfo':['MemTotal','MemFree','MemAvailable','Buffers','Cached','SwapTotal','SwapFree','SwapCached','Active(anon)','AnonPages','Committed_AS'],
 'vmstat':['pgfault','pgmajfault','pswpin','pswpout','nr_free_pages','nr_anon_pages','pgpgin','pgpgout'],
 'procstat':['user','nice','sys','idle','iowait','irq','softirq','steal','guest','guest_nice','cores_up','context_switches','procs_running','procs_blocked'],
 'procdiskstats':['reads_comp#sdc1','writes_comp#sdc1','sect_read#sdc1','sect_written#sdc1','sect_read.rate#sdc1','sect_written.rate#sdc1','disk.byte_read#sdc1','disk.byte_written#sdc1','disk.byte_read.rate#sdc1','disk.byte_written.rate#sdc1','time_ios#sdc1','ios_in_progress#sdc1']
}
out = {'checked_on':'2026-09-07','block':'CPU-MEM_mono','scope':'Selected required metric fields in all rows of four streams, plus complete labels and event log. Other streams not audited.','streams':{}}
timeline = {}
memory_times = []
memory_pressure = []
for name, cols in SPEC.items():
    file = BASE/'ldms/csv'/name
    header = pd.read_csv(file,nrows=0).columns.tolist()
    times = []
    lows, highs, negatives, nonfinite, decreases = {}, {}, {}, {}, {}
    nulls = 0
    prev = None
    for d in pd.read_csv(file,usecols=['#Time']+cols,chunksize=50000):
        nulls += int(d.isna().sum().sum())
        times.append(d['#Time'].to_numpy())
        for c in cols:
            lows[c] = min(lows.get(c,float('inf')),float(d[c].min()))
            highs[c] = max(highs.get(c,float('-inf')),float(d[c].max()))
            negatives[c] = negatives.get(c,0)+int((d[c]<0).sum())
            nonfinite[c] = nonfinite.get(c,0)+int((~np.isfinite(d[c])).sum())
            decrease = int((d[c].diff()<0).sum())
            if prev is not None:
                decrease += int(d[c].iloc[0] < prev[c])
            decreases[c] = decreases.get(c,0)+decrease
        prev = d.iloc[-1]
        if name == 'meminfo':
            memory_times.append(d['#Time'].to_numpy())
            memory_pressure.append((1-d['MemAvailable']/d['MemTotal']).to_numpy())
    t = np.concatenate(times)
    timeline[name] = t
    delta = np.diff(t)
    report = {'file_bytes':file.stat().st_size,'all_columns':header,'audited_columns':cols,'rows':len(t),'start':float(t[0]),'end':float(t[-1]),'span_days':float((t[-1]-t[0])/86400),
              'duplicate_timestamps':int(len(t)-len(np.unique(t))),'nonpositive_deltas':int((delta<=0).sum()),
              'sampling_interval_seconds':dict(zip(['min','p50','p99','max'],[float(v) for v in np.quantile(delta,[0,.5,.99,1])])),
              'gaps_over_2_seconds':int((delta>2).sum()),'missing_integer_seconds_within_span':int(np.floor(t[-1])-np.floor(t[0])+1-len(np.unique(np.floor(t)))),
              'null_cells_selected':nulls,'nonfinite_counts':nonfinite,'negative_counts':negatives,
              'ranges':{c:[lows[c],highs[c]] for c in cols},'decrease_counts':decreases}
    out['streams'][name]=report
    print(name,report['rows'],'rows; sampling',report['sampling_interval_seconds'],'gaps >2s',report['gaps_over_2_seconds'],flush=True)
labels = pd.read_csv(next(BASE.glob('labels_*.csv')),sep=';',keep_default_na=False)
events = pd.read_csv(next(BASE.glob('injection-*.csv')),sep=';',keep_default_na=False)
is_leak = events['args'].str.contains('/leak ',regex=False)
starts = events[is_leak & events['type'].eq('status_start')]
ends = events[is_leak & events['type'].eq('status_end')]
paired = starts.merge(ends,on='seqNum',suffixes=('_start','_end'),validate='one_to_one')
expected = np.zeros(len(labels),dtype=bool)
lt = labels['#Time'].to_numpy()
for _,row in paired.iterrows():
    expected |= (lt>=int(row['timestamp_start'])) & (lt<int(row['timestamp_end']))
actual = labels['#Fault'].str.startswith('leak').to_numpy()
mt = np.concatenate(memory_times)
mp = np.concatenate(memory_pressure)
memory_leak = np.zeros(len(mt),dtype=bool)
episodes = []
for _,row in paired.iterrows():
    start,end = int(row['timestamp_start']),int(row['timestamp_end'])
    mask = (mt>=start)&(mt<end)
    memory_leak |= mask
    episodes.append({'seqNum':int(row['seqNum']),'start':start,'end':end,'duration_seconds':end-start,
                     'low_intensity':str(row['args_start']).endswith(' l'),
                     'memory_pressure_max':float(mp[mask].max()) if mask.any() else None})
out['labels']={'rows':len(labels),'start':int(lt[0]),'end':int(lt[-1]),'interval_counts':{str(k):int(v) for k,v in pd.Series(np.diff(lt)).value_counts().items()},
               'fault_second_counts':{str(k):int(v) for k,v in labels['#Fault'].value_counts().items()},
               'event_types':{str(k):int(v) for k,v in events['type'].value_counts().items()},'event_error_rows':int(events['error'].ne('None').sum()),
               'leak_episodes':len(paired),'leak_duration_seconds':dict(zip(['min','median','max'],[float(x) for x in np.quantile(paired['timestamp_end']-paired['timestamp_start'],[0,.5,1])])),
               'label_mismatches_vs_start_inclusive_end_exclusive':int((expected!=actual).sum()),
               'mismatch_examples':labels.loc[expected!=actual].head(8).to_dict(orient='records'),
               'low_intensity_episodes':sum(e['low_intensity'] for e in episodes)}
out['memory_pressure']={'definition':'1 - MemAvailable / MemTotal; not process RSS or proof of a leak','range':[float(mp.min()),float(mp.max())],
                        'during_leak_range':[float(mp[memory_leak].min()),float(mp[memory_leak].max())],
                        'seconds_at_or_above_0_8':int((mp>=.8).sum()),'leak_episodes_reaching_0_8':sum(e['memory_pressure_max'] is not None and e['memory_pressure_max']>=.8 for e in episodes)}
out['timestamp_alignment']={name:{'same_row_count_as_meminfo':len(t)==len(mt),
                                'max_abs_timestamp_offset_when_equal_rows':float(np.max(np.abs(t-mt))) if len(t)==len(mt) else None,
                                'samples_outside_label_time_extent':int(((t<lt[0])|(t>=lt[-1]+1)).sum())} for name,t in timeline.items()}
out['leak_episode_details']=episodes
(ROOT/'data/metadata/antarex_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['streams','leak_episode_details']},indent=2),flush=True)
