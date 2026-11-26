"""Real Logic Code Confirm -> cold editor -> Run of the same project entry.

The no-retain/damage modes withhold or corrupt only generated fixture artifacts,
never source, to distinguish the ordinary required link from validated reuse.
"""
import json,os,sys,tempfile,time
from pathlib import Path
from playwright.sync_api import expect,sync_playwright
from project_run_compile_recovery import editor
from editor_logic_workflow import open_main,edit_body,review,run_from_dock

def exercise(root,repo,command,browser,case):
    project=root/'Active';project.mkdir()
    ns='Test.ConfirmedLink.Active';marker=root/'result.txt'
    manifest=project/'project.cpack'
    manifest.write_text(f'''project {ns} version "1" {{ standalone true;
      registry Confectory.Build.DotNet {json.dumps(str(repo/'targets/dotnet/pack.cpack'))};
      dependency Confectory.Build.DotNet version "0.1.0";
      target linux Confectory.Build.DotNet::Linux; entry {ns}::Main;
      element Main function "Main.celem"; element MainBody implementation "MainBody.celem";
    }}''')
    (project/'Main.celem').write_text(f'function {ns}::Main () -> int {{ provide {ns}::Main with {ns}::MainBody; }}')
    (project/'MainBody.celem').write_text(f'implementation {ns}::MainBody for {ns}::Main () -> int {{ body common "Main.csbody"; }}')
    source=project/'Main.csbody';source.write_text('return 0;\n')
    output=project/'.confectory/outputs/linux';retained=output/'confirmed-link'
    with editor(root,repo,command,project,browser) as page:
        panel=open_main(page,ns+'::Main')
        expect(panel.locator('[data-native-source]')).to_have_value('return 0;\n')
        panel.locator('[data-native-convert]').click()
        expect(panel.locator('.bp-status')).to_contain_text('C# 미리보기')
        panel.locator('[data-bp-save]').click()
        expect(panel.get_by_role('tab',name='논리 코드',exact=True)).to_be_visible(timeout=120000)
        text=f'System.IO.File.WriteAllText({json.dumps(str(marker))}, "confirmed");\nreturn 0;\n'
        edit_body(page,panel,text,change=True)
        panel.locator('[data-bp-save]').click()
        expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000)
        pending=review(page,panel.locator('[data-bp-complete]'))
        pending.locator('[data-reject]').click()
        assert source.read_text()=='return 0;\n' and not retained.exists() and not marker.exists()
        pending=review(page,panel.locator('[data-bp-complete]'))
        if case=='conflict':
            source.write_text('return 0; // external original change\n')
            pending.locator('#confirm').click()
            expect(page.locator('#status')).to_contain_text('최종 소스에 반영되지 않았습니다',timeout=120000)
            expect(pending).to_be_visible()
            assert source.read_text()=='return 0; // external original change\n'
            assert not retained.exists() and not (output/'latest.json').exists() and not marker.exists()
            print('PASS external Review conflict refused without retaining link or rewriting original',flush=True)
            return
        started=time.perf_counter();pending.locator('#confirm').click()
        expect(pending).to_be_hidden(timeout=120000)
        expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')
        confirm_ms=round((time.perf_counter()-started)*1000)
        trace=[json.loads(line.removeprefix('CONFECTORY_UI_TRACE ')) for line in (root/'Active.log').read_text().splitlines() if line.startswith('CONFECTORY_UI_TRACE ') and '"retainConfirmedLink"' in line]
        retain_ms=round(sum(row.get('elapsedMs',0) for row in trace))
        print('TIMING post-commit candidate retention ms',retain_ms,flush=True)
        assert (retained/'latest.json').is_file(), 'Confirm did not retain validated link'
        assert not (output/'latest.json').exists(), 'Confirm published a Run output'
        assert not marker.exists()
        page.evaluate('async()=>await confectoryFlushPresentation()')
    if case=='damage':
        id=json.loads((retained/'latest.json').read_text())['id']
        (retained/id/'Confectory.App.dll').write_bytes(b'damaged candidate output')
    elif case=='no-retain':
        retained.rename(retained.with_name('withheld-confirmed-link'))
    # Actual new editor process and profile-aware cold project entry.
    with editor(root,repo,command,project,browser) as page:
        workspace=page.get_by_role('tab',name='Workspace',exact=True)
        if workspace.get_attribute('aria-selected')!='true':workspace.click()
        started=time.perf_counter();run_from_dock(page,marker,'confirmed')
        wall_ms=round((time.perf_counter()-started)*1000)
        stats=json.loads((output/'latest.json').read_text())['statistics']
        print('OBSERVED',case,dict(confirmMs=confirm_ms,runMs=wall_ms,links=stats['targetInvocations'].get('link',0),linkMs=round(stats['targetElapsedMilliseconds'].get('link',0)),reusedConfirmed=stats['reusedConfirmedLinks'],compiled=stats['compiledPacks']),flush=True)
        assert stats['reusedConfirmedLinks']==(1 if case=='reuse' else 0),stats
        assert stats['targetInvocations'].get('link',0)==(0 if case=='reuse' else 1),stats
        print('PASS cancelled Review, confirmed source, cold actual editor Run and exact output',flush=True)

if __name__=='__main__':
    repo=Path(sys.argv[1]).resolve();command=json.loads(Path(sys.argv[2]).read_text())['run']
    case=sys.argv[3] if len(sys.argv)>3 else 'reuse'
    assert case in ('reuse','no-retain','damage','conflict')
    expect.set_options(timeout=30000)
    with tempfile.TemporaryDirectory(prefix='cf-confirmed-link-') as temp,sync_playwright() as pw:
        with pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'],ignore_default_args=['--disable-dev-shm-usage']) as browser:
            exercise(Path(temp),repo,command,browser,case)
