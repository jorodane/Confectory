"""Exact authored fullscreen integration; execution, permissions and completed editing stay byte-identical."""
import hashlib,json,pathlib,re,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((r/'docs/v666-run-fullscreen-delta.json').read_text())
def old(n):return subprocess.check_output(['git','show',plan['baseCommit']+':'+n],cwd=r,text=True)
for name in {v['path']for v in plan['deltas']}:
 expected=old(name)
 for v in (d for d in plan['deltas']if d['path']==name):assert expected.count(v['before'])==v['count'];expected=expected.replace(v['before'],v['after'])
 assert (r/name).read_text()==expected,name
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle)
for name,mime in [(name,'text/javascript')for name in ['run-windows.js','workspace.js','window-documents.js','v508-runtime.js']]+[('style.css','text/css')]:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"'+re.escape(mime)+'","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,count=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert count==1
assert (r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={'examples/editor-home/ui/'+name for name in ['run-windows.js','workspace.js','window-documents.js','v508-runtime.js','style.css']}|{bundle},changed
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 css=z.read('Confectory-v666/dist/style.css').decode()
 for row in plan['referenceCss']:assert row in css
for name in ['examples/editor-home/ui/feature-authoring.js','packs/pack-workspace/Blueprint.csbody','packs/editor-home-model/RunWindows.csbody']:assert (r/name).read_text()==old(name),name
for name in ['run-windows.js','workspace.js','window-documents.js','v508-runtime.js']:subprocess.run(['node','--check',str(r/'examples/editor-home/ui'/name)],check=True)
print('PASS exact Run presentation/native stacking/document-close/placement adaptations and canonical resources only; authored CSS source, process/lease/permission contracts, window geometry persistence and all completed editor save code unchanged')
