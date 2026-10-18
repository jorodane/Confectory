"""Real ordinary EditorHome + ButtonGame packs through the common local web transport."""
import re,hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,urllib.error,uuid,shutil
from playwright.sync_api import sync_playwright,expect
from owned_responses import OwnedResponses
class FailureEvidence:
 def __enter__(self):return self
 def __exit__(self,type,error,traceback):
  if error is not None:
   print('UI page errors:',globals().get('errors',[]),flush=True)
   try:
    page.screenshot(path='/tmp/confectory-web-ui-failure.png',full_page=True);print('UI failure status:',page.locator('#status').inner_text(),flush=True)
    print('UI failure controls:',page.evaluate("()=>({confirm:document.querySelector('#confirm')?.disabled,run:document.querySelector('#run')?.disabled,source:document.querySelector('#selection')?.textContent})"),flush=True)
   except Exception:pass
  return False
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());kind=sys.argv[3]
with tempfile.TemporaryDirectory(prefix='confectory-web-ui-') as directory:
 root=pathlib.Path(directory);env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),XDG_DATA_HOME=str(root/'data'),XDG_CACHE_HOME=str(root/'cache'))
 if env.get('CONFECTORY_DOTNET'):env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env.get('PATH','')
 # A regular existing user project copy, with actual object source and normal draft storage.
 project=root/'button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'))
 manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
 if kind in ['blueprint-integrated','declaration-navigation','browser-data-fill','browser-data-fields','instant-table','schema-exact','schema-actions']:
  (project/'ZBroken.celem').write_text('object Example.ButtonGame::ZBroken {}')
  (project/'TableStats.celem').write_text('schema Example.ButtonGame::TableStats {field amount single general long;field tags multiple general int;}')
  (project/'TableTwin.celem').write_text('object Example.ButtonGame::TableTwin extends Example.ButtonGame::Score {data amount = 9223372036854775806;}')
  score_source=project/'Score.celem';score_source.write_text(score_source.read_text().replace('{','{ value description = "Separate metadata";use schema Example.ButtonGame::TableStats;data amount = 9223372036854775807;data tags = [1,2];',1))
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element TableStats schema "TableStats.celem";element TableTwin object "TableTwin.celem";element ZBroken object "ZBroken.celem";'+source[index:])
 if kind in ['blueprint-integrated','declaration-navigation','browser-data-fill','browser-data-fields']:
  ref=root/'browser-reference';ref.mkdir();(ref/'pack.cpack').write_text('pack BrowserReference version "1" {element External object "External.celem";}');(ref/'External.celem').write_text('object BrowserReference::External {value initial = 7;}')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'registry BrowserReference '+json.dumps(str(ref/'pack.cpack'))+';dependency BrowserReference version "1";'+source[index:])
 if kind=='declaration-navigation':
  ref=root/'browser-reference';(ref/'External.celem').write_text('object BrowserReference::External {description "Registered parent definition";value externalMeta = 7;}')
  score=project/'Score.celem';score.write_text(score.read_text().replace('object Example.ButtonGame::Score {','object Example.ButtonGame::Score extends BrowserReference::External {',1))
  definitions={'GameRoot':('category','category Example.ButtonGame::GameRoot {}'),'GameChild':('category','category Example.ButtonGame::GameChild extends Example.ButtonGame::GameRoot {contain object Example.ButtonGame::Score;}'),'Party':('concept','concept Example.ButtonGame::Party {use schema Example.ButtonGame::TableStats;}')}
  for name,(_,text) in definitions.items():(project/(name+'.celem')).write_text(text)
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,_) in definitions.items())+source[index:])
 if kind=='browser-data-fill':
  (project/'TableThird.celem').write_text('object Example.ButtonGame::TableThird extends Example.ButtonGame::Score {data amount = 9223372036854775804;}')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element TableThird object "TableThird.celem";'+source[index:])
 if kind in ['schema-exact','schema-actions']:
  stats=project/'TableStats.celem';stats.write_text(stats.read_text().replace('tags multiple general int','tags multiple general long'))
  score_source=project/'Score.celem';score_source.write_text(score_source.read_text().replace('{','{ value huge = 9223372036854775807;',1).replace('data tags = [1,2]','data tags = [9223372036854775807,9223372036854775806]'))
 if kind=='schema-actions':
  (project/'TableLeaf.celem').write_text('schema Example.ButtonGame::TableLeaf {field n single general long;field flag single general bool;}')
  stats=project/'TableStats.celem';source=stats.read_text();stats.write_text(source[:-1]+'field profile single compound Example.ButtonGame::TableLeaf;}')
  score_source=project/'Score.celem';score_source.write_text(score_source.read_text().replace('{','{ data profile = { n = 9223372036854775807;flag = true; };',1))
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element TableLeaf schema "TableLeaf.celem";'+source[index:])
 if kind=='reference-definition':
  ref=root/'reference-api';ref.mkdir();(ref/'pack.cpack').write_text('pack ReferenceApi version "1" {element Work function "Work.celem";element Body implementation "Body.celem";}')
  (ref/'Work.celem').write_text('function ReferenceApi::Work (long input) -> long {description "Registered definition A";}')
  (ref/'Body.celem').write_text('implementation ReferenceApi::Body for ReferenceApi::Work (long input) -> long {body common "missing-never-read.csbody";}')
  main=project/'main.celem';main.write_text(main.read_text().replace('{','{ use function ReferenceApi::Work;use implementation ReferenceApi::Body;',1))
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'registry ReferenceApi '+json.dumps(str(ref/'pack.cpack'))+';dependency ReferenceApi version "1";'+source[index:])
 if kind=='reference-gestures':
  (project/'RefStats.celem').write_text('schema Example.ButtonGame::RefStats {field peer single reference Example.ButtonGame::RefStats;field amount single general long;}')
  for name,n in [('Peer',2),('OtherPeer',3)]: (project/(name+'.celem')).write_text('object Example.ButtonGame::'+name+' {use schema Example.ButtonGame::RefStats;data amount = '+str(n)+';}')
  score=project/'Score.celem';score.write_text(score.read_text().replace('{','{use schema Example.ButtonGame::RefStats;data peer = Example.ButtonGame::Peer;data amount = 1;',1))
  (project/'RefModule.celem').write_text('module Example.ButtonGame::RefModule {}')
  raw=manifest.read_text();i=raw.rfind('}');manifest.write_text(raw[:i]+'element RefStats schema "RefStats.celem";element Peer object "Peer.celem";element OtherPeer object "OtherPeer.celem";element RefModule module "RefModule.celem";'+raw[i:])
 env['CONFECTORY_WEB_PROJECT']=str(manifest)
 if kind in ['node-tasks','blueprint','blueprint-implicit','blueprint-external-ref','blueprint-nested','blueprint-property','blueprint-property-set','blueprint-property-ref','blueprint-integrated','blueprint-code-regions','blueprint-methods','blueprint-enum-plan','blueprint-switch','blueprint-camera','blueprint-create','call-wrapper','registered-call','placed-find','locals','ref-nodes','alias-locals']:
  fixture=report['nodeTaskFixture']
  typename='long' if kind.startswith('blueprint') or kind in ['call-wrapper','registered-call','placed-find','locals','ref-nodes','alias-locals'] else 'int'
  (project/'NodeValue.celem').write_text(fixture['feature']);(project/'NodeValueBody.celem').write_text('implementation Example.ButtonGame::NodeValueBody for Example.ButtonGame::NodeValue ('+typename+' n) -> '+typename+' {blueprint common "node-value.graph.json";}')
  (project/'node-value.graph.json').write_text(json.dumps(fixture['graph']));(project/'calculate.node.json').write_text(json.dumps(fixture['node']))
  if kind.startswith('blueprint') or kind in ['call-wrapper','registered-call','placed-find','locals','ref-nodes','alias-locals']:(project/'condition.node.json').write_text(json.dumps(report['additionalNodeFixture']))
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element NodeValue function "NodeValue.celem";element NodeValueBody implementation "NodeValueBody.celem";'+source[index:])
 if kind in ['blueprint-property','blueprint-property-set','blueprint-property-ref','blueprint-integrated']:
  (project/'PropertyVitals.celem').write_text('schema Example.ButtonGame::PropertyVitals {field health single general long;field enabled single general bool;field f single general float;field samples multiple general long;field peer single reference Example.ButtonGame::PropertyVitals;}')
  (project/'Monster.celem').write_text('object Example.ButtonGame::Monster {use schema Example.ButtonGame::PropertyVitals;data health = 999;}')
  (project/'CreateMonster.celem').write_text('function Example.ButtonGame::CreateMonster (long value) -> object {provide Example.ButtonGame::CreateMonster with Example.ButtonGame::CreateMonsterBody;}')
  (project/'CreateMonsterBody.celem').write_text('implementation Example.ButtonGame::CreateMonsterBody for Example.ButtonGame::CreateMonster (long value) -> object {body common "create-monster.csbody";}')
  # The editor never executes user code while reading field contracts or confirming source.
  (project/'create-monster.csbody').write_text('throw new InvalidOperationException("Contract reads and compiler Confirm never call the object producer");')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'registry Confectory.ObjectModel '+json.dumps(str(repo/'packs/object-model/pack.cpack'))+';dependency Confectory.ObjectModel version "0.1.0";element PropertyVitals schema "PropertyVitals.celem";element Monster object "Monster.celem";element CreateMonster function "CreateMonster.celem";element CreateMonsterBody implementation "CreateMonsterBody.celem";'+source[index:])
 if kind in ['blueprint-implicit','blueprint-external-ref']:
  (project/'LiftValue.celem').write_text('function Example.ButtonGame::LiftValue (long n) -> long {}')
  (project/'LiftValueBody.celem').write_text('implementation Example.ButtonGame::LiftValueBody for Example.ButtonGame::LiftValue (long original) -> long {body common "lift.csbody";}')
  (project/'lift.csbody').write_bytes(b'if (original < 0) return this.Invoke(-original);\r\nreturn original + 3;\r\n')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element LiftValue function "LiftValue.celem";element LiftValueBody implementation "LiftValueBody.celem";'+source[index:])
 if kind=='blueprint-external-ref':
  (project/'LiftValue.celem').write_text('function Example.ButtonGame::LiftValue (ref long left,ref long right,out long audit) -> long {}')
  (project/'LiftValueBody.celem').write_text('implementation Example.ButtonGame::LiftValueBody for Example.ButtonGame::LiftValue (ref long a,ref long b,out long copied) -> long {body common "lift.csbody";}')
  (project/'lift.csbody').write_bytes(b'if (a < 0) { a = -a; return this.Invoke(ref a,ref b,out copied); }\r\na = 10; b += a; copied = a + b; return a + b + copied;\r\n')
 if kind=='blueprint-camera':
  other=report['cameraSecondGraph'];(project/'OtherValue.celem').write_text(other['feature']);(project/'OtherValueBody.celem').write_text('implementation Example.ButtonGame::OtherValueBody for Example.ButtonGame::OtherValue (long n) -> long {blueprint common "other-value.graph.json";}');(project/'other-value.graph.json').write_text(json.dumps(other['graph']));(project/'other-condition.node.json').write_text(json.dumps(report['additionalNodeFixture']));(project/'other-calculate.node.json').write_text(json.dumps(report['nodeTaskFixture']['node']));source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element OtherValue function "OtherValue.celem";element OtherValueBody implementation "OtherValueBody.celem";'+source[index:])
 if kind=='call-wrapper':
  (project/'Double.celem').write_text('function Example.ButtonGame::Double (long value) -> long {description "Existing double feature";provide Example.ButtonGame::Double with Example.ButtonGame::DoubleBody;}')
  (project/'DoubleBody.celem').write_text('implementation Example.ButtonGame::DoubleBody for Example.ButtonGame::Double (long value) -> long {body common "double.csbody";}');(project/'double.csbody').write_text('return value * 2;')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element Double function "Double.celem";element DoubleBody implementation "DoubleBody.celem";'+source[index:])
 if kind=='registered-call':
  registered=root/'registered-api';registered.mkdir();(registered/'pack.cpack').write_text('pack ReferenceApi version "1" {element Double function "Double.celem";element DoubleBody implementation "DoubleBody.celem";}')
  (registered/'Double.celem').write_text('function ReferenceApi::Double (long value) -> long {description "Read only registered Double contract";provide ReferenceApi::Double with ReferenceApi::DoubleBody;}')
  (registered/'DoubleBody.celem').write_text('implementation ReferenceApi::DoubleBody for ReferenceApi::Double (long value) -> long {body common "double.csbody";}');(registered/'double.csbody').write_text('return value * 7;')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'registry ReferenceApi '+json.dumps(str(registered/'pack.cpack'))+';dependency ReferenceApi version "1";'+source[index:])
 if kind in ['window-documents','tab-arrangement']:
  (project/'DocOther.celem').write_text('object Example.ButtonGame::DocOther {description \"Independent document property source\";}')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element DocOther object \"DocOther.celem\";'+source[index:])
 if kind in ['module-interface','object-provide','object-implementation','registered-implementation','function-import']:
  fixtures={
   'ModuleValue':('function','function Example.ButtonGame::ModuleValue (long value) -> long {}'),
   'ModuleValueBody':('implementation','implementation Example.ButtonGame::ModuleValueBody for Example.ButtonGame::ModuleValue (long value) -> long {body common "module-value.csbody";}'),
   'ModuleSecondBody':('implementation','implementation Example.ButtonGame::ModuleSecondBody for Example.ButtonGame::ModuleValue (long value) -> long {body common "module-second.csbody";}'),
   'ParentRules':('module','module Example.ButtonGame::ParentRules {require Example.ButtonGame::ModuleValue (long) -> long;default Example.ButtonGame::ModuleValue with Example.ButtonGame::ModuleValueBody;}'),
   'Rules':('module','module Example.ButtonGame::Rules extends Example.ButtonGame::ParentRules {description "Owned module interface";}')}
  if kind in ['registered-implementation','function-import']:
   registered=root/'registered-api';registered.mkdir();(registered/'pack.cpack').write_text('pack ReferenceApi version "1" {element Value function "Value.celem";element DefaultBody implementation "DefaultBody.celem";}')
   (registered/'Value.celem').write_text('function ReferenceApi::Value (long value) -> long {provide ReferenceApi::Value with ReferenceApi::DefaultBody;}');(registered/'DefaultBody.celem').write_text('implementation ReferenceApi::DefaultBody for ReferenceApi::Value (long value) -> long {body common "default.csbody";}');(registered/'default.csbody').write_text('return value + 7;')
   source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'registry ReferenceApi '+json.dumps(str(registered/'pack.cpack'))+';dependency ReferenceApi version "1";'+source[index:]);fixtures.pop('ModuleValue');fixtures={name:(kind,source.replace('Example.ButtonGame::ModuleValue ','ReferenceApi::Value ')) for name,(kind,source) in fixtures.items()}
  for name,(_,source) in fixtures.items():(project/(name+'.celem')).write_text(source)
  (project/'module-value.csbody').write_text('return value + 3;');(project/'module-second.csbody').write_text('return value + 100;')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+''.join('element '+name+' '+definition[0]+' "'+name+'.celem";' for name,definition in fixtures.items())+source[index:])
 if kind in ['object-provide','object-implementation','registered-implementation','function-import']:
  (project/'ParentConsumer.celem').write_text('object Example.ButtonGame::ParentConsumer {provide '+('ReferenceApi::Value' if kind in ['registered-implementation','function-import'] else 'Example.ButtonGame::ModuleValue')+' with Example.ButtonGame::ModuleValueBody;}')
  (project/'Consumer.celem').write_text('object Example.ButtonGame::Consumer extends Example.ButtonGame::ParentConsumer {module Example.ButtonGame::Rules;description "Object module scope";}')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element ParentConsumer object "ParentConsumer.celem";element Consumer object "Consumer.celem";'+source[index:])
 if kind=='function-import':
  env['CONFECTORY_FUNCTION_IMPORT_COUNTER']=str(root/'donor-counter.log')
  (project/'ImportedDouble.celem').write_text('function Example.ButtonGame::ImportedDouble (long input) -> long {provide Example.ButtonGame::ImportedDouble with Example.ButtonGame::ImportedDoubleBody;}')
  (project/'ImportedDoubleBody.celem').write_text('implementation Example.ButtonGame::ImportedDoubleBody for Example.ButtonGame::ImportedDouble (long input) -> long {body common "imported-double.csbody";}');(project/'imported-double.csbody').write_text('System.IO.File.AppendAllText(Environment.GetEnvironmentVariable("CONFECTORY_FUNCTION_IMPORT_COUNTER")!,"called\\n");return input * 7;')
  source=manifest.read_text();index=source.rfind('}');manifest.write_text(source[:index]+'element ImportedDouble function "ImportedDouble.celem";element ImportedDoubleBody implementation "ImportedDoubleBody.celem";'+source[index:])
 if kind=='build-jobs':
  env['CONFECTORY_BUILD_UI_SENTINEL']=str(root/'build-sentinel.txt')
  body=project/'main.csbody';body.write_text('System.IO.File.AppendAllText(Environment.GetEnvironmentVariable("CONFECTORY_BUILD_UI_SENTINEL")!,"run\\n");\n'+body.read_text())
 if kind=='blueprint-integrated':
  from v480_integrated_workflow import prepare
  prepare(repo,project,env)
 original=(project/'Score.celem').read_bytes();log=root/'host.log';owned=OwnedResponses(None) if kind=='editor' else None
 with log.open('w') as output:
  host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=output,stderr=subprocess.STDOUT)
  try:
   url=None;deadline=time.monotonic()+45
   while time.monotonic()<deadline:
    for line in log.read_text().splitlines():
     if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
    if url:break
    assert host.poll() is None,log.read_text();time.sleep(.1)
   assert url,log.read_text();origin,token=url.split('/#')
   def restart_actual_host():
    global host,origin,token,url
    host.send_signal(signal.SIGINT);host.wait(timeout=15);assert host.returncode==0,log.read_text()
    offset=log.stat().st_size
    host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=output,stderr=subprocess.STDOUT)
    url=None;deadline=time.monotonic()+45
    while time.monotonic()<deadline:
     with log.open() as stream:stream.seek(offset);lines=stream.read().splitlines()
     for line in lines:
      if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
     if url:break
     assert host.poll() is None,log.read_text();time.sleep(.1)
    assert url,log.read_text();origin,token=url.split('/#')
    page.goto(url);expect(page.locator('#status')).to_have_text('Ready',timeout=30000)
   def send(data):
    req=urllib.request.Request(origin+'/api/request',data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
    return json.load(urllib.request.urlopen(req,timeout=20))
   def envelope(view,op,**kw):return dict(op=op,view=view['view'],scope=view['scope'],**kw)
   def settle(view,request_id):
    for _ in range(200):
     reply=send(envelope(view,'update'));assert reply['ok'],reply
     for row in reply['results']:
      if row['requestId']==request_id:return row,reply
     time.sleep(.01)
    raise AssertionError('request remained pending')
   def update(view):
    for _ in range(400):
     reply=send(envelope(view,'update'));assert reply.get('ok'),reply
     if reply.get('busy'):time.sleep(.01);continue
     assert 'revision' in reply and 'state' in reply,reply
     return reply
    raise AssertionError('read-only update stayed busy')
   def mount():
    for _ in range(400):
     reply=send({'op':'mount'})
     if reply.get('error',{}).get('code')=='busy':time.sleep(.01);continue
     assert reply.get('ok') and 'view' in reply,reply
     return reply
    raise AssertionError('read-only mount stayed busy')
   for headers in [{},{'X-Confectory-Session':token,'Origin':'https://untrusted.invalid'}]:
    try:urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=b'{"op":"mount"}',headers=headers));raise AssertionError('unauthorized transport accepted')
    except urllib.error.HTTPError as error:assert error.code==403
   for path in ['/missing.js','/../project.cpack','/api/snapshot']:
    try:urllib.request.urlopen(origin+path);raise AssertionError('undeclared resource served')
    except urllib.error.HTTPError:pass
   first=mount();assert first['ok'];op='increase' if kind=='button' else 'objects'
   request=envelope(first,'invoke',endpoint=op,requestId='wrong-scope',expectedRevision=first['revision'],input={});request['scope']={'projectId':'other','helperId':'other'}
   assert send(request)['error']['code']=='scope_mismatch'
   request['scope']=dict(first['scope'],helperId='forged-helper');assert send(request)['error']['code']=='scope_mismatch'
   for denied in ['shell','readFile','Confectory.EditorHome.Model::Command','confirm','ai-start','host.open-file','host.create-project','host.close']:
    assert send(envelope(first,'invoke',endpoint=denied,requestId=denied,expectedRevision=first['revision'],input={}))['error']['code']=='endpoint_denied'
   stale=send(envelope(first,'invoke',endpoint=op,requestId='stale',expectedRevision=first['revision']-1,input={}));assert stale['ok'];assert settle(first,'stale')[0]['error']['code']=='stale_revision'
   request=envelope(first,'invoke',endpoint=op,requestId='dedup',expectedRevision=first['revision'],input={});assert send(request)['ok'];row,new=settle(first,'dedup');assert row['ok'],row
   assert send(request)['requestId']=='dedup';request['input']={'unexpected':'changed'};assert send(request)['error']['code']=='request_id_reused'
   assert send(envelope(first,'cancel',requestId='dedup'))['status']=='already_completed'
   assert send(envelope(first,'dispose'))['ok'];assert send(envelope(first,'update'))['error']['code']=='view_closed'
   with sync_playwright() as p,FailureEvidence():
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);expect(page.locator('#status')).to_have_text('Ready',timeout=30000)
    if kind=='button':
     expect(page.locator('#score')).to_have_text('1');page.locator('#increase').click();expect(page.locator('#score')).to_have_text('2');page.locator('#reconnect').click();expect(page.locator('#status')).to_have_text('Reconnected');expect(page.locator('#score')).to_have_text('2');page.locator('#reset').click();expect(page.locator('#score')).to_have_text('0')
    elif kind=='review-before':
     page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click()
     page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-schema-field="initial"]')).to_be_visible(timeout=30000)
     value=page.locator('[data-schema-field="initial"]');value.fill('1');value.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
     page.locator('#semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
     review=page.locator('.window[data-key="review"]');expect(review.locator('[data-change]')).to_be_disabled()
     review.locator('[data-review-advanced]').click();expect(review.locator('[data-source-after]')).to_be_visible()
     review.locator('[data-review-advanced]').click();expect(review.locator('[data-source-after]')).to_be_visible()
     review.locator('[data-close]').click();expect(review).to_have_count(0)
     assert (project/'Score.celem').read_bytes()==original
     print('REPRODUCED ordinary 1c3a68b: selection disabled; second advanced click does not collapse; window X closes without Confirm',flush=True)
    elif kind=='review-presentation':
     prefix='Example.ButtonGame::'
     def presentation_browser():
      page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click()
     def action(selector):
      page.locator('#browser-actions').click();page.locator(selector).click()
     manifest=(project/'project.cpack').read_bytes()
     presentation_browser();page.locator('[data-new]').click();page.locator('.context-menu button').filter(has_text='개념 생성').click();page.locator('#new-declaration-name').fill('ReviewPending');page.locator('#new-declaration').click()
     expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'ReviewPending',timeout=30000)
     page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
     page.locator('.window[data-key="schema"] [data-close]').click();presentation_browser();page.locator('[data-id="'+prefix+'Score"]').click()
     value=page.locator('[data-schema-field="initial"]');value.fill('1');value.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000)
     page.locator('#semantic-save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
     page.locator('.window[data-key="schema"] [data-close]').click();presentation_browser();action('#advanced-source');page.locator('.browser-tools input[type="range"]').press('End')
     for id in ('Score','ReviewPending','ProjectManifest'):page.locator('[data-review-id="'+prefix+id+'"]').check()
     action('#review-group');review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-group]')).to_have_count(2,timeout=30000)
     numeric=review.locator('[data-review-unit="'+prefix+'Score"] [data-semantic-change]');expect(numeric.locator('del')).to_have_text('0');expect(numeric.locator('[data-semantic-after]')).to_have_text('1');expect(numeric.locator('[data-review-group]')).to_be_checked()
     boxes=[numeric.locator(selector).bounding_box() for selector in ('[data-review-group]','strong','del','[aria-hidden]','[data-semantic-after]')];assert max(b['y'] for b in boxes)-min(b['y'] for b in boxes)<8,boxes
     page.screenshot(path='/tmp/confectory-review-numeric-inline.png',full_page=True)
     state=mount();initial_token=state['state']['review']['token'];assert send(envelope(state,'dispose'))['ok']
     review.get_by_role('checkbox',name='Score · 전체 변경',exact=True).uncheck();expect(page.locator('#confirm')).to_be_disabled();review.locator('[data-rereview]').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
     state=mount();current=state['state']['review'];assert current['token']!=initial_token and prefix+'Score' not in [u['id'] for u in current['units']]
     expect(review.locator('.caption strong')).to_have_text('변경 검토 · '+current['units'][0]['id'].split('::')[-1]);assert send(envelope(state,'dispose'))['ok']
     page.screenshot(path='/tmp/confectory-review-subset-caption.png',full_page=True)
     review.locator('[data-close]').click();expect(review).to_have_count(0)
     assert (project/'Score.celem').read_bytes()==original and (project/'project.cpack').read_bytes()==manifest and not (project/'elements/ReviewPending.celem').exists()
     print('PASS actual compact numeric row and fresh subset caption: complete creation group, exact new token, no source writes',flush=True)
    elif kind=='local-augment':
     from v424_local_augment import verify_local_augment
     verify_local_augment(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='function-import':
     from v480_function_import import verify_function_import
     verify_function_import(page,project,registered,root/'donor-counter.log',mount,send,envelope,settle,restart_actual_host)
    elif kind=='registered-implementation':
     from v480_registered_implementation import verify_registered_implementation
     verify_registered_implementation(page,project,registered,mount,send,envelope,settle,restart_actual_host)
    elif kind=='object-implementation':
     from v480_object_implementation import verify_object_implementation
     verify_object_implementation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='object-provide':
     from v480_object_provide import verify_object_provide
     verify_object_provide(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='tab-arrangement':
     from v480_window_documents import verify_window_documents
     verify_window_documents(page,project,mount,send,envelope,settle,restart_actual_host,arrange=True)
    elif kind=='navigation-state':
     from v480_navigation import verify_navigation
     verify_navigation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='workspace-links':
     from v480_workspace_links import verify_workspace_links
     verify_workspace_links(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='window-documents':
     from v480_window_documents import verify_window_documents
     verify_window_documents(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='note-documents':
     from v480_note_documents import verify_note_documents
     verify_note_documents(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='rich-notes':
     from v480_rich_notes import verify_rich_notes
     verify_rich_notes(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='placed-find':
     from v480_placed_find import verify_placed_find
     verify_placed_find(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='module-interface':
     from v480_module_interface import verify_module_interface
     verify_module_interface(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='registered-call':
     from v480_registered_call import verify_registered_call
     verify_registered_call(page,project,registered,mount,send,envelope,settle,restart_actual_host)
    elif kind=='call-wrapper':
     from v480_call_wrapper import verify_call_wrapper
     verify_call_wrapper(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='feature-create':
     from v480_feature_creation import verify_feature_creation
     verify_feature_creation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-create':
     from v480_node_creation import verify_node_creation
     verify_node_creation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='ref-nodes':
     from v480_ref_nodes import verify_ref_nodes
     verify_ref_nodes(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-switch':
     from v480_switch import verify_switch
     verify_switch(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-enum-plan':
     from v480_enum_plan import verify_enum_plan
     verify_enum_plan(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-methods':
     from v480_methods import verify_methods
     verify_methods(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-code-regions':
     from v480_code_regions import verify_code_regions
     verify_code_regions(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-integrated':
     from v480_integrated_workflow import verify_integrated
     verify_integrated(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-property-ref':
     from v480_property_ref import verify_property_ref
     verify_property_ref(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-property-set':
     from v480_property_set import verify_property_set
     verify_property_set(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-property':
     from v480_property import verify_property
     verify_property(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-nested':
     from v480_nested import verify_nested
     verify_nested(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='alias-locals':
     from v480_alias_locals import verify_alias_locals
     verify_alias_locals(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='locals':
     from v480_locals import verify_locals
     verify_locals(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='multiout':
     from v480_multiout import verify_multiout
     verify_multiout(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-external-ref':
     from v480_external_ref import verify_external_ref
     verify_external_ref(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-implicit':
     from v480_implicit_conversion import verify_implicit_conversion
     verify_implicit_conversion(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint-camera':
     from v480_blueprint_camera import verify_blueprint_camera
     verify_blueprint_camera(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='blueprint':
     from v480_blueprint import verify_blueprint
     verify_blueprint(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='node-tasks':
     from v424_node_tasks import verify_node_tasks
     verify_node_tasks(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='build-jobs':
     from v424_build_jobs import verify_build_jobs
     verify_build_jobs(page,project,report,env,mount,send,envelope,settle,restart_actual_host)
    elif kind=='draft-history':
     from v424_draft_history import verify_draft_history
     verify_draft_history(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='source-conflict':
     from v424_source_conflict import verify_source_conflict
     verify_source_conflict(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='startup-restore':
     from v424_startup_restore import verify_startup_restore
     verify_startup_restore(page,project,restart_actual_host)
    elif kind=='object-variation':
     from v424_object_variation import verify_object_variation
     verify_object_variation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='schema-actions':
     from v424_schema_actions import verify_schema_actions
     verify_schema_actions(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='schema-exact':
     from v424_schema_exact import verify_schema_exact
     verify_schema_exact(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='reference-gestures':
     from v480_reference_navigation import verify_reference_navigation
     verify_reference_navigation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='declaration-navigation':
     from v480_declaration_navigation import verify_declaration_navigation
     verify_declaration_navigation(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='browser-data-fill':
     from v480_browser_fill import verify_browser_fill
     verify_browser_fill(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='browser-data-fields':
     from v480_browser_data import verify_browser_data
     verify_browser_data(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='instant-table':
     from v424_instant_table import verify_instant_table
     verify_instant_table(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='reference-definition':
     from v424_reference_ui import verify_reference_definition
     verify_reference_definition(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='relations-map':
     from v424_relations_map import verify_relations_map
     verify_relations_map(page,project,mount,send,envelope,settle,restart_actual_host)
    elif kind=='declaration-forms':
     def open_browser():
      page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click();page.locator('.window[data-key="browser"] [data-tab="concept"]').click();expect(page.locator('#nav')).to_be_enabled()
     def browser_action(selector):page.locator('#browser-actions').click();page.locator(selector).click()
     from v424_declaration_forms import verify_declaration_forms
     verify_declaration_forms(page,project,mount,send,envelope,settle,open_browser,browser_action,restart_actual_host)
    elif kind=='declarations':
     def open_browser():
      page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click()
     def browser_action(selector):page.locator('#browser-actions').click();page.locator(selector).click()
     from v424_authoring import verify_declaration_kinds
     verify_declaration_kinds(page,project,mount,send,envelope,settle,open_browser,browser_action,restart_actual_host)
    elif kind=='creation':
     def open_browser():
      page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();expect(page.locator('#nav')).to_be_enabled();page.locator('#nav').click()
     def browser_action(selector):page.locator('#browser-actions').click();page.locator(selector).click()
     from semantic_authoring import verify_concept_creation
     verify_concept_creation(page,project,mount,send,envelope,open_browser,browser_action,restart_actual_host)
    else:
     def nav_menu(visible):
      # Navigation is local UI state: never leave a blind toggle over the next source action.
      for _ in range(3):
       if bool(page.locator('.nav-menu').count())==visible:return
       page.locator('#nav').click()
      expect(page.locator('.nav-menu')).to_have_count(1 if visible else 0)
     def open_browser():
      selected=page.locator('.window[data-key="browser"] [data-tab].selected');group=selected.get_attribute('data-tab') if selected.count() else 'concept'
      nav_menu(True);page.locator('.nav-menu').get_by_role('button',name={'concept':'개념','feature':'기능','module':'모듈'}[group],exact=True).click();expect(page.locator('#nav')).to_be_enabled();nav_menu(False)
     def browser_action(selector):
      page.locator('#browser-actions').click();page.locator(selector).click()
     def retained_window(index=0):
      page.locator('#browser-actions').click();page.locator('.context-menu button').filter(has_text='유지된 창 ·').nth(index).click()
     def propose_direction(text):
      page.locator('.augment-overlay [data-propose]').click();page.locator('#augment-direction').fill(text);page.locator('.modal form button[type="submit"]').click()
     # Every original portrait must cross the ordinary declared-resource transport intact.
     for image_path in sorted((repo/'examples/editor-home/ui/assets').glob('*.png')):
      served=urllib.request.urlopen(origin+'/assets/'+image_path.name).read()
      assert hashlib.sha256(served).digest()==hashlib.sha256(image_path.read_bytes()).digest()
      assert page.evaluate("async path=>{const image=new Image();image.src=path;await image.decode();return image.naturalWidth>0&&image.naturalHeight>0}",'/assets/'+image_path.name)
     page.locator('#issues').click();expect(page.locator('.modal')).to_contain_text('연결되지 않았습니다');page.locator('.modal [data-close]').click()
     assert page.locator('.home-side').is_visible()
     assert not page.locator('#source').is_visible(),'raw source should be an explicit advanced view'
     page.locator('#add-helper').click();expect(page.locator('[data-recruit="global"]')).to_be_visible()
     page.locator('[data-recruit="global"]').click();expect(page.locator('#helper-list')).to_contain_text('main-helper')
     page.locator('#helper-list button').click();expect(page.locator('#helper-summary')).to_contain_text('main-helper',timeout=30000)
     expect(page.locator('.helper-local-settings')).to_contain_text('기억 대상: main-helper',timeout=30000)
     # Common memory excluded by default. No provider or account is opened.
     expect(page.locator('#allow-common')).not_to_be_checked()
     page.locator('#helper-memory').fill('local explicitly scoped note');page.locator('#remember').click();expect(page.locator('#status')).to_contain_text('로컬에 저장됨',timeout=30000)
     page.locator('.modal [data-close]').click()
     page.locator('#chat').click();page.locator('#chat-input').fill('local project message');page.locator('#chat-input').blur();expect(page.locator('#status')).to_contain_text('전송 없음')
     page.locator('#add-agent').click();expect(page.locator('[data-connection-choice]')).to_have_count(2)
     local_state=mount();assert local_state['scope']['helperId']=='main-helper';assert not local_state['scope']['allowCommon'];assert local_state['state']['chatDraft']=='local project message';assert local_state['state']['aiState']=='idle';assert 'memory' not in local_state['state']['helperProfile'];assert 'config' not in local_state['state'];assert send(envelope(local_state,'dispose'))['ok']
     page.locator('[data-connection-cancel]').click()

     open_browser();button=page.locator('[data-id="Example.ButtonGame::Score"]');expect(button).to_be_visible();button.click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score');page.screenshot(path='/tmp/confectory-v196-semantic-project.png',full_page=True);page.locator('#yogi').click();expect(page.locator('#nav')).to_be_enabled();page.locator('[data-schema-field="initial"]').click();page.locator('[data-type="ey"]').click();expect(page.locator('#yogi-items')).to_contain_text('Example.ButtonGame::Score');page.locator('[data-type="lay"]').click();page.locator('#yogi-capture').click();expect(page.locator('#yogi-items')).to_contain_text('선택 영역 이미지',timeout=30000);page.locator('[data-operation="image-preview"]').click();expect(page.locator('[data-yogi-image]')).to_be_visible();assert page.locator('[data-yogi-image]').evaluate("canvas=>{const bytes=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;return new Set(bytes).size>2}")
     capture_state=mount();images=[item for item in capture_state['state']['yogi']['items'] if item['kind']=='image'];assert len(images)==1 and 'pixels' not in images[0]['capture'];assert 0<images[0]['capture']['width']<=512 and 0<images[0]['capture']['height']<=512
     invalid={'action':'capture','id':'Example.ButtonGame::Score','image':{'encoding':'rgb24-base64','width':1,'height':1,'pixels':'AAAA','hash':'0'*64}}
     assert send(envelope(capture_state,'invoke',endpoint='yogi',requestId='bad-capture-hash',expectedRevision=capture_state['revision'],input=invalid))['ok'];rejected,after_capture=settle(capture_state,'bad-capture-hash');assert not rejected['ok'];assert len(after_capture['state']['yogi']['items'])==2 and after_capture['state']['yogi']['pending']==[];assert send(envelope(capture_state,'dispose'))['ok']
     page.locator('#yogi-text').fill('local object package');page.locator('#yogi-text').blur();expect(page.locator('#status')).to_contain_text('내용 적용됨');page.locator('#yogi-seal').click();expect(page.locator('.yogi-package')).to_be_visible();page.locator('.yogi-package').click();expect(page.locator('#yogi-seal')).to_have_text('확정');page.locator('.yogi-clipboard [data-close]').click();page.locator('.window[data-key="schema"] [data-close]').click();open_browser();browser_action('#advanced-source');expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000);expect(page.locator('#selection')).to_have_text('Example.ButtonGame::Score')
     advanced=mount();bodies=[u['id'] for u in advanced['state']['units'] if u['kind']=='body'];assert bodies,'advanced mode must expose actual owned bodies';owned.target=bodies[0];assert send(envelope(advanced,'dispose'))['ok']
     page.locator('[data-id="'+bodies[0]+'"]').click();expect(page.locator('#selection')).to_have_text(bodies[0],timeout=30000)
     open_browser();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000);open_browser();browser_action('#advanced-source')
     # Independent production Model owners retain exact IDs and local input across selection/hide/poll.
     open_browser();browser_action('#keep-source')
     one=page.locator('.window[data-key="editor-1"]');expect(one.locator('[data-editor-id]')).to_have_text('Example.ButtonGame::Score')
     first_text=one.locator('[data-editor-source]').input_value();one.locator('[data-editor-source]').fill(first_text+'\n// retained independently\n')
     open_browser();page.locator('[data-id="'+bodies[0]+'"]').click();open_browser();browser_action('#keep-source')
     two=page.locator('.window[data-key="editor-2"]');expect(two.locator('[data-editor-id]')).to_have_text(bodies[0]);other_text=two.locator('[data-editor-source]').input_value();two.locator('[data-editor-source]').fill(other_text+'\n// second independent input\n')
     open_browser();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000)
     # A primary selection does not retarget either independent source window.
     expect(one.locator('[data-editor-source]')).to_have_value(first_text+'\n// retained independently\n');expect(two.locator('[data-editor-source]')).to_have_value(other_text+'\n// second independent input\n')
     page.locator('.brand').click();expect(page.locator('[data-project]')).not_to_have_count(0);page.locator('[data-project]').filter(has_text='ButtonGame').first.locator('[data-enter]').click()
     one=page.locator('.window[data-key="editor-1"]');two=page.locator('.window[data-key="editor-2"]');expect(one.locator('[data-editor-source]')).to_have_value(first_text+'\n// retained independently\n');expect(two.locator('[data-editor-source]')).to_have_value(other_text+'\n// second independent input\n')
     open_browser();retained_window();one.locator('[data-close]').click();open_browser();retained_window();expect(one.locator('[data-editor-source]')).to_have_value(first_text+'\n// retained independently\n')
     one.locator('[data-editor-apply]').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000)
     shared=mount();assert shared['state']['draft']['text']==first_text+'\n// retained independently\n';assert shared['state']['editorViews'][0]['id']=='Example.ButtonGame::Score';assert shared['state']['editorViews'][1]['id']==bodies[0];assert send(envelope(shared,'dispose'))['ok']
     # Restore only the edited draft through the public CAS action, and release clean owners.
     one.locator('[data-editor-source]').fill(first_text);one.locator('[data-editor-apply]').click();expect(page.locator('#status')).to_have_text('Shared draft updated');one.locator('[data-editor-release]').click();expect(page.locator('.window[data-key^="editor-"]')).to_have_count(1)
     open_browser();retained_window();two.locator('[data-editor-reset]').click();two.locator('[data-editor-release]').click()
     open_browser();page.locator('[data-tab="feature"]').click();expect(page.locator('#objects [data-id="Example.ButtonGame::Score"]')).to_have_count(0,timeout=30000);expect(page.locator('#objects [data-id="Example.ButtonGame::Main"]')).to_be_visible(timeout=30000)
     open_browser();browser_action('#keep-properties');prop=page.locator('.window[data-key="editor-1"]');expect(prop.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score')
     open_browser();page.locator('[data-id="Example.ButtonGame::Main"]').click();expect(page.locator('#browser-actions')).to_be_enabled(timeout=30000);open_browser();retained_window()
     field=prop.locator('[data-schema-field="initial"]');field.fill('7');field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000);expect(prop.locator('[data-schema-field="initial"]')).to_have_value('7')
     field=prop.locator('[data-schema-field="initial"]');field.fill('0');field.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(prop.locator('[data-schema-field="initial"]')).to_have_value('0',timeout=30000);prop.locator('[data-operation="release-view"]').click();expect(page.locator('.window[data-key^="editor-"]')).to_have_count(0)
     page.locator('[data-tab="concept"]').click();expect(page.locator('#objects [data-id="Example.ButtonGame::Main"]')).to_have_count(0);expect(page.locator('#objects [data-id="Example.ButtonGame::Score"]')).to_be_visible();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#browser-actions')).to_be_enabled();open_browser();browser_action('#advanced-source');expect(page.locator('#source')).to_be_visible(timeout=30000)
     no_task=mount()
     for endpoint in ['prepareWorker','stopWorker','recoverWorker','inspectAdoption','reviewWorker','adoptWorker']:
      no_task_state=update(no_task);request_id='foreign-'+endpoint;assert send(envelope(no_task,'invoke',endpoint=endpoint,requestId=request_id,expectedRevision=no_task_state['revision'],input={'task':'unowned-task','ids':['Unowned::Source'],'token':'forged','goalEvidence':'must not write'}))['ok'];failed,no_task_state=settle(no_task,request_id);assert not failed['ok'],endpoint
     assert send(envelope(no_task,'dispose'))['ok']
     source=page.locator('#source');text=source.input_value()+'\n// common-web-ui-draft\n';source.fill(text);page.locator('#save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged',timeout=30000)
     assert (project/'Score.celem').read_bytes()==original,'Save performed source Confirm'
     retained_draft=mount();assert retained_draft['state']['draft']['text']==text;assert send(envelope(retained_draft,'dispose'))['ok']
     page.reload();expect(page.locator('#status')).to_have_text('Ready');open_browser();browser_action('#advanced-source');expect(source).to_have_value(text)
     # Another independent mount reads the same domain draft, without a UI-only storage copy.
     second=mount();assert second['state']['draft']['text']==text and second['state']['draft']['dirty'];assert 'context' not in second['state'] and 'path' not in second['state']['draft']
     # Consumer CAS also rejects an outdated draft revision under a fresh transport revision.
     stale_input={'id':second['state']['draft']['id'],'text':'must not replace the shared draft','revision':second['state']['draft']['revision']-1}
     assert send(envelope(second,'invoke',endpoint='editDraft',requestId='draft-cas',expectedRevision=second['revision'],input=stale_input))['ok']
     result,current=settle(second,'draft-cas');assert not result['ok'] and current['state']['draft']['text']==text
     request=envelope(second,'invoke',endpoint='select',requestId='foreign-object',expectedRevision=current['revision'],input={'id':'Unowned.Project::Object'})
     assert send(request)['ok'];assert not settle(second,'foreign-object')[0]['ok']
     assert send(envelope(second,'dispose'))['ok']
     page.locator('#review').click();expect(page.locator('[data-review-advanced]')).to_be_visible(timeout=30000)
     from semantic_authoring import inspect_advanced_review
     inspect_advanced_review(page)
     assert (project/'Score.celem').read_bytes()==original,'Review performed source Confirm'
     review=mount();assert review['state']['review']['id']=='Example.ButtonGame::Score'
     assert review['state']['review']['before']==original.decode() and review['state']['review']['after']==text
     assert 'path' not in review['state']['review'];assert send(envelope(review,'dispose'))['ok']
     page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
     assert (project/'Score.celem').read_text()==text,'explicit compiler-backed Confirm did not apply exact reviewed source'
     page.locator('#schema').click();expect(page.locator('[data-schema-id]')).to_have_text('Example.ButtonGame::Score',timeout=30000)
     schema_state=mount();assert schema_state['state']['schema']['id']=='Example.ButtonGame::Score';assert send(envelope(schema_state,'dispose'))['ok']
     # Actual settings pack authoring and permission review, with no credentials or provider dispatch.
     page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible(timeout=30000);page.locator('#add-helper').click();expect(page.locator('#global-helper-list')).to_contain_text('main-helper');page.locator('.modal [data-close]').click();page.locator('#add-agent').click()
     setup=page.get_by_role('dialog',name='사용할 AI',exact=True);setup.get_by_role('button',name='OpenAI Responses',exact=True).click()
     expect(setup.locator('[data-connection-field="model"]')).to_be_visible(timeout=30000)
     assert page.locator('.home-grid').is_visible()
     for name,value in [('model','owned-ui-no-call'),('endpoint',owned.endpoint),('credentialReference','')]:
      setup.locator('[data-connection-field="'+name+'"]').fill(value)
     setup.locator('[data-connection-save]').click();expect(setup.locator('[data-connection-result]')).to_contain_text('설정 초안을 저장',timeout=30000)
     setup.locator('[data-connection-cancel]').click();expect(page.locator('[data-project]')).to_have_count(1,timeout=30000);page.locator('[data-enter]').click()
     page.locator('#add-agent').click();setup=page.get_by_role('dialog',name='사용할 AI',exact=True);setup.get_by_role('button',name='OpenAI Responses',exact=True).click();expect(setup.locator('[data-connection-field="model"]')).to_have_value('owned-ui-no-call')
     setup.locator('[data-connection-use]').click();expect(page.locator('#status')).to_contain_text('설정 선택됨',timeout=30000)
     setup.locator('[data-connection-cancel]').click();page.locator('#chat').click();page.locator('#chat-input').fill('review without sending');page.locator('#chat-prepare').click();expect(page.locator('#ai-start')).to_be_disabled(timeout=30000)
     preview=mount();assert preview['state']['aiPreview']['message']=='review without sending';assert 'config' not in preview['state']['aiPreview'];assert len(preview['state']['aiPreview']['requirements'])==2
     assert send(envelope(preview,'invoke',endpoint='startAI',requestId='unapproved-start',expectedRevision=preview['revision'],input={'token':preview['state']['aiPreview']['token']}))['ok'];refused,after=settle(preview,'unapproved-start');assert not refused['ok'] and after['state']['aiOutput'] in [None,''];assert send(envelope(preview,'dispose'))['ok']
     page.locator('[data-permission="contentApproved"]').check();expect(page.locator('#status')).to_contain_text('아직 전송 없음');expect(page.locator('#ai-start')).to_be_disabled()
     page.locator('#cancel-preview').click();expect(page.locator('#status')).to_contain_text('전송 없음');page.locator('#logs-tab').click()
     page.locator('#augment').click();propose_direction('retain semantic object focus');expect(page.locator('#ai-start')).to_be_disabled(timeout=30000)
     proposal=mount();assert proposal['state']['aiPreview']['kind']=='proposals' and proposal['state']['aiPreview']['target']=='Example.ButtonGame::Score';assert proposal['state']['augment']['cards']==[];assert proposal['state']['workers']==[];assert send(envelope(proposal,'dispose'))['ok']
     page.locator('#cancel-preview').click();expect(page.locator('#status')).to_contain_text('전송 없음');assert owned.requests==[],'preflight/denied start contacted provider'
     # Positive HTML path over unchanged production Responses, Agent, tools, Task and adoption contracts.
     expect(page.locator('.augment-overlay')).to_be_visible();propose_direction('Owned loopback proposal, no account or credentials')
     def approve_and_start():
      for permission in ['contentApproved','usageApproved']:
       choice=page.locator('[data-permission="'+permission+'"]');choice.check();expect(choice).to_be_enabled(timeout=30000)
      expect(page.locator('#ai-start')).to_be_enabled(timeout=30000);page.locator('#ai-start').click();expect(page.locator('.window[data-key="ai-preview"]')).to_have_count(0,timeout=30000)
     approve_and_start();expect(page.locator('[data-card]')).to_have_count(3,timeout=30000);assert len(owned.requests)==1 and not owned.errors,owned.errors
     page.locator('[data-card]').first.click();expect(page.locator('#worker-summary button')).to_have_count(1,timeout=30000);page.locator('.augment-overlay [data-close]').click();page.locator('.home-side [data-helper]').filter(has_text='main-helper').click();page.locator('.participant-expanded-card [data-worker]').click();page.locator('#worker-prepare').click();approve_and_start()
     expect(page.locator('#worker-source-list')).to_contain_text(bodies[0],timeout=30000);expect(page.locator('.window[data-key="worker"]')).to_contain_text('awaiting-verification',timeout=30000);assert len(owned.requests)==4 and not owned.errors,owned.errors
     body_owner=bodies[0].split('::',1)[1].split('/body:',1)[0];locator=re.search(r'element\s+'+re.escape(body_owner)+r'\s+implementation\s+"([^"]+)"',manifest.read_text());assert locator;definition=(project/locator.group(1)).read_text();body_path=project/re.search(r'body\s+common\s+"([^"]+)"',definition).group(1);before_worker=body_path.read_text();assert 'owned HTTP Worker draft' not in before_worker,'Worker bypassed draft boundary'
     page.locator('[data-worker-source]').check();page.locator('#worker-review').click();expect(page.locator('#worker-adopt')).to_be_enabled(timeout=30000);assert body_path.read_text()==before_worker,'Review committed Worker draft'
     page.locator('#worker-goal-evidence').fill('Observed exact owned HTTP comment staged in the selected body. Compiler and source acceptance only; game runtime outcome not executed.');page.locator('#worker-adopt').click();expect(page.locator('.window[data-key="worker-review"]')).to_have_count(0,timeout=180000);assert body_path.read_text()==before_worker+'\n// owned HTTP Worker draft; human review required\n'
     adopted=mount();assert adopted['state']['workers'][0]['status']=='completed';assert adopted['state']['workers'][0]['adoptionState']=='recorded';assert send(envelope(adopted,'dispose'))['ok'];page.locator('.window[data-key="worker"] [data-close]').click()
     page.locator('#build-target').click();expect(page.locator('[data-target-choice] option')).to_have_count(3);page.locator('[data-target-choice]').select_option('windows');expect(page.locator('#status')).to_contain_text('windows');page.locator('[data-target-choice]').select_option('linux');page.locator('.window[data-key="targets"] [data-close]').click()
     open_browser();browser_action('#advanced-source')
     from semantic_authoring import verify_schema_authoring
     verify_schema_authoring(page,project,mount,send,envelope,open_browser,browser_action,retained_window)
     pending_text=text+'\n// retained browser input\n';source.fill(pending_text)
     page.locator('.brand').click();expect(page.locator('[data-project]')).to_have_count(1,timeout=30000)
     page.screenshot(path='/tmp/confectory-v196-consumer-home.png',full_page=True)
     page.locator('#open-project').click();expect(page.locator('.modal')).to_contain_text('지원하지 않습니다');page.locator('.modal [data-close]').click()
     page.locator('[data-enter]').click();expect(page.locator('#source')).to_have_value(pending_text,timeout=30000)
     assert (project/'Score.celem').read_text()==text,'hide/open committed unsaved browser input'
     assert mount()['state']['draft']['text']==text,'HTML input became domain draft without Apply'
     source_window=page.locator('.window[data-key="source"]');source_window.locator('[data-fold]').click();expect(source).not_to_be_visible()
     assert source.input_value()==pending_text;source_window.locator('[data-fold]').click();expect(source).to_have_value(pending_text)
     # v318 uses a panning world; fixed Dock controls must remain usable above it.
     assert page.locator('#dock').evaluate("dock=>[...dock.querySelectorAll('.bubble')].every(button=>{const r=button.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.closest('button')===button;})"),'world windows occlude fixed Dock controls'
     page.set_viewport_size({'width':960,'height':700});expect(source).to_have_value(pending_text);page.set_viewport_size({'width':1280,'height':720})
     page.locator('#run').click();page.locator('[data-run-play]').click();expect(page.locator('[data-run-stop]')).to_be_enabled(timeout=30000)
     execution=mount();assert execution['state']['executionState'] in ['building','running'];assert send(envelope(execution,'dispose'))['ok']
     # Live execution logs can advance the common revision after Update and before queued Invoke.
     # A rejected stale request executed nothing: explicitly retry the real UI Stop action only.
     for attempt in range(5):
      page.locator('[data-run-stop]').click();expect(page.locator('#run')).to_be_enabled(timeout=30000)
      if page.locator('#status').inner_text()!='stale_revision':break
     expect(page.locator('[data-run-play]')).to_be_enabled(timeout=30000)
     stopped=mount();assert stopped['state']['executionState']=='stopped',stopped['state']['executionState'];assert send(envelope(stopped,'dispose'))['ok']
     expect(page.locator('#execution-logs')).to_contain_text('Stopped this project execution');expect(source).to_have_value(pending_text)
     assert (project/'Score.celem').read_text()==text,'Run/Stop applied unconfirmed browser input'
     changed_view=mount();assert send(envelope(changed_view,'invoke',endpoint='select',requestId='other-editor-selection',expectedRevision=changed_view['revision'],input={'id':'Example.ButtonGame::Main'}))['ok']
     changed_row,changed_state=settle(changed_view,'other-editor-selection');assert changed_row['ok'];assert changed_state['state']['draft']['id']=='Example.ButtonGame::Main'
     expect(page.locator('#source-notice')).to_contain_text('입력을 유지했습니다',timeout=30000);expect(source).to_have_value(pending_text);expect(page.locator('#selection')).to_have_text('Example.ButtonGame::Score')
     open_browser();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('#source-notice')).to_have_text('',timeout=30000);expect(source).to_have_value(pending_text)
     assert send(envelope(changed_view,'dispose'))['ok']
     # The preceding regression deliberately retained unapplied Score input. Explicitly revert it
     # to the already confirmed file through the ordinary Apply control before starting another edit.
     open_browser();browser_action('#advanced-source');source.fill((project/'Score.celem').read_text());page.locator('#apply').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000)
     from semantic_authoring import verify_concept_creation
     verify_concept_creation(page,project,mount,send,envelope,open_browser,browser_action,restart_actual_host)






    page.screenshot(path='/tmp/confectory-web-ui-'+kind+'.png',full_page=True);assert not errors,errors;browser.close()
   print('Actual common WebUI '+kind+' Chromium PASS')
  except Exception:
   try:
    page.screenshot(path='/tmp/confectory-web-ui-failure.png',full_page=True);print('UI failure status:',page.locator('#status').inner_text(),flush=True)
   except Exception:pass
   raise
  finally:
   if host.poll() is None:host.send_signal(signal.SIGINT)
   try:host.wait(timeout=15)
   except subprocess.TimeoutExpired:host.kill();host.wait();raise AssertionError('host lifetime cleanup did not complete')
   if owned is not None:owned.close()
   assert host.returncode==0,log.read_text()
