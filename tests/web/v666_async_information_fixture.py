"""A contained information-owned function, created only through existing APIs."""
import hashlib,json,pathlib,re,shutil,subprocess,uuid
import v536_field_definitions_ui as d
f=d.f;owner=d.owner
feature=owner+'_Function_'+'b'*32;graph=None;impl=None;node='body';paths={};owner_draft=None
(f.project/'Main.csbody').write_bytes('// 원래 진입 😀\r\nreturn 7;\r\n'.encode())
physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts}
new_source='// 새 기능의 명시 코드 😀\nawait global::System.Threading.Tasks.Task.Yield();\nglobal::System.Console.WriteLine("fresh");\nreturn;\n'
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def unchanged():
 assert all(p.read_bytes()==v for p,v in physical.items()if p.name not in ['project.cproj','FreeInfo.celem']);assert (f.project/'FreeInfo.celem').read_text()==owner_draft
def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def units():return json.loads(next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes']
def draft_unit():return next(u for u in units()if u["id"]==graph+"/node:body")
def path():return paths[graph+"/node:body"]
def owner_proof():
 if f.state().get('workspace',{}).get('unit',{}).get('id')!=owner:f.invoke('select',{'id':owner})
 f.invoke('schema',{'id':owner});s=f.state()['schema'];return dict(owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision'])
def rpc(action,success=True,**body):
 if action in ['read','authorBatch','settledAuthorBatch']:body={**owner_proof(),**body}
 return f.invoke('blueprint',{'action':action,**body},success)['result'].get('result')
def read():return rpc('read',id=graph)
def proof(d):return json.dumps(sorted([[r['id'],r['revision'],r['hash']]for r in d['sources']]),separators=(',',':'))
def request(d,enabled=True,body=True):return dict(id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=[dict(action='asyncTransition',node='$root',definition=dict(enabled=enabled,nodes=[dict(node=node,enabled=body)]))])
def create():
 global graph,impl,paths,owner_draft
 f.invoke('select',{'id':owner});proof=owner_proof();basis=rpc('readOwnerEdits',id=owner,hash=proof['ownerHash']);rpc('applySlots',id=owner,rows=[],basis=basis['basis'],declaration={'id':owner,'hash':proof['ownerHash'],'changes':[{'type':'function-add','id':feature,'name':'정보 비동기','description':'직접 소유 함수'}]});f.invoke('schema',{'id':owner});row=next(v for v in f.state()['schema']['ownFunctions']if v['id']==feature);preview=rpc('readFeature',id=feature,hash=row['hash'],revision=row['revision'],**owner_proof());created=rpc('createFeature',id=feature,basis=preview['basis']);graph=created['id'];impl=graph.split('/body:')[0];f.invoke('saveDraft',{});paths={u['id']:f.project/u['path']for u in units()if u['id']in [feature,impl,graph,graph+'/node:body']};assert len(paths)==4 and not any(p.exists()for p in paths.values());owner_draft=next(u['draft']for u in units()if u['id']==owner);return created

def run(project,name,expected,stdout):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(project/'project.cproj'),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout[-5000:]+r.stderr
 v=subprocess.run(json.loads(r.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=v.returncode,stdout=v.stdout,stderr=v.stderr)));assert(v.returncode,v.stdout.strip())==(expected,stdout),(v.returncode,v.stdout,v.stderr)
def metadata(operation,**request):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation=operation,**request)),text=True,capture_output=True,env=f.env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
def build_new(name):
 destination=f.case/name;shutil.copytree(f.project,destination,ignore=shutil.ignore_patterns('.confectory'));probe=f.n+'ExplicitAsyncProbe';impl=probe+'Body';alias='fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24];meta=json.dumps(json.dumps({'schema':1,'completion':'probe_complete'},separators=(',',':')))
 a=metadata('blueprintPrepareFeature',id=probe,text='function '+probe+' () -> int {value blueprintAsync = '+meta+';}',implementation=impl,graphPath='probe.graph.json',nodePath='probe.node.json');a['graph']['nodes'][0]['imports']=[feature];a['implementation']=a['implementation'].replace('{','{import '+feature+' as '+alias+' () -> void in '+owner+';',1)
 defs=metadata('featureBlueprintNodes',featureSource=a['function'],graph=a['graph'],featureContracts={feature:xtext(destination)});a['node'].update(definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']=='body'),source='await '+alias+'.InvokeAsync();return 11;')
 for filename,value in [('Probe.celem',a['function']),('ProbeBody.celem',a['implementation']),('probe.graph.json',json.dumps(a['graph'])),('probe.node.json',json.dumps(a['node']))]:(destination/filename).write_text(value)
 p=destination/'project.cproj';p.write_text(re.sub(r'entry\s+[^;]+;','entry '+probe+';',p.read_text(),count=1).replace('{','{element ExplicitAsyncProbe function "Probe.celem";element ExplicitAsyncProbeBody implementation "ProbeBody.celem";',1));run(destination,name,11,'fresh')
def xtext(project):return (project/paths[feature].relative_to(f.project)).read_text()
def reject_sync(name):
 destination=f.case/name;shutil.copytree(f.project,destination,ignore=shutil.ignore_patterns('.confectory'));p=destination/'MainBody.celem';p.write_text(p.read_text().replace('{','{import '+feature+' as NewOwn () -> void in '+owner+';',1));(destination/'Main.csbody').write_text('_ = calls.NewOwn.InvokeAsync();return 7;')
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(destination/'project.cproj'),'portable'],text=True,capture_output=True,env=f.env);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode!=0 and 'TARGET_FAILURE'in r.stdout+r.stderr and 'InvokeAsync'in r.stdout+r.stderr,r.stdout+r.stderr
