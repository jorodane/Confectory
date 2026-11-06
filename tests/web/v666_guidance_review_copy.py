"""Exact V2 review wording; preserve all executable guards and native diagnostics."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if(r/'docs/v666-finder-modules-delta.json').exists():
 import runpy
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_finder_modules_copy.py')),run_name='__main__')
 raise SystemExit(0)
plan=json.loads((r/'docs/v666-review-guidance-copy.json').read_text())
def old(path):return subprocess.check_output(['git','show',plan['baseCommit']+':'+path],cwd=r,text=True)
source=plan['path'];expected=old(source)
for row in plan['changes']:
 assert not any(c in row['before']+row['after']for c in "\n\r'\"`\\"),row
 assert not any(c in row['before']for c in '<>')or row['before']in['>Before</h3>','>After</h3>']
 assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
assert(r/source).read_text()==expected,'Unlisted logic/selector/guard/layout or diagnostic change'
assert hashlib.sha256((r/plan['source']).read_bytes()).hexdigest()==plan['sourceSha256']
style=plan['styleDelta'];expected=old(style['path']);assert expected.count(style['before'])==style['count'];assert(r/style['path']).read_text()==expected.replace(style['before'],style['after'])
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle)
for name,mime in [('v508-runtime.js','text/javascript'),('runtime.css','text/css')]:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"'+mime+'","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1
assert(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={source,style['path'],bundle},changed
subprocess.run(['node','--check',str(r/source)],check=True)
print('PASS exact 19 Review/Confirm messages/24 sites + bounded canvas stacking isolation + canonical resources; all original commands, CAS/selection/ack/retries, geometry, permissions, C# and backend diagnostics preserved')
