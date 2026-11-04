"""Contained contract ownership and whole first-creation group async guards."""
import copy,hashlib,json,os,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]);tool=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';ns='Owned.Information';owner=ns+'::Info';fn=owner+'_Function_'+'a'*32;impl=fn+'BlueprintBody';gid=impl+'/body:common';nid=gid+'/node:body';mid=ns+'::ProjectManifest'
def m(op,ok=True,**q):
 r=subprocess.run([os.environ['CONFECTORY_DOTNET'],str(tool)],input=json.dumps(dict(operation=op,**q)),capture_output=True,text=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;return v.get('result',v)
text='function '+fn+' () -> void {}';base='schema '+owner+' {field Power single general long;}';info=base[:-1]+'contain function '+fn+';}';a=m('blueprintPrepareImplementation',owner=owner,ownerText=info,id=fn,text=text,implementation=impl,graphPath='blueprints/root.json',nodePath='nodes/body.json');assert a['graph']['profile']=='sync-acyclic-switch-v1'
original='project '+ns+' version "1" {element Info schema "Info.celem";}';current=original[:-1]+'element '+fn.split('::')[1]+' function "elements/function.celem";element '+impl.split('::')[1]+' implementation "elements/implementation.celem";}'
units={}
def u(id,kind,path,text,missing=True,draft=None):units[id]=dict(kind=kind,path=path,original=''if missing else text,draft=text if draft is None else draft,baseline='missing'if missing else hashlib.sha256(text.encode()).hexdigest(),revision=1)
u(owner,'schema','Info.celem',base,False,a['owner']);u(mid,'project','project.cproj',original,False,current);u(fn,'function','elements/function.celem',text);units[fn]['creationOwner']=owner
for id,kind,path,value in [(impl,'implementation','elements/implementation.celem',a['implementation']),(gid,'blueprint','blueprints/root.json',json.dumps(a['graph'])),(nid,'blueprint-node','blueprints/nodes/body.json',json.dumps(a['node']))]:u(id,kind,path,value)
units[impl]['creationOwner']=owner;group=sorted(units)
for unit in units.values():unit['atomicEditGroup']=group
q=dict(namespace=ns,id=gid,owner=owner,units=units);m('blueprintAsyncCandidates',**q);v=m('blueprintAsyncTransition',**q,plan=dict(enabled=True,nodes=[dict(node='body',enabled=True)]));saved=copy.deepcopy(units);saved.update(v['units']);assert set(v['group'])==set(group);assert saved[fn]['asyncTransition']['informationOwner']==owner and saved[fn]['asyncTransition']['creationFunction']==text;m('blueprintAsyncGuards',namespace=ns,units=saved);assert all(saved[i]['baseline']=='missing'for i in [fn,impl,gid,nid]);assert saved[owner]['draft']==a['owner'];print('PASS direct information creation keeps exact contain/provide, whole original review group, first IO and missing-file guards',flush=True)
for tag in ['no-owner','other-owner','contain-missing','wrong-owner-origin','shared-binding','wrong-creator','old-identity','foreign-group']:
 bad=copy.deepcopy(units);request={**q,'units':bad}
 if tag=='no-owner':request.pop('owner')
 elif tag=='other-owner':request['owner']=ns+'::Peer'
 elif tag=='contain-missing':bad[owner]['draft']=bad[owner]['draft'].replace('contain function '+fn+';','')
 elif tag=='wrong-owner-origin':bad[owner]['baseline']='0'*64
 elif tag=='shared-binding':bad[ns+'::Peer']=dict(kind='object',path='Peer.celem',original='',draft='object '+ns+'::Peer {provide '+fn+' with '+impl+';}',baseline='missing')
 elif tag=='wrong-creator':bad[impl]['creationOwner']=ns+'::Peer'
 elif tag=='old-identity':old=base[:-1]+'contain function '+fn+';}';bad[owner].update(original=old,baseline=hashlib.sha256(old.encode()).hexdigest())
 else:
  for row in bad.values():row['atomicEditGroup']=group+[ns+'::Peer']
 if tag=='foreign-group':m('blueprintAsyncTransition',False,**request,plan=dict(enabled=True,nodes=[]))
 else:m('blueprintAsyncCandidates',False,**request)
print('PASS missing/foreign owner, changed containment, shared provider, creator mismatch, old absent source and unrelated group are refused',flush=True)
for tag in ['owner-marker','assignment','containment','origin']:
 bad=copy.deepcopy(saved)
 if tag=='owner-marker':bad[fn]['asyncTransition'].pop('informationOwner')
 elif tag=='assignment':bad[owner]['draft']=bad[owner]['draft'].replace(impl,ns+'::Other')
 elif tag=='containment':bad[owner]['draft']=bad[owner]['draft'].replace('contain function '+fn+';','')
 else:bad[fn]['asyncTransition']['creationFunction']=text.replace('-> void','-> int')
 m('blueprintAsyncGuards',False,namespace=ns,units=bad)
print('PASS restored receipt cannot lose owner, change assignment/containment or replace original IO',flush=True)
# A separately confirmed own declaration may get its first blank implementation.
published=copy.deepcopy(units);oldInfo=base[:-1]+'contain function '+fn+';}';published[owner].update(original=oldInfo,baseline=hashlib.sha256(oldInfo.encode()).hexdigest());published[fn].update(original=text,baseline=hashlib.sha256(text.encode()).hexdigest());published[fn].pop('creationOwner');oldManifest=original[:-1]+'element '+fn.split('::')[1]+' function "elements/function.celem";}';published[mid].update(original=oldManifest,baseline=hashlib.sha256(oldManifest.encode()).hexdigest());m('blueprintAsyncTransition',namespace=ns,id=gid,owner=owner,units=published,plan=dict(enabled=True,nodes=[dict(node='body',enabled=True)]));print('PASS physically confirmed contained function can create its first owned async implementation without changing IO',flush=True)
