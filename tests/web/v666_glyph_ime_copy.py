"""Bound the shared glyph Escape fix; preserve callbacks, native ABI and source authority."""
import ast,hashlib,json,pathlib,re,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-glyph-ime-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','*.celem','*.cpack','*.css','*.html')
n='examples/editor-home/ui/glyph-popover.js';prior=old(n);needle="document.addEventListener('keydown',e=>{if(e.key==='Escape'";assert prior.count(needle)==1;expected=prior.replace(needle,"document.addEventListener('keydown',e=>{if(e.isComposing||e.keyCode===229)return;if(e.key==='Escape'");assert read(n)==expected
parse=lambda s:json.loads(re.search(r'var resources=System.Text.Json.Nodes.JsonNode.Parse\("""(.*?)"""\)',s)[1]);prior=parse(old('examples/editor-home/WebBundle.csbody'));now=parse(read('examples/editor-home/WebBundle.csbody'));assert set(now)==set(prior)
for name in now:
 if name!='glyph-popover.js':assert now[name]==prior[name],name
raw=read(n).encode();v=now['glyph-popover.js'];assert v['file']=='glyph-popover.js'and v['bytePolicy']=='utf8-lf-v1'and v['canonicalSize']==len(raw)and v['canonicalSha256']==hashlib.sha256(raw).hexdigest()
p=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(p)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();assert 'function editIconValue('in s and "root.querySelector('[data-cancel]').onclick=()=>{close();anchor.focus({preventScroll:true})}"in s and 'id="object-icon-input"'in s
tree=ast.parse(read('tools/verify_desktop.py'));arms=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'glyph-ime'"];assert len(arms)==3 and 'v666_glyph_ime_ui.py'in'\n'.join(ast.unparse(n)for n in arms)
print('PASS single shared glyph/image Escape guard and pinned bundle only; original Apply, ordinary cancel, decode sequence/lifetime, permissions, native contracts and layout unchanged')
