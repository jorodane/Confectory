"""Actual owned private switch case calls and atomic saved input closure."""
import ast, shutil, sys
from pathlib import Path

scenario=sys.argv[3] if len(sys.argv)>3 else 'after'
assert scenario in ('after','empty','shared')
fixture=Path(__file__).with_name('v821_child_case_order_ui.py')
setup=ast.parse(fixture.read_text()).body
argv=sys.argv
sys.argv=[*argv[:3],'shared' if scenario=='shared' else 'normal']
try:
    exec(compile(ast.Module(body=setup[:next(i for i,n in enumerate(setup) if isinstance(n,ast.Try))],type_ignores=[]),str(fixture),'exec'),globals())
finally:sys.argv=argv
if scenario=='empty':
    child['nodes']=[n for n in child['nodes'] if n['id'] not in initial]
    child['edges']=[e for e in child['edges'] if e['from'] not in initial]
    next(e for e in child['edges'] if e['port']=='case:positive')['to']='return:choose'
    for name in initial:(f.project/f'Pair.{name}.node.json').unlink()
    initial=[]
    graph_path.write_text(json.dumps(root))
path='body/nest' if '--nested' in sys.argv else 'body'
if path!='body':
    for invocation in root['nodes'][:2]:
        nested=copy.deepcopy(invocation);nested['id']='nest'
        invocation['graph']=dict(schema=1,profile='sync-acyclic-nested-v1',entry='nest',nodes=[nested],edges=[edge('nest','exit:return')],exits={'return':{'node':'nest'} if invocation['id']=='body' else None})
    child=root['nodes'][0]['graph']['nodes'][0]['graph']
    definitions=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'PairBody',text=(f.project/'PairBody.celem').read_text(),bodyTarget='common',graph=root,definitionsOnly=True)
    assert definitions['state']=='node-definitions'
    hashes={n['id']:n['definitionHash'] for n in definitions['nodes']+definitions['nestedNodes']}
    for identity,node in [(path+'/'+n['id'],n) for n in child['nodes']]+[('peer/nest/positive',peer),('after',root['nodes'][-1])]:
        file=f.project/node['implementation'];data=json.loads(file.read_text());data['definitionHash']=hashes[identity];file.write_text(json.dumps(data))
    graph_path.write_text(json.dumps(root))
    frame=t.graph+'/graph:body/graph:nest';other=t.graph+'/graph:peer/graph:nest'
    def read(id=frame):return f.invoke('blueprint',dict(action='read',id=id))['result']['result']
    def enter_body():
        if doc().locator('[data-document-cell="choose"]').is_visible():return
        breadcrumb=panel().locator('.bp-breadcrumbs button').first
        if breadcrumb.is_visible():breadcrumb.click();f.idle()
        for segment in path.split('/'):
            doc().locator(f'[data-document-internal="{segment}"]').click();f.idle()
        expect(doc().locator('[data-document-cell="choose"]')).to_be_visible()

probe=f.n+'CaseProbe';following=f.n+'CaseFollow'
for name,feature,ret,body in [('CaseProbe',probe,'int','global::System.Console.WriteLine("case-probe:"+amount); return amount+5;'),('CaseFollow',following,'void','global::System.Console.WriteLine("case-follow:"+amount);')]:
    (f.project/f'{name}.celem').write_text(f'function {feature} (int amount) -> {ret} {{provide {feature} with {feature}Body;}}')
    (f.project/f'{name}Body.celem').write_text(f'implementation {feature}Body for {feature} (int amount) -> {ret} {{body common "{name}.csbody";}}')
    (f.project/f'{name}.csbody').write_text(body)
    manifest=f.project/'project.cproj'
    manifest.write_text(manifest.read_text().rstrip().removesuffix('}')+f'element {name} function "{name}.celem";element {name}Body implementation "{name}Body.celem";}}')
x.physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
original=graph_path.read_bytes();original_graph=json.loads(original)
other_project=f.case/'same IDs case project';shutil.copytree(f.project,other_project,ignore=shutil.ignore_patterns('.confectory','.build'))
other_files={p:p.read_bytes() for p in other_project.rglob('*') if p.is_file()}

def pick(button,feature):
    expect(button).to_be_enabled();button.click()
    f.page.get_by_role('dialog',name='블루프린트 노드 검색').locator(f'[data-resource-feature="{feature}"]').click()

def bind(id,label):
    value=doc().locator(f'[data-document-cell="{id}"] [data-document-value][data-document-port="field:amount"]')
    value.click();f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('button',name=label,exact=True).click()

