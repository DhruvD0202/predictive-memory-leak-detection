import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
folder=root/'data/packages'
expected={'review2_preprocessed_colab.zip':'287ffaa139819f78f493e540e527c56ac0c240477034c76fa8b258b94d5e6bb2',
          'review2_baseline_results_colab.zip':'2b242a47288ea5db25ddd4d79de2069980ef1dc462fea157580e67ec19c01ba3'}
files=[]
for name,digest in expected.items():
    p=folder/name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    files.append({'entry':name,'sha256':digest,'bytes':p.stat().st_size})
output=folder/'review2_lstm_inputs.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as archive:
    for item in files: archive.write(folder/item['entry'],item['entry'])
    archive.writestr('MANIFEST.json',json.dumps({'stage':'LSTM inputs','files':files},indent=2))
receipt={'file':output.name,'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'files':files}
output.with_suffix('.manifest.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
