"""Authored PDF renderer bytes/notices and closed asset-only native extension."""
import sys,pathlib,json,subprocess,hashlib,zipfile
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-resource-description-delta.json').exists():
 import runpy
 runpy.run_path(str(r/'tests/web/v666_resource_description_copy.py'),run_name='__main__');raise SystemExit
d=json.loads((r/'docs/v666-resource-pdf-delta.json').read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_bytes()if name.endswith(('.bcmap','.pfb','.ttf'))else(r/name).read_text().encode()).hexdigest()==digest,name
allowed={'packs/web-ui/Open.csbody','examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/style.css','examples/editor-home/ui/resource-pdf.js','examples/editor-home/ui/resource-pdf-policy.js','examples/editor-home/ui/resource-pdf-worker.js'};prefix='examples/editor-home/ui/assets/vendor/pdfjs-dist-4.10.38/';assert all(name in allowed or name.startswith(prefix)for name in changed)
before=git('show',d['baseCommit']+':packs/web-ui/Open.csbody');now=(r/'packs/web-ui/Open.csbody').read_text();assert now.replace('AsObject().Count>384','AsObject().Count>256').replace('or "application/json" or "application/octet-stream"))throw new ArgumentException("Unsupported resource MIME")','or "application/json"))throw new ArgumentException("Unsupported resource MIME")')==before
for path in ['src','targets','packs/editor-home-model','packs/project-resources','packs/file-stream','packs/edit-workspace','packs/browser-host','examples/editor-home/WebInvoke.csbody','examples/editor-home/Main.celem','examples/editor-home/ui/resource-office.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-layout.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/v508-runtime.js']:assert not git('diff','--name-only',d['baseCommit'],'--',path),path
parts=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');prior=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert parts[0]==prior[0]and parts[2]==prior[2];bundle=json.loads(parts[1]);old=json.loads(prior[1]);new=set(bundle)-set(old);assert len(new)==187
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name not in new and name not in ['resource-previews.js','style.css']:assert row==old[name]
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 names={name.removeprefix('Confectory-v666/dist/')for name in z.namelist()if '/pdfjs-dist-4.10.38/'in name and not name.endswith('/')};assert len(names)==188;assert {name.removeprefix('examples/editor-home/ui/')for name in changed if name.startswith(prefix)}==names
 for name in names:assert (r/'examples/editor-home/ui'/name).read_bytes()==z.read('Confectory-v666/dist/'+name),name
 authored=z.read('Confectory-v666/dist/resource-preview.js').decode();css=z.read('Confectory-v666/dist/style.css').decode();current=(r/'examples/editor-home/ui/style.css').read_text();base=git('show',d['baseCommit']+':examples/editor-home/ui/style.css');assert current.startswith(base)
 for line in current[len(base):].splitlines():
  if line.startswith('.'):assert line in css,line
 for text in ['loadPdf','이전 페이지','다음 페이지','미리보기 배율','isEvalSupported:false','enableXfa:false']:assert text in authored,text
current=(r/'examples/editor-home/ui/resource-previews.js').read_text();previous=git('show',d['baseCommit']+':examples/editor-home/ui/resource-previews.js');start='  const read=async';end='    const mime=';assert current[current.index(start):current.index(end)]==previous[previous.index(start):previous.index(end)]
print('PASS exact original 188 PDF vendor/notices files, native asset count/MIME-only extension, same source/permission/read/CAS/override contracts and authored PDF controls/styles')
