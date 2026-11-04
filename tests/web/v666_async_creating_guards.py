"""New owned leaf provenance and missing-file CAS; never a missing header/graph exception."""
import copy,hashlib,json,os,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]);tool=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';ns='Owned.NewAsync';fn=ns+'::Flow';impl=fn+'Body';gid=impl+'/body:common';newid=gid+'/node:fresh'
def m(op,ok=True,**q):
 r=subprocess.run([os.environ['CONFECTORY_DOTNET'],str(tool)],input=json.dumps(dict(operation=op,**q)),capture_output=True,text=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;return v.get('result',v)
a=m('blueprintPrepareFeature',id=fn,text='function '+fn+' () -> void {description "원래 설명";}',implementation=impl,graphPath='flow/Flow.graph.json',nodePath='nodes/old.node.json');old=copy.deepcopy(a['graph']);old['profile']='sync-acyclic-switch-v1';units={}
def unit(id,kind,path,original,draft=None,baseline=None):units[id]=dict(kind=kind,path=path,original=original,draft=original if draft is None else draft,baseline=hashlib.sha256(original.encode()).hexdigest()if baseline is None else baseline,revision=1)
source='// original 😀\r\nglobal::System.Console.WriteLine("old");\r\n';defs=m('featureBlueprintNodes',featureSource=a['function'],graph=old);record=dict(schema=1,node='body',definitionHash=defs['nodes'][0]['definitionHash'],source=source)
unit(fn,'function','Flow.celem',a['function']);unit(impl,'implementation','FlowBody.celem',a['implementation']);unit(gid,'blueprint','flow/Flow.graph.json',json.dumps(old));unit(gid+'/node:body','blueprint-node','flow/nodes/old.node.json',json.dumps(record,ensure_ascii=False))
graph=copy.deepcopy(old);graph['nodes'].append(dict(id='fresh',kind='code',control='next',intent='새 동작',signature=dict(args=[],**{'return':'void'}),arguments={},implementation='nodes/fresh.node.json'));graph['edges']=[dict(**{'from':'body'},port='next',to='fresh'),dict(**{'from':'fresh'},port='next',to='exit:return')];units[gid]['draft']=json.dumps(graph)
defs=m('featureBlueprintNodes',featureSource=a['function'],graph=graph);newsource='// authored before first Confirm\r\nglobal::System.Console.WriteLine("new");\r\n';newrecord=dict(schema=1,node='fresh',definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']=='fresh'),source=newsource);unit(newid,'blueprint-node','flow/nodes/fresh.node.json','',json.dumps(newrecord),baseline='missing')
q=dict(namespace=ns,id=gid,units=units);c=m('blueprintAsyncCandidates',**q);assert any(n['id']=='fresh'for n in c['nodes']);v=m('blueprintAsyncTransition',**q,plan=dict(enabled=True,nodes=[dict(node='fresh',enabled=True)]));current=copy.deepcopy(units);current.update(v['units']);assert current[fn]['asyncTransition']['reads'][newid]=={'path':'flow/nodes/fresh.node.json','hash':'missing'};assert json.loads(current[newid]['draft'])['source']==newsource;assert json.loads(current[gid+'/node:body']['draft'])['source']==source;m('blueprintAsyncGuards',namespace=ns,units=current);print('PASS exact owned new leaf retains original C# and absent-file final CAS in a complete group',flush=True)
def original_graph(u,g):u[gid]['original']=json.dumps(g);u[gid]['baseline']=hashlib.sha256(u[gid]['original'].encode()).hexdigest()
for kind in ['existing-id','existing-path','nonempty-original','wrong-record','wrong-path','new-header','new-graph','foreign','alias','missing-member']:
 bad=copy.deepcopy(units)
 if kind=='existing-id':g=copy.deepcopy(old);g['nodes'].append(copy.deepcopy(graph['nodes'][-1]));original_graph(bad,g)
 elif kind=='existing-path':g=copy.deepcopy(old);g['nodes'][0]['implementation']='nodes/fresh.node.json';original_graph(bad,g)
 elif kind=='nonempty-original':bad[newid]['original']='previous source'
 elif kind=='wrong-record':r=copy.deepcopy(newrecord);r['node']='body';bad[newid]['draft']=json.dumps(r)
 elif kind=='wrong-path':bad[newid]['path']='other.node.json'
 elif kind=='new-header':bad[fn]['baseline']='missing';bad[fn]['original']=''
 elif kind=='new-graph':bad[gid]['baseline']='missing';bad[gid]['original']=''
 elif kind=='foreign':bad[newid]['kind']='body'
 elif kind=='alias':bad[newid]['path']=bad[impl]['path']
 else:bad.pop(newid)
 m('blueprintAsyncCandidates',False,namespace=ns,id=gid,units=bad)
print('PASS original identity/path reuse, forged missing originals, headers/graphs, aliases and missing members refused',flush=True)
for kind in ['missing-proof','changed-proof','missing-unit','changed-source-path']:
 bad=copy.deepcopy(current)
 if kind=='missing-proof':bad[fn]['asyncTransition']['reads'].pop(newid)
 elif kind=='changed-proof':bad[fn]['asyncTransition']['reads'][newid]['hash']='0'*64
 elif kind=='missing-unit':bad.pop(newid)
 else:bad[newid]['path']='another.node.json'
 m('blueprintAsyncGuards',False,namespace=ns,units=bad)
print('PASS cold/Review guard retains the exact absent-file provenance and rejects tampered receipts',flush=True)

blank=copy.deepcopy(units);r=copy.deepcopy(newrecord);r.update(source='',definitionHash='0'*64);blank[newid]['draft']=json.dumps(r);v=m('blueprintAsyncTransition',namespace=ns,id=gid,units=blank,plan=dict(enabled=True,nodes=[dict(node='fresh',enabled=True)]));assert json.loads(v['units'][newid]['draft'])['source']=='';assert json.loads(v['units'][newid]['draft'])['definitionHash']!='0'*64
forged=copy.deepcopy(units);r=copy.deepcopy(newrecord);r['definitionHash']='0'*64;forged[newid]['draft']=json.dumps(r);m('blueprintAsyncTransition',False,namespace=ns,id=gid,units=forged,plan=dict(enabled=True,nodes=[dict(node='fresh',enabled=True)]))
print('PASS only a proven blank new-node placeholder receives a definition receipt; authored source is never silently rebound',flush=True)
