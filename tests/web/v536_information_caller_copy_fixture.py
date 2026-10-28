"""The edited information function is called by a copy assigned to another owner."""
import copy,json
from pathlib import Path
import v536_information_context_fixture as c
f,d,n,owner,fn,caller,mode=c.f,c.d,c.n,c.owner,c.fn,c.caller,c.mode
old=copy.deepcopy(c.old);new=copy.deepcopy(old);new['args'][0]['name']='renamed';remap={'amount':'renamed','count':'count'}
donor_impl=caller+'Body';donor_id=donor_impl+'/body:common';donor_path='CallerBody.celem';donor_body_path='whole-caller.csbody'
(f.project/donor_path).write_text(c.cpp);(f.project/donor_body_path).write_bytes(c.original_caller.encode())
copy_owner=f.n+'CallerHost';copy_id=f.n+'CallerOwnedCopy'
for local,kind,text in [('CallerRules','module','module '+f.n+'CallerRules {require '+caller+' (long,long) -> long;}'),('CallerHost','object','object '+copy_owner+' {module '+f.n+'CallerRules;}')]:
    (f.project/(local+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' '+kind+' "'+local+'.celem";registry Confectory.Build.DotNet',1))
prepared=f.metadata('implementationCopy',project=str(f.manifest),action='prepare',feature=caller,source=donor_impl,target='common',implementation=copy_id,owner=copy_owner,ownerText=(f.project/'CallerHost.celem').read_text())
(f.project/'CallerOwnedCopy.celem').write_text(prepared['implementation']);(f.project/'CallerHost.celem').write_text(prepared['owner']);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element CallerOwnedCopy implementation "CallerOwnedCopy.celem";registry Confectory.Build.DotNet',1))
graph_path=prepared['graphPath'];(f.project/graph_path).parent.mkdir(parents=True,exist_ok=True);(f.project/graph_path).write_text(json.dumps(prepared['graph']))
for record in prepared['records']:
    path=f.project/Path(graph_path).parent/record['relative'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record['record']))
graph_id=copy_id+'/body:common';body_id=graph_id+'/node:'+prepared['records'][0]['id'];body_path=str(Path(graph_path).parent/prepared['records'][0]['relative']);edited=c.original_caller+'// 소유 호출자 copy · 원본 바이트 보존\r\n'
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def selections(preview):
    code=preview['functionBodies'][body_id];donor=preview['functionBodies'][donor_id];callee=preview['functionBodies'][c.body_id]
    assert code['sourceKind']=='whole-caller-csharp' and code['copyOwner']==copy_owner
    return {'before':old,'args':remap,'copies':copy.deepcopy(preview['functionCopies']),'bodies':{
        body_id:{k:code[k] for k in ['hash','path','whole']}|{'beforeSignature':code['signature'],'signature':code['signature'],'contract':new,'text':edited},
        donor_id:{k:donor[k] for k in ['hash','path']}|{'beforeSignature':donor['signature'],'signature':donor['signature'],'contract':new,'text':c.original_caller},
        c.body_id:{k:callee[k] for k in ['hash','path','whole']}|{'beforeSignature':callee['signature'],'signature':callee['signature'],'contract':new,'text':c.b.base.original}}}
def request():
    r=n.request(new,remap);preview={key:f.metadata(op,project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,function=fn,includeBlueprintTargets=True,units=r['units']) for key,op in [('functionBodies','informationFunctionBodies'),('functionCopies','informationFunctionCopies')]};r['changes'][0]['mapping']=selections(preview);return r
def unchanged():assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())
def verify(checkpoint):
    rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert json.loads(rows[body_id]['draft'])['source']==edited;assert json.loads(rows[graph_id]['draft'])['copySource']==prepared['graph']['copySource'];assert (f.project/donor_path).read_bytes()==snapshot[donor_path] and (f.project/donor_body_path).read_bytes()==snapshot[donor_body_path];unchanged();return rows[owner]['atomicEditGroup']
