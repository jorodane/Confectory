"""Existing direct field contracts use the full original definition/source validator."""
import copy,json,pathlib,runpy,sys
import v666_field_contracts_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));fields=[row for row in r['changes']if row['type']in ['schema-field','data']];native=[row for row in r['changes']if row['type']not in ['schema-field','data']]
  for changes in [fields,native]:
   one=copy.deepcopy(r);one['changes']=changes;x.n.prepare(one)
  x.unchanged();f.checked('existing compound/reference field selections with exact catalogue proofs and the explicit native ABI/body group validate independently')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published source rejects only the combined field/native group without applying any candidate or altering original named definitions')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates}|{x.owner:{'draft':p['text']}});reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert p['text']==q['text']and {v['id']:v['text']for v in updates}=={v['id']:v['text']for v in q['updates']+q['linkedUpdates']};one=copy.deepcopy(r);one['changes']=native;prior=x.n.prepare(one);assert {v['id']:v['text']for v in updates}=={v['id']:v['text']for v in prior['updates']+prior['linkedUpdates']};x.unchanged();f.checked('field contract composition retains exact field IDs/defaults and native/caller bytes under reversed row order without touching original type sources')
   for fault in ['stale-owner','wrong-schema','wrong-contract','missing-proof','forged-proof','unknown-type','undeclared-type','bad-kind','bad-cardinality','nested-definition','duplicate','extra-key','incompatible-default','stale-native','missing-body']:
    if '--family=body'in sys.argv and fault=='missing-body':continue
    bad=copy.deepcopy(r);row=next(v for v in bad['changes']if v['type']=='schema-field');method=next(v for v in bad['changes']if v['type']=='function-edit')
    if fault=='stale-owner':row['schemaHash']='0'*64
    elif fault=='wrong-schema':row['schema']=f.n+'Leaf'
    elif fault=='wrong-contract':row['contract']['type']=f.n+'LeafChild'
    elif fault=='missing-proof':row['sources']=None
    elif fault=='forged-proof':row['sources']={}
    elif fault=='unknown-type':row['definition']['type']=f.n+'Missing'
    elif fault=='undeclared-type':row['definition']['type']='Outside.Pack::Leaf'
    elif fault=='bad-kind':row['definition']['kind']='module'
    elif fault=='bad-cardinality':row['definition']['cardinality']='many'
    elif fault=='nested-definition':row['path']=['Tree','Count']
    elif fault=='duplicate':bad['changes'].append(copy.deepcopy(row))
    elif fault=='extra-key':row['grant']=True
    elif fault=='incompatible-default':row['definition']=dict(kind='general',cardinality='single',type='long');row['sources']=None
    elif fault=='stale-native':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
    elif fault=='missing-body':method['mapping']['bodies'].clear()
    (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
   f.checked('stale or foreign definitions/proofs, incompatible defaults, unknown or nested contracts and incomplete native plans reject atomically')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_field_contracts_'+check+'.py')),run_name='__main__')
