"""Existing atomic acceptance suite with a real direct call at the use site."""
import json
import v536_information_call_inputs_fixture as c
x,f,n,owner,fn=c.x,c.f,c.n,c.owner,c.fn
if x.mode!='callee-conflict':
 import v536_information_input_replacements_api
else:
 try:
  f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes()
  f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(m for m in s['ownFunctions'] if m['id']==fn)
  preview=f.invoke('blueprint',{'action':'readOwnerEdits','id':owner,'hash':s['textHash'],'includeFunctionInputs':fn})['result']['result']
  change={'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(preview)}
  path=f.project/'InputLeaf.celem';path.write_text(path.read_text().replace('{','{description "다른 편집자의 callee 변경";',1));peer=path.read_bytes()
  f.invoke('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':preview['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[change]}},False)
  assert checkpoint.read_bytes()==saved and path.read_bytes()==peer
  assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items() if p!='InputLeaf.celem')
  f.checked('선택 후 실제 callee 선언 변경은 전체 미적용이며 peer·C#·기존 checkpoint 보존')
 finally:
  print(json.dumps({'checks':f.checks,'mode':x.mode,'evidence':str(f.case),'nativeWindows':False,'projectRun':False},ensure_ascii=False));f.stop()
