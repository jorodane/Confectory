"""Explicit private Task transitions retain public IO, source and receipts."""
import copy,hashlib,json,os,pathlib,subprocess,sys
c=pathlib.Path(sys.argv[1]);tool=c/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';ns='Private.Async';fn=ns+'::Flow';impl=ns+'::FlowBody';gid=impl+'/body:common';view=gid+'/graph:task';nid=gid+'/node:task/node:body';units={}
def m(op,ok=True,**q):
 r=subprocess.run([os.environ['CONFECTORY_DOTNET'],str(tool)],input=json.dumps(dict(operation=op,**q)),text=True,capture_output=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;return v.get('result',v)
def unit(id,kind,path,text):units[id]=dict(kind=kind,path=path,original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest(),revision=1)
a=m('blueprintPrepareFeature',id=fn,text='function '+fn+' () -> int {}',implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json');g=a['graph'];g['profile']='sync-acyclic-nested-v1';leaf=copy.deepcopy(g['nodes'][0]);child=dict(schema=1,profile=g['profile'],entry='body',nodes=[leaf],edges=[dict(from_='body',port='next',to='exit:done')],exits={'done':{'node':'body'}});child['edges'][0]['from']=child['edges'][0].pop('from_');g['nodes']=[dict(id='task',kind='graph',control='next',intent='Owned private boundary',signature=copy.deepcopy(leaf['signature']),arguments={},graph=child)];g['entry']='task';g['edges']=[{'from':'task','port':'next','to':'exit:done'}];g['exits']={'done':{'node':'task'}}
context=dict(implementation=impl,feature=fn,signature=leaf['signature'],imports={});d=m('featureBlueprintNodes',featureSource=a['function'],graph=g,implementationContext=context,bodyTarget='common');assert d['state']=='node-definitions',d;record=dict(schema=1,node='body',definitionHash=next(n['definitionHash']for n in d['nestedNodes']if n['id']=='task/body'),source='// original CRLF 😀\r\nreturn 7;\r\n')
unit(fn,'function','Flow.celem',a['function']);unit(impl,'implementation','FlowBody.celem',a['implementation']);unit(gid,'blueprint','Flow.graph.json',json.dumps(g));unit(nid,'blueprint-node','Flow.node.json',json.dumps(record,ensure_ascii=False))
held=copy.deepcopy(units);m('blueprintAsyncTransition',False,namespace=ns,id=view,units=units,plan=dict(enabled=True,nodes=[]));assert units==held;print('PASS private Task requires explicit async containing function; no automatic promotion',flush=True)
v=m('blueprintAsyncTransition',namespace=ns,id=gid,units=units,plan=dict(enabled=True,nodes=[dict(node='task',enabled=True)]));current=copy.deepcopy(units);current.update(v['units']);public=current[fn]['draft'];assert m('blueprintAsyncCandidates',namespace=ns,id=view,units=current)['enabled'];assert json.loads(current[nid]['draft'])['source']==record['source'];m('blueprintAsyncGuards',namespace=ns,units=current)
v=m('blueprintAsyncTransition',namespace=ns,id=view,units=current,plan=dict(enabled=True,nodes=[dict(node='body',enabled=True)]));current.update(v['units']);assert current[fn]['draft']==public and json.loads(current[nid]['draft'])['source']==record['source'];m('blueprintAsyncGuards',namespace=ns,units=current);print('PASS private leaf transition refreshes complete nested source hashes without changing public IO or C#',flush=True)
for tag in ['wrong-owner','missing-record','changed-source-proof','copied-root','inherited-implementation','invalid-private-path']:
 bad=copy.deepcopy(current);args=dict(namespace=ns,id=view,units=bad,plan=dict(enabled=True,nodes=[]))
 if tag=='wrong-owner':args['owner']=ns+'::Other'
 elif tag=='missing-record':bad.pop(nid)
 elif tag=='changed-source-proof':bad[nid]['baseline']='0'*64
 elif tag=='copied-root':t=json.loads(bad[gid]['draft']);t['copySource']={};bad[gid]['draft']=json.dumps(t)
 elif tag=='inherited-implementation':bad[impl]['draft']='implementation '+impl+' for '+fn+' () -> int extends '+ns+'::Parent {blueprint common "Flow.graph.json";}'
 else:args['id']=gid+'/graph:task/graph:absent'
 m('blueprintAsyncTransition',False,**args)
print('PASS exact owned view, original hashes, complete source closure and non-owned guards remain enforced',flush=True)
# Disable the child operation explicitly before its caller. Its source remains
# the original integer-return body behind the existing completion adapter.
v=m('blueprintAsyncTransition',namespace=ns,id=view,units=current,plan=dict(enabled=True,nodes=[dict(node='body',enabled=False)]));current.update(v['units']);wire=copy.deepcopy(current);t=json.loads(wire[gid]['draft']);t['edges'].append({'from':'task','port':'completion','to':'return:task'});wire[gid]['draft']=json.dumps(t);wired=m('blueprintAsyncTransition',namespace=ns,id=gid,units=wire,plan=dict(enabled=True,nodes=[dict(node='task',enabled=False)]));wired_graph=json.loads(wired['units'][gid]['draft']);assert wired_graph['edges']==t['edges'];wired_marker=wired_graph['nodes'][0]['completionBranch'];v=m('blueprintAsyncTransition',namespace=ns,id=view,units=current,plan=dict(enabled=False,nodes=[]));current.update(v['units']);assert current[fn]['draft']==public and json.loads(current[nid]['draft'])['source']==record['source'];assert json.loads(current[gid]['draft'])['nodes'][0]['completionBranch']==wired_marker;m('blueprintAsyncGuards',namespace=ns,units=current);print('PASS connected sync return retains source, data, public contract and one completion ID from either view',flush=True)
# Existing void Result forwarding keeps its source member IDs as well as the
# parent's connected completion. It is not converted to a new public contract.
a=m('blueprintPrepareFeature',id=fn,text='function '+fn+' () -> void {}',implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json')
enum={'primary':'none','members':[{'id':'none','name':'None','value':0},{'id':'success','name':'Success','value':7}]}
leaf=copy.deepcopy(a['graph']['nodes'][0]);leaf.update(control='switch',executionEnum=copy.deepcopy(enum))
inside=dict(schema=2,profile='sync-acyclic-switch-v1',executionExitMode=True,entry='body',nodes=[leaf],edges=[{'from':'body','port':'case:success','to':'exit:yes'},{'from':'body','port':'next','to':'exit:no'}],exits={'yes':{'executionBranch':'success'},'no':{'executionBranch':'none'}})
g=a['graph'];g.update(profile='sync-acyclic-switch-v1',entry='task',nodes=[dict(id='task',kind='graph',control='switch',intent='Original forwarded results',signature=copy.deepcopy(leaf['signature']),arguments={},executionSource='body',executionEnum=copy.deepcopy(enum),graph=inside)],edges=[{'from':'task','port':'next','to':'exit:done'}],exits={'done':None})
d=m('featureBlueprintNodes',featureSource=a['function'],graph=g,implementationContext=dict(implementation=impl,feature=fn,signature=leaf['signature'],imports={}),bodyTarget='common')
record=dict(schema=1,node='body',definitionHash=next(n['definitionHash']for n in d['nestedNodes']if n['id']=='task/body'),source='// original Result CRLF\r\nreturn Result.Success;\r\n')
units={}
unit(fn,'function','Flow.celem',a['function'])
unit(impl,'implementation','FlowBody.celem',a['implementation'])
unit(gid,'blueprint','Flow.graph.json',json.dumps(g))
unit(nid,'blueprint-node','Flow.node.json',json.dumps(record))
v=m('blueprintAsyncTransition',namespace=ns,id=gid,units=units,plan=dict(enabled=True,nodes=[dict(node='task',enabled=True)]))
units.update(v['units'])
g=json.loads(units[gid]['draft']);g['edges'].append({'from':'task','port':'completion','to':'return:task'});units[gid]['draft']=json.dumps(g)
public=units[fn]['draft']
v=m('blueprintAsyncTransition',namespace=ns,id=view,units=units,plan=dict(enabled=False,nodes=[]))
units.update(v['units'])
demoted=json.loads(units[gid]['draft'])
boundary=demoted['nodes'][0]
assert demoted['edges']==g['edges']and boundary['executionSource']=='body'
assert boundary['executionEnum']==boundary['graph']['nodes'][0]['executionEnum']
assert all(member in boundary['executionEnum']['members']for member in enum['members'])
assert json.loads(units[nid]['draft'])['source']==record['source']and units[fn]['draft']==public
m('blueprintAsyncGuards',namespace=ns,units=units)
print('PASS forwarded Result source/IDs/public IO/C# and connected completion remain one exact candidate',flush=True)
