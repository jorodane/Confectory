"""One passive refresh fix, no permission/mutation/IO implementation changes."""
import pathlib,subprocess,hashlib,json,sys
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-office-io-poll-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
paths=set(git('diff','--name-only',d['baseCommit'],'--','src','packs','targets','examples').splitlines());assert paths==set(d['productFiles'])=={'packs/editor-home-model/Command.csbody'},paths
name=next(iter(paths));s=(r/name).read_text();assert hashlib.sha256(s.encode()).hexdigest()==d['productFiles'][name]
old=git('show',d['baseCommit']+':'+name)
insert='// Passive detail refresh must not reacquire a draft lock held by admitted tool I/O.\n// Adoption and explicit editing keep their original synchronous validation.\n'
condition='&&(operation!="poll"||aiRows[activeContext.ToString()]?["toolsObservationPending"]?.GetValue<bool>()!=true)'
assert s.replace(insert,'').replace(condition,'')==old
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
print('PASS only passive pending-tool detail refresh deferred; synchronous adoption/edit/ReviewConfirm/CAS, authentic IO/permission and UI layout remain byte-equivalent')
