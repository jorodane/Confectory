"""Normalize only existing typed-value rows; preserve the full original validation."""
import copy,json,pathlib,runpy,sys
import v666_typed_values_contracts_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));values=x.value_changes();native=[row for row in r['changes']if row['type']in ['function-edit','description','icon']]
  for changes in [values,native]:
   one=copy.deepcopy(r);one['changes']=changes;x.n.prepare(one)
  x.unchanged();f.checked('six existing typed defaults and the explicit native ABI/body/caller group validate independently')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published candidate rejects only their combination and preserves owner, data, contracts and registered/external sources')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates}|{x.owner:{'draft':p['text']}});reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert p['text']==q['text']and {v['id']:v['text']for v in updates}=={v['id']:v['text']for v in q['updates']+q['linkedUpdates']};one=copy.deepcopy(r);one['changes']=native;prior=x.n.prepare(one);assert {v['id']:v['text']for v in updates}=={v['id']:v['text']for v in prior['updates']+prior['linkedUpdates']};x.unchanged();f.checked('typed-value normalization composes all original contracts and exact defaults without changing native/caller update bytes or row-order semantics')
   for name,path,value in [('Tree',['Tree','Count'],9223372036854775801),('ExternalTree',['ExternalTree','HP'],9223372036854775802),('Samples',['Samples',1],9223372036854775804)]:
    leaf=copy.deepcopy(r);row=next(row for row in leaf['changes']if row['type']=='data'and row['path']==[name]);row.update(path=path,contract=copy.deepcopy(x.scalar),valueJson=str(value));out=x.n.prepare(leaf);assert f.metadata('inspect',text=out['text'])['values']==f.metadata('inspect',text=p['text'])['values']
   reset=copy.deepcopy(r);row=next(row for row in reset['changes']if row['type']=='data'and row['path']==['Tree']);row.pop('valueJson');row['type']='unset';out=x.n.prepare(reset);assert 'editorFieldDefault_Tree'not in f.metadata('inspect',text=out['text'])['values'];f.checked('existing nested compound/list paths and explicit stored root reset retain the same validated owner-value semantics')
   scope=f.metadata('informationBodyGroupGuards',action='prepare',namespace=f.n[:-2],project=str(f.manifest),units=r['units'],declaration=dict(id=x.owner,changes=r['changes']));assert scope['required'];checks={row['path']for row in scope['checks']};assert ('registered/Leaf.celem'in checks if '--outside-values'not in sys.argv else str(x.external_definition)in {v['path']for v in scope['reads']})and all(any(path.endswith(name)for path in checks)for name in ['RefTarget2.celem','NativeAltBody.celem','ValueMode.celem']),checks;f.checked('the original read scope includes registered type and selected reference/provider/enum sources without adding them as write members')
   for fault in ['wrong-contract','unknown-field','bad-index','negative-index','reference-descent','unknown-member','implicit-parent','nested-unset','overlap','duplicate','extra-key','bad-value','wrong-reference','wrong-function','unknown-enum','oversized-value','overlong-path','stale-native','missing-body']:
    if '--family=body'in sys.argv and fault=='missing-body':continue
    bad=copy.deepcopy(r);row=next(row for row in bad['changes']if row['type']=='data'and row['path']==['Tree']);method=next(row for row in bad['changes']if row['type']=='function-edit')
    if fault=='wrong-contract':row['contract']['type']=f.n+'LeafChild'
    elif fault=='unknown-field':row['path']=['Missing']
    elif fault in ['bad-index','negative-index']:row.update(path=['Samples',2 if fault=='bad-index'else -1],contract=x.scalar,valueJson='7')
    elif fault=='reference-descent':row.update(path=['Peer','Count'],contract=x.scalar,valueJson='7')
    elif fault=='unknown-member':row.update(path=['Tree','Missing'],contract=x.scalar,valueJson='7')
    elif fault=='implicit-parent':row.update(path=['Tree','Count','More'],contract=x.scalar,valueJson='7')
    elif fault=='nested-unset':row.update(type='unset',path=['Tree','Count'],contract=x.scalar);row.pop('valueJson')
    elif fault=='overlap':bad['changes'].append(dict(type='data',path=['Tree','Count'],contract=x.scalar,valueJson='7'))
    elif fault=='duplicate':bad['changes'].append(copy.deepcopy(row))
    elif fault=='extra-key':row['sourceProof']={}
    elif fault=='bad-value':row['valueJson']='{"Count":"not a long"}'
    elif fault=='wrong-reference':next(v for v in bad['changes']if v['type']=='data'and v['path']==['Peer'])['valueJson']='{"$ref":"Outside.Pack::Target"}'
    elif fault=='wrong-function':next(v for v in bad['changes']if v['type']=='data'and v['path']==['Handler'])['valueJson']=json.dumps({'$ref':f.n+'RefTarget2'})
    elif fault=='unknown-enum':next(v for v in bad['changes']if v['type']=='data'and v['path']==['Mode'])['valueJson']='"missing"'
    elif fault=='oversized-value':row['valueJson']=' '*65537
    elif fault=='overlong-path':row.update(path=['Tree']+['Count']*64,contract=x.scalar,valueJson='7')
    elif fault=='stale-native':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
    elif fault=='missing-body':method['mapping']['bodies'].clear()
    (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
   f.checked('wrong/unknown typed paths, bounds, reference traversal, overlapping edits, incompatible/foreign targets and incomplete native plans reject atomically')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_typed_values_contracts_'+check+'.py')),run_name='__main__')
