"""Bounded ENV4 replay: five failing methods and related compilation/native regressions, never all 235.

Use the same SDK, four-CPU cgroup and Xorg configuration as the recorded run.
The observer records owned PID identities/resources and cgroup counters, not argv, environment or pipe secrets.
"""
import argparse, concurrent.futures, gzip, hashlib, json, os, pathlib, re, signal, subprocess, threading, time
from env4_processes import scan, owned_tree

REPO=pathlib.Path(__file__).resolve().parents[2]
GROUPS={
 'graph-call':['FeatureBlueprintTests.test_blueprint_owned_function_reference_call_import_cas_history_and_execution'],
 'graph-create':['FeatureBlueprintTests.test_blueprint_owned_node_creation_removal_review_group_and_cold_restore'],
 'ui-close':['WebUITests.test_actual_editor_v480_local_run_frame_ack_pause_step_reconnect_and_stop'],
 'native':['EngineTests.test_role_composition_two_windows_and_cleanup','ProjectExecutionTests.test_actual_native_button_game_pause_single_draw_step_and_stop','ProjectExecutionTests.test_actual_native_engine_cooperative_frame_callbacks','ButtonTests.test_shared_button_game_without_editor_state_input_navigation_native_targets_and_locality'],
 'related-ref':['PropertyAuthoringTests.test_field_ref_preview_typed_aliases_source_cas_cold_confirm_actual_clr_and_schema_rejection'],
 'related-set':['PropertyAuthoringTests.test_property_set_field_preview_explicit_profile_save_cold_confirm_actual_clr_and_schema_drift'],
}

