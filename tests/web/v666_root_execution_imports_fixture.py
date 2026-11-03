"""Public definition updates observe registered native-import/scope headers only."""
import copy,json,pathlib,stat
import v666_root_execution_observers_fixture as x
f=x.f
pack=f.case/'registered readonly import';pack.mkdir()
foreign='External.Observed::Value';provider='External.Observed::ValueBody';scope='External.Observed::Scope'
files={'Value.celem':'function '+foreign+' () -> int {}','ValueBody.celem':'implementation '+provider+' for '+foreign+' () -> int {body common "Value.csbody";}','Rules.celem':'module External.Observed::Rules {include External.Observed::BaseRules;require '+foreign+' () -> int;}','BaseRules.celem':'module External.Observed::BaseRules {}','Scope.celem':'object '+scope+' {module External.Observed::Rules;provide '+foreign+' with '+provider+';}','Value.csbody':'return 7;','pack.cpack':'pack External.Observed version "1" {element Value function "Value.celem";element ValueBody implementation "ValueBody.celem";element Scope object "Scope.celem";element Rules module "Rules.celem";element BaseRules module "BaseRules.celem";}'}
for name,text in files.items():(pack/name).write_bytes((text+'\r\n').encode() if name=='Value.celem' else text.encode())
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','dependency External.Observed version "1";registry External.Observed "'+str(pack/'pack.cpack')+'";registry Confectory.Build.DotNet',1))
p=f.project/'AuditBody.celem';implementation=p.read_text().replace('blueprint common','import '+foreign+' as Observed () -> int in '+scope+';blueprint common');p.write_text(implementation)
# Insert before the existing native return, keeping CRLF and source identity.
x.audit_source=x.audit_source.replace('return value;','if(calls.Observed.Invoke()!=7)throw new global::System.InvalidOperationException("registered scope lost");\r\nreturn value;')
p=f.project/'audit original.csbody';p.chmod(0o600);p.write_bytes(x.audit_source.encode());p.chmod(0o400)
# Use actual conversion to retain the native source/context contract exactly.
native=implementation.replace('blueprint common "Audit.graph.json";','body common "audit original.csbody";')
(f.project/'AuditBody.celem').write_text(native)
lift=f.metadata('blueprintConversion',project=str(x.manifest),id=x.audit_impl,text=native,target='common',graphPath='Audit.graph.json',nodePath='Audit.node.json')
(f.project/'AuditBody.celem').write_text(lift['implementation']);(f.project/'Audit.graph.json').write_text(json.dumps(lift['graph']))
d=f.metadata('featureBlueprintNodes',featureSource=x.audit_function,implementationContext=lift['context'],bodyTarget='common',featureContracts={x.feature:x.function,foreign:files['Value.celem']},graph=lift['graph']);assert d['state']=='node-definitions',d
x.audit_record=copy.deepcopy(lift['node']);x.audit_record['definitionHash']=next(n['definitionHash'] for n in d['nodes'] if n['id']==x.audit_node);assert x.audit_record['source']==x.audit_source
(f.project/'Audit.node.json').write_text(json.dumps(x.audit_record,ensure_ascii=False))
for p in pack.iterdir():p.chmod(0o440)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};physical.update({p:p.read_bytes() for p in pack.iterdir()});x.physical=physical;x.base.physical=physical
modes={p:p.stat().st_mode for p in pack.iterdir()}
def request(data,plan=None):
 req=x.request(data,plan);req['dependencyHash']=data['rootExecutionDependencyHash'];return req
read=x.read;rpc=x.rpc;checkpoint=x.checkpoint;original=x.original;build=x.build;plan=x.plan

def mutate(path,suffix=b' '):
 path.chmod(0o640)
 try:path.write_bytes(physical[path]+suffix)
 finally:path.chmod(modes[path])
def restore(path):
 path.chmod(0o640)
 try:path.write_bytes(physical[path])
 finally:path.chmod(modes[path])
def retained():
 x.preserved(json.loads((f.project/'Audit.node.json').read_text()));assert all(p.read_bytes()==v for p,v in physical.items() if p.parent==pack);assert all(p.stat().st_mode==v for p,v in modes.items())
def __getattr__(name):return getattr(x,name)
