"""Create a new function through EditorHome, write Logic Code, publish and run it."""
import json
from pathlib import Path
import re
import shutil
import sys
import time

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as f
from editor_navigation import open_workspace_menu

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gui'))
from editor_logic_workflow import review, run_from_dock

early = len(sys.argv)>3 and sys.argv[3]=='before-save'
session_child = len(sys.argv)>3 and sys.argv[3]=='session-child'
full_clean = len(sys.argv)>3 and sys.argv[3]=='full-clean'
full_session = full_clean or len(sys.argv)>3 and sys.argv[3]=='full-session'
session = full_session or session_child or len(sys.argv)>3 and sys.argv[3]=='session'
staged = session or len(sys.argv)>3 and sys.argv[3]=='staged'
branch_mode = staged or len(sys.argv)>3 and sys.argv[3]=='branch'
compound = branch_mode or len(sys.argv)>3 and sys.argv[3]=='compound'
name = 'LocalAuthorProbe'
target = 'Example.FrameLoop::' + name
marker = f.root / 'new-function-result.txt'
donor_marker = f.root / 'referenced-function-result.txt'
donor = 'Example.FrameLoop::LocalDonor'
# Add an ordinary published donor to the synthetic project only.
manifest = f.projects[0]
manifest.write_text(manifest.read_text().rstrip().removesuffix('}') +
    'element LocalDonor function "LocalDonor.celem";element LocalDonorBody implementation "LocalDonorBody.celem";}')
donor_sources = {
    'LocalDonor.celem': f'function {donor} (int amount) -> void {{provide {donor} with {donor}Body;}}',
    'LocalDonorBody.celem': f'implementation {donor}Body for {donor} (int amount) -> void {{body common "LocalDonor.csbody";}}',
    'LocalDonor.csbody': 'System.IO.File.WriteAllText(' + json.dumps(str(donor_marker)) + ', amount.ToString());',
}
for filename, text in donor_sources.items():
    path = manifest.parent / filename
    path.write_text(text)
    f.before[str(path)] = path.read_bytes()
f.before[str(manifest)] = manifest.read_bytes()
expect.set_options(timeout=60000)

