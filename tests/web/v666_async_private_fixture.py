"""Existing owned private graph, explicit async caller, original C# records."""
import copy,hashlib,json,subprocess,uuid
import v536_wide_mixed as f
n=f.n;feature=n+'Flow';impl=n+'FlowBody';graph=impl+'/body:common';child=graph+'/graph:task';leaf=graph+'/node:task/node:body';caller=n+'MainBody/body:common';signature={'args':[{'type':'long','name':'amount'}],'return':'long'}
def text(id,sig):return 'function '+id+' '+sig+' {value blueprintAsync = '+json.dumps(json.dumps(dict(schema=1,completion='explicit-completion')))+';}'
a=f.metadata('blueprintPrepareFeature',id=feature,text=text(feature,'(long amount) -> long'),implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json');function=a['function'];g=a['graph'];body={'id':'body','kind':'code','control':'next','intent':'Preserve original private C#','signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'implementation':'Flow.node.json'};inside={'schema':1,'profile':'sync-acyclic-methods-v1','entry':'body','nodes':[body],'edges':[{'from':'body','port':'next','to':'exit:done'}],'exits':{'done':{'node':'body'}}};g.update(entry='task',nodes=[dict(id='task',kind='graph',control='next',intent='Explicit private Task',signature=copy.deepcopy(signature),arguments={'amount':{'input':'amount'}},graph=inside)],edges=[{'from':'task','port':'next','to':'exit:done'}],exits={'done':{'node':'task'}})
context=dict(implementation=impl,feature=feature,signature=signature,imports={});d=f.metadata('featureBlueprintNodes',featureSource=function,graph=g,implementationContext=context,bodyTarget='common');source='// original private source 😀\r\nreturn Twice(amount)+1;\r\n';record=dict(schema=1,node='body',definitionHash=next(r['definitionHash']for r in d['nestedNodes']if r['id']=='task/body'),source=source,helpers='private static long Twice(long value) => value*2;')
main=f.metadata('blueprintPrepareFeature',id=n+'Main',text=text(n+'Main','() -> int'),implementation=n+'MainBody',graphPath='Main.graph.json',nodePath='Main.node.json');cg=main['graph'];cg.update(entry='invoke',nodes=[dict(id='invoke',kind='call',control='next',intent='Explicit async caller',feature=feature,signature=copy.deepcopy(signature),arguments={'amount':{'constant':3}}),dict(id='after',kind='code',control='next',intent='Observe private result',signature={'args':[{'type':'long','name':'value'}],'return':'void'},arguments={'value':{'node':'invoke'}},implementation='After.node.json')],edges=[{'from':'invoke','port':'next','to':'after'},{'from':'after','port':'next','to':'exit:done'}],exits={'done':{'constant':7}});dd=f.metadata('featureBlueprintNodes',featureSource=main['function'],graph=cg,featureContracts={feature:function});after=dict(schema=1,node='after',definitionHash=next(r['definitionHash']for r in dd['nodes']if r['id']=='after'),source='global::System.Console.WriteLine("private:"+value);');alias='fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24]
for name,value in [('Flow.celem',function),('FlowBody.celem',a['implementation']),('Flow.graph.json',json.dumps(g)),('Flow.node.json',json.dumps(record,ensure_ascii=False)),('Main.celem',main['function']),('MainBody.celem','implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as '+alias+' (long) -> long;blueprint common "Main.graph.json";}'),('Main.graph.json',json.dumps(cg)),('After.node.json',json.dumps(after))]:(f.project/name).write_text(value)
manifest=f.project/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Flow function "Flow.celem";element FlowBody implementation "FlowBody.celem";registry Confectory.Build.DotNet'));physical={p:p.read_bytes()for p in f.project.iterdir()if p.is_file()};public=(f.project/'Flow.celem').read_bytes()
_stop=f.stop
def stop():
 _stop()
 if f.host is not None:f.host.wait(timeout=15)
f.stop=stop
def rpc(action,ok=True,**q):return f.invoke('blueprint',{'action':action,'id':graph,**q},ok)['result'].get('result')
def read(id=child):return rpc('read',id=id)
def proof(d):return json.dumps(sorted([[r['id'],r['revision'],r['hash']]for r in d['sources']]),separators=(',',':'))
def request(d,nodes=None,enabled=True):return dict(id=d['id'],attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=[dict(action='asyncTransition',node='$root',definition=dict(enabled=enabled,nodes=nodes or []))])
def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def unchanged():
 assert(f.project/'Flow.celem').read_bytes()==public;assert json.loads((f.project/'Flow.node.json').read_text())['source']==source
 for p,v in physical.items():
  if p.name not in ['Flow.graph.json','Flow.node.json']:assert p.read_bytes()==v,p
def parent():
 d=read(graph);return rpc('authorBatch',**request(d,[dict(node='task',enabled=True)]))
def build(name):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'portable'],capture_output=True,text=True,env=f.env,timeout=120);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr;report=json.loads(r.stdout);r=subprocess.run(report['run'],capture_output=True,text=True,env=f.env,timeout=20);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)));assert(r.returncode,r.stdout.strip())==(7,'private:7'),(r.returncode,r.stdout,r.stderr)
def confirm():
 ids=read()['reviewIds'];r=f.invoke('reviewGroup',dict(ids=ids))['state']['review'];assert not r.get('errors'),r;v=f.invoke('confirmGroup',dict(ids=ids,token=r['token']))['result']['result'];assert v['sourceConfirmed'],v
