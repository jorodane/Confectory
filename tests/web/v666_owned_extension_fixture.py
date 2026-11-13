"""Add one new owned child inside an existing marked, observed tree."""
import copy,hashlib,json,time,sys
import v666_owned_structure_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
existing_paths=dict(_base.owned_paths);owned_paths={};schema_paths=dict(existing_paths);root_key='Stats';new_key='Extra';title_key='Title';power_key='Power';power_label=original_model['ownedDefinitions'][root_key]['tree']['fields'][0]['name'];power_value=original_value[power_key];note='명시한 새 자식 값 · 😀';title_label='새 값';expected_manifest=None

def child_id(path):return owner+'_Properties_'+hashlib.sha256(json.dumps(path,separators=(',',':')).encode()).hexdigest()[:24]
def tree():
 result=copy.deepcopy(original_model['ownedDefinitions'][root_key]['tree']);result['fields'][0]['name']=power_label;result['fields'].append(dict(key=new_key,name='새 자식',icon='',definition=dict(kind='owned',cardinality='single'),sources=None,children=dict(fields=[leaf(title_key,name=title_label,icon='★')])));return result
def edited_value():return original_value|{power_key:power_value,new_key:{title_key:note}}
def owned_change():
 field=original_model['fields'][root_key];return dict(type='owned-definition',name=root_key,displayName='소유 통계',icon='☆',cardinality='single',contract={k:field[k]for k in ['kind','cardinality','type']},schema=owner,schemaHash=field['schemaHash'],tree=tree(),sources=copy.deepcopy(original_model['ownedDefinitions'][root_key]['sources']),valueJson=json.dumps(edited_value(),ensure_ascii=False,separators=(',',':')))
def capture(r):
 global owned_paths,schema_paths,expected_manifest
 only=copy.deepcopy(r);only['changes']=[owned_change()];candidate=f.metadata('informationDefinitions',**only);assert len(candidate['additions'])==1 and candidate['additions'][0]['id']==child_id([root_key,new_key]);owned_paths={v['id']:v['path']for v in candidate['additions']};schema_paths=existing_paths|owned_paths;expected_manifest=candidate['manifest'];return candidate
def request():
 r=_base._prior.request();capture(r);r['changes'].append(owned_change());return r
def expected():
 if 'accepted_description'in globals():_base._prior.accepted_description=accepted_description
def verify_owned(rows):
 current={id:rows.get(id,{}).get('draft',(f.project/path).read_bytes().decode('utf-8-sig')if(f.project/path).exists()else'')for id,path in schema_paths.items()};assert all(current.values())
 for id in existing_paths:assert current[id].startswith(child_prefix)
 root=rows.get(owner,{}).get('draft',schema_path.read_text());before=f.metadata('inspect',text=schema_text);actual=f.metadata('inspect',text=root);semantic=lambda fields:{k:{n:v for n,v in row.items()if n!='Loc'}for k,row in fields.items()};assert semantic(actual['fields'])==semantic(before['fields']);assert json.loads(actual['values']['editorFieldDefault_'+root_key])==edited_value();changed={'editorIcon','editorFieldDefault_'+root_key};assert{k:v for k,v in actual['values'].items()if k not in changed}=={k:v for k,v in before['values'].items()if k not in changed}
 r=copy.deepcopy(original_query);r.update(text=root,manifest=expected_manifest,drafts=[v for v in r['drafts']if v['id']not in schema_paths]+[dict(id=id,text=text)for id,text in current.items()]);m=model(r);assert m['ownedDefinitions'][root_key]['tree']==tree()and set(m['ownedDefinitions'][root_key]['sources'])==set(schema_paths)
