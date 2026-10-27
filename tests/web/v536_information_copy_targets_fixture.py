"""Two already explicit copy selections, never an implicit all-target clone."""
import copy,json,hashlib
from pathlib import Path
import v536_information_caller_copy_fixture as first
f,d,n,owner,fn,mode=first.f,first.d,first.n,first.owner,first.fn,first.mode
old,new,remap=first.old,first.new,first.remap
# Extend the fixture donor only. The existing copy operation still selects one target.
p=f.project/first.donor_path;p.write_text(p.read_text().replace('body common "whole-caller.csbody";', 'body common "whole-caller.csbody";body windows "whole-caller-windows.csbody";'))
windows_original=first.c.original_caller+'// windows 원본 · 9223372036854775805\r\n'
(f.project/'whole-caller-windows.csbody').write_bytes(windows_original.encode())
second_owner=f.n+'WindowsHost';second_copy=f.n+'WindowsOwnedCopy'
for local,kind,text in [('WindowsHost','object','object '+second_owner+' {module '+f.n+'CallerRules;}')]:
 (f.project/(local+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' '+kind+' "'+local+'.celem";registry Confectory.Build.DotNet',1))
second=f.metadata('implementationCopy',project=str(f.manifest),action='prepare',feature=first.caller,source=first.donor_impl,target='windows',implementation=second_copy,owner=second_owner,ownerText=(f.project/'WindowsHost.celem').read_text())
(f.project/'WindowsOwnedCopy.celem').write_text(second['implementation']);(f.project/'WindowsHost.celem').write_text(second['owner']);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element WindowsOwnedCopy implementation "WindowsOwnedCopy.celem";registry Confectory.Build.DotNet',1))
(f.project/second['graphPath']).parent.mkdir(parents=True,exist_ok=True);(f.project/second['graphPath']).write_text(json.dumps(second['graph']))
for row in second['records']:
 p=f.project/Path(second['graphPath']).parent/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(row['record']))
second_graph=second_copy+'/body:windows';second_body=second_graph+'/node:'+second['records'][0]['id'];second_path=str(Path(second['graphPath']).parent/second['records'][0]['relative']);second_edited=windows_original+'// windows copy의 명시 본문 · 9223372036854775804\r\n'
body_ids=[first.body_id,second_body];graphs=[first.graph_id,second_graph];copies=[first.copy_id,second_copy];owners=[first.copy_owner,second_owner];donor_windows=first.donor_impl+'/body:windows'
expected_text={first.body_id:first.edited,second_body:second_edited}
# Windows is an explicit fixture review target. Common remains its declared fallback;
# the Windows-only copy is never silently used for a portable/Linux target.
f.manifest.write_text(f.manifest.read_text().replace('target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;', 'target windows Confectory.Build.DotNet::Portable;'))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
guard_baselines={p:hashlib.sha256(value).hexdigest() for p,value in snapshot.items()}
def selections(preview):
 plan=first.selections(preview);plan['copies']=copy.deepcopy(preview['functionCopies'])
 for key,text in [(second_body,second_edited),(donor_windows,windows_original)]:
  row=preview['functionBodies'][key];plan['bodies'][key]={k:row[k] for k in ['hash','path']}|{'beforeSignature':row['signature'],'signature':row['signature'],'contract':new,'text':text}
  if 'whole' in row:plan['bodies'][key]['whole']=copy.deepcopy(row['whole'])
 assert set(plan['copies'])==set(graphs),plan['copies']
 assert [plan['copies'][g]['owner'] for g in graphs]==owners
 return plan

def request():
 r=n.request(new,remap);preview={key:f.metadata(op,project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,function=fn,includeBlueprintTargets=True,units=r['units']) for key,op in [('functionBodies','informationFunctionBodies'),('functionCopies','informationFunctionCopies')]};r['changes'][0]['mapping']=selections(preview);return r

def unchanged():assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())
def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
 for body,text in expected_text.items():assert json.loads(rows[body]['draft'])['source']==text
 for graph,prepared in zip(graphs,[first.prepared,second]):assert json.loads(rows[graph]['draft'] if graph in rows else (f.project/prepared['graphPath']).read_text())['copySource']==prepared['graph']['copySource']
 for path in [first.donor_path,first.donor_body_path,'whole-caller-windows.csbody','CallerHost.celem','WindowsHost.celem','project.cproj']:assert (f.project/path).read_bytes()==snapshot[path]
 receipt=rows[owner]['slotSaveReceipt'];guards=receipt['readGuards']
 for path in ['CallerHost.celem','WindowsHost.celem','CallerOwnedCopy.celem','WindowsOwnedCopy.celem',first.graph_path,second['graphPath'],'project.cproj']:
  assert guards[path]['path']==path and guards[path]['hash']==guard_baselines[path]
 assert all(set(g)=={'path','hash'} for g in guards.values())
 unchanged();return rows[owner]['atomicEditGroup']
