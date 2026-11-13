"""A new explicitly owned schema tree and existing native plans share one Save."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
root_key='NewStats';power_key='Power';inner_key='Inner';title_key='Title';power_label='힘 공동';title_label='제목 공동';power_value=9223372036854775806;note='명시한 새 내부 값 · 😀';new_label='새 소유 통계';owned_paths={};expected_manifest=None
schema_path=f.project/'FreeInfo.celem';schema_text=schema_path.read_text();manifest_text=f.manifest.read_text();definition_source=f.project/'Leaf2.celem';definition_original=definition_source.read_bytes();original_query=_prior.request()
def leaf(key,type='string',name=None,icon=''):return dict(key=key,name=name or key,icon=icon,definition=dict(kind='general',cardinality='single',type=type),sources=None)
def tree():return dict(fields=[leaf(power_key,'long',power_label,'★'),dict(key=inner_key,name='내부',icon='',definition=dict(kind='owned',cardinality='single'),sources=None,children=dict(fields=[leaf(title_key,name=title_label)]))])
def edited_value():return{power_key:power_value,inner_key:{title_key:note}}
def child_id(path):return owner+'_Properties_'+hashlib.sha256(json.dumps(path,separators=(',',':')).encode()).hexdigest()[:24]
def model(r):return f.metadata('effective',**{k:r[k]for k in ['project','manifest','id','text','drafts']},definitionTypes=True,schemaView=True,validateObjects=True,observeSources=True)['schemaModel']
original_model=model(original_query)
def owned_change():return dict(type='owned-definition',name=root_key,displayName=new_label,icon='',cardinality='single',contract=None,schema=None,schemaHash=None,tree=tree(),sources={},valueJson=json.dumps(edited_value(),ensure_ascii=False,separators=(',',':')))
def capture(r):
 global owned_paths,expected_manifest
 only=copy.deepcopy(r);only['changes']=[owned_change()];candidate=f.metadata('informationDefinitions',**only);expected={child_id([root_key]),child_id([root_key,inner_key])};assert{v['id']for v in candidate['additions']}==expected and not candidate['updates'];owned_paths={v['id']:v['path']for v in candidate['additions']};expected_manifest=candidate['manifest'];return candidate
def request():
 r=_prior.request();capture(r);r['changes'].append(owned_change());return r
def expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_owned(rows):
 current={id:rows.get(id,{}).get('draft',(f.project/path).read_bytes().decode('utf-8-sig')if(f.project/path).exists()else'')for id,path in owned_paths.items()};assert all(current.values());root=rows.get(owner,{}).get('draft',schema_path.read_text());base=f.metadata('inspect',text=schema_text);actual=f.metadata('inspect',text=root);before=base['fields'];after=actual['fields'];assert set(after)==set(before)|{root_key}
 semantic=lambda fields:{k:{n:v for n,v in row.items()if n!='Loc'}for k,row in fields.items()};assert semantic({k:v for k,v in after.items()if k!=root_key})==semantic(before);assert after[root_key]['Type']==child_id([root_key]) and json.loads(actual['values']['editorFieldDefault_'+root_key])==edited_value();changed={'editorIcon','editorFieldDefault_'+root_key,'editorFieldName_'+root_key};assert{k:v for k,v in actual['values'].items()if k not in changed}=={k:v for k,v in base['values'].items()if k not in changed}
 r=copy.deepcopy(original_query);r.update(text=root,manifest=expected_manifest,drafts=r['drafts']+[dict(id=id,text=text)for id,text in current.items()]);m=model(r);assert m['ownedDefinitions'][root_key]['tree']==tree()and set(m['ownedDefinitions'][root_key]['sources'])==set(owned_paths)
def verify_rows(rows):
 expected();_prior.verify_rows(rows);verify_owned(rows)
def verify(checkpoint):
 expected();ids=_prior.verify(checkpoint);rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_owned(rows);assert set(owned_paths)<=set(ids);assert rows[f.n+'ProjectManifest']['draft']==expected_manifest
 for id,path in owned_paths.items():
  unit=rows[id];assert unit['kind']=='schema'and unit['path']==path and unit['baseline']=='missing'and unit['original']==''and unit['creationOwner']==owner
  assert not(f.project/path).exists()
 return ids
def verify_live():
 expected();verify_rows({owner:dict(draft=schema_path.read_text())});assert f.manifest.read_text()==expected_manifest and definition_source.read_bytes()==definition_original;allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(schema_path.relative_to(f.project)),str(f.manifest.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}|set(owned_paths.values())
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 for id,path in owned_paths.items():assert f.metadata('ownedDefinitionOwnership',owner=owner,ownerText=schema_path.read_text(),id=id,text=(f.project/path).read_text(),path=path)['owned']is True
 execute(edited_result,'native-return-execution');f.checked('two explicitly created child schemas and their exact registration Confirm with both native plans; original named/parent/reference sources, values and unselected CSharp stay unchanged')
def unchanged():
 _prior.unchanged()
 for path in owned_paths.values():assert not(f.project/path).exists()
_open_info=d.open_info
def open_info():
 f.page.set_viewport_size({'width':2300,'height':3000});key='editor-1'if d.is_view else'schema';restored=f.page.locator('.window[data-key="'+key+'"]');title=restored.locator('.object-title-name')
 if title.count()and title.is_visible()and title.inner_text()=='FreeInfo':f.owner=lambda:restored;f.idle();return
 return _open_info()
d.open_info=open_info
def own():return f.owner().locator('[data-owned-definition="'+root_key+'"]')
def direct(row,attr):return row.locator(':scope>.property-content-box>['+attr+']')
def tree_rows(row):return row.locator(':scope>.property-content-box>.property-expanded-content>.property-complex-body>.property-fields>.object-property-row')
def expanded(row):
 if not tree_rows(row).first.is_visible():row.locator(':scope>.property-content-box>.object-property-default>.property-expand').click()
 return tree_rows(row)
def add(row):row.locator(':scope>.property-content-box>.object-property-default>[data-owned-add]').click();return tree_rows(row).last
def choose(row,kind):
 direct(row,'data-property-type').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);picker.locator('[data-type="'+kind+'"]'if kind in ['string','long','double','bool']else'[data-field-kind="'+kind+'"]').click()
def value(row,text):row.locator(':scope>.property-content-box>.object-property-default>[data-property-value]').fill(text)
def after_contract(index):
 global root_key,power_key,inner_key,title_key
 from playwright.sync_api import expect
 _prior.after_contract(index)
 if index!=1:return
 f.owner().locator('[data-schema-add]').click();row=f.owner().locator('[data-definition-key]').last;direct(row,'data-property-name').fill(new_label);choose(row,'owned');root_key=f.owner().locator('[data-owned-definition]').last.get_attribute('data-owned-definition');first=add(own());direct(first,'data-property-name').fill(power_label);choose(first,'long');value(tree_rows(own()).first,str(power_value));nested=add(own());direct(nested,'data-property-name').fill('내부');choose(nested,'owned');title=add(tree_rows(own()).nth(1));direct(title,'data-property-name').fill(title_label);value(tree_rows(tree_rows(own()).nth(1)).first,note)
 direct(tree_rows(own()).first,'data-property-icon').click();dialog=f.page.get_by_role('dialog',name=power_label+' 아이콘 편집',exact=True);dialog.locator('[data-icon-choice="★"]').click();dialog.get_by_role('button',name='적용',exact=True).click();f.idle();cells=d.pending();created=next(v for _,v in cells if v.get('kind')=='owned-definition');power_key=created['tree']['fields'][0]['key'];inner_key=created['tree']['fields'][1]['key'];title_key=created['tree']['fields'][1]['children']['fields'][0]['key'];assert len(cells)==5 and created['contract']is None and created['sources']=={}and created['tree']==tree()and json.loads(created['text'])==edited_value();capture(original_query);unchanged();f.checked('original Add/owned-type/nested controls capture two new child sources, exact64 value, native plans and presentation as five inputs without writing or registering files')
 if mode=='reproduce-owned-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'};replies=[r['result']for r in f.traffic[mark:]if r.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed owned creation/native Save response')
  assert d.pending()==cells and checkpoint.read_bytes()==before;unchanged();f.checked('published UI rejects the combined new child/registration/native Save and preserves every input, original registration, checkpoint and missing destination');f.browser.close();raise SystemExit(0)
def validate_history():
 held=d.pending();target=direct(tree_rows(own()).first,'data-property-icon');target.press('Control+z');cell=next(v for _,v in d.pending()if v.get('kind')=='owned-definition');assert cell['tree']['fields'][0]['icon']==''and json.loads(cell['text'])==edited_value();target.press('Control+y');assert d.pending()==held;target.press('Control+z');target.press('Control+Shift+z');assert d.pending()==held
 for key in ['Control+z','Control+y','Control+Shift+z']:f.owner().locator('[data-own-functions-toggle]').press(key);assert d.pending()==held
 f.checked('new owned icon Undo/Redo retains stable native keys, exact value and both explicit function plans; stale function snapshots cannot erase the creation')
