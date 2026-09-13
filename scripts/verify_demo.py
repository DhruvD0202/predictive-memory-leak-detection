"""Verify the runnable prototype without training or tuning any model."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.demo_service import DATASETS, ReplayRepository, json_bytes, verify_manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-checks',action='store_true',help='Also run saved LSTMs; requires torch and the verified prepared data')
    args=parser.parse_args()
    start=time.perf_counter()
    repository=ReplayRepository(ROOT)
    report={'checked_utc':datetime.now(timezone.utc).isoformat(),'source_files_verified':repository.verified_files,
            'test_origins_available':sum(len(r) for r in repository.records.values()),
            'dataset_checks':[], 'new_training_performed':False, 'paper_written':False}
    for dataset in DATASETS:
        count=len(repository.records[dataset])
        cases=[]
        for index in [0,count//2,count-1]:
            replay=repository.replay(dataset,index)
            now=replay['current']['origin_timestamp']
            assert all(p['t']<=now for p in replay['observations'])
            assert all(p['origin']<=now and 'actual' not in p for p in replay['forecasts'])
            assert all(a['t']<=now for a in replay['alarms'])
            if dataset!='antarex_mono':
                assert all(p['leak'] is None for p in replay['observations'])
            json_bytes(replay)
            case={'index':index,'causal_display_passed':True}
            if args.model_checks:
                inference=repository.infer(dataset,index)
                assert inference['matches_saved'],inference
                case['inference']=inference
            cases.append(case)
        timings=[]
        for _ in range(30):
            tick=time.perf_counter()
            json_bytes(repository.replay(dataset,count//2))
            timings.append((time.perf_counter()-tick)*1000)
        report['dataset_checks'].append({'dataset':dataset,'cases':cases,
            'replay_prepare_and_serialize_median_ms':statistics.median(timings),
            'replay_prepare_and_serialize_max_ms':max(timings)})
    report['source_files_verified_after_checks']=verify_manifest(repository.forecasts)+verify_manifest(repository.warnings)
    report['timing_scope']='Local replay response assembly/JSON serialization; excludes browser/HTTP. Inference timings are separately scoped per request; not production monitoring overhead.'
    report['elapsed_seconds']=time.perf_counter()-start
    report['all_checks_passed']=True
    output=ROOT/'results/verification/implementation_checks.json'
    output.write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    print(f'Passed: {report["source_files_verified"]} source files; {report["test_origins_available"]} replay origins; 12 boundary/midpoint checks.')
    print('Saved:',output)


if __name__=='__main__':
    main()
