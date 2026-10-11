"""Ordinary EditorHome authoring of real declarations in the opened ButtonGame pack."""
import re
from playwright.sync_api import expect

def verify_schema_authoring(page,project,mount,send,envelope,browser,browser_action,retained_window):
 prefix='Example.ButtonGame::'
 def create(name,kind):
  browser();page.locator('[data-new]').click();page.locator('.context-menu button').filter(has_text='스키마 생성' if kind=='schema' else '개념 생성').click();page.locator('#new-declaration-name').fill(name);page.locator('#new-declaration').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+name,timeout=30000)
 def field(name,kind,type_name,cardinality='single'):
  page.locator('.window[data-key="schema"] [data-add]').click()
  form=page.locator('.window[data-key="schema"] .schema-row').filter(has=page.locator('[data-definition="name"]'))
  form.locator('[data-definition="name"]').fill(name);form.locator('[data-definition="kind"]').select_option(kind);form.locator('[data-definition="type"]').fill(type_name);form.locator('[data-definition="cardinality"]').select_option(cardinality);form.locator('[data-operation="definition-apply"]').click();expect(page.locator('.window[data-key="schema"]').get_by_role('textbox',name='필드 이름',exact=True).last).to_have_value(name,timeout=30000)
 def close():page.locator('.window[data-key="schema"] [data-close]').click()
 create('EntryMeta','schema');field('note','general','string');field('enabled','general','bool');close()
 create('SceneSpec','schema');field('child','compound',prefix+'EntryMeta');field('ticks','general','int','multiple');close()
 create('PreviewSettings','object');close();browser();browser_action('#advanced-source');expect(page.locator('#source')).to_be_visible();expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)
 # Explicit advanced author input attaches the schema using the existing source-draft operation.
 # No consumer-generated source formatter or additional execution pack is introduced.
 text='object '+prefix+'PreviewSettings { use schema '+prefix+'SceneSpec; data child = { note = ""; enabled = false; }; data ticks = [0, 2]; }\n'
 page.locator('#source').fill(text);page.locator('#apply').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000);page.locator('#schema').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'PreviewSettings',timeout=30000)
 def edit(name,value):
  input=page.locator('.window[data-key="schema"] [data-schema-field="'+name+'"]')
  if isinstance(value,bool):input.set_checked(value)
  else:input.fill(str(value))
  input.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000);expect(input).to_be_enabled(timeout=30000)
 edit('note','real nested value');edit('enabled',True);edit('ticks[1]',5);page.screenshot(path='/tmp/confectory-v196-schema-authoring.png',full_page=True)
 # A retained semantic window stays pinned while primary selection moves to its schema definition.
 close();browser();browser_action('#keep-properties');prop=page.locator('.window[data-key="editor-1"]');expect(prop.locator('[data-schema-id]')).to_have_text(prefix+'PreviewSettings',timeout=30000)
 prop.locator('[data-schema-field="note"]').fill('unsent nested input');expect(prop.locator('[data-schema-origin="'+prefix+'EntryMeta"]')).to_have_count(1);prop.locator('[data-schema-origin="'+prefix+'SceneSpec"]').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'SceneSpec',timeout=30000);expect(prop.locator('[data-schema-field="note"]')).to_have_value('unsent nested input');close();prop.locator('[data-close]').click();browser();retained_window();expect(prop.locator('[data-schema-field="note"]')).to_have_value('unsent nested input');prop.locator('[data-schema-field="note"]').locator('..').get_by_role('button',name='현재 값으로 되돌리기',exact=True).click();prop.locator('[data-operation="release-view"]').click();expect(page.locator('.window[data-key^="editor-"]')).to_have_count(0)
 browser();browser_action('#advanced-source');expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)
 state=mount();manifest_ids=[row['id'] for row in state['state']['units'] if row['kind']=='project'];assert len(manifest_ids)==1,state['state']['units'];assert send(envelope(state,'dispose'))['ok']
 page.locator('.browser-tools input[type="range"]').press('End');expect(page.locator('#density-label')).to_have_text('Data')
 for id in [prefix+'EntryMeta',prefix+'SceneSpec',prefix+'PreviewSettings',manifest_ids[0]]:page.locator('[data-review-id="'+id+'"]').check()
 browser_action('#review-group');expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 reviewed=mount();registration=next(row['after'] for row in reviewed['state']['review']['units'] if row['kind']=='project');locator=re.search(r'element\s+PreviewSettings\s+object\s+"([^"]+)"',registration);assert locator;source_path=project/locator.group(1);assert send(envelope(reviewed,'dispose'))['ok'];assert not source_path.exists(),'creation or Review bypassed final Confirm'
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 assert 'real nested value' in source_path.read_text();assert 'data ticks = [0, 5];' in source_path.read_text();assert 'enabled = true;' in source_path.read_text();assert 'element PreviewSettings object' in (project/'project.cpack').read_text()
 browser();page.locator('[data-id="'+prefix+'Score"]').click();expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000);close();browser();browser_action('#advanced-source');expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)

