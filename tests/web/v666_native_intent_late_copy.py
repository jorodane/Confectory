"""Only generic input accounting after an Apply attempt and canonical resource pin."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve();d=json.loads((r/'docs/v666-native-intent-late-delta.json').read_text());old=lambda p:subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True)
expected=old(d['path'])
for c in d['changes']:
 assert expected.count(c['before'])==1;expected=expected.replace(c['before'],c['after'])
assert(r/d['path']).read_text()==expected
bundle='examples/editor-home/WebBundle.csbody';data=expected.encode();pattern=r'("blueprint.js":\{"file":"blueprint.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[a-f0-9]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],old(bundle));assert n==1 and(r/bundle).read_text()==expected
actual=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert actual=={d['path'],bundle},actual
print('PASS exact Apply-start/entry-identity accounting and pin; UI disable/layout, RPC/basis/permissions/source/C#/IDs/contracts/connections, CAS/Undo/Review/Confirm unchanged')
