"""Existing value/ref/out/return information function contract in the real body editor/compiler."""
import json,re,shutil,subprocess,time
from playwright.sync_api import sync_playwright,expect
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'7'*32
signature={'args':[{'name':'amount','type':'long'},{'name':'total','type':'long','mode':'ref'},{'name':'ready','type':'bool','mode':'out'}],'return':'long'}
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('schema',{'id':owner});s=f.state()['schema'];basis=f.invoke('blueprint',{'action':'readOwnerEdits','id':owner,'hash':s['textHash']})['result']['result']['basis'];f.invoke('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':basis,'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'누적 계산','description':'ref와 out 보존','signature':signature}]}})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1850,'height':1450});d.open_info();f.idle();f.owner().locator('[data-inline-method] [data-function-write-direct]').click();body=f.author().locator('[data-bp-node=body]');expect(body).to_be_visible();expect(f.author().locator('[data-bp-name]')).to_have_value('누적 계산');f.author().locator(':scope>.window-title .caption').click(position={'x':5,'y':5});f.author().locator('[data-bp-overview-node=body]').click();body.locator('[data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');expect(value).to_have_value(re.compile('ref long total'));expect(value).to_have_value(re.compile('out bool ready'));value.evaluate(r'''el=>{el.focus();el.setSelectionRange(el.value.indexOf('\n{\n')+3,el.value.lastIndexOf('\n}'));}''');f.page.keyboard.insert_text('total+=amount;ready=true;return total;');dialog.locator('[data-code-save]').click();f.author().locator('[data-bp-save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   if not [v for key,v in f.pending()['blueprint'] if '|v508-author|' in key]:break
   f.page.wait_for_timeout(30)
  assert not [v for key,v in f.pending()['blueprint'] if '|v508-author|' in key];f.close_author();f.invoke('schema',{'id':owner});actual=next(row for row in f.state()['schema']['ownFunctions'] if row['id']==fn)['signature'];assert [(v['Name'],v['Type'],v.get('Mode')) for v in actual['Args']]==[('amount','long',None),('total','long','ref'),('ready','bool','out')] and actual['return']=='long';f.originals();f.checked('실제 정보 본문 UI는 기존 long/ref/out/반환 계약을 보호하고 C# 본문만 임시 저장한다')
  review=d.review()
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);f.idle();clone=f.case/'typed callable compile';shutil.copytree(f.project,clone,ignore=shutil.ignore_patterns('.confectory'));main=clone/'MainBody.celem';main.write_text(main.read_text().replace('{','{import '+fn+' as OwnCall (long,ref long,out bool) -> long in '+owner+';',1));(clone/'Main.csbody').write_text('long total=3;return checked((int)calls.OwnCall.Invoke(2,ref total,out bool ready));');compiled=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(clone/'project.cproj'),'portable'],capture_output=True,text=True,env=f.env);(f.case/'typed-scope-build.json').write_text(compiled.stdout);assert compiled.returncode==0,compiled.stderr;assert not json.loads(compiled.stdout)['warnings'];f.checked('명시적 compiler Confirm과 별도 사본의 실제 정보 scope value/ref/out/반환 호출이 경고 없이 컴파일되며 프로젝트를 실행하지 않는다');assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'own-body-typed-failure.json').write_text(json.dumps({'state':f.state(),'traffic':f.traffic[-100:],'checks':f.checks,'errors':f.errors},ensure_ascii=False,indent=2));f.page.screenshot(path=str(f.case/'own-body-typed-failure.png'))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':True,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
