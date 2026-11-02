"""New owned copy of an existing registered function, before first registration."""
import copy,json,uuid,types
import v666_root_execution_registered_fixture as r
f=r.f;x=types.SimpleNamespace(**vars(r.x));x.feature=r.feature;owner=r.owner;module=r.module;implementation=f.n+'M12CreatingCopy';graph=implementation+'/body:common'
(f.project/'FreeInfo.celem').write_text('schema '+owner+' {module '+module+';}');m=f.project/'M12Rules.celem';m.write_text(m.read_text().replace(';}',';default '+x.feature+' with '+x.impl+';}'))
caller=json.loads((f.project/'Main.graph.json').read_text());caller['nodes'].append({'id':'failed','kind':'code','control':'next','intent':'기존 실패 분기 소비','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'Failed.node.json','branchOwner':'invoke'});caller['edges'] += [x.edge('invoke','failed','case:failure'),x.edge('failed','return:invoke')]
definitions=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Main.celem').read_text(),graph=caller,featureContracts={x.feature:r.function_file.read_text()});assert definitions['state']=='node-definitions',definitions;(f.project/'Main.graph.json').write_text(json.dumps(caller));(f.project/'Failed.node.json').write_text(json.dumps({'schema':1,'node':'failed','definitionHash':next(n['definitionHash'] for n in definitions['nodes'] if n['id']=='failed'),'source':'global::System.Console.WriteLine("failure");'}))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};physical.update({p:p.read_bytes() for p in r.pack.iterdir()});f.original={str(p.relative_to(f.project)):v for p,v in physical.items() if p.is_relative_to(f.project)};source_file=r.function_file
mutate_source=r.mutate_parent
restore_source=r.restore_parent
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def retained():assert all(p.read_bytes()==v for p,v in physical.items() if p.name not in ['FreeInfo.celem','project.cproj']);assert all(p.stat().st_mode==v for p,v in r.modes.items())
def binding():
 s=f.invoke('schema',{'id':owner})['state']['schema'];return {'revision':s['revision'],'hash':s['textHash']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':owner,**kw},ok)['result'].get('result')
def selection():return rpc('readImplementationCopy',function=x.feature,source=x.impl,target='common',implementation=implementation,**binding())
def row(selected,branch='failure'):
 d=selected['preview'];exits={r['name']:json.loads(r['valueJson']) for r in d['exits']};exits['yes']={'executionBranch':branch}
 return {'function':x.feature,'implementation':implementation,'copySource':x.impl,'copyTarget':'common','basis':selected['basis'],'fingerprint':selected['fingerprint'],'edits':[{'type':'branch-exits','node':'$branches','text':json.dumps({'entry':d['entry'],'edges':copy.deepcopy(d['edges']),'exits':exits})}]}
def read():
 b=binding();return rpc('read',id=graph,owner=owner,ownerHash=b['hash'],ownerRevision=b['revision'])
def checkpoint():return x.checkpoint()
def confirm(ids):
 review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not review['state']['review'].get('errors');return f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result']
def build(label,branch=None):x.build(label,stdout='callee:1' if branch is None or branch=='success' else 'callee:1\n'+('failure\n' if branch=='failure' else '')+'after:10')
