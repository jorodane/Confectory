"""Actual local browser diagnostics, no project text or chat in the result.

Run with REPO BUILD_REPORT and the standard local EditorHome fixture variables.
Windows native timing is a separate host file; this test exercises the shared
renderer/engine collector on Linux Chromium without a Windows device.
"""
import json, time
from playwright.sync_api import expect, sync_playwright
import v821_property_window_reopen_ui as r
from editor_navigation import goto_editor

f,d=r.fixture,r.fallback
r.seed()
local=f.root/'local-appdata';local.mkdir()
f.env['XDG_DATA_HOME']=str(local)
f.env.pop('CONFECTORY_PERFORMANCE',None)
root=local/'Confectory'/'Performance'
secret='PRIVATE_PERFORMANCE_SENTINEL_79d2'
expect.set_options(timeout=60000)

def records(path):
    if not path.exists():return []
    result=[]
    for line in path.read_text().splitlines():
        try:result.append(json.loads(line))
        except json.JSONDecodeError:pass # writer may be appending the final line
    return result

def current_file():
    files=list(root.glob('*/engine.jsonl'))
    assert len(files)>0,root
    return max(files,key=lambda path:path.stat().st_mtime_ns)

def wait_records(page,path,condition):
    end=time.monotonic()+30
    while time.monotonic()<end:
        data=records(path)
        if condition(data):return data
        page.wait_for_timeout(100)
    raise AssertionError((path,records(path)[-15:]))

try:
    with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']) as browser:
        f.start(0);page=f.setup(browser)
        mounted=f.mount();assert mounted.get('performance') is not True
        denied=f.raw({'op':'performance','view':mounted['view'],'scope':mounted['scope'],'rows':[{'stage':'input-delay','operation':'click','elapsedMs':1,'pageMs':1}]})
        assert not denied['ok']
        f.raw({'op':'dispose','view':mounted['view']});page.close();f.stop();assert not root.exists()
        f.env['CONFECTORY_PERFORMANCE']='1';f.start(1);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200})
        path=current_file()
        w,_=r.floating.open_properties(page,d.TARGET,'StockFolder')
        r.floating.property_value(w,'Note').fill(secret)
        page.locator('#chat-input').fill(secret)
        mounted=f.mount();assert mounted['performance'] is True
        # Even a local mounted page cannot emit arbitrary data into the capture.
        bad={'stage':'renderer-call','operation':secret,'elapsedMs':1,'pageMs':1}
        f.raw({'op':'performance','view':mounted['view'],'scope':mounted['scope'],'rows':[bad]})
        denied=f.raw({'op':'performance','view':mounted['view'],'scope':mounted['scope'],'rows':[dict(bad,text=secret)]});assert not denied['ok']
        f.raw({'op':'dispose','view':mounted['view']})
        expect(r.floating.property_value(w,'Note')).to_have_value(secret)
        page.evaluate('()=>confectoryFlushPresentation()')
        rows=wait_records(page,path,lambda a: any(x.get('stage')=='window-ready' for x in a) and any(x.get('stage')=='input-frame' for x in a))
        assert any(x.get('stage')=='renderer-call' and x.get('operation')=='openEditorView' for x in rows)
        assert any(x.get('stage')=='consumer' and x.get('operation')=='openEditorView' for x in rows)
        assert any(x.get('stage')=='invoke-queue' and x.get('operation')=='openEditorView' for x in rows)
        assert any(x.get('stage') in ('authoring-stream','authoring-process') for x in rows)
        assert secret not in path.read_text()
        page.close();f.stop()
        f.env.pop('CONFECTORY_WEB_PROJECT',None);f.start(2);page=browser.new_page(viewport={'width':2000,'height':1200});goto_editor(page,f.url)
        page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').click()
        expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(1)
        expect(r.floating.property_value(page.locator('.window[data-key="editor-1"]'),'Note')).to_have_value(secret)
        path=current_file();rows=wait_records(page,path,lambda a: all(any(x.get('stage')==stage for x in a) for stage in ('restore-view','restore-total','restore-layout','workspace-attach')))
        assert secret not in path.read_text()
        # The writer is bounded even if a mounted diagnostic client sends more
        # data than an ordinary capture. This never runs a domain command.
        mounted=f.mount();batch=[{'stage':'input-frame','operation':'click','elapsedMs':1,'pageMs':1}]*32
        for _ in range(260):
            assert f.raw({'op':'performance','view':mounted['view'],'scope':mounted['scope'],'rows':batch})['ok']
        f.raw({'op':'dispose','view':mounted['view']})
        capped=wait_records(page,path,lambda a:any(x.get('stage')=='capture-limit' for x in a))
        assert len(capped)==8192
        for file in root.glob('*/engine.jsonl'):

            data=records(file);assert len(data)<=8192
            for row in data:
                assert set(row)=={'stage','operation','elapsedMs','atMs','pageMs'},row
                assert isinstance(row['elapsedMs'],(int,float)) and isinstance(row['atMs'],(int,float)),row
            assert secret not in file.read_text()
        f.original();print('PASS actual disabled capture, local renderer/host timings, restart restoration, private input and strict numeric records',flush=True)
finally:f.stop();print('evidence',f.root,flush=True)
