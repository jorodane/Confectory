"""Root with two outs and a nonvoid return: display order has no ABI permutation."""
import copy,json,types
import v666_export_binding_recovery_fixture as base
x=base.x;f=x.f;n=f.n
feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file;names=['left','right'];original_order=['left','right','return'];selected=['left','return','right'];late_order=['return','left','right']
sig='(out int left,out int right)';function='function '+feature+' '+sig+' -> int {provide '+feature+' with '+n+'PairBody;}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+sig+' -> int {}',implementation=n+'PairBody',graphPath=graph_file,nodePath=source_file)
definition=dict(schema=1,profile='sync-acyclic-implicit-out-v1',feature=feature,contractHash=prepared['graph']['contractHash'],entry='body',nodes=[dict(id='body',kind='code',control='next',intent='기존 C# 본문',signature=dict(args=[],**{'return':'int'}),arguments={},implementation=source_file),dict(id='publish',kind='export',control='next',intent='기존 출력 발행',output='left',signature=dict(args=[dict(name='value',type='int')],**{'return':'void'}),arguments=dict(value={'constant':17}))],edges=[dict(**{'from':'body','port':'next','to':'publish'}),dict(**{'from':'publish','port':'next','to':'exit:return'})],exits={'left':None,'right':None,'return':{'node':'body','output':'return'}},outputOrder=original_order)
right=copy.deepcopy(definition['nodes'][1]);right.update(id='keep',output='right');right['arguments']['value']={'constant':23};definition['nodes'].append(right);definition['edges'][-1]['to']='keep';definition['edges'].append(dict(**{'from':'keep','port':'next','to':'exit:return'}))
base_plan=dict(args=[dict(name=name,type='int',mode='out')for name in names],returnType='int',remap={name:name for name in names},outputOrder=original_order)
normalized=f.metadata('blueprintRootContract',functionText=function,text=prepared['implementation'],bodyTarget='common',graph=definition,plan=base_plan);function=normalized['function'];implementation=normalized['implementation'];definition=normalized['graph']
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=definition);assert defs['state']=='node-definitions';original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("body");\r\nreturn 10;\r\n'
for filename,text in {'Pair.celem':function,'PairBody.celem':implementation,graph_file:json.dumps(definition,ensure_ascii=False),source_file:json.dumps(dict(schema=1,node='body',definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']=='body'),source=original_source),ensure_ascii=False),'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as Pair (out int,out int) -> int;body common "Main.csbody";}','Main.csbody':'int result=calls.Pair.Invoke(out int left,out int right);global::System.Console.WriteLine(left+":"+right+":"+result);return result;'}.items():(f.project/filename).write_text(text)
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return read()['outputOrder']
def plan(order):return dict(args=copy.deepcopy(base_plan['args']),returnType='int',remap={name:name for name in names},outputOrder=copy.deepcopy(order))
def after(order):v=copy.deepcopy(definition);v['outputOrder']=order;return v
expected=(10,'body\n17:23:10')
