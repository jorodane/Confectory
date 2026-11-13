"""Explicit new compound definitions retain their original full validation."""
import copy,json,pathlib,runpy,sys
import v666_compound_creation_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));definitions=[v for v in r['changes']if v['type']=='typed-definition'];native=[v for v in r['changes']if v['type']!='typed-definition']
  for changes in [definitions,native]:
   one=copy.deepcopy(r);one['changes']=changes;x.n.prepare(one)
  x.unchanged();f.checked('new compound definition with explicit exact64 members and selected type proof, and original native ABI/body group, validate independently')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published source rejects only the combined new definition/native group without changing checkpoint, original fields or named type sources')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({v['id']:{'draft':v['text']}for v in updates}|{x.owner:{'draft':p['text']}});reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);x.verify_rows({v['id']:{'draft':v['text']}for v in q['updates']+q['linkedUpdates']}|{x.owner:{'draft':q['text']}});assert {v['id']:v['text']for v in updates}=={v['id']:v['text']for v in q['updates']+q['linkedUpdates']};one=copy.deepcopy(r);one['changes']=native;prior=x.n.prepare(one);assert{v['id']:v['text']for v in updates}=={v['id']:v['text']for v in prior['updates']+prior['linkedUpdates']};(f.case/'candidate-orders.json').write_text(json.dumps(dict(original=p,reversed=q),ensure_ascii=False,indent=2));x.unchanged();f.checked('new compound composition retains the same complete owner field/default/presentation semantics and identical native/caller bytes under reversed row order; new metadata insertion order follows the explicit plan')
   for fault in ['existing-id','duplicate-label','missing-proof','forged-proof','unknown-type','undeclared-type','bad-kind','bad-cardinality','duplicate','extra-key','incompatible-default','wrong-integer','oversized-value','stale-native','missing-body']:
    if '--family=body'in sys.argv and fault=='missing-body':continue
    bad=copy.deepcopy(r);row=next(v for v in bad['changes']if v['type']=='typed-definition');method=next(v for v in bad['changes']if v['type']=='function-edit')
    if fault=='existing-id':row['name']='Tree'
    elif fault=='duplicate-label':row['displayName']='Tree'
    elif fault=='missing-proof':row['sources']=None
    elif fault=='forged-proof':row['sources']={}
    elif fault=='unknown-type':row['contract']['type']=f.n+'Missing'
    elif fault=='undeclared-type':row['contract']['type']='Outside.Pack::Leaf'
    elif fault=='bad-kind':row['contract']['kind']='module'
    elif fault=='bad-cardinality':row['contract']['cardinality']='many'
    elif fault=='duplicate':bad['changes'].append(copy.deepcopy(row))
    elif fault=='extra-key':row['grant']=True
    elif fault=='incompatible-default':row['valueJson']='{"Count":false,"Note":"wrong"}'
    elif fault=='wrong-integer':row['valueJson']='{"Count":9223372036854775808,"Note":"overflow"}'
    elif fault=='oversized-value':row['valueJson']=json.dumps(dict(Count=1,Note='a'*65537))
    elif fault=='stale-native':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
    elif fault=='missing-body':method['mapping']['bodies'].clear()
    (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
   f.checked('duplicate identity/label, stale or foreign proof, invalid kinds/defaults/budgets and incomplete native plans reject atomically')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_compound_creation_'+check+'.py')),run_name='__main__')
