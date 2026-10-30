"""M11 stored, singly assigned same-contract copy; optional owned private path, separate donor."""
import copy,json,pathlib,subprocess,uuid,sys
import v536_field_definitions_ui as d
import v666_node_internal_api as x
storage=None
if '--storage-copy' in sys.argv:
 import v666_node_internal_storage_fixture as storage
nested=None
if any(a.startswith('--depth=') for a in sys.argv[3:]):
 import v666_node_internal_nested_fixture as nested
f=x.f;feature=x.feature;owner=d.owner;impl=f.n+'M11OwnedCopy';graph=impl+'/body:common';child=graph+'/graph:calculate';original_id=graph+'/node:calculate';leaf=original_id+'/node:body'
parts=(['frame'] if storage.private else []) if storage else nested.parts if nested else [];path='/'.join(parts);parent=graph+''.join('/graph:'+p for p in parts);child=parent+'/graph:calculate';record_id=(path+'/' if path else '')+'calculate';original_id=graph+'/node:'+record_id.replace('/','/node:');leaf=original_id+'/node:body'
def at(document):
 for part in parts:document=next(r for r in document['nodes'] if r['id']==part)['graph']
 return document
info=f.project/'FreeInfo.celem';module=f.n+'M11Rules'
call_signature='('+storage.callargs+') -> int' if storage else '(long) -> long'
(f.project/'M11Rules.celem').write_text('module '+module+' {require '+feature+' '+call_signature+';}')
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+module+';',1))
f.manifest=x.manifest;f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element M11Rules module "M11Rules.celem";registry Confectory.Build.DotNet',1))
prepared=f.metadata('implementationCopy',project=str(f.manifest),action='prepare',feature=feature,source=x.impl,target='common',implementation=impl,owner=owner,ownerText=info.read_text())
(f.project/'M11Copy.celem').write_text(prepared['implementation']);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element M11OwnedCopy implementation "M11Copy.celem";registry Confectory.Build.DotNet',1));info.write_text(prepared['owner'])
graph_path=prepared['graphPath'];(f.project/graph_path).parent.mkdir(parents=True,exist_ok=True);(f.project/graph_path).write_text(json.dumps(prepared['graph']))
for row in prepared['records']:
 p=f.project/pathlib.Path(graph_path).parent/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(row['record'],ensure_ascii=False))
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow '+call_signature+' in '+owner+';body common "Main.csbody";}')
if '--shared' in sys.argv:
 p=f.project/'Vitals.celem';p.write_text(p.read_text().replace('Vitals {','Vitals {module '+module+';provide '+feature+' with '+impl+';',1))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};f.original={str(p.relative_to(f.project)):v for p,v in physical.items()};x.physical=physical
provenance=copy.deepcopy(prepared['graph']['copySource']);original_record=next(r['record'] for r in prepared['records'] if r['id']==record_id)
guard=f.project/pathlib.Path(graph_path).parent/next(r['relative'] for r in prepared['records'] if r['id']==record_id)
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def binding():
 row=f.invoke('schema',{'id':owner})['state']['schema'];return {'owner':owner,'ownerHash':row['textHash'],'ownerRevision':row['revision']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':parent,**binding(),**kw},ok)['result'].get('result')
def read(id=parent):return rpc('read',id=id)
def request(data,nonce=None,source=None):
 r={'id':parent,**binding(),'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':x.proof(data),'edits':[{'action':'internalizeNode','node':'calculate','definition':{'nonce':nonce or uuid.uuid4().hex,**({'source':source} if source is not None else {})}}]}
 if parts:
  row=next(n for n in data['nodes'] if n['id']=='calculate');observed=next(s for s in data['sources'] if s['id']==row['sourceId']);r['edits'][0]['definition']['binding']={'graph':parent,'root':graph,'node':'calculate','source':row['sourceId'],'definitionHash':row['definitionHash'],'sourceHash':observed['hash']}
 return r
def edit_source(increment=1):
 if storage:return 'return Mutate('+','.join(a['mode']+' '+a['name'] for a in storage.params)+')+'+str(increment)+';'
 return 'return amount+'+str(7+increment)+';'
def build(label,expected=7):
 if storage:return storage.build(label,0 if expected==7 else expected-10)
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],capture_output=True,text=True,env=f.env);(f.case/(label+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout[-3000:]+r.stderr[-3000:];v=subprocess.run(json.loads(r.stdout)['run'],capture_output=True,text=True,env=f.env);assert v.returncode==expected,(v.returncode,v.stdout,v.stderr)
