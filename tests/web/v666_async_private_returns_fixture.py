"""Connected private completion line, original native data and explicit exits."""
import copy,hashlib,json,subprocess,uuid
import v666_async_private_fixture as base
f=base.f;feature,impl,graph,child,leaf=base.feature,base.impl,base.graph,base.child,base.leaf
# The authored fixture has native return + out from the outset; conversion
# never changes that public contract or infers a caller conversion.
a=f.metadata('blueprintPrepareFeature',id=feature,text=base.text(feature,'(long amount,out int audit) -> long'),implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json');signature=copy.deepcopy(a['graph']['nodes'][0]['signature']);initial=copy.deepcopy(base.g);initial['contractHash']=a['graph']['contractHash'];task=initial['nodes'][0];task['signature']=copy.deepcopy(signature);inside=task['graph'];inside['nodes'][0]['signature']=copy.deepcopy(signature)
def publish(owner):return dict(id='publishAudit',kind='export',control='next',intent='Original out publication',output='audit',signature={'args':[{'type':'int','name':'value'}],'return':'void'},arguments={'value':{'node':owner,'output':'audit'}})
inside['nodes'].append(publish('body'));inside['edges']=[{'from':'body','port':'next','to':'publishAudit'},{'from':'publishAudit','port':'next','to':'exit:done'}];initial['nodes'].append(publish('task'));initial['edges']=[{'from':'task','port':'next','to':'publishAudit'},{'from':'publishAudit','port':'next','to':'exit:done'}]
context=dict(implementation=impl,feature=feature,signature=signature,imports={});d=f.metadata('featureBlueprintNodes',featureSource=a['function'],graph=initial,implementationContext=context,bodyTarget='common');record=copy.deepcopy(base.record);record['definitionHash']=next(r['definitionHash']for r in d['nestedNodes']if r['id']=='task/body');record['source']='audit=checked((int)amount*2);\r\n'+record['source']
main=copy.deepcopy(base.cg);main['nodes'][0]['signature']=copy.deepcopy(signature);main['nodes'][1]['signature']['args'].append(dict(type='int',name='audit'));main['nodes'][1]['arguments']['audit']={'node':'invoke','output':'audit'};md=f.metadata('featureBlueprintNodes',featureSource=base.main['function'],graph=main,featureContracts={feature:a['function']});after=dict(schema=1,node='after',definitionHash=next(r['definitionHash']for r in md['nodes']if r['id']=='after'),source='global::System.Console.WriteLine("private:"+value+":"+audit);')
for name,value in [('Flow.celem',a['function']),('FlowBody.celem',a['implementation']),('Flow.graph.json',json.dumps(initial)),('Flow.node.json',json.dumps(record,ensure_ascii=False)),('Main.graph.json',json.dumps(main)),('After.node.json',json.dumps(after)),('MainBody.celem','implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as '+base.alias+' (long,out int) -> long;blueprint common "Main.graph.json";}')]:(f.project/name).write_text(value)
units={}
for id,kind,path in [(feature,'function','Flow.celem'),(impl,'implementation','FlowBody.celem'),(graph,'blueprint','Flow.graph.json'),(leaf,'blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(base.caller,'blueprint','Main.graph.json'),(base.caller+'/node:after','blueprint-node','After.node.json')]:
 text=(f.project/path).read_text();units[id]=dict(kind=kind,path=path,original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest(),revision=1)
v=f.metadata('blueprintAsyncTransition',namespace='Owned.Elements',id=graph,units=units,plan=dict(enabled=True,nodes=[dict(node='task',enabled=True)]));units.update(v['units'])
for u in units.values():(f.project/u['path']).write_text(u['draft'])
g=json.loads((f.project/'Flow.graph.json').read_text());g['nodes'].append(dict(id='done',kind='code',control='next',branchOwner='task',intent='Existing connected completion',signature={'args':[{'type':'long','name':'value'},{'type':'int','name':'audit'}],'return':'void'},arguments={'value':{'node':'task'},'audit':{'node':'task','output':'audit'}},implementation='Done.node.json'));g['edges'] += [{'from':'task','port':'completion','to':'done'},{'from':'done','port':'next','to':'return:task'}]
d=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Flow.celem').read_text(),graph=g,implementationContext=context,bodyTarget='common');assert d['state']=='node-definitions',d
(f.project/'Done.node.json').write_text(json.dumps(dict(schema=1,node='done',definitionHash=next(r['definitionHash']for r in d['nodes']if r['id']=='done'),source='global::System.Console.WriteLine("private-complete:"+value+":"+audit);')));(f.project/'Flow.graph.json').write_text(json.dumps(g));physical={p:p.read_bytes()for p in f.project.iterdir()if p.is_file()};public=(f.project/'Flow.celem').read_bytes();code={p.name:json.loads(p.read_text())['source']for p in physical if p.name.endswith('.node.json')};original_edges=copy.deepcopy(g['edges']);original_value=copy.deepcopy(g['nodes'][0]['graph']['exits']['done']);rpc,read,proof,request,checkpoint=base.rpc,base.read,base.proof,base.request,base.checkpoint
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def unchanged():
 assert(f.project/'Flow.celem').read_bytes()==public
 for name,text in code.items():assert json.loads((f.project/name).read_text())['source']==text,name
 for p,v in physical.items():
  if p.name not in ['Flow.graph.json','Flow.node.json','Done.node.json']:assert p.read_bytes()==v,p
def marker():return next(n for n in read(graph)['nodes']if n['id']=='task')['completionBranch']
def selection(branch):
 d=read();plan=dict(entry=d['entry'],edges=copy.deepcopy(d['edges']),exits={e['name']:json.loads(e['valueJson'])for e in d['exits']});plan['exits']['done']['executionBranch']=branch
 return dict(id=child,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=[dict(action='branchExits',node='$branches',definition=plan)])
def select(branch):return rpc('authorBatch',**selection(branch))
def build(name,completed):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(base.manifest),'portable'],capture_output=True,text=True,env=f.env,timeout=120);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr;r=subprocess.run(json.loads(r.stdout)['run'],capture_output=True,text=True,env=f.env,timeout=20);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)));assert(r.returncode,r.stdout.strip())==(7,('private-complete:7:6\n'if completed else'')+'private:7:6'),(r.returncode,r.stdout,r.stderr)
def confirm():
 d=read();ids=d['reviewIds']or[s['id']for s in d['sources']]
 r=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not r.get('errors'),r
 v=f.invoke('confirmGroup',dict(ids=ids,token=r['token']))['result']['result'];assert v['sourceConfirmed'],v
