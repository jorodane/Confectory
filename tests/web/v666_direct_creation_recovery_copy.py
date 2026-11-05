"""Exact UI-only candidate/retry wiring, unchanged native contracts and authored layout."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if (r/'docs/v666-text-pair-recovery-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_text_pair_recovery_copy.py'),str(r)],check=True);raise SystemExit(0)
plan=json.loads((r/'docs/v666-direct-creation-recovery-delta.json').read_text())
def old(name):return subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
name='examples/editor-home/ui/feature-authoring.js';expected=old(name)
assert {d['path']for d in plan['deltas']}=={name,'packs/pack-workspace/Blueprint.csbody'}
for path in {d['path']for d in plan['deltas']}:
 expected=old(path)
 for d in (d for d in plan['deltas']if d['path']==path):assert expected.count(d['before'])==d['count'];expected=expected.replace(d['before'],d['after'])
 assert(r/path).read_text()==expected
expected=(r/name).read_text()
bundle='examples/editor-home/WebBundle.csbody';data=expected.encode();expected,n=re.subn(r'("feature-authoring.js":\{"file":"feature-authoring.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")',lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],old(bundle));assert n==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={name,bundle,'packs/pack-workspace/Blueprint.csbody'},changed
for script in ['v666_direct_creation_guard.mjs','v666_root_followup_proof.mjs']:subprocess.run(['node',str(pathlib.Path(__file__).with_name(script)),str(r)],check=True)
native=(r/'packs/pack-workspace/Blueprint.csbody').read_text();assert native.count('ownedDirectCreationBatch')==5 and 'PlainSourcesUnchanged(actual,requireOriginal:ownedNodeInputBatch||ownedDirectCreationBatch)'in native
print('PASS exact direct creation Save/retry and bounded unapplied-baseline observation delta only; native admission/ownership/CAS/contracts and authored layout unchanged')
