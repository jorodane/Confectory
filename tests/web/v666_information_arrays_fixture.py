"""Existing owned function/editor over explicit primitive, nested and enum arrays."""
import hashlib,json
import v666_information_struct_fixture as x
f=x.f;root_path=x.schema_path;leaf=f.n+'ArrayLeaf';choice=f.n+'ArrayChoice';leaf_path='ArrayLeaf.celem';choice_path='ArrayChoice.celem'
symbol=lambda s:'E'+hashlib.sha256(json.dumps(s).encode()).hexdigest()[:24];native=lambda id:'Confectory.Information.'+symbol(id.split('::')[0])+'.'+symbol(id);leaf_type=native(leaf);choice_type=native(choice)
(f.project/leaf_path).write_bytes(('schema '+leaf+' {field Count single general long;}\r\n').encode())
(f.project/choice_path).write_text('enum '+choice+' {value editorEnumProfile="nominal-members-native-v2";value editorEnumValues="[{\\"id\\":\\"done-id\\",\\"name\\":\\"완료\\"}]";value editorEnumNumbers="{\\"done-id\\":31}";}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element ArrayLeaf schema "'+leaf_path+'";element ArrayChoice enum "'+choice_path+'";registry Confectory.Build.DotNet',1))
path=f.project/root_path;path.write_bytes(path.read_bytes().replace(b'field HP single general long;',('field HP single general long;field Values multiple general long;field Labels multiple general string;field Items multiple compound '+leaf+';field Choices multiple enum '+choice+';').encode()))
x.selected='if(data.Values.Length!=2||data.Labels[0]!="한글 😀"||'+choice_type+'Ids.ToId(data.Choices[0])!="done-id")throw new System.Exception("명시 배열");data.HP=checked(data.Values[0]+data.Values[1]+data.Items[0].Count);return data; // 배열 값 직접 편집 😀\r\n'
(f.project/'Main.csbody').write_text('var original=new '+x.type+' {HP=30,Values=new long[]{10,20},Labels=new string[]{"한글 😀"},Items=new '+leaf_type+'[]{new '+leaf_type+' {Count=1}},Choices=new '+choice_type+'[]{'+choice_type+'Ids.FromId("done-id")}};var value=calls.TypedValue.Invoke(original);if(original.HP!=30||!Object.ReferenceEquals(original.Values,value.Values))throw new System.Exception("원래 C# 값/배열");Console.WriteLine(value.HP);return checked((int)value.HP);')
x.snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};x.schema_path=leaf_path;previous=x.verify

def verify(checkpoint):
 ids,receipt=previous(checkpoint);assert {root_path,leaf_path,choice_path}<=set(receipt['readGuards']);return ids,receipt
x.verify=verify
