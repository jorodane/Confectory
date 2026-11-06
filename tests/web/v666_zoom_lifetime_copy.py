"""Bounded presentation-only delta, including canonical web resource pin."""
import hashlib,json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve();d=json.loads((r/'docs/v666-zoom-lifetime-delta.json').read_text())
old=lambda path:subprocess.check_output(['git','show',d['baseCommit']+':'+path],cwd=r,text=True)
assert old(d['path']).count(d['before'])==1;assert(r/d['path']).read_text()==old(d['path']).replace(d['before'],d['after'])
bundle='examples/editor-home/WebBundle.csbody';data=(r/d['path']).read_text().encode();pattern=r'("workspace.js":\{"file":"workspace.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")'
expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],old(bundle));assert n==1 and(r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={d['path'],bundle},changed
print('PASS exact Workspace menu/project ownership checks and canonical pin only; markup/geometry, wheel policy, source/C#/contracts, permissions, CAS/Review/Confirm/Undo unchanged')
