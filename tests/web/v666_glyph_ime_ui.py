"""Shared glyph/image picker IME cancel; generated assets, synthetic DOM events only."""
import base64,json,pathlib,sys,traceback
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3]if len(sys.argv)>3 else'normal';leaf='GlyphCategory';owner=f.n+leaf;glyph='한'
for suffix in ['Base','']:
 name=leaf+suffix;parent=''if suffix else' extends '+f.n+leaf+'Base'
 (f.project/(name+'.celem')).write_text('category '+f.n+name+parent+' { // IME 원본 주석 😀\r\nvalue Exact=9223372036854775805;value editorIcon="📦";}')
 f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' category "'+name+'.celem";registry Confectory.Build.DotNet'))
file=f.project/(leaf+'.celem');snapshot={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()};phase=snapshot.copy()
def panel():return f.page.locator('.window[data-key=declaration]')
def icon():return panel().locator('.object-icon-control>.obj-icon')
def pending():return [(k,v)for k,v in f.pending()['schema']if '|'+owner+'|element|'in k]
def original():assert all(p.read_bytes()==v for p,v in phase.items())
def open_card():
 f.idle()
 if panel().locator('.object-title-name').is_visible()and panel().locator('.object-title-name').inner_text()==leaf:return
 f.page.locator('#workspace').click(button='right',position={'x':1550,'y':140});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=concept]').click();b.locator('[data-browser-control=object-query]').fill(leaf);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+owner+'"]').press('F2');f.idle();b.locator('[data-close]').first.click();expect(panel().locator('.object-title-name')).to_have_text(leaf)
def popup():
 panel().locator('.object-icon-edit').click();p=f.page.get_by_role('dialog',name=leaf+' 아이콘 편집',exact=True);expect(p).to_be_visible();return p
def image(p):
 uri=f.page.evaluate("()=>{const c=document.createElement('canvas');c.width=64;c.height=32;const x=c.getContext('2d');x.fillStyle='#936';x.fillRect(0,0,64,32);return c.toDataURL('image/png')}");p.locator('[type=file]').set_input_files(dict(name='synthetic-ime.png',mimeType='image/png',buffer=base64.b64decode(uri.split(',')[1])));expect(p.locator('.object-icon-preview img')).to_be_visible();expect(p.locator('[type=submit]')).to_be_enabled();return p.locator('.object-icon-preview img').get_attribute('src')
def ime(field,legacy):
 flags=field.evaluate("(el,legacy)=>{el.dispatchEvent(new CompositionEvent('compositionstart',{data:'한',bubbles:true}));const e=new KeyboardEvent('keydown',{key:'Escape',code:'Escape',bubbles:true,cancelable:true,isComposing:!legacy,keyCode:legacy?229:27});el.dispatchEvent(e);el.dispatchEvent(new CompositionEvent('compositionend',{data:'한',bubbles:true}));return {composing:e.isComposing,keyCode:e.keyCode,trusted:e.isTrusted,prevented:e.defaultPrevented};}",legacy);assert flags==dict(composing=not legacy,keyCode=229 if legacy else 27,trusted=False,prevented=mode=='baseline'),flags
def exercise(kind,legacy):
 p=popup();field=p.get_by_label('기호나 이모지',exact=True)
 if kind=='image':selected=image(p)
 else:field.fill(glyph);selected=glyph
 ime(field,legacy)
 if mode=='baseline':expect(p).to_have_count(0);assert not pending()and checkpoint.read_bytes()==before;original();f.checked('published 4ef098e4 '+kind+' '+('legacy229'if legacy else'isComposing')+' Escape discards picker copy; source/checkpoint unchanged');return
 expect(p).to_be_visible();expect(field).to_be_focused();expect(panel().locator('.object-icon-edit')).to_have_attribute('aria-expanded','true')
 if kind=='image':assert p.locator('.object-icon-preview img').get_attribute('src')==selected;expect(field).to_have_value('')
 else:expect(field).to_have_value(glyph);expect(p.locator('.object-icon-preview')).to_have_text(glyph)
 expect(p.locator('[type=submit]')).to_be_enabled();assert not pending()and checkpoint.read_bytes()==before;original();f.page.keyboard.press('Escape');expect(p).to_have_count(0);expect(panel().locator('.object-icon-edit')).to_be_focused();expect(panel().locator('.object-icon-edit')).to_have_attribute('aria-expanded','false');assert not pending()and checkpoint.read_bytes()==before;original();f.checked(kind+' '+('legacy229'if legacy else'isComposing')+' preserves picker copy/focus; ordinary Escape still cancels without Apply/source writes')
