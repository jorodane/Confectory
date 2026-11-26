"""Actual mouse movement between two cases in a directly owned child switch."""
import ast
import copy
import json
from pathlib import Path
import shutil
import sys
import uuid

from playwright.sync_api import expect, sync_playwright

scenario = sys.argv[3] if len(sys.argv)>3 else 'normal'
assert scenario in {'normal','baseline','single','baseline-position','middle','start'}
fixture = Path(__file__).with_name('v821_child_case_order_ui.py')
setup = ast.parse(fixture.read_text()).body
argv = sys.argv
sys.argv = [*argv[:3], 'normal']
try:
    exec(compile(ast.Module(body=setup[:next(i for i,n in enumerate(setup) if isinstance(n,ast.Try))],
                            type_ignores=[]),str(fixture),'exec'),globals())
finally:
    sys.argv = argv

# A no-argument void action can move without a value dependency. Keep the
# other case's value-carrying cells and another frame with the same local ID.
tail['signature']['args'] = []
tail['arguments'] = {}
if scenario=='single':
    child['nodes']=[node for node in child['nodes'] if node['id']!='positive']
    child['edges']=[route for route in child['edges'] if route['from']!='positive']
    next(route for route in child['edges'] if route['port']=='case:positive')['to']='tail'
    (f.project/'Pair.positive.node.json').unlink()
    initial=['tail']
peer['id'] = 'tail'
peer_frame = root['nodes'][1]['graph']
peer_frame['entry'] = 'tail'
peer_frame['edges'][0]['from'] = 'tail'
leaf = f.project / tail['implementation']
peer_file = f.project / peer['implementation']
definitions = f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=f.n+'PairBody',
                         text=(f.project/'PairBody.celem').read_text(),bodyTarget='common',graph=root,definitionsOnly=True)
assert definitions['state']=='node-definitions'
hashes={node['id']:node['definitionHash'] for node in definitions['nestedNodes']}
for path,file,source in [('body/tail',leaf,'global::System.Console.WriteLine("tail:7");'),
                         ('peer/tail',peer_file,'global::System.Console.WriteLine("peer");')]:
    file.write_text(json.dumps(dict(schema=1,node='tail',definitionHash=hashes[path],source=source)))
graph_path.write_text(json.dumps(root,ensure_ascii=False))
x.physical={path:path.read_bytes() for path in f.project.iterdir() if path.is_file()}
expected=copy.deepcopy(root)
changed=expected['nodes'][0]['graph']
links={(e['from'],e['port']):e for e in changed['edges']}
links[('choose','case:positive') if scenario=='single' else ('positive','next')]['to']='return:choose'
if scenario=='start':
    links[('choose','case:negative')]['to']='tail'
    links[('tail','next')]['to']='negative'
elif scenario=='middle':
    links[('negative','next')]['to']='tail'
    links[('tail','next')]['to']='negativeTail'
else:
    links[('negativeTail','next')]['to']='tail'
    links[('tail','next')]['to']='return:choose'
pos_before=['tail'] if scenario=='single' else ['positive','tail'];neg_before=['negative','negativeTail']
pos_after=[] if scenario=='single' else ['positive'];neg_after=['tail','negative','negativeTail'] if scenario=='start' else ['negative','tail','negativeTail'] if scenario=='middle' else ['negative','negativeTail','tail']
original_output=output()
lines=original_output.splitlines();lines.remove('tail:7');lines.insert(lines.index('negative:-2') if scenario=='start' else lines.index('negative:-2')+1 if scenario=='middle' else lines.index('negativeTail:-2')+1,'tail:7')
changed_output='\n'.join(lines)


def case_order(name):
    pane=select_case(name)
    return pane.locator(':scope>[data-document-cell]').evaluate_all('(els)=>els.map(e=>e.dataset.documentCell)')


def cases(pos,neg):
    assert case_order('positive')==pos
    assert case_order('negative')==neg


