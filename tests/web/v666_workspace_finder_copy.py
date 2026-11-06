"""Reviewed authored finder delta; native ownership and completed flows stay unchanged."""
import hashlib,json,pathlib,re,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((r/'docs/v666-workspace-finder-delta.json').read_text())
def old(n):return subprocess.check_output(['git','show',plan['baseCommit']+':'+n],cwd=r,text=True)
for name in {row['path']for row in plan['deltas']}:
 expected=old(name)
 for row in (v for v in plan['deltas']if v['path']==name):assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
 assert (r/name).read_text()==expected,name
for name,digest in plan['newFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
bundle='examples/editor-home/WebBundle.csbody';expected=old(bundle)
for name,mime in [('find.js','text/javascript'),('v508-runtime.js','text/javascript'),('style.css','text/css')]:
 data=(r/'examples/editor-home/ui'/name).read_text().encode();pattern='("'+re.escape(name)+'":\\{"file":"'+re.escape(name)+'","mime":"'+re.escape(mime)+'","bytePolicy":"utf8-lf-v1","canonicalSize":)\\d+(,"canonicalSha256":")[0-9a-f]+(")';expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],expected);assert n==1
name='workspace-finder.js';data=(r/'examples/editor-home/ui'/name).read_text().encode();anchor='"workspace.js":';expected=expected.replace(anchor,json.dumps(name)+':'+json.dumps(dict(file=name,mime='text/javascript',bytePolicy='utf8-lf-v1',canonicalSize=len(data),canonicalSha256=hashlib.sha256(data).hexdigest()),separators=(',',':'))+','+anchor);assert (r/bundle).read_text()==expected
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());expected_names={row['path']for row in plan['deltas']}|set(plan['newFiles'])|{bundle};tracked_new={n for n in plan['newFiles']if subprocess.run(['git','ls-files','--error-unmatch',n],cwd=r,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0};assert changed==expected_names-(set(plan['newFiles'])-tracked_new),changed
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 css=z.read('Confectory-v666/dist/style.css').decode()
 for row in plan['referenceCss']:assert row in css
for name in ['examples/editor-home/ui/feature-authoring.js','examples/editor-home/ui/workspace.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/run-windows.js','packs/pack-workspace/Blueprint.csbody','packs/editor-home-model/RunWindows.csbody']:assert (r/name).read_text()==old(name),name
for name in ['find.js','workspace-finder.js','v508-runtime.js']:subprocess.run(['node','--check',str(r/'examples/editor-home/ui'/name)],check=True)
print('PASS exact authored finder/markup/canonical resources and aria-hidden input exclusion only; original C#/native contracts/permissions/CAS/ReviewConfirm, completed source editing/Run controls and existing placed Ctrl+F lifecycle retained')
