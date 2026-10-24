"""Same-data v536 source oracle for compound array geometry and value colors.

Static renderer only: does not prove engine persistence or native window behavior.
"""
import http.server,json,pathlib,re,sys,tempfile,threading,zipfile
from playwright.sync_api import sync_playwright

repo=pathlib.Path(sys.argv[1]).resolve()
with zipfile.ZipFile(repo/'reference/site-ui/Confectory-Editor-Prototype-v536.zip') as archive:
 app=next(name for name in archive.namelist() if name.endswith('/dist/app.js'))
 source=archive.read(app).decode('utf-8')
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-field-visual-'))
def function(name):
 start=source.index('function '+name+'(');end=source.find('\nfunction ',start+1);return source[start:end]
functions='\n'.join(function(n) for n in ['objectEditorId','propertyKey','propertyTypeLabel','propertyTypeSummary','propertyValueAt','informationSource','informationFields','informationDefaults','propertyDefault','inheritedPropertySources','renderObjectSchema','propertyTypeChoiceObjects','choosePropertyType'])
constants=source[source.index('const primitivePropertyTypes='):source.index('function propertyTypeLabel(')]
styles='\n'.join((repo/'examples/editor-home/ui'/name).read_text() for name in ['style.css','consumer.css','runtime.css'])
styles=re.sub(r'@import\s+url\([^)]*\)\s*;','',styles)
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(repo),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/fixture':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(('<style>'+styles+'</style><main style="position:absolute;left:40px;top:40px;width:420px"><section class="object-schema"></section></main>').encode())
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:'+str(server.server_port)+'/fixture')
  page.add_script_tag(content='''const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');const profileIconMarkup=esc;
   const leaf={id:'Owned::Leaf',name:'Leaf',kind:'Info',group:'info',propertyModel:1,schemaFields:[{id:'count',key:'Count',name:'Count',type:'정수',multi:false,fields:[]}],Count:42},owner={id:'Owned::Owner',name:'Owner',kind:'Info',group:'info',propertyModel:1,schemaFields:[{id:'items',key:'Items',name:'Items',type:'정보',infoId:'Owned::Leaf',multi:true,fields:[]}],Items:[{Count:42}]},project={objects:[leaf,owner,...Array.from({length:5},(_,i)=>({id:'Owned::Fn'+i,name:'Fn'+i,kind:'Feature',group:'feature'}))]};const w={key:'schema',body:$('main'),el:$('main'),meta:{id:owner.id},elementScope:'owned',elementStatusGeneration:0};const ensureObjectProperties=()=>{},bindObjectReferenceDrag=()=>{},setupPropertyReorder=()=>{},bindObjectSourceMenus=()=>{};
  '''+constants+functions+"\nrenderObjectSchema(w);")
  assert not errors,errors
  page.evaluate("globalThis.originalField=document.querySelector('.object-property-row')")
  selectors=[':scope',':scope>.property-content-box',':scope .property-multi-values',':scope .property-multi-item',':scope .property-value-box',':scope .property-multi-index',':scope .property-multi-content',':scope .property-multi-remove',':scope .property-value-box>.property-expanded-content',':scope .property-complex-body',':scope .inherited-property-name',':scope [data-property-value]']
  measure='selectors=>selectors.map(selector=>{const el=originalField.querySelector(selector)||((selector===":scope")?originalField:null),r=el.getBoundingClientRect(),base=originalField.getBoundingClientRect();return {selector,x:r.x-base.x,y:r.y-base.y,width:r.width,height:r.height,color:getComputedStyle(el).color}})'
  before=page.evaluate(measure,selectors);page.screenshot(path=str(case/'original-array.png'))
  page.evaluate('''async()=>{const {renderInformationValues}=await import('/examples/editor-home/ui/element-information-values.js');const row={name:'Items',path:['Items'],kind:'compound',cardinality:'multiple',type:leaf.id,valueJson:'[{"Count":42}]',writable:true,localOverride:true},schema={id:owner.id,revision:0,textHash:'same',rows:[row],types:{[leaf.id]:{fields:{Count:{kind:'general',cardinality:'single',type:'long'}}}}};w.elementSchema=schema;const value={kind:'definition',nativeKey:'Items',name:'Items',definition:{kind:'compound',cardinality:'multiple',type:leaf.id},typeChoice:{types:schema.types},text:row.valueJson,wireJson:true},inputs=new Map([['new-definition',value]]),api={$, $$,esc,inputs,windows:new Map([['schema',w]]),current:{projectId:'owned'},name:id=>id.split('::').at(-1),controls:()=>{},persist:()=>{},fail:()=>{},refresh:()=>{},valueJson:()=>{throw Error('No visual writes');}};originalField.querySelector(':scope>.property-content-box>.property-expanded-content').remove();renderInformationValues(api,w,schema,'new-definition',value,originalField,()=>{});}''')
  after=page.evaluate(measure,selectors);page.screenshot(path=str(case/'adapted-array.png'))
  (case/'comparison.json').write_text(json.dumps({'original':before,'adapted':after,'errors':errors},indent=2))
  assert not errors,errors
  assert before==after,json.dumps({'original':before,'adapted':after,'evidence':str(case)},indent=2)
  # The source's narrow complex-array wrapper is intentionally preserved here;
  # this oracle distinguishes a prototype defect from an adapter regression.
  print(json.dumps({'pass':True,'rectangles':len(selectors),'evidence':str(case),'scope':'same-data compound array source geometry/colors; not engine/native QA'}))
  browser.close()
finally:server.shutdown()
