"""New owned child creation/registration beside explicit native body plans."""
import copy,json,sys,pathlib,runpy
import importlib
x=importlib.import_module('v666_owned_extension_fixture'if'--existing-root'in sys.argv else'v666_owned_creation_fixture');sys.modules['v666_owned_creation_fixture']=x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));owned=[v for v in r['changes']if v['type']=='owned-definition'];native=[v for v in r['changes']if v['type']!='owned-definition']
  for changes in [owned,native]:
   one=copy.deepcopy(r);one['changes']=changes;x.n.prepare(one)
  f.checked('new owned child/registration and explicit native groups independently validate without touching original files or missing destinations')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published combined candidate rejects the new owned creation/native group with all originals and destinations unchanged');raise SystemExit(0)
  p=x.n.prepare(r);(f.case/'combined-candidate.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));assert len(p['additions'])==len(x.owned_paths) and not any(v['id']in x.owned_paths for v in p['updates'])and p['manifest']==x.expected_manifest;rows={v['id']:dict(draft=v['text'])for v in p['additions']+p['updates']+p['linkedUpdates']}|{x.owner:dict(draft=p['text'])};x.verify_rows(rows);x.unchanged();f.checked('full candidate explicitly creates the exact declared owned schemas and registration with native/caller sources preserved outside the selected body plans')
  prior=copy.deepcopy(r);prior['changes']=native;native_candidate=x.n.prepare(prior);assert{v['id']:v['text']for v in p['updates']+p['linkedUpdates']if v['id']not in getattr(x,'schema_paths',x.owned_paths)}=={v['id']:v['text']for v in native_candidate['updates']+native_candidate['linkedUpdates']};reversed_request=copy.deepcopy(r);reversed_request['changes'].reverse();q=x.n.prepare(reversed_request);x.verify_rows({v['id']:dict(draft=v['text'])for v in q['additions']+q['updates']+q['linkedUpdates']}|{x.owner:dict(draft=q['text'])});assert q['manifest']==p['manifest']and{v['id']:v['text']for v in q['additions']+q['updates']+q['linkedUpdates']}=={v['id']:v['text']for v in p['additions']+p['updates']+p['linkedUpdates']};f.checked('row order preserves the exact created IDs/paths/registration and all child/native/caller bytes; selected CSharp matches the independent explicit native candidate')
  for fault in ['extra-key','sources','contract','schema','schema-hash','existing-root','cardinality','bad-value','overflow','duplicate','duplicate-name','bad-icon','missing-body','stale-native','new-existing-mix','conversion']:
   bad=copy.deepcopy(r);row=next(v for v in bad['changes']if v['type']=='owned-definition');method=next(v for v in bad['changes']if v['type']=='function-edit')
   if fault=='extra-key':row['grant']=True
   elif fault=='sources':row['sources'][f.n+'Leaf2']='0'*64
   elif fault=='contract':row['contract']=dict(kind='compound',cardinality='single',type=f.n+'Leaf2')
   elif fault=='schema':row['schema']=f.n+'Foreign'
   elif fault=='schema-hash':row['schemaHash']='0'*64
   elif fault=='existing-root':row['name']='Tree'
   elif fault=='cardinality':row['cardinality']='multiple'
   elif fault=='bad-value':value=x.edited_value();value[x.power_key]=False;row['valueJson']=json.dumps(value)
   elif fault=='overflow':value=x.edited_value();value[x.power_key]=9223372036854775808;row['valueJson']=json.dumps(value)
   elif fault=='duplicate':row['tree']['fields'].append(copy.deepcopy(row['tree']['fields'][0]))
   elif fault=='duplicate-name':row['tree']['fields'][1]['name']=row['tree']['fields'][0]['name']
   elif fault=='bad-icon':row['tree']['fields'][0]['icon']='<script>'
   elif fault=='missing-body':method['mapping']['bodies'].clear()
   elif fault=='stale-native':next(iter(method['mapping']['bodies'].values()))['hash']='0'*64
   elif fault=='new-existing-mix':row.update(contract=dict(kind='compound',cardinality='single',type=f.n+'Leaf2'),schema=x.owner,schemaHash=__import__('hashlib').sha256(r['text'].encode()).hexdigest(),sources={f.n+'Leaf2':'0'*64})
   elif fault=='conversion':row['conversion']=dict(mode='reset-empty-v1',originalValueJson='{}',typeSources={})
   (f.case/'current-rejection.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False,indent=2));x.n.prepare(bad,False);x.unchanged()
  guards=f.metadata('informationBodyGroupGuards',action='prepare',project=r['project'],namespace=f.n[:-2],units=r['units'],declaration=dict(id=x.owner,hash=__import__('hashlib').sha256(r['text'].encode()).hexdigest(),changes=r['changes']));assert guards['required']and{v['path']for v in guards['checks']if v['hash']=='missing'}==set(x.owned_paths.values());assert any(v==owned[0]for v in guards['ownerEdits']);(f.case/'guard-prepare.json').write_text(json.dumps(guards,ensure_ascii=False,indent=2));f.checked('complete creation plan and exactly the declared missing destinations bind to the original native read scope; incomplete/borrowed/converted/stale/invalid requests reject as a whole')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
else:runpy.run_path(str(pathlib.Path(__file__).with_name('v666_owned_creation_'+check+'.py')),run_name='__main__')