def drag_to_negative(allowed,cancel=False,node='tail',position=None):
    select_case('positive')
    start_drag(node)
    tab=doc().locator('[data-document-branch="case:negative"][data-document-owner=choose]')
    bounds=tab.bounding_box();assert bounds
    x_pos=bounds['x']+bounds['width']/2;y_pos=bounds['y']+bounds['height']/2
    f.page.mouse.move(x_pos+3,y_pos,steps=15)
    f.page.mouse.move(x_pos,y_pos,steps=3)
    marker=f.page.locator('.fd-cell-drop-marker[data-branch-transfer]')
    expect(marker).to_have_count(int(allowed),timeout=3000)
    if allowed:expect(marker).to_have_text('분기 끝에 놓기')
    if position is not None:
        pane=doc().locator('[data-document-panel="case:negative"]')
        if position=='baseline':
            expect(pane).to_be_hidden()
        else:
            expect(pane).to_be_visible()
            target=pane.locator(':scope>[data-document-cell="negative"]');bounds=target.bounding_box();assert bounds
            f.page.mouse.move(bounds['x']+bounds['width']/2,bounds['y']+bounds['height']*(.25 if position=='start' else .75),steps=15)
            expect(marker).to_have_text('분기 안에 놓기')

    if cancel:f.page.keyboard.press('Escape')
    f.page.mouse.up();f.idle();expect(marker).to_have_count(0)
    if cancel and position in {'start','middle'}:
        expect(doc().locator('[data-document-panel="case:positive"]')).to_be_visible()
        expect(doc().locator('[data-document-panel="case:negative"]')).to_be_hidden()



def transfer_request(data):
    edits=[dict(action='route',node=e['from'],port=e['port'],to=e['to'])
           for e in changed['edges'] if e['from'] in {'positive','negative','negativeTail','tail'} or e['port'].startswith('case:')]
    return dict(action='authorBatch',id=frame,attempt=uuid.uuid4().hex,
                documentFrame=copy.deepcopy(data[key]),checkpointHash=data['checkpointHash'],
                sourceProof=x.proof(data),edits=edits)


