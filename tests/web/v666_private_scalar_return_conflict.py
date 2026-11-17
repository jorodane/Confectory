"""Conflict-only trusted activation observation; preserve all original flow assertions."""
import pathlib
path=pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py');source=path.read_text();start=source.index('def reject_conflict():');end=source.index('def finish_early():',start)
replacement=r'''def reject_conflict():
    events=[]
    def trace(binding,event):
        events.append(event);(f.case/'conflict-activation-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
    f.invoke('schema',dict(id=x.owner));f.idle()
    f.page.expose_binding('recordNativeChainActivation',trace)
    f.page.evaluate("""()=>{globalThis.boundaryMessages=[];const collect=()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text))boundaryMessages.push(text)}};collect();globalThis.boundaryObserver=new MutationObserver(collect);boundaryObserver.observe(document.body,{subtree:true,childList:true,characterData:true});for(const type of ['pointerdown','pointerup','click'])document.addEventListener(type,e=>{const b=e.target.closest?.('[data-element-action=save]');if(b)window.recordNativeChainActivation({type,trusted:e.isTrusted,disabled:b.disabled,connected:b.isConnected,handler:typeof b.onclick})},true)}""")
    mark=len(f.traffic)
    def requests():return [r for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots']
    def rejected():return f.page.evaluate('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))')
    try:
        button=f.owner().locator('[data-element-action=save]');expect(button).to_be_enabled();button.click();deadline=time.monotonic()+30
        while time.monotonic()<deadline and not requests()and not rejected():f.page.wait_for_timeout(50)
        # Retry only an observed undelivered UI activation, never a command.
        if not requests()and not any(e['type']=='click'and e['trusted']for e in events):
            assert pending()==held and checkpoint.read_bytes()==baseline;x.unchanged();expect(button).to_be_enabled();button.click()
        f.page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000);f.idle()
        assert any(e['type']=='click'and e['trusted']for e in events)
        ids={r['invoke']['requestId']for r in requests()};assert not any(r.get('result',{}).get('requestId')in ids and r['result'].get('ok')for r in f.traffic[mark:])
        (f.case/'conflict-activation-proof.json').write_text(json.dumps(dict(events=events,requests=list(ids),messages=f.page.evaluate('()=>boundaryMessages'),checkpointRetained=checkpoint.read_bytes()==baseline,inputRetained=pending()==held),ensure_ascii=False,indent=2))
    finally:f.page.evaluate('()=>boundaryObserver.disconnect()')
'''
assert source.count('def reject_conflict():')==1
exec(compile(source[:start]+replacement+source[end:],str(path),'exec'),globals())
