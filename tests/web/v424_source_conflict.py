"""Owned three-way comparison against real files, explicit resolution and compiler publication."""
import json,uuid,hashlib,os
from playwright.sync_api import expect

def verify_source_conflict(page,project,mount,send,envelope,settle,restart):
 id='Example.ButtonGame::Score';path=project/'Score.celem';original=path.read_text();files={p:p.read_bytes() for p in project.glob('*') if p.is_file()};description='Game-owned score; buttons contain no editor/model semantics.'
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request='conflict-'+uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];out,_=settle(v,request);assert out['ok']==ok,out;assert send(envelope(v,'dispose'))['ok'];return out.get('result')
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=60000)
 def window():return page.locator('.window[data-key="conflict"]')
 def nav_item(name):
  if not page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click()

 def open_compare():
  nav_item('소스 충돌 비교');ready();expect(window().locator('[data-conflict-id]')).to_have_text(id)
 def open_raw():
  nav_item('개념');ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();expect(page.locator('#source')).to_be_visible()
 current=state()['draft'];invoke('editMetadata',{'id':id,'field':'initial','valueJson':'10','revision':current['revision'],'hash':hashlib.sha256(current['text'].encode()).hexdigest()});local=state()['draft']['text'];invoke('reviewGroup',{'ids':[id],'target':'linux'});token=state()['review']['token']
 stamp=path.stat().st_mtime_ns;remoteA=original.replace(description,'External A');path.write_text(remoteA);os.utime(path,ns=(stamp,stamp));preview=invoke('inspectSourceConflict',{'id':id});assert preview['baseText']==original and preview['fileText']==remoteA and preview['draftText']==local and preview['status']=='conflict';assert state()['review']['token']==token and state()['draft']['text']==local;assert all(k not in state()['sourceConflict'] for k in ['baseText','draftText','fileText'])
 open_compare();window().locator('[data-close]').click();nav_item('변경 검토');ready()
 review=page.locator('.window[data-key="review"]');expect(review.locator('[data-review-conflict-notice]')).to_be_visible();expect(review.locator('#confirm')).to_be_disabled();token=state()['review']['token'];review.locator('[data-review-conflict="'+id+'"]').click();ready()
 for button in window().locator('[data-conflict-apply],[data-conflict-save],[data-conflict-review]').all():
  box=button.bounding_box();dock=page.locator('#dock').bounding_box();assert box and (box['x']+box['width']<=dock['x'] or box['y']+box['height']<=dock['y']), (box,dock)
 expect(window().locator('[data-conflict-version="baseText"]')).to_have_value(original);expect(window().locator('[data-conflict-version="fileText"]')).to_have_value(remoteA);expect(window().locator('[data-conflict-version="draftText"]')).to_have_value(local)
 mergedA=local.replace(description,'External A');window().locator('[data-conflict-candidate]').fill(mergedA);remoteB=original.replace(description,'External B');path.write_text(remoteB);os.utime(path,ns=(stamp,stamp));window().locator('[data-conflict-apply]').click();ready();expect(window().locator('[data-conflict-notice]')).to_contain_text('입력은 유지');expect(window().locator('[data-conflict-candidate]')).to_have_value(mergedA);assert state()['draft']['text']==local and path.read_text()==remoteB and state()['review']['token']==token
 window().locator('[data-conflict-read]').click();ready();expect(window().locator('[data-conflict-candidate]')).to_have_value(mergedA);expect(window().locator('[data-conflict-apply]')).to_be_disabled();window().locator('[data-conflict-bind]').click();merged=local.replace(description,'External B');window().locator('[data-conflict-candidate]').fill(merged);window().locator('[data-conflict-apply]').click();ready();assert state()['draft']['text']==merged and state()['review'] is None and path.read_text()==remoteB
 # A read and an exact no-op resolution preserve a valid current Review.
 invoke('reviewGroup',{'ids':[id],'target':'linux'});token=state()['review']['token'];preview=invoke('inspectSourceConflict',{'id':id});result=invoke('resolveSourceConflict',{'id':id,'text':merged,'revision':preview['revision'],'draftHash':preview['draftHash'],'fileHash':preview['fileHash']});assert result['accepted'] and not result['changed'] and state()['review']['token']==token
 window().locator('[data-conflict-save]').click();ready();unapplied=merged.replace('initial = 10','initial = 11');assert unapplied!=merged;window().locator('[data-conflict-candidate]').fill(unapplied);nav_item('변경 검토');ready();expect(page.locator('#status')).to_contain_text('미적용 합치기');assert state()['review']['token']==token
 if page.locator('.nav-menu').count():page.locator('#nav').click()
 page.evaluate('()=>globalThis.confectoryFlushPresentation()');presentation=state()['presentation'];layout=next(row for row in presentation['layout'] if row['key']=='conflict');assert set(layout.get('meta',{}))=={'conflictSourceId'} and 'baseText' not in json.dumps(presentation)
 restart();ready();expect(window().locator('[data-conflict-candidate]')).to_have_value(unapplied,timeout=30000);expect(window().locator('[data-conflict-version]')).to_have_count(0);expect(window().locator('[data-conflict-apply]')).to_be_disabled();window().locator('[data-conflict-read]').click();ready();expect(window().locator('[data-conflict-candidate]')).to_have_value(unapplied);expect(window().locator('[data-conflict-apply]')).to_be_disabled();window().locator('[data-conflict-bind]').click();window().locator('[data-conflict-apply]').click();ready();assert state()['draft']['text']==unapplied and path.read_text()==remoteB;window().locator('[data-conflict-save]').click();ready();page.screenshot(path='/tmp/confectory-v424-source-conflict.png',full_page=True)
 window().locator('[data-conflict-review]').click();ready();review=page.locator('.window[data-key="review"]');review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
 if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled();review.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000);ready();assert path.read_text()==unapplied
 # A newer unapplied raw source input survives applying an older merge candidate.
 open_raw();raw12=unapplied.replace('initial = 11','initial = 12');raw13=unapplied.replace('initial = 11','initial = 13');page.locator('#source').fill(raw12);page.locator('#source-conflict').click();ready();expect(window().locator('[data-conflict-candidate]')).to_have_value(raw12);expect(window().locator('[data-conflict-apply]')).to_be_disabled();window().locator('[data-conflict-bind]').click();open_raw();page.locator('#source').fill(raw13);page.locator('#source-conflict').click();ready();expect(window().locator('[data-conflict-candidate]')).to_have_value(raw12);window().locator('[data-conflict-apply]').click();ready();expect(page.locator('#source')).to_have_value(raw13);expect(window().locator('[data-conflict-candidate]')).to_have_value(raw13);expect(window().locator('[data-conflict-apply]')).to_be_disabled();assert state()['draft']['text']==raw12 and path.read_text()==unapplied
 for p,content in files.items():
  if p!=path:assert p.read_bytes()==content,p.name
 print('PASS actual source conflict: real baseline/file/draft, stale file all-or-refuse, explicit input binding, no-op Review preservation, Save/cold input, compiler Confirm, and newer raw input preserved',flush=True)
