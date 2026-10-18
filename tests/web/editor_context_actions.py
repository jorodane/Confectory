"""Declared context actions: real typed SetValue call, no application or generic executor."""
import copy,json,shutil,uuid
from playwright.sync_api import expect

def prepare_context_actions(project,root,repo):
 library=root/'schema-editing';shutil.copytree(repo/'packs/schema-editing',library)
 manifest=project/'project.cpack';text=manifest.read_text();at=text.rfind('}')
 text=text[:at]+'registry Confectory.SchemaEditing '+json.dumps(str(library/'pack.cpack'))+';dependency Confectory.SchemaEditing version "0.1.0";element Menu object "Menu.celem";element UnboundMenu object "UnboundMenu.celem";'+text[at:];manifest.write_text(text)
 action=(repo/'examples/editor-context-actions/MetadataProposal.celem').read_text().replace('Example.EditorContextActions::MetadataProposal','Example.ButtonGame::Menu');(project/'Menu.celem').write_text(action)
 (project/'UnboundMenu.celem').write_text('object Example.ButtonGame::UnboundMenu {value editorContextMenu = true;value editorName = "등록만 된 기능";provide Example.ButtonGame::Main with Example.ButtonGame::MainBody;}')
 plugin=root/'menu-pack';plugin.mkdir();(plugin/'pack.cpack').write_text('pack Example.ActionPack version "1" {dependency Confectory.SchemaEditing version "0.1.0";element Menu object "Menu.celem";}');(plugin/'Menu.celem').write_text(action.replace('Example.ButtonGame::Menu','Example.ActionPack::Menu').replace('메타데이터 변경안','팩의 변경안'))
 text=manifest.read_text();at=text.rfind('}');manifest.write_text(text[:at]+'registry Example.ActionPack '+json.dumps(str(plugin/'pack.cpack'))+';dependency Example.ActionPack version "1";'+text[at:])
 second=root/'second-project';shutil.copytree(project,second,ignore=shutil.ignore_patterns('.confectory'))
 storage=root/'storage';storage.mkdir(exist_ok=True);(storage/'projects.json').write_text(json.dumps([{'path':str(folder/'project.cpack'),'title':name,'description':'Owned context action fixture'} for folder,name in [(project,'Actions A'),(second,'Actions B')]]))

