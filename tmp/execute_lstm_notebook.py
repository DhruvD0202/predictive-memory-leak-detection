"""Execute the delivered LSTM notebook and retain real outputs with live progress."""
import base64,contextlib,io,json
from datetime import datetime,timezone
from pathlib import Path
import sys,time

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'notebooks/03_lstm_colab.ipynb'
nb=json.loads(path.read_text(encoding='utf-8'))
namespace={'__name__':'__notebook__'}
started=time.perf_counter(); count=0
class Tee(io.StringIO):
    def __init__(self,terminal): super().__init__(); self.terminal=terminal
    def write(self,text): self.terminal.write(text); self.terminal.flush(); return super().write(text)
    def flush(self): self.terminal.flush(); super().flush()

for cell in nb['cells']:
    if cell['cell_type']!='code': continue
    count+=1; outputs=[]
    def display(value):
        data={'text/plain':str(value)}
        if hasattr(value,'to_html'): data['text/html']=value.to_html(index=False)
        elif hasattr(value,'save') and hasattr(value,'mode'):
            buf=io.BytesIO(); value.save(buf,format='PNG'); data['image/png']=base64.b64encode(buf.getvalue()).decode()
        outputs.append({'output_type':'display_data','metadata':{},'data':data})
    namespace['display']=display
    captured=Tee(sys.stdout)
    print(f'Executing notebook cell {count}',flush=True)
    with contextlib.redirect_stdout(captured),contextlib.redirect_stderr(captured):
        exec(compile(''.join(cell['source']),f'{path.name}:cell{count}','exec'),namespace)
    if captured.getvalue(): outputs.append({'output_type':'stream','name':'stdout','text':captured.getvalue()})
    cell['execution_count']=count; cell['outputs']=outputs
nb['metadata']['execution_evidence']={'environment':'Local Windows CPU; hosted Colab run not yet verified',
    'completed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':round(time.perf_counter()-started,2),
    'code_cells_executed':count,'all_cells_succeeded':True}
path.write_text(json.dumps(nb,indent=1,ensure_ascii=False),encoding='utf-8')
print(json.dumps(nb['metadata']['execution_evidence']),flush=True)
