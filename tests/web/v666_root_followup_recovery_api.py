"""A durable ordinary receipt retains its already validated root-group closure."""
import copy,json,uuid
import v666_root_followup_recovery_fixture as t
x=t.x;f=x.f
def request(edits):
 data=t.read();return dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=edits)
def root_group():
 q=request([dict(action='rootParameters',node='$root',definition=t.root_plan())]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];d,g=t.complete_group();assert not any(u['draft']!=u['original']for u in d['changes']);return q
def source(text):return request([dict(action='source',node='body',text=text)])
def rejected_restart(index,mutate):
 p=t.checkpoint();original=p.read_bytes();d=json.loads(original);mutate(d);p.write_text(json.dumps(d,ensure_ascii=False));held=p.read_bytes();f.stop();rejected=False
 try:
  try:f.start(index)
  except AssertionError:rejected=True
  assert rejected,'invalid root checkpoint must not become an editable scope';assert p.read_bytes()==held;x.original()
 finally:f.stop();p.write_bytes(original);f.start(index+1)
 t.complete_group();x.original()
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});root_group();raw=t.checkpoint().read_bytes();q=source(t.text);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];d,g=t.complete_group();assert g['authorSaveReceipt']['ownedSource']is True;assert sum(u['draft']!=u['original']for u in d['changes'])==1;assert t.current()==t.text;x.original();saved=t.checkpoint().read_bytes();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and t.checkpoint().read_bytes()==saved;f.stop();f.start(1);assert t.current()==t.text;assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];t.complete_group();x.original();f.checked('root no-op then ordinary source Save/cold settles one durable receipt with a complete existing root group; physical sources unchanged')
 q=source(t.original_source);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];d,g=t.complete_group();assert not any(u['kind']!='blueprint-node'and u['draft']!=u['original']for u in d['changes']);assert t.current()==t.original_source;assert g['authorSaveReceipt']['ownedSource']is True;f.stop();f.start(2);assert t.current()==t.original_source;assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];x.original();f.checked('explicitly restoring original body retains zero-dirty root members and source receipt across restart; node JSON formatting may be normalized')
 q=source(t.original_source);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];t.complete_group();raw=t.checkpoint().read_bytes();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and raw==t.checkpoint().read_bytes();f.stop();f.start(3);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];t.complete_group();x.original();f.checked('unchanged ordinary source value after root Save is idempotent and recoverable with a complete root group')
 def remove(d):d['changes']=[u for u in d['changes']if u['id']!=t.feature]
 rejected_restart(4,remove);f.checked('missing saved root member remains rejected; serializer retention never silently reconstructs a group')
 def group(d):next(u for u in d['changes']if u['id']==t.feature)['rootContractGroup'].reverse()
 rejected_restart(6,group);f.checked('mismatched explicit root group remains rejected')
 def path(d):next(u for u in d['changes']if u['id']==t.feature)['path']='../outside.celem'
 rejected_restart(8,path);f.checked('saved root member path cannot grant outside-source access')
 def namespace(d):next(u for u in d['changes']if u['id']==t.feature)['id']='Foreign.Elements::Pair'
 rejected_restart(10,namespace);f.checked('saved root member namespace cannot grant external ownership')
 p=t.checkpoint();original=p.read_bytes();d=json.loads(original);g=next(u for u in d['changes']if u['id']==t.graph);g['authorSaveReceipt']['sources'][t.graph]['hash']='0'*64;p.write_text(json.dumps(d));f.stop();f.start(12);assert not f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];x.original();f.stop();p.write_bytes(original);f.start(13);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];t.complete_group();x.original();f.checked('tampered receipt still cannot acknowledge a source Save; verified original checkpoint restarts without migration')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ROOT_FOLLOWUP_RECOVERY_API_FIXTURE',f.case,flush=True)
