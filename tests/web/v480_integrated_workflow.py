"""One owned project: Home/Data -> Set/ref graph -> Confirm -> real Run -> Workspace/cold."""
import hashlib,json,pathlib,re,subprocess,time,uuid
from playwright.sync_api import expect

def prepare(repo,project,env):
 manifest=project/'project.cpack';source=manifest.read_text();at=source.rfind('}');manifest.write_text(source[:at]+'element IntegrationTick function "IntegrationTick.celem";element IntegrationTickBody implementation "IntegrationTickBody.celem";'+source[at:])
 (project/'main.celem').write_text('function Example.ButtonGame::Main () -> int {use object Example.ButtonGame::Score;provide Example.ButtonGame::Main with Example.ButtonGame::MainBody;provide Example.ButtonGame::NodeValue with Example.ButtonGame::NodeValueBody;provide Confectory.RealTimeUpdate::Advance with Confectory.RealTimeUpdate::AdvanceBody;}')
 (project/'IntegrationTick.celem').write_text('function Example.ButtonGame::IntegrationTick (long[] model) -> void {provide Example.ButtonGame::IntegrationTick with Example.ButtonGame::IntegrationTickBody;}')
 (project/'IntegrationTickBody.celem').write_text('implementation Example.ButtonGame::IntegrationTickBody for Example.ButtonGame::IntegrationTick (long[] model) -> void {body common "integration-tick.csbody";}')
 (project/'integration-tick.csbody').write_text('model[0]++;')
 query={'operation':'blueprintPropertyCatalog','project':str(manifest),'sourceId':'Example.ButtonGame::NodeValueBody','owner':'Example.ButtonGame::Monster'}
 result=subprocess.run([env.get('CONFECTORY_DOTNET','dotnet'),str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(query),capture_output=True,text=True,check=True)
 reply=json.loads(result.stdout);assert reply['ok'],reply;descriptor=reply['result']['descriptor'];field=next(f for f in descriptor['fields'] if f['name']=='health');literal=lambda value:json.dumps(value,ensure_ascii=True)
 env['CONFECTORY_INTEGRATED_PRODUCER']=str(project.parent/'integrated-producer.log')
 (project/'CreateMonsterBody.celem').write_text('implementation Example.ButtonGame::CreateMonsterBody for Example.ButtonGame::CreateMonster (long value) -> object {import Confectory.ObjectModel::Create as Create (string,string[],object[]) -> object;body common "create-monster.csbody";}')
 # Observation only: graph receivers still come exclusively from the explicit producer result pin.
 (project/'create-monster.csbody').write_text('object instance=calls.Create.Invoke('+literal(json.dumps(descriptor,separators=(',',':')))+',new[]{'+literal(field['id'])+'},new object[]{value});AppDomain.CurrentDomain.SetData("Confectory.IntegrationFixture.ObservedInstance",instance);System.IO.File.AppendAllText(Environment.GetEnvironmentVariable("CONFECTORY_INTEGRATED_PRODUCER")!,value.ToString(System.Globalization.CultureInfo.InvariantCulture)+"\\n");return instance;')
 (project/'main_body.celem').write_text('implementation Example.ButtonGame::MainBody for Example.ButtonGame::Main () -> int {import Example.ButtonGame::NodeValue as Value (long) -> long;import Confectory.ObjectModel::Read as Read (object,string,string,string) -> object;import Confectory.FrameControl::Open as Open () -> string;import Confectory.FrameControl::Begin as Begin (string) -> int;import Confectory.FrameControl::Complete as Complete (string) -> void;import Confectory.FrameControl::Close as Close (string) -> void;import Confectory.RealTimeUpdate::Advance as Advance (double[],double,double,double,double,int) -> double[];import Example.ButtonGame::IntegrationTick as Tick (long[]) -> void;body common "main.csbody";}')
 prefix='''using var catalogStream=System.IO.File.OpenRead(System.IO.Path.Combine(AppContext.BaseDirectory,"public-linkage.json"));
var catalog=System.Text.Json.Nodes.JsonNode.Parse(catalogStream)!;var score=System.Linq.Enumerable.Single(catalog["elements"]!.AsArray(),e=>e!["id"]!.ToString()=="Example.ButtonGame::Score")!;
long seed=score["typedData"]!["amount"]!["scalar"]!.GetValue<long>();AppDomain.CurrentDomain.SetData("Confectory.IntegrationFixture.ObservedInstance",null);long result=calls.Value.Invoke(seed);
object observed=AppDomain.CurrentDomain.GetData("Confectory.IntegrationFixture.ObservedInstance")??throw new InvalidOperationException("Producer did not execute");
'''
 prefix+='long actual=(long)calls.Read.Invoke(observed,"Example.ButtonGame::Monster",'+literal(field['id'])+','+literal(field['hash'])+');AppDomain.CurrentDomain.SetData("Confectory.IntegrationFixture.ObservedInstance",null);Console.WriteLine("INTEGRATED_V480 "+new System.Text.Json.Nodes.JsonObject{["seed"]=seed,["result"]=result,["field"]=actual}.ToJsonString());if(result!=42||actual!=42)throw new InvalidOperationException("Actual Set/ref result mismatch");\n'
 (project/'main.csbody').write_text(prefix+(repo/'examples/frame-loop/Main.csbody').read_text())
 baseline=subprocess.run([env.get('CONFECTORY_DOTNET','dotnet'),str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'linux'],capture_output=True,text=True)
 assert baseline.returncode==0,baseline.stdout+baseline.stderr

def verify_integrated(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1150});graph='Example.ButtonGame::NodeValueBody/body:common';score='Example.ButtonGame::Score';amount='data:["amount"]';counter=project.parent/'integrated-producer.log';facts={'version':1,'singleProject':True,'stages':[]}
 def checkpoint(message):facts['stages'].append(message);print('INTEGRATION CHECKPOINT '+message,flush=True)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,input):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=rid,expectedRevision=v['revision'],input=input))['ok'];deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   r=send(envelope(v,'update'));assert r['ok'];row=next((x for x in r['results'] if x['requestId']==rid),None)
   if row:break
   time.sleep(.02)
  else:raise AssertionError('pending integration request')
  assert row['ok'],row;assert send(envelope(v,'dispose'))['ok'];return row['result']
 def nav(name):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def read():return invoke('blueprint',{'action':'read','id':graph})
 def panel():return page.locator('.window[data-key="blueprint"]')
 def apply(field):field.locator('..').locator('[data-apply]').click();ready()
 def route(node,to):
  panel().locator('[data-bp-select="'+node+'"]').click();field=panel().locator('[data-bp-route="next"]');field.select_option(to);apply(field)
 def confirm():
  review=page.locator('.window[data-key="review"]');expect(review).to_be_visible(timeout=180000)
  if review.locator('[data-review-advanced]').count():review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  expect(page.locator('#confirm')).to_be_enabled(timeout=180000);page.locator('#confirm').click();ready();expect(page.locator('#status')).to_contain_text('Source confirmed',timeout=180000)
 def source_bytes():return {str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
 def card():return state()['cards'][0]
 def edit_receipt():
  expect(page.locator('[data-stat="lastEdit"][data-status="available"]').first).to_be_visible(timeout=180000);return card()['summary']['lastEdit']
 def enter():
  expect(page.locator('[data-stat="objects"][data-status="available"]').first).to_be_visible(timeout=180000);page.locator('[data-enter]').first.click();ready()
 ready();page.locator('.brand').click();expect(page.locator('#home-project-search')).to_be_visible();page.locator('#home-project-search').fill('ButtonGame');page.locator('#home-project-search').press('Enter');expect(page.locator('[data-project]')).to_have_count(1);listing=card()['id'];enter();owner=state()['projectId'];facts['project']={'listingId':listing,'projectId':owner};checkpoint('Home owned project/search/open')
 nav('개념');browser=page.locator('.window[data-key="browser"]');browser.locator('[data-namespace="Example.ButtonGame"]').click();browser.locator('[data-browser-definition="'+score+'"]').click();ready();schema=page.locator('.window[data-key="schema"]');initial=schema.locator('[data-schema-field="initial"]');initial.fill('3');initial.locator('..').get_by_role('button',name='Apply field',exact=True).click();ready();schema.locator('[data-close]').click()
 browser.locator('input[type=range][aria-label="객체 표시 밀도 Compact Preview Data"]').evaluate('e=>{e.value="100";e.dispatchEvent(new Event("input",{bubbles:true}));}');browser.locator('[data-browser-fields]').click();builder=page.locator('.window[data-key="custom"]');builder.locator('[data-table-probe]').select_option(score);ready()
 for c in builder.locator('[data-table-object]').all():c.uncheck()
 builder.locator('[data-table-object="'+score+'"]').check()
 for c in builder.locator('[data-table-field]').all():c.uncheck()
 builder.locator('[data-table-field=\''+amount+'\']').check();builder.locator('[data-table-create]').click();ready();builder.locator('[data-close]').click()
 cell=browser.locator('[data-table-cell="'+score+'"][data-column=\''+amount+'\']');cell.fill('7');browser.locator('[data-table-apply="'+score+'"][data-column=\''+amount+'\']').click();ready();assert 'data amount = 7' not in (project/'Score.celem').read_text();browser.locator('[data-browser-fields-review]').click();confirm();assert re.search(r'data amount\s*=\s*7\s*;', (project/'Score.celem').read_text());assert re.search(r'value initial\s*=\s*3\s*;', (project/'Score.celem').read_text());checkpoint('declaration metadata + Data amount 7 -> shared draft -> compiler Confirm')
 browser.locator('[data-browser-fields-release]').click();ready();browser.locator('[data-close]').click();page.locator('.brand').click();before_graph=edit_receipt();assert before_graph['kind']=='confirm';enter()
 from v480_property_ref import verify_property_ref
 verify_property_ref(page,project,mount,send,envelope,settle,restart);assert not counter.exists(),'preview/Confirm executed producer';checkpoint('field ref explicit upgrade/typed parameter/CAS rejection/cold/group Confirm')
 # Add a checked Set before the existing actual field ref, within the same graph/source owner.
 panel().locator('[data-bp-property-set-open]').click();form=page.locator('.window[data-key="blueprint-code:'+graph+'/$property"]');form.locator('[data-property-node]').fill('set_health');form.locator('[data-property-owner]').fill('Example.ButtonGame::Monster');form.locator('[data-property-fields]').click();ready();form.locator('[data-property-field]').select_option('health');form.locator('[data-property-target-choice]').select_option('{"node":"spawn","output":"return"}');form.locator('[data-property-value]').fill('{"constant":31}');form.locator('[data-property-read]').click();ready();form.locator('[data-property-ack]').check();form.locator('[data-property-apply]').click();ready();route('spawn','set_health');route('set_health','health_ref')
 panel().locator('[data-bp-code-open="calculate"]').click();code=page.locator('.window[data-key="blueprint-code:'+graph+'/calculate"]');code.locator('[data-bp-code]').fill('if(cell!=31)throw new InvalidOperationException("Set did not reach the field before ref");cell=42;return cell;');code.locator('[data-apply]').click();ready();code.locator('[data-close]').click();assert read()['diagnostics']['state']=='source-ready';panel().locator('[data-bp-review]').click();confirm();assert not counter.exists();published=json.loads((project/'node-value.graph.json').read_text());assert {'property-set','property-ref'}<={n['kind'] for n in published['nodes']};confirmed=source_bytes();checkpoint('same graph Set -> actual ref -> CSharp write -> compiler Confirm')
 panel().locator('[data-close]').click();page.locator('#run').click();run=page.locator('.window[data-key="run"]');run.locator('[data-run-target]').select_option('linux');run.locator('[data-run-play]').click();expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=180000);marker=re.compile(r'INTEGRATED_V480 (\{[^\n]*\})');expect(run.locator('[data-run-logs]')).to_contain_text(marker,timeout=180000);match=marker.search(run.locator('[data-run-logs]').text_content());assert match,run.locator('[data-run-logs]').text_content();actual=json.loads(match[1]);assert actual=={'seed':7,'result':42,'field':42},actual;assert counter.read_text().splitlines()==['7']
 def wait_control(predicate):
  deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   current=state()['executionControl']
   if predicate(current):return current
   time.sleep(.025)
  raise AssertionError(current)
 run.locator('[data-run-pause]').click();paused=wait_control(lambda c:c.get('mode')=='paused' and c.get('ack')==1);run.locator('[data-run-step]').click();stepped=wait_control(lambda c:c.get('ack')==2);assert int(stepped['frame'])==int(paused['frame'])+1;run.locator('[data-run-stop]').click();expect(run.locator('.run-status')).to_contain_text('stopped',timeout=30000);assert source_bytes()==confirmed;facts['run']={'actual':actual,'frameBeforeStep':paused['frame'],'frameAfterStep':stepped['frame'],'ack':stepped['ack']};checkpoint('actual Run reads compiled Data 7 / Set31 / field-ref42, Pause/one Step/owned Stop');run.locator('[data-close]').click()
 for w in page.locator('.window:visible').all():
  close=w.locator('[data-close]').first
  if close.count():close.click()
 area=page.locator('#workspace').bounding_box();page.locator('#workspace').click(button='right',position={'x':area['width']-140,'y':area['height']-180});page.get_by_role('button',name='메모 만들기',exact=True).click();note=page.locator('.workspace-note').last;note.locator('[data-note-editor],textarea').fill('INTEGRATED_PRIVATE_NOTE');page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert source_bytes()==confirmed;page.screenshot(path='/tmp/confectory-v480-integrated-before-cold.png',full_page=True)
 page.locator('.brand').click();after_graph=edit_receipt();assert after_graph['kind']=='confirm' and after_graph['sequence']>before_graph['sequence'];page.evaluate('()=>globalThis.confectoryFlushHomePreferences()');restart();ready();expect(page.locator('.workspace-note [data-note-editor],.workspace-note textarea')).to_have_text('INTEGRATED_PRIVATE_NOTE');fresh=state();assert fresh['projectId']==owner and not fresh.get('executionHandle') and fresh['executionState']=='idle',{'expectedProject':owner,'actualProject':fresh['projectId'],'handle':fresh.get('executionHandle'),'state':fresh['executionState']};assert source_bytes()==confirmed;nav('기능 Blueprint');panel().locator('[data-bp-read]').click();ready();assert read()['diagnostics']['state']=='source-ready';assert source_bytes()==confirmed;page.locator('.brand').click();assert edit_receipt()==after_graph;enter();checkpoint('private Workspace note/source separation -> fresh host -> same project/Data/graph -> no run authority adoption -> Home receipt');facts['cold']={'projectMatches':True,'executionState':fresh['executionState'],'executionOwnerAdopted':False,'lastEditSequence':after_graph['sequence']};facts['sourceSha256']={p:hashlib.sha256(b).hexdigest() for p,b in confirmed.items()};page.screenshot(path='/tmp/confectory-v480-integrated-after-cold.png',full_page=True);pathlib.Path('/tmp/confectory-v480-integrated-workflow.json').write_text(json.dumps(facts,indent=2)+'\n');print('PASS actual v480 integrated Home/Data/Set/ref/Confirm/Run/Workspace/new-host flow: seed7/result42/field42 and no authority adoption',flush=True)
