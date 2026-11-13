"""Existing explicitly owned child structures and native bodies share one Save."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
root_key='Stats';flag_key='Flag';power_label='힘 공동';title_label='제목'if'--unchanged-child'in sys.argv else'제목 공동';note='원래 내부 값'if'--unchanged-child'in sys.argv else'명시한 내부 값 · 😀';precise=9223372036854775804
def leaf(key,type='string',name=None,icon=''):return dict(key=key,name=name or key,icon=icon,definition=dict(kind='general',cardinality='single',type=type),sources=None)
seed=_prior.request();catalogue=f.metadata('effective',**seed,definitionTypes=True,schemaView=True,validateObjects=True,observeSources=True)['definitionTypes'];selected_type=next(v for v in catalogue if v['kind']=='compound'and v['id']==f.n+'Leaf2');assert selected_type['available']
original_value=dict(Power=9223372036854775806,Inner=dict(Title='원래 내부 값'),Named=dict(Count=precise,Note='원래 명명 값'));power_value=original_value['Power']
seed_row=dict(type='owned-definition',name=root_key,displayName='소유 통계',icon='☆',cardinality='single',contract=None,schema=None,schemaHash=None,tree=dict(fields=[leaf('Power','long','힘'),dict(key='Inner',name='내부',icon='',definition=dict(kind='owned',cardinality='single'),sources=None,children=dict(fields=[leaf('Title',name='제목')])),dict(key='Named',name='명명 정보',icon='',definition=dict(kind='compound',cardinality='single',type=f.n+'Leaf2'),sources=copy.deepcopy(selected_type['sources']))]),sources={},valueJson=json.dumps(original_value,ensure_ascii=False,separators=(',',':')))
created=f.metadata('informationDefinitions',**(seed|dict(changes=[seed_row])));assert len(created['additions'])==2 and not created['updates']
schema_path=f.project/'FreeInfo.celem';schema_path.write_text(created['text']);f.manifest.write_text(created['manifest']);owned_paths={};child_prefix='// 원래 소유 자식 · 😀\r\n'
for row in created['additions']:
 path=f.project/row['path'];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((child_prefix+row['text'].replace('\r\n','\n').replace('\n','\r\n')).encode());owned_paths[row['id']]=row['path']
snapshot.update({str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts});f.original.update(snapshot);schema_text=schema_path.read_text();manifest_text=f.manifest.read_text();definition_source=f.project/'Leaf2.celem';definition_original=definition_source.read_bytes()
_open_info=d.open_info
def open_info():
 f.page.set_viewport_size({'width':2300,'height':3000});key='editor-1'if d.is_view else'schema';restored=f.page.locator('.window[data-key="'+key+'"]');title=restored.locator('.object-title-name')
 if title.count()and title.is_visible()and title.inner_text()=='FreeInfo':
  f.owner=lambda:restored;f.idle();return
 return _open_info()
d.open_info=open_info
def model(r):return f.metadata('effective',**{k:r[k]for k in ['project','manifest','id','text','drafts']},definitionTypes=True,schemaView=True,validateObjects=True,observeSources=True)['schemaModel']
original_query=_prior.request();original_model=model(original_query)
def physical(path):
 s=path.stat();return(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_mtime_ns)
owned_physical={id:physical(f.project/path)for id,path in owned_paths.items()}
def edited_tree(before):
 tree=copy.deepcopy(before);tree['fields'][0].update(name=power_label,icon='★');tree['fields'][1]['children']['fields'][0]['name']=title_label;tree['fields'].append(leaf(flag_key,'bool','상태'));return tree
def edited_value():return original_value|dict(Power=power_value,Inner=dict(Title=note),**{flag_key:True})
def owned_change(r):
 m=model(r);field=m['fields'][root_key];owned=m['ownedDefinitions'][root_key];assert len(owned['sources'])==2;return dict(type='owned-definition',name=root_key,displayName='소유 통계',icon='☆',cardinality='single',contract={k:field[k]for k in ['kind','cardinality','type']},schema=owner,schemaHash=field['schemaHash'],tree=edited_tree(owned['tree']),sources=copy.deepcopy(owned['sources']),valueJson=json.dumps(edited_value(),ensure_ascii=False,separators=(',',':')))
def request():
 r=_prior.request();r['changes'].append(owned_change(r));return r
def expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_owned(rows):
 current={}
 for id,path in owned_paths.items():
  current[id]=rows.get(id,{}).get('draft',(f.project/path).read_bytes().decode('utf-8-sig'));assert current[id].startswith(child_prefix)
 root=rows.get(owner,{}).get('draft',schema_path.read_text());base=f.metadata('inspect',text=schema_text);actual=f.metadata('inspect',text=root);semantic=lambda fields:{k:{n:v for n,v in row.items()if n!='Loc'}for k,row in fields.items()};assert semantic(actual['fields'])==semantic(base['fields']);assert json.loads(actual['values']['editorFieldDefault_'+root_key])==edited_value();changed={'editorIcon','editorFieldDefault_'+root_key};assert{k:v for k,v in actual['values'].items()if k not in changed}=={k:v for k,v in base['values'].items()if k not in changed}
 r=copy.deepcopy(original_query);r.update(text=root,manifest=manifest_text,drafts=[v for v in r['drafts']if v['id']not in owned_paths]+[dict(id=id,text=text)for id,text in current.items()]);m=model(r);assert m['ownedDefinitions'][root_key]['tree']==edited_tree(original_model['ownedDefinitions'][root_key]['tree']);assert set(m['ownedDefinitions'][root_key]['sources'])==set(owned_paths)
def verify_rows(rows):
 expected();_prior.verify_rows(rows);verify_owned(rows)
def verify(checkpoint):
 expected();ids=_prior.verify(checkpoint);rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_owned(rows);child_ids=set(owned_paths);root_child=original_model['fields'][root_key]['type'];assert root_child in ids
 if '--unchanged-child'in sys.argv:
  for id in child_ids-{root_child}:assert id not in rows or rows[id]['draft']==rows[id]['original']==snapshot[owned_paths[id]].decode('utf-8-sig')
 else:assert child_ids<=set(ids)
 assert not any(v.get('baseline')=='missing'for v in rows.values());return ids
def verify_live():
 expected();verify_rows({owner:dict(draft=schema_path.read_text())});assert f.manifest.read_text()==manifest_text and definition_source.read_bytes()==definition_original
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(schema_path.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}|set(owned_paths.values())
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if '--unchanged-child'in sys.argv:
  for id,path in owned_paths.items():
   if id!=original_model['fields'][root_key]['type']:assert(f.project/path).read_bytes()==snapshot[path]and physical(f.project/path)==owned_physical[id]
  f.checked('unchanged owned sibling remains an original Review/read member with no dirty draft or physical byte/inode/mode/mtime write through Confirm')
 execute(edited_result,'native-return-execution');f.checked('existing marked child IDs/locators, exact values and original registration Confirm with both explicit native plans; ordinary named/parent/external sources and unselected CSharp remain unchanged')
def own():return f.owner().locator('[data-owned-definition="'+root_key+'"]')
def direct(row,attr):return row.locator(':scope>.property-content-box>['+attr+']')
def tree_rows(row):return row.locator(':scope>.property-content-box>.property-expanded-content>.property-complex-body>.property-fields>.object-property-row')
def expanded(row):
 if not tree_rows(row).first.is_visible():row.locator(':scope>.property-content-box>.object-property-default>.property-expand').click()
 return tree_rows(row)
def after_contract(index):
 global flag_key
 from playwright.sync_api import expect
 _prior.after_contract(index)
 if index!=1:return
 rows=expanded(own());direct(rows.nth(0),'data-property-name').fill(power_label);f.idle();inner=tree_rows(own()).nth(1);expanded(inner);direct(tree_rows(inner).first,'data-property-name').fill(title_label);tree_rows(inner).first.locator(':scope>.property-content-box>.object-property-default>[data-property-value]').fill(note);f.idle();own().locator(':scope>.property-content-box>.object-property-default>[data-owned-add]').click();added=tree_rows(own()).last;direct(added,'data-property-name').fill('상태');direct(added,'data-property-type').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);picker.locator('[data-type=bool]').click();tree_rows(own()).last.locator(':scope>.property-content-box>.object-property-default>[data-property-value]').fill('true');f.idle();held=d.pending();cell=next(v for _,v in held if v.get('kind')=='owned-definition');flag_key=cell['tree']['fields'][-1]['key']
 direct(tree_rows(own()).first,'data-property-icon').click();dialog=f.page.get_by_role('dialog',name=power_label+' 아이콘 편집',exact=True);expect(dialog).to_be_visible();dialog.locator('[data-icon-choice="★"]').click();dialog.get_by_role('button',name='적용',exact=True).click();f.idle();held=d.pending();cell=next(v for _,v in held if v.get('kind')=='owned-definition');assert len(held)==5 and cell['tree']==edited_tree(original_model['ownedDefinitions'][root_key]['tree'])and json.loads(cell['text'])==edited_value();assert cell['sources']==original_model['ownedDefinitions'][root_key]['sources'];unchanged();f.checked('original owned controls capture existing marked child structure/member edits and both native plans in five inputs; precise values, source proofs, IDs and original files retained')
 if mode=='reproduce-owned-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'};replies=[r['result']for r in f.traffic[mark:]if r.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed owned/native Save response')
  assert d.pending()==held and checkpoint.read_bytes()==before;unchanged();f.checked('published original UI rejects the combined owned structure/native Save and preserves all five inputs, original registration, children and checkpoint');f.browser.close();raise SystemExit(0)
def validate_history():
 held=d.pending()
 for key in ['Control+z','Control+y','Control+Shift+z']:
  f.owner().locator('[data-own-functions-toggle]').press(key);assert d.pending()==held
 target=direct(tree_rows(own()).first,'data-property-icon');target.press('Control+z');undone=d.pending();cell=next(v for _,v in undone if v.get('kind')=='owned-definition');assert len(undone)==5 and cell['tree']['fields'][0]['icon']==''and json.loads(cell['text'])==edited_value();target.press('Control+y');assert d.pending()==held;target.press('Control+z');assert d.pending()==undone;target.press('Control+Shift+z');assert d.pending()==held;f.checked('owned child icon Undo/Redo retains every other structure/value/native input; stale function history cannot rewrite the owned tree')
