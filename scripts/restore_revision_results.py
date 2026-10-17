"""Restore the supplied, checksummed study archive without overwriting different files."""
from pathlib import Path
import argparse, hashlib, json, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.lstm_forecasting import unpack_inputs

def sha(path):
    with path.open('rb') as handle: return hashlib.file_digest(handle,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,default=ROOT/'data/packages/revision_study_results_20261016.zip')
    parser.add_argument('--receipt',type=Path,default=ROOT/'data/packages/revision_study_results_20261016.json')
    parser.add_argument('--input-package',type=Path,default=ROOT/'data/packages/review2_lstm_inputs.zip')
    args=parser.parse_args()
    receipt=json.loads(args.receipt.read_text())
    assert sha(args.archive)==receipt['sha256'],'Wrong result archive'
    target=(ROOT/'results/revision_20261016').resolve()
    with zipfile.ZipFile(args.archive) as archive:
        manifest=json.loads(archive.read('MANIFEST.json'))
        files={item['path']:item for item in manifest['files']}
        assert len(files)==len(manifest['files'])
        assert set(archive.namelist())==set(files)|{'MANIFEST.json'}
        assert len(archive.namelist())==len(files)+1
        # Verify every entry and existing destination before writing any result.
        for name in archive.namelist():
            dest=(target/name).resolve()
            assert dest.is_relative_to(target),'Unsafe archive entry'
            content=archive.read(name); digest=hashlib.sha256(content).hexdigest()
            if name in files:
                assert len(content)==files[name]['bytes'] and digest==files[name]['sha256']
            if dest.exists(): assert sha(dest)==digest,'Refusing to replace different file: '+str(dest)
        for name in archive.namelist():
            dest=target/name; dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists(): dest.write_bytes(archive.read(name))
    unpack_inputs(args.input_package,ROOT/'data/revision_inputs')
    print('Restored verified results and inputs. Run scripts/verify_revision_study.py next.')

if __name__=='__main__': main()
