"""Existing public IO controls and an explicitly authored execution-only caller."""
import hashlib,json,shutil
from playwright.sync_api import expect

def build(x,name):
 f=x.f;data=x.read();args=data['signature']['args'];input=next(a for a in args if a.get('mode')!='out');output=next(a for a in args if a.get('mode')=='out');value=3 if input['type']=='int'else'payload'
 destination=f.case/name;shutil.copytree(f.project,destination,ignore=shutil.ignore_patterns('.confectory'))
 metadata=json.dumps(json.dumps(dict(schema=1,completion='main_complete'),separators=(',',':')));main=f.n+'Main';implementation=f.n+'MainBody';main_source='function '+main+' () -> int {value blueprintAsync = '+metadata+';}'
 prepared=f.metadata('blueprintPrepareFeature',id=main,text=main_source,implementation=implementation,graphPath='Main.graph.json',nodePath='Main.node.json');caller=prepared['graph']
 call=dict(id='call',kind='call',control='next',intent='명시적으로 기다리는 테스트 호출자',feature=x.feature,signature=data['signature'],arguments={input['name']:dict(constant=value)})
 body=dict(id='body',kind='code',control='next',intent='입출력 실제 전달 확인',signature=dict(args=[dict(name='result',type='int'),dict(name='reply',type=output['type'])],**{'return':'int'}),arguments=dict(result=dict(node='call'),reply=dict(node='call',output=output['name'])),implementation='Main.node.json')
 caller.update(entry='call',nodes=[call,body],edges=[dict(**{'from':'call'},port='next',to='body'),dict(**{'from':'body'},port='next',to='exit:return')],exits=dict(**{'return':dict(node='body')}))
 definitions=f.metadata('featureBlueprintNodes',featureSource=prepared['function'],graph=caller,featureContracts={x.feature:x.paths[x.feature].read_text()});assert definitions['state']=='node-definitions',definitions
 record=dict(schema=1,node='body',definitionHash=next(n for n in definitions['nodes']if n['id']=='body')['definitionHash'],source='global::System.Console.WriteLine("reply:"+reply);return result;')
 alias='fg_call_'+hashlib.sha256(x.feature.encode()).hexdigest()[:24];signature='('+input['type']+',out '+output['type']+') -> int'
 for filename,text in [('Main.celem',prepared['function']),('MainBody.celem',prepared['implementation'].replace('{','{ import '+x.feature+' as '+alias+' '+signature+';',1)),('Main.graph.json',json.dumps(caller)),('Main.node.json',json.dumps(record,ensure_ascii=False))]:(destination/filename).write_text(text)
 x.run(destination,name,11,'fresh\nreply:'+str(value))

def bind(x):x.build_new=lambda name:build(x,name)

def pan(x,panel):
 box=panel().locator('.bp-viewport').bounding_box();left=box['x']+box['width']*.9;top=box['y']+box['height']*.55;x.f.page.mouse.move(left,top);x.f.page.mouse.down(button='middle');x.f.page.mouse.move(left,top+100,steps=10);x.f.page.mouse.up(button='middle')

def stage(x,panel):
 f=x.f
 f.page.on('pageerror',lambda error:(f.case/'root-io-error-stack.txt').write_text(str(error.stack)))
 try:
  panel().locator('[data-signature-add=inputs]').click();field=panel().locator('[data-signature-id=input1] [data-signature-name]');field.fill('seed');field.press('Enter');expect(panel().locator('[data-signature-id=seed]')).to_be_visible()
  box=panel().locator('.bp-viewport').bounding_box();panel().locator('.bp-viewport').click(button='right',position={'x':box['width']*.65,'y':box['height']*.65});menu=f.page.get_by_role('dialog',name='블루프린트 노드 검색');menu.locator('[data-resource-kind]').select_option('export');menu.locator('[data-resource-output-create]').click();output=panel().locator('[data-bp-node^=export_]');expect(output).to_have_count(1);node=output.get_attribute('data-bp-node');panel().locator('[data-bp-overview-node="'+node+'"]').click();field=output.locator('[data-bp-export-name]');field.fill('reply');field.press('Enter');output.get_by_role('button',name='값 목록 열기',exact=True).click();picker=f.page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(picker).to_be_visible(timeout=5000);search=picker.get_by_role('searchbox',name='값 검색',exact=True);search.fill('payload');search.press('Enter');literal_plan=json.loads(next(v['text']for _,v in f.pending()['blueprint']if v['type']=='root-parameters'));assert literal_plan['outputCreates'][0]['valueJson']=='{"constant":"payload"}';output.get_by_role('button',name='값 목록 열기',exact=True).click();f.page.get_by_role('dialog',name='핀 값 선택',exact=True).get_by_role('button',name='입력 · seed',exact=True).click()
  panel().locator('[data-bp-overview-node="$entry"]').click();panel().locator('.bp-port[data-node="$entry"][data-side=out]:not([data-kind])').click();panel().locator('[data-bp-overview-node="'+node+'"]').click();output.locator('.bp-exec-header-in').click();panel().locator('[data-bp-overview-node="'+node+'"]').click();output.locator('.bp-exec-line-out[data-port=next]').click();panel().locator('[data-bp-overview-node=body]').click();pan(x,panel);panel().locator('[data-bp-node=body] .bp-exec-header-in').click()
  cells=f.pending()['blueprint'];plan=json.loads(next(v['text']for _,v in cells if v['type']=='root-parameters'));assert plan['args']==[dict(name='seed',type='string'),dict(name='reply',type='string',mode='out')];assert plan['outputCreates'][0]['valueJson']=='{"input":"seed"}';assert plan['outputEntry']==node and plan['outputRoutes']==[dict(node=node,to='body')];panel().locator('.bp-viewport').press('Control+z');previous=json.loads(next(v['text']for _,v in f.pending()['blueprint']if v['type']=='root-parameters'));assert previous!=plan;x.original();panel().locator('.bp-viewport').press('Control+y');assert json.loads(next(v['text']for _,v in f.pending()['blueprint']if v['type']=='root-parameters'))==plan;x.original();f.checked('원본 입력 추가/이름·새 출력/값·실행 연결과 Undo/Redo는 첫 Save 전에 같은 공개 IO 입력을 보존한다')
 except Exception:
  f.page.screenshot(path=str(f.case/'root-io-stage-failure.png'));(f.case/'root-io-stage-failure.html').write_text(f.page.content());raise
