"""A child owns its explicit body while inheriting a fixed public contract."""
import copy,json,sys
import v666_node_internal_api as x
nested=None
if '--nested' in sys.argv:
 import v666_node_internal_nested_fixture as nested
f=x.f;parent=f.n+'M11Parent';borrower=f.n+'M11Inherited';root=x.graph
# The parent has a different retained implementation and is never a write target.
parent_text='implementation '+parent+' for '+x.feature+' (long amount) -> long {body common "M11Parent.csbody";}'
(f.project/'M11Parent.celem').write_text(parent_text);(f.project/'M11Parent.csbody').write_text('return amount*100;')
p=f.project/'FlowBody.celem';p.write_text(p.read_text().replace(' {',' extends '+parent+' {',1))
(f.project/'M11Inherited.celem').write_text('implementation '+borrower+' for '+x.feature+' (long amount) -> long extends '+parent+' {}')
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element M11Parent implementation "M11Parent.celem";element M11Inherited implementation "M11Inherited.celem";registry Confectory.Build.DotNet',1))
x.physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
physical=x.physical
parent_files={p:(p.read_bytes(),p.stat().st_mode) for p in [f.project/'M11Parent.celem',f.project/'M11Parent.csbody',f.project/'M11Inherited.celem']}
path=nested.path if nested else '';graph=nested.graph if nested else x.g
frame=root+''.join('/graph:'+p for p in path.split('/') if p);child=frame+'/graph:calculate'
def read():return x.rpc('read',id=frame)
def request(data,**kw):return nested.request(data,**kw) if nested else x.request(data,**kw)
def original():x.original()
def ancestors_original():assert all(p.read_bytes()==data and p.stat().st_mode==mode for p,(data,mode) in parent_files.items())