try:
    x.build('before-child-case-transfer',14,original_output)
    f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
    checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400))
        open_document();enter_body();enlarge()
        baseline=read();peer_before=read(other)['nodes']
        cases(pos_before,neg_before)
        if scenario=='baseline':
            assert not baseline.get('documentBranchTransfer')
            drag_to_negative(False)
            cases(pos_before,neg_before)
            assert not pending() and checkpoint.read_bytes()==before
            f.checked('Existing child UI cannot transfer the ordinary action to the other case')
        elif scenario=='baseline-position':
            assert baseline['documentBranchTransfer']['movable']==['tail']
            drag_to_negative(True,cancel=True,position='baseline')
            cases(pos_before,neg_before);assert not pending() and checkpoint.read_bytes()==before
            f.checked('Existing branch tab only exposes append; the destination cells cannot be targeted')
        else:
            assert baseline['documentBranchTransfer']['movable']==['tail']
            if scenario in {'normal','middle','start'}:
                drag_to_negative(False,node='positive');cases(pos_before,neg_before);assert not pending()
            position=scenario if scenario in {'start','middle'} else None
            drag_to_negative(True,cancel=True,position=position);cases(pos_before,neg_before);assert not pending()
            drag_to_negative(True,position=position);cases(pos_after,neg_after)
            held=pending();assert len(held)==len(pos_before)+len(neg_before)+2 and checkpoint.read_bytes()==before
            local_undo();cases(pos_before,neg_before);assert not pending()
            local_undo(True);cases(pos_after,neg_after);assert pending()==held
            restart_child(1);cases(pos_after,neg_after);assert pending()==held
            x.original();assert read(other)['nodes']==peer_before
            wrong=transfer_request(baseline);wrong['documentFrame']['path']='peer'
            f.invoke('blueprint',wrong,False)
            assert pending()==held and checkpoint.read_bytes()==before
            if scenario in {'middle','start'}:
                reordered=transfer_request(baseline)
                replacements={('choose','case:negative'):'negativeTail',('negativeTail','next'):'tail',('tail','next'):'negative',('negative','next'):'return:choose'}
                for edit in reordered['edits']:
                    if (edit['node'],edit['port']) in replacements:edit['to']=replacements[(edit['node'],edit['port'])]
                f.invoke('blueprint',reordered,False)
                assert pending()==held and checkpoint.read_bytes()==before

            f.checked('Mouse transfer, Escape, local Undo/Redo and cold preserve the same-ID sibling and original files')

            if scenario in {'normal','middle'}:
                # A different project has the same original sources and graph IDs.
                duplicate=f.case/'same IDs other project'
                shutil.copytree(f.project,duplicate,ignore=shutil.ignore_patterns('.confectory'))
                originals={p:p.read_bytes() for p in duplicate.rglob('*') if p.is_file()}
                original_project=f.env['CONFECTORY_WEB_PROJECT'];f.pending();f.page.close();f.stop()
                try:
                    f.env['CONFECTORY_WEB_PROJECT']=str(duplicate/f.manifest.name);f.start(6)
                    f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{})
                    other_checkpoint=next(duplicate.glob('.confectory/edit-workspaces/*/draft.json'));other_before=other_checkpoint.read_bytes()
                    same=read();assert same[key]==baseline[key] and same['checkpointHash']!=baseline['checkpointHash']
                    f.invoke('blueprint',transfer_request(baseline),False)
                    assert other_checkpoint.read_bytes()==other_before and all(p.read_bytes()==raw for p,raw in originals.items())
                finally:
                    f.stop();f.env['CONFECTORY_WEB_PROJECT']=original_project
                f.start(7);f.page=f.setup();f.page.set_viewport_size(dict(width=1800,height=1400));open_document();enter_body()
                cases(pos_after,neg_after);assert pending()==held and checkpoint.read_bytes()==before
                f.checked('Same-ID project rejects the original transfer and returning retains the local route inputs')

            raw=peer_file.read_bytes();peer_file.write_bytes(raw+b' ')
            try:
                save();assert retained(held) and checkpoint.read_bytes()==before and peer_file.read_bytes()==raw+b' '
            finally:peer_file.write_bytes(raw)
            save();assert not pending();saved=read()
            assert saved['edges']==changed['edges'] and read(other)['nodes']==peer_before
            x.original()
            for direction,edges in [('undo',baseline['edges']),('redo',changed['edges'])]:
                step=f.invoke('draftHistory',dict(action='inspect'))['result']['result'][direction]
                assert step['available']
                assert f.invoke('draftHistory',dict(action=direction,token=step['token']))['result']['result']['accepted']
                assert read()['edges']==edges and read(other)['nodes']==peer_before
            f.invoke('saveDraft',{});restart_child(2);cases(pos_after,neg_after);x.original()
            f.checked('Sibling CAS refuses Save; shared Undo/Redo and cold retain exactly the two case routes')

            r=review();r.locator('[data-reject]').click();x.original()
            r=review();saved_checkpoint=checkpoint.read_bytes();peer_file.write_bytes(raw+b' ')
            try:
                r.locator('#confirm').click();f.idle()
                assert checkpoint.read_bytes()==saved_checkpoint and graph_path.read_bytes()==x.physical[graph_path] and peer_file.read_bytes()==raw+b' '
            finally:peer_file.write_bytes(raw)
            if r.is_visible():r.locator('[data-reject]').click()
            r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
            assert json.loads(graph_path.read_text())==expected
            assert all(p.read_bytes()==raw for p,raw in x.physical.items() if p!=graph_path)
            x.build('after-child-case-transfer',14,changed_output)
            restart_child(3);cases(pos_after,neg_after);assert not pending() and read(other)['nodes']==peer_before
            f.checked('Confirm changes only the two branch routes; actual other branch executes the moved cell and all return values remain unchanged')
        assert not f.errors and not f.external,(f.errors,f.external)
        f.browser.close()
finally:
    (f.case/'child-case-transfer-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False))
    f.stop()
    print('V821_CHILD_CASE_TRANSFER',scenario,f.case,flush=True)
