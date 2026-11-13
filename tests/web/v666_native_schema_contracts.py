"""Original one-Save property/contract closure; no automatic CSharp rewriting."""
import copy,json,pathlib,runpy,sys,hashlib
import v666_native_schema_contracts_fixture as x
f=x.f;check=next((arg.removeprefix('--check=')for arg in sys.argv if arg.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));schema=[row for row in r['changes']if row['type']=='schema-field'];native=[row for row in r['changes']if row['type']!='schema-field']
  for changes in [schema,native]:
   single=copy.deepcopy(r);single['changes']=changes;x.n.prepare(single)
  x.unchanged();f.checked('existing scalar field type edit and the native ABI/body/caller plus owner presentation group each validate independently')
  if x.mode=='reproduce':
   x.n.prepare(r,False);x.unchanged();f.checked('published one-Save candidate rejects only their combination and preserves every original field/default/body/caller byte')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates}|{x.owner:{'draft':p['text']}});reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert p['text']==q['text']and{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};x.unchanged();f.checked('one original-hash candidate composes the explicit scalar field and native ABI/body/caller edits independent of row order')
   without=copy.deepcopy(r);without['changes']=native;body_only=x.n.prepare(without);assert{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in body_only['updates']+body_only['linkedUpdates']};f.checked('adding the field edit changes only its owned schema; explicit native source/caller updates are byte-identical to the existing supported group')
   scope=f.metadata('informationBodyGroupGuards',action='prepare',namespace=f.n[:-2],project=str(f.manifest),units=r['units'],declaration=dict(id=x.owner,changes=r['changes']));assert scope['required']and any(row['path']==x.retained_file for row in scope['checks']);f.checked('both same-contract and ABI-changing native classifiers bind the complete original read scope when the scalar field row is present')
   legacy=copy.deepcopy(r);field=next(row for row in legacy['changes']if row['type']=='schema-field');field.pop('definition');field.pop('sources');field['nativeType']=x.field_type;old=x.n.prepare(legacy);assert{k:v for k,v in old.items()if k!='observations'}=={k:v for k,v in p.items()if k!='observations'};current_reads={v['path']:v['hash']for v in p['observations']};legacy_reads={v['path']:v['hash']for v in old['observations']};assert legacy_reads.items()<=current_reads.items();extra_reads={path:value for path,value in current_reads.items()if path not in legacy_reads};catalogue=str(f.project/'registered/Leaf.celem');assert extra_reads=={catalogue:hashlib.sha256(pathlib.Path(catalogue).read_bytes()).hexdigest()};f.checked('legacy/nativeType and current UI scalar forms produce byte-identical write candidates; the current type catalogue retains its additional existing registered Leaf read')
   for fault in ['stale-field','foreign-schema','wrong-field-contract','unknown-field','nested-field','duplicate-field','extra-source','reference-kind','array-kind','unknown-native-type','incompatible-default','field-creation','field-deletion','missing-body','stale-body','missing-caller']:
    # An unchanged contract may legitimately omit a body edit and keep that
    # original source; incomplete ABI replacement is the rejection being tested.
    if '--family=body'in sys.argv and fault in ['missing-body','missing-caller']:continue
    bad=copy.deepcopy(r);field=next(row for row in bad['changes']if row['type']=='schema-field');method=next(row for row in bad['changes']if row['type']=='function-edit')
    if fault=='stale-field':field['schemaHash']='0'*64
    elif fault=='foreign-schema':field['schema']='Other.Pack::Unowned'
    elif fault=='wrong-field-contract':field['contract']['type']='int'
    elif fault=='unknown-field':field['path']=['Missing']
    elif fault=='nested-field':field['path']=['Tree','Count']
    elif fault=='duplicate-field':bad['changes'].append(copy.deepcopy(field))
    elif fault=='extra-source':field['sources']={'inferred':'not an existing scalar proof'}
    elif fault=='reference-kind':field['contract']['kind']='reference'
    elif fault=='array-kind':field['contract']['cardinality']='list'
    elif fault=='unknown-native-type':field['definition']['type']='object'
    elif fault=='incompatible-default':field['definition']['type']='string'
    elif fault=='field-creation':field.update(type='info-definition',name='Inferred')
    elif fault=='field-deletion':field['type']='schema-remove'
    elif fault=='missing-body':method['mapping']['bodies'].clear()
    elif fault=='stale-body':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
    elif fault=='missing-caller':method['mapping'].pop('callers',None);method['mapping']['args']['amount']=None
    (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
   f.checked('stale/foreign/nested/duplicate/unsupported property plans, incompatible defaults and incomplete native plans reject the whole candidate without rewriting defaults or source')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_schema_contracts_'+check+'.py')),run_name='__main__')