def restart(i):f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});open_card()
def review():
 panel().locator('[data-declaration-header-action=confirm]').click();p=f.page.locator('.window[data-key=review]');expect(p).to_be_visible(timeout=120000)
 if p.locator('[data-review-advanced]').count():
  p.locator('[data-review-advanced]').click()
  if p.locator('[data-advanced-reviewed]').count():p.locator('[data-advanced-reviewed]').check()
 expect(p.locator('#confirm')).to_be_enabled(timeout=120000);return p
def save_confirm(wanted,cycle):
 global phase,before
 original();assert checkpoint.read_bytes()==before;panel().locator('[data-declaration-header-action=save]').click();f.idle();assert not pending();original();restart(cycle);expect(icon().locator('img')if wanted.startswith('data:')else icon()).to_be_visible()
 state=f.invoke('inspectDeclaration',dict(id=owner));d=f.state()['declaration'];assert d['values']['editorIcon']==wanted and d['values']['Exact']==9223372036854775805 and d['parent']==f.n+leaf+'Base'
 p=review();p.locator('[data-reject]').click();expect(p).to_be_hidden();original();p=review();p.locator('#confirm').click();expect(p).to_be_hidden(timeout=120000);f.idle();assert {p.name for p,v in snapshot.items()if p.read_bytes()!=v}=={file.name};assert '// IME 원본 주석 😀\r\n'.encode()in file.read_bytes();phase={p:p.read_bytes()for p in snapshot};before=checkpoint.read_bytes();restart(cycle+1);assert not pending();f.checked('explicit '+('generated image'if wanted.startswith('data:')else'glyph')+' Apply/Save/cold/Review cancel/Confirm preserve Exact64,parent and all other original source bytes')
try:
 f.start(0);f.invoke('select',dict(id=owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2100,'height':1500});open_card()
  try:
   for kind in ['glyph','image']:
    for legacy in [False,True]:exercise(kind,legacy)
   if mode!='baseline':
    for _ in range(2):p=popup();p.get_by_label('기호나 이모지',exact=True).fill(glyph);ime(p.get_by_label('기호나 이모지',exact=True),False);p.locator('[data-cancel]').click();expect(p).to_have_count(0);assert not pending()and checkpoint.read_bytes()==before;original()
    f.checked('repeated explicit close after composition cancels only local picker and releases listeners')
    if mode=='normal':
     p=popup();p.get_by_label('기호나 이모지',exact=True).fill(glyph);ime(p.get_by_label('기호나 이모지',exact=True),False);p.get_by_role('button',name='적용',exact=True).click();expect(icon()).to_have_text(glyph);assert next(v['text']for _,v in pending()if v['kind']=='icon')==glyph;panel().locator('.object-icon-edit').press('Control+z');expect(icon()).to_have_text('📦');assert not pending();panel().locator('.object-icon-edit').press('Control+y');expect(icon()).to_have_text(glyph);save_confirm(glyph,1)
     p=popup();wanted=image(p);ime(p.get_by_label('기호나 이모지',exact=True),True);expect(p).to_be_visible();assert p.locator('.object-icon-preview img').get_attribute('src')==wanted;p.get_by_role('button',name='적용',exact=True).click();save_confirm(wanted,3)
    else:
     restart(1);assert not pending()and checkpoint.read_bytes()==before;original();p=popup();wanted=image(p);ime(p.get_by_label('기호나 이모지',exact=True),False);p.locator('[data-cancel]').click();expect(icon()).to_have_text('📦');assert not pending()and checkpoint.read_bytes()==before;original();f.checked('cold current-owner picker and generated image explicit close preserve original/cancel semantics')
    assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/('glyph-ime-'+mode+'.png')),timeout=5000)
  except Exception as error:
   (f.case/'failure-exception.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));print(traceback.format_exc(),flush=True)
   try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000)
   except Exception:pass
   raise
  f.browser.close()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('GLYPH_IME_UI',f.case,flush=True)