try:
    with sync_playwright() as pw, pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
        f.start(0)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        menu = open_workspace_menu(page)
        menu.locator('[data-workspace-create-menu]').click()
        page.locator('[data-workspace-create=Feature]').click()
        dialog = page.get_by_role('dialog', name='새 기능 만들기', exact=True)
        dialog.locator('#object-name').fill(name)
        dialog.get_by_role('button', name='생성', exact=True).click()
        expect(dialog).to_be_hidden()
        declaration = page.locator('.window[data-key=declaration]')
        expect(declaration.locator('.object-title-name')).to_have_text(name)
        assert '() -> int' in f.state()['draft']['text']
        declaration.locator('[data-function-write-direct]').click()
        panel = page.locator('.window[data-key=blueprint]')
        expect(panel.locator('.function-document')).to_be_visible()
        panel.get_by_role('tab', name='논리 코드', exact=True).click()
        doc = panel.locator('.function-document')
        expect(doc.locator('[data-document-cell="$entry"]')).to_be_visible()
        if early:
            entry = doc.locator('[data-document-cell="$entry"]')
            entry.locator('[data-document-contract="$entry"]').click()
            contract = entry.locator('[data-document-contract-side=inputs]')
            contract.locator('[data-mobile-contract-add]').click()
            field=contract.locator('[data-mobile-contract-field=input1]')
            expect(field).to_be_visible()
            field.locator('[data-signature-type]').click()
            page.get_by_role('dialog',name='속성 타입 선택').locator('[data-type=int]').click()
            output=entry.locator('[data-document-contract-side=outputs] [data-mobile-contract-field=return]')
            output.locator('[data-signature-type]').click()
            page.get_by_role('dialog',name='속성 타입 선택').locator('[data-type=long]').click()
            entry.locator('[data-document-contract="$entry"]').click()
            f.original()
        code = doc.locator('[data-document-code=body]')
        expect(code).to_be_enabled()
        code.click()
        script = page.locator('.bp-script-dialog')
        source = script.locator('[data-code-source]')
        expect(source).to_be_visible()
        new = 'System.IO.File.WriteAllText(' + json.dumps(str(marker)) + ', "new function executed");\nreturn 0;'
        source.evaluate('''el => {
            const parts=Array.from(el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight] > span'));
            const index=parts.findIndex(part=>part.dataset.codeRegion==='body');
            if(index<0)throw Error('Missing editable body');
            const start=parts.slice(0,index).reduce((offset,part)=>offset+part.textContent.length,0);
            el.focus();el.setSelectionRange(start,start+parts[index].textContent.length);
        }''')
        page.keyboard.insert_text(new)
        expect(script.locator('[data-code-region=body]')).to_have_text(new)
        script.locator('[data-code-save]').click()
        expect(script).to_be_hidden()
        if not early:
            panel.locator('[data-bp-save]').click()
            expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
            f.original()
            r=review(page,panel.locator('[data-bp-complete]'))
            r.locator('#confirm').click()
            expect(r).to_be_hidden(timeout=120000)
            assert name in f.projects[0].read_text() and name not in f.projects[1].read_text()
            print('PASS actual new feature declaration, document code edit, Save and Confirm', flush=True)
        if session:
            page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(5)
            page=f.setup(browser);page.set_viewport_size({'width':1900,'height':1500});panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
            graph_path=next(manifest.parent.glob('blueprints/*.graph.json'));original_graph=graph_path.read_bytes()
            retained_source=graph_path.parent/json.loads(original_graph)['nodes'][0]['implementation'];retained_bytes=retained_source.read_bytes()
            checkpoint=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'),None)
            checkpoint_before=checkpoint.read_bytes() if checkpoint else None
            before_composition=len(f.requests)
            page.evaluate('''()=>{globalThis.compoundMarks={};document.addEventListener('click',event=>{if(!event.isTrusted)return;const target=event.target.closest('button');if(!target)return;const key=target.matches('[data-document-internal]')?'wrap':target.matches('[data-document-insert-call]')?'search':target.matches('[data-resource-feature]')?'select':null;if(key)compoundMarks[key]=performance.now();},true);}''')
            def unchanged():
                assert graph_path.read_bytes()==original_graph and retained_source.read_bytes()==retained_bytes
                current=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'),None)
                assert (current.read_bytes() if current else None)==checkpoint_before
            def replace_body(text):
                script=page.locator('.bp-script-dialog');source=script.locator('[data-code-source]');expect(source).to_be_visible()
                source.evaluate("el=>{const spans=Array.from(el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight] > span'));const idx=spans.findIndex(s=>s.dataset.codeRegion==='body');if(idx<0)throw Error('Missing body');const start=spans.slice(0,idx).reduce((a,b)=>a+b.textContent.length,0);el.focus();el.setSelectionRange(start,start+spans[idx].textContent.length)}")
                page.keyboard.insert_text(text);script.locator('[data-code-save]').click();expect(script).to_be_hidden()
            started=time.perf_counter();doc.locator('[data-document-internal=body]').click();expect(panel.locator('.bp-breadcrumbs')).to_be_visible(timeout=20000)
            panel.get_by_role('tab',name='논리 코드',exact=True).click();expect(doc.locator('[data-document-cell=body]')).to_be_visible()
            add=doc.locator('[data-document-add="$entry"]');expect(add).to_be_enabled()
            print('TIMING wrap editable ms',round((time.perf_counter()-started)*1000),flush=True)
            print('TIMING trusted wrap click to editable ms',round(page.evaluate('performance.now()-compoundMarks.wrap')),flush=True)
            started=time.perf_counter();add.click()
            cell=doc.locator('[data-document-cell^="cell_"]');expect(cell).to_be_visible();created=cell.get_attribute('data-document-cell');print('TIMING unsaved child add ms',round((time.perf_counter()-started)*1000),flush=True)
            mode_marker=f.root/'private-case-mode.txt'
            def declare_first():
                first=doc.locator(f'[data-document-call-first-branch="{created}"]');expect(first).to_be_enabled();started=time.perf_counter();first.click()
                expect(page.locator('.bp-script-dialog [data-code-source]')).to_be_visible();print('TIMING unsaved branch editor ms',round((time.perf_counter()-started)*1000),flush=True)
                replace_body('var mode=System.IO.File.ReadAllText('+json.dumps(str(mode_marker))+'); return mode=="positive"?Result.Positive:mode=="negative"?Result.Negative:Result.NoBranch;')
                expect(doc.locator('[data-document-branch="case:positive"]')).to_be_visible()
            branch_marker=f.root/'private-case-marker.txt'
            def compose_case(save_between):
                doc.locator('[data-document-branch="case:positive"]').click();case=doc.locator('[data-document-panel="case:positive"]')
                add=case.locator('[data-document-branch-add]');expect(add).to_be_enabled();started=time.perf_counter();add.click()
                branch_cell=case.locator('[data-document-cell^="cell_"]');expect(branch_cell).to_be_visible();branch_id=branch_cell.get_attribute('data-document-cell')
                print('TIMING branch child add ms',round((time.perf_counter()-started)*1000),flush=True)
                branch_cell.locator('[data-document-code]').click();replace_body('System.IO.File.WriteAllText('+json.dumps(str(branch_marker))+', "positive");return;')
                if save_between:panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000)
                doc.locator('[data-document-branch="case:positive"]').click();case=doc.locator('[data-document-panel="case:positive"]')
                add=case.locator(f'[data-document-insert-call="{branch_id}"]');expect(add).to_be_enabled();started=time.perf_counter();add.click()
                page.get_by_role('dialog',name='블루프린트 노드 검색').locator(f'[data-resource-feature="{donor}"]').click()
                call_cell=case.locator('[data-document-cell^="call_"]');expect(call_cell).to_be_visible();branch_call=call_cell.get_attribute('data-document-cell')
                print('TIMING branch reference add ms',round((time.perf_counter()-started)*1000),flush=True)
                value=call_cell.locator('[data-document-value][data-document-port="field:amount"]');expect(value).to_be_enabled()
                print('TIMING trusted search to selection and selection to editable ms',page.evaluate('[Math.round(compoundMarks.select-compoundMarks.search),Math.round(performance.now()-compoundMarks.select)]'),flush=True)
                started=time.perf_counter();value.click();search=page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');search.fill('37');search.press('Enter')
                expect(value).to_have_text('37');print('TIMING value binding ms',round((time.perf_counter()-started)*1000),flush=True)
                if save_between:panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000)
                return branch_id,branch_call
            if not session_child:declare_first();unchanged()
            if full_session:branch_id,branch_call=compose_case(False);unchanged()
            if full_session and not full_clean:
                preview_request=next(row['input'] for row in reversed(f.requests[before_composition:]) if row.get('endpoint')=='blueprint' and row.get('input',{}).get('action')=='previewNodeInternal')
                reference_request=next(row['input'] for row in reversed(f.requests[before_composition:]) if row.get('endpoint')=='blueprint' and row.get('input',{}).get('action')=='readCall')
                if preview_request.get('observedBasis'):
                    graph_path.write_bytes(original_graph+b' ')
                    try:f.call('blueprint',preview_request,False)
                    finally:graph_path.write_bytes(original_graph)
                    unchanged()
                    print('PASS reused preview basis rejects changed physical graph',flush=True)
                if reference_request.get('contractOnly'):
                    observed=f.call('blueprint',reference_request)
                    assert observed.get('contractOnly') is True and not observed.get('basis')
                    donor_path=manifest.parent/'LocalDonor.celem';old=donor_path.read_bytes();donor_path.write_bytes(old+b' ')
                    try:f.call('blueprint',reference_request,False)
                    finally:donor_path.write_bytes(old)
                    unchanged()
                    print('PASS contract-only read produces no mutation basis and rejects changed declaration',flush=True)

            doc.locator('.fd-document-title').click();page.keyboard.press('Control+z');expect(doc.locator('[data-document-internal=body]')).to_be_visible();expect(panel.locator('.bp-breadcrumbs button')).to_have_count(0);unchanged()
            doc.locator('.fd-document-title').click();page.keyboard.press('Control+y');expect(panel.locator('.bp-breadcrumbs button')).to_have_count(1)
            panel.get_by_role('tab',name='논리 코드',exact=True).click();expect(doc.locator(f'[data-document-cell="{created}"]' if session_child else '[data-document-branch="case:positive"]')).to_be_visible();unchanged()
            page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(6)
            page=f.setup(browser);page.set_viewport_size({'width':1900,'height':1500});panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
            declaration=page.locator('.window[data-key=declaration]')
            if declaration.is_visible():declaration.locator('[data-close]').first.click()
            expect(doc.locator(f'[data-document-cell="{created}"]' if session_child else '[data-document-branch="case:positive"]')).to_be_visible();unchanged()
            if full_session:
                doc.locator('[data-document-branch="case:positive"]').click()
                expect(doc.locator(f'[data-document-cell="{branch_call}"] [data-document-value][data-document-port="field:amount"]')).to_have_text('37')
            mark=len(f.requests)
            if full_session:
                assert not any(row.get('endpoint')=='saveDraft' or row.get('endpoint')=='blueprint' and row.get('input',{}).get('action')=='authorBatch' for row in f.requests[before_composition:mark])
            if not full_clean:
                graph_path.write_bytes(original_graph+b' ')
                try:
                    panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
                    assert panel.locator('.bp-status').inner_text()!='저장됨' and graph_path.read_bytes()==original_graph+b' '
                    current=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'),None)
                    assert (current.read_bytes() if current else None)==checkpoint_before
                    expect(doc.locator(f'[data-document-cell="{created}"]' if session_child else '[data-document-branch="case:positive"]')).to_be_visible()
                finally:graph_path.write_bytes(original_graph)
                if full_session:
                    donor_declaration=manifest.parent/'LocalDonor.celem';donor_before=donor_declaration.read_bytes()
                    donor_declaration.write_bytes(donor_before.replace(b'int amount',b'long amount'))
                    try:
                        panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
                        assert panel.locator('.bp-status').inner_text()!='저장됨' and graph_path.read_bytes()==original_graph
                        current=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'),None)
                        assert (current.read_bytes() if current else None)==checkpoint_before
                        expect(doc.locator(f'[data-document-cell="{branch_call}"] [data-document-value][data-document-port="field:amount"]')).to_have_text('37')
                    finally:donor_declaration.write_bytes(donor_before)
                    print('PASS changed donor declaration blocks Save and retains typed call input',flush=True)
                if full_session and checkpoint is not None:
                    checkpoint.write_bytes(checkpoint_before+b' ')
                    try:
                        panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
                        assert panel.locator('.bp-status').inner_text()!='저장됨' and checkpoint.read_bytes()==checkpoint_before+b' ' and graph_path.read_bytes()==original_graph
                        expect(doc.locator(f'[data-document-cell="{branch_call}"] [data-document-value][data-document-port="field:amount"]')).to_have_text('37')
                    finally:checkpoint.write_bytes(checkpoint_before)
                    print('PASS conflicting checkpoint Save preserves call, value and originals',flush=True)
                if full_session:
                    # The real Save carries a name and intent for the new cell.
                    # Corrupt only the intent in flight; the atomic batch must
                    # leave neither field, the source, nor the checkpoint applied.
                    corruptions=[]
                    def invalid_presentation(route):
                        if route.request.method=='POST' and route.request.url.startswith(f.origin+'/'):
                            try:body=route.request.post_data_json
                            except Exception:body=None
                            if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
                                request=body.get('input',{})
                                if request.get('action')=='authorBatch':
                                    plan=request.get('edits',[{}])[0].get('definition',{}).get('childPlan')
                                    if plan and plan.get('creation'):
                                        intent=next(e for e in plan['creation'] if e['action']=='intent')
                                        intent['text']='x'*16385
                                        corruptions.append(True)
                                        route.continue_(post_data=json.dumps(body));return
                        route.fallback()
                    page.route('**/*',invalid_presentation)
                    try:
                        panel.locator('[data-bp-save]').click()
                        expect(panel.locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
                        assert corruptions and panel.locator('.bp-status').inner_text()!='저장됨'
                        unchanged()
                        current=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'),None)
                        assert (current.read_bytes() if current else None)==checkpoint_before
                        expect(doc.locator(f'[data-document-cell="{branch_call}"] [data-document-value][data-document-port="field:amount"]')).to_have_text('37')
                    finally:page.unroute('**/*',invalid_presentation)
                    print('PASS invalid paired intent rejects the entire Save and retains the UI input',flush=True)
            started=time.perf_counter();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000)
            print('TIMING combined wrap and branch Save ms',round((time.perf_counter()-started)*1000),flush=True)
            assert graph_path.read_bytes()==original_graph and retained_source.read_bytes()==retained_bytes
            if session_child:
                declare_first();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000)
            print('PASS wrap and child authored without intermediate Save; grouped Undo/Redo and cold recovery',flush=True)
            if not full_session:branch_id,branch_call=compose_case(True)
            else:
                accepted=[row for row in f.requests[mark:] if row.get('endpoint')=='blueprint' and row.get('input',{}).get('action')=='authorBatch']
                assert any(row['input']['edits'][0]['definition'].get('childPlan',{}).get('call') for row in accepted)
                if full_clean:assert len(accepted)==1
                print('PASS branch body, call and typed value in same unsaved work copy',flush=True)
            if not full_clean:
                r=review(page,panel.locator('[data-bp-complete]'));r.locator('[data-reject]').click();expect(r).to_be_hidden()
                r=review(page,panel.locator('[data-bp-complete]'));retained_source.write_bytes(retained_bytes+b' ')
                try:
                    r.locator('#confirm').click();page.evaluate('async()=>await confectoryFlushPresentation()');expect(r).to_be_visible()
                    assert graph_path.read_bytes()==original_graph
                finally:retained_source.write_bytes(retained_bytes)
                r.locator('[data-reject]').click();expect(r).to_be_hidden()
            confirm_mark=len(f.requests)
            r=review(page,panel.locator('[data-bp-complete]'));started=time.perf_counter();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);print('TIMING final confirm ms',round((time.perf_counter()-started)*1000),flush=True)
            if full_clean:assert sum(row.get('endpoint')=='confirmGroup' for row in f.requests[confirm_mark:])==1
            assert retained_source.read_bytes()==retained_bytes
            assert all(Path(p).read_bytes()==old for p,old in f.before.items() if Path(p).is_relative_to(f.projects[1].parent))
            if full_session:
                saved_graph=json.loads(graph_path.read_bytes())
                def descendants(graph):
                    for node in graph['nodes']:
                        yield node
                        if node.get('graph'):yield from descendants(node['graph'])
                by_id={node['id']:node for node in descendants(saved_graph)}
                plan=accepted[-1]['input']['edits'][0]['definition']['childPlan']
                for field in ('creation','body'):
                    for edit in plan[field]:
                        if edit['action'] in ('rename','intent'):
                            assert by_id[edit['node']]['displayName' if edit['action']=='rename' else 'intent']==edit['text']
                print('PASS paired name and intent both persist in the committed graph',flush=True)
            print('PASS same draft continued through actual branch body and reference, one final Confirm' if full_clean else 'PASS same draft continued through actual branch body and reference, final stale refusal and Confirm',flush=True)
        elif compound:
            page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(5)
            page=f.setup(browser);page.set_viewport_size({'width':1800,'height':1200});panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
            graph_path=next(manifest.parent.glob('blueprints/*.graph.json'))
            original_graph=graph_path.read_bytes()
            retained_source=graph_path.parent/json.loads(original_graph)['nodes'][0]['implementation'];retained_bytes=retained_source.read_bytes()
            start=doc.locator('[data-document-internal=body]');expect(start).to_be_enabled();wrap_requests=len(f.requests);started=time.perf_counter();start.click()
            try:expect(panel.locator('.bp-breadcrumbs')).to_be_visible(timeout=20000)
            except Exception:
                print('internalize failure:',panel.locator('.bp-status').inner_text(),flush=True);raise
            panel.get_by_role('tab',name='논리 코드',exact=True).click()
            expect(doc.locator('[data-document-cell=body]')).to_be_visible();expect(panel.locator('.bp-breadcrumbs button')).to_have_count(1);print('TIMING wrap editable ms',round((time.perf_counter()-started)*1000),flush=True)
            wrap_calls=[r['input'] for r in f.requests[wrap_requests:] if r.get('endpoint')=='blueprint' and r.get('input',{}).get('action') in ('read','previewNodeInternal')]
            assert len([r for r in wrap_calls if r.get('action')=='previewNodeInternal'])==1 and any(r.get('action')=='previewNodeInternal' and r.get('observedSources') and r.get('observedCheckpoint') for r in wrap_calls), [(r.get('action'),bool(r.get('observedSources'))) for r in wrap_calls]
            print('PASS direct root wrapping uses one bound preview request; concurrent reads:',sum(r.get('action')=='read' for r in wrap_calls),flush=True)
            doc.locator('.fd-document-title').click();page.keyboard.press('Control+z');expect(doc.locator('[data-document-internal=body]')).to_be_visible();expect(panel.locator('.bp-breadcrumbs button')).to_have_count(0)
            assert graph_path.read_bytes()==original_graph
            doc.locator('.fd-document-title').click();page.keyboard.press('Control+y');expect(panel.locator('.bp-breadcrumbs button')).to_have_count(1)
            panel.get_by_role('tab',name='논리 코드',exact=True).click()
            started=time.perf_counter();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);print('TIMING checkpoint save ms',round((time.perf_counter()-started)*1000),flush=True)
            if not staged:
                r=review(page,panel.locator('[data-bp-complete]'));started=time.perf_counter();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);print('TIMING confirm ms',round((time.perf_counter()-started)*1000),flush=True)
            def effective_graph():
                if staged:
                    checkpoint=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'))
                    return json.loads(next(row['draft'] for row in json.loads(checkpoint.read_bytes())['changes'] if row['kind']=='blueprint' and row['id'].startswith(target)))
                return json.loads(graph_path.read_text())
            # The default new feature uses the switch-capable profile even before
            # any selector is created. Its newly wrapped body must be editable.
            graph=effective_graph();wrapped_graph=json.loads(json.dumps(graph));frame=next(n['graph'] for n in graph['nodes'] if n['id']=='body')
            assert graph['profile']==frame['profile']=='sync-acyclic-switch-v1'
            if not staged:
                page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(6)
                page=f.setup(browser);page.set_viewport_size({'width':1800,'height':1200});panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
            expect(panel.locator('.bp-breadcrumbs button')).to_have_count(1)
            declaration=page.locator('.window[data-key=declaration]')
            if not staged and declaration.is_visible():declaration.locator('[data-close]').first.click()
            old_graph=graph_path.read_bytes()
            add=doc.locator('[data-document-add="$entry"]');expect(add).to_be_enabled();started=time.perf_counter();add.click()
            cell=doc.locator('[data-document-cell^="cell_"]');expect(cell).to_be_visible();created=cell.get_attribute('data-document-cell');print('TIMING compound child add visible ms',round((time.perf_counter()-started)*1000),flush=True)
            doc.press('Control+z');expect(cell).to_have_count(0);doc.press('Control+y');expect(cell).to_be_visible()
            cell.locator('[data-document-code]').click();script=page.locator('.bp-script-dialog');source=script.locator('[data-code-source]')
            body=script.locator('[data-code-region=body]').text_content()
            source.evaluate('(el,body)=>{let at=el.value.indexOf(body);el.focus();el.setSelectionRange(at,at+body.length)}',body)
            page.keyboard.insert_text('System.IO.File.WriteAllText('+json.dumps(str(donor_marker))+', "37"); return;')
            script.locator('[data-code-save]').click();expect(script).to_be_hidden()
            checkpoint=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
            graph_path.write_bytes(old_graph+b' ')
            try:
                panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
                assert panel.locator('.bp-status').inner_text()!='저장됨' and checkpoint.read_bytes()==before and graph_path.read_bytes()==old_graph+b' '
                expect(cell).to_be_visible()
            finally:graph_path.write_bytes(old_graph)
            page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(10)
            page=f.setup(browser);page.set_viewport_size({'width':1800,'height':1200});panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
            expect(doc.locator(f'[data-document-cell="{created}"]')).to_be_visible()
            started=time.perf_counter();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);print('TIMING checkpoint save ms',round((time.perf_counter()-started)*1000),flush=True)
            if not staged:
                r=review(page,panel.locator('[data-bp-complete]'));r.locator('[data-reject]').click();expect(r).to_be_hidden();assert graph_path.read_bytes()==old_graph
                r=review(page,panel.locator('[data-bp-complete]'));started=time.perf_counter();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);print('TIMING confirm ms',round((time.perf_counter()-started)*1000),flush=True)
            else:assert graph_path.read_bytes()==original_graph
            graph=effective_graph();frame=next(n['graph'] for n in graph['nodes'] if n['id']=='body');assert frame['entry']==created
            assert {'from':created,'port':'next','to':'body'} in frame['edges']
            frame['nodes']=[n for n in frame['nodes'] if n['id']!=created];frame['edges']=[e for e in frame['edges'] if e['from']!=created];frame['entry']='body'
            assert graph==wrapped_graph and retained_source.read_bytes()==retained_bytes
            print('PASS created feature to compound, structural Undo/Redo, new child source, stale refusal and cold retry',flush=True)
            if branch_mode:
                def reopen(index):
                    page.evaluate('async()=>await confectoryFlushPresentation()');page.close();f.stop();f.start(index)
                    new_page=f.setup(browser);new_page.set_viewport_size({'width':1900,'height':1500})
                    new_panel=new_page.locator('.window[data-key=blueprint]');new_doc=new_panel.locator('.function-document')
                    expect(new_panel.locator('.bp-breadcrumbs')).to_be_visible()
                    declaration=new_page.locator('.window[data-key=declaration]')
                    if declaration.is_visible():declaration.locator('[data-close]').first.click()
                    return new_page,new_panel,new_doc
                def save_confirm():
                    started=time.perf_counter();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);print('TIMING checkpoint save ms',round((time.perf_counter()-started)*1000),flush=True)
                    if not staged:
                        r=review(page,panel.locator('[data-bp-complete]'));started=time.perf_counter();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);print('TIMING confirm ms',round((time.perf_counter()-started)*1000),flush=True)
                    else:assert graph_path.read_bytes()==original_graph
                def replace_body(text):
                    script=page.locator('.bp-script-dialog');source=script.locator('[data-code-source]');expect(source).to_be_visible()
                    source.evaluate('''el=>{const spans=Array.from(el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight] > span'));const idx=spans.findIndex(s=>s.dataset.codeRegion==='body');if(idx<0)throw Error('Missing body');const start=spans.slice(0,idx).reduce((a,b)=>a+b.textContent.length,0);el.focus();el.setSelectionRange(start,start+spans[idx].textContent.length)}''')
                    page.keyboard.insert_text(text);script.locator('[data-code-save]').click();expect(script).to_be_hidden()
                if not staged:page,panel,doc=reopen(20)
                first_branch=doc.locator(f'[data-document-call-first-branch="{created}"]');expect(first_branch).to_be_visible();first_branch.click()
                old_path=graph_path.read_bytes();checkpoint_before=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()
                page.locator('.bp-script-dialog [data-code-cancel]').click();expect(first_branch).to_be_visible()
                first_branch.click()
                mode_marker=f.root/'private-case-mode.txt'
                replace_body('var mode=System.IO.File.ReadAllText('+json.dumps(str(mode_marker))+'); return mode=="positive"?Result.Positive:mode=="negative"?Result.Negative:Result.NoBranch;')
                expect(doc.locator('[data-document-branch="case:positive"]')).to_be_visible()
                doc.press('Control+z');expect(doc.locator('[data-document-branch="case:positive"]')).to_have_count(0)
                doc.press('Control+y');expect(doc.locator('[data-document-branch="case:positive"]')).to_be_visible()
                graph_path.write_bytes(old_path+b' ')
                try:
                    panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).not_to_have_text('저장 중…',timeout=120000)
                    assert panel.locator('.bp-status').inner_text()!='저장됨' and next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==checkpoint_before
                finally:graph_path.write_bytes(old_path)
                page,panel,doc=reopen(21)
                started=time.perf_counter();panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);print('TIMING checkpoint save ms',round((time.perf_counter()-started)*1000),flush=True)
                if not staged:
                 r=review(page,panel.locator('[data-bp-complete]'))
                 selector_source=graph_path.parent/next(n['implementation'] for n in json.loads(old_path)['nodes'][0]['graph']['nodes'] if n['id']==created)
                 selector_raw=selector_source.read_bytes();saved_checkpoint=next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes();selector_source.write_bytes(selector_raw+b' ')
                 try:
                     mark=len(f.requests);r.locator('#confirm').click();page.evaluate('async()=>await confectoryFlushPresentation()')
                     expect(r).to_be_visible();assert any(row.get('endpoint')=='confirmGroup' for row in f.requests[mark:])
                     assert graph_path.read_bytes()==old_path and selector_source.read_bytes()==selector_raw+b' ' and next(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==saved_checkpoint
                 finally:selector_source.write_bytes(selector_raw)
                 if r.is_visible():r.locator('[data-reject]').click();expect(r).to_be_hidden()
                 r=review(page,panel.locator('[data-bp-complete]'));started=time.perf_counter();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);print('TIMING confirm ms',round((time.perf_counter()-started)*1000),flush=True)
                committed=effective_graph();child=committed['nodes'][0]['graph'];selector=next(n for n in child['nodes'] if n['id']==created)
                assert selector['control']=='switch' and {e['port']:e['to'] for e in child['edges'] if e['from']==created}=={'next':'body','case:positive':'return:'+created,'case:negative':'return:'+created}
                if not staged:page,panel,doc=reopen(22)
                doc.locator('[data-document-branch="case:positive"]').click();case=doc.locator('[data-document-panel="case:positive"]')
                add=case.locator('[data-document-branch-add]');expect(add).to_be_enabled();add.click()
                branch_cell=case.locator('[data-document-cell^="cell_"]');expect(branch_cell).to_be_visible();branch_id=branch_cell.get_attribute('data-document-cell');assert branch_id!=created
                branch_marker=f.root/'private-case-marker.txt'
                branch_cell.locator('[data-document-code]').click();replace_body('System.IO.File.WriteAllText('+json.dumps(str(branch_marker))+', "positive");return;')
                save_confirm()
                if not staged:page,panel,doc=reopen(23)
                doc.locator('[data-document-branch="case:positive"]').click();case=doc.locator('[data-document-panel="case:positive"]')
                add=case.locator(f'[data-document-insert-call="{branch_id}"]');expect(add).to_be_enabled();add.click()
                page.get_by_role('dialog',name='블루프린트 노드 검색').locator(f'[data-resource-feature="{donor}"]').click()
                call_cell=case.locator('[data-document-cell^="call_"]');expect(call_cell).to_be_visible();branch_call=call_cell.get_attribute('data-document-cell')
                value=call_cell.locator('[data-document-value][data-document-port="field:amount"]');value.click();search=page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');search.fill('37');search.press('Enter')
                expect(value).to_have_text('37');save_confirm()
                if staged:
                    assert graph_path.read_bytes()==original_graph and retained_source.read_bytes()==retained_bytes
                    r=review(page,panel.locator('[data-bp-complete]'));r.locator('[data-reject]').click();expect(r).to_be_hidden()
                    r=review(page,panel.locator('[data-bp-complete]'));retained_source.write_bytes(retained_bytes+b' ')
                    try:
                        mark=len(f.requests);r.locator('#confirm').click();page.evaluate('async()=>await confectoryFlushPresentation()');expect(r).to_be_visible()
                        assert graph_path.read_bytes()==original_graph and any(row.get('endpoint')=='confirmGroup' for row in f.requests[mark:])
                    finally:retained_source.write_bytes(retained_bytes)
                    if r.is_visible():r.locator('[data-reject]').click();expect(r).to_be_hidden()
                    r=review(page,panel.locator('[data-bp-complete]'));started=time.perf_counter();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);print('TIMING confirm ms',round((time.perf_counter()-started)*1000),flush=True)
                    print('PASS all intermediate Saves remained in one unconfirmed retained group',flush=True)
                page,panel,doc=reopen(24)
                doc.locator('[data-document-branch="case:positive"]').click();expect(doc.locator(f'[data-document-cell="{branch_call}"]')).to_be_visible()
                final=json.loads(graph_path.read_text());frame=final['nodes'][0]['graph'];assert next(n for n in frame['nodes'] if n['id']==branch_call)['arguments']=={'amount':{'constant':37}}
                assert final['nodes'][0]['retainedCode']==committed['nodes'][0]['retainedCode'] and next(n for n in frame['nodes'] if n['kind']=='export')==next(n for n in child['nodes'] if n['kind']=='export')
                assert retained_source.read_bytes()==retained_bytes
                print('PASS first private branch declaration, explicit empty returns, stale refusal, general cell and typed call in case, exact retained return',flush=True)

        if not compound:
         # Add a typed published feature from the Logic Code view itself,
         # without switching to Blueprint or manually reconnecting execution.
         add = doc.locator('[data-document-insert-call="$entry"]')
         expect(add).to_be_enabled()
         add.click()
         picker = page.get_by_role('dialog', name='블루프린트 노드 검색')
         candidate = picker.locator(f'[data-resource-feature="{donor}"]')
         expect(candidate).to_be_visible()
         picker.locator('[data-resource-close]').click()
         expect(doc.locator('[data-document-cell^="call_"]')).to_have_count(0)
         add.click()
         expect(candidate).to_be_visible()
         candidate.click()
         call_cell = doc.locator('[data-document-cell^="call_"]')
         expect(call_cell).to_be_visible()
         call_id = call_cell.get_attribute('data-document-cell')
         assert doc.locator('[data-document-cell]').evaluate_all('(cells)=>cells.map(c=>c.dataset.documentCell)')[:3] == ['$entry',call_id,'body']
         doc.press('Control+z')
         expect(call_cell).to_have_count(0)
         doc.press('Control+y')
         expect(call_cell).to_be_visible()
         value = call_cell.locator('[data-document-value][data-document-port="field:amount"]')
         value.click()
         values = page.get_by_role('dialog', name='핀 값 선택')
         if early:
             values.get_by_role('button',name='입력 · input1',exact=True).click()
             expect(value).to_contain_text('input1')
         else:
             values.get_by_role('searchbox', name='값 검색').fill('37')
             values.get_by_role('searchbox', name='값 검색').press('Enter')
             expect(value).to_have_text('37')
         if early:
             f.original()
             candidate_path=manifest.parent/'LocalDonor.celem'
             original=candidate_path.read_bytes()
             candidate_path.write_bytes(original+b' ')
             try:
                 panel.locator('[data-bp-save]').click()
                 expect(panel.locator('.bp-status')).to_contain_text('모든 입력은 유지됩니다.',timeout=30000)
                 assert not list(manifest.parent.glob('blueprints/*.graph.json'))
                 assert not list(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'))
                 assert candidate_path.read_bytes()==original+b' '
             finally:
                 candidate_path.write_bytes(original)
             page.evaluate('async()=>await confectoryFlushPresentation()')
             page.close();f.stop();f.start(10)
             page=f.setup(browser);page.set_viewport_size({'width':1800,'height':1200})
             panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
             expect(doc.locator(f'[data-document-cell="{call_id}"]')).to_be_visible()
             expect(doc.locator(f'[data-document-value="{call_id}"][data-document-port="field:amount"]')).to_contain_text('input1')
             f.original()
         panel.locator('[data-bp-save]').click()
         expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
         if early:
             f.original()
         r = review(page,panel.locator('[data-bp-complete]'))
         r.locator('[data-reject]').click()
         expect(r).to_be_hidden()
         r = review(page,panel.locator('[data-bp-complete]'))
         r.locator('#confirm').click()
         expect(r).to_be_hidden(timeout=120000)
         graph_path = next(manifest.parent.glob('blueprints/*.graph.json'))
         graph = json.loads(graph_path.read_text())
         if early:
             declaration_path=next(manifest.parent.rglob(name+'.celem'))
             assert '(int input1) -> long' in declaration_path.read_text()
         assert graph['feature'] == target and graph['entry'] == call_id
         assert {'from':call_id,'port':'next','to':'body'} in graph['edges']
         call = next(node for node in graph['nodes'] if node['id']==call_id)
         assert call['kind']=='call' and call['feature']==donor and call['arguments']=={'amount':{'input':'input1'} if early else {'constant':37}}
         assert all((manifest.parent / file).read_text()==source for file,source in donor_sources.items())
         assert donor not in f.projects[1].read_text()
         print('PASS actual Logic Code feature insertion, value binding, Undo/Redo and Review/Confirm', flush=True)
        page.close()
        f.stop()

        # Restore the same authored project and editor presentation before running.
        f.start(1)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        restored = page.locator('.window[data-key=blueprint] .function-document')
        if compound:expect(restored.locator(f'[data-document-cell="{created}"]')).to_be_visible()
        else:
            expect(restored.locator(f'[data-document-cell="{call_id}"]')).to_be_visible()
            expect(restored.locator(f'[data-document-value="{call_id}"][data-document-port="field:amount"]')).to_contain_text('input1' if early else '37')
        page.close()
        f.stop()
        print('PASS cold restart restores the committed compound child' if compound else 'PASS cold restart restores the committed call and typed input', flush=True)

        # The tested authoring product has no new test-only execution action.
        # Select the committed function as the ordinary entry in a separate
        # synthetic copy, without modifying any authored function or original project.
        pdir = f.root / 'new function execution harness'
        shutil.copytree(f.projects[0].parent, pdir, ignore=shutil.ignore_patterns('.confectory', '.build'))
        manifest = pdir / f.projects[0].name
        text, count = re.subn(r'\bentry\s+[^;]+;', f'entry {target};', manifest.read_text(), count=1)
        assert count == 1
        if early:
            # Execution harness uses the ordinary entry with the new input contract.
            text=text.replace('entry '+target+';', 'entry Example.FrameLoop::Main;')
            (pdir/'MainBody.celem').write_text(
                'implementation Example.FrameLoop::MainBody for Example.FrameLoop::Main () -> int {import '+target+' as Probe (int) -> long;body common "Main.csbody";}')
            (pdir/'Main.csbody').write_text('return checked((int)calls.Probe.Invoke(37));')
        if branch_mode:
            text=text.replace('entry '+target+';', 'entry Example.FrameLoop::Main;')
            (pdir/'MainBody.celem').write_text('implementation Example.FrameLoop::MainBody for Example.FrameLoop::Main () -> int {import '+target+' as Probe () -> int;body common "Main.csbody";}')
            execution_marker=f.root/'private-case-execution.txt'
            mode_path=json.dumps(str(mode_marker));donor_path=json.dumps(str(donor_marker));branch_path=json.dumps(str(branch_marker))
            (pdir/'Main.csbody').write_text('foreach(string mode in new[]{"positive","negative","primary"}) {System.IO.File.WriteAllText('+mode_path+',mode);System.IO.File.Delete('+donor_path+');System.IO.File.Delete('+branch_path+');if(calls.Probe.Invoke()!=0)return 81;if(mode=="positive"){if(System.IO.File.ReadAllText('+donor_path+')!="37"||System.IO.File.ReadAllText('+branch_path+')!="positive")return 82;}else if(System.IO.File.Exists('+donor_path+')||System.IO.File.Exists('+branch_path+'))return 83;}System.IO.File.WriteAllText('+json.dumps(str(execution_marker))+',"positive,negative,primary");return 0;')
        manifest.write_text(text)
        f.env['CONFECTORY_WEB_PROJECT'] = str(manifest)
        f.start(2)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        run_started=time.perf_counter()
        run_from_dock(page, marker, 'new function executed')
        print('TIMING Run to observed output ms',round((time.perf_counter()-run_started)*1000),flush=True)
        if branch_mode:assert execution_marker.read_text()=='positive,negative,primary'
        else:assert donor_marker.read_text() == '37'
        assert not f.errors and not f.external, (f.errors, f.external)
        print('PASS ordinary editor Run in isolated entry harness executes the newly authored feature', flush=True)
        page.close()
finally:
    f.stop()
    print('evidence', f.root, flush=True)
