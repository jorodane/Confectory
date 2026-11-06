"""Existing value input and three outs: moving only return display position preserves the ABI."""
import copy,json
import v666_export_binding_recovery_fixture as base
x=base.x;f=x.f;n=f.n
feature=base.feature;graph=base.graph;graph_file=base.graph_file;source_file=base.source_file;names=['left','middle','right'];original_order=['left','middle','right','return'];selected=['left','return','middle','right'];late_order=['return','left','middle','right']
args=[dict(name='amount',type='int'),*[dict(name=name,type='int',mode='out')for name in names]]
sig='(int amount,out int left,out int middle,out int right)';function='function '+feature+' '+sig+' -> int {provide '+feature+' with '+n+'PairBody;}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+sig+' -> int {}',implementation=n+'PairBody',graphPath=graph_file,nodePath=source_file)
definition=dict(schema=1,profile='sync-acyclic-implicit-out-v1',feature=feature,contractHash=prepared['graph']['contractHash'],entry='body',nodes=[dict(id='body',kind='code',control='next',intent='기존 C# 본문',signature=dict(args=[dict(name='amount',type='int')],**{'return':'int'}),arguments=dict(amount={'input':'amount'}),implementation=source_file)],edges=[],exits={**{name:None for name in names},'return':{'node':'body','output':'return'}},outputOrder=original_order)
previous='body'
for identifier,name,value in zip(['publish','keep','third'],names,[17,23,29]):
 definition['nodes'].append(dict(id=identifier,kind='export',control='next',intent='기존 출력 발행',output=name,signature=dict(args=[dict(name='value',type='int')],**{'return':'void'}),arguments=dict(value={'constant':value})));definition['edges'].append(dict(**{'from':previous,'port':'next','to':identifier}));previous=identifier
definition['edges'].append(dict(**{'from':previous,'port':'next','to':'exit:return'}))
base_plan=dict(args=args,returnType='int',remap={arg['name']:arg['name']for arg in args},outputOrder=original_order)
normalized=f.metadata('blueprintRootContract',functionText=function,text=prepared['implementation'],bodyTarget='common',graph=definition,plan=base_plan);function=normalized['function'];implementation=normalized['implementation'];definition=normalized['graph']
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=definition);assert defs['state']=='node-definitions';original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("body");\r\nreturn checked(amount+3);\r\n'
for filename,text in {'Pair.celem':function,'PairBody.celem':implementation,graph_file:json.dumps(definition,ensure_ascii=False),source_file:json.dumps(dict(schema=1,node='body',definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']=='body'),source=original_source),ensure_ascii=False),'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as Pair (int,out int,out int,out int) -> int;body common "Main.csbody";}','Main.csbody':'int result=calls.Pair.Invoke(7,out int left,out int middle,out int right);global::System.Console.WriteLine(left+":"+middle+":"+right+":"+result);return result;'}.items():(f.project/filename).write_text(text)
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def read():return base.read()
def current():return read()['outputOrder']
def plan(order):return dict(args=copy.deepcopy(args),returnType='int',remap={arg['name']:arg['name']for arg in args},outputOrder=copy.deepcopy(order))
def after(order):v=copy.deepcopy(definition);v['outputOrder']=copy.deepcopy(order);return dict(graph=v,function=function,implementation=implementation)
expected=(10,'body\n17:23:29:10')
