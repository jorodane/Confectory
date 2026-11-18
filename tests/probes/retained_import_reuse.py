"""Exercise sealed evidence and routing guards without rerunning source tests."""
from pathlib import Path
import copy,json,subprocess,sys,zipfile
repo,record,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(repo/'tools'))
from verification_retained_import_reuse import validate,bind,same_invocation,SOURCE
out.mkdir(parents=True,exist_ok=True);prior=json.loads(record.read_text());commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
with zipfile.ZipFile(prior['evidence'])as z:inputs=json.loads(z.read('source.json'))['dependencyInputs']
_,rows,_=validate(repo,record,commit,inputs);assert len(rows)==22 and sum(n.startswith('lf-')for n in rows)==15 and all(n.startswith(('lf-','crlf-'))for n in rows);assert not any(n.endswith(('clone','checkout','restore','release','mcp','engine','package'))for n in rows)
def rejects(action,message):
 try:action()
 except RuntimeError as e:assert str(e)==message,(str(e),message)
 else:raise AssertionError(message)
bad=copy.deepcopy(inputs);bad['sdk']['sha256']='0'*64;rejects(lambda:validate(repo,record,commit,bad),'Recovery dependency identity changed')
rejects(lambda:validate(repo,record,'c460ce29a7a2e63dc72eaf71c6105a1b382f12ad',inputs),'Recovery source ancestry changed')
for fault in ['missing-result','unsealed-archive']:
 data=copy.deepcopy(prior)
 if fault=='missing-result':data['results'].pop(0);message='All 34 source/build stages and completed package command required'
 else:
  invalid=out/'invalid.zip';invalid.write_bytes(b'not sealed evidence');data['evidence']=str(invalid);message='Sealed output-pipe interruption evidence required'
 p=out/(fault+'.json');p.write_text(json.dumps(data));p.with_suffix('.manifest.json').write_bytes(record.with_suffix('.manifest.json').read_bytes());rejects(lambda:validate(repo,p,commit,inputs),message)
class Work:
 def __init__(self):
  self.root=out/'owned';self.evidence=out/'proof';self.evidence.mkdir();self.state={};self.fresh=[]
 def save(self):(out/'observed-state.json').write_text(json.dumps(self.state))
 def run(self,name,command,*args,**kw):self.fresh.append(name);return dict(fresh=name)
w=Work();bind(repo,record,commit,inputs,w)
for name,row in rows.items():
 command=[str(v).replace(prior['root'],str(w.root))for v in row['command']];assert w.run(name,command)==row
assert len(w.state['reusedChecks'])==22 and not w.fresh
name=next(iter(rows));command=[str(v).replace(prior['root'],str(w.root))for v in rows[name]['command']]
rejects(lambda:w.run(name,command+['--changed-input']),'Reused invocation differs');rejects(lambda:w.run(name,command),'Reused invocation repeats');assert len(w.state['reusedChecks'])==22
assert w.run('fresh-build',[])==dict(fresh='fresh-build')and w.fresh==['fresh-build']
proof=dict(identicalPassingFacts=22,source=SOURCE,recoverySource=commit,changedSdkRejected=True,changedSourceRejected=True,missingResultRejected=True,unsealedArchiveRejected=True,changedCommandRejected=True,repeatedFactRejected=True,buildsPackagesRestoreDelegatedFresh=True,actualSourceTestsRerun=False)
(out/'reuse-guard-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
