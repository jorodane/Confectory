"""Fixed authored storage-name/source save, exact product delta and final suite provenance."""
import ast,hashlib,json,pathlib,re,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-alias-source-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','*.celem','*.cpack','*.css','*.html')
for n in ['examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/code-editor.js','examples/editor-home/ui/resource-browser.js','examples/editor-home/ui/set-authoring.js','targets/element-authoring/BlueprintAliases.cs','packs/pack-workspace/Review.csbody']:
 if(r/n).exists():assert read(n)==old(n),n
parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old('examples/editor-home/WebBundle.csbody'));now=parse(read('examples/editor-home/WebBundle.csbody'));assert set(now)==set(prior)
for name in now:
 if name!='feature-authoring.js':assert now[name]==prior[name],name
raw=read('examples/editor-home/ui/feature-authoring.js').encode();v=now['feature-authoring.js'];assert v['file']=='feature-authoring.js'and v['bytePolicy']=='utf8-lf-v1'and v['canonicalSize']==len(raw)and v['canonicalSha256']==hashlib.sha256(raw).hexdigest()
p=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(p)as z:
 s=z.read('Confectory-v666/dist/blueprint.js').decode()
 for token in ['variable.name=name','graph.localVariables.push({id:uid(),nodeId:id,port,name})','remember();updatePinLabels();return true']:assert token in s,token
s=read('tools/verify_desktop.py');tree=ast.parse(s);arms=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'alias-source'"];assert len(arms)==3
for token in ['alias_source_copy','alias_source_guard','alias_source_api','alias_source_ui','text_pair_recovery_ui']:assert token in'\n'.join(ast.unparse(n)for n in arms),token
print('PASS fixed authored name/body behavior; exact UI/bundle/checkpoint dispatcher delta; unchanged ABI, code editor, storage helper, source authority and permission contracts; LF/CRLF/package/restore dispatch')
