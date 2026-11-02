"""Bounded M12: owned sync void root and explicit direct Blueprint caller."""
import copy,hashlib,json,pathlib,subprocess,sys,uuid
import v536_wide_mixed as f
compound_mode='--compound-root' in sys.argv
data_mode=compound_mode or '--data-root' in sys.argv
out_mode=data_mode or any(flag in sys.argv for flag in ['--out-root','--multi-root','--no-callers'])
result_code=10 if out_mode else 7;initial_stdout='callee:1\nafter:10' if out_mode else 'callee:1\nafter';final_stdout='callee:1'
signature='(long amount,out int result)' if out_mode else '(long amount)'
if data_mode:
 signature='(long amount,ref int total,out long result,out string label)'
 result_code=42;initial_stdout='callee:1\nafter:420:value:42:42'
if compound_mode:initial_stdout='callee:1\nother:99\nafter:420:value:42:42:99'
expected_review_members=9 if compound_mode else 8
expected_outputs=[{'name':'result','type':'long'},{'name':'label','type':'string'}] if data_mode else [{'name':'result','type':'int'}] if out_mode else []
n=f.n;feature=n+'Flow';impl=n+'FlowBody';graph=impl+'/body:common';caller=n+'MainBody/body:common';manifest=f.project/'project.cproj'
function='function '+feature+' '+signature+' -> void {description "실행 분기 기능";provide '+feature+' with '+impl+';}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+signature+' -> void {}',implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json')
def edge(a,b,port='next'):return {'from':a,'port':port,'to':b}
original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("callee:"+amount);\r\nreturn amount>0?Result.Positive:Result.Negative;\r\n'
root={'schema':1,'profile':'sync-acyclic-switch-v1','feature':feature,'contractHash':prepared['graph']['contractHash'],'entry':'choose','nodes':[{'id':'choose','kind':'code','control':'switch','intent':'기존 C# 판단','signature':{'args':[{'type':'long','name':'amount'}],'return':'void'},'executionEnum':{'primary':'next','members':[{'id':'next','name':'None','value':0},{'id':'positive','name':'Positive','value':1},{'id':'negative','name':'Negative','value':2}]},'arguments':{'amount':{'input':'amount'}},'implementation':'Flow.node.json'}],'edges':[edge('choose','exit:none'),edge('choose','exit:yes','case:positive'),edge('choose','exit:no','case:negative')],'exits':{'yes':None,'no':None,'none':None}}
if out_mode:
 original_source=original_source.replace('return amount>0', ('total=checked(total+(int)amount);\r\nresult=checked(total*10L);\r\nlabel="value:"+total;\r\n' if data_mode else 'result=checked((int)amount*10);\r\n')+'return amount>0')
 if data_mode:
  root['nodes'][0]['signature']['args'].append({'type':'int','name':'total','mode':'ref'})
  root['nodes'][0]['arguments']['total']={'input':'total'}
 root['nodes'][0]['signature']['args'] += [dict(type=p['type'],name=p['name'],mode='out') for p in expected_outputs]
 for name in ['yes','no','none']:
  for p in expected_outputs:
   node='publish_'+name+('_'+p['name'] if data_mode else '')
   root['nodes'].append({'id':node,'kind':'export','control':'next','intent':'기존 출력 발행','output':p['name'],'signature':{'args':[{'type':p['type'],'name':'value'}],'return':'void'},'arguments':{'value':{'node':'choose','output':p['name']}}})
   if name!='none':root['nodes'][-1]['branchOwner']='choose'
   for link in root['edges']:
    if link['to']=='exit:'+name:link['to']=node
   root['edges'].append(edge(node,'exit:'+name))
