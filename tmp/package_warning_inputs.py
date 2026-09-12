from pathlib import Path
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import warning_evaluation as w

names = [('review2_preprocessed_colab.zip', w.PREP_SHA256), ('review2_lstm_results_colab.zip', w.FORECAST_SHA256)]
paths = [ROOT / 'data/packages' / name for name, _ in names]
for path, (_, digest) in zip(paths, names):
    assert w.file_sha256(path) == digest
manifest = {'stage': 'warning evaluation inputs', 'protocol_version': w.PROTOCOL_VERSION,
            'protocol_sha256': w.file_sha256(ROOT / 'research/WARNING_PROTOCOL.md'),
            'files': [{'entry': path.name, 'bytes': path.stat().st_size, 'sha256': w.file_sha256(path)} for path in paths]}
package = ROOT / 'data/packages/review2_warning_inputs.zip'
with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_STORED) as archive:
    for path in paths:
        archive.write(path, path.name)
    archive.writestr('MANIFEST.json', json.dumps(manifest, indent=2))
receipt = {'file': package.name, 'bytes': package.stat().st_size, 'sha256': w.file_sha256(package), 'source_hashes_verified': True}
w.dump_json(package.with_suffix('.manifest.json'), receipt)
print(json.dumps(receipt, indent=2))
