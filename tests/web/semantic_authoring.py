"""Ordinary EditorHome authoring of real declarations in the opened ButtonGame pack."""
import re
from playwright.sync_api import expect

def inspect_advanced_review(page):
 review=page.locator('.window[data-key="review"]')
 expect(review.locator('[data-source-before]')).to_have_count(0)
 expect(review.locator('[data-additional-changes]').first).to_be_visible()
 expect(page.locator('#confirm')).to_be_disabled()
 review.locator('[data-review-advanced]').click()
 expect(review.locator('[data-source-after]').first).to_be_visible()
 review.locator('[data-advanced-reviewed]').check()
 expect(page.locator('#confirm')).to_be_enabled(timeout=30000)


def verify_schema_authoring(page,project,mount,send,envelope,browser,browser_action,retained_window):
 prefix='Example.ButtonGame::'
 def create(name,kind):
  browser();page.locator('[data-new]').click();page.locator('.context-menu button').filter(has_text='스키마 생성' if kind=='schema' else '개념 생성').click();page.locator('#new-declaration-name').fill(name);page.locator('#new-declaration').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+name,timeout=30000)
 def field(name,kind,type_name,cardinality='single'):
  page.locator('.window[data-key="schema"] [data-add]').click()
  form=page.locator('.window[data-key="schema"] .schema-row').filter(has=page.locator('[data-definition="name"]'))
  form.locator('[data-definition="name"]').fill(name);form.locator('[data-definition="kind"]').select_option(kind);form.locator('[data-definition="type"]').fill(type_name);form.locator('[data-definition="cardinality"]').select_option(cardinality);form.locator('[data-operation="definition-apply"]').click();expect(page.locator('.window[data-key="schema"]').get_by_role('textbox',name='필드 이름',exact=True).last).to_have_value(name,timeout=30000)
 def close():
  button=page.locator('.window[data-key="schema"] [data-close]')
  if button.count():button.click()
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
 browser_action('#review-group');expect(page.locator('[data-review-advanced]')).to_be_visible(timeout=30000)
 # Applied schema relations now have a complete semantic explanation alongside data/field changes.
 review=page.locator('.window[data-key="review"]');expect(review.locator('[data-additional-changes]')).to_have_count(0);expect(review.get_by_role('group',name='사용 관계',exact=True)).to_contain_text(prefix+'SceneSpec');expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 review.locator('[data-review-advanced]').click();expect(review.locator('[data-source-after]')).to_have_count(4);expect(review.locator('[data-advanced-reviewed]')).to_have_count(0)

 reviewed=mount();registration=next(row['after'] for row in reviewed['state']['review']['units'] if row['kind']=='project');locator=re.search(r'element\s+PreviewSettings\s+object\s+"([^"]+)"',registration);assert locator;source_path=project/locator.group(1);assert send(envelope(reviewed,'dispose'))['ok'];assert not source_path.exists(),'creation or Review bypassed final Confirm'
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 assert 'real nested value' in source_path.read_text();assert 'data ticks = [0, 5];' in source_path.read_text();assert 'enabled = true;' in source_path.read_text();assert 'element PreviewSettings object' in (project/'project.cpack').read_text()
 browser();page.locator('[data-id="'+prefix+'Score"]').click();expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000);close();browser();browser_action('#advanced-source');expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)