def verify_concept_creation(page,project,mount,send,envelope,browser,browser_action,restart):
 prefix='Example.ButtonGame::'
 def create(name,kind):
  browser();page.locator('[data-new]').click();page.locator('.context-menu button').filter(has_text='개념 생성').click();page.locator('#new-declaration-name').fill(name);page.locator('#new-declaration').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+name,timeout=30000)
 def close():page.locator('.window[data-key="schema"] [data-close]').click()
 # Reproduce the ordinary lowercase concept path, without advanced group selection.
 create('test','object')
 state=mount();draft=state['state']['draft'];ids=draft['creationReviewIds']
 assert draft['kind']=='object' and draft['dirty'] and prefix+'test' in ids and prefix+'ProjectManifest' in ids
 assert any(row['id']==prefix+'test' for row in state['state']['units']), 'new concept hidden by filter/page'
 # Exercise the old single-unit Review path: safe diagnosis, retained dirty drafts.
 import time
 request_id='creation-without-registration'
 assert send(envelope(state,'invoke',endpoint='reviewDraft',requestId=request_id,expectedRevision=state['revision'],input={'id':prefix+'test'}))['ok']
 for _ in range(400):
  updated=send(envelope(state,'update'));matches=[row for row in updated.get('results',[]) if row['requestId']==request_id]
  if matches:break
  time.sleep(.01)
 assert matches and not matches[0]['ok'] and matches[0]['error']['code']=='consumer_error', matches
 assert updated['state']['sourceError']=='creation_registration_required', updated['state']['sourceError']
 assert updated['state']['draft']['dirty'] and updated['state']['draft']['creationReviewIds']==ids
 assert send(envelope(state,'dispose'))['ok']
 source_path=project/'elements/test.celem';assert not source_path.exists()
 page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 saved=list((project/'.confectory/edit-workspaces').glob('*/draft.json'));assert saved
 import json
 assert any({prefix+'test',prefix+'ProjectManifest'} <= {row['id'] for row in json.loads(file.read_text())['changes']} for file in saved)
 # Description editing uses the existing source authoring contract; no ID rename is introduced.
 close();browser();browser_action('#advanced-source');expect(page.locator('#source')).to_be_visible()
 # An accepted consumer operation is not proof that compiler-backed source acceptance succeeded.
 page.locator('#source').fill('object '+prefix+'test { use schema '+prefix+'MissingCreationSchema; }\n')
 page.locator('#apply').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000)
 page.locator('#review').click();expect(page.locator('#review-creation')).to_be_visible(timeout=30000)
 page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('최종 소스에 반영되지 않았습니다. 컴파일 검증·충돌 상태를 확인하고 초안을 수정한 뒤 다시 Review하세요.',timeout=180000)
 expect(page.locator('#confirm')).to_be_disabled();assert not source_path.exists()
 assert 'element test object' not in (project/'project.cpack').read_text()
 page.locator('.window[data-key="review"] [data-close]').click()
 page.locator('#source').fill('object '+prefix+'test { value initial = 1; description "created through ordinary editor"; }\n')
 page.locator('#apply').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000)
 page.locator('#schema').click();expect(page.locator('[data-schema-field="initial"]')).to_have_value('1',timeout=30000)
 page.locator('[data-schema-field="initial"]').fill('2');page.locator('#semantic-save').click()
 expect(page.locator('#status')).to_have_text('필드 입력을 먼저 적용하세요. 입력은 유지됩니다.',timeout=30000)
 expect(page.locator('[data-schema-field="initial"]')).to_have_value('2')
 page.locator('[data-schema-field="initial"]').locator('..').get_by_role('button',name='Apply field',exact=True).click()
 expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
 page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 page.locator('#semantic-review').click();expect(page.locator('#review-creation')).to_be_visible(timeout=30000)
 expect(page.locator('[data-creation-review-id]')).to_have_count(2)
 page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 page.screenshot(path='/tmp/confectory-new-concept-review.png',full_page=True)
 assert not source_path.exists(), 'Save/Review wrote final sources'
 reviewed=mount();assert {row['id'] for row in reviewed['state']['review']['units']}=={prefix+'test',prefix+'ProjectManifest'};assert send(envelope(reviewed,'dispose'))['ok']
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 expect(page.locator('.window[data-key="schema"] [data-dirty]')).to_have_text('작업 사본',timeout=30000)
 assert 'value initial = 2;' in source_path.read_text() and 'created through ordinary editor' in source_path.read_text()
 assert 'element test object "elements/test.celem"' in (project/'project.cpack').read_text()
 close();browser();page.locator('.window[data-key="browser"] [data-tab="concept"]').click()
 expect(page.locator('[data-id="'+prefix+'test"]')).to_be_visible(timeout=30000)
 print('PASS normal lowercase test creation: dirty declaration+registration, Save, editable values, explicit Review, compiler Confirm, actual browser',flush=True)
 # A fresh actual EditorHome process must discover the confirmed manifest and source, not live draft rows.
 restart()
 browser();page.locator('.window[data-key="browser"] [data-tab="concept"]').click()
 expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000)
 expect(page.locator('[data-id="'+prefix+'test"]')).to_be_visible(timeout=30000)
 page.locator('[data-id="'+prefix+'test"]').click()
 expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'test',timeout=30000)
 expect(page.locator('[data-schema-field="initial"]')).to_have_value('2',timeout=30000)
 expect(page.locator('.window[data-key="schema"] textarea[readonly]')).to_have_value('created through ordinary editor')
 fresh=mount();assert fresh['state']['draft']['id']==prefix+'test' and not fresh['state']['draft']['dirty'] and not fresh['state']['draft']['creationReviewIds'];assert send(envelope(fresh,'dispose'))['ok']
 page.screenshot(path='/tmp/confectory-new-concept-reopened.png',full_page=True)
 print('PASS new concept actual process reopen: source+registration discovery, editable saved value, actual description, clean draft',flush=True)
