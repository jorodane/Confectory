"""Result 없는 원문·native 반환/out·연결된 완료를 가진 직접 소유 자료."""
import copy,hashlib,json,subprocess,uuid
import v536_wide_mixed as f
feature=f.n+'Flow';impl=f.n+'FlowBody';graph=impl+'/body:common';caller=f.n+'MainBody/body:common'
fn='function '+feature+' (long amount,out int result) -> void {provide '+feature+' with '+impl+';}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' (long amount,out int result) -> void {}',implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json')
signature={'args':[{'type':'long','name':'amount'},{'type':'int','name':'result','mode':'out'}],'return':'long'}
root={'schema':1,'profile':'sync-acyclic-switch-v1','feature':feature,'contractHash':prepared['graph']['contractHash'],'entry':'choose','nodes':[
 {'id':'choose','kind':'code','control':'next','intent':'원문과 별도 완료 선택','signature':signature,'arguments':{'amount':{'input':'amount'}},'implementation':'Flow.node.json'},
 {'id':'publish','kind':'export','control':'next','intent':'출력 발행','output':'result','signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'choose','output':'result'}}},
 {'id':'completed','kind':'code','control':'next','intent':'기존 완료 작업','signature':{'args':[{'type':'int','name':'value'},{'type':'long','name':'native'}],'return':'void'},'arguments':{'value':{'node':'choose','output':'result'},'native':{'node':'choose','output':'return'}},'implementation':'Completed.node.json'}],
 'edges':[{'from':'choose','port':'next','to':'publish'},{'from':'publish','port':'next','to':'exit:return'},{'from':'completed','port':'next','to':'exit:return'}],'exits':{'return':None}}
main=(f.project/'Main.celem').read_text();main_id=f.n+'Main'
cg={'schema':1,'profile':'sync-acyclic-switch-v1','feature':main_id,'contractHash':f.metadata('blueprintPrepareFeature',id=main_id,text='function '+main_id+' () -> int {}',implementation=f.n+'MainBody',graphPath='Main.graph.json',nodePath='After.node.json')['graph']['contractHash'],'entry':'invoke','nodes':[
 {'id':'invoke','kind':'call','control':'next','intent':'명시 원본 호출','feature':feature,'signature':{'args':copy.deepcopy(signature['args']),'return':'void'},'arguments':{'amount':{'constant':1}}},
 {'id':'after','kind':'code','control':'next','intent':'기존 다음 동작','signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'invoke','output':'result'}},'implementation':'After.node.json'}],
 'edges':[{'from':'invoke','port':'next','to':'after'},{'from':'after','port':'next','to':'exit:return'}],'exits':{'return':{'node':'invoke','output':'result'}}}
alias='fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24]
texts={'Flow.celem':fn,'FlowBody.celem':prepared['implementation'],'Flow.graph.json':json.dumps(root),'Main.graph.json':json.dumps(cg),'MainBody.celem':'implementation '+f.n+'MainBody for '+main_id+' () -> int {import '+feature+' as '+alias+' (long,out int) -> void;blueprint common "Main.graph.json";}'}
source='// 원문·줄바꿈 보존 😀\r\n_ = Result(); result=checked((int)amount*10);\r\nglobal::System.Console.WriteLine("callee:"+amount); return amount+1L;\r\n'
helpers='public static int Result() { return 7; }\r\n'
for g,ft,files,contracts in [(root,fn,{'choose':('Flow.node.json',source,helpers),'completed':('Completed.node.json','global::System.Console.WriteLine("completed:"+value+":"+native);','')},{}),(cg,main,{'after':('After.node.json','global::System.Console.WriteLine("after:"+value);','')},{feature:fn})]:
 definitions=f.metadata('featureBlueprintNodes',featureSource=ft,graph=g,featureContracts=contracts);assert definitions['state']=='node-definitions',definitions
 for nid,(path,body,extra) in files.items():texts[path]=json.dumps({'schema':1,'node':nid,'definitionHash':next(n['definitionHash']for n in definitions['nodes']if n['id']==nid),'source':body,'helpers':extra},ensure_ascii=False)
for name,text in texts.items():(f.project/name).write_text(text)
manifest=f.project/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Flow function "Flow.celem";element FlowBody implementation "FlowBody.celem";registry Confectory.Build.DotNet',1))
units={}
for ident,kind,path in [(feature,'function','Flow.celem'),(impl,'implementation','FlowBody.celem'),(graph,'blueprint','Flow.graph.json'),(graph+'/node:choose','blueprint-node','Flow.node.json'),(graph+'/node:completed','blueprint-node','Completed.node.json'),(main_id,'function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(caller,'blueprint','Main.graph.json'),(caller+'/node:after','blueprint-node','After.node.json')]:
 text=(f.project/path).read_text();units[ident]={'kind':kind,'path':path,'original':text,'draft':text,'baseline':hashlib.sha256(text.encode()).hexdigest(),'revision':0}
for ident,nodes in [(graph,[{'node':'choose','enabled':True}]),(caller,[])]:
 result=f.metadata('blueprintAsyncTransition',namespace='Owned.Elements',id=ident,units=units,plan={'enabled':True,'nodes':nodes});units.update(result['units'])
for unit in units.values():(f.project/unit['path']).write_text(unit['draft'])
root=json.loads((f.project/'Flow.graph.json').read_text());next(n for n in root['nodes']if n['id']=='completed')['branchOwner']='choose';next(e for e in root['edges']if e['from']=='completed')['to']='return:choose';root['edges'].append({'from':'choose','port':'completion','to':'completed'})
definitions=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Flow.celem').read_text(),graph=root);assert definitions['state']=='node-definitions',definitions
for name,nid in [('Flow.node.json','choose'),('Completed.node.json','completed')]:
 record=json.loads((f.project/name).read_text());record['definitionHash']=next(n['definitionHash']for n in definitions['nodes']if n['id']==nid);(f.project/name).write_text(json.dumps(record,ensure_ascii=False))
(f.project/'Flow.graph.json').write_text(json.dumps(root))
physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts};initial_edges=copy.deepcopy(root['edges'])
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def code_unchanged():
 record=json.loads((f.project/'Flow.node.json').read_text());assert record['source']==source and record['helpers']==helpers
def read():return f.invoke('blueprint',{'action':'read','id':graph})['result']['result']
def proof(data):return json.dumps(sorted([[r['id'],r['revision'],r['hash']]for r in data['sources']]),separators=(',',':'))
def rpc(action,success=True,**body):return f.invoke('blueprint',{'action':action,**body},success)['result'].get('result')
def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def request(data,flag=False):return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':proof(data),'edits':[{'action':'asyncTransition','node':'$root','definition':{'enabled':True,'nodes':[{'node':'choose','enabled':flag}]}}]}
def edit(data,selection):return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':proof(data),'edits':[{'action':'completionCode','node':'choose','definition':{'source':source,'completion':selection}}]}
def selected():return next(n for n in read()['nodes']if n['id']=='choose')
def selection():return 'return context.result==10 && context.NativeReturn==2L ? Result.'+selected()['completionBranch']['name']+' : Result.None;'
def build(name,completed=False):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout[-5000:]+r.stderr
 report=json.loads(r.stdout);r=subprocess.run(report['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}));assert(r.returncode,r.stdout.strip())==(10,'callee:1\n'+('completed:10:2\n'if completed else '')+'after:10'),(r.returncode,r.stdout,r.stderr)
def confirm():
 ids=read()['reviewIds'];r=f.invoke('reviewGroup',{'ids':ids})['state']['review'];assert not r.get('errors'),r;return f.invoke('confirmGroup',{'ids':ids,'token':r['token']})['result']['result']
