"""Real checkpoint atomicity: explicit source then ordinary storage names, no public ABI change."""
import copy,json,uuid,sys
import v666_alias_source_fixture as t
f=t.f;x=t.x;checks=[];smoke=len(sys.argv)>3 and sys.argv[3]=='smoke'
def check(text):checks.append(text);print('PASS '+text,flush=True)
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=t.checkpoint();before=checkpoint.read_bytes();data=t.read();alias=dict(id='stable_alias',name=t.name,type='int',sourceJson=json.dumps(dict(node=t.node,output='return')));plan=dict(aliases=[alias],bindings=[dict(kind='exit',name='return',valueJson='{"local":"stable_alias"}')]);edits=[dict(action='source',node=t.node,text=t.text),dict(action='aliasPlan',node='$locals',definition=plan)];basis=dict(action='authorBatch',id=t.graph,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=edits)
 def request(q,ok=True):return f.invoke('blueprint',dict(attempt=uuid.uuid4().hex,**q),ok)['result']
 bad=[]
 q=copy.deepcopy(basis);q['edits'].reverse();bad.append(q)
 q=copy.deepcopy(basis);q['edits'].append(dict(action='source',node=t.node,text=t.late));bad.append(q)
 q=copy.deepcopy(basis);q['edits'][0]['node']='foreign';bad.append(q)
 q=copy.deepcopy(basis);q['edits'][0]['frame']=t.graph;bad.append(q)
 q=copy.deepcopy(basis);q['owner']='foreign';bad.append(q)
 q=copy.deepcopy(basis);q['sourceProof']='[]';bad.append(q)
 q=copy.deepcopy(basis);q['checkpointHash']='missing';bad.append(q)
 for change in [dict(name=''),dict(type='long'),dict(sourceJson='{"node":"foreign","output":"return"}'),dict(sourceJson='{"constant":9}')]:
  q=copy.deepcopy(basis);q['edits'][1]['definition']['aliases'][0].update(change);bad.append(q)
 for q in ([bad[0],bad[-1]]if smoke else bad):
  request(q,False);assert checkpoint.read_bytes()==before and t.current()['source']==t.original_source and not t.aliases();x.original()
 check(('representative order/storage rejection'if smoke else'reversed/multiple/foreign/frame/owner/stale and alias type/name/storage rejection')+' preserves entire checkpoint and physical originals')
 source=f.project/t.source_file;raw=source.read_bytes()
 if not smoke:
  checkpoint.chmod(0o400)
  failed=dict(attempt=uuid.uuid4().hex,**basis)
  try:f.invoke('blueprint',failed,False);assert checkpoint.read_bytes()==before and t.current()['source']==t.original_source and not t.aliases();x.original()
  finally:checkpoint.chmod(0o600)
  query={**failed,'action':'settledAuthorBatch'};assert f.invoke('blueprint',query)['result']['result']['baselineUnchanged']
  source=f.project/t.source_file;raw=source.read_bytes();source.write_bytes(raw+b' ')
  try:reply=f.invoke('blueprint',query)['result']['result'];assert not reply['settled']and not reply['baselineUnchanged']and checkpoint.read_bytes()==before and source.read_bytes()==raw+b' '
  finally:source.write_bytes(raw)
  check('real checkpoint write denial preserves both draft fields; only original physical sources permit a corrected unapplied attempt')
 attempt=uuid.uuid4().hex;q=dict(attempt=attempt,**basis)
 if not smoke:
  source.write_bytes(raw+b' ')
  try:assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and source.read_bytes()==raw+b' 'and all(path.read_bytes()==value for path,value in x.physical.items()if path!=source)
  finally:source.write_bytes(raw)
  check('initial draft Save preserves external physical changes for the existing final Confirm CAS; it never publishes source files')
 else:assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];check('generated/restored runtime atomically stages one explicit body and alias/consumer plan')
 accepted=checkpoint.read_bytes();actual=t.read();assert t.current()['source']==t.text and actual['locals'][0]['name']==t.name and json.loads(actual['locals'][0]['sourceJson'])==dict(node=t.node,output='return')and json.loads(actual['exits'][0]['valueJson'])==dict(local='stable_alias');x.original();assert f.invoke('blueprint',q)['result']['result']['checkpointSaved']and checkpoint.read_bytes()==accepted
 settled={**q,'action':'settledAuthorBatch'};assert f.invoke('blueprint',settled)['result']['result']['settled'];tampered=copy.deepcopy(q);tampered['edits'][1]['definition']['aliases'][0]['name']='tampered';f.invoke('blueprint',tampered,False);assert checkpoint.read_bytes()==accepted;x.original();check('one owned source and alias/consumer checkpoint atomically, keep public IDs/contracts/originals, and exact receipt replay settles without rewriting; tampering rejects')
 one=dict(action='authorBatch',id=t.graph,checkpointHash=actual['checkpointHash'],sourceProof=x.proof(actual),edits=[dict(action='aliasPlan',node='$locals',definition=dict(aliases=[{**alias,'name':'기존 별칭 단독 변경'}],bindings=[]))]);assert request(one)['result']['checkpointSaved']and t.current()['source']==t.text and t.aliases()[0]['id']=='stable_alias';x.original();check('existing alias-only save remains supported and preserves the source and same storage ID')
finally:
 (f.case/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('ALIAS_SOURCE_API',f.case,flush=True)
