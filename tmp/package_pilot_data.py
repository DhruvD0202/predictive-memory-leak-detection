"""Package original pilot data and provenance; no preprocessing is performed."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/packages'
OUT.mkdir(parents=True,exist_ok=True)
target=OUT/'review2_pilot_raw.zip'
base=ROOT/'data/raw/antarex/CPU-MEM_mono/extracted/results'
files=[]
for name in ['meminfo','vmstat','procstat','procdiskstats']:
    files.append((base/'ldms/csv'/name,'antarex/CPU-MEM_mono/'+name+'.csv'))
files += [(p,'antarex/CPU-MEM_mono/'+p.name) for p in sorted(base.glob('*.csv'))]
files += [(ROOT/f'data/raw/westermo/system-{i}.csv',f'westermo/system-{i}.csv') for i in [1,2,3]]
files += [(ROOT/'data/raw/westermo'/name,'westermo/'+name) for name in ['LICENSE','README.md']]
files.append((ROOT/'data/raw/antarex/Readme_Antarex_Dataset.pdf','antarex/Readme_Antarex_Dataset.pdf'))
files += [(p,'provenance/'+p.name) for p in sorted((ROOT/'data/metadata').glob('*.json'))]
manifest={'created_on':'2026-09-07','description':'Unmodified source content. Only the four required Antarex streams and their labels/logs, Westermo systems 1-3, and provenance are packaged. No training or preprocessing has been run.','files':[]}
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as archive:
    for source,name in files:
        sha=hashlib.sha256()
        with source.open('rb') as src,archive.open(name,'w',force_zip64=True) as dest:
            while data:=src.read(4*1024*1024):
                dest.write(data)
                sha.update(data)
        manifest['files'].append({'entry':name,'source_project_path':str(source.relative_to(ROOT)),'bytes':source.stat().st_size,'sha256':sha.hexdigest()})
        print('Packaged',name,flush=True)
    archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as archive:
    for entry in manifest['files']:
        sha=hashlib.sha256()
        with archive.open(entry['entry']) as src:
            while data:=src.read(4*1024*1024):
                sha.update(data)
        assert sha.hexdigest()==entry['sha256'],entry['entry']
with target.open('rb') as src:
    sha=hashlib.file_digest(src,'sha256').hexdigest()
summary={'file':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,'sha256':sha,'source_content_bytes':sum(e['bytes'] for e in manifest['files']),'all_entry_hashes_verified':True,'files':manifest['files']}
(OUT/'review2_pilot_raw.manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('Verified package:',summary['bytes'],'bytes, SHA256',sha,flush=True)
