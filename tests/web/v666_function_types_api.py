"""Native chooser read proofs survive candidate and final CAS without new grants."""
import copy,json,subprocess
import v666_function_types_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();c=x.catalog();choices={r['id']:r for r in c['nativeTypes']};assert choices[x.f.n+'Payload']['available']and choices[x.f.n+'NativeRules']['available']and choices['External.Fields::Leaf']['available'];assert choices[x.owner]['available']and choices[x.owner]['profile']=='information-struct-references-v1'and not choices[x.f.n+'LegacyMood']['available'];assert not any(r['id'].startswith('Hidden.Types::')for r in c['nativeTypes']);x.unchanged();f.checked('catalogue exposes supported struct/enum/interface and declared external types, disables unsupported definitions and excludes registered-only namespaces without selecting providers')
 req=x.request(c);row=req['declaration']['changes'][0];fn=row['id'];path=f.project/'Leaf.celem';raw=path.read_bytes();path.write_bytes(raw+b'\n// peer source edit\n');f.invoke('blueprint',req,False);assert checkpoint.read_bytes()==before;x.unchanged({'Leaf.celem'});path.write_bytes(raw)
 for mutate in ['absent','missing','tamper','extra']:
  bad=copy.deepcopy(req);proof=bad['declaration']['changes'][0]['nativeTypes']
  if mutate=='absent':bad['declaration']['changes'][0].pop('nativeTypes')
  elif mutate=='missing':proof.pop(next(iter(proof)))
  elif mutate=='tamper':next(iter(proof.values()))['sources'][f.n+'Leaf']['source']='0'*64
  else:proof['object']={}
  f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;x.unchanged()
 f.checked('deep definition changes and missing/tampered/extra selected type proofs reject the entire new declaration and retain the original checkpoint')
 reply=f.invoke('blueprint',req)['result']['result'];assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(checkpoint,fn,row['signature']);x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint,fn,row['signature'])==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;saved=checkpoint.read_bytes();path.write_bytes(raw+b'\n// peer source edit\n');out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed']is False;assert checkpoint.read_bytes()==saved;path.write_bytes(raw);x.unchanged();f.checked('typed function/owner/registration save atomically and cold-restore; a deep type change after Review blocks final CAS')
 # Cold validation must reject missing/tampered retained read proof as well.
 units={row['id']:row for row in json.loads(checkpoint.read_text())['changes']}
 for field in ['nativeTypeProofs','nativeTypeReads']:
  broken=copy.deepcopy(units);broken[x.owner]['slotSaveReceipt'].pop(field)
  out=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationTypeGuards',action='validate',project=str(f.manifest),namespace='Owned.Elements',units=broken,selected=ids)),env=f.env,text=True,capture_output=True,check=True);assert not json.loads(out.stdout)['ok'];assert checkpoint.read_bytes()==saved
 f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';foreign=x.external/'Leaf.celem';foreign_raw=foreign.read_bytes();foreign.write_bytes(foreign_raw+b'\n// peer source edit\n');out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed']is False and checkpoint.read_bytes()==saved;foreign.write_bytes(foreign_raw);x.unchanged();f.checked('missing retained type proofs/reads are rejected; an already registered source outside the project remains read-only and its post-Review change blocks Confirm')
 f.stop();f.start(2);f.invoke('select',dict(id=x.owner));f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';f.invoke('confirmGroup',dict(ids=ids,token=review['token']));source=f.project/('elements/'+fn.split('::')[1]+'.celem');assert source.exists()and row['signature']['return']in source.read_text();x.unchanged({'FreeInfo.celem','project.cproj'});f.checked('exact type restoration and explicit new Review/Confirm publish stable generated contracts while all original C# and external definitions remain byte-identical')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
