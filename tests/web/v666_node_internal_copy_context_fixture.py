"""기존 native copy의 whole-body context를 실제 소유 copy와 donor에서 각각 실행한다."""
import copy,json,pathlib,subprocess,sys,uuid
import v536_field_definitions_ui as d
import v666_node_internal_context_fixture as base
x=base.x;f=base.f;feature=base.feature;owner=d.owner;module=f.n+'M11Rules'
implementation_id=f.n+'M11OwnedCopy';implementation_file='M11Copy.celem'
raw='--raw-copy' in sys.argv;node='body' if raw else 'calculate'
for name in ['refs','void','args','public_args','signature','source','other_target','function','expected']:
 globals()[name]=getattr(base,name)
if raw:(f.project/'FlowBody.celem').write_text(base.original_impl)
call_signature=base.declaration(public_args,False);info=f.project/'FreeInfo.celem'
(f.project/'M11Rules.celem').write_text('module '+module+' {require '+feature+' '+call_signature+';}')
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+module+';',1))
f.manifest=base.manifest;manifest=f.manifest
manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element M11Rules module "M11Rules.celem";registry Confectory.Build.DotNet',1))
prepared=f.metadata('implementationCopy',project=str(manifest),action='prepare',feature=feature,source=x.impl,target='common',implementation=implementation_id,owner=owner,ownerText=info.read_text())
(f.project/implementation_file).write_text(prepared['implementation']);info.write_text(prepared['owner'])
manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element M11OwnedCopy implementation "M11Copy.celem";registry Confectory.Build.DotNet',1))
graph_file=prepared['graphPath'];graph=copy.deepcopy(prepared['graph']);(f.project/graph_file).parent.mkdir(parents=True,exist_ok=True);(f.project/graph_file).write_text(json.dumps(graph,ensure_ascii=False))
for row in prepared['records']:
 file=f.project/pathlib.Path(graph_file).parent/row['relative'];file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps(row['record'],ensure_ascii=False))
context=copy.deepcopy(next(r for r in graph['nodes'] if r['id']==node)['implementationContext'])
assert context['implementation']==implementation_id and context['imports']['Scoped']['scope']==f.n+'ChosenScope'
assert next(r for r in graph['nodes'] if r['id']==node)['sourceIdentity'].endswith('whole original.csbody')
implementation=prepared['implementation'];root=implementation_id+'/body:common';parent=root;child=root+'/graph:'+node;leaf=root+'/node:'+node+'/node:body'
guard=f.project/pathlib.Path(graph_file).parent/next(r['relative'] for r in prepared['records'] if r['id']==node)
old_main=(f.project/'Main.csbody').read_text().replace('return 7;','')
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow '+call_signature+' in '+owner+';import '+feature+' as DonorFlow '+call_signature+';body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('{'+old_main+'}{'+old_main.replace('calls.Flow.','calls.DonorFlow.')+'}return 7;')
if '--shared' in sys.argv:
 p=f.project/'Vitals.celem';p.write_text(p.read_text().replace('Vitals {','Vitals {module '+module+';provide '+feature+' with '+implementation_id+';',1))
x.physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
f.original={str(p.relative_to(f.project)):v for p,v in x.physical.items()}
def original():assert all(p.read_bytes()==v for p,v in x.physical.items())
def owner_binding():
 schema=f.invoke('schema',{'id':owner})['state']['schema'];return {'owner':owner,'ownerHash':schema['textHash'],'ownerRevision':schema['revision']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':root,**owner_binding(),**kw},ok)['result'].get('result')
def read(id=root):return rpc('read',id=id)
def request(data,nonce=None,text=None):
 row=next(r for r in data['nodes'] if r['id']==node);source_row=next(r for r in data['sources'] if r['id']==row['sourceId'])
 return {'id':root,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':x.proof(data),'edits':[{'action':'internalizeNode','node':node,'definition':{'nonce':nonce or uuid.uuid4().hex,'binding':{'graph':root,'root':root,'node':node,'source':row['sourceId'],'definitionHash':row['definitionHash'],'sourceHash':source_row['hash']},**({'source':text} if text is not None else {})}}]}
def source_path(row):return f.project/pathlib.Path(graph_file).parent/row['implementation']
donor_expected={'portable':expected}
def build(name,increment=0,target='portable'):
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),target],capture_output=True,text=True,env=f.env)
 (f.case/(name+'-build.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout[-3000:]+result.stderr[-3000:]
 done=subprocess.run(json.loads(result.stdout)['run'],capture_output=True,text=True,env=f.env);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':done.returncode,'stdout':done.stdout,'stderr':done.stderr}));assert done.returncode==7,(done.returncode,done.stderr)
 rows=done.stdout.strip().splitlines();count=len(expected.splitlines());assert len(rows)==count*2,rows
 wanted='\n'.join(str(int(row.split(',')[0])+increment)+','+row.split(',',1)[1] for row in expected.splitlines());assert '\n'.join(rows[:count])==wanted,(done.stdout,wanted)
 donor='\n'.join(rows[count:])
 if target not in donor_expected:donor_expected[target]=donor
 assert donor==donor_expected[target],(donor,donor_expected[target]);return done.stdout
