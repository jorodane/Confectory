"""M12 keeps existing native IInvoke and legacy NoBranch consumers unchanged."""
import copy,json,re,stat
import v666_root_execution_fixture as base
f=base.f
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller
root=base.root;function=base.function;manifest=base.manifest;edge=base.edge
observer_mode=True;data_mode=True;out_mode=True;result_code=10;expected_review_members=17
conflict_file='After.node.json'
audit=f.n+'Audit';audit_impl=f.n+'AuditBody';audit_graph=audit_impl+'/body:common';scope=f.n+'AuditScope'
legacy=f.n+'Legacy';legacy_impl=f.n+'LegacyBody';legacy_graph=legacy_impl+'/body:common';driver=f.n+'Driver'
audit_function='function '+audit+' (long amount) -> int {provide '+audit+' with '+audit_impl+';}'
audit_implementation='implementation '+audit_impl+' for '+audit+' (long amount) -> int {import '+feature+' as Flow (long,out int) -> void in '+scope+';body common "audit original.csbody";}'
audit_source='// 원래 native consumer·CRLF 😀\r\nstring Member([global::System.Runtime.CompilerServices.CallerMemberName] string name="")=>name;\r\nstring File([global::System.Runtime.CompilerServices.CallerFilePath] string path="")=>global::System.IO.Path.GetFileName(path);\r\nif(Member()!="Invoke"||File()!="audit original.csbody")throw new global::System.InvalidOperationException("native source identity changed");\r\ncalls.Flow.Invoke(amount,out int value);\r\nglobal::System.Console.WriteLine("audit:"+value);\r\nreturn value;\r\n'
legacy_function='function '+legacy+' () -> int {provide '+legacy+' with '+legacy_impl+';}'
legacy_implementation='implementation '+legacy_impl+' for '+legacy+' () -> int {import '+feature+' as '+base.alias+' (long,out int) -> void;blueprint common "Legacy.graph.json";}'
legacy_enum={'primary':'next','members':[{'id':'next','name':'Continue','value':0},{'id':'kept','name':'Kept','value':17}]}
legacy_source='// legacy ordinary original outcome stays NoBranch\r\nglobal::System.Console.WriteLine("legacy:"+(int)originalBranch+":"+amount);\r\nreturn Result.Kept;\r\n'
wrapper=f.metadata('blueprintCallWrapper',functionText=function,executionEnum=legacy_enum,source=legacy_source)
post={'mode':'execution-enum','contractHash':wrapper['contractHash'],'source':legacy_source,'helpers':''}
wrapped={'id':'wrapped','kind':'call','control':'switch','intent':'기존 ordinary wrapper','feature':feature,'signature':copy.deepcopy(base.call_sig),'arguments':{'amount':{'constant':3}},'executionEnum':copy.deepcopy(legacy_enum),'postCall':post}
legacy_body={'schema':1,'profile':'sync-acyclic-switch-v1','feature':legacy,'contractHash':f.metadata('blueprintPrepareFeature',id=legacy,text='function '+legacy+' () -> int {}',implementation=legacy_impl,graphPath='Legacy.graph.json',nodePath='unused.node.json')['graph']['contractHash'],'entry':'wrapped','nodes':[wrapped,{'id':'mark','kind':'code','control':'next','branchOwner':'wrapped','intent':'기존 wrapper 분기17','signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'wrapped','output':'result'}},'implementation':'LegacyMark.node.json'}],'edges':[edge('wrapped','exit:return'),edge('wrapped','mark','case:kept'),edge('mark','return:wrapped')],'exits':{'return':{'node':'wrapped','output':'result'}}}
driver_source='int value=calls.Caller.Invoke();int native=calls.NativeAudit.Invoke(2);int wrapped=calls.Legacy.Invoke();global::System.Console.WriteLine("driver:"+value+":"+native+":"+wrapped);return value;'
for name,text in [('Audit.celem',audit_function),('AuditBody.celem',audit_implementation),('audit original.csbody',audit_source),('AuditScope.celem','object '+scope+' {provide '+feature+' with '+impl+';}'),('Legacy.celem',legacy_function),('LegacyBody.celem',legacy_implementation),('Legacy.graph.json',json.dumps(legacy_body)),('Driver.celem','function '+driver+' () -> int {provide '+driver+' with '+f.n+'DriverBody;}'),('DriverBody.celem','implementation '+f.n+'DriverBody for '+driver+' () -> int {import '+f.n+'Main as Caller () -> int;import '+audit+' as NativeAudit (long) -> int;import '+legacy+' as Legacy () -> int;body common "Driver.csbody";}'),('Driver.csbody',driver_source)]:
 (f.project/name).write_bytes(text.encode())
entries='element Audit function "Audit.celem";element AuditBody implementation "AuditBody.celem";element AuditScope object "AuditScope.celem";element Legacy function "Legacy.celem";element LegacyBody implementation "LegacyBody.celem";element Driver function "Driver.celem";element DriverBody implementation "DriverBody.celem";'
manifest.write_text(manifest.read_text().replace('entry '+f.n+'Main;','entry '+driver+';').replace('registry Confectory.Build.DotNet',entries+'registry Confectory.Build.DotNet',1))
manifest.write_text(re.sub(r'element (\w+) \w+ "[^"]+";',lambda m:m.group() if m[1] in {'Main','MainBody','Flow','FlowBody','Audit','AuditBody','AuditScope','Legacy','LegacyBody','Driver','DriverBody'} else '',manifest.read_text()))
lift=f.metadata('blueprintConversion',project=str(manifest),id=audit_impl,text=audit_implementation,target='common',graphPath='Audit.graph.json',nodePath='Audit.node.json');audit_body=lift['graph'];assert audit_body['profile']=='sync-acyclic-implicit-v1';audit_node=audit_body['nodes'][0]['id'];audit_source_id=audit_graph+'/node:'+audit_node
(f.project/'AuditBody.celem').write_text(lift['implementation']);(f.project/'Audit.graph.json').write_text(json.dumps(audit_body))
defs=f.metadata('featureBlueprintNodes',featureSource=audit_function,implementationContext=lift['context'],bodyTarget='common',featureContracts={feature:function},graph=audit_body);assert defs['state']=='node-definitions',defs
audit_record=copy.deepcopy(lift['node']);audit_record['definitionHash']=next(n['definitionHash'] for n in defs['nodes'] if n['id']==audit_node);assert audit_record['source']==audit_source
(f.project/'Audit.node.json').write_text(json.dumps(audit_record,ensure_ascii=False))
defs=f.metadata('featureBlueprintNodes',featureSource=legacy_function,bodyTarget='common',featureContracts={feature:function},graph=legacy_body);assert defs['state']=='node-definitions',defs
(f.project/'LegacyMark.node.json').write_text(json.dumps({'schema':1,'node':'mark','definitionHash':next(n['definitionHash'] for n in defs['nodes'] if n['id']=='mark'),'source':'global::System.Console.WriteLine("wrapped:17:"+value);'}))
readonly=['Audit.celem','AuditScope.celem','audit original.csbody','Legacy.celem']
for name in readonly:(f.project/name).chmod(0o400)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};base.physical=physical
tail='\ncallee:2\naudit:20\ncallee:3\nlegacy:0:3\nwrapped:17:30\ndriver:10:20:30'
initial_stdout=base.initial_stdout+tail;final_stdout=base.final_stdout+tail
original=base.original;read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof
def preserved(record):
 before=copy.deepcopy(audit_record);after=copy.deepcopy(record);before.pop('definitionHash');after.pop('definitionHash');assert after==before
 for name in ['Audit.graph.json','Legacy.graph.json','LegacyMark.node.json','Driver.csbody',*readonly]:
  p=f.project/name;assert p.read_bytes()==physical[p],p
 for name in readonly:assert stat.S_IMODE((f.project/name).stat().st_mode)==0o400
def build(name,code=None,stdout=None):
 base.build(name,result_code if code is None else code,final_stdout if stdout is None else stdout)
 record=json.loads((f.project/'Audit.node.json').read_bytes());preserved(record)
 if 'blueprintExecutionBranches' in (f.project/'Flow.celem').read_text():assert record['definitionHash']!=audit_record['definitionHash']
def plan(data):return base.plan(data)
def request(data,selected=None):return base.request(data,selected or plan(data))
def __getattr__(name):return getattr(base,name)
