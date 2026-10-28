"""Owned verification workspaces and two-generation, verified package storage.

Linux test infrastructure, not editor storage policy. No pre-existing checkout,
cache, package, profile or evidence directory can be adopted for cleanup.
"""
import argparse
import ctypes
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
import zipfile

MIB = 1024 * 1024


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(MIB), b''):
            h.update(block)
    return h.hexdigest()


def identity(path):
    s = Path(path).lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_uid != os.getuid():
        raise RuntimeError('Not an owned, link-free directory: ' + str(path))
    return [s.st_dev, s.st_ino, s.st_uid]


def no_links(path):
    if any(p.is_symlink() for p in [Path(path), *Path(path).parents]):
        raise RuntimeError('Linked path: ' + str(path))


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path, value):
    path = Path(path)
    pending = path.with_name(path.name + '.' + uuid.uuid4().hex + '.pending')
    try:
        with pending.open('x') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write('\n'); out.flush(); os.fsync(out.fileno())
        os.replace(pending, path); fsync_dir(path.parent)
    finally:
        if pending.exists():
            pending.unlink()


def process_identity(pid):
    try:
        # PID plus kernel start time prevents acting on a reused PID. No FD/maps
        # access or system-wide process ownership inference is needed.
        fields = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        return [int(pid), int(fields[19])] if fields[0] != 'Z' else None
    except FileNotFoundError:
        return None


def alive(record):
    return bool(record) and process_identity(record[0]) == record


def send(record, signum):
    """Signal the recorded process, never a newly reused PID."""
    try:
        fd = os.pidfd_open(record[0])
    except ProcessLookupError:
        return
    try:
        current = process_identity(record[0])
        if current is None: return
        if current != record:
            raise RuntimeError('PID was reused; signal refused')
        signal.pidfd_send_signal(fd, signum)
    finally:
        os.close(fd)


def files(root):
    root = Path(root); result = {}
    no_links(root)
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            p = Path(directory) / name; s = p.lstat()
            if stat.S_ISLNK(s.st_mode) or not (stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode)):
                raise RuntimeError('Non-regular verification input: ' + str(p))
        for name in names:
            p = Path(directory) / name
            result[p.relative_to(root).as_posix()] = p
    return result


def archive(root, target):
    """Freeze all evidence, including profiles, screenshots and failure input."""
    entries = files(root)
    proof = {n: {'sha256': sha(p), 'size': p.stat().st_size,
                 'mode': stat.S_IMODE(p.stat().st_mode), 'directory': False} for n, p in entries.items()}
    directories = {}
    for directory, names, _ in os.walk(root,followlinks=False):
        for name in names:
            path = Path(directory)/name
            relative = path.relative_to(root).as_posix()+'/'
            directories[relative] = path
            proof[relative] = {'sha256':hashlib.sha256(b'').hexdigest(),'size':0,
                               'mode':stat.S_IMODE(path.stat().st_mode),'directory':True}
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for name, path in sorted({**entries,**directories}.items()):
            out.write(path, name)
    verify_archive(target, proof)
    if files(root).keys() != entries.keys() or any(sha(p) != proof[n]['sha256'] for n, p in entries.items()):
        raise RuntimeError('Evidence changed during archival')
    return proof


