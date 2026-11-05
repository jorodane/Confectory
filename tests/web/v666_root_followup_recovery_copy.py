"""Only retain the validated closure of already-retained author receipts."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if(r/'docs/v666-direct-creation-recovery-delta.json').exists():
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_direct_creation_recovery_copy.py')),run_name='__main__')
 raise SystemExit(0)
plan=json.loads((r/'docs/v666-root-followup-recovery-delta.json').read_text());path='packs/edit-workspace/Export.csbody';v=plan['deltas'][0];assert v['path']==path and v['count']==1
old=lambda name:subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
original=old(path);assert original==v['before'] and(r/path).read_text()==v['after']
assert {d['path']for d in plan['deltas']}=={path,'examples/editor-home/ui/feature-authoring.js'}
for name in {d['path']for d in plan['deltas']}:
 expected=old(name)
 for d in (d for d in plan['deltas']if d['path']==name):assert expected.count(d['before'])==d['count'];expected=expected.replace(d['before'],d['after'])
 assert(r/name).read_text()==expected,'Unlisted source delta: '+name
bundle='examples/editor-home/WebBundle.csbody';data=(r/'examples/editor-home/ui/feature-authoring.js').read_text().encode();pattern=r'("feature-authoring.js":\{"file":"feature-authoring.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],old(bundle));assert n==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={path,'examples/editor-home/ui/feature-authoring.js',bundle},changed
flags=lambda text:set(re.findall(r'authorSaveReceipt"\]\?\["(owned\w+)"',text));assert flags(original)==flags(v['after']) and len(flags(original))==11
assert v['after'].count('RetainAuthor(')==3 and 'RetainAuthor(member,id!.ToString())'in v['after'] and 'RetainAuthor(unit,entry.Key)'in v['after']
for name in ['packs/edit-workspace/Restore.csbody','packs/edit-workspace/ValidateReviewSelection.csbody','packs/pack-workspace/Blueprint.csbody']:
 assert(r/name).read_text()==subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
subprocess.run(['node',str(pathlib.Path(__file__).with_name('v666_root_followup_proof.mjs')),str(r)],check=True)
print('PASS exact retained-root-closure and receipt-bound single owned source proof delta; same 11 durable flags and graph binding; restore/permissions/ABI/source/UI/layout unchanged')
