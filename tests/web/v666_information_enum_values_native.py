"""Nominal information-choice defaults/data, dependency proofs and used-id protection."""
import copy,json,pathlib,sys
helper=pathlib.Path(__file__).with_name('v666_owned_information_native.py')
exec(compile(helper.read_text().split('\nv=prepare(',1)[0],str(helper),'exec'))
members=[dict(id='stable-ready',name='준비 됨',icon='★'),dict(id='stable-done',name='완료')]
def enum_text(rows):return 'enum '+ns+'Mood { // 保持する種類\r\nvalue editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(rows,ensure_ascii=False,separators=(',',':')))+';}'
items['Mood']=('enum',enum_text(members));manifest=manifest[:-1]+'element Mood enum "Mood.celem";}';project.write_text(manifest);(root/'Mood.celem').write_text(items['Mood'][1]);original.update({project:project.read_bytes(),root/'Mood.celem':(root/'Mood.celem').read_bytes()})
def request(id=owner,text=None,drafts=None):return base(id,text,m=manifest,drafts=drafts)
def inspect(q):
 r=rpc('effective',{**q,'schemaView':True,'validateObjects':True,'definitionTypes':True});assert r['status']=='available',r;return r
q=request();catalog=inspect(q)['definitionTypes'];choice=next(c for c in catalog if c['kind']=='enum');assert choice['targets']==members and json.loads(choice['valueJson'])=='stable-ready';assert set(choice['sources'])=={ns+'Mood'}
row=dict(type='typed-definition',name='Choice',displayName='기분',contract=dict(kind='enum',cardinality='single',type=ns+'Mood'),sources=choice['sources'],valueJson='"stable-done"')
v=prepare([row],q);q=overlay(v,q);view=inspect(q);assert view['schemaModel']['data']['Choice']['scalar']=='stable-done' and view['schemaModel']['enums'][ns+'Mood']==members;assert '9223372036854775805' in v['text'] and not v['updates'] and not v['additions'];check('a new information property stores an explicit enum owner and stable item id; defaults are typed metadata, not numeric/C# values')
for invalid in ['0','"완료"','"missing"','null','{"$ref":"'+ns+'Item"}']:
 prepare([dict(row,name='Bad',displayName='나쁜 값',valueJson=invalid),dict(type='description',text='partial forbidden')],q,False)
bad=copy.deepcopy(row);bad['name']='Stale';bad['displayName']='오래된 선택';bad['sources'][ns+'Mood']='0'*64;prepare([bad],q,False)
check('labels, ordinals, missing members, object references and stale type proofs reject the whole candidate without source writes')
array=dict(row,name='Many',displayName='기분 목록',contract=dict(row['contract'],cardinality='multiple'),valueJson='["stable-ready","stable-done",""]');q=overlay(prepare([array],q),q);assert len(inspect(q)['schemaModel']['data']['Many']['items'])==3
reordered=[dict(members[1],name='새 완료 이름'),members[0]];q['drafts']= [dict(d,text=enum_text(reordered)) if d['id']==ns+'Mood' else d for d in q['drafts']];assert inspect(q)['schemaModel']['data']['Choice']['scalar']=='stable-done';check('name/order changes retain selected identity; scalar/list choices and the prototype empty selection stay distinct')
enum_request=dict(project=str(project),manifest=q['manifest'],id=ns+'Mood',text=enum_text(reordered),drafts=[dict(id=owner,text=q['text'])]+[d for d in q['drafts'] if d['id']!=ns+'Mood'])
rpc('functionPresentation',{**enum_request,'changes':[dict(type='enum-values',text=json.dumps([members[0]]))]},False)
rpc('functionPresentation',{**enum_request,'changes':[dict(type='enum-values',text=json.dumps(reordered))]})
check('removing a used member is wholly refused; renaming/reordering is accepted without changing property/default records')
obj=request(ns+'Item');obj_choice=next(c for c in inspect(obj)['definitionTypes'] if c['kind']=='enum');object_row={k:v for k,v in dict(row,sources=obj_choice['sources']).items() if k!='displayName'};ov=prepare([object_row],obj);oq=overlay(ov,obj);data=inspect(oq)['schemaModel']['data'];assert data['Choice']['scalar']=='stable-done' and data['Keep']['scalar']==9223372036854775804
edited=prepare([dict(type='data',path=['Choice'],contract=row['contract'],valueJson='"stable-ready"')],oq);assert inspect(overlay(edited,oq))['schemaModel']['data']['Choice']['scalar']=='stable-ready'
check('an object owns only its local enum property definition/data; applied source, exact64 values and enum originals remain intact')
# Generated registered-pack fixture: choosing its public enum never edits it.
external=root/'registered choices';external.mkdir();foreign='External.Choices::Mood';foreign_members=[dict(id='foreign-id',name='외부 종류',icon='◇')]
external_source='enum '+foreign+' {value editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(foreign_members,ensure_ascii=False))+';}'
(external/'Mood.celem').write_text(external_source);(external/'pack.cpack').write_text('pack External.Choices version "1" {element Mood enum "Mood.celem";}')
original.update({p:p.read_bytes() for p in external.iterdir()})
registered=manifest[:-1]+'registry External.Choices "registered choices/pack.cpack";dependency External.Choices version "1";}'
foreign_q=base(m=registered);foreign_choice=next(c for c in inspect(foreign_q)['definitionTypes'] if c['id']==foreign)
foreign_row=dict(row,name='ImportedChoice',displayName='외부 선택',contract=dict(kind='enum',cardinality='single',type=foreign),sources=foreign_choice['sources'],valueJson='"foreign-id"')
result=prepare([foreign_row],foreign_q);assert inspect(overlay(result,foreign_q))['schemaModel']['data']['ImportedChoice']['scalar']=='foreign-id'
prepare([dict(foreign_row,valueJson='"stable-done"')],foreign_q,False)
undeclared=copy.deepcopy(foreign_q);undeclared['manifest']=registered.replace('dependency External.Choices version "1";','');prepare([foreign_row],undeclared,False)
check('qualified enum owners use only declared dependencies; foreign membership is checked and registered manifest/enum bytes stay untouched')
print(json.dumps(dict(checks=checks,evidence=str(root),sourceWritten=False,csharpEnumRepresentation='undecided'),ensure_ascii=False))
