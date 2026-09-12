"""Recover complete stored ZIP members from the interrupted approved download."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'data/raw/antarex/Antarex.zip.part'
members = json.loads((ROOT/'data/metadata/antarex_archive_members.json').read_text())
records = []
with source.open('rb') as stream:
    for m in members:
        if not ('CPU-MEM_' in m['name'] and m['name'].endswith('.csv') or m['name'].endswith('results_cpu-mem-mono.7z')):
            continue
        stream.seek(m['offset'])
        header = struct.unpack('<4s5H3I2H',stream.read(30))
        assert header[0] == b'PK\x03\x04' and header[3] == 0
        name = stream.read(header[-2]).decode('utf-8')
        assert name == m['name']
        stream.read(header[-1])
        assert stream.tell()+m['size'] <= source.stat().st_size, f'Incomplete member: {name}'
        dest = ROOT/'data/raw/antarex'/Path(name).relative_to('Antarex')
        dest.parent.mkdir(parents=True,exist_ok=True)
        crc = 0
        sha = hashlib.sha256()
        remaining = m['size']
        with dest.open('wb') as out:
            while remaining:
                block = stream.read(min(4*1024*1024, remaining))
                assert block
                out.write(block)
                remaining -= len(block)
                crc = zlib.crc32(block,crc)
                sha.update(block)
        assert crc == m['crc'], f'ZIP CRC mismatch: {name}'
        records.append({'archive_url':'https://zenodo.org/api/records/2553224/files/Antarex.zip/content',
                        'archive_member':name,'path':str(dest.relative_to(ROOT)), 'bytes':m['size'],
                        'zip_crc_verified':True,'sha256':sha.hexdigest(),
                        'note':'Complete member recovered from partial ZIP; full archive MD5 not verified.'})
        print(name,m['size'],'CRC verified',flush=True)
(ROOT/'data/metadata/antarex_subset_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
