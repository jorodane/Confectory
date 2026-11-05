"""Exact source Save/guidance delta and unchanged authored layout/contracts."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((r/'docs/v666-name-recovery-delta.json').read_text());paths={v['path']for v in plan['deltas']}
def old(path):return subprocess.check_output(['git','show',plan['baseCommit']+':'+path],cwd=r,text=True)
for path in paths:
 expected=old(path)
 for v in (v for v in plan['deltas']if v['path']==path):assert expected.count(v['before'])==v['count'],v['before'][:100];expected=expected.replace(v['before'],v['after'])
 assert(r/path).read_text()==expected,'Unlisted product change: '+path
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle);data=(r/'examples/editor-home/ui/feature-authoring.js').read_text().encode();pattern=r'("feature-authoring.js":\{"file":"feature-authoring.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed==paths|{bundle},changed
for file in ['v666-code-editor-copy.json','v666-value-guidance-copy.json']:
 for v in json.loads((r/'docs'/file).read_text())['changes']:assert(r/'examples/editor-home/ui/feature-authoring.js').read_text().count(v['after'])==v['count']
print('PASS exact ordinary-name recovery and 3 guidance messages/3 existing occurrences; previous completed features/layout/contracts unchanged')
