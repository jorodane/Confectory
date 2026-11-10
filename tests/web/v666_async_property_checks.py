"""Async property fixture and interrupted UI checks over the existing property flow.

Only generated owned data and registered ObjectModel dependencies are used.
The synchronous fixture remains the regression for the same authored UI.
"""
import copy,hashlib,json,time

def configure(c):
    for name in ['Main','Calc']:
        kind,text=c['items'][name]
        metadata='value blueprintAsync = '+json.dumps(json.dumps(dict(schema=1,completion='completion')))+';'
        c['items'][name]=(kind,text.replace('{','{'+metadata,1))
    prepared=c['metadata']('blueprintPrepareFeature',id=c['n']+'Calc',text=c['items']['Calc'][1].replace('provide '+c['n']+'Calc with '+c['n']+'CalcBody;',''),implementation=c['n']+'CalcBody',graphPath='Calc.graph.json',nodePath='combine.node.json')
    c['g']['profile']='async-acyclic-switch-v1';c['g']['contractHash']=prepared['graph']['contractHash']
    next(n for n in c['g']['nodes']if n['id']=='combine')['async']=True

def complete_sources(c):
    rejected=copy.deepcopy(c['g']);rejected['nodes'][0]['kind']='property-ref'
    result=c['metadata']('featureBlueprintNodes',featureSource=c['items']['Calc'][1],graph=rejected,propertyContracts={c['n']+'Monster':c['descriptor']},featureContracts=c['contracts'])
    assert result['state']=='invalid'and result['diagnostics'][0]['code']=='GRAPH_NODE_KIND',result
    c['record']['source']='await global::System.Threading.Tasks.Task.Delay(15);\n'+c['record']['source']
    c['sources']['combine.node.json']=json.dumps(c['record'])
    main=c['metadata']('blueprintPrepareFeature',id=c['n']+'Main',text=c['items']['Main'][1].replace('provide '+c['n']+'Main with '+c['n']+'MainBody;',''),implementation=c['n']+'MainBody',graphPath='Main.graph.json',nodePath='Main.node.json')
    node=main['graph']['nodes'][0];node['async']=True;node['imports']=[c['n']+'Calc',c['model']+'::Create']
    contracts={c['n']+'Calc':c['items']['Calc'][1],c['model']+'::Create':(c['repo']/'packs/object-model/Create.celem').read_text()}
    defs=c['metadata']('featureBlueprintNodes',featureSource=main['function'],graph=main['graph'],featureContracts=contracts)
    alias=lambda id:'fg_call_'+hashlib.sha256(id.encode()).hexdigest()[:24]
    source=c['sources'].pop('Main.csbody').replace('calls.Create',alias(c['model']+'::Create'))
    for number in ['20','30']:
        source=source.replace('Console.WriteLine(calls.Calc.Invoke(target,'+number+'));','Console.WriteLine((await '+alias(c['n']+'Calc')+'.InvokeAsync(target,'+number+')).Return);')
    assert 'calls.'not in source
    c['sources']['Main.celem']=main['function'];c['sources']['MainBody.celem']=c['items']['MainBody'][1].replace('body common "Main.csbody"','blueprint common "Main.graph.json"').replace(' as Calc ',' as '+alias(c['n']+'Calc')+' ').replace(' as Create ',' as '+alias(c['model']+'::Create')+' ')
    c['sources']['Main.graph.json']=json.dumps(main['graph']);c['sources']['Main.node.json']=json.dumps(dict(schema=1,node=node['id'],definitionHash=next(n['definitionHash']for n in defs['nodes']if n['id']==node['id']),source=source))

def begin(c):
    c['call']('select',{'id':c['n']+'Calc'});c['call']('saveDraft',{})
    data=c['current']();assert data['profile']=='async-acyclic-switch-v1'
    assert any(s.get('path')=='project.cproj'for s in data['sources']),data['sources']
    c['_checkpoint']=next(c['project'].glob('.confectory/edit-workspaces/*/draft.json'))
    plan=dict(reads=[dict(node='rejectedRead',owner=c['n']+'Monster',field='health',descriptor=c['descriptor'],targetJson='{"input":"replacement"}')],changes=[dict(action='route',node='write',port='next',to='rejectedRead'),dict(action='route',node='rejectedRead',port='next',to='second'),dict(action='argument',node='second',name='value',valueJson='{"node":"rejectedRead","output":"return"}')])
    request=dict(id=data['id'],attempt='1'*32,checkpointHash=data['checkpointHash'],sourceProof=json.dumps(sorted([[v['id'],v['revision'],v['hash']]for v in data['sources']]),separators=(',',':')),edits=[dict(action='propertyPlan',node='$properties',definition=plan)])
    before=c['_checkpoint'].read_bytes();c['call']('blueprint',dict(action='authorBatch',**request),False);assert c['_checkpoint'].read_bytes()==before;assert c['current']()['checkpointHash']==data['checkpointHash'];c['unchanged']()
    source_only=copy.deepcopy(request);source_only['attempt']='2'*32;source_only['edits']=[dict(action='source',node='combine',text=next(v for v in data['nodes']if v['id']=='combine')['source'])];c['call']('blueprint',dict(action='authorBatch',**source_only),False);assert c['_checkpoint'].read_bytes()==before
    c['checked']('async 속성 receiver 자료형 오류와 field-ref 문맥은 거절하고 원본/Task/입력을 보존한다')
    c['checked']('async 속성 읽기는 등록 프로젝트·객체·스키마 관측과 원래 Task 계약을 보존한다')

