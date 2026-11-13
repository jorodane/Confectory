"""Finite owner-local scalar grammar; the full declaration validator stays authoritative."""
import copy,json,pathlib,runpy,sys
import v666_scalar_owner_contracts_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));owner=x.owner_changes();native=[row for row in r['changes']if row['type']in ['function-edit','description','icon']]
  for changes in [owner,native]:
   one=copy.deepcopy(r);one['changes']=changes;x.n.prepare(one)
  x.unchanged();f.checked('scalar structure/default/presentation group and native ABI/body/caller group independently validate')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published candidate rejects only their combination; source bytes remain original')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates}|{x.owner:{'draft':p['text']}});q=copy.deepcopy(r);q['changes'].reverse();reverse=x.n.prepare(q);a=f.metadata('inspect',text=p['text']);b=f.metadata('inspect',text=reverse['text']);assert a['values']==b['values']and a['description']==b['description']and x.semantic_fields(a['fields'])==x.semantic_fields(b['fields']);assert {row['id']:row['text']for row in updates}=={row['id']:row['text']for row in reverse['updates']+reverse['linkedUpdates']};one=copy.deepcopy(r);one['changes']=native;prior=x.n.prepare(one);assert updates==prior['updates']+prior['linkedUpdates'];scope=f.metadata('informationBodyGroupGuards',action='prepare',namespace=f.n[:-2],project=str(f.manifest),units=r['units'],declaration=dict(id=x.owner,changes=r['changes']));assert scope['required']and any(row['path']==x.retained_file for row in scope['checks']);x.unchanged();f.checked('combined candidate is order-independent, exact64/default/ID preserving and has byte-identical native updates and complete original read guards')
   for kind in ['unset','info-definition']:
    alt=copy.deepcopy(r)
    if kind=='unset':alt['changes']=[row for row in alt['changes']if row['type']!='data'];alt['changes'].append(dict(type='unset',path=['Gauge'],contract=x.scalar));out=x.n.prepare(alt);assert 'editorFieldDefault_Gauge'not in f.metadata('inspect',text=out['text'])['values']
    else:next(row for row in alt['changes']if row['type']=='typed-definition')['type']=kind;x.n.prepare(alt)
   f.checked('existing explicit unset and legacy scalar definition formats also compose without inferred conversion')
   limit=copy.deepcopy(r)
   for number in range(64-len(limit['changes'])):
    field=copy.deepcopy(next(row for row in r['changes']if row['type']=='typed-definition'));field.update(name='Extra_'+str(number),displayName='추가 '+str(number),icon='★');limit['changes'].append(field)
   bounded=x.n.prepare(limit);assert len(f.metadata('inspect',text=bounded['text'])['fields'])==len(f.metadata('inspect',text=p['text'])['fields'])+54
   limit['changes'].append(dict(type='unset',path=['Power'],contract=x.scalar));x.n.prepare(limit,False);x.unchanged();f.checked('the existing 64-row declaration limit accepts distinct scalar additions with icons and rejects row65; native/source member budgets unchanged')
   for fault in ['stale','foreign','nested','wrong-contract','duplicate','overlap','remove-edited','unknown','extra-source','array','reference','compound','extra-key','duplicate-name','invalid-default','missing-body','stale-body','missing-caller','too-many']:
    if '--family=body'in sys.argv and fault in ['missing-body','missing-caller']:continue
    bad=copy.deepcopy(r);row=next(row for row in bad['changes']if row['type']=='schema-remove');created=next(row for row in bad['changes']if row['type']=='typed-definition');method=next(row for row in bad['changes']if row['type']=='function-edit')
    if fault=='stale':row['schemaHash']='0'*64
    elif fault=='foreign':row['schema']='Unowned.Pack::Other'
    elif fault=='nested':row['path']=['Tree','Count']
    elif fault=='wrong-contract':row['contract']['type']='string'
    elif fault=='duplicate':bad['changes'].append(copy.deepcopy(row))
    elif fault=='overlap':bad['changes'].append(dict(type='unset',path=['Gauge'],contract=x.scalar))
    elif fault=='remove-edited':row['path']=['Gauge']
    elif fault=='unknown':row['path']=['Unknown']
    elif fault=='extra-source':created['sources']={'inferred':'unregistered'}
    elif fault in ['array','reference','compound']:created['contract']['cardinality'if fault=='array'else'kind']='list'if fault=='array'else fault
    elif fault=='extra-key':row['unexpected']=True
    elif fault=='duplicate-name':created['name']='Gauge'
    elif fault=='invalid-default':created['valueJson']='"not a long"'
    elif fault=='missing-body':method['mapping']['bodies'].clear()
    elif fault=='stale-body':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
    elif fault=='missing-caller':method['mapping'].pop('callers',None);method['mapping']['args']['amount']=None
    elif fault=='too-many':bad['changes']+=copy.deepcopy([created]*55)
    (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
   f.checked('stale/foreign/nested/duplicate/overlap/unsupported/source-proof/default/budget and incomplete native plans reject atomically')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_scalar_owner_contracts_'+check+'.py')),run_name='__main__')
