"""Read-only Linux observations for owned ENV4 test process trees. Never record argv/env secrets."""
import json, os, pathlib, time

HZ=os.sysconf('SC_CLK_TCK')
PAGE=os.sysconf('SC_PAGE_SIZE')

def scan():
 rows={}
 for path in pathlib.Path('/proc').iterdir():
  if not path.name.isdigit():continue
  try:
   fields=(path/'stat').read_text().rsplit(') ',1)[1].split();args=(path/'cmdline').read_bytes().decode(errors='replace').split('\0');args=[x for x in args if x]
   dll=next((pathlib.Path(a).name for a in args[1:] if a.endswith('.dll')),'')
   role='other'
   if dll=='Confectory.Tests.dll':role='test-harness'
   elif dll=='Confectory.ProjectExecutionHost.dll':role='run-worker' if 'run' in args else 'metadata-execution-host'
   elif dll=='Confectory.ElementAuthoring.dll':role='element-authoring-host'
   elif dll=='Confectory.Build.DotNet.dll':role='compiler-pack-host'
   elif dll in ['VBCSCompiler.dll','MSBuild.dll']:role='compiler-server'
   elif 'build' in args[:3]:role='sdk-build'
   elif args and pathlib.Path(args[0]).name.startswith('chrom'):role='browser'
   elif args and pathlib.Path(args[0]).name=='Xorg':role='xorg'
   elif args and args[0].endswith('python3'):role='python-fixture'
   elif dll:role='generated-driver'
   rows[int(path.name)]={'pid':int(path.name),'ppid':int(fields[1]),'startTicks':int(fields[19]),'state':fields[0],
    'cpuMs':(int(fields[11])+int(fields[12]))*1000/HZ,'waitedChildCpuMs':(int(fields[13])+int(fields[14]))*1000/HZ,'rss':max(0,int(fields[21]))*PAGE,'threads':int(fields[17]),
    'executable':pathlib.Path(args[0]).name if args else '', 'assembly':dll,'role':role}
  except (OSError,ValueError,IndexError):continue
 return rows

def owned_tree(pid, rows=None):
 rows=scan() if rows is None else rows;owned={pid};changed=True
 while changed:
  added={n for n,r in rows.items() if r['ppid'] in owned}-owned;changed=bool(added);owned|=added
 result=[]
 for n in sorted(owned):
  if n not in rows:continue
  row=dict(rows[n]);parent=rows.get(row['ppid'],{})
  if row['role']=='generated-driver' and parent.get('role')=='run-worker':row['role']='run-runtime'
  result.append(row)
 return result

def event(phase, data):
 folder=os.environ.get('CONFECTORY_ENV4_TRACE')
 if not folder:return
 row={'utc':time.time(),'monotonicNs':time.monotonic_ns(),'pid':os.getpid(),'phase':phase,'data':data}
 with (pathlib.Path(folder)/('python-'+str(os.getpid())+'.jsonl')).open('a') as output:output.write(json.dumps(row,separators=(',',':'))+'\n')

def tree_event(pid, phase):
 if not os.environ.get('CONFECTORY_ENV4_TRACE'):return []
 rows=owned_tree(pid);event(phase,{'hostPid':pid,'processes':rows});return rows

def remember_runs(host_pid, known):
 """Retain birth identities, so a live runtime reparented after worker exit is still checked."""
 for row in owned_tree(host_pid):
  if row['role'] in ['run-worker','run-runtime']:known[(row['pid'],row['startTicks'])]=row['role']

def assert_runs_retired(host_pid, known):
 rows=scan()
 live_known=[dict(rows[pid],role=role) for (pid,birth),role in known.items()
             if pid in rows and rows[pid]['startTicks']==birth and rows[pid]['state']!='Z']
 descendants=owned_tree(host_pid,rows)
 live_new=[row for row in descendants if row['role'] in ['run-worker','run-runtime'] and row['state']!='Z']
 zombies=[pid for pid,birth in known if pid in rows and rows[pid]['startTicks']==birth and rows[pid]['state']=='Z']
 event('run-retirement-check',{'hostPid':host_pid,'knownRunBirths':[{'pid':p,'startTicks':b,'role':r} for (p,b),r in known.items()],
       'liveKnown':live_known,'liveNew':live_new,'exitedZombies':zombies,'otherDescendants':descendants})
 assert not live_known and not live_new,{'liveKnownRun':live_known,'newRunDescendants':live_new}
