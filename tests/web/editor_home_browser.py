"""Actual same editor ProjectPack; static WASM, common Canvas layout, real browser input/files."""
import http.server,json,pathlib,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
report=json.load(open(sys.argv[1]));site=pathlib.Path(report['output'])/'site'
assert report['entry']=='Confectory.EditorHome::Main'
catalog=json.loads((site/'public-linkage.json').read_text());assert catalog['entry']==report['entry']
assert next(i for i in catalog['implementations'] if i['id']=='Confectory.EditorHome::MainBody')['bodySelection']=='common'
class Static(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(site),**kwargs)
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Static);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with tempfile.TemporaryDirectory(prefix='confectory-real-browser-') as temporary,sync_playwright() as p:
  folder=pathlib.Path(temporary)/'BrowserFixture';folder.mkdir();(folder/'project.cproj').write_text('project BrowserFixture version "1" { standalone true; entry BrowserFixture::Main; registry Untrusted "MUST_NOT_EXECUTE"; target browser Untrusted::Build; }')
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':850});errors=[];requests=[]
  page.on('console',lambda m:print(m.type,m.text));page.on('pageerror',lambda e:(errors.append(str(e)),print('PAGEERROR',e.stack)));page.on('request',lambda r:requests.append((r.method,r.url)))
  def click(x,y):
   before=page.evaluate('confectoryPlatform.presented');page.mouse.click(x,y);page.wait_for_function('(before)=>confectoryPlatform.presented>before+1',arg=before)
  page.goto('http://127.0.0.1:'+str(server.server_port));page.wait_for_function('globalThis.confectoryPlatform?.loops.size>0');page.wait_for_timeout(2100)
  page.screenshot(path='/tmp/confectory-same-editor-first.png');click(600,510);page.wait_for_timeout(150)
  click(275,164);name=page.locator('input[data-control="10"]');intent=page.locator('textarea[data-control="11"]');name.wait_for(state='visible')
  name.fill('BrowserActual');name.click();page.keyboard.press('Tab');expect(intent).to_be_focused();page.keyboard.press('Shift+Tab');expect(name).to_be_focused();intent.fill('actual common layout 한글 draft');page.wait_for_timeout(150);assert name.input_value()=='BrowserActual'
  page.evaluate('window.originalName=document.querySelector("input[data-control=\\"10\\"]")');click(560,460);page.wait_for_timeout(150);click(275,164);name.wait_for(state='visible')
  assert page.evaluate('window.originalName===document.querySelector("input[data-control=\\"10\\"]")');assert name.input_value()=='BrowserActual'
  page.screenshot(path='/tmp/confectory-same-editor-create.png');click(560,460);page.wait_for_timeout(150)
  page.screenshot(path="/tmp/confectory-before-folder-chooser.png")
  with page.expect_file_chooser() as cancelled:click(540,164)
  cancelled.value.set_files([]);revision=page.evaluate('confectoryPlatform.presented');page.wait_for_function('(revision)=>confectoryPlatform.presented>revision+1',arg=revision)
  assert page.locator('textarea[data-control="38"]').count()==0
  with page.expect_file_chooser() as chooser:click(540,164)
  chooser.value.set_files(str(folder));chat=page.locator('textarea[data-control="38"]');chat.wait_for(state='visible');chat.fill('command test');chat.click()
  page.evaluate("""()=>{const [host]=[...confectoryPlatform.hosts].find(([_,h])=>[...h.fields.values()].some(row=>row.args.id===38&&row.args.visible));window.commandHost=host;confectoryPlatform.request('native',JSON.stringify({host,operation:'commands',payload:JSON.stringify({id:38,keys:[0xff0d]}),parent:0}));}""")
  page.keyboard.press('Enter');expect(chat).to_have_value('command test')
  page.evaluate("confectoryPlatform.request('native',JSON.stringify({host:window.commandHost,operation:'commands',payload:JSON.stringify({id:38,keys:[]}),parent:0}))")
  page.keyboard.press('Enter');expect(chat).to_have_value('command test\n');chat.fill('실제 공용 editor draft');page.wait_for_timeout(150)
  page.evaluate('window.originalChat=document.querySelector("textarea[data-control=\\"38\\"]")');chat.click();page.keyboard.press('End');page.keyboard.type(' keyboard');page.wait_for_timeout(150)
  assert chat.input_value()=='실제 공용 editor draft keyboard';click(270,30);page.wait_for_timeout(100);click(270,236);page.wait_for_timeout(200)
  click(800,174);chat.wait_for(state='visible');expect(chat).to_have_value('실제 공용 editor draft keyboard')
  page.evaluate('window.reopenedChat=document.querySelector("textarea[data-control=\\"38\\"]")');click(270,30);page.wait_for_timeout(100);click(270,86);page.wait_for_timeout(100);click(250,304);page.wait_for_timeout(100)
  assert page.evaluate('window.reopenedChat===document.querySelector("textarea[data-control=\\"38\\"]")')
  page.screenshot(path='/tmp/confectory-same-editor-project.png');assert 'native OS windows/folders and dynamic compilation unavailable' in page.locator('#capabilities').inner_text()
  assert page.evaluate("""()=>{try{confectoryPlatform.request('native',JSON.stringify({host:'unknown-owner',operation:'close',payload:'{}',parent:0}));return false;}catch(error){return error.message.includes('Unknown browser native owner');}}""")
  fault=page.evaluate("""()=>{const field=document.querySelector('textarea[data-control="38"]'),remove=field.remove.bind(field);let failed=false;field.remove=()=>{if(!failed){failed=true;throw Error('actual DOM release fault');}remove();};try{confectoryPlatform.bridge.Close();return {error:false,retained:false};}catch(error){return {error:true,retained:confectoryPlatform.hosts.size>0&&field.isConnected};}}""")
  assert fault=={'error':True,'retained':True},fault
  assert page.evaluate('confectoryPlatform.bridge.Close()');assert page.evaluate('confectoryPlatform.bridge.Close()');page.wait_for_timeout(100);assert page.locator('#fields input,#fields textarea').count()==0
  assert not errors,errors;assert any(url.endswith('.wasm') for _,url in requests);assert all(method=='GET' and '/api/' not in url for method,url in requests)
  print('PASS same actual editor common entry/render/input/folder import/edit/repeat/leave/reopen/stable controls/close; static GET-only WASM');browser.close()
finally:server.shutdown()
