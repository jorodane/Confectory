"""Original return/out ABI, shared consumer choices and joint native compiler guards."""
import copy,json,hashlib
import v666_native_return_chain_fixture as x
f=x.f
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(x.original_result,'original-return-chain');x.unchanged();f.checked('original imported native returns long42/40 and out35/34; unchanged shared caller executes52')
 if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published planner rejects jointly authored return/import contracts, preserving every original')
 else:
  single=copy.deepcopy(r);single['changes']=single['changes'][:1];one=x.n.prepare(single);assert not any(v['id']in[x.second,x.second+'Body',x.second+'Body/body:common']for v in one['updates']+one['linkedUpdates']);x.unchanged();f.checked('an explicitly authored valid single return edit retains the unchanged imported callee and its original return contract')
  result=x.n.prepare(r);rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});assert all(v['hash']==hashlib.sha256(r['units'][v['id']]['draft'].encode()).hexdigest()for v in rows);reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse);assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent original-hash candidate compiles both authored return contracts/imports and explicit compatible out consumers')
  for fault in ['missing-second-body','stale-body','bad-call','wrong-native','missing-caller','outputs','out-identity','new-input','disagree','role']:
   bad=copy.deepcopy(r);row=bad['changes'][0];body=next(iter(row['mapping']['bodies'].values()));caller=next(iter(row['mapping']['callers'].values()))
   if fault=='missing-second-body':bad['changes'][1]['mapping']['bodies'].clear()
   elif fault=='stale-body':body['hash']='0'*64
   elif fault=='bad-call':body['text']='long observed;long value=calls.Second.Invoke(amount,real,out observed);count=observed;return value;'
   elif fault=='wrong-native':body['signature']=copy.deepcopy(x.native)
   elif fault=='missing-caller':row['mapping']['callers'].clear()
   elif fault=='outputs':caller['outputs']['return']='return'
   elif fault=='out-identity':caller['outputs']['count']=None
   elif fault=='new-input':caller['inputs']['amount']={'valueJson':'123'}
   elif fault=='disagree':bad['changes'][1]['mapping']['bodies'][x.first+'Body/body:common']=copy.deepcopy(body)
   elif fault=='role':row['signature']['args'][0]['mode']='ref'
   x.n.prepare(bad,False);x.unchanged()
  f.checked('missing/stale selected source, invalid return call/native declaration, missing or implicit consumer choices, changed inputs/out identities and mixed roles reject atomically')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
