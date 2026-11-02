"""Bounded M12: owned sync void root and explicit direct Blueprint caller."""
import copy,hashlib,json,pathlib,subprocess,sys,uuid
import v536_wide_mixed as f
out_mode=any(flag in sys.argv for flag in ['--out-root','--multi-root','--no-callers'])
result_code=10 if out_mode else 7;initial_stdout='callee:1\nafter:10' if out_mode else 'callee:1\nafter';final_stdout='callee:1'
signature='(long amount,out int result)' if out_mode else '(long amount)'
n=f.n;feature=n+'Flow';impl=n+'FlowBody';graph=impl+'/body:common';caller=n+'MainBody/body:common';manifest=f.project/'project.cproj'
function='function '+feature+' '+signature+' -> void {description "실행 분기 기능";provide '+feature+' with '+impl+';}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+signature+' -> void {}',implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json')
def edge(a,b,port='next'):return {'from':a,'port':port,'to':b}
original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("callee:"+amount);\r\nreturn amount>0?Result.Positive:Result.Negative;\r\n'
root={'schema':1,'profile':'sync-acyclic-switch-v1','feature':feature,'contractHash':prepared['graph']['contractHash'],'entry':'choose','nodes':[{'id':'choose','kind':'code','control':'switch','intent':'기존 C# 판단','signature':{'args':[{'type':'long','name':'amount'}],'return':'void'},'executionEnum':{'primary':'next','members':[{'id':'next','name':'None','value':0},{'id':'positive','name':'Positive','value':1},{'id':'negative','name':'Negative','value':2}]},'arguments':{'amount':{'input':'amount'}},'implementation':'Flow.node.json'}],'edges':[edge('choose','exit:none'),edge('choose','exit:yes','case:positive'),edge('choose','exit:no','case:negative')],'exits':{'yes':None,'no':None,'none':None}}
if out_mode:
 original_source=original_source.replace('return amount>0', 'result=checked((int)amount*10);\r\nreturn amount>0')
 root['nodes'][0]['signature']['args'].append({'type':'int','name':'result','mode':'out'})
 for name in ['yes','no','none']:
  node='publish_'+name
  root['nodes'].append({'id':node,'kind':'export','control':'next','intent':'기존 정수 출력 발행','output':'result','signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'choose','output':'result'}}})
  if name!='none':root['nodes'][-1]['branchOwner']='choose'
  for link in root['edges']:
   if link['to']=='exit:'+name:link['to']=node
  root['edges'].append(edge(node,'exit:'+name))
main=(f.project/'Main.celem').read_text();main_id=n+'Main';call_sig={'args':[{'type':'long','name':'amount'}]+([{'type':'int','name':'result','mode':'out'}] if out_mode else []),'return':'void'}
cg={'schema':1,'profile':'sync-acyclic-switch-v1','feature':main_id,'contractHash':f.metadata('blueprintPrepareFeature',id=main_id,text='function '+main_id+' () -> int {}',implementation=n+'MainBody',graphPath='Main.graph.json',nodePath='After.node.json')['graph']['contractHash'],'entry':'invoke','nodes':[{'id':'invoke','kind':'call','control':'next','intent':'명시 원본 호출','feature':feature,'signature':call_sig,'arguments':{'amount':{'constant':1}}},{'id':'after','kind':'code','control':'next','intent':'기존 다음 동작','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'After.node.json'}],'edges':[edge('invoke','after'),edge('after','exit:return')],'exits':{'return':{'constant':7}}}
if out_mode:
 cg['nodes'][1]['signature']['args']=[{'type':'int','name':'value'}];cg['nodes'][1]['arguments']={'value':{'node':'invoke','output':'result'}}
 cg['exits']['return']={'node':'invoke','output':'result'}
alias='fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24]
for name,text in [('Flow.celem',function),('FlowBody.celem',prepared['implementation']),('Flow.graph.json',json.dumps(root)),('MainBody.celem','implementation '+n+'MainBody for '+main_id+' () -> int {import '+feature+' as '+alias+(' (long,out int)' if out_mode else ' (long)')+' -> void;blueprint common "Main.graph.json";}'),('Main.graph.json',json.dumps(cg))]:(f.project/name).write_text(text)
for g,fn,file,node,source,contracts in [(root,function,'Flow.node.json','choose',original_source,{}),(cg,main,'After.node.json','after',('global::System.Console.WriteLine("after:"+value);' if out_mode else 'global::System.Console.WriteLine("after");'),{feature:function})]:
 defs=f.metadata('featureBlueprintNodes',featureSource=fn,graph=g,featureContracts=contracts);assert defs['state']=='node-definitions',defs
 record={'schema':1,'node':node,'definitionHash':next(r['definitionHash'] for r in defs['nodes'] if r['id']==node),'source':source};(f.project/file).write_text(json.dumps(record,ensure_ascii=False))
manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Flow function "Flow.celem";element FlowBody implementation "FlowBody.celem";registry Confectory.Build.DotNet',1))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def read(id=graph):return f.invoke('blueprint',{'action':'read','id':id})['result']['result']
def proof(data):return json.dumps(sorted([[r['id'],r['revision'],r['hash']] for r in data['sources']]),separators=(',',':'))
def plan(data):return {'branches':[{'id':'success','name':'성공','value':1},{'id':'failure','name':'실패','value':2}],'entry':data['entry'],'edges':copy.deepcopy(data['edges']),'exits':{'yes':{'executionBranch':'success'},'no':{'executionBranch':'failure'},'none':{'executionBranch':'none'}},'caller':{'graph':caller,'node':'invoke','routes':[{'branch':'success','to':'exit:return'}]}}
def request(data,selected=None):return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':proof(data),'edits':[{'action':'rootExecution','node':'$root','definition':selected or plan(data)}]}
def rpc(action,success=True,**body):return f.invoke('blueprint',{'action':action,**body},success)['result'].get('result')
def checkpoint():return {str(p):p.read_bytes() for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def build(name,code=None,stdout=None):
 code=result_code if code is None else code;stdout=final_stdout if stdout is None else stdout
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout[-4000:]+result.stderr[-1000:];report=json.loads(result.stdout);run=subprocess.run(report['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr}));assert (run.returncode,run.stdout.strip())==(code,stdout),(run.returncode,run.stdout,run.stderr)
