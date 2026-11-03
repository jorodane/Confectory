"""Real Task/await ABI against a checkout or packaged/restored content.
Only generated fixtures, metadata and local compiler/process calls; no account,
network, provider selection policy or actual Windows device claim.
"""
import copy,hashlib,json,os,pathlib,selectors,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-async-runtime-'));project=case/'project';project.mkdir();dotnet=os.environ['CONFECTORY_DOTNET'];checks=[]
def check(message):
 checks.append(message);(case/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
def invoke(command,request=None):
 return subprocess.run(command,input=None if request is None else json.dumps(request,ensure_ascii=False),text=True,capture_output=True,timeout=120)
def metadata(operation,**request):
 r=invoke([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],dict(operation=operation,**request));assert r.returncode==0,r.stderr;reply=json.loads(r.stdout);assert reply['ok'],reply;return reply['result']
def quote(value):return json.dumps(value,ensure_ascii=False)
def async_source(id,signature,branches=False):
 values='value blueprintAsync = '+quote(json.dumps(dict(schema=1,completion='completion')))+';'
 if branches:values+='value blueprintExecutionBranches = '+quote(json.dumps(dict(schema=1,branches=[dict(id='success',name='성공',value=7),dict(id='failure',name='실패',value=13)]),ensure_ascii=False))+';'
 return 'function '+id+' '+signature+' {'+values+'}'
def prepare(id,signature,branches=False):
 return metadata('blueprintPrepareFeature',id='Async.Fixture::'+id,text=async_source('Async.Fixture::'+id,signature,branches),implementation='Async.Fixture::'+id+'Body',graphPath=id+'.graph.json',nodePath=id+'.node.json')
flow=prepare('Flow','(int n,out int audit) -> int',True);main=prepare('Main','() -> int');g=flow['graph'];g['entry']='body';last=g['nodes'][-1]['id'];g['edges'].append({'from':last,'port':'next','to':'exit:done'});g['exits']={'done':{'executionBranch':'success','value':{'node':'body'}}}
sig=dict(args=[dict(type='int',name='n'),dict(type='int',name='audit',mode='out')],return_='int');sig['return']=sig.pop('return_');cg=main['graph'];cg['entry']='call';alias='fg_call_'+hashlib.sha256(b'Async.Fixture::Flow').hexdigest()[:24]
# Match the stable public enum code symbols; display names never identify branches.
def member(id):return 'Branch_'+hashlib.sha256(json.dumps(id,separators=(',',':')).encode()).hexdigest()[:24]
execution_enum={'primary':'none','members':[{'id':'none','name':'None','value':0},{'id':'success','name':member('success'),'value':7},{'id':'failure','name':member('failure'),'value':13}]}

def code(id,owner=None):
 row=dict(id=id,kind='code',control='next',intent='Observe '+id,signature={'args':[{'type':'int','name':'native'},{'type':'int','name':'audit'}],'return':'void'},arguments={'native':{'node':'call'},'audit':{'node':'call','output':'audit'}},implementation=id+'.node.json')
 if owner:row['branchOwner']=owner
 return row
cg['nodes']=[dict(id='call',kind='call',control='switch',intent='Explicit await with exact public result',feature='Async.Fixture::Flow',signature=sig,arguments={'n':{'constant':5}},publicExecution=g['contractHash'],executionEnum=execution_enum),code('complete','call'),code('success','call'),code('after')]
cg['edges']=[{'from':'call','port':'completion','to':'complete'},{'from':'call','port':'case:success','to':'success'},{'from':'call','port':'next','to':'after'},{'from':'after','port':'next','to':'exit:done'}];cg['exits']={'done':{'constant':0}}
main['implementation']='implementation Async.Fixture::MainBody for Async.Fixture::Main () -> int {import Async.Fixture::Flow as '+alias+' (int,out int) -> int;blueprint common "Main.graph.json";}'
original='// Preserve original task source and CRLF 😀\r\nawait global::System.Threading.Tasks.Task.Delay(30);\r\naudit=n*2;Console.WriteLine("awaited");return n+1;\r\n'
records={}
def write_graph(prepared,bodies):
 graph=prepared['graph'];source=prepared['function'];definitions=metadata('featureBlueprintNodes',featureSource=source,graph=graph,featureContracts={'Async.Fixture::Flow':flow['function']});assert definitions['state']=='node-definitions',definitions
 for name,body in bodies.items():
  row=next(n for n in definitions['nodes'] if n['id']==name);record=dict(schema=1,node=name,definitionHash=row['definitionHash'],source=body);path=next(n['implementation'] for n in graph['nodes'] if n['id']==name);(project/path).write_text(json.dumps(record,ensure_ascii=False));records[path]=record
 id=graph['feature'].split('::')[1];(project/(id+'.celem')).write_text(source);(project/(id+'Body.celem')).write_text(prepared['implementation']);(project/(id+'.graph.json')).write_text(json.dumps(graph,ensure_ascii=False))
write_graph(flow,{'body':original});write_graph(main,{'complete':'Console.WriteLine("complete:"+native+","+audit);','success':'Console.WriteLine("success:"+native+","+audit);','after':'Console.WriteLine("after:"+native+","+audit);'})
manifest=project/'project.cproj';manifest.write_text('project Async.Fixture version "1" {entry Async.Fixture::Main;dependency Confectory.Build.DotNet version "0.1.0";registry Confectory.Build.DotNet '+quote(str(repo/'targets/dotnet/pack.cpack'))+';target portable Confectory.Build.DotNet::Portable;'+''.join('element '+name+' '+kind+' '+quote(name+'.celem')+';' for name,kind in [('Main','function'),('MainBody','implementation'),('Flow','function'),('FlowBody','implementation')])+'}')
cli=repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'
def build(name):
 r=invoke([dotnet,str(cli),'build',str(manifest),'portable']);(case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr;return json.loads(r.stdout)
def run(name,report):
 r=invoke(report['run']);(case/(name+'-execution.json')).write_text(json.dumps(dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)));return r
baseline={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
r=run('first',build('first'));assert (r.returncode,r.stdout.strip())==(0,'awaited\ncomplete:6,10\nsuccess:6,10\nafter:6,10'),(r.returncode,r.stdout,r.stderr);check('real await -> native/out publication -> completion -> exact result -> continuation')
r=run('repeat',build('repeat'));assert r.returncode==0 and r.stdout.count('complete:')==1 and r.stdout.count('success:')==1 and r.stdout.count('after:')==1;assert all(p.read_bytes()==v for p,v in baseline.items());check('repeated build/run preserves original bytes and executes each phase once')
record_path=project/'Flow.node.json';record=copy.deepcopy(records['Flow.node.json']);record['source']='await global::System.Threading.Tasks.Task.Delay(20);throw new InvalidOperationException("original-task-error");';record_path.write_text(json.dumps(record));r=run('failure',build('failure'));assert r.returncode!=0 and 'original-task-error' in r.stderr and not any(t in r.stdout for t in ['complete:','success:','after:']);record_path.write_bytes(baseline[record_path]);check('task failure propagates unchanged without synthesizing completion or failure routing')
# Terminate only this fixture-owned child while its Task is awaiting, then retry.
record['source']='Console.WriteLine("waiting");await global::System.Threading.Tasks.Task.Delay(30000);audit=n*2;return n+1;';record_path.write_text(json.dumps(record));pending=build('interrupted');child=subprocess.Popen(pending['run'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);selector=selectors.DefaultSelector()
try:
 selector.register(child.stdout,selectors.EVENT_READ);assert selector.select(10),'Awaiting fixture did not start';assert child.stdout.readline().strip()=='waiting';child.terminate();out,err=child.communicate(timeout=5);assert not any(t in out for t in ['complete:','success:','after:']);(case/'interrupted-execution.json').write_text(json.dumps(dict(exit=child.returncode,stdout='waiting\n'+out,stderr=err)))
finally:
 selector.close()
 if child.poll() is None:child.kill();child.communicate(timeout=5)
 record_path.write_bytes(baseline[record_path])
r=run('retry',build('retry'));assert (r.returncode,r.stdout.strip())==(0,'awaited\ncomplete:6,10\nsuccess:6,10\nafter:6,10');assert all(p.read_bytes()==v for p,v in baseline.items());check('owned process interruption during await leaves sources intact; a fresh retry completes once')
# An existing synchronous caller is rejected; no source or caller conversion is inferred.
sync=metadata('blueprintPrepareFeature',id='Async.Fixture::Main',text='function Async.Fixture::Main () -> int {}',implementation='Async.Fixture::MainBody',graphPath='Main.graph.json',nodePath='Main.node.json');sg=copy.deepcopy(cg);sg['profile']='sync-acyclic-switch-v1';sg['contractHash']=sync['graph']['contractHash'];before=json.dumps(sg);denied=metadata('featureBlueprintDescribe',featureSource=sync['function'],graph=sg,featureContracts={'Async.Fixture::Flow':flow['function']});assert denied['state']=='invalid' and denied['diagnostics'][0]['code']=='GRAPH_ASYNC_CALLER_REQUIRED',denied;assert before==json.dumps(sg);check('sync caller errors until explicitly converted; no blocking or automatic mutation')
assert all(p.read_bytes()==v for p,v in baseline.items());(case/'evidence.json').write_text(json.dumps(dict(content=str(repo),checks=checks,sourceSha256=hashlib.sha256(original.encode()).hexdigest(),windowsExecuted=False),ensure_ascii=False,indent=2));print('ASYNC_RUNTIME_FIXTURE '+str(case),flush=True)
