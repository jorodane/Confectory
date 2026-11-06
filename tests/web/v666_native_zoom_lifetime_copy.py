"""Exact general Blueprint read/menu lifetime deltas and canonical pins only."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if(r/'docs/v666-native-read-close-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_native_read_close_copy.py'),str(r)],check=True);sys.exit(0)
d=json.loads((r/'docs/v666-native-zoom-lifetime-delta.json').read_text());old=lambda p:subprocess.check_output(['git','show',d['baseCommit']+':'+p],cwd=r,text=True)
expected=old('examples/editor-home/WebBundle.csbody');changed=set()
for c in d['changes']:
 assert old(c['path']).count(c['before'])==1 and(r/c['path']).read_text()==old(c['path']).replace(c['before'],c['after']);changed.add(c['path']);name=pathlib.Path(c['path']).name;data=(r/c['path']).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[a-f0-9]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1
assert(r/'examples/editor-home/WebBundle.csbody').read_text()==expected;changed.add('examples/editor-home/WebBundle.csbody');actual=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert actual==changed,actual
print('PASS exact general Blueprint readonly entry/menu lifetime guards and resource pins; original layout, C#/contracts, ownership/permissions, source mutations, CAS/Review/Confirm/Undo unchanged')
