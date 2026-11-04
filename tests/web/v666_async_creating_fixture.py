"""An existing owned async root; the next ordinary leaf has no physical source yet."""
import copy,hashlib,json,subprocess,uuid
import v536_wide_mixed as f
feature=f.n+'Main';impl=f.n+'MainBody';graph=impl+'/body:common';node='fresh';source_id=lambda n:graph+'/node:'+n
metadata=json.dumps(json.dumps({'schema':1,'completion':'main_complete'},separators=(',',':')))
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' () -> int {description "원래 함수 설명";value blueprintAsync = '+metadata+';}',implementation=impl,graphPath='Main.graph.json',nodePath='Main.node.json');root=prepared['graph'];root['nodes'][0].pop('async',None)
original_source='// 기존 본문 😀\r\nglobal::System.Console.WriteLine("after");\r\nreturn 7;\r\n'
defs=f.metadata('featureBlueprintNodes',featureSource=prepared['function'],graph=root);record={'schema':1,'node':'body','definitionHash':defs['nodes'][0]['definitionHash'],'source':original_source}
for name,text in [('Main.celem',prepared['function']),('MainBody.celem',prepared['implementation']),('Main.graph.json',json.dumps(root)),('Main.node.json',json.dumps(record,ensure_ascii=False))]:(f.project/name).write_text(text)
physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts};initial=copy.deepcopy(root)
new_source='// 새 본문도 사용자가 명시적으로 작성한다 😀\nawait global::System.Threading.Tasks.Task.Yield();\nglobal::System.Console.WriteLine("work");\n'
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def unchanged():
 for p,v in physical.items():
  if p.name not in ['Main.graph.json','Main.node.json']:assert p.read_bytes()==v,p
 assert json.loads((f.project/'Main.node.json').read_text())['source']==original_source

def read():return f.invoke('blueprint',{'action':'read','id':graph})['result']['result']
def proof(d):return json.dumps(sorted([[r['id'],r['revision'],r['hash']]for r in d['sources']]),separators=(',',':'))
def rpc(action,success=True,**body):return f.invoke('blueprint',{'action':action,**body},success)['result'].get('result')
def request(d,edits):return dict(id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=edits)
def transition(d,enabled=True):return request(d,[dict(action='asyncTransition',node='$root',definition=dict(enabled=True,nodes=[dict(node=node,enabled=enabled)]))])
def create():
 d=read();req=request(d,[dict(action='createNode',node=node,definition=dict(kind='code',control='next',intent='새 비동기 동작',signature=dict(args=[],**{'return':'void'}))),dict(action='route',node=node,port='next',to='body')]);assert rpc('authorBatch',**req)['settled'];d=read();rpc('entry',id=graph,node=node,basis=d['basis']);f.invoke('saveDraft',{});return req

def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def draft_unit():
 s=json.loads(next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_text());return next(u for u in s['changes']if u['id']==source_id(node))
new_path=None
def path():
 global new_path
 if new_path is None:new_path=f.project/draft_unit()['path']
 return new_path
def build(name,created=False):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.project/'project.cproj'),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout[-4000:]+r.stderr
 result=subprocess.run(json.loads(r.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=result.returncode,stdout=result.stdout,stderr=result.stderr)));assert(result.returncode,result.stdout.strip())==(7,'work\nafter'if created else'after'),(result.returncode,result.stdout,result.stderr)