def refused(c,mark):
    for _ in range(3000):
        ids={r['requestId']for r in c['traffic'][mark:]};rows=[v for k,v in c['results'].items()if k in ids and (not v.get('ok')and v.get('error',{}).get('code')not in ['stale_revision','busy','stale_scope'] or v.get('result',{}).get('sourceConfirmed')is False)]
        if rows:return rows
        c['page'].wait_for_timeout(20)
    (c['case']/'rejection-details.json').write_text(json.dumps(dict(traffic=c['traffic'][mark:],results=c['results'],state=c['state']()),ensure_ascii=False,indent=2))
    raise AssertionError('expected atomic rejection response')

def restart(c,index):
    c['pending']();c['page'].close();c['stop']();c['start'](index);c['page']=c['setup'](c['browser']);c['page'].set_viewport_size({'width':1480,'height':1050});c['idle']()
    c['expect'](c['author']().locator('[data-bp-save]')).to_be_enabled()

def save(c,held):
    mode=c['async_mode'];page=c['page'];panel=c['author'];checkpoint=c['_checkpoint'];before=checkpoint.read_bytes()
    if mode in ['storage','conflict']:
        path=checkpoint if mode=='storage'else c['project']/'project.cproj';original=path.read_bytes()
        if mode=='storage':path.chmod(0o400)
        else:path.write_bytes(original+b'\n')
        mark=len(c['traffic'])
        try:
            panel().locator('[data-bp-save]').click();failure=refused(c,mark);(c['case']/(mode+'-save-refusal.json')).write_text(json.dumps(failure,ensure_ascii=False,indent=2));c['idle']();assert all(dict(c['pending']()).get(k)==v for k,v in held);assert checkpoint.read_bytes()==before
        finally:
            if mode=='storage':path.chmod(0o600)
            else:path.write_bytes(original)
        c['unchanged']();c['checked']('저장 실패/원본 경합은 읽기·Set·receiver·입력을 한 후보로 거절하고 재시도한다')
    mark=len(c['traffic'])
    if mode not in ['loss','late']:
        panel().locator('[data-bp-save]').click();return c['saved'](mark)
    requests=set();queries=set();paused={};lost=[]
    def interrupt(route):
        data=route.request.post_data_json
        if data.get('op')=='invoke'and data.get('endpoint')=='blueprint':
            action=data.get('input',{}).get('action')
            if action=='authorBatch':requests.add(data['requestId'])
            elif requests and action=='settledAuthorBatch':queries.add(data['requestId'])
        response=route.fetch();payload=response.json()
        if '_interrupt_observations'in c:
            c['_interrupt_observations'].extend(copy.deepcopy(r)for r in payload.get('results',[])if r.get('requestId')in requests|queries)
            (c['case']/'interruption-observations.json').write_text(json.dumps(dict(requests=sorted(requests),queries=sorted(queries),results=c['_interrupt_observations']),ensure_ascii=False,indent=2))
        if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):
            paused.update(route=route,response=response);return
        if mode=='loss':
            for result in payload.get('results',[]):
                if result['requestId']in requests|queries:
                    rid=result['requestId'];lost.append(rid);result.clear();result.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
        route.fulfill(response=response,json=payload)
    if mode=='late'and '_interrupt_observations'in c:
        page.set_viewport_size({'width':1480,'height':1050});panel().locator('[data-bp-percent]').click();zoom=page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.get_by_role('button',name='전체 보기',exact=True).click();page.keyboard.press('Escape')
    page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
    deadline=time.monotonic()+c.get('_interrupt_timeout_seconds',30)
    while time.monotonic()<deadline:
        if paused or requests and any(r in queries for r in lost):break
        page.wait_for_timeout(30)
    assert len(requests)==1
    if mode=='late':
        def trace(phase):
            if '_interrupt_observations'in c:print('LATE_PHASE '+phase,flush=True)
        assert paused;trace('success held; resize');page.set_viewport_size({'width':1480,'height':1050});trace('resized; select stored output');panel().locator('[data-bp-node=first] .bp-pin-plug[data-side=out] .bp-pin-value').click();trace('selected; enter new name');name=panel().get_by_role('textbox',name='지역변수 이름',exact=True);name.fill('늦은 보관값');name.press('Enter');trace('new input entered; release response');paused['route'].fulfill(response=paused['response']);trace('response released')
    else:assert any(r in queries for r in lost)
    page.unroute('**/api/request',interrupt);c['idle']();assert c['pending']();restart(c,3);retry=len(c['traffic']);panel().locator('[data-bp-save]').click();c['idle']()
    for _ in range(1000):
        if any(r.get('input',{}).get('action')=='settledAuthorBatch'for r in c['traffic'][retry:]):break
        c['page'].wait_for_timeout(20)
    assert not any(r.get('input',{}).get('action')=='authorBatch'for r in c['traffic'][retry:])
    if mode=='late':
        assert c['pending']();next_mark=len(c['traffic']);panel().locator('[data-bp-save]').click();c['saved'](next_mark);assert next(l for l in c['current']()['locals']if l['id']=='firstValue')['name']=='늦은 보관값'
    else:assert c['pending']()==[]
    c['checked']('응답 유실/늦은 새 입력은 cold 후 기존 영수증을 먼저 조회하고 새 입력만 별도로 저장한다')
    return [r for r in c['traffic'][mark:]if r.get('input',{}).get('action')=='authorBatch'][:1]

