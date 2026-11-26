"""Restore three owned windows using the initial status already read by the host."""
import sys,time,json
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from editor_navigation import goto_editor

f, d = r.fixture, r.fallback
r.seed()
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
expect.set_options(timeout=60000)
close_mode=mode in ('primary-close-restore','primary-close-persist')
partial_modes={'partial-middle':[d.PEER],'partial-first':[d.TARGET],'partial-two':[d.TARGET,d.PEER],'partial-reuse':[d.PEER]}
partial_mode=mode in partial_modes
primary_mode=mode in ('primary','primary-after-save','primary-save-own','primary-fallback','primary-external-during','missing-primary') or close_mode or partial_mode
save_mode=mode in ('after-save','primary-after-save','primary-save-own') or close_mode or partial_mode
try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as b:
        f.start(0)
        page = f.setup(b)
        page.set_viewport_size({'width': 2000, 'height': 1200})
        if primary_mode:
            # The primary and detached owners are distinct. Open the primary
            # before filling all three detached slots, avoiding a duplicate UI target.
            browser=r.browser_window(page)
            r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder2"]')
            r.search(browser,d.LABEL,'Extra2')
            browser.locator(f'[data-object="{d.NS}::Extra2"]').click(button='right')
            page.locator(".context-menu").get_by_role("button", name="스키마 열기", exact=True).click()
            primary=page.locator('.window[data-key="schema"]')
            expect(r.floating.property_value(primary,'Note')).to_have_value(d.FIRST+' Extra2')
            if close_mode:r.floating.property_value(primary,'Note').fill('Retained primary close input')
            if mode=='primary-save-own':r.floating.property_value(primary,'Note').fill('Retained primary Extra2')
        notes = {}
        for name, folder in [(d.TARGET, 'StockFolder'), (d.PEER, 'PeerFolder'), ('Extra1', 'ExtraFolder1')]:
            window, key = r.floating.open_properties(page, name, folder)
            value = 'Retained local ' + name
            r.floating.property_value(window, 'Note').fill(value)
            notes[key] = (f'{d.NS}::{name}', value)
        if mode in ('stale','detached-close-restore'):
            # A retained dirty working copy deliberately exercises the ordinary
            # host admission fallback instead of the clean local read model.
            window.locator('[data-element-action="save"]').click()
            expect(page.locator('#project-menu')).to_be_enabled()
        geometry={key:page.locator(f'.window[data-key="{key}"]').bounding_box() for key in notes} if close_mode or partial_mode else {}
        saved_id=f.state()['draft']['id']
        if primary_mode:assert saved_id==d.NS+'::Extra2',saved_id
        page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
        page.evaluate('()=>confectoryFlushPresentation()')
        page.close()
        f.stop()
        # Real outside edit after the original session has stopped.
        schema = f.projects[0].parent / 'private-source-StockInfo.celem'
        if not save_mode:
            schema.write_text(schema.read_text().rstrip()[:-1] + ' field RestartFlag single general string;\n}\n')
            f.before[str(schema)] = schema.read_bytes()
        if mode=='missing-primary':
            manifest=f.projects[0]
            marker='element Extra2 object "private-source-Extra2.celem";'
            assert marker in manifest.read_text()
            manifest.write_text(manifest.read_text().replace(marker,''))
            f.before[str(manifest)]=manifest.read_bytes()
        if partial_mode:
            manifest=f.projects[0]
            text=manifest.read_text()
            for name in partial_modes[mode]:
                marker=f'element {name} object "private-source-{name}.celem";'
                assert marker in text
                text=text.replace(marker,'')
            manifest.write_text(text)
            f.before[str(manifest)]=manifest.read_bytes()
        f.env.pop('CONFECTORY_WEB_PROJECT', None)
        f.start(1)
        page = b.new_page(viewport={'width': 2000, 'height': 1200})
        invokes = []
        held=[]
        def intercept(route):
            if not route.request.url.startswith(f.origin + '/'):
                route.abort()
                return
            if route.request.method == 'POST':
                req = route.request.post_data_json
                if req.get('op') == 'invoke':
                    invokes.append(req)
                    if mode=='primary-fallback' and req.get('endpoint')=='preparePropertyModels' and req.get('input',{}).get('restoreStatuses'):
                        # Exercise an actual host response without the optional
                        # restore status proof (older endpoint contract).
                        request=dict(req,input={k:v for k,v in req['input'].items() if k!='restoreStatuses'})
                        route.continue_(post_data=json.dumps(request));return
                    if (close_mode or mode=='primary-external-during') and req.get('endpoint')=='preparePropertyModels' and not held:
                        held.append(route);return
                    if mode in ('stale','detached-close-restore') and req.get('endpoint')=='openEditorView' and req.get('input',{}).get('view')=='2' and not held:
                        held.append(route);return
            route.continue_()
        page.route('**/*', intercept)
        goto_editor(page, f.url)
        page.locator('.project-card').filter(has=page.get_by_role('heading', name=d.FIRST, exact=True)).locator('[data-enter]').click()
        if partial_mode:
            failed_ids={d.NS+'::'+name for name in partial_modes[mode]}
            valid={key:(identifier,value) for key,(identifier,value) in notes.items() if identifier not in failed_ids}
            failed={key:(identifier,value) for key,(identifier,value) in notes.items() if identifier in failed_ids}
            expect(page.locator('#status')).to_contain_text('편집창 복원 실패')
            expect(page.locator('#project-menu')).to_be_enabled()
            print('visible property owners',page.locator('.window[data-element-owner]:visible').evaluate_all('rows=>rows.map(w=>w.dataset.elementOwner)'),flush=True)
            for key,(identifier,value) in valid.items():
                window=page.locator(f'.window[data-key="{key}"]')
                expect(window).to_be_visible(timeout=5000)
                expect(r.floating.property_value(window,'Note')).to_have_value(value)
                assert window.get_attribute('data-element-owner')==identifier
                box=window.bounding_box()
                assert all(abs(box[field]-geometry[key][field])<=2 for field in ('x','y','width','height')),(key,box,geometry[key])
            for key in failed:expect(page.locator(f'.window[data-key="{key}"]')).to_be_hidden()
            expect(page.locator('#status')).to_contain_text('일부 편집창 복원 실패')
            assert not failed_ids.intersection(row['id'] for row in f.state()['editorViews'])
            # A manual/non-restoration request still rejects the missing owner.
            failed_key,(failed_owner,_)=next(iter(failed.items()))
            f.call('openEditorView',{'view':failed_key.removeprefix('editor-'),'id':failed_owner,'viewMode':'properties'},ok=False)
            occupied=next(iter(valid))
            # The restore classification cannot replace a differently bound slot.
            f.call('openEditorView',{'view':occupied.removeprefix('editor-'),'id':failed_owner,'viewMode':'properties','restoreSaved':True},ok=False)
            assert not failed_ids.intersection(row['id'] for row in f.state()['editorViews'])
            print('PASS missing registration does not block following valid owners',flush=True)
            key=next(key for key,(identifier,_) in valid.items() if identifier==d.NS+'::Extra1')
            target=page.locator(f'.window[data-key="{key}"]')
            note=r.floating.property_value(target,'Note')
            note.click()
            assert page.evaluate('document.activeElement.closest(".window")?.dataset.key')==key
            changed='Saved following valid window '+mode
            note.fill(changed)
            source=f.projects[0].parent/'private-source-Extra1.celem'
            assert source.read_bytes()==f.before[str(source)]
            marker=len(invokes)
            target.locator('[data-element-action="confirm"]').click()
            expect(page.locator('#status')).to_have_text('저장했습니다.',timeout=120000)
            expect(page.locator('#project-menu')).to_be_enabled()
            assert f'data Note = "{changed}"' in source.read_text()
            f.before[str(source)]=source.read_bytes()
            calls=[req['endpoint'] for req in invokes[marker:]]
            assert calls.count('reviewGroup')==calls.count('confirmGroup')==1,calls
            valid[key]=(valid[key][0],changed)
            schema.write_text(schema.read_text().rstrip()[:-1]+' field AfterPartialFlag single general string;\n}\n')
            f.before[str(schema)]=schema.read_bytes()
            rows=f.state()['editorViews']
            row=next(row for row in rows if row['id']==d.NS+'::Extra1')
            f.call('browserDrafts',{'action':'status','view':row['view'],'id':row['id'],'ids':[row['id']]})
            for key,(identifier,value) in valid.items():
                window=page.locator(f'.window[data-key="{key}"]')
                expect(d.field(window,'AfterPartialFlag')).to_be_visible()
                expect(r.floating.property_value(window,'Note')).to_have_value(value)
            if mode=='partial-reuse':
                replacement,replacement_key=r.floating.open_properties(page,'Extra2','ExtraFolder2')
                assert replacement_key in failed
                replacement_value='New input in reused slot'
                r.floating.property_value(replacement,'Note').fill(replacement_value)
                valid[replacement_key]=(d.NS+'::Extra2',replacement_value)
            page.evaluate('()=>confectoryFlushPresentation()')
            presentations=[json.loads(path.read_text()) for path in (f.root/'profile'/'presentations').glob('*.json')]
            presentation=next(row for row in presentations if any(binding['id']==d.NS+'::Extra1' for binding in row.get('editorBindings',[])))
            if mode=='partial-reuse':
                assert any(binding['id']==d.NS+'::Extra2' and binding['view']==replacement_key.removeprefix('editor-') for binding in presentation['editorBindings'])
                assert not failed_ids.intersection(binding['id'] for binding in presentation['editorBindings'])
            else:assert failed_ids.issubset(binding['id'] for binding in presentation['editorBindings'])
            for _,(identifier,value) in failed.items():
                assert any(identifier in key and value==entry.get('text') for key,entry in presentation['inputs']['schema'])
            f.original()
            page.close();f.stop();f.start(2)
            page=b.new_page(viewport={'width':2000,'height':1200})
            page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort())
            goto_editor(page,f.url)
            page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').click()
            expect(page.locator('#project-menu')).to_be_enabled()
            for key,(identifier,value) in valid.items():
                window=page.locator(f'.window[data-key="{key}"]')
                expect(r.floating.property_value(window,'Note')).to_have_value(value)
                assert window.get_attribute('data-element-owner')==identifier
            for key in failed:
                if key not in valid:expect(page.locator(f'.window[data-key="{key}"]')).to_be_hidden()
            page.locator('.brand').click()
            expect(page.locator('.home-grid')).to_be_visible()
            page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.SECOND,exact=True)).locator('[data-enter]').click()
            browser=r.browser_window(page)
            r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder1"]')
            r.search(browser,d.LABEL,'Extra1')
            browser.locator(f'[data-object="{d.NS}::Extra1"]').click(button='right')
            page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
            other=page.locator(f'.window[data-element-owner="{d.NS}::Extra1"][data-element-mode="properties"]:visible')
            expect(r.floating.property_value(other,'Note')).to_have_value(d.SECOND+' Extra1')
            f.original()
            print('PASS partial restoration saves exact owner, preserves failed input, restarts and isolates projects',flush=True)
            raise SystemExit(0)
        if mode=='primary-external-during':
            deadline=time.monotonic()+30
            while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
            assert len(held)==1
            try:
                primary=page.locator('.window[data-key="schema"]')
                expect(d.field(primary,'RestartFlag')).to_be_visible()
                schema.write_text(schema.read_text().rstrip()[:-1]+' field DuringRestoreFlag single general string;\n}\n')
                f.before[str(schema)]=schema.read_bytes()
            finally:held[0].continue_()
        if close_mode:
            deadline=time.monotonic()+30
            while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
            assert len(held)==1
            primary=page.locator('.window[data-key="schema"]')
            try:
                expect(primary).to_be_visible()
                primary.get_by_role('button',name='창 닫기',exact=True).click()
                expect(primary).to_be_hidden()
                # Home navigation cannot race the in-progress restore.
                try:page.locator('.brand').click(timeout=1500)
                except PlaywrightTimeoutError:pass
                expect(page.locator('.work-body')).to_be_visible()
                expect(page.locator('#title')).to_contain_text(d.FIRST)
            finally:held[0].continue_()
        if mode=='missing-primary':
            expect(page.locator('.work-body')).to_be_visible()
            expect(page.locator('#title')).to_contain_text(d.FIRST)
            expect(page.locator('#status')).to_contain_text('실제 편집창 복원 실패')
            f.original()
            print('PASS missing saved primary owner retains the project and reports recovery failure',flush=True)
            raise SystemExit(0)
        if mode=='detached-close-restore':
            deadline=time.monotonic()+30
            while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
            assert len(held)==1
            key=next(key for key,(identifier,_) in notes.items() if identifier==d.NS+'::'+d.TARGET)
            target=page.locator(f'.window[data-key="{key}"]')
            try:
                expect(target).to_be_visible(timeout=5000)
                target.get_by_role('button',name='창 닫기',exact=True).click()
                expect(target).to_be_hidden()
            finally:held[0].continue_()
            expect(page.locator('#project-menu')).to_be_enabled()
            expect(target).to_be_hidden(timeout=3000)
            for peer,(identifier,value) in notes.items():
                if peer!=key:
                    window=page.locator(f'.window[data-key="{peer}"]')
                    expect(window).to_be_visible()
                    expect(r.floating.property_value(window,'Note')).to_have_value(value)
            r.drag(page,d.TARGET,'StockFolder')
            expect(target).to_be_visible()
            expect(r.floating.property_value(target,'Note')).to_have_value(notes[key][1])
            f.original()
            print('PASS retained detached window closes during next admission and reopens with input',flush=True)
            raise SystemExit(0)
        if mode=='stale':
            deadline=time.monotonic()+30
            while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
            assert len(held)==1
            # Advance the actual shared revision without changing the cursor or source.
            try:f.call('browserDrafts',{'action':'status','ids':[saved_id]})
            finally:held[0].continue_()
        expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(3)
        expect(page.locator('#project-menu')).to_be_enabled()
        if close_mode:
            expect(primary).to_be_hidden(timeout=3000)
            print('PASS completed restore does not reopen the explicitly closed primary',flush=True)
            # Other restored windows retain geometry and are real, editable owners.
            for key,box in geometry.items():
                actual=page.locator(f'.window[data-key="{key}"]').bounding_box()
                assert actual and all(abs(actual[field]-box[field])<=2 for field in ('x','y','width','height')),(key,box,actual)
        for key, (identifier, value) in notes.items():
            window = page.locator(f'.window[data-key="{key}"]')
            expect(r.floating.property_value(window, 'Note')).to_have_value(value)
            if not save_mode:expect(d.field(window, 'RestartFlag')).to_be_visible()
            assert window.get_attribute('data-element-owner') == identifier
        opens = [req for req in invokes if req.get('endpoint') == 'openEditorView']
        status = [req for req in invokes if req.get('endpoint') == 'browserDrafts' and req.get('input',{}).get('view')]
        if mode=='stale':
            assert len(opens)>=4, opens
        else:
            # Clean restoration can use one shared preparation rather than a
            # separate host view admission for every visible window.
            assert len(opens) in (0,3), opens
            if not opens:assert any(req.get('endpoint')=='preparePropertyModels' for req in invokes)
        if mode=='stale':
            attempts=[req['expectedRevision'] for req in opens if req['input']['view']=='2']
            assert len(attempts)>=2 and attempts[0]!=attempts[-1],attempts
            print('actual stale restore admission revisions',attempts,flush=True)
        if mode=='normal':
            # The first visible Browser projection needs both views of the same
            # project. The combined read must replace the separate map command.
            projections=[req for req in invokes if req.get('endpoint')=='localInventory' and req.get('input',{}).get('relations')]
            assert len(projections)==1, projections
            assert not any(req.get('endpoint')=='relationsMap' for req in invokes), invokes
        if mode=='primary-close-persist':
            page.evaluate('()=>confectoryFlushPresentation()')
            page.close()
            f.stop()
            f.start(2)
            page=b.new_page(viewport={'width':2000,'height':1200})
            page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort())
            goto_editor(page,f.url)
            page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').click()
            expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(3)
            expect(page.locator('#project-menu')).to_be_enabled()
            expect(page.locator('.window[data-key="schema"]')).to_be_hidden()
            for key,(identifier,value) in notes.items():
                window=page.locator(f'.window[data-key="{key}"]')
                expect(r.floating.property_value(window,'Note')).to_have_value(value)
                assert window.get_attribute('data-element-owner')==identifier
            browser=r.browser_window(page)
            r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder2"]')
            r.search(browser,d.LABEL,'Extra2')
            browser.locator(f'[data-object="{d.NS}::Extra2"]').click(button='right')
            page.locator('.context-menu').get_by_role('button',name='스키마 열기',exact=True).click()
            expect(r.floating.property_value(page.locator('.window[data-key="schema"]'),'Note')).to_have_value('Retained primary close input')
            f.original()
            print('PASS closed layout persists across restart; explicit reopen retains input',flush=True)
            raise SystemExit(0)
        snapshot=f.state()
        assert snapshot['draft']['id']==saved_id and len(snapshot['editorViews']) in (0,3)
        if primary_mode:
            assert snapshot['schema']['id']==saved_id
            assert not any(req.get('endpoint') in ('select','schema') for req in invokes),invokes
            if not close_mode:
                preparations=[req['input'] for req in invokes if req.get('endpoint')=='preparePropertyModels' and req['input'].get('restoreStatuses')]
                assert len(preparations)==1 and saved_id in preparations[0]['ids'],preparations
                def primary_reads():return [req for req in invokes if req.get('endpoint')=='browserDrafts' and req['input'].get('ids')==[saved_id]]
                if mode in ('primary-fallback','primary-external-during'):
                    deadline=time.monotonic()+10
                    while not primary_reads() and time.monotonic()<deadline:page.wait_for_timeout(20)
                    assert primary_reads(),invokes
                    expect(page.locator('#project-menu')).to_be_enabled()
                else:assert not primary_reads(),invokes
            if close_mode:
                browser=r.browser_window(page)
                r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder2"]')
                r.search(browser,d.LABEL,'Extra2')
                browser.locator(f'[data-object="{d.NS}::Extra2"]').click(button='right')
                page.locator('.context-menu').get_by_role('button',name='스키마 열기',exact=True).click()
                expect(primary).to_be_visible()
                expect(r.floating.property_value(primary,'Note')).to_have_value('Retained primary close input')
                print('PASS manual reopen retains closed primary input and exact owner',flush=True)
            else:expect(r.floating.property_value(page.locator('.window[data-key="schema"]'),'Note')).to_have_value('Retained primary Extra2' if mode=='primary-save-own' else d.FIRST+' Extra2')
            if not save_mode:expect(d.field(page.locator('.window[data-key="schema"]'),'RestartFlag')).to_be_visible()
        elif mode!='baseline':assert snapshot['schema'] is None, snapshot['schema']

        print('restored detached status reads',len(status),flush=True)
        if mode=='stale':
            # The deliberately dirty retained owner has no clean initial proof.
            # It may perform one ordinary bound status read; clean peers must not.
            assert len(status)<=1 and all(req['input']['ids']==[d.NS+'::Extra1'] for req in status),status
        elif mode not in ('baseline','primary-fallback','primary-external-during'):
            assert not status,status
        if mode=='primary-external-during':
            for key in notes:expect(d.field(page.locator(f'.window[data-key="{key}"]'),'DuringRestoreFlag')).to_be_visible()
            browser=r.browser_window(page)
            r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder2"]')
            r.search(browser,d.LABEL,'Extra2')
            browser.locator(f'[data-object="{d.NS}::Extra2"]').click(button='right')
            page.locator('.context-menu').get_by_role('button',name='스키마 열기',exact=True).click()
            expect(d.field(page.locator('.window[data-key="schema"]'),'DuringRestoreFlag')).to_be_visible()
            print('PASS external schema change during preparation rejects old primary status proof',flush=True)
        if save_mode:
            if mode=='primary-save-own':
                key='schema'
                notes[key]=(d.NS+'::Extra2','Retained primary Extra2')
                source=f.projects[0].parent/'private-source-Extra2.celem'
            else:
                key=next(key for key,(identifier,_) in notes.items() if identifier==d.NS+'::Extra1')
                source=f.projects[0].parent/'private-source-Extra1.celem'
            target=page.locator(f'.window[data-key="{key}"]')
            marker=len(invokes)
            button=target.locator('[data-element-action="confirm"]')
            expect(button).to_have_text('저장')
            note=r.floating.property_value(target,'Note')
            if key=='schema':page.locator('.window[data-key="browser"]').get_by_role('button',name='창 닫기',exact=True).click()
            note.click()
            assert page.evaluate('document.activeElement.closest(".window")?.dataset.key')==key
            expect(note).to_have_value(notes[key][1])
            if key!='schema':assert target.get_attribute('data-element-owner')==notes[key][0]
            else:assert f.state()['draft']['id']==notes[key][0]
            assert source.read_bytes()==f.before[str(source)]
            button.click()
            expect(page.locator('#status')).to_have_text('저장했습니다.',timeout=120000)
            expect(page.locator('#project-menu')).to_be_enabled()
            calls=[req['endpoint'] for req in invokes[marker:]]
            if key=='schema':assert calls.count('directPropertyConfirm')==1,calls
            else:assert calls.count('reviewGroup')==calls.count('confirmGroup')==1,calls
            assert f'data Note = "{notes[key][1]}"' in source.read_text()
            f.before[str(source)]=source.read_bytes()
            for peer,(_,value) in notes.items():
                if peer!=key:expect(r.floating.property_value(page.locator(f'.window[data-key="{peer}"]'),'Note')).to_have_value(value)
        # The initial proof is one-shot, not a session cache. A later real
        # dependency change must still be visible on an ordinary status read.
        schema.write_text(schema.read_text().rstrip()[:-1] + ' field AfterRestoreFlag single general string;\n}\n')
        f.before[str(schema)] = schema.read_bytes()
        rows = f.state()['editorViews']
        if rows:
            row = rows[0]
            f.call('browserDrafts', {'action':'status', 'view':row['view'], 'id':row['id'], 'ids':[row['id']]})
        else:
            for name,folder in [(d.TARGET,'StockFolder'),(d.PEER,'PeerFolder'),('Extra1','ExtraFolder1')]:
                r.drag(page,name,folder)
                expect(page.locator('#project-menu')).to_be_enabled()
        for key, (_, value) in notes.items():
            window = page.locator(f'.window[data-key="{key}"]')
            expect(d.field(window, 'AfterRestoreFlag')).to_be_visible()
            expect(r.floating.property_value(window, 'Note')).to_have_value(value)
        f.original()
        if save_mode:
            page.evaluate('()=>confectoryFlushPresentation()')
            page.close()
            f.stop()
            f.start(2)
            page=b.new_page(viewport={'width':2000,'height':1200})
            page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort())
            goto_editor(page,f.url)
            page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.FIRST,exact=True)).locator('[data-enter]').click()
            expect(page.locator('#project-menu')).to_be_enabled()
            for restored, (identifier,value) in notes.items():
                window=page.locator(f'.window[data-key="{restored}"]')
                expect(r.floating.property_value(window,'Note')).to_have_value(value)
                if restored!='schema':assert window.get_attribute('data-element-owner')==identifier
            page.locator('.brand').click()
            expect(page.locator('.home-grid')).to_be_visible()
            page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.SECOND,exact=True)).locator('[data-enter]').click()
            browser=r.browser_window(page)
            r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder1"]')
            r.search(browser,d.LABEL,'Extra1')
            browser.locator(f'[data-object="{d.NS}::Extra1"]').click(button='right')
            page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
            other=page.locator(f'.window[data-element-owner="{d.NS}::Extra1"][data-element-mode="properties"]:visible')
            expect(r.floating.property_value(other,'Note')).to_have_value(d.SECOND+' Extra1')
            f.original()
            print('PASS restored string direct save, exact persisted source, restart and same-ID project isolation',flush=True)
        print('PASS cold restore ('+mode+'): exact three owners, retained input and external schema refresh', flush=True)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