def verify_context_actions(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2200,'height':1400});id='Example.ButtonGame::Score';aid='Example.ButtonGame::Menu';initial={f:f.read_bytes() for f in project.iterdir() if f.is_file()}
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(args,ok=True,endpoint='contextActions'):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,input=args,requestId=rid,expectedRevision=v['revision']))['ok'];result,_=settle(v,rid);assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result.get('result')
 def request(**data):return {'projectId':state()['projectId'],**data}
 def listing():return invoke(request(operation='list',id=id,target='linux'))
 def call(menu,ok=True):return invoke(request(operation='invoke',token=menu['token'],actionId=aid,field='initial',value='23'),ok)
 def nav():
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def menu():
  ready();page.locator('[data-id="'+id+'"]').click(button='right');page.wait_for_function("()=>document.querySelector('.context-menu')?.textContent.includes('등록 기능 ·')||document.querySelector('.context-menu')?.textContent.includes('조회 실패')",timeout=120000)
  failed=page.get_by_role('button',name='등록 기능 조회 실패 · 다시 여세요',exact=True)
  if failed.count():failed.click();raise AssertionError('Menu discovery failed: '+page.locator('#status').inner_text())
  expect(page.get_by_role('button',name='등록 기능 · 메타데이터 변경안',exact=True)).to_be_visible()
 def form():menu();page.get_by_role('button',name='등록 기능 · 메타데이터 변경안',exact=True).click();return page.get_by_role('dialog',name='메타데이터 변경안',exact=True)
 nav();page.locator('[data-id="'+id+'"]').click();ready();page.locator('.window[data-key="schema"] [data-close]').click();before=state()['draft'];page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();source=page.locator('#source');pending=source.input_value()+'\n// PRIVATE_MENU_INPUT';source.fill(pending);source.evaluate('e=>globalThis.__menuSource=e');menu();expect(page.get_by_role('button',name='예시 · 전투 테스트 · 미지원',exact=True)).to_be_visible();expect(page.get_by_role('button',name='등록 기능 · 등록만 된 기능 · 미지원',exact=True)).to_be_visible();page.keyboard.press('Escape');page.locator('#workspace').click(position={'x':1700,'y':800});assert state()['draft']==before
 d=form();d.locator('[data-action-field]').fill('initial');d.locator('[data-action-value]').fill('23');d.locator('[data-action-cancel]').click();expect(d).to_have_count(0);assert state()['draft']==before
 d=form();d.locator('[data-action-field]').fill('initial');d.locator('[data-action-value]').fill('23');d.locator('[data-action-invoke]').dblclick();expect(d).to_have_attribute('data-action-status','completed',timeout=120000);expect(d.locator('[data-action-result]')).to_contain_text('value initial = 23;');assert state()['draft']==before;page.screenshot(path='/tmp/confectory-context-actions.png',full_page=True);d.locator('[data-close]').click()
 d=form();d.locator('[data-action-field]').fill('initial');d.locator('[data-action-value]').fill('null');d.locator('[data-action-invoke]').click();expect(d).to_have_attribute('data-action-status','failed',timeout=120000);expect(d.locator('[data-action-result]')).to_contain_text('Scalar metadata required');expect(d.locator('[data-action-value]')).to_have_value('null');assert state()['draft']==before;d.locator('[data-close]').click()
 # The returned transformed source proves SetValue actually ran; CheckCall cannot produce this output.
 fresh=listing();result=call(fresh);assert result['status']=='completed' and result['executed'] and not result['sourceWritten'];assert 'value initial = 23;' in result['output'];assert call(fresh)==result;invoke(request(operation='invoke',token=fresh['token'],actionId=aid,field='initial',value='24'),False)
 plugin_menu=listing();assert any(a['id']=='Example.ActionPack::Menu' and a['available'] for a in plugin_menu['actions']);result=invoke(request(operation='invoke',token=plugin_menu['token'],actionId='Example.ActionPack::Menu',field='initial',value='31'));assert result['status']=='completed' and 'value initial = 31;' in result['output']
 canceled=listing();invoke(request(operation='cancel',token=canceled['token']));invoke(request(operation='invoke',token=canceled['token'],actionId=aid,field='initial',value='23'),False)
 bad=listing();failure=invoke(request(operation='invoke',token=bad['token'],actionId=aid,field='initial',value='null'));assert failure['status']=='failed' and failure['executed'] and 'Scalar metadata required' in failure['message'];assert state()['draft']==before
 # Main selection and current draft version are independent fences on a prepared menu.
 old=listing();invoke({'id':'Example.ButtonGame::Menu'},endpoint='select');call(old,False);invoke({'id':id},endpoint='select');call(old,False)
 stale=listing();s=state()['draft'];invoke({'id':id,'text':s['text'].replace('{','{ value preserved = 91;',1)+'\n// CURRENT_ACTION_DRAFT','revision':s['revision']},endpoint='editDraft');failure=call(stale);assert failure['status']=='failed' and not failure['executed'];current=copy.deepcopy(state()['draft']);assert 'CURRENT_ACTION_DRAFT' in current['text']
 fresh=listing();result=call(fresh);assert result['status']=='completed' and 'value preserved = 91;' in result['output'],result;assert state()['draft']==current;expect(source).to_have_value(pending);assert source.evaluate('e=>e===globalThis.__menuSource')
 # A removed context, changed action source, changed trusted body and target mismatch never dispatch.
 old=listing();source_file=project/'Score.celem';raw=source_file.read_bytes();source_file.unlink();failure=call(old);assert failure['status']=='failed' and not failure['executed'];source_file.write_bytes(raw)
 old=listing();registration=project/'Menu.celem';raw=registration.read_bytes();registration.write_bytes(raw+b'\n// REGISTRATION_CHANGED');failure=call(old);assert failure['status']=='failed' and not failure['executed'];registration.write_bytes(raw)
 old=listing();body=project.parent/'schema-editing/SetValue.csbody';raw=body.read_bytes();body.write_bytes(raw+b'\n// SAME_ID_DIFFERENT_BODY');changed=listing();action=next(a for a in changed['actions'] if a['id']==aid);assert not action['available'] and 'version changed' in action['reason'];failure=call(old);assert failure['status']=='failed' and not failure['executed'];body.write_bytes(raw)
 unavailable=invoke(request(operation='list',id=id,target='android'));assert not any(a['available'] for a in unavailable['actions'])
 old=listing();pid=state()['projectId'];page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Actions B').locator('[data-enter]').click();ready();invoke(request(operation='invoke',token=old['token'],actionId=aid,field='initial',value='23'),False);page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Actions A').locator('[data-enter]').click();ready();assert state()['projectId']==pid;assert state()['draft']['text']==current['text'];call(old,False)
 # Closing the host retires every prepared capability; registration survives as source metadata only.
 old=listing();page.evaluate('()=>globalThis.confectoryFlushPresentation()');private=state()['presentation']['inputs']['source'];assert private['text']==pending and private['draft']['revision']==before['revision'];restart();ready();expect(source).to_have_value(pending);invoke(request(operation='invoke',token=old['token'],actionId=aid,field='initial',value='23'),False)
 for f,raw in initial.items():assert f.read_bytes()==raw,f
 assert not (project/'.confectory/project-activity').exists()
 print('PASS actual declared context actions: discovery vs unbound/example, explicit input and real SetValue output, no draft/source write, cancel and duplicate token, changed selection/revision/deletion/registration/body/target/project, cold token retirement and failed function result',flush=True)
