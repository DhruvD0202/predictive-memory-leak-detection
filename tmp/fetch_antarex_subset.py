"""Fetch approved CPU/memory members via standard HTTP byte ranges."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import struct
import time
import urllib.request
import zlib

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://zenodo.org/api/records/2553224/files/Antarex.zip/content'
SIZE = 1632357471
BLOCK = 8 * 1024 * 1024
META = ROOT / 'data/metadata'

def get_range(start, end):
    for attempt in range(3):
        try:
            request = urllib.request.Request(URL, headers={'Range': f'bytes={start}-{end}', 'User-Agent':'AcademicDatasetValidation/1.0'})
            with urllib.request.urlopen(request, timeout=90) as response:
                expected = f'bytes {start}-{end}/{SIZE}'
                if response.status != 206 or response.headers.get('Content-Range') != expected:
                    raise ValueError(f'Range not honored: {response.status}, {response.headers.get("Content-Range")}')
                data = response.read(end-start+2)
                if len(data) != end-start+1:
                    raise ValueError(f'Incomplete range: {len(data)}')
                return data
        except Exception as exc:
            print(f'Range retry {attempt+1}: {exc}', flush=True)
            if attempt == 2:
                raise
            time.sleep(3)

def member_data_start(m):
    header = get_range(m['offset'], m['offset']+29)
    values = struct.unpack('<4s5H3I2H', header)
    if values[0] != b'PK\x03\x04' or values[3] != 0:
        raise ValueError('Expected stored ZIP member')
    return m['offset'] + 30 + values[-2] + values[-1]

def acquire(m):
    name = Path(m['name'])
    destination = ROOT / 'data/raw/antarex' / name.relative_to('Antarex')
    start = member_data_start(m)
    if not destination.exists():
        chunks = ROOT / 'tmp' / (name.name + '.chunks')
        chunks.mkdir(parents=True, exist_ok=True)
        def chunk(i):
            lo = start+i*BLOCK
            hi = min(start+m['size']-1,lo+BLOCK-1)
            dest = chunks/f'{i:04d}.bin'
            if not dest.exists() or dest.stat().st_size != hi-lo+1:
                dest.write_bytes(get_range(lo,hi))
            print(f'{name.name}: chunk {i+1}/{(m["size"]+BLOCK-1)//BLOCK}',flush=True)
            return dest
        count = (m['size']+BLOCK-1)//BLOCK
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            files = list(pool.map(chunk, range(count)))
        destination.parent.mkdir(parents=True,exist_ok=True)
        part = destination.with_name(destination.name+'.part')
        with part.open('wb') as out:
            for f in files:
                out.write(f.read_bytes())
        part.replace(destination)
    crc = 0
    sha = hashlib.sha256()
    with destination.open('rb') as src:
        while data := src.read(BLOCK):
            crc = zlib.crc32(data, crc)
            sha.update(data)
    if destination.stat().st_size != m['size'] or crc != m['crc']:
        raise ValueError(f'{name}: ZIP CRC/size mismatch')
    return {'archive_url':URL,'archive_member':m['name'],'path':str(destination.relative_to(ROOT)),
            'bytes':m['size'],'zip_crc_verified':True,'sha256':sha.hexdigest()}

def main():
    members = json.loads((META/'antarex_archive_members.json').read_text())
    wanted = [m for m in members if 'CPU-MEM_' in m['name'] and m['name'].endswith('.csv')]
    wanted += [m for m in members if m['name'].endswith('results_cpu-mem-mono.7z')]
    manifest = []
    for member in wanted:
        manifest.append(acquire(member))
        (META/'antarex_subset_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Selected CPU/memory block and both workload schedules verified.',flush=True)

if __name__ == '__main__':
    main()
