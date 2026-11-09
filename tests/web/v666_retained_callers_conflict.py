"""Real keyboard activation of Save must reject a peer's changed owner source."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_retained_callers_fixture as x
f,d=x.f,x.d
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  for index in range(2):x.after_contract(index)
  held=d.pending();assert len(held)==2;sc=f.state()['schema'];f.invoke('editDescription',dict(id=x.owner,hash=sc['textHash'],revision=sc['revision'],value='peer 설명 보존'))
  f.page.evaluate("""()=>{globalThis.conflictEvents=[];for(const type of ['keydown','click'])document.addEventListener(type,e=>{const b=e.target.closest?.('[data-element-action=save]');if(b)conflictEvents.push({type,key:e.key,trusted:e.isTrusted,disabled:b.disabled,connected:b.isConnected,handler:typeof b.onclick})},true);globalThis.boundaryMessages=[];const collect=()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text))boundaryMessages.push(text)}};collect();globalThis.boundaryObserver=new MutationObserver(collect);boundaryObserver.observe(document.body,{subtree:true,childList:true,characterData:true})}""")
  mark=len(f.traffic);button=f.owner().locator('[data-element-action=save]');button.focus();button.press('Enter');f.page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000);f.idle();events=f.page.evaluate('()=>conflictEvents');assert any(e['type']=='click'and e['trusted']and e['handler']=='function'for e in events),events
  ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};assert not any(row.get('result',{}).get('requestId')in ids and row['result'].get('ok')for row in f.traffic[mark:]);assert d.pending()==held and checkpoint.read_bytes()==baseline;assert f.metadata('inspect',text=f.state()['draft']['text'])['description']=='peer 설명 보존';x.unchanged();(f.case/'keyboard-conflict.json').write_text(json.dumps(dict(events=events,messages=f.page.evaluate('()=>boundaryMessages'),pending=d.pending(),traffic=f.traffic[mark:]),ensure_ascii=False,indent=2));f.checked('actual trusted Enter/click on existing Save rejects a peer owner change, retaining both native inputs, original checkpoint and peer text');assert not f.errors and not f.external;f.browser.close()
except Exception:
 failure=dict(traffic=f.traffic[-60:],checks=f.checks)
 try:failure.update(events=f.page.evaluate('()=>globalThis.conflictEvents'),messages=f.page.evaluate('()=>globalThis.boundaryMessages'),errors=f.page.locator('[data-element-error]').all_text_contents(),pending=d.pending());f.page.screenshot(path=str(f.case/'keyboard-conflict-failure.png'))
 except Exception:pass
 (f.case/'keyboard-conflict-failure.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2));raise
finally:f.stop()
