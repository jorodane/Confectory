"""Real copy preparation, saved owned copy and unchanged native donor files."""
import copy,json
from pathlib import Path
import v536_information_whole_body_fixture as b
f,d,n,owner,fn,caller,mode=b.f,b.d,b.n,b.owner,b.fn,b.caller,b.mode
old=copy.deepcopy(b.old);new=copy.deepcopy(old);new['args'][0]['name']='renamed'
remap={'amount':'renamed','count':'count'}
original=b.original;selected=b.native
# Keep the donor as the native body which the user explicitly copies.
b.implementation_file.write_text(b.cpp)
copy_id=f.n+'OwnedCopy'
prepared=f.metadata('implementationCopy',project=str(f.manifest),action='prepare',feature=fn,source=fn+'Body',target='common',implementation=copy_id,owner=owner,ownerText=b.info.read_text())
copy_path='OwnedCopy.celem';(f.project/copy_path).write_text(prepared['implementation'])
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element OwnedCopy implementation "'+copy_path+'";registry Confectory.Build.DotNet',1))
graph_path=prepared['graphPath'];(f.project/graph_path).parent.mkdir(parents=True,exist_ok=True);(f.project/graph_path).write_text(json.dumps(prepared['graph']))
for row in prepared['records']:
    path=f.project/Path(graph_path).parent/row['relative'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(row['record']))
b.info.write_text(prepared['owner'])
graph_id=copy_id+'/body:common';body_id=graph_id+'/node:'+prepared['records'][0]['id'];body_path=str(Path(graph_path).parent/prepared['records'][0]['relative'])
donor_id=fn+'Body/body:common'
donor_impl=fn+'Body';donor_path=b.implementation_path;donor_body_path='whole-original.csbody';copy_owner=owner
edited=original.replace('원래 별칭','소유 복사본 직접 편집')
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
    row=preview['functionBodies'][body_id];donor=preview['functionBodies'][donor_id]
    assert row['sourceKind']=='whole-graph-csharp' and donor['sourceKind']=='csharp'
    native=copy.deepcopy(selected)
    return {'before':old,'args':remap,'copies':copy.deepcopy(preview['functionCopies']),'bodies':{
        body_id:{k:row[k] for k in ['hash','path','whole']}|{'beforeSignature':native,'signature':native,'contract':new,'text':edited,'outputs':{'return':'return','nativeTotal':'nativeTotal'}},
        donor_id:{k:donor[k] for k in ['hash','path']}|{'beforeSignature':native,'signature':native,'contract':new,'text':original}}}

def request():
    r=n.request(new,remap)
    p={key:f.metadata(op,project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,function=fn,includeBlueprintTargets=True,units=r['units']) for key,op in [('functionBodies','informationFunctionBodies'),('functionCopies','informationFunctionCopies')]}
    r['changes'][0]['mapping']=selections(p);return r

def unchanged():assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())

def verify(checkpoint):
    rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[body_id]['draft'])['source']==edited
    graph=json.loads(rows[graph_id]['draft']);assert graph['copySource']==prepared['graph']['copySource']
    assert graph['nodes'][0]['arguments']=={'nativeAmount':{'input':'renamed'}}
    assert (f.project/b.implementation_path).read_bytes()==snapshot[b.implementation_path]
    assert (f.project/'whole-original.csbody').read_bytes()==snapshot['whole-original.csbody']
    unchanged();return rows[owner]['atomicEditGroup']