def verify_archive(path, proof, restore=None):
    directory_modes = []
    with zipfile.ZipFile(path) as source:
        names = source.namelist()
        if len(names) != len(set(names)) or set(names) != set(proof):
            raise RuntimeError('Archive file set differs')
        for name in names:
            parts = PurePosixPath(name)
            if parts.is_absolute() or '..' in parts.parts or '\\' in name or not parts.parts:
                raise RuntimeError('Unsafe archive member')
            info = source.getinfo(name); row = proof[name]
            if info.is_dir() != row.get('directory',False):
                raise RuntimeError('Archive entry type differs')
            if stat.S_ISLNK(info.external_attr >> 16):
                raise RuntimeError('Linked archive member')
            data = source.read(name)  # also checks the ZIP CRC
            if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise RuntimeError('Archive bytes differ: ' + name)
            if stat.S_IMODE(info.external_attr >> 16) != row['mode']:
                raise RuntimeError('Archive mode differs: ' + name)
            if restore is not None:
                target = Path(restore) / name
                if row.get('directory'):
                    target.mkdir(parents=True,exist_ok=True)
                    directory_modes.append((target,row['mode'])); continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as out:
                    out.write(data)
                target.chmod(row['mode'])
    if restore is not None:
        actual = files(restore)
        expected = {n for n,r in proof.items() if not r.get('directory')}
        actual_dirs = {p.relative_to(restore).as_posix()+'/' for p in Path(restore).rglob('*') if p.is_dir()}
        expected_dirs = {n for n,r in proof.items() if r.get('directory')}
        # Early bootstrap archives recorded files only. Their implied parent
        # directories are still checked; new archives also preserve empty dirs.
        expected_dirs.update(parent.as_posix()+'/' for n in expected for parent in PurePosixPath(n).parents if parent != PurePosixPath('.'))
        if set(actual) != expected or actual_dirs != expected_dirs or any(sha(p) != proof[n]['sha256'] for n, p in actual.items()):
            raise RuntimeError('Restored archive differs')
        for directory,mode in sorted(directory_modes,key=lambda row:-len(row[0].parts)):
            directory.chmod(mode)


def recover_copy(target):
    target = Path(target); no_links(target.parent)
    receipt = target.with_name('.'+target.name+'.copy.json')
    if not receipt.exists(): return
    no_links(receipt); record = json.loads(receipt.read_text())
    if alive(record['creator']) and record['creator'] != process_identity(os.getpid()):
        raise RuntimeError('Persistent copy owner is still running')
    if record['parent'] != identity(target.parent) or Path(record['pending']).name != record['pending']:
        raise RuntimeError('Persistent copy ownership changed')
    pending = target.parent/record['pending']
    if pending.exists() or pending.is_symlink():
        s = pending.lstat()
        if (not stat.S_ISREG(s.st_mode) or
            [s.st_dev,s.st_ino,s.st_uid] != record.get('identity')):
            raise RuntimeError('Uncertified/replaced partial copy; preserve it')
        pending.unlink(); fsync_dir(target.parent)
    receipt.unlink(); fsync_dir(target.parent)


def durable_copy(source, target, safety=64*MIB):
    target = Path(target); no_links(target.parent)
    recover_copy(target)
    if target.exists() or target.is_symlink():
        raise FileExistsError(target)
    if shutil.disk_usage(target.parent).free < Path(source).stat().st_size + safety:
        raise OSError('Insufficient persistent space; preserve the RAM workspace')
    pending = target.with_name('.' + target.name + '.' + uuid.uuid4().hex + '.pending')
    receipt = target.with_name('.'+target.name+'.copy.json')
    record = {'creator':process_identity(os.getpid()),'parent':identity(target.parent),
              'pending':pending.name,'identity':None}
    atomic_json(receipt,record)
    try:
        with Path(source).open('rb') as src, pending.open('xb') as out:
            s = os.fstat(out.fileno()); record['identity'] = [s.st_dev,s.st_ino,s.st_uid]
            atomic_json(receipt,record)  # certify ownership before writing any payload
            shutil.copyfileobj(src, out, MIB); out.flush(); os.fsync(out.fileno())
        if sha(source) != sha(pending):
            raise RuntimeError('Persistent copy differs')
        os.replace(pending, target); fsync_dir(target.parent)
    finally:
        recover_copy(target)  # only its recorded inode, including partial failure