def verify_concept_creation(page,project,mount,send,envelope,browser,browser_action,restart):
 prefix='Example.ButtonGame::'
 def create(name,kind):
  browser();page.locator('[data-new]').click();page.locator('.context-menu button').filter(has_text='개념 생성').click();page.locator('#new-declaration-name').fill(name);page.locator('#new-declaration').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+name,timeout=30000)
 def close():
  button=page.locator('.window[data-key="schema"] [data-close]')
  if button.count():button.click()
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
 page.locator('#review-creation').click();expect(page.locator('[data-review-advanced]')).to_be_visible(timeout=30000);expect(page.locator('[data-additional-changes]')).to_have_count(0);expect(page.locator('.window[data-key="review"]').get_by_role('group',name='사용 관계',exact=True)).to_contain_text(prefix+'MissingCreationSchema');expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('최종 소스에 반영되지 않았습니다. 컴파일 검증·충돌 상태를 확인하고 초안을 수정한 뒤 다시 Review하세요.',timeout=180000)
 expect(page.locator('#confirm')).to_be_disabled();assert not source_path.exists()
 assert 'element test object' not in (project/'project.cpack').read_text()
 page.locator('.window[data-key="review"] [data-close]').click()
 page.locator('#source').fill('object '+prefix+'test { value initial = 1; description "created through ordinary editor"; }\n')
 page.locator('#apply').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000)
 page.locator('#schema').click();expect(page.locator('[data-schema-field="initial"]')).to_have_value('1',timeout=30000)
 page.locator('.window[data-key="source"] [data-close]').click()
 expect(page.locator('.window[data-key="source"]')).to_be_hidden()
 page.locator('[data-schema-field="initial"]').fill('2');page.locator('#semantic-save').click()
 expect(page.locator('#status')).to_have_text('필드 입력을 먼저 적용하세요. 입력은 유지됩니다.',timeout=30000)
 expect(page.locator('[data-schema-field="initial"]')).to_have_value('2')
 page.locator('[data-schema-field="initial"]').locator('..').get_by_role('button',name='Apply field',exact=True).click()
 expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
 page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 page.locator('#semantic-review').click();expect(page.locator('#review-creation')).to_be_visible(timeout=30000)
 expect(page.locator('[data-creation-review-id]')).to_have_count(2)
 page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 expect(page.locator('.window[data-key="review"] [data-source-before]')).to_have_count(0)
 expect(page.locator('.window[data-key="review"]')).to_contain_text('개념 생성')
 expect(page.locator('.window[data-key="review"]')).to_contain_text('프로젝트에 등록')
 expect(page.locator('.window[data-key="review"]')).to_contain_text('값 · initial')
 # The new declaration and manifest are one atomic selectable group; nothing is auto-confirmed.
 review_window=page.locator('.window[data-key="review"]');expect(review_window.locator('[data-review-group]')).to_have_count(1)
 group=review_window.locator('[data-review-group]');group.uncheck();expect(page.locator('#confirm')).to_be_disabled();expect(review_window.locator('[data-rereview]')).to_be_disabled();assert not source_path.exists()
 group.check();expect(page.locator('#confirm')).to_be_enabled()
 for _ in range(3):
  review_window.locator('[data-review-advanced]').click();expect(review_window.locator('[data-review-source]')).to_be_visible();expect(review_window.locator('[data-review-advanced]')).to_have_attribute('aria-expanded','true')
  review_window.locator('[data-review-advanced]').click();expect(review_window.locator('[data-review-source]')).to_be_hidden();expect(review_window.locator('[data-review-advanced]')).to_have_attribute('aria-expanded','false')
 prior=mount();old_token=prior['state']['review']['token'];assert send(envelope(prior,'dispose'))['ok']
 review_window.locator('[data-close]').click();expect(review_window).to_have_count(0);assert not source_path.exists()
 page.locator('#semantic-review').click();page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 reopened=mount();assert reopened['state']['review']['token']!=old_token;assert send(envelope(reopened,'dispose'))['ok']
 page.screenshot(path='/tmp/confectory-new-concept-review.png',full_page=True)
 assert not source_path.exists(), 'Save/Review wrote final sources'
 reviewed=mount();assert {row['id'] for row in reviewed['state']['review']['units']}=={prefix+'test',prefix+'ProjectManifest'};assert send(envelope(reviewed,'dispose'))['ok']
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 expect(page.locator('.window[data-key="schema"] [data-dirty]')).to_have_text('작업 사본',timeout=30000)
 assert 'value initial = 2;' in source_path.read_text() and 'created through ordinary editor' in source_path.read_text()
 assert 'element test object "elements/test.celem"' in (project/'project.cpack').read_text()
 # The ordinary description form stages only the declaration description, preserving ID/references.
 manifest_before=(project/'project.cpack').read_bytes()
 description='일반 폼 설명 "인용"\n두 번째 줄'
 field=page.locator('.window[data-key="schema"] [data-description]')
 expect(field).to_be_editable();expect(page.locator('.window[data-key="schema"] input[readonly]')).to_have_value('test')
 field.fill(description)
 # A second field edit advances the shared draft: the older description input must not overwrite it.
 initial=page.locator('[data-schema-field="initial"]');initial.fill('3');initial.locator('..').get_by_role('button',name='Apply field',exact=True).click()
 expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000);expect(field).to_have_value(description)
 page.locator('#semantic-save').click();expect(page.locator('#status')).not_to_have_text('Draft saved; final sources unchanged',timeout=30000)
 expect(page.locator('#status')).to_have_text('소스 작업을 완료하지 못했습니다. 작업 사본과 입력은 유지됩니다. 선택과 변경 검토를 다시 확인하세요.',timeout=30000)
 expect(field).to_have_value(description)
 page.locator('[data-operation="reset-description"]').click();expect(field).to_have_value('created through ordinary editor')
 initial.fill('2');initial.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
 field.fill(description)
 page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 assert source_path.read_text().find('created through ordinary editor')>=0, 'description Save bypassed Confirm'
 saved_description=mount();assert saved_description['state']['draft']['dirty'];revision=saved_description['state']['schema']['revision']
 # Reject a stale description edit through the actual consumer, retaining the saved description draft.
 request_id='stale-description'
 assert send(envelope(saved_description,'invoke',endpoint='editDescription',requestId=request_id,expectedRevision=saved_description['revision'],input={'id':prefix+'test','value':'must not replace draft','revision':revision-1}))['ok']
 for _ in range(400):
  updated=send(envelope(saved_description,'update'));matches=[row for row in updated.get('results',[]) if row['requestId']==request_id]
  if matches:break
  time.sleep(.01)
 assert matches and not matches[0]['ok'];assert updated['state']['draft']['dirty']
 assert send(envelope(saved_description,'dispose'))['ok']
 expect(field).to_have_value(description)
 page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 review_window=page.locator('.window[data-key="review"]')
 expect(review_window.locator('[data-semantic-change]')).to_have_count(1)
 expect(review_window.locator('[data-semantic-before]')).to_have_text('created through ordinary editor')
 expect(review_window.locator('[data-semantic-after]')).to_have_text(description)
 expect(review_window.locator('[data-source-before]')).to_have_count(0)
 assert 'object Example.ButtonGame::test' not in review_window.inner_text()
 assert '현재 소스' not in review_window.inner_text() and '공유 초안' not in review_window.inner_text()
 page.screenshot(path='/tmp/confectory-description-semantic-review.png',full_page=True)
 review_window.locator('[data-review-advanced]').click()
 expect(review_window.locator('[data-source-after]')).to_contain_text('object '+prefix+'test')
 page.locator('.window[data-key="review"] [data-reject]').click()
 expect(field).to_have_value(description);assert 'created through ordinary editor' in source_path.read_text()
 page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 assert (project/'project.cpack').read_bytes()==manifest_before, 'description edit changed registrations/references'
 assert 'object '+prefix+'test' in source_path.read_text() and 'value initial = 2;' in source_path.read_text()
 # Actual short-description inline layout, followed by long/narrow text without truncation.
 field.fill('하하');page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000);page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 field.fill('하하?');page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 review_window=page.locator('.window[data-key="review"]');row=review_window.locator('[data-semantic-change]')
 expect(row).to_have_text('설명하하→하하?');boxes=[row.locator(selector).bounding_box() for selector in ('[data-review-group]','strong','[data-semantic-before]','[aria-hidden]','[data-semantic-after]')];assert max(b['y'] for b in boxes)-min(b['y'] for b in boxes)<8,boxes
 for selector in ('[data-semantic-before]','[data-semantic-after]'):expect(row.locator(selector)).to_have_attribute('role','group')
 page.screenshot(path='/tmp/confectory-review-short-inline.png',full_page=True)
 review_window.locator('[data-review-group]').uncheck();expect(page.locator('#confirm')).to_be_disabled();review_window.locator('[data-reject]').click();expect(review_window).to_have_count(0)
 expect(field).to_have_value('하하?');assert '하하?' not in source_path.read_text()
 # Add an independent real Score draft, then exclude it with a fresh exact subset Review.
 close();browser();page.locator('[data-id="'+prefix+'Score"]').click();expect(page.locator('[data-schema-field="initial"]')).to_be_visible(timeout=30000)
 score_source=(project/'Score.celem').read_bytes();score=page.locator('[data-schema-field="initial"]');score.fill('9');score.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
 page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 close();browser();page.locator('[data-id="'+prefix+'test"]').click();expect(field).to_be_visible(timeout=30000)
 description='긴 설명 <script>literal</script> "인용" & 내용\n'+('끊기지않는내용'*25)+'\n마지막 줄'
 field.fill(description);page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
 close();browser();browser_action('#advanced-source');page.locator('.browser-tools input[type="range"]').press('End');expect(page.locator('#density-label')).to_have_text('Data')
 for id in (prefix+'Score',prefix+'test'):page.locator('[data-review-id="'+id+'"]').check()
 browser_action('#review-group');expect(review_window.locator('[data-review-group]')).to_have_count(2,timeout=30000)
 mounted=mount();old_token=mounted['state']['review']['token'];assert send(envelope(mounted,'dispose'))['ok']
 for check in review_window.locator('[data-review-group]').all():check.uncheck()
 expect(page.locator('#confirm')).to_be_disabled();expect(review_window.locator('[data-rereview]')).to_be_disabled()
 review_window.get_by_role('checkbox',name='test · 전체 변경',exact=True).check();expect(page.locator('#confirm')).to_be_disabled();expect(review_window.locator('[data-rereview]')).to_be_enabled()
 review_window.locator('[data-rereview]').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 fresh_review=mount();assert fresh_review['state']['review']['token']!=old_token and [u['id'] for u in fresh_review['state']['review']['units']]==[prefix+'test'];assert send(envelope(fresh_review,'dispose'))['ok']
 expect(review_window.locator('[data-semantic-after]')).to_have_text(description);expect(review_window.locator('script')).to_have_count(0)
 # Resize the actual Review through its normal handle; compare full content and scroll width.
 handle=review_window.locator('[data-resize="se"]');box=handle.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.mouse.move(box['x']-160,box['y']+box['height']/2,steps=8);page.mouse.up()
 expect(review_window.locator('[data-semantic-after]')).to_have_text(description)
 assert review_window.locator('.window-content').evaluate('(e)=>e.scrollWidth<=e.clientWidth+2'), 'narrow Review overflows horizontally'
 page.screenshot(path='/tmp/confectory-review-long-narrow.png',full_page=True)
 review_window.locator('[data-review-advanced]').click();expect(review_window.locator('[data-review-source]')).to_be_visible();review_window.locator('[data-review-advanced]').click();expect(review_window.locator('[data-review-source]')).to_be_hidden()
 review_window.locator('[data-close]').click();expect(review_window).to_have_count(0);assert (project/'Score.celem').read_bytes()==score_source
 # Reopen the previously reviewed subset explicitly through ordinary browser selection.
 browser();browser_action('#review-group');expect(review_window.locator('[data-review-group]')).to_have_count(2,timeout=30000)
 review_window.get_by_role('checkbox',name='Score · 전체 변경',exact=True).uncheck();review_window.locator('[data-rereview]').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 assert (project/'Score.celem').read_bytes()==score_source and (project/'project.cpack').read_bytes()==manifest_before
 print('PASS actual Review controls: dependency group, selection/all off, fresh subset token, advanced repeated toggle, X/cancel/reopen, short inline/long narrow/escaping, unselected source untouched',flush=True)
 print('PASS ordinary description form: shared draft Save, stale revision rejection, Review cancel retains draft, exact Confirm, unchanged ID/value/manifest',flush=True)

 close();browser();page.locator('.window[data-key="browser"] [data-tab="concept"]').click()
 expect(page.locator('[data-id="'+prefix+'test"]')).to_be_visible(timeout=30000)
 print('PASS normal lowercase test creation: dirty declaration+registration, Save, editable values, explicit Review, compiler Confirm, actual browser',flush=True)
 # A fresh actual EditorHome process must discover the confirmed manifest and source, not live draft rows.
 restart()
 browser();page.locator('.window[data-key="browser"] [data-tab="concept"]').click()
 expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000)
 expect(page.locator('[data-id="'+prefix+'test"]')).to_be_visible(timeout=30000)
 # Restored floating windows keep their placement. Close the restored Run and
 # property presentations through their ordinary controls before selecting the row.
 run_close=page.locator('.window[data-key="run"] [data-close]')
 if run_close.count():run_close.click()
 close()
 page.locator('[data-id="'+prefix+'test"]').click()
 expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'test',timeout=30000)
 expect(page.locator('[data-schema-field="initial"]')).to_have_value('2',timeout=30000)
 expect(page.locator('.window[data-key="schema"] [data-description]')).to_have_value(description)
 fresh=mount();assert fresh['state']['draft']['id']==prefix+'test' and not fresh['state']['draft']['dirty'] and not fresh['state']['draft']['creationReviewIds'];assert send(envelope(fresh,'dispose'))['ok']
 page.screenshot(path='/tmp/confectory-new-concept-reopened.png',full_page=True)
 print('PASS new concept actual process reopen: source+registration discovery, editable saved value, actual description, clean draft',flush=True)