def cgroup():
 result={}
 for name in ['cpu.stat','cpu.pressure','memory.current','memory.peak','memory.events','memory.pressure','pids.current']:
  p=pathlib.Path('/sys/fs/cgroup')/name
  if p.exists():result[name]=p.read_text().strip()
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('output',type=pathlib.Path);parser.add_argument('--workers',type=int,choices=[1,2,3,6],default=6);parser.add_argument('--groups',nargs='+',choices=GROUPS,default=list(GROUPS));parser.add_argument('--extended-load',action='store_true');parser.add_argument('--sample-seconds',type=float,choices=[.2,.5,1.0],default=.5);parser.add_argument('--xorg-config',type=pathlib.Path,required=True);args=parser.parse_args()
 if args.extended_load:
  GROUPS['related-ref'].append('WebUITests.test_actual_editor_v480_field_ref_restricted_catalog_true_parameter_cold_and_confirm')
  GROUPS['related-set'].append('WebUITests.test_actual_editor_v480_property_set_explicit_receiver_value_cold_and_confirm')
 out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);trace=out/'trace';trace.mkdir();active={};identities={};lock=threading.Lock();stop=threading.Event();started=time.monotonic_ns();outcomes={}
 names=subprocess.check_output(['git','ls-files','-z'],cwd=REPO).decode().split('\0')+subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=REPO).decode().split('\0')
 source={name:hashlib.sha256((REPO/name).read_bytes()).hexdigest() for name in sorted(set(names)) if name and name.split('/')[0] not in ['docs','reference'] and (REPO/name).is_file()}
 def intact():
  for name,digest in source.items():assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==digest,name
 metadata={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'workers':args.workers,'selectedGroups':args.groups,'methods':{k:GROUPS[k] for k in args.groups},'cpu.max':pathlib.Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory.max':pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip(),'source':source,'sourceManifestSha256':hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'xorgConfigSha256':hashlib.sha256(args.xorg_config.read_bytes()).hexdigest(),'samplingSeconds':args.sample_seconds,'resourceSampleSeconds':1,'before':cgroup(),'instrumentation':'Opt-in test fixture timing/wait snapshots + owned /proc observer. Assertions and original timeout values unchanged. Limited workload mix, not a replay of all 235 methods or their original launch timestamps.'}
 (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 def observer():
  last=0
  with gzip.open(out/'processes.jsonl.gz','wt') as output:
   while not stop.is_set():
    now=time.monotonic_ns();rows=scan()
    with lock:roots=dict(active)
    current={}
    for label,pid in roots.items():
     for row in owned_tree(pid,rows):current[(row['pid'],row['startTicks'])]=(label,row)
    for key,(label,row) in list(identities.items()):
     if key not in current and row['pid'] in rows and rows[row['pid']]['startTicks']==row['startTicks']:current[key]=(label,dict(rows[row['pid']],role=row['role']))
    births=[dict(group=label,**row) for key,(label,row) in current.items() if key not in identities]
    exits=[{'group':label,'pid':row['pid'],'startTicks':row['startTicks']} for key,(label,row) in identities.items() if key not in current]
    if births or exits:output.write(json.dumps({'monotonicNs':now,'births':births,'exits':exits},separators=(',',':'))+'\n')
    if now-last>=1_000_000_000:
     output.write(json.dumps({'monotonicNs':now,'cgroup':cgroup(),'processes':[dict(group=label,**row) for label,row in current.values()]},separators=(',',':'))+'\n');output.flush();last=now
    identities.clear();identities.update(current);stop.wait(args.sample_seconds)
 thread=threading.Thread(target=observer,daemon=True);thread.start()
 def run(name):
  intact();env=os.environ.copy();env['CONFECTORY_ENV4_TRACE']=str(trace);display=None;display_stream=None;begin=time.monotonic_ns()
  print('START',name,flush=True)
  try:
   if name=='native':
    assert not pathlib.Path('/tmp/.X11-unix/X97').exists(),'Owned display97 is already in use'
    display_stream=(out/'xorg-console.log').open('w');display=subprocess.Popen(['/usr/bin/Xorg',':97','-noreset','-nolisten','tcp','-ac','-config',str(args.xorg_config),'-logfile',str(out/'xorg.log')],stdout=display_stream,stderr=subprocess.STDOUT,start_new_session=True)
    for _ in range(150):
     if pathlib.Path('/tmp/.X11-unix/X97').exists():break
     assert display.poll() is None;time.sleep(.1)
    else:raise AssertionError('Xorg startup deadline')
    env['DISPLAY']=':97';env['XDG_CACHE_HOME']='/workspace/scratch/confectory-v480-integration/native-cache'
   command=[env['CONFECTORY_DOTNET'],str(REPO/'tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll'),*GROUPS[name],'--require-runtime']
   with (out/(name+'.log')).open('w') as stream:
    child=subprocess.Popen(command,cwd=REPO,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
    with lock:active[name]=child.pid
    code=child.wait()
   raw=(out/(name+'.log')).read_text();observed=re.findall(r'^(PASS|FAIL|SKIP) ([A-Za-z0-9]+Tests\.test_[^\n:]+)',raw,re.M);assert sorted(n for _,n in observed)==sorted(GROUPS[name]),(name,observed)
   row={'pid':child.pid,'exit':code,'startMonotonicNs':begin,'endMonotonicNs':time.monotonic_ns(),'outcomes':[{'method':n,'outcome':v} for v,n in observed],'logSha256':hashlib.sha256((out/(name+'.log')).read_bytes()).hexdigest()}
   with lock:outcomes[name]=row;(out/'outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n')
   print('DONE',name,code,flush=True);return code
  finally:
   if display is not None:
    os.killpg(display.pid,signal.SIGTERM);display.wait(timeout=10);display_stream.close()
   intact()
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:list(pool.map(run,args.groups))
 finally:
  stop.set();thread.join();metadata['after']=cgroup();metadata['elapsedSeconds']=(time.monotonic_ns()-started)/1e9;metadata['observerCpuSeconds']=time.process_time();(out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 print('COMPLETE',len(outcomes),'groups; failures retained; no automatic retries',flush=True)

if __name__=='__main__':main()
