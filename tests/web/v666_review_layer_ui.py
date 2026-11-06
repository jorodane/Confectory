"""Shipped CSS hit testing: placed focus order must not cover a floating Review.
Local geometry fixture, not a native permission/backend or actual-device test.
"""
import http.server,json,pathlib,sys,tempfile,threading
from playwright.sync_api import sync_playwright,expect
r=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(tempfile.mkdtemp(prefix='confectory-review-layer-'));plan=json.loads((r/'docs/v666-review-guidance-copy.json').read_text());delta=plan['styleDelta'];style=(r/delta['path']).read_text();before=style.replace(delta['after'],delta['before']);assert before!=style
html='''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/runtime.css?VARIANT"><style>body{margin:0;display:block}#workspace{position:relative;width:100vw;height:100vh;margin:0;overflow:hidden}</style><div id="workspace" class="workspace"><div class="workspace-world-layer"><div class="workspace-window-layer"><section id="placed" class="window is-placed" style="left:0;top:0;width:100%;height:100%;z-index:200"><button style="width:100%;height:100%">Blueprint 포커스 200</button></section></div></div><div class="workspace-window-layer workspace-floating-window-layer"><section id="review" class="window" style="left:100px;top:100px;width:495px;height:390px;z-index:210"><header class="window-title"><strong>변경 검토</strong></header><div class="window-body"><div class="window-content"><p>확정할 변경을 선택하십시오. 같은 객체의 변경은 함께 선택됩니다. 최종 소스는 Confirm에서만 반영됩니다.</p><button id="advanced">고급 검토 · 소스 변경 보기</button><p id="count">0</p></div></div></section></div></div><script>document.querySelector('#advanced').onclick=()=>document.querySelector('#count').textContent=Number(document.querySelector('#count').textContent)+1;</script>'''
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  path=self.path.split('?')[0]
  if path=='/':data=html.replace('VARIANT',self.path.split('?')[-1]).encode();mime='text/html'
  elif path=='/style.css':data=(r/'examples/editor-home/ui/style.css').read_bytes();mime='text/css'
  elif path=='/runtime.css':data=(before if self.path.endswith('?before')else style).encode();mime='text/css'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',mime);self.end_headers();self.wfile.write(data)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin='http://127.0.0.1:'+str(server.server_port);result=[]
try:
 with sync_playwright()as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000})
  boxes=[]
  for variant in ['before','after']:
   page.goto(origin+'/?'+variant);button=page.locator('#advanced');expect(button).to_be_visible();boxes.append(page.locator('#review').bounding_box());hit=button.evaluate('(el)=>{const r=el.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.closest("section")?.id}');assert hit==('placed'if variant=='before'else'review'),(variant,hit)
   if variant=='after':button.click();expect(page.locator('#count')).to_have_text('1')
   page.screenshot(path=str(out/(variant+'.png')));result.append(dict(variant=variant,hit=hit,review=boxes[-1]))
  assert boxes[0]==boxes[1],boxes
  for z in [81,1000,100000]:
   page.locator('#placed').evaluate('(el,z)=>el.style.zIndex=z',z);page.locator('#advanced').click()
  expect(page.locator('#count')).to_have_text('4');page.set_viewport_size({'width':900,'height':760});page.locator('#advanced').click();expect(page.locator('#count')).to_have_text('5');browser.close()
 (out/'evidence.json').write_text(json.dumps(dict(checks=result,geometryUnchanged=True,placedFocusOrderRetained=True,actualNativeBackend=False),ensure_ascii=False,indent=2));print('PASS shipped CSS baseline interception and isolated floating Review hit target, identical geometry, repeated focus 81/1000/100000, desktop viewport resize; '+str(out))
finally:server.shutdown();server.server_close()
