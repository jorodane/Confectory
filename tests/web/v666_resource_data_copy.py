"""Exact source delta and authored sort; native data/permission contract is unchanged."""
import sys,pathlib,json,hashlib,subprocess,re,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-data-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','*.celem','*.cpack','*.css','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/resource-description.js','examples/editor-home/ui/resource-filter.js','examples/editor-home/ui/resource-keyboard.js','examples/editor-home/ui/resource-selection.js','examples/editor-home/ui/resource-parent.js','examples/editor-home/ui/resource-original.js')
n='examples/editor-home/WebBundle.csbody';parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old(n));now=parse(read(n));assert set(now)==set(prior)
for name in now:
 if name not in ['resource-browser.js','resource-layout.js']:assert now[name]==prior[name],name
for name in ['resource-browser.js','resource-layout.js']:
 raw=read('examples/editor-home/ui/'+name).encode();v=now[name];assert v['file']==name and v['mime']=='text/javascript'and v['bytePolicy']=='utf8-lf-v1'and v['canonicalSize']==len(raw)and v['canonicalSha256']==hashlib.sha256(raw).hexdigest()
s=read('examples/editor-home/ui/resource-browser.js')
for token in ['browser-data-identity','browser-data-fields','browser-data-edit','input.readOnly=true','bindDataName(w,name,row,owner,token)','cancelNameActivation(w)']:assert token in s,token
s=read('examples/editor-home/ui/resource-layout.js')
for token in ['function bindDataName','setTimeout(','},260)','basis()===job.basis','clearTimeout(job.timer)','cancelNameActivation(w)','[data-resource-rename]']:assert token in s,token
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();a=s.index('function renderResourceItems');b=s.index('\nfunction ',a+1);s=s[a:b]
 for token in ['browser-data-identity','browser-data-name','browser-data-fields','browser-data-edit','data-resource-name','data-resource-open','readonly','종류','크기','nameRenameTimer','260']:assert token in s,token
s=read('tools/verify_desktop.py');tree=ast.parse(s);arms=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-data'"];assert len(arms)==3
for token in ['resource_data_copy','resource_data_ui','resource_sort_ui','resource_keyboard_ui','resource_filter_ui','resource_parent_ui','resource_layout_ui','resource_original_ui']:assert token in'\n'.join(ast.unparse(n)for n in arms),token
print('PASS authored Data controls/260ms name activation; exact three UI assets; unchanged CSS/native data/ABI/permissions/CAS; source, generated and restored dispatch')
