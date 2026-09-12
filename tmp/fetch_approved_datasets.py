"""Acquire only the two datasets approved on 2026-09-07."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / 'data' / 'metadata'
COMMIT = '47e0ccdc10c30e86327d6eb828ed48d164469fd4'

def fetch(url, dest, expected_size=None, md5=None, blob_sha=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + '.part')
    if not dest.exists():
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'AcademicDatasetValidation/1.0'})
                with urllib.request.urlopen(req, timeout=90) as response, part.open('wb') as out:
                    while block := response.read(4 * 1024 * 1024):
                        out.write(block)
                part.replace(dest)
                break
            except Exception as exc:
                print(f'Retry {attempt + 1}: {dest.name}: {exc}', flush=True)
                if attempt == 2:
                    raise
                time.sleep(3)
    size = dest.stat().st_size
    m = hashlib.md5()
    sha = hashlib.sha256()
    git = hashlib.sha1(f'blob {size}\0'.encode())
    with dest.open('rb') as source:
        while block := source.read(4 * 1024 * 1024):
            m.update(block)
            sha.update(block)
            git.update(block)
    if expected_size is not None and size != expected_size:
        raise ValueError(f'{dest.name}: size mismatch {size} != {expected_size}')
    if md5 and m.hexdigest() != md5:
        raise ValueError(f'{dest.name}: publisher MD5 mismatch')
    if blob_sha and git.hexdigest() != blob_sha:
        raise ValueError(f'{dest.name}: Git blob hash mismatch')
    result = {'url': url, 'path': str(dest.relative_to(ROOT)), 'bytes': size,
              'sha256': sha.hexdigest(), 'md5': m.hexdigest(),
              'publisher_hash_verified': bool(md5 or blob_sha)}
    print(f'Acquired {dest.name}: {size:,} bytes; verified={result["publisher_hash_verified"]}', flush=True)
    return result

def main():
    results = []
    results.append(fetch('https://zenodo.org/api/records/2553224', META / 'antarex_record_2553224.json'))
    results.append(fetch(f'https://api.github.com/repos/westermo/test-system-performance-dataset/git/trees/{COMMIT}?recursive=1', META / 'westermo_tree.json'))
    record = json.loads((META / 'antarex_record_2553224.json').read_text())
    tree = json.loads((META / 'westermo_tree.json').read_text())
    tasks = []
    for f in record['files']:
        tasks.append((f['links']['self'], ROOT / 'data' / 'raw' / 'antarex' / f['key'],
                      f['size'], f['checksum'].split(':', 1)[1], None))
    for f in tree['tree']:
        if f['path'].startswith('data/') and f['path'].endswith('.csv') or f['path'] in ('LICENSE', 'README.md'):
            url = f'https://raw.githubusercontent.com/westermo/test-system-performance-dataset/{COMMIT}/{f["path"]}'
            dest = ROOT / 'data' / 'raw' / 'westermo' / Path(f['path']).name
            tasks.append((url, dest, f['size'], None, f['sha']))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(fetch, *args) for args in tasks]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            (META / 'download_manifest.json').write_text(json.dumps({'checked_on': '2026-09-07', 'westermo_commit': COMMIT, 'files': results}, indent=2), encoding='utf-8')
    print('All approved source files acquired and checked.', flush=True)

if __name__ == '__main__':
    main()
