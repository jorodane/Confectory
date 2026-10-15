"""Read a registered definition through the ordinary Home consumer and cold restart."""
import hashlib,json,uuid,os
from playwright.sync_api import expect

def verify_reference_definition(page,project,mount,send,envelope,settle,restart):
 prefix='Example.ButtonGame::';main=prefix+'Main';score=prefix+'Score';target='ReferenceApi::Work';originals={p:p.read_bytes() for p in project.glob('*') if p.is_file()};external=project.parent/'reference-api'/'Work.celem';original_external=external.read_bytes()
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request='definition-'+uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];result,_=settle(v,request);assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=30000)
 def check_frame():
  frame=definition.bounding_box();heading=definition.locator('[data-reference-id]').bounding_box();footer=definition.locator('[data-reference-source]').bounding_box();workspace=page.locator('#workspace').bounding_box();assert heading['y']>=frame['y']+30 and footer['y']+footer['height']<=frame['y']+frame['height']-5 and frame['y']+frame['height']<=workspace['y']+workspace['height'],(frame,heading,footer,workspace)
 current=state();draft=current['draft'];invoke('editMetadata',{'id':score,'field':'initial','valueJson':'2','revision':draft['revision'],'hash':hashlib.sha256(draft['text'].encode()).hexdigest()});invoke('reviewGroup',{'ids':[score],'target':'linux'});token=state()['review']['token']
 page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념 맵',exact=True).click();ready();w=page.locator('.window[data-key="map"]');expect(w.locator('[data-map-scene]')).to_be_visible();w.locator('[data-map-query]').fill(target);w.locator('[data-map-fit]').click();w.locator('[data-relation-node="'+target+'"]').click();w.locator('[data-map-open-source]').click();ready()
 definition=page.locator('.window[data-key="definition"]');expect(definition.locator('[data-reference-id]')).to_have_text(target);text=definition.locator('[data-reference-text]');expect(text).to_have_value(original_external.decode());assert text.evaluate('e=>e.readOnly') is True;assert definition.locator('[data-reference-hash]').inner_text()==hashlib.sha256(original_external).hexdigest();assert definition.locator('button').filter(has_text='Save').count()==0
 current=state();assert current['draft']['id']==score and current['review']['token']==token;assert current['referenceDefinition']['origin']=='confirmed-registered-file';assert str(project.parent) not in json.dumps(current['referenceDefinition'])
 source=next(n for n in current['relationsMap']['nodes'] if n['id']==main);request={'sourceId':main,'id':target,'revision':source['revision'],'hash':source['textHash']}
 invoke('readReferenceDefinition',dict(request,hash='0'*64),False);assert state()['review']['token']==token and state()['draft']['id']==score
 invoke('readReferenceDefinition',dict(request,id='ReferenceApi::NotAReference'));assert state()['referenceDefinition']['code']=='NOT_DECLARED_REFERENCE' and state()['review']['token']==token
 invoke('readReferenceDefinition',dict(request,id='ReferenceApi::Body'));assert 'missing-never-read.csbody' in state()['referenceDefinition']['text'] and not external.with_name('missing-never-read.csbody').exists();assert state()['review']['token']==token
 # Re-reading the selected declaration detects changed bytes even with restored mtime.
 stamp=external.stat().st_mtime_ns;external.write_text(original_external.decode().replace('definition A','definition B'));os.utime(external,ns=(stamp,stamp));definition.locator('[data-reference-reload]').click();ready()
 expect(definition.locator('[data-reference-text]')).to_have_value(external.read_text());assert state()['referenceDefinition']['textHash']!=hashlib.sha256(original_external).hexdigest();assert state()['review']['token']==token
 external.write_bytes(original_external);definition.locator('[data-reference-reload]').click();ready();expect(definition.locator('[data-reference-text]')).to_have_value(original_external.decode());check_frame()
 page.screenshot(path='/tmp/confectory-v424-reference-definition.png',full_page=True)
 page.evaluate('()=>globalThis.confectoryFlushPresentation()');presentation=state()['presentation'];assert 'Registered definition A' not in json.dumps(presentation),'reference text must not be persisted as presentation'
 restart();ready();definition=page.locator('.window[data-key="definition"]');expect(definition.locator('[data-reference-id]')).to_have_text(target,timeout=30000);expect(definition.locator('[data-reference-text]')).to_have_count(0);expect(definition.locator('[data-reference-state]')).to_contain_text('다시 읽어야');definition.locator('[data-reference-reload]').click();ready();expect(definition.locator('[data-reference-text]')).to_have_value(original_external.decode());assert state()['draft']['id']==score
 definition.locator('[data-reference-source]').click();ready();declaration=page.locator('.window[data-key="declaration"]');expect(declaration.locator('[data-declaration-id]')).to_have_text(main);declaration.locator('[data-declaration-references] summary').click();declaration.locator('[data-reference-target="'+target+'"]').click();ready();expect(definition.locator('[data-reference-text]')).to_have_value(original_external.decode());assert state()['draft']['id']==main
 for p,original in originals.items():assert p.read_bytes()==original,p.name
 assert external.read_bytes()==original_external
 print('PASS actual registered reference definition: map to read-only source, exact identity/hash, selected registry only, stale refusal, review preservation, changed external bytes and cold restart; original owned files unchanged',flush=True)
