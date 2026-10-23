"""Original wrapper-modal content geometry in the SAME existing host/state.
Excludes native host, full Blueprint scene, execution outcomes and pixel parity.
"""
import json,pathlib,re,sys,tempfile,zipfile
from playwright.sync_api import sync_playwright
repo=pathlib.Path(sys.argv[1]).resolve();dom=pathlib.Path(sys.argv[2]).read_text();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-native-wrapper-visual-'))
with zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v508.zip') as z:
 blueprint=z.read('Confectory-v508/dist/blueprint.js').decode();style=z.read('Confectory-v508/dist/style.css').decode()
line=next(line for line in blueprint.splitlines() if "modal('분기 기능 편집 · '" in line)
expression=line[line.index("'<p class="):line.index(',(dialog,close)=>{')]
style+='\n'+'\n'.join((repo/'examples/editor-home/ui'/name).read_text() for name in ['consumer.css','runtime.css']);style=re.sub(r'@import\s+url\([^)]*\)\s*;','',style)
selectors=['[role=dialog]','.modal-head','.bp-script-guide','.bp-wrapper-bindings','.bp-script-editor','.bp-script-backdrop','[data-code-source]','[data-code-status]','[data-code-error]','.actions','[data-code-cancel]','[data-code-save]','[data-wrapper-complete]']
measure='selectors=>selectors.map(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return {selector,x:r.x,y:r.y,width:r.width,height:r.height}})'
errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.set_content('<style>'+style+'</style>'+dom);page.wait_for_function('()=>document.fonts.status==="loaded"');adapted=page.evaluate(measure,selectors);page.screenshot(path=str(case/'adapted-modal.png'))
 page.evaluate('expression=>{const esc=v=>String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll("\\\"","&quot;"),state={source:{name:"NativeVoid"}},locals=[],root=document.querySelector("[role=dialog]"),header=root.querySelector(".modal-head").outerHTML;root.innerHTML=header+eval(expression);}',expression)
 original=page.evaluate(measure,selectors);page.screenshot(path=str(case/'original-modal.png'));record={'original':original,'adapted':adapted,'pageErrors':errors,'scope':'original wrapper modal CONTENT markup in same runtime host; native-void source contract; enum source differs; no whole scene/native/pixel/branch parity','evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));assert not errors,errors;assert original==adapted,json.dumps(record,indent=2);browser.close()
print(json.dumps({'pass':True,'rectangles':len(selectors),'evidence':str(case),'scope':record['scope']},indent=2))
