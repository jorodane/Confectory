"""A peer refresh between pointerdown and release must preserve the Save target."""
import json
from playwright.sync_api import sync_playwright,expect
import v666_retained_callers_fixture as x
f,d=x.f,x.d;mine='저장 전 내 설명 입력';peer='peer 설명 보존'
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info();f.owner().locator('.object-title-description').fill(mine);f.idle();held=d.pending();assert len(held)==1
  def trace(source,payload):
   with(f.case/'activation-events.jsonl').open('a')as out:out.write(json.dumps(payload,ensure_ascii=False)+'\n')
  f.page.expose_binding('recordActivation',trace)
  f.page.evaluate("""()=>{globalThis.pressedSave=document.querySelector('.window[data-key=schema] [data-element-action=save]');globalThis.oldError=document.querySelector('.window[data-key=schema] [data-element-error]');globalThis.boundaryMessages=[];const collect=()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text)){boundaryMessages.push(text);window.recordActivation({message:text})}}};collect();new MutationObserver(collect).observe(document.body,{subtree:true,childList:true,characterData:true});for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,e=>{const b=e.target.closest?.('[data-element-action=save]');if(b)window.recordActivation({type,trusted:e.isTrusted,disabled:b.disabled,connected:b.isConnected,same:b===pressedSave,handler:typeof b.onclick})},true)}""")
  button=f.owner().locator('[data-element-action=save]');expect(button).to_be_enabled();box=button.bounding_box();f.page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);f.page.mouse.down();sc=f.state()['schema'];f.invoke('editDescription',dict(id=x.owner,hash=sc['textHash'],revision=sc['revision'],value=peer));f.invoke('schema',dict(id=x.owner));f.page.wait_for_function('()=>!oldError.isConnected',timeout=30000);expect(button).to_be_enabled();identity=f.page.evaluate('()=>({same:pressedSave===document.querySelector(".window[data-key=schema] [data-element-action=save]"),connected:pressedSave.isConnected})');(f.case/'button-identity.json').write_text(json.dumps(identity))
  mark=len(f.traffic);f.page.mouse.up()
  if x.mode=='reproduce-activation':
   assert identity==dict(same=False,connected=False),identity;f.idle();assert d.pending()==held and checkpoint.read_bytes()==baseline;assert not any(t.get('invoke',{}).get('endpoint')=='blueprint'and t['invoke']['input'].get('action')=='applySlots'for t in f.traffic[mark:]);x.unchanged();f.checked('published refresh replaces the pressed Save DOM node; release issues no Save, retaining input/checkpoint/peer');f.browser.close();raise SystemExit(0)
  assert identity==dict(same=True,connected=True),identity;f.page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000);f.idle();assert d.pending()==held and checkpoint.read_bytes()==baseline;assert f.metadata('inspect',text=f.state()['draft']['text'])['description']==peer;x.unchanged();f.checked('same-project/owner refresh keeps the pressed Save node and current handler; release rejects stale input without applying or discarding it');assert not f.errors and not f.external;f.browser.close()
except Exception:
 (f.case/'activation-failure.json').write_text(json.dumps(dict(traffic=f.traffic[-60:],checks=f.checks),ensure_ascii=False,indent=2));raise
finally:f.stop()
