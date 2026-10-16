"""A real delayed metadata request must not race persisted source View restoration."""
from playwright.sync_api import expect

def verify_startup_restore(page,project,restart):
 target='Example.ButtonGame::Main';originals={p:p.read_bytes() for p in project.glob('*') if p.is_file()}
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='기능',exact=True).click();expect(page.locator('#nav')).to_be_enabled()
 if page.locator('.nav-menu').count():page.locator('#nav').click()
 page.locator('.window[data-key="browser"] [data-id="'+target+'"]').click();expect(page.locator('[data-declaration-id]')).to_have_text(target);expect(page.locator('#nav')).to_be_enabled();page.evaluate('()=>globalThis.confectoryFlushPresentation()')
 # Delay, but do not synthesize, a response or model operation. Other real
 # requests can proceed while this fetch waits in the browser.
 page.add_init_script('''(()=>{const send=globalThis.fetch.bind(globalThis);globalThis.startupRequests=[];globalThis.fetch=(url,init)=>{let request;try{request=JSON.parse(init?.body||'{}')}catch{}const forward=()=>{if(request?.op==='invoke')globalThis.startupRequests.push(request.endpoint);return send(url,init)};return request?.op==='invoke'&&request.endpoint==='helperList'?new Promise(resolve=>setTimeout(resolve,300)).then(forward):forward()}})();''')
 restart();expect(page.locator('[data-declaration-id]')).to_have_text(target,timeout=30000);expect(page.locator('#selection')).to_have_text(target);expect(page.locator('#nav')).to_be_enabled()
 requests=page.evaluate('()=>globalThis.startupRequests');assert requests.count('helperList')==1 and requests.index('helperList')<requests.index('select'),requests
 for p,original in originals.items():assert p.read_bytes()==original,p.name
 print('PASS actual startup metadata delay and owned source restoration: helper read completes before selection restore, no duplicate request or source write',flush=True)
