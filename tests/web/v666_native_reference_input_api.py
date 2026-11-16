"""Nominal scopes, source CAS, cold restore and explicit Review/Confirm."""
import copy,json
import v666_native_reference_input_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();cats=x.catalogs();r=x.apply_request(cats)
 for fault in ['missing-scope','wrong-scope','missing-type','missing-dependencies','wrong-dependencies','value-proof','missing-caller','stale-body','bad-code','conflicting-shared','missing-selected-caller','wrong-selected-signature']:
  bad=copy.deepcopy(r);a,b=bad['declaration']['changes'];plans=a['mapping']['bodies']
  if fault=='missing-scope':a['nativeTypes'].pop('$function:'+x.first)
  elif fault=='wrong-scope':a['nativeTypes']['$function:'+x.first]=b['nativeTypes']['$function:'+x.second]
  elif fault=='missing-type':a['nativeTypes']={k:v for k,v in a['nativeTypes'].items()if k.startswith('$function:')}
  elif fault=='missing-dependencies':a['mapping'].pop('dependencies')
  elif fault=='wrong-dependencies':a['mapping']['dependencies']=copy.deepcopy(b['mapping']['dependencies'])
  elif fault=='value-proof':
   base=a['signature']['args'][0]['type'].removesuffix('[]');a['nativeTypes'][base]=copy.deepcopy(next(v['proof']for v in cats[x.first]['nativeTypes']if v['id']==f.n+'Leaf'))
  elif fault=='missing-caller':plans.pop(x.callers[x.first])
  elif fault=='stale-body':plans[x.bodies[x.first]]['hash']='0'*64
  elif fault=='bad-code':b['mapping']['bodies'][x.bodies[x.second]]['text']=x.sources[x.bodies[x.second]]
  elif fault=='missing-selected-caller':b['mapping']['bodies'].pop(x.bodies[x.first])
  elif fault=='wrong-selected-signature':b['mapping']['bodies'][x.bodies[x.first]]['signature']=copy.deepcopy(x.old)
  else:b['mapping']['bodies'][x.bodies[x.first]]['text']+='\n// different authored shared body\n'
  f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;x.unchanged()
 bad=copy.deepcopy(r);bad['declaration']['changes']=x.mixed(x.request(cats),cats)['changes'];f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;x.unchanged()
 f.checked('missing/crossed nominal function proofs, omitted caller, stale source, incompatible C# and conflicting shared source fail without applying any member')
 for kind in ['reference-return','jagged-array']:
  bad=copy.deepcopy(r);bad['declaration']['changes']=x.unsupported(x.request(cats),kind,cats)['changes'];f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;x.unchanged()
 bad=copy.deepcopy(r);proof=bad['declaration']['changes'][0]['nativeTypes'];base=bad['declaration']['changes'][0]['signature']['args'][0]['type'].removesuffix('[]');proof[base+'[]']=proof.pop(base);f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;x.unchanged()
 f.checked('reference returns/jagged inputs and array-keyed element proofs reject with every original and checkpoint intact')
 f.invoke('blueprint',r);ids=x.verify(checkpoint);f.checked('one Save captures both selected nominal scopes and every explicit native source and the selected callee/consumer in the existing group/receipt')
 f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids;f.checked('cold restore retains both nominal function scopes and body group')
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=f.invoke('blueprint',dict(action='readOwnerEdits',id=x.owner,hash=s['textHash']))['result']['result'];f.invoke('blueprint',dict(action='applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[dict(type='description',text='구조체 공동 저장 후 설명')])));assert x.verify(checkpoint)==ids;f.checked('follow-up owner metadata Save retains the captured native bodies and per-function type proofs')
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=f.invoke('blueprint',dict(action='readOwnerEdits',id=x.owner,hash=s['textHash']))['result']['result'];current=next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==x.first);import hashlib
 row=dict(type='function-edit',id=x.first,hash=hashlib.sha256(current['draft'].encode()).hexdigest(),name=x.labels[0],description='구조체 캡처 후 기능 설명',signature=r['declaration']['changes'][0]['signature']);f.invoke('blueprint',dict(action='applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=[row])));assert x.verify(checkpoint)==ids;f.checked('follow-up function metadata retains exact nominal ABI, complete body captures and both original native scopes')
 for number,path in enumerate([x.paths[x.callers[x.first]],x.paths[x.callers[x.second]],'Leaf.celem']):
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;saved=checkpoint.read_bytes();p=f.project/path;raw=p.read_bytes();p.write_bytes(raw+b'\n// peer after Review\n');out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed']is False and checkpoint.read_bytes()==saved and p.read_bytes()==raw+b'\n// peer after Review\n';p.write_bytes(raw);x.unchanged();f.checked('post-Review '+path+' conflict rejects complete final CAS and preserves checkpoint and peer text');f.stop();f.start(2+number);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids

 f.stop();f.start(5);f.invoke('select',dict(id=x.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed'],(out,f.state().get('logs'));x.verify_live()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
