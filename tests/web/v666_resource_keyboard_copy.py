"""Authored keyboard delta, exact UI asset set and unchanged native transaction contract."""
import sys,pathlib,json,hashlib,subprocess,re,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-keyboard-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','*.celem','*.cpack','*.css','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/workspace.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-selection.js','examples/editor-home/ui/resource-description.js','examples/editor-home/ui/resource-filter.js','examples/editor-home/ui/resource-parent.js','examples/editor-home/ui/resource-original.js','examples/editor-home/ui/resource-previews.js')
n='examples/editor-home/WebBundle.csbody';parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old(n));now=parse(read(n));assert set(now)-set(prior)=={'resource-keyboard.js'};allowed={'resource-keyboard.js','resource-browser.js','resource-layout.js'}
for name in now:
 if name not in allowed:assert now[name]==prior[name],name
for name in allowed:
 raw=read('examples/editor-home/ui/'+name).encode();v=now[name];assert v['file']==name and v['mime']=='text/javascript'and v['bytePolicy']=='utf8-lf-v1'and v['canonicalSize']==len(raw)and v['canonicalSha256']==hashlib.sha256(raw).hexdigest(),name
s=read('examples/editor-home/ui/resource-keyboard.js');assert 'api.'not in s and 'fetch'not in s and 'localStorage'not in s
for token in ['isComposing','keyCode===229','defaultPrevented','Object.hasOwn(actions,event.key)','ctrlKey||event.metaKey']:assert token in s,token
s=read('examples/editor-home/ui/resource-layout.js')
for token in ['const visible=api.rows(w)','!guard.current()||!guard.open()','w.resourceKeyboardDelete','resourceKeyboardAction(event)','event.repeat','guard.current())return;const command','api.pending(w)','api.open(row,()=>api.alive(w,owner,token)']:assert token in s,token
s=read('examples/editor-home/ui/resource-browser.js');assert 'w.body.contains(event.target)'in s and "event.target.closest?.('.window')!==w.el"in s and 'layoutControls.keydown(w,owner,token,event)'in s
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();a=s.index('function renderResourceBrowser');b=s.index('\nfunction ',a+1);s=s[a:b]
 for token in ['event.ctrlKey||event.metaKey',"event.key==='Enter'","event.key==='Delete'","event.key==='F2'","event.key==='Escape'",'resourceSelection(w)','deleteResource(selected)']:assert token in s,token
s=read('tools/verify_desktop.py');tree=ast.parse(s);arms=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-keyboard'"];assert len(arms)==3
for token in ['resource_keyboard_copy','resource_keyboard.mjs','resource_keyboard_ui','resource_filter_ui','resource_parent_ui','resource_layout_ui','resource_original_ui']:assert token in'\n'.join(ast.unparse(n)for n in arms),token
print('PASS original five list shortcuts, four UI-only assets, native ABI/permissions/storage/final CAS and completed input recovery unchanged; final three-suite dispatch')