def review_ready(c):
    panel=c['author'];page=c['page']
    if not panel().is_visible():
        page.set_viewport_size({'width':1480,'height':1050});c['open_author']()
    panel().locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');c['expect'](review).to_be_visible(timeout=120000)
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
    return review

def review(c,first):
    first.locator('[data-reject]').click();c['expect'](first).not_to_be_visible();c['unchanged']();current=review_ready(c)
    if c['async_mode']=='conflict':
        path=c['project']/'project.cproj';before=path.read_bytes();path.write_bytes(before+b'\n');mark=len(c['traffic'])
        try:
            current.locator('#confirm').click();failure=refused(c,mark);(c['case']/'manifest-cas-refusal.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2));assert any(v.get('result',{}).get('sourceConfirmed')is False for v in failure);c['idle']();assert all((c['project']/k).read_bytes()==v for k,v in c['original'].items()if k!='project.cproj')
        finally:path.write_bytes(before)
        if current.is_visible():current.locator('[data-reject]').click()
        c['checked']('Review 뒤 프로젝트 변경도 최종 CAS에서 전부 미반영하고 저장된 후보를 보존한다');current=review_ready(c)
    return current

def after_saved(c):
    if c['async_mode']!='normal':return
    page=c['page'];panel=c['author'];expect=c['expect'];page.set_viewport_size({'width':1480,'height':1050});c['idle']()
    panel().locator('[data-bp-percent]').click();zoom=page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.get_by_role('button',name='전체 보기',exact=True).click();page.keyboard.press('Escape')
    baseline={u['id']:u for u in json.loads(c['_checkpoint'].read_text())['changes']}
    def edit(cancel):
        panel().locator('[data-bp-node=combine] [data-internal-code]').click();dialog=page.get_by_role('dialog',name='C# Script · 보관값 합치기',exact=True);editor=dialog.locator('[data-code-source]');body=dialog.locator('[data-code-region=body]').text_content();text=body+'\n// 명시적 후속 본문 편집'
        editor.evaluate('(el,body)=>{const at=el.value.indexOf(body);if(at<0)throw Error("body missing");el.focus();el.setSelectionRange(at,at+body.length)}',body);page.keyboard.insert_text(text);dialog.locator('[data-code-cancel]'if cancel else'[data-code-save]').click();return text
    held=c['pending']();edit(True);assert c['pending']()==held
    text=edit(False);held=c['pending']();checkpoint=c['_checkpoint'];before=checkpoint.read_bytes();before_source=next(v for v in c['current']()['nodes']if v['id']=='combine')['source'];mark=len(c['traffic']);checkpoint.chmod(0o400)
    try:
        panel().locator('[data-bp-save]').click();failure=refused(c,mark);c['idle']();now=c['pending']();(c['case']/'csharp-save-failure.json').write_text(json.dumps(dict(before=held,after=now,response=failure),ensure_ascii=False,indent=2));assert all(dict(now).get(k)==v for k,v in held),'C# private input lost before checkpoint save';assert checkpoint.read_bytes()==before;assert next(v for v in c['current']()['nodes']if v['id']=='combine')['source']==before_source
    finally:checkpoint.chmod(0o600)
    c['checked']('속성 뒤 C# 본문 저장 실패도 개인 입력·기존 checkpoint·원본을 보존하고 같은 후보로 재시도한다')
    mark=len(c['traffic']);panel().locator('[data-bp-save]').click();c['saved'](mark)
    c['idle']();assert not c['pending']();after={u['id']:u for u in json.loads(c['_checkpoint'].read_text())['changes']};gid=c['n']+'CalcBody/body:common';assert after[gid]['propertyObservations']==baseline[gid]['propertyObservations'];assert json.loads(after[gid+'/node:combine']['draft'])['source']==text;c['unchanged']()
    restart(c,4);assert next(v for v in c['current']()['nodes']if v['id']=='combine')['source']==text
    c['expected_changed']={'Calc.graph.json','combine.node.json'};c['checked']('속성 저장 뒤 기존 C# 편집·취소·Save·cold 복원은 원본 관측을 재기준화하지 않고 새 본문만 보존한다')

def after_confirm(c):
    c['call']('saveDraft',{});assert c['current']()['diagnostics']['state']in['source-ready','source-assembled'];c['checked']('Confirm의 실제 반영 후 이전 원본 관측을 종료하여 같은 세션의 반복 Save도 허용한다')
