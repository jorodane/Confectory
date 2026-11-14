"""Joint native compiler context uses only complete, original explicit source plans."""
import copy,json,hashlib
import v666_native_chain_fixture as x
f=x.f
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(x.original_result,'original-native-chain');x.unchanged();f.checked('original native import chain and shared Blueprint caller execute85 with exact source/permissions')
 if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published source planner rejects jointly authored input/native import changes without modifying original program')
 else:
  result=x.n.prepare(r);rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});assert all(v['hash']==hashlib.sha256(r['units'][v['id']]['draft'].encode()).hexdigest()for v in rows);reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse);assert {v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent original-hash candidate compiles the jointly selected contracts/imports and exact authored bodies')
  for fault in ['partial','stale-body','bad-call','wrong-native','missing-receipt','missing-caller','disagree','foreign-unit']:
   bad=copy.deepcopy(r);row=bad['changes'][0];body=next(iter(row['mapping']['bodies'].values()))
   if fault=='partial':bad['changes'].pop()
   elif fault=='stale-body':body['hash']='0'*64
   elif fault=='bad-call':body['text']='return calls.Second.Invoke(123,count);'
   elif fault=='wrong-native':body['signature']=copy.deepcopy(x.native)
   elif fault=='missing-receipt':bad['changes'][1]['mapping'].pop('dependencies')
   elif fault=='missing-caller':row['mapping']['callers'].clear()
   elif fault=='disagree':bad['changes'][1]['mapping']['bodies'][x.first+'Body/body:common']=copy.deepcopy(body)
   elif fault=='foreign-unit':bad['units'][x.external_helper]=dict(kind='function',path='foreign.celem',draft=x.external_function.read_text())
   x.n.prepare(bad,False);x.unchanged()
  f.checked('partial joint source, stale hashes, invalid new call/signature, missing proof/caller and extra source claims reject atomically')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
