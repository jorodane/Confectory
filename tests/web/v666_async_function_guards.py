"""공개 완료의 저장/복원 관측 범위와 임의 계약 변조 거절."""
import copy,hashlib,json,subprocess
import v666_async_function_fixture as x
f=x.f;sdk=f.env['CONFECTORY_DOTNET'];tool=f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';units={}
for id,row in x.previous.units.items():
 text=(f.project/row['path']).read_text();units[id]=dict(kind=row['kind'],path=row['path'],original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest(),revision=0)
p=f.project/'PublicDone.node.json';text=p.read_text();units[x.caller+'/node:publicDone']=dict(kind='blueprint-node',path=p.name,original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest(),revision=0)
def meta(operation,ok=True,**kw):
 r=subprocess.run([sdk,str(tool)],input=json.dumps(dict(operation=operation,**kw)),text=True,capture_output=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;return v.get('result')
def transition(source,enabled):
 r=meta('blueprintAsyncTransition',namespace='Owned.Elements',id=x.graph,units=source,plan=dict(enabled=enabled,nodes=[]));out=copy.deepcopy(source);out.update(r['units']);return out
current=transition(units,False);assert meta('blueprintAsyncGuards',namespace='Owned.Elements',units=current)['valid'];x.original();print('PASS public completion preserves the owned full caller/source group',flush=True)
lazy=copy.deepcopy(current);lazy['Owned.Elements::Dormant/body:common']=dict(kind='blueprint',path='unrelated.graph.json',draft=None);assert meta('blueprintAsyncGuards',namespace='Owned.Elements',units=lazy)['valid'];print('PASS unrelated lazy body locators stay unread during cold validation',flush=True)
for label,mutate in [
 ('caller receipt',lambda u:u[x.feature]['asyncTransition'].update(callers=[])),
 ('required caller draft',lambda u:u[x.caller].update(draft=None)),
 ('call contract',lambda u:None),
 ('public marker',lambda u:None)]:
 bad=copy.deepcopy(current)
 if label=='call contract':
  g=json.loads(bad[x.caller]['draft']);next(n for n in g['nodes']if n['id']=='invoke')['publicExecution']='0'*64;bad[x.caller]['draft']=json.dumps(g)
 elif label=='public marker':bad[x.feature]['draft']=bad[x.feature]['draft'].replace('blueprintFunctionCompletion','missingFunctionCompletion')
 else:mutate(bad)
 assert bad!=current,label;meta('blueprintAsyncGuards',False,namespace='Owned.Elements',units=bad);x.original();print('PASS tampered '+label+' is rejected without weakening source observations',flush=True)
bad=copy.deepcopy(units);bad[f.n+'MainBody']['draft']=bad[f.n+'MainBody']['draft'].replace('blueprint common "Main.graph.json"','body common "Main.csbody"');held=copy.deepcopy(bad);meta('blueprintAsyncTransition',False,namespace='Owned.Elements',id=x.graph,units=bad,plan=dict(enabled=False,nodes=[]));assert bad==held;x.original();print('PASS native import caller retains its explicit source compatibility boundary',flush=True)
again=transition(current,True);off=transition(again,False);assert json.loads(off[x.caller]['draft'])['edges']==x.original_edges;assert json.loads(off[x.graph]['draft'])['nodes']==x.local_nodes;assert meta('blueprintAsyncGuards',namespace='Owned.Elements',units=off)['valid'];x.original();print('PASS whole-function repetition reserves the same completion and original local/source identities',flush=True)
# Existing ordinary branch removal remains explicit. A retained completion
# wire may not disappear as an accidental side effect of deleting its port.
clean=copy.deepcopy(current)
for row in clean.values():
 row['original']=row['draft'];row['baseline']=hashlib.sha256(row['draft'].encode()).hexdigest();row.pop('asyncTransition',None);row.pop('atomicEditGroup',None)
choices=meta('blueprintRootExecutionCandidates',id=x.graph,units=clean);m=choices['branches'][0];g=json.loads(clean[x.graph]['draft']);plan=dict(branches=[],entry=g['entry'],edges=g['edges'],exits=g['exits'],caller=dict(graph=x.caller,node='invoke',routes=[]))
meta('blueprintRootExecution',False,namespace='Owned.Elements',id=x.graph,units=clean,plan=plan);x.original();print('PASS removing a still-wired ordinary public completion retains the full input',flush=True)
plan['caller']['routes']=[dict(branch=m['id'],to=None)];deleted=meta('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=clean,plan=plan);out=copy.deepcopy(clean);out.update(deleted['units']);wires=json.loads(out[x.caller]['draft'])['edges'];assert wires==[e for e in x.original_edges if not(e['from']=='invoke'and e['port']=='completion')];assert 'blueprintFunctionCompletion'not in out[x.feature]['draft'];x.original();print('PASS explicit existing caller disconnection removes only its chosen completion wire and marker',flush=True)
referenced=copy.deepcopy(units);g=json.loads(referenced[x.caller]['draft']);next(n for n in g['nodes']if n['id']=='invoke')['imports']=[x.feature];referenced[x.caller]['draft']=json.dumps(g);result=transition(referenced,False);assert meta('blueprintAsyncGuards',namespace='Owned.Elements',units=result)['valid'];x.original();print('PASS a declared graph-call reference is not mistaken for opaque C# source calls',flush=True)
# Its ordinary number/name stay reserved while the same port is implicit async.
reserved=copy.deepcopy(again)
for row in reserved.values():
 row['original']=row['draft'];row['baseline']=hashlib.sha256(row['draft'].encode()).hexdigest();row.pop('asyncTransition',None);row.pop('atomicEditGroup',None)
c=meta('blueprintRootExecutionCandidates',id=x.graph,units=reserved);g=json.loads(reserved[x.graph]['draft']);bad=dict(branches=[dict(id='other',name='다른 분기',value=1)],entry=g['entry'],edges=g['edges'],exits=g['exits'],caller=dict(graph=x.caller,node='invoke',routes=[]));meta('blueprintRootExecution',False,namespace='Owned.Elements',id=x.graph,units=reserved,plan=bad);x.original();print('PASS async reservation prevents another public branch from taking the completion number',flush=True)
bad['branches'][0]['value']=2;valid=meta('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=reserved,plan=bad);assert valid['group'];x.original();print('PASS an explicitly distinct public branch remains editable beside the async reservation',flush=True)
