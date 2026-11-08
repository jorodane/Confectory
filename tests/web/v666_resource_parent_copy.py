"""Authored parent navigation; view root is presentation, never source authority."""
import sys,pathlib,subprocess,json,re,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-parent-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
n='packs/project-resources/Layout.csbody';s=read(n);a=s.index('// Parent navigation observes');b=s.index('if(operation=="load")',a);branch=s[a:b];assert s[:a]+s[b:]==old(n)
for token in ['Keys(request,"id","hash","revision")','resource_read_changed','locationMetadata','containing?.DeepClone()','contentSnapshots','descriptionsSnapshot','deletionsSnapshot']:assert token in branch,token
assert 'CommitPlan'not in branch and 'WriteAtomic'not in branch
n='packs/editor-home-model/Resources.csbody';assert read(n).replace('"locate" or ','')==old(n)
n='examples/editor-home/WebInvoke.csbody';s=read(n);a=s.index('if(endpoint=="readProjectResourceLocation")');b=s.index('if(endpoint is "readProjectResourceFile"',a);assert s[:a]+s[b:]==old(n);assert s[a:b].count('calls.Cancelled.Invoke(cancellation)')==2
n='examples/editor-home/WebBundle.csbody';parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old(n));current=parse(read(n));assert set(current)-set(prior)=={'resource-parent.js'}
allowed={'resource-parent.js','resource-browser.js','resource-layout.js','v508-runtime.js'}
for name in current:
 if name not in allowed:assert current[name]==prior[name],name
for name in allowed:
 raw=read('examples/editor-home/ui/'+name).encode();assert current[name]['canonicalSize']==len(raw)and current[name]['canonicalSha256']==hashlib.sha256(raw).hexdigest(),name
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','*.celem','*.cpack','*.css','packs/file-stream','packs/project-resources/Request.csbody','examples/editor-home/ui/workspace.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-original.js')
s=read('examples/editor-home/ui/resource-parent.js');assert 'view.call'not in s and 'localStorage'not in s and 'data'not in s.split('const jobs=')[1]
for token in ['validateResourceLocation(await read()','controller.abort()','prior.key===key','pagehide','api.open(final.item,final.parent)']:assert token in s,token
s=read('examples/editor-home/ui/v508-runtime.js');assert 'function openResourceParent(item,parent)'in s and 'resourceBrowser.navigate(w,parentId,item.id)'in s and 'workspaceRuntime.focusWorkspaceWindow(w)'in s
s=read('examples/editor-home/ui/resource-layout.js');assert "['상위 카테고리 열기'"in s and 'row(base?folder(base):null,0)'in s and "...(base?[]:[{id:null,name:'ProjectPack'}])"in s and 'row?.focus({preventScroll:true})'in s
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();a=s.index('function openResourceParent');b=s.index('function resourceRoot',a);assert "browserInstanceKey('tree','resource',parent),parent,null,true"in s[a:b]and 'navigateResources(view,parent,item.id)'in s[a:b]
 assert "['상위 카테고리 열기',()=>openResourceParent(item)]"in s
p=read('tools/verify_desktop.py');t=ast.parse(p);arms=[n for n in ast.walk(t)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-parent'"];assert len(arms)==3
for token in ['resource_parent_copy','resource_parent.mjs','resource_parent_cas','resource_parent_test','resource_parent_ui','resource_layout_ui','resource_original_ui']:assert token in'\n'.join(ast.unparse(n)for n in arms),token
print('PASS authored independent parent-rooted browser/file-folder-root selection, fresh metadata/final read, unchanged source/storage/ABI/permission/layout runtime, existing key persistence and final dispatch')
