"""Closed V7 text-view slice, exact authored renderer/CSS and read-only bridge."""
import pathlib,sys,json,hashlib,subprocess,zipfile
r=pathlib.Path(sys.argv[1]);
if (r/'docs/v666-resource-layout-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_resource_layout_copy.py'),str(r)],check=True);raise SystemExit(0)
d=json.loads((r/'docs/v666-resource-preview-delta.json').read_text());git=lambda *args:subprocess.check_output(['git',*args],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for path,digest in d['productFiles'].items():assert hashlib.sha256((r/path).read_text().encode()).hexdigest()==digest,path
assert not any(path.startswith(('src/','targets/','packs/'))for path in changed)
previous=json.loads((r/'docs/v666-resource-import-delta.json').read_text())
for path,digest in previous['productFiles'].items():assert hashlib.sha256(git('show',d['baseCommit']+':'+path).encode()).hexdigest()==digest,path
bridge=(r/'examples/editor-home/WebInvoke.csbody').read_text();start=bridge.index('if(endpoint=="readProjectResource"){');end=bridge.index('if(endpoint=="projectResources"){',start);read=bridge[start:end]
assert 'args.Count!=3' in read and 'p.Key is not ("project" or "id" or "hash")' in read and 'calls.Resources.Invoke(context,"read",args.ToJsonString())' in read and read.count('calls.Cancelled.Invoke(cancellation)')==2
assert bridge[:start]+bridge[end:]==git('show',d['baseCommit']+':examples/editor-home/WebInvoke.csbody')
new=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert new[0]==old[0]and new[2].replace('new System.Text.Json.Nodes.JsonArray("readProjectResource","runWindowRead"','new System.Text.Json.Nodes.JsonArray("runWindowRead"')==old[2]
bundle=json.loads(new[1]);before=json.loads(old[1]);assert set(bundle)-set(before)=={'resource-previews.js'}and not set(before)-set(bundle)
for name,row in bundle.items():
 if name in ['resource-previews.js','resource-browser.js','v508-runtime.js','workspace-host.js','style.css']:
  raw=(r/'examples/editor-home/ui'/name).read_text().encode();assert row['canonicalSha256']==hashlib.sha256(raw).hexdigest()and row['canonicalSize']==len(raw)
 else:assert row==before[name],name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==previous['referenceSha256']
with zipfile.ZipFile(reference)as z:
 original=z.read('Confectory-v666/dist/resource-preview.js').decode();source=(r/'examples/editor-home/ui/resource-previews.js').read_text()
 for line in original.splitlines():
  if line.startswith('const textExtensions='):assert line in source
 codec="bytes[0]===255&&bytes[1]===254?'utf-16le':bytes[0]===254&&bytes[1]===255?'utf-16be':'utf-8',pre=element('pre',new TextDecoder(encoding).decode(bytes),'resource-document-text')";assert codec in original and codec in source
 css=z.read('Confectory-v666/dist/style.css').decode();prefixes=('.resource-file-editor{','.resource-editor-body{','.resource-preview-panel{','.resource-preview-toolbar{','.resource-preview-toolbar strong{','[data-resource-preview-controls]{','.resource-preview{','.resource-preview.is-preview-message{','.resource-preview.is-preview-message p{','.resource-preview:is(','.resource-preview pre{','.resource-preview-status{','.resource-preview-status:empty{','.resource-settings{','.resource-settings h3{','.resource-settings .resource-storage-note{','.resource-content-actions{','.resource-name-label','.resource-description-label{','@container resource-editor','.resource-editor-heading{','.resource-editor-heading>','.resource-file-editor>.window-title')
 expected=git('show',d['baseCommit']+':examples/editor-home/ui/style.css')+'\n/* Authored v666 read-only resource text preview. */\n'+'\n'.join(line for line in css.splitlines()if line.startswith(prefixes))+'\n';assert (r/'examples/editor-home/ui/style.css').read_text()==expected
assert "api.view.observe('readProjectResource'" in source and 'api.view.call('not in source and 'api.persist(' in source
assert 'resourceOwner' in source and 'token.controller.abort()' in source and 'token.generation===api.view.generation' in source
print('PASS authored bounded read-only text preview; source/asset schema/import receipts/contracts/permissions and original mutation lanes unchanged')
