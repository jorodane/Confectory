"""Void root value-input rename; positional call and original C# bytes remain fixed."""
import copy,json
import v666_root_input_name_recovery_fixture as base
x=base.x;f=base.f;n=f.n;feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file
index=1;original_name='scale';selected='multiplier';late_name='factor'
original_args=[dict(name='amount',type='int'),dict(name=original_name,type='int')]
function='function '+feature+' (int amount,int scale) -> void {provide '+feature+' with '+n+'PairBody;}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' (int amount,int scale) -> void {}',implementation=n+'PairBody',graphPath=graph_file,nodePath=source_file)
definition=prepared['graph'];definition['outputOrder']=[]
base_plan=dict(args=copy.deepcopy(original_args),returnType='void',remap={a['name']:a['name']for a in original_args},outputOrder=[])
normalized=f.metadata('blueprintRootContract',functionText=function,text=prepared['implementation'],bodyTarget='common',graph=definition,plan=base_plan)
function=normalized['function'];implementation=normalized['implementation'];definition=normalized['graph']
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=definition);assert defs['state']=='node-definitions',defs
original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("body");\r\nglobal::System.Console.WriteLine(checked(amount+scale));\r\n'
for filename,text in {'Pair.celem':function,'PairBody.celem':implementation,graph_file:json.dumps(definition,ensure_ascii=False),source_file:json.dumps(dict(schema=1,node='body',definitionHash=next(row['definitionHash']for row in defs['nodes']if row['id']=='body'),source=original_source),ensure_ascii=False),'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as Pair (int,int) -> void;body common "Main.csbody";}','Main.csbody':'calls.Pair.Invoke(7,3);global::System.Console.WriteLine("done");return 0;'}.items():(f.project/filename).write_text(text)
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return read()['signature']['args'][index]['name']
def plan(name,before=original_name):
 args=copy.deepcopy(original_args);args[index]['name']=name;return dict(args=args,returnType='void',remap={'amount':'amount',before:name},outputOrder=[])
def after(name):return f.metadata('blueprintRootContract',functionText=function,text=implementation,bodyTarget='common',graph=copy.deepcopy(definition),plan=plan(name))
expected=(0,'body\n10\ndone')
