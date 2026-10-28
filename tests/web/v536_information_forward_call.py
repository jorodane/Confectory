"""Existing forwarded call cells: rename root only, keep the real callee ABI."""
import copy,json
import v536_information_whole_contract_fixture as b
f,n,owner,fn=b.f,b.n,b.owner,b.fn
leaf=f.n+'ForwardLeaf';helper='function '+leaf+' (long x,out long sum) -> long {provide '+leaf+' with '+leaf+'Body;}'
(f.project/'ForwardLeaf.celem').write_text(helper);(f.project/'ForwardLeafBody.celem').write_text('implementation '+leaf+'Body for '+leaf+' (long x,out long sum) -> long {body common "ForwardLeaf.csbody";}');(f.project/'ForwardLeaf.csbody').write_text('sum=checked(x+1);return sum; // 保持すべき fixture')
f.manifest.write_text(f.manifest.read_text().replace('{','{element ForwardLeaf function "ForwardLeaf.celem";element ForwardLeafBody implementation "ForwardLeafBody.celem";',1))
impl=b.base.implementation_file;cpp='implementation '+fn+'Body for '+fn+' (long nativeAmount,out long nativeTotal) -> long {blueprint common "function.graph.json";}'
sig={'args':[{'name':'x','type':'long'},{'name':'sum','type':'long','mode':'out'}],'return':'long'}
g=json.loads((f.project/'function.graph.json').read_text());g.update(profile='sync-acyclic-ref-v1',nodes=[],entry='',edges=[],exits={'count':None,'return':None})
prepared=f.metadata('blueprintPrepareCall',id=fn+'Body',text=cpp,targetText=helper,graph=g,definition={'id':'body','feature':leaf,'intent':'기존 외부 호출 저장소','control':'next'});impl.write_text(prepared['implementation']);g=prepared['graph'];g['nodes'][0]['forwardCallerStorage']=True;g['nodes'][0]['arguments']={'x':{'input':'amount'}};g['entry']='body';g['edges']=[{'from':'body','port':'next','to':'exit:return'}];g['exits']['return']={'node':'body'};(f.project/'function.graph.json').write_text(json.dumps(g))
new=copy.deepcopy(b.old);new['args'][0]['name']='renamed';new['args'][1]['name']='result';remap={'amount':'renamed','count':'result'};snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
r=n.request(new,remap);candidate=n.prepare(r);rows={v['id']:v['text'] for v in candidate['linkedUpdates']};graph=json.loads(rows[fn+'Body/body:common']);assert graph['nodes'][0]['signature']==sig and graph['nodes'][0]['feature']==leaf and graph['nodes'][0]['arguments']=={'x':{'input':'renamed'}};assert graph['edges']==g['edges'];assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())
bad=copy.deepcopy(r);bad['changes'][0]['signature']['args'][0]['type']='string';n.prepare(bad,False)
print('PASS forwarded call은 callee/source·실제 셀을 보존한 root 이름 대응만 허용하며 외부 타입·역할 추측을 거절한다',flush=True)
passed=1
ui='ui' in __import__('sys').argv[4:]
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});f.invoke('schema',{'id':owner});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 if ui:
  from playwright.sync_api import sync_playwright,expect
  import time
  with sync_playwright() as pw:
   expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});b.d.open_info()
   f.owner().locator('[data-inline-method="'+fn+'"] > .function-node-heading').dblclick(position={'x':190,'y':3});p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();p.locator('[data-signature-id=arg0] [data-signature-name]').fill('renamed');p.locator('[data-signature-id=arg1] [data-signature-name]').fill('result');p.get_by_role('button',name='저장',exact=True).click();f.idle()
   expected=b.d.pending();assert expected
   f.owner().locator('[data-own-functions-toggle]').press('Control+z');f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert b.d.pending()==expected
   f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+90
   while b.d.pending() and time.monotonic()<deadline:f.page.wait_for_timeout(20)
   assert not b.d.pending();review=b.d.review()
   if review.locator('[data-review-advanced]').count():
    review.locator('[data-review-advanced]').click()
    if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
   expect(review.locator('#confirm')).to_be_enabled();review.locator('#confirm').click();expect(review).to_have_count(0);f.idle();f.page.screenshot(path=str(f.case/'forward-call-ui.png'));assert not f.errors and not f.external;f.browser.close()
 else:
  s=f.state()['schema'];method=next(v for v in s['ownFunctions'] if v['id']==fn);p=f.invoke('blueprint',{'action':'readOwnerEdits','id':owner,'hash':s['textHash'],'includeFunctionInputs':fn})['result']['result']
  f.invoke('blueprint',{'action':'applySlots','id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':new,'mapping':{'before':b.old,'args':remap}}]}})
  changes={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};ids=changes[owner]['atomicEditGroup'];f.stop();f.start(1);f.invoke('select',{'id':owner});f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',{'ids':ids,'token':review['token']})
 assert json.loads((f.project/'function.graph.json').read_text())['nodes'][0]['arguments']=={'x':{'input':'renamed'}};assert (f.project/'ForwardLeaf.celem').read_text()==helper
 passed=2
 print('PASS 실제 화면/엔진의 명시 저장·Undo·compiler Review/Confirm은 callee·원문·forwarded 저장소를 보존한다' if ui else 'PASS 실제 저장·cold·compiler Review/Confirm 후에도 외부 callee·원문·forwarded 저장소 대응을 유지한다',flush=True)
finally:
 f.stop();print(json.dumps({'checks':passed,'evidence':str(f.case),'actualEngine':True,'actualRenderer':ui,'executed':False},ensure_ascii=False))
