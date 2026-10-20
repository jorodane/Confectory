from editor_navigation import open_project_tools
"""Owned source Rename through the ordinary host, browser, transport and cold restore."""
import json,uuid,copy
from pathlib import Path
from playwright.sync_api import expect

def verify_rename(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2200,'height':1400});graph='Example.ButtonGame::NodeValueBody/body:common';other='Example.ButtonGame::OtherValueBody/body:common';original={p:p.read_bytes() for d in [project,project.parent/'second-project'] for p in d.iterdir() if p.is_file()}
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def panel():return window('blueprint')
 def label():return panel().locator('[data-bp-name="calculate"]')
 def edit():return label().locator('[data-bp-rename]')
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,input=args,requestId=rid,expectedRevision=v['revision']))['ok'];result,_=settle(v,rid);assert send(envelope(v,'dispose'))['ok'];assert result['ok'],result;return result.get('result')
 def read():return invoke('blueprint',dict(action='read',id=graph))
 def node(data):return next(n for n in data['nodes'] if n['id']=='calculate')
 def nav(text):
  ready();open_project_tools(page);page.locator('.nav-menu').get_by_role('button',name=text,exact=True).click();ready()
  if page.locator('.nav-menu').count():open_project_tools(page)
 def select():panel().locator('[data-bp-select="calculate"]').click();ready()
 def f2():front();label().focus();page.keyboard.press('F2');expect(edit()).to_be_visible()
 def commit(text):edit().fill(text);edit().press('Enter');ready()
 def front():
  title=panel().locator('.window-title');point=title.evaluate("e=>{const r=e.getBoundingClientRect();for(const f of [.8,.6,.3,.95]){const x=Math.floor(r.width*f),y=18,hit=document.elementFromPoint(r.left+x,r.top+y);if(hit&&e.contains(hit)&&!hit.closest('button'))return {x,y}}return null}");assert point;title.click(position=point)
 nav('기능 Blueprint');initial=read();assert node(initial)['displayName']=='calculate';profile=initial['profile'];definitions={n['id']:n['definitionHash'] for n in initial['nodes']};select();panel().locator('[data-bp-fit]').click()
 # Dragging the name remains movement, including when the node already has focus.
 box=label().bounding_box();page.mouse.move(box['x']+20,box['y']+8);page.mouse.down();page.mouse.move(box['x']+55,box['y']+23,steps=6);page.mouse.up();expect(edit()).to_have_count(0);assert node(read())['displayName']=='calculate'
 label().click();expect(edit()).to_be_visible();edit().fill('취소할 이름');edit().press('Escape');expect(edit()).to_have_count(0);assert node(read())['displayName']=='calculate'
 f2();edit().fill('한글 이름');edit().evaluate("e=>e.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',isComposing:true,bubbles:true}))");expect(edit()).to_be_visible();assert node(read())['displayName']=='calculate'
 edit().evaluate("e=>e.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:229,bubbles:true}))");expect(edit()).to_have_value('한글 이름');assert node(read())['displayName']=='calculate';edit().press('Enter');ready();expect(edit()).to_have_count(0);assert node(read())['displayName']=='한글 이름'
 f2();edit().fill('반복 입력 유지');page.keyboard.press('F2');edit().click();expect(edit()).to_have_value('반복 입력 유지');edit().press('Escape');f2();commit('   ');expect(edit()).to_have_count(0);assert node(read())['displayName']=='한글 이름'
 label().click(button='right');page.get_by_role('menuitem',name='Rename · F2',exact=True).click();commit('메뉴로 변경');assert node(read())['displayName']=='메뉴로 변경'
 # Another ordinary editor changes the exact graph basis while the name stays unsent.
 f2();edit().fill('CAS 입력 유지');before=read();invoke('blueprint',dict(action='intent',id=graph,node='calculate',basis=before['basis'],text='Changed behavior needs source reapplication'))
 edit().press('Enter');ready();expect(edit()).to_have_value('CAS 입력 유지');expect(page.locator('#status')).to_contain_text('입력은 유지됩니다');assert node(read())['displayName']=='메뉴로 변경'
 panel().locator('[data-bp-read]').click();ready();f2();expect(edit()).to_have_value('CAS 입력 유지');label().get_by_role('button',name='표시 이름 기준 재검토',exact=True).click();edit().press('Enter');ready();assert node(read())['displayName']=='CAS 입력 유지' and node(read())['sourceStatus']=='stale'
 # Other unsent inputs refuse Apply without consuming either buffer or its basis.
 panel().locator('[data-bp-intent]').fill('UNSENT_INTENT');f2();commit('이름도 미적용');expect(edit()).to_have_value('이름도 미적용');expect(panel().locator('[data-bp-intent]')).to_have_value('UNSENT_INTENT');assert node(read())['displayName']=='CAS 입력 유지';edit().press('Escape')
 panel().locator('[data-bp-intent]').locator('..').locator('[data-reset]').click()
 panel().locator('[data-bp-code-open="calculate"]').click();cw=window('blueprint-code:'+graph+'/calculate');cw.locator('[data-bp-code]').fill('return value + 77; // UNSENT_CODE');cw.locator('[data-close]').click();f2();commit('코드와 함께 보존');expect(edit()).to_have_value('코드와 함께 보존');edit().press('Escape');panel().locator('[data-bp-code-open="calculate"]').click();expect(cw.locator('[data-bp-code]')).to_have_value('return value + 77; // UNSENT_CODE');cw.locator('[data-reset]').click();cw.locator('[data-close]').click()
 # Same node IDs in another graph/project cannot consume or submit this name.
 f2();edit().fill('COLD_UNSENT_NAME');panel().locator('[data-bp-tab="'+other+'"]').click();ready();select();f2();expect(edit()).to_have_value('calculate');edit().press('Escape');panel().locator('[data-bp-tab="'+graph+'"]').click();ready();f2();expect(edit()).to_have_value('COLD_UNSENT_NAME')
 page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Overview B').locator('[data-enter]').click();ready();nav('기능 Blueprint');select();f2();expect(edit()).to_have_value('calculate');edit().press('Escape');page.locator('.brand').click();page.locator('[data-project]').filter(has_text='Overview A').locator('[data-enter]').click();ready();front();panel().locator('[data-bp-read]').click();ready();f2();expect(edit()).to_have_value('COLD_UNSENT_NAME')
 invoke('saveDraft',{});restart();ready();front();panel().locator('[data-bp-read]').click();ready();f2();expect(edit()).to_have_value('COLD_UNSENT_NAME');edit().press('Enter');ready();expect(page.locator('#status')).to_contain_text('기준 재검토');expect(edit()).to_have_value('COLD_UNSENT_NAME');assert node(read())['displayName']=='CAS 입력 유지'
 label().get_by_role('button',name='표시 이름 기준 재검토',exact=True).click();edit().press('Enter');ready();assert node(read())['displayName']=='COLD_UNSENT_NAME' and node(read())['sourceStatus']=='stale'
 final=read();assert final['profile']==profile and final['signature']==initial['signature'] and final['edges']==initial['edges'];assert node(final)['definitionHash']!=definitions['calculate'];assert all(p.read_bytes()==raw for p,raw in original.items())
 evidence=dict(imeEnter=['isComposing','keyCode229'],cancel=['Escape','blank'],dragBeforeRename=True,focusedClickF2Context=True,casRefusedAndRebased=True,unsentIntentAndCodePreserved=True,graphs=2,projects=2,coldUnsentBasisRefused=True,persistedDisplayName=node(final)['displayName'],staleCompletionRemainsStale=True,profileSignatureRoutesPreserved=True,originalFiles=len(original),actualBrowser='Chromium ordinary EditorHome host')
 page.screenshot(path='/tmp/confectory-v508-rename.png',full_page=True);Path('/workspace/scratch/confectory-v508-rename-ui.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n');print('PASS actual v508 Blueprint rename '+json.dumps(evidence,ensure_ascii=False),flush=True)
