"""Exact existing node display-name admission delta and canonical bundle only."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if (r/'docs/v666-root-void-name-recovery-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_root_void_name_recovery_copy.py'),str(r)],check=True);raise SystemExit(0)
p=json.loads((r/'docs/v666-node-names-recovery-delta.json').read_text())
def old(n):return subprocess.check_output(['git','show',p['baseCommit']+':'+n],cwd=r,text=True)
for name in {d['path']for d in p['deltas']}:
 expected=old(name)
 for d in (v for v in p['deltas']if v['path']==name):assert expected.count(d['before'])==d['count'];expected=expected.replace(d['before'],d['after'])
 assert (r/name).read_text()==expected
name='examples/editor-home/ui/feature-authoring.js';bundle='examples/editor-home/WebBundle.csbody';data=(r/name).read_text().encode();expected,n=re.subn(r'("feature-authoring.js":\{"file":"feature-authoring.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")',lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],old(bundle));assert n==1 and (r/bundle).read_text()==expected
assert set(subprocess.check_output(['git','diff','--name-only',p['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines())=={name,bundle,'packs/pack-workspace/Blueprint.csbody'}
for script in ['v666_node_names_recovery_guard.mjs','v666_root_return_position_guard.mjs','v666_root_value_rename_guard.mjs','v666_node_text_recovery_guard.mjs','v666_root_followup_proof.mjs']:subprocess.run(['node',str(r/'tests/web'/script),str(r)],check=True)
print('PASS existing ordinary node display names only; source writer, receipt format, history, ownership/CAS and authored layout unchanged')
