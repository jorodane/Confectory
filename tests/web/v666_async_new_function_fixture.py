"""A new directly owned global function, created only through existing APIs."""
import hashlib,json,pathlib,re,shutil,subprocess,uuid
import v536_wide_mixed as f
feature=f.n+'FreshAsync';graph=None;impl=None;node='body';paths={}
(f.project/'Main.csbody').write_bytes('// 원래 진입 😀\r\nreturn 7;\r\n'.encode())
physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts}
new_source='// 새 기능의 명시 코드 😀\nawait global::System.Threading.Tasks.Task.Yield();\nglobal::System.Console.WriteLine("fresh");\nreturn 11;\n'
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def unchanged():assert all(p.read_bytes()==v for p,v in physical.items()if p.name!='project.cproj')
def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def units():return json.loads(next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes']
def draft_unit():return next(u for u in units()if u["id"]==graph+"/node:body")
def path():return paths[graph+"/node:body"]
def rpc(action,success=True,**body):return f.invoke('blueprint',{'action':action,**body},success)['result'].get('result')
def read():return rpc('read',id=graph)
def proof(d):return json.dumps(sorted([[r['id'],r['revision'],r['hash']]for r in d['sources']]),separators=(',',':'))
def request(d,enabled=True,body=True):return dict(id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=[dict(action='asyncTransition',node='$root',definition=dict(enabled=enabled,nodes=[dict(node=node,enabled=body)]))])
def create():
 global graph,impl,paths
 f.invoke('createDeclaration',dict(id=feature,kind='function'));s=f.invoke('inspectDeclaration',dict(id=feature))['state']['declaration'];preview=rpc('readFeature',id=feature,hash=s['textHash'],revision=s['revision']);created=rpc('createFeature',id=feature,basis=preview['basis']);graph=created['id'];impl=graph.split('/body:')[0];f.invoke('saveDraft',{});paths={u['id']:f.project/u['path']for u in units()if u['id']in [feature,impl,graph,graph+'/node:body']};assert len(paths)==4 and not any(p.exists()for p in paths.values());return created

def run(project,name,expected,stdout):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(project/'project.cproj'),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout[-5000:]+r.stderr
 v=subprocess.run(json.loads(r.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=v.returncode,stdout=v.stdout,stderr=v.stderr)));assert(v.returncode,v.stdout.strip())==(expected,stdout),(v.returncode,v.stdout,v.stderr)
def build_new(name):
 destination=f.case/name;shutil.copytree(f.project,destination,ignore=shutil.ignore_patterns('.confectory'));p=destination/'project.cproj';p.write_text(re.sub(r'entry\s+[^;]+;','entry '+feature+';',p.read_text(),count=1));run(destination,name,11,'fresh')
