"""Actual installed Chromium, local pack host, no external deployment or uploads."""
import json, os, pathlib, re, signal, subprocess, sys, tempfile, time, urllib.request
from playwright.sync_api import sync_playwright, expect
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
env=os.environ.copy();env['CONFECTORY_EDITOR_REPO']=str(repo)
with tempfile.TemporaryDirectory(prefix='confectory-browser-gate-') as temporary:
 log=pathlib.Path(temporary)/'host.log'
 with log.open('w') as output:
  host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=output,stderr=subprocess.STDOUT)
  try:
   deadline=time.monotonic()+30;url=None
   while time.monotonic()<deadline:
    for line in log.read_text().splitlines():
     if line.startswith('CONFECTORY_BROWSER '):url=line.split(' ',1)[1]
    if url:break
    if host.poll() is not None:raise AssertionError(log.read_text())
    time.sleep(.05)
   assert url,log.read_text()
   origin,token=url.split('/#');origin+='/'
   try:urllib.request.urlopen(urllib.request.Request(origin+'api/snapshot',data=b'{}',headers={'Content-Type':'application/json'}));raise AssertionError('anonymous API accepted')
   except urllib.error.HTTPError as error:assert error.code==403
   with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu'])
    page=browser.new_page(viewport={'width':1200,'height':850});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);page.get_by_role('status').filter(has_text='Ready').wait_for()
    assert page.get_by_role('heading',name='Confectory',exact=True).is_visible()
    bad={'name':'broken.cproj','mimeType':'text/plain','buffer':b'not a pack'}
    page.locator('#file').set_input_files(bad);expect(page.locator('#status')).to_contain_text(re.compile('expected|error',re.I))
    assert page.locator('#project').is_hidden()
    pack={'name':'한글 공백 프로젝트.cproj','mimeType':'text/plain','buffer':b'project BrowserUser version "1" { standalone true; entry BrowserUser::Main; registry Untrusted "DO_NOT_EXECUTE"; target web Untrusted::Build; }'}
    page.locator('#file').set_input_files(pack);page.locator('#project').wait_for(state='visible');assert page.locator('#title').inner_text()=='BrowserUser'
    assert 'standalone declaration: true' in page.locator('#capabilities').inner_text()
    assert 'DO_NOT_EXECUTE' in page.locator('#source').input_value()
    page.locator('#chat').fill('미제출 draft');page.locator('#source').fill(page.locator('#source').input_value()+'\n// browser edit')
    page.locator('#file').set_input_files(pack);expect(page.locator('#status')).to_contain_text('Already open')
    assert page.locator('#chat').input_value()=='미제출 draft' and '// browser edit' in page.locator('#source').input_value()
    other={'name':'library.cpack','mimeType':'text/plain','buffer':b'pack SharedLibrary version "1" { standalone false; }'}
    page.locator('#file').set_input_files(other);expect(page.locator('#status')).to_contain_text('Leave the current')
    assert page.locator('#title').inner_text()=='BrowserUser' and page.locator('#chat').input_value()=='미제출 draft'
    with page.expect_file_chooser() as chooser:page.locator('#file').click()
    chooser.value.set_files([]);assert page.locator('#chat').input_value()=='미제출 draft'
    page.once('dialog',lambda dialog:dialog.dismiss());page.locator('#leave').click();assert page.locator('#project').is_visible()
    with page.expect_download() as pending:page.locator('#download').click()
    download=pending.value;download.save_as(str(pathlib.Path(temporary)/'download.cproj'));assert '// browser edit' in pathlib.Path(download.path()).read_text()
    assert 'Unsaved changes' in page.locator('#dirty').inner_text(),'download initiation must not claim durable save'
    page.once('dialog',lambda dialog:dialog.accept());page.locator('#leave').click();page.locator('#project').wait_for(state='hidden')
    page.locator('#file').set_input_files(other);page.locator('#project').wait_for(state='visible');assert page.locator('#title').inner_text()=='SharedLibrary'
    assert 'standalone declaration: false' in page.locator('#capabilities').inner_text()
    # A clean active project also prevents replacement; no dirty-state prerequisite.
    page.locator('#file').set_input_files(pack);expect(page.locator('#status')).to_contain_text('Leave the current')
    assert page.locator('#title').inner_text()=='SharedLibrary'
    page.locator('#leave').click();page.locator('#project').wait_for(state='hidden');page.locator('#file').set_input_files(pack);page.locator('#project').wait_for(state='visible')
    assert page.locator('#chat').input_value()=='미제출 draft' and '// browser edit' in page.locator('#source').input_value(),'explicit Leave/reopen lost retained session drafts'
    page.set_viewport_size({'width':390,'height':844});assert page.locator('#source').bounding_box()['width']<390
    page.screenshot(path=os.environ.get('CONFECTORY_BROWSER_SCREENSHOT',str(pathlib.Path(temporary)/'browser.png')));assert not errors,errors
    # Forbidden commands fail with the authenticated session; native path/run cannot be tunneled.
    reply=page.request.post(origin+'api/run',data='{}',headers={'X-Confectory-Session':token,'Content-Type':'application/json'});assert reply.status==400
    browser.close()
   host.send_signal(signal.SIGINT);host.wait(timeout=10);assert host.returncode==0,log.read_text()
   print('Actual Chromium Browser Entry/Home PASS: startup/render/input/import/repeat/cancel/unsaved/clean-active guard/leave/reopen/download/loopback capabilities/owner exit')
  finally:
   if host.poll() is None:host.kill();host.wait(timeout=10)
