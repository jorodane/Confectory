"""Reuse sealed tests after one runner-relative lookup fix; rebuild packages."""
import json
from pathlib import Path
import subprocess
import zipfile

from verification_workspace import atomic_json, sha, verify_archive


ARG = "    parser.add_argument('--reuse-callee-role-renderer',type=Path,help='Sealed identical LF/CRLF test checks after the exact restored renderer lookup correction; builds/packages remain fresh')\n"
HOOK = "        if args.reuse_callee_role_renderer:\n            if args.suite!='private-callee-value-out':raise ValueError('Callee role renderer evidence requires its own suite')\n            from verification_callee_role_reuse import bind\n            bind(repo,args.reuse_callee_role_renderer,commit,inputs,work)\n"


def bind(repo, record, commit, inputs, work):
    record = Path(record)
    prior = json.loads(record.read_text())
    manifest = json.loads(record.with_suffix('.manifest.json').read_text())
    digest = sha(prior['evidence'])
    if prior['status'] != 'cleaned' or digest != prior['evidenceSha256'] or manifest['archiveSha256'] != digest:
        raise RuntimeError('Sealed completed evidence is required')
    verify_archive(prior['evidence'], manifest['files'])
    script = 'tests/web/v666_private_callee_value_out_renderer.py'
    helper = 'tools/verification_callee_role_reuse.py'
    driver = 'tools/verify_desktop.py'
    git = lambda *args: subprocess.check_output(['git', *args], cwd=repo, text=True)
    subprocess.run(['git', 'merge-base', '--is-ancestor', prior['source'], commit], cwd=repo, check=True)
    changed = git('diff', '--name-only', prior['source'], commit).splitlines()
    if any(name not in {script, helper, driver} and not name.startswith('docs/') for name in changed):
        raise RuntimeError('Product, fixture, dependency or other test inputs changed')
    old = git('show', prior['source'] + ':' + script)
    new = git('show', commit + ':' + script)
    before = "runpy.run_path(str(repo/'tests/web/v666_private_callee_return_renderer.py'),run_name='__main__')"
    after = "runpy.run_path(str(pathlib.Path(__file__).with_name('v666_private_callee_return_renderer.py')),run_name='__main__')"
    if old.count(before) != 1 or new.count(after) != 1 or new.replace(after, before) != old:
        raise RuntimeError('Renderer assertions or behavior changed beyond the lookup')
    new_driver = git('show', commit + ':' + driver)
    if new_driver.count(ARG) != 1 or new_driver.count(HOOK) != 1:
        raise RuntimeError('Reuse hook differs')
    normalized = new_driver.replace(ARG, '').replace(HOOK, '').replace("'verification_callee_role_reuse.py',", '')
    if normalized != git('show', prior['source'] + ':' + driver):
        raise RuntimeError('Driver routing, budgets or checks changed')
    failed = [row['name'] for row in prior['results'] if row['exit'] != 0]
    if failed != ['restored-private-callee-value-out-renderer']:
        raise RuntimeError('Only the captured restored lookup failure can be resumed')
    with zipfile.ZipFile(prior['evidence']) as archive:
        source = json.loads(archive.read('source.json'))
        if source['commit'] != prior['source'] or any(source['dependencyInputs'].get(key) != inputs.get(key) for key in ['sdk', 'nuget', 'configuration', 'rid']):
            raise RuntimeError('SDK, dependencies or configuration changed')
        log = archive.read(failed[0] + '.log').decode()
        missing = str(Path(prior['root']) / 'restored/content/tests/web/v666_private_callee_return_renderer.py')
        if 'FileNotFoundError' not in log or missing not in log or 'PASS changed original source hash rejects reentry' not in log:
            raise RuntimeError('Captured failure does not match the exact lookup boundary')
        for label, eol in [('lf', 'false'), ('crlf', 'true')]:
            checkout = json.loads(archive.read(label + '-checkout.json'))
            if checkout['commit'] != prior['source'] or checkout['coreAutocrlf'] != eol or checkout['noSharedGitObjects'] is not True:
                raise RuntimeError('Independent source/EOL facts differ')
    # Clones, restores, builds and engines are prerequisites whose temporary
    # outputs were cleaned by the old run. Execute those and all package checks.
    prefixes = ('lf-v536_', 'crlf-v536_', 'lf-private-callee-value-out-', 'crlf-private-callee-value-out-')
    rows = {row['name']: row for row in prior['results'] if row['exit'] == 0 and row['name'].startswith(prefixes)}
    if len(rows) != 27 or sum(name.startswith('lf-') for name in rows) != 20:
        raise RuntimeError('The complete 27 passing test facts are required')
    # For the old LF invocation, repo/tests and the runner's sibling are the
    # same file. Only restored content lacks tests; that case executes freshly.
    renderer = rows['lf-private-callee-value-out-renderer']['command']
    if Path(renderer[1]).with_name('v666_private_callee_return_renderer.py') != Path(renderer[2]) / 'tests/web/v666_private_callee_return_renderer.py':
        raise RuntimeError('Old LF lookup equivalence is unproven')
    proof = dict(previousRecord=str(record), previousSource=prior['source'], sourceCommit=commit,
                 previousArchive=prior['evidence'], archiveSha256=digest,
                 allowedChangedFiles=changed, identicalProductFixturesAndDependencies=True,
                 onlyTestChange='runner-relative sibling lookup; LF resolution identical',
                 failedChecksReused=False, buildsAndPackagesReused=False, stages=[])
    atomic_json(work.evidence/'callee-role-reuse.json', proof)
    original = work.run

    def run(name, command, *args, **kwargs):
        if name not in rows:
            return original(name, command, *args, **kwargs)
        row = rows[name]
        normalize = lambda values, root: [str(value).replace(root, '$OWNED_WORKSPACE') for value in values]
        if kwargs.get('expected', 0) != 0 or normalize(row['command'], prior['root']) != normalize(command, str(work.root)):
            raise RuntimeError('Completed test invocation differs: ' + name)
        proof['stages'].append(name)
        work.state.setdefault('reusedChecks', []).append(dict(name=name, sourceCommit=prior['source'], record=str(record), archiveSha256=digest))
        work.save()
        atomic_json(work.evidence/'callee-role-reuse.json', proof)
        atomic_json(work.evidence/(name + '.reused.json'), dict(proof=proof, priorResult=row))
        print(json.dumps(dict(stage=name, reused=True, sourceCommit=prior['source'])), flush=True)
        return row

    work.run = run
