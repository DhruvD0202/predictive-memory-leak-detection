"""Execute the delivered notebook cells locally and preserve their real outputs."""
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'notebooks/01_preprocessing_colab.ipynb'
nb=json.loads(path.read_text(encoding='utf-8'))
namespace={'__name__':'__notebook__'}
count=0
start=time.perf_counter()
for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    count+=1
    outputs=[]
    def display(value):
        data={'text/plain':str(value)}
        if hasattr(value,'to_html'):
            data['text/html']=value.to_html(index=False)
        outputs.append({'output_type':'display_data','metadata':{},'data':data})
    namespace['display']=display
    captured=io.StringIO()
    print(f'Executing notebook code cell {count}...',flush=True)
    with contextlib.redirect_stdout(captured),contextlib.redirect_stderr(captured):
        exec(compile(''.join(cell['source']),f'{path.name}:cell{count}','exec'),namespace)
    if captured.getvalue():
        outputs.append({'output_type':'stream','name':'stdout','text':captured.getvalue()})
        print(captured.getvalue(),flush=True)
    cell['execution_count']=count
    cell['outputs']=outputs
nb['metadata']['execution_evidence']={'environment':'Local Windows CPU; not a hosted Google Colab run',
    'completed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':round(time.perf_counter()-start,2),
    'code_cells_executed':count,'all_cells_succeeded':True}
path.write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
print(json.dumps(nb['metadata']['execution_evidence']),flush=True)
