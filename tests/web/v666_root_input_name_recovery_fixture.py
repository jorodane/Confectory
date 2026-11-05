"""One ordinary root input name: positional ABI and original body/caller bytes stay fixed."""
import copy,json
import v666_export_binding_recovery_fixture as base
x=base.x;f=x.f;n=f.n
feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file
original_name='amount';selected='units';late_name='quantity'
function='function '+feature+' (int amount) -> int {provide '+feature+' with '+n+'PairBody;}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' (int amount) -> int {}',implementation=n+'PairBody',graphPath=graph_file,nodePath=source_file)
definition=prepared['graph'];definition['outputOrder']=['return']
base_plan=dict(args=[dict(name=original_name,type='int')],returnType='int',remap={original_name:original_name},outputOrder=['return'])
normalized=f.metadata('blueprintRootContract',functionText=function,text=prepared['implementation'],bodyTarget='common',graph=definition,plan=base_plan)
function=normalized['function'];implementation=normalized['implementation'];definition=normalized['graph']
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=definition);assert defs['state']=='node-definitions',defs
original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("body");\r\nreturn checked(amount+3);\r\n'
for filename,text in {'Pair.celem':function,'PairBody.celem':implementation,graph_file:json.dumps(definition,ensure_ascii=False),source_file:json.dumps(dict(schema=1,node='body',definitionHash=next(row['definitionHash']for row in defs['nodes']if row['id']=='body'),source=original_source),ensure_ascii=False),'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as Pair (int) -> int;body common "Main.csbody";}','Main.csbody':'int result=calls.Pair.Invoke(7);global::System.Console.WriteLine(result);return result;'}.items():(f.project/filename).write_text(text)
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return read()['signature']['args'][0]['name']
def plan(name,before=original_name):return dict(args=[dict(name=name,type='int')],returnType='int',remap={before:name},outputOrder=['return'])
def after(name):return f.metadata('blueprintRootContract',functionText=function,text=implementation,bodyTarget='common',graph=copy.deepcopy(definition),plan=plan(name))
expected=(10,'body\n10')
