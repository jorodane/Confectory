"""One authored menu; no storage migration, source/permission rewrite or new size policy."""
import sys,pathlib,json,subprocess,hashlib,zipfile,re,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-original-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
n='packs/project-resources/Layout.csbody';s=read(n);a=s.index('// Explicit original-file opening');b=s.index('if(operation is "read"',a);branch=s[a:b];assert s[:a]+s[b:]==old(n);assert 'CommitPlan.Invoke'not in branch and 'WriteAtomic'not in branch
for t in ['size is <0 or >4194304','1048576','resource_content_integrity','resource_read_changed','content["current"]','original["data"]','metadata["name"]','contentSnapshots','descriptionsSnapshot','identitySnapshot','deletionsSnapshot']:assert t in branch,t
n='packs/editor-home-model/Resources.csbody';assert read(n).replace('"read-file" or "read-file-part" or ','')==old(n)
n='examples/editor-home/WebInvoke.csbody';s=read(n);a=s.index('if(endpoint is "readProjectResourceFile"');b=s.index('if(endpoint=="readProjectResourceOfficePart"',a);assert s[:a]+s[b:]==old(n);assert s[a:b].count('calls.Cancelled.Invoke(cancellation)')==2
n='examples/editor-home/WebBundle.csbody';parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);current= parse(read(n));prior=parse(old(n));assert set(current)-set(prior)=={'resource-original.js'}
for key in current:
 if key not in ['resource-original.js','resource-layout.js','resource-browser.js']:assert current[key]==prior[key],key
for key in ['resource-original.js','resource-layout.js','resource-browser.js']:
 raw=read('examples/editor-home/ui/'+key).encode();assert current[key]['canonicalSize']==len(raw)and current[key]['canonicalSha256']==hashlib.sha256(raw).hexdigest()
s=read('examples/editor-home/ui/resource-original.js');assert 'view.call'not in s and 'localStorage'not in s and 'fetch('not in s
for token in ['readProjectResourceFilePart','readProjectResourceFile','opener=null','300000','urls.size+jobs.size>=4','resourceOriginalMime','controller.abort()','pagehide','tab.closed','blank(tab)','await refresh()']:assert token in s,token
assert not git('diff','--name-only',d['baseCommit'],'--','*.celem','*.cpack','packs/file-stream','src','targets','*.css')
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();a=app.index('async function openResourceOriginal');b=app.index('function openResourceParent',a);flow=app[a:b]
 for t in ['resourceBlob(project.id,item.id)',"tab.opener=null","300000","text/plain","원본 파일 열기"]:assert t in(flow if t!='원본 파일 열기'else app),t
 assert "objectStore('files').get(ownerId+':'+id)"in app and 'async function writeResourceContent'in app
p=read('tools/verify_desktop.py');t=ast.parse(p);arms=[n for n in ast.walk(t)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-original'"];assert len(arms)==3
for x in ['resource_original_copy','resource_original_parts_cas','resource_original_test','v666_resource_original.mjs','resource_content','resource_total','v666_resource_original_ui.py']:assert x in'\n'.join(ast.unparse(n)for n in arms),x
print('PASS authored current-file menu only, exact existing read/save/storage/CAS/ABI/permissions/layout, bounded observations/popup lifecycle and final independent dispatch')
