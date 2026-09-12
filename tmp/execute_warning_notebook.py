"""Run all notebook cells locally and retain measured outputs, with live progress."""
import base64
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'notebooks/04_leak_warning_colab.ipynb'
notebook = json.loads(path.read_text(encoding='utf-8'))
namespace = {'__name__': '__notebook__'}
started = time.perf_counter()
count = 0


class Tee(io.StringIO):
    def write(self, text):
        sys.__stdout__.write(text)
        sys.__stdout__.flush()
        return super().write(text)


for cell in notebook['cells']:
    if cell['cell_type'] != 'code':
        continue
    count += 1
    outputs = []
    def display(value):
        data = {'text/plain': str(value)}
        if hasattr(value, 'to_html'):
            data['text/html'] = value.to_html(index=False)
        elif hasattr(value, 'save') and hasattr(value, 'mode'):
            buffer = io.BytesIO()
            value.save(buffer, format='PNG')
            data['image/png'] = base64.b64encode(buffer.getvalue()).decode()
        outputs.append({'output_type': 'display_data', 'metadata': {}, 'data': data})
    namespace['display'] = display
    captured = Tee()
    print(f'Executing warning notebook cell {count}', flush=True)
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        exec(compile(''.join(cell['source']), f'{path.name}:cell{count}', 'exec'), namespace)
    if captured.getvalue():
        outputs.append({'output_type': 'stream', 'name': 'stdout', 'text': captured.getvalue()})
    cell['execution_count'] = count
    cell['outputs'] = outputs
notebook['metadata']['execution_evidence'] = {
    'environment': 'Local Windows CPU using verified Colab inputs; hosted warning run pending',
    'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': round(time.perf_counter() - started, 2),
    'code_cells_executed': count, 'all_cells_succeeded': True}
path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding='utf-8')
print(json.dumps(notebook['metadata']['execution_evidence']), flush=True)
