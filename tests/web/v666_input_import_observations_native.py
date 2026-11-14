"""Individually valid explicit input/callee edits retain original import receipts."""
import copy,json,hashlib
import v666_input_import_observations_fixture as x
f=x.f
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 for row in r['changes']:
  one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
 x.unchanged();x.execute(x.original_result,'original-input-imports');f.checked('each original type/body/caller plan validates independently; unchanged mixed owned/registered helper program executes79')
 if x.mode=='reproduce':
  x.n.prepare(r,False);x.unchanged();f.checked('published group rejects independently valid actual contract changes with existing import/registered receipts; no source or permission changed')
 else:
  result=x.n.prepare(r);updates=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in updates});assert all(v['hash']==hashlib.sha256(r['units'][v['id']]['draft'].encode()).hexdigest()for v in updates);reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse);assert{v['id']:v['text']for v in updates}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent original-hash candidate composes explicit string bodies, typed caller imports/bindings and unchanged readonly dependencies')
  for fault in ['missing-proof','missing-contract','caller-proof','receipt-schema','stale-body','bad-last-body','missing-caller','disconnect','literal','foreign-unit','changed-import']:
   bad=copy.deepcopy(r);row=bad['changes'][1];mapping=row['mapping'];plan=next(iter(mapping['bodies'].values()));proof=next(iter(mapping['dependencies'].values()));caller=next(iter(mapping['callers'].values()))
   if fault=='missing-proof':mapping.pop('dependencies')
   elif fault=='missing-contract':proof['contracts'].pop(x.external_helper)
   elif fault=='caller-proof':proof['callerHash']='0'*64
   elif fault=='receipt-schema':proof['schema']=2
   elif fault=='stale-body':plan['hash']='0'*64
   elif fault=='bad-last-body':plan['text']='return MissingImportedValue;'
   elif fault=='missing-caller':mapping['callers'].clear()
   elif fault=='disconnect':caller['disconnect'].clear()
   elif fault=='literal':caller['inputs']['amount']={'valueJson':'123'}
   elif fault=='foreign-unit':bad['units'][x.external_helper]=dict(kind='function',draft=x.external_function.read_text(),path='foreign.celem')
   elif fault=='changed-import':bad['units'][x.functions[1]+'Body']['draft']=bad['units'][x.functions[1]+'Body']['draft'].replace('StableHelper (long)','StableHelper (string)')
   x.n.prepare(bad,False);x.unchanged()
  f.checked('missing/stale receipt, body, caller/disconnect/value, foreign owned-unit claim and changed typed import reject the complete candidate')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
