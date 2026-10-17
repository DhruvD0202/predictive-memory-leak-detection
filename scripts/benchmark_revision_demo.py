"""Bounded local prototype measurements; never injects a leak or exhausts RAM."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, platform, statistics, sys, time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import psutil
from src.demo_service import DATASETS, ReplayRepository, LiveMonitor, SystemSampler, json_bytes, verify_manifest

def distribution(values):
    values=sorted(values)
    return {'n':len(values),'median':statistics.median(values),'p95':values[min(len(values)-1,int(.95*(len(values)-1)))],
            'min':min(values),'max':max(values),'mean':statistics.mean(values)}

def save_report(report):
    report['completed_utc']=datetime.now(timezone.utc).isoformat()
    out=ROOT/'results/revision_diagnostics'
    out.mkdir(exist_ok=True,parents=True)
    (out/'prototype_benchmark.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait-for-study',action='store_true')
    parser.add_argument('--skip-live',action='store_true',help='Measure archived replay/inference only; mark live collection unvalidated.')
    args=parser.parse_args()
    if args.wait_for_study:
        deadline=time.monotonic()+7200
        while not (ROOT/'results/revision_20261016/MANIFEST.json').exists():
            if time.monotonic()>deadline: raise TimeoutError('Study has not completed; no benchmark was run.')
            time.sleep(2)
    process=psutil.Process()
    report={'started_utc':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),
        'processor':platform.processor(),'logical_cpus':psutil.cpu_count(),'physical_cpus':psutil.cpu_count(logical=False),
        'installed_ram_gib':psutil.virtual_memory().total/2**30,'psutil':psutil.__version__,
        'python':platform.python_version(),'rss_before_repository_mib':process.memory_info().rss/2**20,
        'training_complete_before_benchmark':(ROOT/'results/revision_20261016/MANIFEST.json').exists(),
        'timing_scope':'In-process replay assembly/JSON and model requests; excludes HTTP, browser rendering and remote transport.'}
    tick=time.perf_counter(); repo=ReplayRepository(ROOT)
    report['repository_startup_seconds']=time.perf_counter()-tick
    report['source_files_verified']=repo.verified_files
    report['test_origins']=sum(len(rows) for rows in repo.records.values())
    report['rss_after_repository_mib']=process.memory_info().rss/2**20
    report['recordings']=[]
    for name in DATASETS:
        n=len(repo.records[name]); mid=n//2
        replay=[]
        for _ in range(100):
            tick=time.perf_counter(); response=repo.replay(name,mid); json_bytes(response)
            replay.append((time.perf_counter()-tick)*1000)
        now=response['current']['origin_timestamp']
        assert all(p['t']<=now for p in response['observations'])
        assert all(p['origin']<=now and 'actual' not in p for p in response['forecasts'])
        tick=time.perf_counter(); first=repo.infer(name,mid)
        first_ms=(time.perf_counter()-tick)*1000
        assert first['matches_saved']
        warm=[]; max_diff=first['absolute_difference_fraction']
        for i in range(100):
            index=[0,mid,n-1][i%3]
            tick=time.perf_counter(); response=repo.infer(name,index)
            warm.append((time.perf_counter()-tick)*1000)
            assert response['matches_saved']
            max_diff=max(max_diff,response['absolute_difference_fraction'])
        report['recordings'].append({'dataset':name,'replay_ms':distribution(replay),
            'first_inference_request_ms':first_ms,'warm_inference_ms':distribution(warm),
            'max_prediction_difference_fraction':max_diff,'inference_requests':101})
    report['rss_after_all_models_mib']=process.memory_info().rss/2**20
    report['source_files_verified_after']=verify_manifest(repo.forecasts)+verify_manifest(repo.warnings)
    if args.skip_live:
        report['live']={'completed':False,'scope':'Live performance not measured in this run. The preceding restricted-environment attempt collected zero samples because Windows performance-counter access failed. An unrestricted rerun was not executed because automatic approval review was unavailable.'}
        save_report(report)
        return
    # Instrument the collector without changing its values, cadence or warning rule.
    original=SystemSampler.sample
    sample_ms=[]
    def measured_sample(self):
        tick=time.perf_counter()
        row=original(self)
        sample_ms.append((time.perf_counter()-tick)*1000)
        return row
    SystemSampler.sample=measured_sample
    monitor=LiveMonitor(ROOT,cadence=5,max_samples=36)
    cpu_start=process.cpu_times(); wall=time.monotonic(); rss=[]; system_cpu=[]
    try:
        monitor.start(.8)
        while monitor.thread.is_alive():
            monitor.thread.join(timeout=1)
            rss.append(process.memory_info().rss/2**20)
            system_cpu.append(psutil.cpu_percent(interval=None))
        snapshot=monitor.snapshot()
        assert snapshot['error'] is None and len(snapshot['rows'])==36
        rows=snapshot['rows']
        assert any(row['ready'] for row in rows)
        exported=monitor.export()
        assert len(exported.splitlines())==37
    finally:
        monitor.stop()
        SystemSampler.sample=original
    elapsed=time.monotonic()-wall; cpu_end=process.cpu_times()
    cpu_seconds=(cpu_end.user+cpu_end.system)-(cpu_start.user+cpu_start.system)
    intervals=[b['timestamp']-a['timestamp'] for a,b in zip(rows,rows[1:])]
    report['live']={'samples':len(rows),'cadence_requested_seconds':5,
        'elapsed_wall_seconds':elapsed,'observed_span_seconds':rows[-1]['timestamp']-rows[0]['timestamp'],
        'sampling_intervals_seconds':distribution(intervals),'collector_call_ms':distribution(sample_ms),
        'process_cpu_seconds':cpu_seconds,'process_cpu_percent_one_logical_cpu':cpu_seconds/elapsed*100,
        'sampled_process_rss_mib':distribution(rss),'system_cpu_percent':distribution(system_cpu),
        'ready_samples':sum(row['ready'] for row in rows),'warning_samples':sum(row['warning'] for row in rows),
        'alarm_starts':sum(row['alarm_start'] for row in rows),'export_rows':len(exported.splitlines())-1,
        'page_faults_available':any(row['page_faults_per_second'] is not None for row in rows),
        'leak_labels_available':False,'lstm_applied_to_live':False,
        'intentional_leak_or_exhaustion_workload':False,
        'scope':'One 36-sample Windows smoke test. Process RSS includes retained replay data, imported libraries and all four loaded models. CPU is process CPU time/wall time, with 100% equal to one logical CPU. Host background activity is uncontrolled; this is not a production overhead estimate.'}
    report['live']['completed']=True
    save_report(report)

if __name__=='__main__': main()
