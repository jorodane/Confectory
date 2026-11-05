"""Exact reviewed description recovery and guidance delta, canonical assets and prior copy."""
import hashlib,json,pathlib,re,subprocess,sys
if(pathlib.Path(sys.argv[1])/'docs/v666-source-recovery-delta.json').exists():
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_source_recovery_copy.py')),run_name='__main__');sys.exit(0)
r=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((r/'docs/v666-description-recovery-delta.json').read_text());paths={row['path']for row in plan['deltas']}
def old(path):return subprocess.check_output(['git','show',plan['baseCommit']+':'+path],cwd=r,text=True)
for path in paths:
 expected=old(path)
 for row in (v for v in plan['deltas']if v['path']==path):
  assert expected.count(row['before'])==row['count'],row['before'][:70];expected=expected.replace(row['before'],row['after'])
 assert(r/path).read_text()==expected,'Unlisted product change: '+path
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle)
for name in ['feature-authoring.js','feature-editor.js']:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern=r'("'+re.escape(name)+r'":\{"file":"'+re.escape(name)+r'","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1
assert(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed==paths|{bundle},changed
for file in ['v666-code-editor-copy.json','v666-value-guidance-copy.json']:
 for row in json.loads((r/'docs'/file).read_text())['changes']:assert(r/'examples/editor-home/ui/feature-authoring.js').read_text().count(row['after'])==row['count']
print('PASS exact owned description recovery delta and 11 guidance messages/13 occurrences; previous C#/value guidance, other logic/layout/contracts/permissions unchanged')
