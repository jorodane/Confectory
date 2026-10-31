"""First-save copy: no copied implementation or graph exists before applySlots."""
import copy,json,pathlib,subprocess,sys,uuid
import v536_field_definitions_ui as d
import v666_node_internal_api as x
context=None;branch=None;nested=None
if '--branch' in sys.argv:
 import v666_node_internal_branch_fixture as branch
elif '--nested' in sys.argv:
 import v666_node_internal_nested_fixture as nested
if '--context' in sys.argv:
 import v666_node_internal_context_fixture as context
f=x.f;feature=x.feature;owner=d.owner;module=f.n+'M11Rules';node='calculate'
if '--raw-copy' in sys.argv:
 assert context is not None
 (f.project/'FlowBody.celem').write_text(context.original_impl);node='body'
source=branch.source if branch else context.source if context else x.record['source']
helpers=branch.helpers if branch else x.record.get('helpers','')
frame_path=branch.frame if branch else nested.path if nested else ''
node_key=(frame_path+'/' if frame_path else '')+node
def at(graph):
 for name in frame_path.split('/') if frame_path else []:graph=next(r for r in graph['nodes'] if r['id']==name)['graph']
 return graph
call_signature=branch.declaration(branch.args,branch.result,False) if branch else context.declaration(context.public_args,False) if context else '(long) -> long'
if '--legacy' in sys.argv:
 document=copy.deepcopy(x.g);document['profile']='sync-acyclic-ref-v1';defs=f.metadata('featureBlueprintNodes',featureSource=x.function,graph=document)
 record=copy.deepcopy(x.record);record['helpers']='';record['source']='return amount+4;';record['definitionHash']=next(r['definitionHash'] for r in defs['nodes'] if r['id']==node)
 (f.project/'Flow.graph.json').write_text(json.dumps(document));(f.project/'Flow.node.json').write_text(json.dumps(record));source=record['source']
info=f.project/'FreeInfo.celem';info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+module+';',1))
(f.project/'M11Rules.celem').write_text('module '+module+' {require '+feature+' '+call_signature+';default '+feature+' with '+x.impl+';}')
manifest=x.manifest;f.manifest=manifest
manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element M11Rules module "M11Rules.celem";registry Confectory.Build.DotNet',1))
old_main=(f.project/'Main.csbody').read_text().replace('return 7;','') if context or branch else 'System.Console.WriteLine(calls.Flow.Invoke(3));'
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow '+call_signature+' in '+owner+';import '+feature+' as DonorFlow '+call_signature+';body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('{'+old_main+'}{'+old_main.replace('calls.Flow.','calls.DonorFlow.')+'}return 7;')
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};x.physical=physical;f.original={str(p.relative_to(f.project)):v for p,v in physical.items()}
def set_copy(id):
 global impl,root,parent,child,leaf
 impl=id;root=impl+'/body:common';parent=root+''.join('/graph:'+p for p in frame_path.split('/') if p);child=parent+'/graph:'+node;leaf=root+'/node:'+node_key.replace('/','/node:')+'/node:body'
set_copy(f.n+'M11PendingCopy')
def unchanged():assert all(p.read_bytes()==v for p,v in physical.items())
def schema():return f.invoke('schema',{'id':owner})['state']['schema']
def rpc(action,ok=True,**kw):
 reply,state=x.any_invoke('blueprint',{'action':action,**kw})
 if bool(reply.get('ok')) is not ok:(f.case/('failed-'+action+'.json')).write_text(json.dumps({'reply':reply,'state':state},ensure_ascii=False,indent=2))
 assert bool(reply.get('ok')) is ok,reply
 return reply.get('result')
def selection(flow=None,privatePath=''):
 s=schema();return rpc('readImplementationCopy',id=owner,function=feature,source=x.impl,target='common',implementation=impl,revision=s['revision'],hash=s['textHash'],privatePath=privatePath,**({'internalFlow':flow} if flow else {}))
def proposal():
 plan={'node':node_key,'nonce':uuid.uuid4().hex};preview=selection(plan,node_key);plan['binding']=preview['preview']['copyNodeFlowBinding'];return preview,plan
def copy_row(prepared,plan):return {'function':feature,'implementation':impl,'copySource':x.impl,'copyTarget':'common','basis':prepared['basis'],'fingerprint':prepared['fingerprint'],'edits':[{'type':'internal-flow','node':node_key,'text':json.dumps(plan,ensure_ascii=False)}]}
def read(id=None):
 s=schema();return rpc('read',id=id or root,owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision'])
def changes():return {r['id']:r for r in json.loads(next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes']}
def edited(increment=1):
 if branch:return source.replace('EditDelta()','(EditDelta()+'+str(increment)+')')
 return source.replace('+proof','+proof+'+str(increment)) if context else source.replace(' + 1',' + '+str(1+increment))
def expected_for(increment=0):
 if not branch:return context.expected if context else '7'
 if branch.refs:return str(42+increment)+'\n'+str(42+increment)+'\n12,16,'+str(26+increment)
 return '\n'.join(str(mode)+':42,'+str(mode+i+increment)+':'+','.join(map(str,[i,i if mode==17 else 0,i if mode==99 else 0,i])) for mode in [-2,17,99] for i in [1,2])
expected=expected_for();donor_expected={'portable':expected}
def build(label,increment=0,target='portable'):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),target],capture_output=True,text=True,env=f.env);(f.case/(label+'-build.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout[-2000:]+p.stderr[-2000:]
 r=subprocess.run(json.loads(p.stdout)['run'],capture_output=True,text=True,env=f.env);(f.case/(label+'-run.json')).write_text(json.dumps({'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}));assert r.returncode==7,(r.returncode,r.stderr)
 rows=r.stdout.strip().splitlines();count=len(expected.splitlines());assert len(rows)==2*count,rows
 wanted=expected_for(increment) if branch else '\n'.join(str(int(line.split(',')[0])+increment)+(','+line.split(',',1)[1] if ',' in line else '') for line in expected.splitlines());assert '\n'.join(rows[:count])==wanted,(rows,wanted)
 donor='\n'.join(rows[count:]);donor_expected.setdefault(target,donor);assert donor==donor_expected[target],(donor,donor_expected[target]);return r.stdout
