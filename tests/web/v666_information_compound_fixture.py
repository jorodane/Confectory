"""Same real owned function/editor, now with an inline child information value."""
import json
import v666_information_struct_fixture as x
root_path=x.schema_path;leaf=x.f.n+'CompoundLeaf';leaf_path='CompoundLeaf.celem'
(x.f.project/leaf_path).write_bytes(('schema '+leaf+' {field Count single general long;}\r\n').encode())
x.f.manifest.write_text(x.f.manifest.read_text().replace('registry Confectory.Build.DotNet','element CompoundLeaf schema "'+leaf_path+'";registry Confectory.Build.DotNet',1))
path=x.f.project/root_path;path.write_bytes(path.read_bytes().replace(b'field HP single general long;',('field HP single general long;field Payload single compound '+leaf+';').encode()))
x.selected='data.Payload.Count=checked(data.Payload.Count+1);data.HP=checked(data.HP+data.Payload.Count);return data; // 중첩 값 직접 편집 😀\r\n'
x.snapshot={str(p.relative_to(x.f.project)):p.read_bytes()for p in x.f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(x.f.project).parts}
# The existing CAS fixture now changes only the nested leaf after snapshot/Review.
# The containing schema and its nominal CLR name stay unchanged.
x.schema_path=leaf_path
previous=x.verify
def verify(checkpoint):
 ids,receipt=previous(checkpoint);assert root_path in receipt['readGuards']and leaf_path in receipt['readGuards'];return ids,receipt
x.verify=verify

