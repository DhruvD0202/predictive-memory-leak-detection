"""Read-only numerical audit; does not preprocess data or train models."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
records = []
for file in sorted((ROOT / 'data/raw/westermo').glob('system-*.csv'), key=lambda p: int(p.stem.split('-')[1])):
    d = pd.read_csv(file)
    t = d['timestamp']
    delta = t.diff().iloc[1:]
    memory = 1 - d['sys-mem-available'] / d['sys-mem-total']
    swap_used = d['sys-mem-swap-total'] - d['sys-mem-swap-free']
    gaps = [{'before': int(t.iloc[i-1]), 'after': int(t.iloc[i]), 'delta_seconds': int(t.iloc[i]-t.iloc[i-1])} for i in np.where(t.diff().to_numpy() > 30)[0]]
    rec = {'file': file.name, 'rows': len(d), 'columns': list(d.columns),
           'start': int(t.min()), 'end': int(t.max()), 'span_days': float((t.max()-t.min())/86400),
           'duplicate_timestamps': int(t.duplicated().sum()), 'nonpositive_deltas': int((delta <= 0).sum()),
           'interval_counts': {str(k):int(v) for k,v in delta.value_counts().items()},
           'gaps': gaps, 'missing_30s_grid_points': int((t.max()-t.min())/30+1-len(d)),
           'null_cells': int(d.isna().sum().sum()), 'nonfinite_cells': int((~np.isfinite(d.to_numpy())).sum()),
           'constant_columns': [c for c in d if d[c].nunique(dropna=False) <= 1],
           'negative_counts': {c:int((d[c]<0).sum()) for c in d if (d[c]<0).any()},
           'memory_pressure_fraction_range': [float(memory.min()),float(memory.max())],
           'invalid_memory_pressure_count': int(((memory < 0)|(memory > 1)|~np.isfinite(memory)).sum()),
           'swap_used_bytes_range': [int(swap_used.min()),int(swap_used.max())],
           'cpu_user_max_raw': float(d['cpu-user'].max()),
           'server_up_counts': {str(k):int(v) for k,v in d['server-up'].value_counts().items()} if 'server-up' in d else None,
           'ranges': {c: [float(d[c].min()),float(d[c].max())] for c in d}}
    records.append(rec)
    print(file.name, len(d), 'columns',len(d.columns),'gaps',len(gaps),'missing_grid',rec['missing_30s_grid_points'],'nulls',rec['null_cells'],flush=True)
out = {'checked_on':'2026-09-07','files_audited':len(records),'total_rows':sum(r['rows'] for r in records),'systems':records}
(ROOT/'data/metadata/westermo_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
