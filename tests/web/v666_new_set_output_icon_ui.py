"""Original Set owned output picker, actual engine candidate/receipt/Confirm; synthetic assets only."""
import copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3] if len(sys.argv)>3 else 'normal';private=False;feature_label='IconPrivate' if private else 'Slot';feature_id=f.n+feature_label;graph_id=f.n+'SlotBody/body:common'
graph_file=f.project/'Slot.graph.json';record_file=f.project/'Slot.node.json'
if private:
 implementation=feature_id+'Body';text='function '+feature_id+' (long amount) -> long {}';prepared=f.metadata('blueprintPrepareFeature',id=feature_id,text=text,implementation=implementation,graphPath='IconPrivate.graph.json',nodePath='IconPrivate.node.json');signature={'args':[{'name':'amount','type':'long'}],'return':'long'}
 child={'schema':1,'profile':'sync-acyclic-methods-v1','entry':'body','nodes':[{'id':'body','kind':'code','control':'next','intent':'직접 소유한 내부 본문','signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'implementation':'IconPrivate.node.json'}],'edges':[{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'node':'body'}},'locals':[]}
 graph=prepared['graph'];graph.update(profile='sync-acyclic-nested-v1',entry='frame',nodes=[{'id':'frame','kind':'graph','control':'next','intent':'직접 소유한 내부 frame','signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'graph':child}],edges=[{'from':'frame','port':'next','to':'exit:return'}],exits={'return':{'node':'frame'}})
 context={'implementation':implementation,'feature':feature_id,'signature':signature,'imports':{}};definitions=f.metadata('featureBlueprintNodes',featureSource=text,implementationContext=context,bodyTarget='common',graph=graph);definition=next(n for n in definitions['nestedNodes'] if n['id']=='frame/body');record={'schema':1,'node':'body','definitionHash':definition['definitionHash'],'source':'return amount+1; // 그대로 보존할 직접 소유 본문 😀\r\n'}
 graph_file=f.project/'IconPrivate.graph.json';record_file=f.project/'IconPrivate.node.json';graph_file.write_text(json.dumps(graph));record_file.write_text(json.dumps(record));(f.project/'IconPrivate.celem').write_text(text.replace('{}','{provide '+feature_id+' with '+implementation+';}'));(f.project/'IconPrivateBody.celem').write_text(prepared['implementation']);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element IconPrivate function "IconPrivate.celem";element IconPrivateBody implementation "IconPrivateBody.celem";registry Confectory.Build.DotNet'));graph_id=implementation+'/body:common/graph:frame'
graph=json.loads(graph_file.read_text());graph.setdefault('locals',[]).extend([{'id':'ownStored','name':'저장한 값','type':'long','initial':{'constant':0}},{'id':'counter','name':'기존 변수','type':'long','initial':{'constant':0}},{'id':'sharedOut','name':'공유 출력','type':'long','initial':{'constant':0}}])
for id,local,output in [('store','ownStored','ownStored'),('shared','counter','sharedOut')]:graph['nodes'].append({'id':id,'kind':'set','control':'next','intent':'중간저장','local':local,'outputLocal':output,'signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'input':'amount'}}})
graph['edges'] += [{'from':'shared','port':'next','to':'store'},{'from':'store','port':'next','to':graph['entry']}];graph['entry']='shared';next(n for n in graph['nodes'] if n['id']=='body')['arguments']['amount']={'node':'store','output':'stored'}
defs=f.metadata('featureBlueprintNodes',featureSource=f.fn,graph=graph,featureContracts={f.n+'Native':f.native,f.n+'Donor':f.items['Donor'][1]});record=json.loads(record_file.read_text());record['definitionHash']=next(n for n in defs['nodes'] if n['id']=='body')['definitionHash'];record_file.write_text(json.dumps(record));graph_file.write_text(json.dumps(graph))
snapshot={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file()};checks=[]
def original():assert all(p.read_bytes()==v for p,v in snapshot.items())
def call(action,**kw):return f.invoke('blueprint',dict(action=action,id=graph_id,**kw))['result']['result']
def data():return call('read')
def node(d):return next(n for n in d['nodes'] if n['id']=='store')
def pending():return [(k,v) for k,v in f.pending()['blueprint'] if v.get('type')=='icon']
def button():return f.author().locator('[data-bp-node=store] [data-signature-icon]')
def open_graph():
 f.idle()
 if f.author().locator('[data-bp-node=store]').is_visible():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature_label);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature_id+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 if private and not button().is_visible():
  f.author().locator('[data-bp-overview-node=frame]').click();f.author().locator('[data-bp-node=frame] [data-function-write-direct]').click()
 expect(button()).to_be_visible()
def popup():
 f.author().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.get_by_role('button',name='전체 보기',exact=True).click();zoom.locator('[data-zoom-value]').press('Escape');f.page.screenshot(path=str(f.case/'set-output-before-popup.png'));button().click();p=f.page.get_by_role('dialog',name='저장한 값 아이콘 편집',exact=True);expect(p).to_be_visible();return p
def position():return f.author().locator('[data-bp-node=store]').evaluate('e=>({x:e.offsetLeft,y:e.offsetTop})')
def pick(value):
 p=popup();p.locator('[data-icon-choice="'+value+'"]').click();p.get_by_role('button',name='적용',exact=True).click();expect(button()).to_have_text(value)
def save():
 f.author().locator('[data-bp-save]').click();f.idle();
 if f.author().locator('.bp-status').inner_text()=='consumer_error':raise AssertionError({'status':'consumer_error','results':[r['result'] for r in f.traffic if 'result' in r]})
 expect(f.author().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle();assert not pending()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();f.idle()
def review():
 def complete():
  if not f.author().locator('[data-bp-complete]').is_visible():f.page.locator('[data-window-tab=blueprint]').click()
  expect(f.author().locator('[data-bp-complete]')).to_be_visible();f.author().locator('[data-bp-complete]').click()
 complete();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=60000)
 target=f.page.locator('.window[data-key=targets]')
 if target.is_visible():target.locator('[data-target-choice]').select_option('portable');target.locator('[data-close]').click();complete()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible();return r

try:
 f.start(0);f.invoke('select',{'id':feature_id});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();baseline=data()
  f.page.set_viewport_size({'width':390,'height':844});f.author().locator('[data-flow-insert][data-from=store][data-port=next]').click();f.page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True).get_by_role('button',name='중간저장 만들기',exact=True).click();overlay=f.page.locator('.bp-flow-overlay-host:visible');expect(overlay.locator('[data-flow-set-target]')).to_be_visible()
  created=next(v['node'] for _,v in f.pending()['blueprint'] if v['type']=='set-plan');overlay.locator('[data-signature-type]').click();f.page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click();overlay.locator('[data-signature-name]').fill('새 저장 출력');overlay.locator('[data-signature-name]').press('Tab');overlay.locator('[data-flow-value]').click();menu=f.page.get_by_role('dialog',name='핀 값 선택',exact=True);menu.get_by_role('searchbox',name='값 검색').fill('17');menu.get_by_role('searchbox',name='값 검색').press('Enter');expect(menu).not_to_be_visible()
  overlay.locator('[data-flow-done]').click()
  if f.author().locator('[data-flow-graph]').is_visible():f.author().locator('[data-flow-graph]').click()
  f.page.set_viewport_size({'width':1800,'height':1400});before=next(v['text'] for _,v in f.pending()['blueprint'] if v['type']=='set-plan');f.author().locator('[data-bp-node="'+created+'"] [data-signature-icon]').click();p=f.page.get_by_role('dialog',name='새 저장 출력 아이콘 편집',exact=True);expect(p).to_be_visible();p.locator('[data-icon-choice="★"]').click();p.get_by_role('button',name='적용',exact=True).click();assert next(v['text'] for _,v in f.pending()['blueprint'] if v['type']=='set-plan')==before;assert pending()[0][1]['text']=='★';original();assert all(n['id']!=created for n in data()['nodes']);f.checked('원본 새 Set 삽입·타입/이름/값 선택 뒤 아이콘만 추가하며 선택한 저장소 ID·타입·실행 삽입과 다른 입력은 유지한다')
  if mode=='guard':
   checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before_checkpoint=checkpoint.read_bytes();held=f.pending()['blueprint']
   def forged(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':body['input']['edits'][0]['definition']['icons'][0]['id']='shared';route.continue_(post_data=json.dumps(body))
    else:route.continue_()
   f.page.route('**/api/request',forged);f.author().locator('[data-bp-save]').click();f.idle()
   # Persisted private input deliberately omits ephemeral engine basis grants;
   # failed saves also retain one exact attempt journal for safe reconciliation.
   content=lambda rows:[[k,{name:value for name,value in v.items() if name!='basis'}] for k,v in rows]
   retained=f.pending()['blueprint'];attempts=[v for _,v in retained if v.get('kind')=='author-attempt']
   assert content([(k,v) for k,v in retained if v.get('kind')!='author-attempt'])==content(held)
   assert len(attempts)==1 and content(attempts[0]['cells'])==content(held)
   assert attempts[0]['edits'][0]['definition']['icons']==[{'id':created,'text':'★'}]
   assert checkpoint.read_bytes()==before_checkpoint;original();f.page.unroute('**/api/request',forged);f.checked('새 Set 계획의 표시 대상을 공유 저장소로 변조해도 전체 미적용하고 모든 생성·연결·이미지 입력과 원래 재시도 기록을 보존한다')
  save();assert not f.pending()['blueprint'];final=data();node=next(n for n in final['nodes'] if n['id']==created);assert node['kind']=='set' and node['icon']=='★' and node['local']==node['outputLocal'];assert node['signature']['args'][0]['type']=='long';assert json.loads(node['arguments'][0]['valueJson'])=={'constant':17};original();restart(2);assert next(n for n in data()['nodes'] if n['id']==created)['icon']=='★';f.checked('기존 setPlan과 표시 아이콘은 한 원자 후보·최종 CAS로 저장·cold 복구되며 원본은 Confirm 전 유지된다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check();expect(r.locator('#confirm')).to_be_enabled(timeout=120000);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert {str(p.relative_to(f.project)) for p,v in snapshot.items() if p.read_bytes()!=v}=={graph_file.name};assert record_file.read_bytes()==snapshot[record_file];assert not f.errors and not f.external;f.checked('Review 취소·명시 compiler Confirm은 새 Set와 그 표시만 반영하며 함수·C#·참조와 원본 본문 stamp를 보존한다');f.page.screenshot(path=str(f.case/'new-set-output-icon.png'));f.browser.close()
except Exception:
 try:(f.case/'new-set-failure.json').write_text(json.dumps(dict(state=f.state(),results=[r['result'] for r in f.traffic if 'result' in r],traffic=f.traffic[-100:],errors=f.errors),ensure_ascii=False,indent=2)+'\n')
 except Exception:pass
 try:f.page.screenshot(path=str(f.case/'new-set-output-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 f.stop();(f.case/'new-set-output-evidence.json').write_text(json.dumps(dict(checks=f.checks,errors=f.errors,actualWindows=False,actualMobile=False),ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