def verify_rows(rows):expected();_base._prior.verify_rows(rows);verify_owned(rows)
def verify(checkpoint):
 expected();ids=_base._prior.verify(checkpoint);rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_owned(rows);assert set(owned_paths)<=set(ids)and rows[f.n+'ProjectManifest']['draft']==expected_manifest
 for id,path in owned_paths.items():assert rows[id]['baseline']=='missing'and rows[id]['original']==''and rows[id]['creationOwner']==owner and rows[id]['path']==path and not(f.project/path).exists()
 for id,path in existing_paths.items():
  if id in rows:assert rows[id]['baseline']!='missing'and rows[id]['original']==snapshot[path].decode('utf-8-sig')
 return ids
def verify_live():
 expected();verify_rows({owner:dict(draft=schema_path.read_text())});assert f.manifest.read_text()==expected_manifest and definition_source.read_bytes()==definition_original;allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(schema_path.relative_to(f.project)),str(f.manifest.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}|set(schema_paths.values())
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 for id,path in owned_paths.items():assert f.metadata('ownedDefinitionOwnership',owner=owner,ownerText=schema_path.read_text(),id=id,text=(f.project/path).read_text(),path=path)['owned']is True
 unchanged_inner=child_id([root_key,'Inner']);path=existing_paths[unchanged_inner];assert(f.project/path).read_bytes()==snapshot[path]and _base.physical(f.project/path)==_base.owned_physical[unchanged_inner];execute(edited_result,'native-return-execution');f.checked('one new nested child and exact registration Confirm with existing observed root updates and both native plans; original inner source bytes/inode/mode/mtime, IDs, values and other CSharp remain intact')
def unchanged():
 _base.unchanged()
 for path in owned_paths.values():assert not(f.project/path).exists()
def own():return f.owner().locator('[data-owned-definition="'+root_key+'"]')
def add(row):row.locator(':scope>.property-content-box>.object-property-default>[data-owned-add]').click();return tree_rows(row).last
def choose(row,kind):
 direct(row,'data-property-type').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);picker.locator('[data-type="'+kind+'"]'if kind in ['string','long','double','bool']else'[data-field-kind="'+kind+'"]').click()
def value(row,text):row.locator(':scope>.property-content-box>.object-property-default>[data-property-value]').fill(text)
def after_contract(index):
 global new_key,title_key
 from playwright.sync_api import expect
 _base._prior.after_contract(index)
 if index!=1:return
 expanded(own());new=add(own());direct(new,'data-property-name').fill('새 자식');choose(new,'owned');title=add(tree_rows(own()).last);direct(title,'data-property-name').fill(title_label);value(tree_rows(tree_rows(own()).last).first,note);direct(tree_rows(tree_rows(own()).last).first,'data-property-icon').click();dialog=f.page.get_by_role('dialog',name=title_label+' 아이콘 편집',exact=True);dialog.locator('[data-icon-choice="★"]').click();dialog.get_by_role('button',name='적용',exact=True).click();f.idle();cells=d.pending();row=next(v for _,v in cells if v.get('kind')=='owned-definition');new_key=row['tree']['fields'][-1]['key'];title_key=row['tree']['fields'][-1]['children']['fields'][0]['key'];assert len(cells)==5 and row['sources']==original_model['ownedDefinitions'][root_key]['sources']and row['tree']==tree()and json.loads(row['text'])==edited_value();capture(original_query);unchanged();f.checked('existing owned Add/type controls explicitly add one child while retaining both original child hashes, stable old fields/values, native plans and five inputs')
def validate_history():
 held=d.pending();target=direct(tree_rows(tree_rows(own()).last).first,'data-property-icon');target.press('Control+z');row=next(v for _,v in d.pending()if v.get('kind')=='owned-definition');assert row['tree']['fields'][-1]['children']['fields'][0]['icon']==''and json.loads(row['text'])==edited_value();target.press('Control+y');assert d.pending()==held;target.press('Control+z');target.press('Control+Shift+z');assert d.pending()==held
 for key in ['Control+z','Control+y','Control+Shift+z']:f.owner().locator('[data-own-functions-toggle]').press(key);assert d.pending()==held
 f.checked('new nested icon history preserves the existing owner/source basis and exact defaults; stale function history cannot erase any input')
