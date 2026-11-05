"""Existing serial export and three declared int outputs; no contract editing."""
import json,subprocess,types
import v536_wide_mixed as f
x=types.SimpleNamespace(f=f);n=f.n
feature=n+'Pair';graph=n+'PairBody/body:common';node='publish';graph_file='Pair.graph.json';source_file='Pair.node.json';original_output='left'
signature='(out int left,out int right,out int spare,out bool flag)'
function='function '+feature+' '+signature+' -> void {provide '+feature+' with '+n+'PairBody;}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+signature+' -> void {}',implementation=n+'PairBody',graphPath=graph_file,nodePath=source_file)
definition=dict(schema=1,profile='sync-acyclic-implicit-out-v1',feature=feature,contractHash=prepared['graph']['contractHash'],entry='body',nodes=[dict(id='body',kind='code',control='next',intent='기존 C# 본문',signature=dict(args=[],**{'return':'void'}),arguments={},implementation=source_file),dict(id=node,kind='export',control='next',intent='기존 출력 발행',output=original_output,signature=dict(args=[dict(name='value',type='int')],**{'return':'void'}),arguments=dict(value={'constant':17}))],edges=[dict(**{'from':'body','port':'next','to':node}),dict(**{'from':node,'port':'next','to':'exit:return'})],exits={'return':None})
original_source='// 원문·줄바꿈 보존 😀\r\nglobal::System.Console.WriteLine("body");\r\n'
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=definition);assert defs['state']=='node-definitions',defs
files={'Pair.celem':function,'PairBody.celem':prepared['implementation'],graph_file:json.dumps(definition,ensure_ascii=False),source_file:json.dumps(dict(schema=1,node='body',definitionHash=next(v['definitionHash']for v in defs['nodes']if v['id']=='body'),source=original_source),ensure_ascii=False),'MainBody.celem':'implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as Pair (out int,out int,out int,out bool) -> void;body common "Main.csbody";}','Main.csbody':'calls.Pair.Invoke(out int left,out int right,out int spare,out bool flag);global::System.Console.WriteLine(left+":"+right+":"+spare+":"+flag);return left>0?1:right>0?2:3;'}
for name,text in files.items():(f.project/name).write_text(text)
manifest=f.project/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Pair function "Pair.celem";element PairBody implementation "PairBody.celem";registry Confectory.Build.DotNet',1))
x.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
def original():assert all(p.read_bytes()==value for p,value in x.physical.items())
def read():return f.invoke('blueprint',dict(action='read',id=graph))['result']['result']
def current():return next(v for v in read()['nodes']if v['id']==node)['output']
def proof(data):return json.dumps(sorted([[v['id'],v['revision'],v['hash']]for v in data['sources']]),separators=(',',':'))
def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def build(name,code,stdout):
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout[-4000:]+result.stderr[-1000:];report=json.loads(result.stdout);run=subprocess.run(report['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(code,stdout),(run.returncode,run.stdout,run.stderr)
x.feature=feature;x.graph=graph;x.original=original;x.proof=proof;x.checkpoint=checkpoint;x.build=build
def expected(value):return (1,'body\n17:0:0:False')if value=='left'else(2,'body\n0:17:0:False')if value=='right'else(3,'body\n0:0:17:False')
