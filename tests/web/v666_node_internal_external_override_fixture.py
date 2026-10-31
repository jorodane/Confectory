"""Generated registered pack, fixed contract, and an explicitly owned child body."""
import json,pathlib,sys
import v666_node_internal_override_fixture as local
x=local.x;f=local.f
pack=f.case/'registered ancestors';pack.mkdir();parent='External.Ancestors::Parent';parent_file=pack/'Parent.celem'
parent_text='implementation '+parent+' for '+x.feature+' (long amount) -> long {body common "Parent.csbody";}'
parent_file.write_text(parent_text);(pack/'Parent.csbody').write_text('return amount*100;')
(pack/'pack.cpack').write_text('pack External.Ancestors version "1" {standalone false;dependency Owned.Elements version "1";element Parent implementation "Parent.celem";}')
for name in ['FlowBody.celem','M11Inherited.celem']:
 p=f.project/name;p.write_text(p.read_text().replace(local.parent,parent))
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','dependency External.Ancestors version "1";registry External.Ancestors "'+str(pack/'pack.cpack')+'";registry Confectory.Build.DotNet',1))
for p in pack.iterdir():p.chmod(0o440)
pack.chmod(0o750)
x.physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};x.physical.update({p:p.read_bytes() for p in pack.iterdir()})
physical=x.physical;parent_files={p:(p.read_bytes(),p.stat().st_mode) for p in pack.iterdir()};borrower=local.borrower;path=local.path;frame=local.frame;child=local.child;graph=local.graph
def read():return local.read()
def original():x.original()
def ancestors_original():assert all(p.read_bytes()==physical[p] and p.stat().st_mode==mode for p,(_,mode) in parent_files.items())
def request(data,**kw):
 r=local.request(data,**kw);node=next(n for n in data['nodes'] if n['id']=='calculate');source=next(s for s in data['sources'] if s['id']==node['sourceId'])
 r['edits'][0]['definition']['binding']={'graph':frame,'root':x.graph,'node':'calculate','source':node['sourceId'],'definitionHash':node['definitionHash'],'sourceHash':source['hash'],'dependencyHash':data['nodeFlowDependencyHash']};return r
def change_parent(suffix):
 parent_file.chmod(0o640)
 try:parent_file.write_bytes(physical[parent_file]+suffix)
 finally:parent_file.chmod(0o440)
def restore_parent():
 parent_file.chmod(0o640)
 try:parent_file.write_bytes(physical[parent_file])
 finally:parent_file.chmod(0o440)
