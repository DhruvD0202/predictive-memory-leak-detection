"""Package the verified study and anonymous handoff materials."""
from pathlib import Path
import argparse, hashlib, json, shutil, zipfile
ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def data_archive():
    source=ROOT/'results/revision_20261016'
    manifest=json.loads((source/'MANIFEST.json').read_text())
    dest=ROOT/'data/packages/revision_study_results_20261016.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for item in manifest['files']:
            path=source/item['path']
            assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes']
            archive.write(path,item['path'])
        archive.write(source/'MANIFEST.json','MANIFEST.json')
    receipt={'file':dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'files':len(manifest['files'])+1,
        'restore_root':'results/revision_20261016','model_count':40,
        'contains':'All study-manifest files, including selected weights, configurations, training origins, histories, validation/test forecasts, warnings and summaries. Optimizer resume checkpoints are excluded.',
        'input_package_required':'review2_lstm_inputs.zip','input_sha256':'208c3b38ffbd7564e95f7452e0a3d203b1d4734858383e43cf602093ef7a1222'}
    dest.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Full result archive:',dest.name,receipt['bytes'],'bytes')

def configuration_copies():
    dest=ROOT/'results/revision_diagnostics/configuration'
    source=ROOT/'data/revision_inputs'
    for name in ['antarex_mono','westermo_1','westermo_2','westermo_3']:
        folder=dest/name; folder.mkdir(parents=True,exist_ok=True)
        for filename in ['summary.json','scaler.json']:
            shutil.copyfile(source/'prepared'/name/filename,folder/filename)
        shutil.copyfile(source/'baselines'/name/'frozen_settings.json',folder/'baseline_settings.json')
    shutil.copyfile(source/'prepared/preprocessing_summary.json',dest/'preprocessing_summary.json')

def zip_items(path,items):
    path.parent.mkdir(parents=True,exist_ok=True)
    manifest=[]
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,data in sorted(items.items()):
            archive.writestr(name,data)
            manifest.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        archive.writestr('PACKAGE_MANIFEST.json',json.dumps({'files':manifest},indent=2)+'\n')
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(manifest)+1
        for item in manifest:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest()==item['sha256']
    print(path.name,len(manifest),'verified files',path.stat().st_size,'bytes')