try:
    f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
    baseline=read();peer_before=read(other)['nodes']
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1500))
        f.open_owner(f.n+'Target1');f.owner().locator('.object-title-description').fill('independent local input')
        peer_input=[(k,v) for k,v in f.pending()['schema'] if '|'+f.n+'Target1|element|' in k];assert peer_input
        def peer_kept():assert all(dict(f.pending()['schema']).get(k)==v for k,v in peer_input)
        open_document();enter_body()
        branch=order(initial)
        add=branch.locator('[data-document-branch-call]' if scenario=='empty' else '[data-document-insert-call=positive]')
        if scenario=='shared':
            assert not baseline.get('documentFrameReferenceBinding');assert not add.count() or not add.is_enabled()
            f.checked('Shared branch refuses private call insertion')
        else:
            assert baseline['documentFrameReferenceBinding']['path']==path
            pick(add,probe)
            cell=branch.locator('[data-document-cell^="call_"]');expect(cell).to_be_visible();first=cell.get_attribute('data-document-cell')
            bind(first,'입력 · amount')
            pick(branch.locator(f'[data-document-insert-call="{first}"]'),following)
            cell=branch.locator(f'[data-document-cell^="call_"]:not([data-document-cell="{first}"])');expect(cell).to_be_visible();second=cell.get_attribute('data-document-cell')
            expected=[first,second] if scenario=='empty' else ['positive',first,second,'tail']
            order(expected);local_undo();assert not cell.count();local_undo(True);order(expected)
            bind(second,'CaseProbe · 결과');held=pending();assert held and checkpoint.read_bytes()==before
            x.original();peer_kept();assert read(other)['nodes']==peer_before
            # Neither an external callee edit nor an original sibling edit can apply any part of this batch.
            source=f.project/'CaseFollow.celem';raw=source.read_bytes();source.write_bytes(raw+b' ')
            try:
                panel().locator('[data-bp-save]').click();f.idle();expect(panel().locator('.bp-status')).not_to_have_text('저장됨')
                assert retained(held) and checkpoint.read_bytes()==before
            finally:source.write_bytes(raw)
            restart_child(1);order(expected);assert retained(held)
            panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=120000);f.idle()
            assert not pending();x.original();peer_kept();current=read();assert read(other)['nodes']==peer_before
            for id,feature in [(first,probe),(second,following)]:
                row=next(n for n in current['nodes'] if n['id']==id);assert row['calledFeature']==feature and row['branchOwner']=='choose'
            r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original()
            r=review();saved=checkpoint.read_bytes();sibling=f.project/peer['implementation'];raw=sibling.read_bytes();sibling.write_bytes(raw+b' ')
            try:
                r.locator('#confirm').click();f.idle();assert checkpoint.read_bytes()==saved and graph_path.read_bytes()==original
            finally:sibling.write_bytes(raw)
            if r.is_visible():r.locator('[data-reject]').click()
            r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
            written=json.loads(graph_path.read_text());case=written
            for segment in path.split('/'):case=next(n['graph'] for n in case['nodes'] if n['id']==segment)
            one=next(n for n in case['nodes'] if n['id']==first);two=next(n for n in case['nodes'] if n['id']==second)
            assert one['arguments']=={'amount':{'input':'amount'}} and two['arguments']=={'amount':{'node':first,'output':'return'}}
            assert one['branchOwner']==two['branchOwner']=='choose'
            anchor='choose' if scenario=='empty' else 'positive';end='return:choose' if scenario=='empty' else 'tail'
            assert next(e['to'] for e in case['edges'] if e['from']==second)==end
            case['nodes']=[n for n in case['nodes'] if n['id'] not in (first,second)]
            case['edges']=[e for e in case['edges'] if e['from'] not in (first,second)]
            next(e for e in case['edges'] if e['from']==anchor and e['port']==('case:positive' if scenario=='empty' else 'next'))['to']=end
            assert written==original_graph
            assert all(p.read_bytes()==raw for p,raw in x.physical.items() if p not in (graph_path,f.project/'PairBody.celem'))
            result=output().replace('finish:7','case-probe:7\ncase-follow:12\nfinish:7') if scenario=='empty' else output().replace('positive:7\ntail:7','positive:7\ncase-probe:7\ncase-follow:12\ntail:7')
            x.build('private-case-call',14,result)
            restart_child(2);order(expected);assert not pending();peer_kept()
            # The exact same IDs in another temporary project remain independent.
            f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other_project/'project.cproj');f.start(3);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1500));open_document();enter_body();order(initial)
            assert not pending() and all(p.read_bytes()==raw for p,raw in other_files.items())
            f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.project/'project.cproj');f.start(4);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1500));f.idle()
            f.page.get_by_role('button',name='프로젝트 실행',exact=True).click();expect(f.page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 14',timeout=120000);peer_kept()
            f.checked('explicit private case gap, connected two calls, local Undo/Redo, atomic Save, stale source refusal, Confirm CAS, actual execution, cold restart and identical-ID isolation')
        assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
    try:f.page.screenshot(path=str(f.case/'private-case-call-failure.png'),timeout=5000)
    except Exception:pass
    raise
finally:
    (f.case/'private-case-call-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('V821_PRIVATE_CASE_CALL',scenario,f.case,flush=True)
