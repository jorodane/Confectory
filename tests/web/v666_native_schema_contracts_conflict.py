"""Observe actual trusted Save activation before asserting the stale boundary."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v666_native_schema_contracts_fixture as x
f,d=x.f,x.d;events=[];peer='peer 설명 보존'
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});d.open_info()
  for index in range(2):
   if True:
    f.owner().locator('[data-inline-method="'+x.functions[index]+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});popup=f.page.locator('.function-detail-popover');expect(popup).to_be_visible();x.edit_contract(popup,index);popup.get_by_role('button',name='저장',exact=True).click();expect(popup).to_have_count(0)
   x.after_contract(index)
  held=d.pending();assert len(held)==5;x.unchanged();schema=f.state()['schema'];f.invoke('editDescription',dict(id=x.owner,hash=schema['textHash'],revision=schema['revision'],value=peer));f.invoke('schema',dict(id=x.owner));f.idle()
  def trace(source,payload):
   events.append(payload);(f.case/'conflict-activation-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
  f.page.expose_binding('recordNamedImportActivation',trace);f.page.evaluate("""()=>{globalThis.boundaryMessages=[];const collect=()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text))boundaryMessages.push(text)}};collect();new MutationObserver(collect).observe(document.body,{subtree:true,childList:true,characterData:true});for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,e=>{const b=e.target.closest?.('[data-element-action=save]');if(b)window.recordNamedImportActivation({type,trusted:e.isTrusted,disabled:b.disabled,connected:b.isConnected,handler:typeof b.onclick})},true)}""")
  mark=len(f.traffic);button=f.owner().locator('[data-element-action=save]');expect(button).to_be_enabled();button.click();f.idle();deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   messages=f.page.evaluate('()=>boundaryMessages');requests=[r for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots']
   if requests or any(__import__('re').search('바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed',text,__import__('re').I)for text in messages):break
   f.page.wait_for_timeout(50)
  # A refresh can consume pointer activation before a trusted click is issued.
  # Retry only that undelivered UI action, with no command/checkpoint mutation.
  if not requests and not any(e['type']=='click'and e['trusted']for e in events):
   assert d.pending()==held and checkpoint.read_bytes()==baseline;x.unchanged();expect(button).to_be_enabled();button.click();f.idle()
  f.page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000);f.idle();assert any(e['type']=='click'and e['trusted']for e in events);ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'};assert not any(r.get('result',{}).get('requestId')in ids and r['result'].get('ok')for r in f.traffic[mark:]);assert d.pending()==held and checkpoint.read_bytes()==baseline and f.metadata('inspect',text=f.state()['draft']['text'])['description']==peer;x.unchanged();f.checked('observed trusted Save rejects the peer-changed owner without applying either explicit type/body edit; checkpoint, peer, original helper sources and all four inputs remain intact');assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'conflict-activation-failure.png'))
 except Exception:pass
 (f.case/'conflict-activation-failure.json').write_text(json.dumps(dict(events=events,traffic=f.traffic[-60:],checks=f.checks),ensure_ascii=False,indent=2));raise
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