main=(f.project/'Main.celem').read_text();main_id=n+'Main';call_sig=copy.deepcopy(root['nodes'][0]['signature'])
cg={'schema':1,'profile':'sync-acyclic-switch-v1','feature':main_id,'contractHash':f.metadata('blueprintPrepareFeature',id=main_id,text='function '+main_id+' () -> int {}',implementation=n+'MainBody',graphPath='Main.graph.json',nodePath='After.node.json')['graph']['contractHash'],'entry':'invoke','nodes':[{'id':'invoke','kind':'call','control':'next','intent':'명시 원본 호출','feature':feature,'signature':call_sig,'arguments':{'amount':{'constant':1}}},{'id':'after','kind':'code','control':'next','intent':'기존 다음 동작','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'After.node.json'}],'edges':[edge('invoke','after'),edge('after','exit:return')],'exits':{'return':{'constant':7}}}
if out_mode:
 cg['nodes'][1]['signature']['args']=[{'type':expected_outputs[0]['type'],'name':'value'}];cg['nodes'][1]['arguments']={'value':{'node':'invoke','output':'result'}}
 cg['exits']['return']={'node':'invoke','output':'result'}
if data_mode:
 cg['locals']=[{'id':'counter','name':'counter','type':'int','initial':{'constant':41}}]
 cg['nodes'][0]['arguments']['total']={'local':'counter'}
 cg['nodes'][1]['signature']['args'] += [{'type':'string','name':'text'},{'type':'int','name':'cell'}]
 cg['nodes'][1]['arguments'].update(text={'node':'invoke','output':'label'},cell={'local':'counter'})
 cg['exits']['return']={'local':'counter'}
alias='fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24]
import_signature=' (long,ref int,out long,out string)' if data_mode else ' (long,out int)' if out_mode else ' (long)'
extra_import='';extra_contracts={}
if compound_mode:
 other_feature=n+'Other';other_function='function '+other_feature+' (int seed) -> int {provide '+other_feature+' with '+n+'OtherBody;}'
 extra_import='import '+other_feature+' as fg_call_'+hashlib.sha256(other_feature.encode()).hexdigest()[:24]+' (int) -> int;'
 extra_contracts[other_feature]=other_function
 cg['nodes'].append({'id':'other','kind':'call','control':'next','intent':'그대로 유지할 다른 직접 호출','feature':other_feature,'signature':{'args':[{'type':'int','name':'seed'}],'return':'int'},'arguments':{'seed':{'constant':99}}})
 next(link for link in cg['edges'] if link['from']=='invoke' and link['port']=='next')['to']='other';cg['edges'].append(edge('other','after'))
 cg['nodes'][1]['signature']['args'].append({'type':'int','name':'other'});cg['nodes'][1]['arguments']['other']={'node':'other','output':'return'}
 for name,text in [('Other.celem',other_function),('OtherBody.celem','implementation '+n+'OtherBody for '+other_feature+' (int seed) -> int {body common "Other.csbody";}'),('Other.csbody','global::System.Console.WriteLine("other:"+seed);return seed;')]:(f.project/name).write_text(text)
for name,text in [('Flow.celem',function),('FlowBody.celem',prepared['implementation']),('Flow.graph.json',json.dumps(root)),('MainBody.celem','implementation '+n+'MainBody for '+main_id+' () -> int {import '+feature+' as '+alias+import_signature+' -> void;'+extra_import+'blueprint common "Main.graph.json";}'),('Main.graph.json',json.dumps(cg))]:(f.project/name).write_text(text)
after_source='global::System.Console.WriteLine("after:"+value+":"+text+":"+cell+":"+other);' if compound_mode else 'global::System.Console.WriteLine("after:"+value+":"+text+":"+cell);' if data_mode else 'global::System.Console.WriteLine("after:"+value);' if out_mode else 'global::System.Console.WriteLine("after");'
for g,fn,file,node,source,contracts in [(root,function,'Flow.node.json','choose',original_source,{}),(cg,main,'After.node.json','after',after_source,{feature:function,**extra_contracts})]:
 defs=f.metadata('featureBlueprintNodes',featureSource=fn,graph=g,featureContracts=contracts);assert defs['state']=='node-definitions',defs
 record={'schema':1,'node':node,'definitionHash':next(r['definitionHash'] for r in defs['nodes'] if r['id']==node),'source':source};(f.project/file).write_text(json.dumps(record,ensure_ascii=False))
manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Flow function "Flow.celem";element FlowBody implementation "FlowBody.celem";registry Confectory.Build.DotNet',1))
if compound_mode:
 manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Other function "Other.celem";element OtherBody implementation "OtherBody.celem";registry Confectory.Build.DotNet',1))
 for name in ['Other.celem','OtherBody.celem','Other.csbody']:(f.project/name).chmod(0o400)
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