def handoffs():
    manuscript=ROOT/'paper/spin2027'
    build=ROOT/'tmp/pdfs/spin_20261016/build'
    assert (build/'main.pdf').is_file() and (build/'main.bbl').is_file()
    shutil.copyfile(build/'main.bbl',manuscript/'main.bbl')
    shutil.copyfile(build/'DescriptionTexts.txt',manuscript/'DescriptionTexts.txt')
    with zipfile.ZipFile(ROOT/'tmp/pdfs/spin_20261016/springer_templates.zip') as template:
        (manuscript/'SPRINGER_README.txt').write_bytes(template.read('readme.txt'))
        for name in ['llncs.cls','splncs04.bst']:
            assert template.read(name)==(manuscript/name).read_bytes()
    items={p.relative_to(manuscript).as_posix():p.read_bytes() for p in manuscript.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.bbl','.cls','.bst','.md','.txt','.pdf']}
    zip_items(ROOT/'output/latex/SPIN2027_Overleaf.zip',items)
    code={}
    def add(path): code[path.relative_to(ROOT).as_posix()]=path.read_bytes()
    for name in ['app.py','start_demo.ps1','requirements-app.txt','requirements-lstm.txt','requirements-baselines.txt','requirements-revision.txt']:
        add(ROOT/name)
    for folder in ['src','tests','dashboard','results/lstm_colab','results/warnings_colab','results/revision_diagnostics']:
        for path in (ROOT/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts: add(path)
    for path in (ROOT/'results/revision_20261016').rglob('*'):
        if path.is_file() and path.name!='last_checkpoint.pt' and path.suffix not in ['.gz','.npy']: add(path)
    for name in ['run_revision_study','verify_revision_study','restore_revision_results','analyze_revision_evidence','benchmark_revision_demo','write_spin_results','verify_demo']:
        add(ROOT/'scripts'/f'{name}.py')
    for name in ['REVISION_PROTOCOL_20261016.md','REVISION_REPRODUCTION.md','BASELINE_PROTOCOL.md','LSTM_PROTOCOL.md','WARNING_PROTOCOL.md']:
        add(ROOT/'research'/name)
    for path in (ROOT/'notebooks').glob('*.ipynb'):
        notebook=json.loads(path.read_text(encoding='utf-8'))
        for cell in notebook['cells']:
            if cell['cell_type']=='code': cell['outputs']=[]; cell['execution_count']=None
            if cell['cell_type']=='markdown':
                cell['source']=[line.replace('C:/dhruv/VIT/Sem-5/OS/Research_Project/','<project-root>/') for line in cell['source']]
            cell.get('metadata',{}).pop('execution',None)
        code[path.relative_to(ROOT).as_posix()]=(json.dumps(notebook,indent=1,ensure_ascii=False)+'\n').encode('utf-8')
    for name,data in items.items(): code['paper/spin2027/'+name]=data
    add(ROOT/'data/packages/revision_study_results_20261016.json')
    readme='''# Anonymous research code supplement

This package supports **Memory-Pressure Forecasting and Growth-Based Warnings: An Empirical Study**. It contains experimental source, four notebooks with outputs cleared, dashboard source, tests, exact settings, selected model weights and numerical results. Notebook outputs are removed and personal folder names in Markdown instructions are replaced by a generic project-root placeholder. These changes prevent local paths from identifying the authors; executable notebook code is unchanged. The study's original per-origin forecasts remain in their verified files.

Start with `research/REVISION_REPRODUCTION.md`. The pinned revision environment and CPU PyTorch installation are documented there. Required input ZIPs are **not** included: obtain the checksum-matching packages from the authors or rebuild using the public data sources and documented pipeline. Access must be arranged with reviewers; this local package is not a public release.

The small new result/configuration files and 40 selected weights are included. The new study's bulk per-origin predictions, warnings and origin arrays are supplied separately in `revision_study_results_20261016.zip`; its JSON receipt is included. The study MANIFEST lists that complete archive, while PACKAGE_MANIFEST lists files actually present in this supplement. Restore the full archive plus required input package before running the default saved-study checker, or train into a new reproduction directory as documented.

The original replay is runnable after installing `requirements-app.txt`: run `python app.py`. On-demand LSTM inference also needs PyTorch and the prepared package. Run `python app.py --prepare data/packages/review2_preprocessed_colab.zip` to restore it; expected SHA-256 is `287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2`. The server binds to 127.0.0.1:8765. The 40 implementation tests use local loopback access.

Original notebooks run in order: 01 uses `review2_pilot_raw.zip`; 02 uses `review2_preprocessed_colab.zip`; 03 uses `review2_lstm_inputs.zip`; 04 uses `review2_warning_inputs.zip`. Preserve each stage's output and integrity receipt. Data sources and their CC BY 4.0 attribution are in the reproduction guide.

Results distinguish forecasts, controlled injected-leak recognition and unlabeled telemetry. No naturally occurring leak diagnosis, validated pre-exhaustion warning or live performance measurement is established. The October live attempt failed before collecting samples. The disclosed AI assistance applies to the code and manuscript; the authors must review and take responsibility before submission.
'''
    code['README.md']=readme.encode()
    banned=['dhruv','dudeja','ayush','srivallabha','24bce0968','24bds0180','24bce0457','c:\\users\\hp']
    for name,data in code.items():
        if Path(name).suffix in ['.md','.json','.py','.ipynb','.tex','.txt','.js','.html','.css','.bib','.bbl']:
            text=data.decode('utf-8').lower()
            assert not any(word in text for word in banned),'Identity string in '+name
    zip_items(ROOT/'output/supplement/SPIN2027_Reproducibility_Code.zip',code)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--data-only',action='store_true'); parser.add_argument('--handoffs-only',action='store_true')
    args=parser.parse_args()
    if not args.handoffs_only: data_archive(); configuration_copies()
    if not args.data_only: handoffs()

if __name__=='__main__': main()
