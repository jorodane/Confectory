"""Focused diagnostic for owned structure/native plan composition."""
import copy,json,sys,pathlib,runpy
import v666_owned_structure_fixture as x
f=x.f
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));owned=[v for v in r['changes']if v['type']=='owned-definition'];native=[v for v in r['changes']if v['type']!='owned-definition']
  for changes in [owned,native]:
   one=copy.deepcopy(r);one['changes']=changes;x.n.prepare(one)
  f.checked('existing owned structure and explicit native ABI/body/caller plans validate independently without writing originals')
  if x.mode=='reproduce':
   x.n.prepare(r,False);x.unchanged();f.checked('published combined candidate rejects raw body/graph registry overlays while preserving every original');raise SystemExit(0)
  p=x.n.prepare(r);(f.case/'combined-candidate.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));x.verify_rows({v['id']:dict(draft=v['text'])for v in p['updates']+p['linkedUpdates']}|{x.owner:dict(draft=p['text'])});x.unchanged();f.checked('combined pure candidate validates both existing child updates with no creations, registration change or inferred CSharp')
  assert not p['additions']and p['manifest']==r['manifest'];native_request=copy.deepcopy(r);native_request['changes']=native;prior=x.n.prepare(native_request);updates=p['updates']+p['linkedUpdates'];assert{v['id']:v['text']for v in updates if v['id']not in x.owned_paths}=={v['id']:v['text']for v in prior['updates']+prior['linkedUpdates']};reversed_request=copy.deepcopy(r);reversed_request['changes'].reverse();q=x.n.prepare(reversed_request);x.verify_rows({v['id']:dict(draft=v['text'])for v in q['updates']+q['linkedUpdates']}|{x.owner:dict(draft=q['text'])});assert{v['id']:v['text']for v in updates}=={v['id']:v['text']for v in q['updates']+q['linkedUpdates']};f.checked('explicit owned row order preserves the complete owner meaning and byte-identical child/native/caller updates; no new file or registration is produced')
  for fault in ['wrong-schema','wrong-schema-hash','wrong-contract','missing-source','stale-source','extra-source','ordinary-named','bad-cardinality','bad-default','overflow','bad-icon','duplicate','extra-key','new-root','conversion','whole-plan','stale-native','missing-body']:
   if '--family=body'in sys.argv and fault=='missing-body':continue
   bad=copy.deepcopy(r);row=next(v for v in bad['changes']if v['type']=='owned-definition');method=next(v for v in bad['changes']if v['type']=='function-edit')
   if fault=='wrong-schema':row['schema']=f.n+'Leaf2'
   elif fault=='wrong-schema-hash':row['schemaHash']='0'*64
   elif fault=='wrong-contract':row['contract']['type']=f.n+'Leaf2'
   elif fault=='missing-source':row['sources'].pop(next(iter(row['sources'])))
   elif fault=='stale-source':row['sources'][next(iter(row['sources']))]='0'*64
   elif fault=='extra-source':row['sources'][f.n+'Leaf2']=__import__('hashlib').sha256(x.definition_original).hexdigest()
   elif fault=='ordinary-named':row['name']='Tree';row['contract']={k:x.original_model['fields']['Tree'][k]for k in ['kind','cardinality','type']}
   elif fault=='bad-cardinality':row['cardinality']='multiple'
   elif fault=='bad-default':row['valueJson']='{"Power":false}'
   elif fault=='overflow':value=x.edited_value();value['Power']=9223372036854775808;row['valueJson']=json.dumps(value)
   elif fault=='bad-icon':row['tree']['fields'][0]['icon']='<script>'
   elif fault=='duplicate':bad['changes'].append(copy.deepcopy(row))
   elif fault=='extra-key':row['grant']=True
   elif fault=='new-root':row.update(name='NewOwned',contract=None,schema=None,schemaHash=None,sources={})
   elif fault=='conversion':row['conversion']=dict(mode='reset-empty-v1',originalValueJson='{}',typeSources={})
   elif fault=='whole-plan':next(iter(method['mapping']['bodies'].values()))['whole']={}
   elif fault=='stale-native':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
   elif fault=='missing-body':method['mapping']['bodies'].clear()
   (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
  f.checked('original owner/child proof, exact values, budget/identity and complete native plans remain mandatory; new source creation, ordinary named edits and other body plans reject without applying input')
  # This formerly rejected operation is the now-supported second creation flow.
  child_request=copy.deepcopy(r);row=next(v for v in child_request['changes']if v['type']=='owned-definition');row['tree']['fields'].append(dict(key='NewOwnedChild',name='새 자식',icon='',definition=dict(kind='owned',cardinality='single'),sources=None,children=dict(fields=[])));value=x.edited_value();value['NewOwnedChild']={};row['valueJson']=json.dumps(value);created=x.n.prepare(child_request);assert len(created['additions'])==1;child=created['additions'][0];assert child['kind']=='schema'and not(f.project/child['path']).exists();assert f.metadata('ownedDefinitionOwnership',owner=x.owner,ownerText=created['text'],id=child['id'],text=child['text'],path=child['path'])['owned']is True;default=json.loads(f.metadata('inspect',text=created['text'])['values']['editorFieldDefault_'+x.root_key]);assert default.pop('NewOwnedChild')=={}and default==x.edited_value();assert{v['id']:v['text']for v in created['updates']+created['linkedUpdates']if v['id']not in x.owned_paths}=={v['id']:v['text']for v in updates if v['id']not in x.owned_paths};x.unchanged();f.checked('explicit new owned child now validates as one exact marked source/registration addition; original values, source proofs and identical native/caller edits remain intact')
  guards=f.metadata('informationBodyGroupGuards',action='prepare',project=r['project'],namespace=f.n[:-2],units=r['units'],declaration=dict(id=x.owner,hash=__import__('hashlib').sha256(r['text'].encode()).hexdigest(),changes=r['changes']));(f.case/'guard-prepare.json').write_text(json.dumps(guards,ensure_ascii=False,indent=2));assert '--observe-guards'in sys.argv or guards.get('required')is True,guards;print(json.dumps(dict(guardRequired=guards.get('required'),checks=len(guards.get('checks',[])),ownerEdits=guards.get('ownerEdits'),evidence=str(f.case)),ensure_ascii=False),flush=True)
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_owned_structure_'+check+'.py')),run_name='__main__')
