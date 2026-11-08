"""Exact UI-only delta and original authored kinds; no native ABI/permission migration."""
import sys,pathlib,json,hashlib,subprocess,re,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-filter-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','*.celem','*.cpack','*.css','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/workspace.js','examples/editor-home/ui/resource-parent.js','examples/editor-home/ui/resource-original.js')
n='examples/editor-home/ui/workspace-host.js';assert read(n).replace("['resourceFilter','resourceSelections'","['resourceSelections'")==old(n)
n='examples/editor-home/ui/resource-layout.js';assert read(n).replace("if(selection)w.meta.resourceFilter='all';",'')==old(n)
n='examples/editor-home/WebBundle.csbody';parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old(n));now=parse(read(n));assert set(now)-set(prior)=={'resource-filter.js'}
allowed={'resource-filter.js','resource-browser.js','resource-layout.js','workspace-host.js','resource-description.js'}
for name in now:
 if name not in allowed:assert now[name]==prior[name],name
for name in allowed:
 v=now[name];raw=(r/'examples/editor-home/ui'/name).read_text().encode();assert v['file']==name and v['mime']=='text/javascript'and v['bytePolicy']=='utf8-lf-v1'and v['canonicalSize']==len(raw)and v['canonicalSha256']==hashlib.sha256(raw).hexdigest(),name
n='examples/editor-home/ui/resource-description.js';s=read(n);start=s.index('canRebind:');end=s.index('active:',start);assert s[:start]+s[end:]==old(n);assert 'connected.every(b=>b.orphan)'in s and 'item.descriptionGeneration===d.generation'in s
s=read('examples/editor-home/ui/resource-filter.js');assert 'api.'not in s and 'fetch'not in s and 'localStorage'not in s
s=read('examples/editor-home/ui/resource-browser.js')
for t in ['resourceMatchesFilter(row,w.meta.resourceFilter)','kind.onpointerdown=event=>{if(!canFilter())event.preventDefault();}','parents.retire(w);render(w);api.persist();',"kind.className='secondary resource-type-filter'",'w.resourceFilterMenu!==menuToken','!descriptions.active(w)','kept=selected.filter(id=>visible.has(id))','resourceFilterValue(w.meta.resourceFilter)]'] :assert t in s,t
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();assert "[['all','모든 자료'],['document','문서'],['image','그림'],['mesh','메시'],['file','기타 파일']]"in s and "filter==='all'||item.kind==='folder'||item.kind===filter"in s and "if(selection)w.meta.resourceFilter='all'"in s and 'sort.before(filter)'in s
s=read('tools/verify_desktop.py');t=ast.parse(s);arms=[n for n in ast.walk(t)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-filter'"];assert len(arms)==3,len(arms)
for token in ['resource_filter_copy','resource_filter.mjs','resource_filter_ui','resource_parent_ui','resource_layout_ui','resource_original_ui']:assert token in'\n'.join(ast.unparse(n)for n in arms),token
print('PASS original five kinds and control placement; six UI-only files; native source/permission/ABI/storage/CAS and existing parent/original modules unchanged; final three-suite dispatch')
