"""M12 callee update preserves an already-public caller's separate contract/return."""
import copy,hashlib,json,re,subprocess
import v666_root_execution_fixture as base
f=base.f
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller
branch_caller_mode=True;data_mode=True;out_mode=True;result_code=10
initial_stdout='callee:1\nafter:10\ncaller:17:10';final_stdout='callee:1\ncaller:17:10'
function=base.function;root=base.root;manifest=base.manifest
main_id=f.n+'Main';driver_id=f.n+'Driver'
units={}
for id,kind,path in [(feature,'function','Flow.celem'),(impl,'implementation','FlowBody.celem'),(graph,'blueprint','Flow.graph.json'),(graph+'/node:choose','blueprint-node','Flow.node.json'),(main_id,'function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(caller,'blueprint','Main.graph.json'),(caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
# Prepare a legitimate previously-confirmed caller contract using the existing M12 API.
primed=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=caller,units=units,plan={'branches':[{'id':'caller_done','name':'성공','value':17}],'entry':base.cg['entry'],'edges':base.cg['edges'],'exits':{'return':{'executionBranch':'caller_done','value':copy.deepcopy(base.cg['exits']['return'])}},'callers':[],'targets':[]})
for id in [main_id,caller]:(f.project/primed['units'][id]['path']).write_text(primed['units'][id]['draft'])
caller_source=(f.project/'Main.celem').read_bytes();caller_graph=json.loads((f.project/'Main.graph.json').read_text())
symbol='E'+hashlib.sha256(json.dumps(main_id,ensure_ascii=False).encode()).hexdigest()[:24]
for name,text in [('Driver.celem','function '+driver_id+' () -> int {provide '+driver_id+' with '+f.n+'DriverBody;}'),('DriverBody.celem','implementation '+f.n+'DriverBody for '+driver_id+' () -> int {import '+main_id+' as Caller () -> int;body common "Driver.csbody";}'),('Driver.csbody','var branch=((global::Confectory.Contracts.'+symbol+'.IExecutionInvoke)calls.Caller).InvokeExecution(out int value);global::System.Console.WriteLine("caller:"+(int)branch+":"+value);return value;')]: (f.project/name).write_text(text)
text=manifest.read_text().replace('entry '+main_id+';','entry '+driver_id+';').replace('registry Confectory.Build.DotNet','element Driver function "Driver.celem";element DriverBody implementation "DriverBody.celem";registry Confectory.Build.DotNet',1)
manifest.write_text(re.sub(r'element (\w+) \w+ "[^"]+";',lambda m:m.group() if m[1] in {'Main','MainBody','Flow','FlowBody','Driver','DriverBody'} else '',text))
(f.project/'Main.celem').chmod(0o400)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};base.physical=physical
original=base.original;read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof

def build(name,code=None,stdout=None):
 base.build(name,result_code if code is None else code,final_stdout if stdout is None else stdout)
 assert (f.project/'Main.celem').read_bytes()==caller_source
 g=json.loads((f.project/'Main.graph.json').read_text());assert g['exits']==caller_graph['exits'] and g['contractHash']==caller_graph['contractHash'] and g['schema']==2 and g['executionExitMode'] is True

def plan(data):return base.plan(data)
def request(data,selected=None):return base.request(data,selected or plan(data))

def __getattr__(name):return getattr(base,name)

def change_header(value):
 p=f.project/'Main.celem';p.chmod(0o600)
 try:p.write_bytes(value)
 finally:p.chmod(0o400)

def check_caller_guards(data,prepared,req,before):
 assert prepared['units'][main_id]['draft'].encode()==caller_source
 g=json.loads(prepared['units'][caller]['draft']);assert g['exits']==caller_graph['exits'] and g['contractHash']==caller_graph['contractHash']
 units={row['id']:{'kind':row['kind'],'path':row['path'],'draft':(f.project/row['path']).read_text()} for row in data['sources']}
 for kind in ['foreign-branch','missing-contract','unknown-caller-return']:
  selected=plan(data);bad=copy.deepcopy(units)
  if kind=='foreign-branch':selected['exits']['yes']['executionBranch']='caller_done'
  elif kind=='missing-contract':bad[main_id]['draft']=base.main
  else:
   body=json.loads(bad[caller]['draft']);body['exits']['return']['executionBranch']='deleted';bad[caller]['draft']=json.dumps(body)
  try:f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=graph,units=bad,plan=selected)
  except AssertionError:pass
  else:raise AssertionError('Caller contract/branch scope was implicitly changed: '+kind)
 change_header(caller_source+b' ')
 try:rpc('authorBatch',False,**req)
 finally:change_header(caller_source)
 assert checkpoint()==before;original();f.checked('호출자 자신의 공개 계약·반환과 readonly 헤더를 보존하며 다른 함수 분기 혼용·계약 누락·Save 전 경합을 거절한다')

def check_caller_final_cas(review,ids):
 before=checkpoint();change_header(caller_source+b' ')
 try:result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert result['sourceConfirmed'] is False,result
 finally:change_header(caller_source)
 assert checkpoint()==before;original();f.stop();f.start(96);assert read()['diagnostics']['state']=='source-ready';f.checked('Review 뒤 호출자의 별도 공개 헤더 경합을 최종 CAS에서 거절하고 재시작 입력을 보존한다')

def check_caller_execution_outcomes():
 p=f.project/'Flow.graph.json';saved=p.read_bytes()
 try:
  for branch in ['failure','none']:
   g=json.loads(saved);g['exits']['yes']['executionBranch']=branch;p.write_text(json.dumps(g))
   build('callee-'+branch,result_code,initial_stdout)
 finally:p.write_bytes(saved)
 f.checked('피호출자의 성공·실패·None dispatch와 다음 줄은 호출자 자신의 분기17·반환10 및 원문을 바꾸지 않는다')
