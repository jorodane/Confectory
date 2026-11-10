"""Real new information-function contracts; no live objects/providers created."""
import copy,hashlib,json,shutil
import v536_field_definitions_ui as d
f,owner=d.f,d.owner
extra={'Payload':('schema','field Value single compound '+f.n+'Leaf;'),
'Mood':('enum','value editorEnumProfile="nominal-members-native-v2";value editorEnumValues='+json.dumps(json.dumps([dict(id='ready',name='준비')],ensure_ascii=False))+';value editorEnumNumbers="{\\"ready\\":7}";'),
'LegacyMood':('enum','value editorEnumProfile="nominal-members-v1";value editorEnumValues="[]";'),
'Required':('function',''), 'NativeRules':('module','require '+f.n+'Required (long) -> long;')}
for name,(kind,inside)in extra.items():
 source=kind+' '+f.n+name+(' (long value) -> long'if kind=='function'else'')+' {'+inside+'}'
 (f.project/(name+'.celem')).write_bytes((source+'\r\n').encode());f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
hidden=f.project/'hidden';hidden.mkdir();(hidden/'pack.cpack').write_text('pack Hidden.Types version "1" {element Secret schema "Secret.celem";}');(hidden/'Secret.celem').write_text('schema Hidden.Types::Secret {field Value single general int;}');f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','registry Hidden.Types "hidden/pack.cpack";registry Confectory.Build.DotNet',1))
external=f.case/'registered outside project';shutil.copytree(f.project/'registered',external);f.manifest.write_text(f.manifest.read_text().replace('"registered/pack.cpack"','"'+str(external/'pack.cpack')+'"'));external_original={p:p.read_bytes()for p in external.iterdir()if p.is_file()}
original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()}
def unchanged(except_names=()):
 assert all((f.project/path).read_bytes()==raw for path,raw in original.items()if path not in except_names)
 assert all(p.read_bytes()==raw for p,raw in external_original.items())
def catalog():
 f.invoke('schema',dict(id=owner));s=f.state()['schema'];return f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=s['textHash'],includeNativeTypes=True))['result']['result']
def request(c=None):
 c=c or catalog();choices={row['id']:row for row in c['nativeTypes']};types=[choices[f.n+n]['clrType']for n in ['Payload','NativeRules','Mood']];signature=dict(args=[dict(name='payload',type=types[0]),dict(name='services',type=types[1]+'[]'),dict(name='choice',type=types[2],mode='out')],return_=types[0]);signature['return']=signature.pop('return_');signature['args'].insert(2,dict(name='remote',type=choices['External.Fields::Leaf']['clrType']));fn=owner+'_Function_'+'d'*32
 row=dict(type='function-add',id=fn,name='정보 값 계약',description='기존 타입 선택',signature=signature,nativeTypes={t:copy.deepcopy(choices[f.n+n]['proof'])for t,n in zip(types,['Payload','NativeRules','Mood'])})
 row['nativeTypes'][choices['External.Fields::Leaf']['clrType']]=copy.deepcopy(choices['External.Fields::Leaf']['proof'])
 return dict(action='applySlots',id=owner,rows=[],basis=c['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=[row]))
def verify(checkpoint,fn,signature):
 document=json.loads(checkpoint.read_text());assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';rows={row['id']:row for row in document['changes']};assert fn in rows;contract=f.metadata('inspect',text=rows[fn]['draft'])['signature'];assert contract['return']==signature['return'];assert[(v['Name'],v['Type'],v.get('Mode','in'))for v in contract['Args']]==[(v['name'],v['type'],v.get('mode','in'))for v in signature['args']];guards=rows[owner]['slotSaveReceipt']['readGuards'];assert all(n+'.celem'in guards for n in ['Payload','Leaf','NativeRules','Required','Mood']);receipt=rows[owner]['slotSaveReceipt'];assert{str(external/'pack.cpack'),str(external/'Leaf.celem')}<={v['path']for v in receipt['nativeTypeReads']};assert 'nativeTypes'not in rows[fn]['draft'];return rows[owner]['atomicEditGroup']
