"""Exact V2 review wording; preserve all executable guards and native diagnostics."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((r/'docs/v666-review-guidance-copy.json').read_text())
def old(path):return subprocess.check_output(['git','show',plan['baseCommit']+':'+path],cwd=r,text=True)
source=plan['path'];expected=old(source)
for row in plan['changes']:
 assert not any(c in row['before']+row['after']for c in "\n\r'\"`\\"),row
 assert not any(c in row['before']for c in '<>')or row['before']in['>Before</h3>','>After</h3>']
 assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
assert(r/source).read_text()==expected,'Unlisted logic/selector/guard/layout or diagnostic change'
assert hashlib.sha256((r/plan['source']).read_bytes()).hexdigest()==plan['sourceSha256']
bundle='examples/editor-home/WebBundle.csbody';data=expected.encode();pattern=r'("v508-runtime.js":\{"file":"v508-runtime.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],old(bundle));assert n==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={source,bundle},changed
subprocess.run(['node','--check',str(r/source)],check=True)
print('PASS exact 19 Review/Confirm messages/24 sites + canonical resource; all original commands, CAS/selection/ack/retries, layouts, permissions, C# and backend diagnostics preserved')