class Workspace:
    def __init__(self, persistent, temporary='/tmp', source=None):
        persistent = Path(persistent); no_links(persistent)
        persistent.mkdir(parents=True, exist_ok=True)
        no_links(temporary)
        self.id = uuid.uuid4().hex
        self.record = persistent / (self.id + '.json')
        self.root = Path(tempfile.mkdtemp(prefix='cv-', dir=temporary))
        self.evidence = self.root / 'evidence'; self.evidence.mkdir()
        self.worker_script = self.evidence/'worker.py'
        shutil.copy2(__file__,self.worker_script)
        token = uuid.uuid4().hex
        atomic_json(self.root / 'owner.json', {'id': self.id, 'token': token})
        self.state = {'schema': 1, 'id': self.id, 'token': token,
                      'root': str(self.root), 'identity': identity(self.root),
                      'temporaryParent': str(Path(temporary).resolve()),
                      'creator': process_identity(os.getpid()), 'source': source,
                      'workers': [], 'status': 'running', 'diskBefore': shutil.disk_usage(persistent).free}
        self.save()

    def save(self):
        atomic_json(self.record, self.state)

    def check(self):
        no_links(self.root)
        if (self.root.parent != Path(self.state['temporaryParent']) or
            identity(self.root) != self.state['identity'] or
            json.loads((self.root/'owner.json').read_text()) != {'id': self.id, 'token': self.state['token']}):
            raise RuntimeError('Workspace identity changed; cleanup refused')

    def profile(self, path):
        path = Path(path); no_links(path)
        relative = path.relative_to(self.evidence).as_posix()
        self.state.setdefault('profileRoots',[]).append({'path':relative,'identity':identity(path)})
        self.save()

    def runtime_directory(self, path):
        path = Path(path); no_links(path)
        relative = path.relative_to(self.evidence).as_posix()
        self.state.setdefault('runtimeDirectories',[]).append({'path':relative,'identity':identity(path)})
        self.save()

    def _preserve_runtime_objects(self):
        for row in self.state.get('runtimeDirectories',[]):
            root = self.evidence/row['path']; no_links(root)
            if identity(root) != row['identity']: raise RuntimeError('Runtime directory replaced')
            retained = []
            for path in root.iterdir():
                mode = path.lstat().st_mode
                if not (stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)): continue
                match = re.fullmatch(r'(?:clr-debug-pipe-|dotnet-diagnostic-)([0-9]+)-[0-9]+-(?:in|out|socket)',path.name)
                if not match or path.lstat().st_uid != os.getuid() or process_identity(int(match[1])) is not None:
                    raise RuntimeError('Uncertified runtime IPC object; preserve it: '+str(path))
                before = path.lstat()
                retained.append({'path':path.name,'mode':before.st_mode,'uid':before.st_uid,
                    'device':before.st_dev,'inode':before.st_ino,'payloadRead':False,
                    'reason':'terminated .NET diagnostic IPC; not fixture input'})
                fd = os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
                try:
                    now = os.stat(path.name,dir_fd=fd,follow_symlinks=False)
                    if (now.st_dev,now.st_ino) != (before.st_dev,before.st_ino):
                        raise RuntimeError('Runtime IPC object replaced')
                    os.unlink(path.name,dir_fd=fd)
                finally: os.close(fd)
            if retained: atomic_json(root/'runtime-ipc-metadata.json',retained)

    def _preserve_profile_links(self):
        # Chromium's transient lock/socket links must never be followed into
        # another directory. Retain their exact metadata as data, not as active
        # archive links. Only explicitly registered new profile roots qualify.
        for row in self.state.get('profileRoots',[]):
            root = self.evidence/row['path']; no_links(root)
            if identity(root) != row['identity']: raise RuntimeError('Profile root replaced')
            links = []
            for directory,dirs,names in os.walk(root,followlinks=False):
                for name in dirs+names:
                    path = Path(directory)/name
                    if path.is_symlink():
                        links.append({'path':path.relative_to(root).as_posix(),'target':os.readlink(path),
                                      'mode':path.lstat().st_mode})
                        path.unlink()  # exact owned link; target is never touched
            if links: atomic_json(root/'profile-link-metadata.json',links)

    def run(self, name, command, cwd=None, env=None, timeout=480, expected=0):
        self.check()
        log = self.evidence / (name + '.log')
        completion = self.root / (name + '.completed.json')
        read, write = os.pipe()
        with log.open('xb') as output:
            try:
                process = subprocess.Popen([sys.executable, str(self.worker_script), '--worker', str(read),
                                            str(completion), json.dumps(list(map(str, command)))],
                                           cwd=cwd or self.root, env=env, stdout=output,
                                           stderr=subprocess.STDOUT, pass_fds=(read,), start_new_session=True)
                os.close(read); read = None
                record = {'name': name, 'identity': process_identity(process.pid),
                          'completion': str(completion), 'command': list(map(str, command))}
                self.state['workers'].append(record); self.save()
                os.write(write, b'1'); os.close(write); write = None
                began = time.monotonic(); minimum = shutil.disk_usage(self.record.parent).free
                peak_memory = 0
                while process.poll() is None:
                    minimum = min(minimum, shutil.disk_usage(self.record.parent).free)
                    peak_memory = max(peak_memory, int(Path('/sys/fs/cgroup/memory.current').read_text()))
                    if time.monotonic() - began > timeout:
                        send(record['identity'], signal.SIGTERM)
                        process.wait(timeout=35)
                        raise TimeoutError(name + ': worker stopped; inspect retained log')
                    time.sleep(.2)
                complete = self._completed(record)
                row = dict(record, exit=complete['exit'], seconds=round(time.monotonic()-began, 2),
                           minimumDisk=minimum, peakMemory=peak_memory)
                self.state.setdefault('results', []).append(row); self.save()
                atomic_json(self.evidence/(name+'.result.json'), row)
                print(json.dumps({'stage': name, 'exit': row['exit'], 'seconds': row['seconds']}, ensure_ascii=False), flush=True)
                if row['exit'] != expected:
                    raise RuntimeError(name + ': exit ' + str(row['exit']) + '; log ' + str(log))
                return row
            finally:
                if read is not None: os.close(read)
                if write is not None: os.close(write)

    def _completed(self, worker):
        if alive(worker['identity']):
            raise RuntimeError('Worker is still using this workspace')
        complete = json.loads(Path(worker['completion']).read_text())
        if complete['identity'] != worker['identity'] or not complete['allChildrenReaped']:
            raise RuntimeError('Child termination has not been certified')
        return complete

    def finish(self, error=None, cleanup=True):
        if self.state['status'] in ['archived','cleaned']:
            if cleanup and self.state['status'] == 'archived': self.cleanup()
            return Path(self.state['evidence'])
        self.check()
        for worker in self.state['workers']:
            if alive(worker['identity']):
                send(worker['identity'], signal.SIGTERM)
                deadline = time.monotonic()+35
                while alive(worker['identity']) and time.monotonic()<deadline:
                    time.sleep(.1)
            self._completed(worker)
        self._preserve_profile_links()
        self._preserve_runtime_objects()
        evidence_zip = self.root/'evidence.zip'
        if self.state['status'] == 'archive-prepared':
            proof = json.loads((self.root/'archive-proof.json').read_text())
            verify_archive(evidence_zip, proof)
        else:
            self.state.update(status='archiving', error=str(error) if error else None)
            self.save(); atomic_json(self.evidence/'run.json', self.state)
            if evidence_zip.exists():
                evidence_zip.unlink()  # this owner's unfinished archive, not evidence input
            proof = archive(self.evidence, evidence_zip)
            atomic_json(self.root/'archive-proof.json', proof)
            self.state['status'] = 'archive-prepared'; self.save()
        destination = self.record.with_suffix('.zip')
        recover_copy(destination)
        if destination.exists():
            verify_archive(destination, proof)
        else:
            durable_copy(evidence_zip, destination)
        atomic_json(self.record.with_suffix('.manifest.json'), {'files': proof, 'archiveSha256': sha(destination)})
        self.state.update(status='archived', evidence=str(destination), evidenceSha256=sha(destination))
        self.save()
        if cleanup: self.cleanup()
        return destination

    def cleanup(self):
        self.check()
        if self.state['status'] != 'archived':
            raise RuntimeError('Evidence is not durably archived')
        for worker in self.state['workers']: self._completed(worker)
        publication = self.state.get('packagePublication')
        if publication:
            store = PackageStore(publication['store'])
            try:
                index = store.recover()
                if not any(index[k] and index[k]['sourceCommit'] == publication['entry']['sourceCommit'] for k in ['latest','rollback']):
                    raise RuntimeError('Verified package not durably retained; keep RAM candidate')
            finally: store.close()
        manifest = json.loads(self.record.with_suffix('.manifest.json').read_text())
        if sha(self.state['evidence']) != self.state['evidenceSha256']:
            raise RuntimeError('Persistent evidence changed; retain workspace')
        verify_archive(self.state['evidence'], manifest['files'])
        if not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError('Safe removal unavailable')
        fd = os.open(self.root.parent, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            self.check(); shutil.rmtree(self.root.name, dir_fd=fd)
        finally:
            os.close(fd)
        self.state.update(status='cleaned', diskAfter=shutil.disk_usage(self.record.parent).free)
        self.save()

    def preserve_partial(self, error):
        """Durable best-effort evidence when child termination is uncertified.

        This is explicitly incomplete and never authorizes workspace removal.
        Regular files are copied to a frozen tree; changing files are reported.
        """
        self.check(); frozen = self.root/('partial-'+uuid.uuid4().hex); frozen.mkdir()
        skipped = []
        for directory,dirs,names,fd in os.fwalk(self.evidence,follow_symlinks=False):
            for name in list(dirs):
                if stat.S_ISLNK(os.stat(name,dir_fd=fd,follow_symlinks=False).st_mode):
                    skipped.append(str(Path(directory,name).relative_to(self.evidence)))
                    dirs.remove(name)
            for name in names:
                relative = Path(directory,name).relative_to(self.evidence).as_posix()
                try:
                    before = os.stat(name,dir_fd=fd,follow_symlinks=False)
                    if not stat.S_ISREG(before.st_mode):
                        skipped.append(relative);continue
                    source_fd = os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
                    with os.fdopen(source_fd,'rb') as source:
                        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                            skipped.append(relative);continue
                        data = source.read()
                    after = os.stat(name,dir_fd=fd,follow_symlinks=False)
                    if (before.st_ino,before.st_size,before.st_mtime_ns) != (after.st_ino,after.st_size,after.st_mtime_ns):
                        skipped.append(relative);continue
                    copy = frozen/relative;copy.parent.mkdir(parents=True,exist_ok=True)
                    copy.write_bytes(data);copy.chmod(stat.S_IMODE(after.st_mode))
                except (FileNotFoundError,OSError): skipped.append(relative)
        atomic_json(frozen/'partial-status.json', {'complete':False,'cleanupAuthorized':False,
                    'error':str(error),'changingFilesSkipped':skipped,'workers':self.state['workers']})
        output = self.root/(frozen.name+'.zip')
        proof = archive(frozen,output)
        destination = self.record.with_name(self.id+'.'+frozen.name+'.zip')
        durable_copy(output,destination)
        atomic_json(destination.with_suffix('.manifest.json'),{'files':proof,'archiveSha256':sha(destination)})
        return destination

    @classmethod
    def load(cls, record):
        self = cls.__new__(cls); self.record = Path(record)
        no_links(self.record)
        self.state = json.loads(self.record.read_text()); self.id = self.state['id']
        self.root = Path(self.state['root']); self.evidence = self.root/'evidence'
        if self.state['status'] == 'cleaned': return self
        if alive(self.state['creator']):
            raise RuntimeError('Original workspace owner is still running')
        self.check()
        return self

    @classmethod
    def recover(cls, record):
        self = cls.load(record)
        if self.state['status'] == 'cleaned': return self
        if self.state['status'] != 'archived': self.finish('Recovered interrupted verification owner',cleanup=False)
        publication = self.state.get('packagePublication')
        if publication:
            store = PackageStore(publication['store'])
            try:
                index = store.recover()
                if not any(index[k] and index[k]['sourceCommit'] == publication['entry']['sourceCommit'] for k in ['latest','rollback']):
                    store.promote(self.root/publication['candidate'],publication['entry'])
            finally: store.close()
        self.cleanup()
        return self


class PackageStore:
    """Only this new store's registered packages have a two-generation lifetime."""
    def __init__(self, root):
        self.root = Path(root); no_links(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.marker = self.root/'owner.json'
        no_links(self.marker)
        if not self.marker.exists():
            if any(self.root.iterdir()): raise RuntimeError('Cannot adopt an existing artifact directory')
            atomic_json(self.marker, {'storeId': uuid.uuid4().hex, 'identity': identity(self.root)})
        self.owner = json.loads(self.marker.read_text())
        if identity(self.root) != self.owner['identity']: raise RuntimeError('Store replaced')
        self.lock = (self.root/'lock').open('a+b')

    def close(self):
        self.lock.close()

    def index(self):
        p = self.root/'index.json'
        no_links(p)
        return json.loads(p.read_text()) if p.exists() else {'storeId': self.owner['storeId'], 'latest': None, 'rollback': None, 'retire': []}

    def _verify(self, entry, restore=None):
        if entry['storeId'] != self.owner['storeId'] or entry['archive'] != entry['sha256']+'.zip':
            raise RuntimeError('Unowned package entry')
        path = self.root/entry['archive']; no_links(path)
        if sha(path) != entry['sha256']: raise RuntimeError('Package archive changed')
        verify_archive(path, entry['files'], restore)

    def prepare(self, package, output, source, evidence):
        actual = files(package); marker = 'confectory-desktop-package.json'
        manifest = json.loads(actual[marker].read_text())
        if set(actual) != set(manifest['files'])|{marker} or any(sha(actual[n]) != h for n,h in manifest['files'].items()):
            raise RuntimeError('Package manifest/file bytes differ')
        proof = archive(package, output)
        if Path(output).stat().st_size > 60*MIB:
            raise OSError('Package archive exceeds the planned 60 MiB budget; no promotion')
        current = self.index()['latest']
        return {'storeId': self.owner['storeId'], 'sha256': sha(output), 'archive': sha(output)+'.zip',
                'expectedLatest':current['sha256'] if current else None,
                'sourceCommit': source, 'files': proof, 'evidence': str(evidence),
                'manifestSha256': sha(actual[marker]), 'archiveBytes': Path(output).stat().st_size,
                'actualWindows': False, 'actualMobile': False, 'libraryDelivered': False}

    def promote(self, archive_path, entry, fail=None):
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        try:
            self._recover()
            old = self.index()
            for role in ['latest', 'rollback']:
                if old[role]: self._verify(old[role])
            evidence = Path(entry['evidence'])
            evidence_manifest = json.loads(evidence.with_suffix('.manifest.json').read_text())
            if sha(evidence) != evidence_manifest['archiveSha256']:
                raise RuntimeError('Package evidence is not durable')
            verify_archive(evidence, evidence_manifest['files'])
            if sha(archive_path) != entry['sha256']:
                raise RuntimeError('Candidate archive changed before promotion')
            verify_archive(archive_path, entry['files'])
            # Repetition still verifies candidate and evidence in full, but it
            # does not displace a distinct known-good rollback.
            if old['latest'] and old['latest']['sourceCommit'] == entry['sourceCommit']:
                return old
            if (old['latest']['sha256'] if old['latest'] else None) != entry.get('expectedLatest'):
                raise RuntimeError('Package publication conflict; prior latest changed')
            destination = self.root/entry['archive']
            atomic_json(self.root/'transaction.json', {'storeId': self.owner['storeId'],
                        'entry': entry, 'createdHere': not destination.exists()})
            if destination.exists(): self._verify(entry)
            else: durable_copy(archive_path, destination)
            self._verify(entry)
            if fail: fail('before-index')
            new = {'storeId': self.owner['storeId'], 'latest': entry, 'rollback': old['latest'],
                   'retire': old.get('retire', []) + ([old['rollback']] if old['rollback'] else [])}
            atomic_json(self.root/'index.json', new)
            if fail: fail('after-index')
            self._retire(new)
            (self.root/'transaction.json').unlink(); fsync_dir(self.root)
            return new
        finally:
            fcntl.flock(self.lock, fcntl.LOCK_UN)

    def _retire(self, index):
        # Exact entries from the prior index only. Never scan old artifacts or
        # delete an unknown store file. New index is durable before retirement.
        live = {index[k]['sha256'] for k in ['latest','rollback'] if index[k]}
        for entry in index.get('retire', []):
            if entry['sha256'] not in live:
                path = self.root/entry['archive']
                if path.exists():
                    self._verify(entry); path.unlink(); fsync_dir(self.root)
        index['retire'] = []; atomic_json(self.root/'index.json', index)

    def _recover(self):
        index = self.index()
        if index['storeId'] != self.owner['storeId']: raise RuntimeError('Foreign index')
        for role in ['latest','rollback']:
            if index[role]: self._verify(index[role])
        transaction = self.root/'transaction.json'
        if transaction.exists():
            txn = json.loads(transaction.read_text()); entry = txn['entry']
            if txn['storeId'] != self.owner['storeId']: raise RuntimeError('Foreign transaction')
            live = {index[k]['sha256'] for k in ['latest','rollback'] if index[k]}
            path = self.root/entry['archive']
            recover_copy(path)
            if txn['createdHere'] and entry['sha256'] not in live and path.exists():
                self._verify(entry); path.unlink(); fsync_dir(self.root)
            self._retire(index)
            transaction.unlink(); fsync_dir(self.root)
        elif index.get('retire'): self._retire(index)

    def recover(self):
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        try: self._recover(); return self.index()
        finally: fcntl.flock(self.lock, fcntl.LOCK_UN)

    def restore(self, role, destination):
        fcntl.flock(self.lock, fcntl.LOCK_SH)
        try:
            index = self.index(); entry = index[role]
            if not entry: raise RuntimeError('No package in role '+role)
            self._verify(entry, destination)
            return entry
        finally:
            fcntl.flock(self.lock, fcntl.LOCK_UN)


def worker(gate, completion, command):
    # Reparent orphan grandchildren (including hosts in their own sessions) to
    # this worker so termination is certified without restricted FD/maps reads.
    if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
        raise OSError('Linux child-subreaper support is required')
    ident = process_identity(os.getpid())
    if os.read(gate, 1) != b'1': return 125
    os.close(gate); stopping = False
    def stopped(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stopped); signal.signal(signal.SIGINT, stopped)
    try:
        child = subprocess.Popen(command)
        deadline = None
        while child.poll() is None:
            if stopping:
                if deadline is None: child.terminate(); deadline = time.monotonic()+5
                elif time.monotonic()>deadline: child.kill()
            time.sleep(.05)
        status = child.returncode
    except BaseException:
        traceback.print_exc(); status = 125
    # All surviving descendants are now direct adopted children. Kill/reap each
    # exact child; this never enumerates or signals unrelated system processes.
    began = time.monotonic()
    while True:
        # Some supported kernels omit /proc/*/task/*/children. PPID/start time
        # from ordinary process stat plus waitpid certifies our adopted children;
        # no restricted FD/maps data is accessed or bypassed.
        children = []
        for item in Path('/proc').iterdir():
            if not item.name.isdecimal(): continue
            try:
                row = (item/'stat').read_text().rsplit(')',1)[1].split()
                if int(row[1]) == os.getpid(): children.append([int(item.name),int(row[19])])
            except (FileNotFoundError,ProcessLookupError,PermissionError): continue
        for child_id in children:
            try: send(child_id, signal.SIGKILL)
            except ProcessLookupError: pass
        no_children = False
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
                if pid == 0: break
            except ChildProcessError:
                no_children = True; break
        if no_children: break
        if time.monotonic()-began>20: raise RuntimeError('Descendants remain; retain workspace')
        time.sleep(.05)
    atomic_json(completion, {'identity': ident, 'exit': status, 'allChildrenReaped': True})
    return status if status >= 0 else 128-status


if __name__ == '__main__':
    if sys.argv[1:2] == ['--worker']:
        sys.exit(worker(int(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])))
    parser = argparse.ArgumentParser()
    parser.add_argument('--recover', required=True)
    args = parser.parse_args(); print(Workspace.recover(args.recover).state['status'])
