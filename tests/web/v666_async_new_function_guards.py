"""First new global function: owned registration, absent-file CAS and frozen IO."""
import copy,hashlib,json,os,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]);tool=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';ns='Owned.NewRoot';fn=ns+'::Fresh';impl=fn+'Body';gid=impl+'/body:common';nid=gid+'/node:body';mid=ns+'::ProjectManifest'
def m(op,ok=True,**q):
 r=subprocess.run([os.environ['CONFECTORY_DOTNET'],str(tool)],input=json.dumps(dict(operation=op,**q)),capture_output=True,text=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;return v.get('result',v)
a=m('blueprintPrepareFeature',id=fn,text='function '+fn+' () -> void {description "새 기능 😀";}',implementation=impl,graphPath='blueprints/root.json',nodePath='nodes/body.json');assert a['graph']['profile']=='sync-acyclic-switch-v1'
for signature in ['(int input,out long count) -> int','(object value) -> object','(out object value) -> void']:
 sample=m('blueprintPrepareFeature',id=fn,text='function '+fn+' '+signature+' {}',implementation=impl,graphPath='blueprints/root.json',nodePath='nodes/body.json');assert sample['graph']['profile']=='sync-acyclic-switch-v1';assert not any(n.get('forwardCallerStorage')for n in sample['graph']['nodes'])
ref=m('blueprintPrepareFeature',id=fn,text='function '+fn+' (ref long value) -> void {}',implementation=impl,graphPath='blueprints/root.json',nodePath='nodes/body.json');assert ref['graph']['nodes'][0]['forwardCallerStorage'] is True
original='project '+ns+' version "1" {element Old function "Old.celem";}'
current=original[:-1]+'element Fresh function "elements/Fresh.celem";element FreshBody implementation "elements/FreshBody.celem";}'
units={}
def u(id,kind,path,text,missing=True,draft=None):units[id]=dict(kind=kind,path=path,original=''if missing else text,draft=text if draft is None else draft,baseline='missing'if missing else hashlib.sha256(text.encode()).hexdigest(),revision=1)
u(mid,'project','project.cproj',original,False,current);u(ns+'::Old','function','Old.celem','function '+ns+'::Old () -> void {}',False)
for id,kind,path,value in [(fn,'function','elements/Fresh.celem',a['function']),(impl,'implementation','elements/FreshBody.celem',a['implementation']),(gid,'blueprint','blueprints/root.json',json.dumps(a['graph'])),(nid,'blueprint-node','blueprints/nodes/body.json',json.dumps(a['node']))]:u(id,kind,path,value)
canonical=copy.deepcopy(units);canonical[gid]['path']='blueprints/./root.json';m('blueprintAsyncCandidates',namespace=ns,id=gid,units=canonical)
q=dict(namespace=ns,id=gid,units=units);assert m('blueprintAsyncCandidates',**q)['enabled']is False
v=m('blueprintAsyncTransition',**q,plan=dict(enabled=True,nodes=[dict(node='body',enabled=True)]));saved=copy.deepcopy(units);saved.update(v['units']);assert saved[fn]['asyncTransition']['creationFunction']==a['function'];assert saved[fn]['asyncTransition']['reads'][mid]['hash']==units[mid]['baseline'];assert all(saved[fn]['asyncTransition']['reads'][id]['hash']=='missing'for id in [fn,impl,gid,nid]);assert json.loads(saved[nid]['draft'])['source']=='';m('blueprintAsyncGuards',namespace=ns,units=saved);print('PASS fresh method scaffold binds all new destinations and original registration to one missing-file CAS group',flush=True)
for tag in ['missing-manifest','new-manifest','bad-manifest-hash','wrong-registration','old-identity','old-path','foreign-owner','nonempty-original','wrong-record','borrowed-body','legacy']:
 bad=copy.deepcopy(units)
 if tag=='missing-manifest':bad.pop(mid)
 elif tag=='new-manifest':bad[mid].update(baseline='missing',original='')
 elif tag=='bad-manifest-hash':bad[mid]['baseline']='0'*64
 elif tag=='wrong-registration':bad[mid]['draft']=current.replace('"elements/Fresh.celem"','"other.celem"')
 elif tag=='old-identity':text=original[:-1]+'element Fresh function "elements/Fresh.celem";}';bad[mid].update(original=text,baseline=hashlib.sha256(text.encode()).hexdigest())
 elif tag=='old-path':text=original[:-1]+'element Alias function "elements/Fresh.celem";}';bad[mid].update(original=text,baseline=hashlib.sha256(text.encode()).hexdigest())
 elif tag=='foreign-owner':bad[fn]['creationOwner']=ns+'::Old'
 elif tag=='nonempty-original':bad[impl]['original']='old body'
 elif tag=='wrong-record':record=copy.deepcopy(a['node']);record['node']='peer';bad[nid]['draft']=json.dumps(record)
 elif tag=='borrowed-body':bad[ns+'::OldBody']=dict(kind='implementation',path='OldBody.celem',original='implementation '+ns+'::OldBody for '+ns+'::Old () -> void {body common "blueprints/root.json";}',draft='implementation '+ns+'::OldBody for '+ns+'::Old () -> void {body common "blueprints/root.json";}',baseline=hashlib.sha256(('implementation '+ns+'::OldBody for '+ns+'::Old () -> void {body common "blueprints/root.json";}').encode()).hexdigest())
 else:g=copy.deepcopy(a['graph']);g['profile']='sync-acyclic-v1';bad[gid]['draft']=json.dumps(g)
 m('blueprintAsyncCandidates',False,namespace=ns,id=gid,units=bad)
print('PASS absent/forged registration, reserved IDs/paths, owner/copy mismatches and legacy conversion refuse without weakening scope',flush=True)
for tag in ['missing-origin','changed-io','missing-read','changed-read','aliased-path']:
 bad=copy.deepcopy(saved)
 if tag=='missing-origin':bad[fn]['asyncTransition'].pop('creationFunction')
 elif tag=='changed-io':bad[fn]['asyncTransition']['creationFunction']=a['function'].replace('-> void','-> int')
 elif tag=='missing-read':bad[fn]['asyncTransition']['reads'].pop(mid)
 elif tag=='changed-read':bad[fn]['asyncTransition']['reads'][nid]['hash']='0'*64
 else:bad[nid]['path']='Old.celem'
 m('blueprintAsyncGuards',False,namespace=ns,units=bad)
print('PASS cold/Review rejects changed first-transition IO, registration receipts, missing reads and path aliasing',flush=True)
