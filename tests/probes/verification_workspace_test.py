"""Real process/crash/ownership/archive tests for the verification harness."""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[2]/'tools'
sys.path.insert(0,str(TOOLS))
import verification_workspace as v


class LifetimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='verify-owner-tests-',dir='/tmp')
        self.base = Path(self.temporary.name)
        self.records = self.base/'records'; self.records.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def workspace(self):
        return v.Workspace(self.records,self.base,source='fixture-source')

    def test_success_failure_repeat_preserve_all_evidence(self):
        for code in [0,7,0]:
            w=self.workspace(); (w.evidence/'input.celem').write_text('원문 9223372036854775806')
            (w.evidence/'profile').mkdir(); (w.evidence/'profile'/'draft').write_text('unsaved input')
            (w.evidence/'empty-input-directory').mkdir()
            try:
                w.run('command',[sys.executable,'-c',f'print("fixture log");raise SystemExit({code})'])
            except RuntimeError:
                self.assertEqual(code,7)
            archive=w.finish('fixture failure' if code else None)
            self.assertFalse(w.root.exists()); self.assertEqual(w.state['status'],'cleaned')
            proof=json.loads(w.record.with_suffix('.manifest.json').read_text())
            restored=self.base/('restore-'+w.id);restored.mkdir()
            v.verify_archive(archive,proof['files'],restored)
            self.assertEqual((restored/'profile/draft').read_text(),'unsaved input')
            self.assertIn('fixture log',(restored/'command.log').read_text())
            self.assertEqual((restored/'input.celem').read_text(),'원문 9223372036854775806')
            self.assertTrue((restored/'empty-input-directory').is_dir())

    def test_detached_descendant_is_reaped(self):
        w=self.workspace()
        script='import subprocess,sys; p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(90)"],start_new_session=True);print(p.pid,flush=True)'
        w.run('orphan',[sys.executable,'-c',script])
        child=int((w.evidence/'orphan.log').read_text().strip())
        self.assertIsNone(v.process_identity(child));w.finish()

    def test_child_start_exception_is_archived(self):
        w=self.workspace()
        with self.assertRaises(RuntimeError):w.run('missing',['/nonexistent/owned-fixture-command'])
        w.finish('start exception');self.assertFalse(w.root.exists())

    def test_timeout_reaps_before_archive(self):
        w=self.workspace()
        with self.assertRaises(TimeoutError):
            w.run('timeout',[sys.executable,'-c','import time;print("before timeout",flush=True);time.sleep(90)'],timeout=.3)
        w.finish('timeout');self.assertFalse(w.root.exists())

    def test_archive_failure_retains_original_then_restart_recovers(self):
        script='''import os,sys
from pathlib import Path
import verification_workspace as v
w=v.Workspace(sys.argv[1],sys.argv[2]);(w.evidence/'input').write_text('never lose')
v.durable_copy=lambda *a,**k: (_ for _ in ()).throw(OSError('injected full disk'))
try:w.finish()
except OSError:os._exit(9)
'''
        p=subprocess.run([sys.executable,'-c',script,str(self.records),str(self.base)],env=dict(os.environ,PYTHONPATH=str(TOOLS)))
        self.assertEqual(p.returncode,9)
        record=next(self.records.glob('*.json'));state=json.loads(record.read_text())
        root=Path(state['root']);self.assertTrue((root/'evidence/input').exists())
        recovered=v.Workspace.recover(record);self.assertEqual(recovered.state['status'],'cleaned')
        self.assertFalse(root.exists());v.Workspace.recover(record)

    def test_crashed_owner_with_live_worker_recovers_without_pid_guessing(self):
        script='''import os,sys
import verification_workspace as v
w=v.Workspace(sys.argv[1],sys.argv[2]);(w.evidence/'draft').write_text('restart input')
w.run('child',[sys.executable,'-c','import os,signal,sys,time;os.kill(int(sys.argv[1]),signal.SIGKILL);print("child survived owner",flush=True);time.sleep(90)',str(os.getpid())])
'''
        p=subprocess.run([sys.executable,'-c',script,str(self.records),str(self.base)],env=dict(os.environ,PYTHONPATH=str(TOOLS)))
        self.assertEqual(p.returncode,-signal.SIGKILL)
        record=next(self.records.glob('*.json'))
        recovered=v.Workspace.recover(record)
        self.assertFalse(recovered.root.exists());self.assertEqual(recovered.state['status'],'cleaned')

    def test_live_owner_replacement_and_symlink_are_not_adopted(self):
        w=self.workspace()
        with self.assertRaisesRegex(RuntimeError,'still running'):v.Workspace.recover(w.record)
        original=json.loads((w.root/'owner.json').read_text())
        v.atomic_json(w.root/'owner.json',{'id':w.id,'token':'replaced'})
        with self.assertRaisesRegex(RuntimeError,'identity changed'):w.finish()
        self.assertTrue(w.root.exists());v.atomic_json(w.root/'owner.json',original)
        victim=self.base/'preserved';victim.write_text('original')
        (w.evidence/'linked').symlink_to(victim)
        with self.assertRaisesRegex(RuntimeError,'Non-regular'):w.finish()
        self.assertEqual(victim.read_text(),'original');(w.evidence/'linked').unlink();w.finish()

    def test_crash_mid_persistent_copy_removes_only_certified_partial(self):
        source=self.base/'source';source.write_bytes(b'regenerable fixture'*1000)
        destination=self.base/'saved.zip'
        script='''import os,sys
import verification_workspace as v
def interrupted(src,out,*a):out.write(b'partial');out.flush();os._exit(11)
v.shutil.copyfileobj=interrupted
v.durable_copy(sys.argv[1],sys.argv[2])
'''
        p=subprocess.run([sys.executable,'-c',script,str(source),str(destination)],env=dict(os.environ,PYTHONPATH=str(TOOLS)))
        self.assertEqual(p.returncode,11);self.assertFalse(destination.exists())
        self.assertEqual(len(list(self.base.glob('.*.pending'))),1)
        v.recover_copy(destination)
        self.assertFalse(list(self.base.glob('.*.pending')));self.assertFalse(list(self.base.glob('.*.copy.json')))
        v.durable_copy(source,destination);self.assertEqual(source.read_bytes(),destination.read_bytes())

    def test_uncertified_worker_preserves_partial_evidence_without_cleanup(self):
        w=self.workspace();(w.evidence/'draft').write_text('保留 입력')
        w.state['workers'].append({'name':'lost-supervisor','identity':[99999999,1],
                                  'completion':str(w.root/'missing.json')})
        with self.assertRaises(FileNotFoundError):w.finish()
        saved=w.preserve_partial('uncertified child termination')
        self.assertTrue(saved.exists());self.assertTrue(w.root.exists())
        w.state['workers']=[];w.finish()

    def test_registered_profile_link_metadata_preserved_without_following(self):
        w=self.workspace();profile=w.evidence/'browser';profile.mkdir();w.profile(profile)
        victim=self.base/'outside';victim.write_text('never read as profile data')
        (profile/'SingletonLock').symlink_to(victim)
        archive=w.finish();proof=json.loads(w.record.with_suffix('.manifest.json').read_text())
        restored=self.base/'restored-profile';restored.mkdir();v.verify_archive(archive,proof['files'],restored)
        links=json.loads((restored/'browser/profile-link-metadata.json').read_text())
        self.assertEqual(links[0]['target'],str(victim));self.assertEqual(victim.read_text(),'never read as profile data')

    def test_known_dead_runtime_fifo_recorded_without_reading_payload(self):
        w=self.workspace();runtime=w.evidence/'fixtures';runtime.mkdir();w.runtime_directory(runtime)
        pipe=runtime/'clr-debug-pipe-99999999-1-out';os.mkfifo(pipe)
        nested=runtime/'nested';nested.mkdir();os.mkfifo(nested/'dotnet-diagnostic-99999999-2-socket')
        w.finish();self.assertFalse(w.root.exists())
        proof=json.loads(w.record.with_suffix('.manifest.json').read_text());restored=self.base/'ipc-restore';restored.mkdir()
        v.verify_archive(w.record.with_suffix('.zip'),proof['files'],restored)
        metadata=json.loads((restored/'fixtures/runtime-ipc-metadata.json').read_text())
        self.assertEqual(len(metadata),2);self.assertFalse(metadata[0]['payloadRead']);self.assertFalse((restored/'fixtures'/pipe.name).exists())

    def test_unknown_fifo_is_never_read_or_removed_for_archive(self):
        w=self.workspace();runtime=w.evidence/'fixtures';runtime.mkdir();w.runtime_directory(runtime)
        pipe=runtime/'input-pipe';os.mkfifo(pipe)
        with self.assertRaisesRegex(RuntimeError,'Uncertified'):w.finish()
        self.assertTrue(pipe.exists());saved=w.preserve_partial('unknown IPC preserved')
        self.assertTrue(saved.exists());self.assertTrue(pipe.exists());pipe.unlink();w.finish()

    def test_truncated_runtime_socket_requires_full_fifo_producer_evidence(self):
        for truncated in ['dotnet-diagnostic-9999','dotnet-diagnostic']:
            with self.subTest(prefix=truncated):
                w=self.workspace();runtime=w.evidence/'fixtures';runtime.mkdir();w.runtime_directory(runtime)
                parent_size=107-len(truncated)-1
                parent=runtime/('x'*(parent_size-len(os.fsencode(runtime))-1));parent.mkdir()
                endpoint=parent/truncated
                s=socket.socket(socket.AF_UNIX);s.bind(str(endpoint));s.close()
                with self.assertRaisesRegex(RuntimeError,'Uncertified'):w.finish()
                self.assertTrue(endpoint.exists())
                os.mkfifo(parent/'clr-debug-pipe-99999999-1-out')
                w.finish();self.assertFalse(w.root.exists())


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='verify-store-tests-',dir='/tmp')
        self.base=Path(self.temporary.name);self.store=v.PackageStore(self.base/'managed')
        self.records=self.base/'records';self.records.mkdir()

    def tearDown(self):
        self.store.close();self.temporary.cleanup()

    def candidate(self,commit,input_identity=None):
        package=self.base/('package-'+commit);package.mkdir()
        (package/'Confectory.exe').write_bytes(b'MZ fixture '+commit.encode());(package/'Confectory.exe').chmod(0o755)
        (package/'input.txt').write_text('원문 '+commit)
        v.atomic_json(package/'confectory-desktop-package.json',{'files':{n:v.sha(p) for n,p in v.files(package).items()}})
        w=v.Workspace(self.records,self.base);(w.evidence/'proof').write_text('fixture engine and renderer passed')
        w.finish()
        archive=self.base/(commit+'.zip')
        entry=self.store.prepare(package,archive,commit,w.record.with_suffix('.zip'),input_identity)
        return archive,entry

    def test_two_generations_repeat_and_restore(self):
        unknown=self.store.root/'preserved.zip';unknown.write_bytes(b'never adopt')
        for commit in ['A','B','C']:
            archive,entry=self.candidate(commit);self.store.promote(archive,entry)
        index=self.store.index();self.assertEqual(index['latest']['sourceCommit'],'C');self.assertEqual(index['rollback']['sourceCommit'],'B')
        self.assertEqual(len([p for p in self.store.root.glob('*.zip') if p!=unknown]),2)
        for role,commit in [('latest','C'),('rollback','B')]:
            restored=self.base/role;restored.mkdir();self.store.restore(role,restored)
            self.assertEqual((restored/'input.txt').read_text(),'원문 '+commit)
            self.assertEqual((restored/'Confectory.exe').stat().st_mode&0o777,0o755)
        self.store.promote(self.base/'C.zip',index['latest'])
        self.assertEqual(self.store.index(),index);self.assertEqual(unknown.read_bytes(),b'never adopt')

    def test_failure_and_restart_before_and_after_atomic_index(self):
        for commit in ['A','B']:
            archive,entry=self.candidate(commit);self.store.promote(archive,entry)
        archive,entry=self.candidate('C')
        def before(stage):
            if stage=='before-index':raise OSError('injected before pointer replacement')
        with self.assertRaises(OSError):self.store.promote(archive,entry,before)
        self.store.close();self.store=v.PackageStore(self.store.root);index=self.store.recover()
        self.assertEqual(index['latest']['sourceCommit'],'B');self.assertEqual(index['rollback']['sourceCommit'],'A')
        def after(stage):
            if stage=='after-index':raise OSError('injected after pointer replacement')
        with self.assertRaises(OSError):self.store.promote(archive,entry,after)
        self.store.close();self.store=v.PackageStore(self.store.root);index=self.store.recover()
        self.assertEqual(index['latest']['sourceCommit'],'C');self.assertEqual(index['rollback']['sourceCommit'],'B')
        self.assertEqual(len(list(self.store.root.glob('*.zip'))),2)

    def test_tampered_package_or_evidence_never_replaces_latest(self):
        archive,entry=self.candidate('A');self.store.promote(archive,entry)
        archive,entry=self.candidate('B');archive.write_bytes(b'bad ZIP')
        with self.assertRaises(Exception):self.store.promote(archive,entry)
        self.assertEqual(self.store.index()['latest']['sourceCommit'],'A')
        self.assertEqual(self.store.index()['rollback'],None)

    def test_concurrent_prepared_candidate_cannot_overwrite_later_latest(self):
        archive,a=self.candidate('A');self.store.promote(archive,a)
        stale,b=self.candidate('B');fresh,c=self.candidate('C');self.store.promote(fresh,c)
        with self.assertRaisesRegex(RuntimeError,'conflict'):self.store.promote(stale,b)
        self.assertEqual(self.store.index()['latest']['sourceCommit'],'C')
        self.assertEqual(self.store.index()['rollback']['sourceCommit'],'A')

    def test_same_source_different_verified_dependency_input_is_not_reused(self):
        archive,a=self.candidate('A','sdk-one');self.store.promote(archive,a)
        archive,b=self.candidate('B','sdk-two');b['sourceCommit']='A';self.store.promote(archive,b)
        index=self.store.index();self.assertEqual(index['latest']['inputIdentity'],'sdk-two')
        self.assertEqual(index['rollback']['inputIdentity'],'sdk-one')

    def test_existing_directory_cannot_become_managed_store(self):
        old=self.base/'old';old.mkdir();(old/'original').write_text('preserve')
        with self.assertRaisesRegex(RuntimeError,'adopt'):v.PackageStore(old)
        self.assertEqual((old/'original').read_text(),'preserve')

    def test_restart_publishes_verified_candidate_before_ram_cleanup(self):
        script='''import os,sys
from pathlib import Path
import verification_workspace as v
w=v.Workspace(sys.argv[1],sys.argv[2]);store=v.PackageStore(sys.argv[3])
(w.evidence/'draft').write_text('preserve after restart')
p=w.root/'package';p.mkdir();(p/'program').write_text('verified fixture')
v.atomic_json(p/'confectory-desktop-package.json',{'files':{'program':v.sha(p/'program')}})
candidate=w.root/'package.zip';entry=store.prepare(p,candidate,'restart-source',w.record.with_suffix('.zip'))
w.state['packagePublication']={'store':str(store.root),'candidate':candidate.name,'entry':entry};w.save()
w.finish(cleanup=False);os._exit(12)
'''
        result=subprocess.run([sys.executable,'-c',script,str(self.records),str(self.base),str(self.store.root)],env=dict(os.environ,PYTHONPATH=str(TOOLS)))
        self.assertEqual(result.returncode,12)
        record=next(p for p in self.records.glob('*.json') if 'root' in json.loads(p.read_text()))
        recovered=v.Workspace.recover(record)
        self.assertFalse(recovered.root.exists())
        self.assertEqual(self.store.index()['latest']['sourceCommit'],'restart-source')
        restored=self.base/'restore-restart';restored.mkdir();self.store.restore('latest',restored)
        self.assertEqual((restored/'program').read_text(),'verified fixture')


if __name__=='__main__':unittest.main(verbosity=2)
