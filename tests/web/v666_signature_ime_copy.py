"""Bound the shared key-routing fix; preserve source authority, layout and native ABI."""
import ast,hashlib,json,pathlib,re,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-signature-ime-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','*.celem','*.cpack','*.css','*.html');n='examples/editor-home/ui/element-functions.js';prior=old(n);a=prior.index('export function openFunctionSignatureEditor(');body=prior[a:];needle="document.addEventListener('keydown',e=>{if(e.key==='Escape'";assert body.count(needle)==2;expected=prior[:a]+body.replace(needle,"document.addEventListener('keydown',e=>{if(e.isComposing||e.keyCode===229)return;if(e.key==='Escape'");assert read(n)==expected
parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old('examples/editor-home/WebBundle.csbody'));now=parse(read('examples/editor-home/WebBundle.csbody'));assert set(now)==set(prior)
for name in now:
 if name!='element-functions.js':assert now[name]==prior[name],name
raw=read(n).encode();v=now['element-functions.js'];assert v['file']=='element-functions.js'and v['bytePolicy']=='utf8-lf-v1'and v['canonicalSize']==len(raw)and v['canonicalSha256']==hashlib.sha256(raw).hexdigest()
p=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(p)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();assert 'function openOwnFunctionPopover('in s and "root.querySelector('[data-detail-close]').onclick=root.querySelector('[data-detail-cancel]').onclick=close"in s
s=read('tools/verify_desktop.py');tree=ast.parse(s);arms=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'signature-ime'"];assert len(arms)==3
assert 'v666_signature_ime_ui.py'in'\n'.join(ast.unparse(n)for n in arms)
print('PASS exact two shared IME Escape guards and bundle hash only; original ordinary cancel/submit/pointer/ownership callbacks, native contracts, permissions, layout and source syntax unchanged')
