"""Source/layout boundary and exact authored finite menu, independent LF/CRLF checkouts."""
import sys,pathlib,json,subprocess,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-resolutions-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
actual=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert actual==set(d['productFiles']),actual
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
for name in ['src','targets','packs','examples/qhd-output','examples/fhd-output','examples/hd-output','examples/resizable-output','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/index.html','examples/editor-home/ui/style.css','examples/editor-home/ui/run-surface.js','examples/editor-home/ui/run-presets.js','examples/editor-home/ui/run-auto-fit.js']:assert not git('diff','--name-only',d['baseCommit'],'--',name),name
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:authored=z.read('Confectory-v666/dist/app.js').decode()
def table(s):return json.loads(s.split('runPreviewResolutions=',1)[1].split(';',1)[0].replace("'",'"'))
s=(r/'examples/editor-home/ui/run-windows.js').read_text();expected=table(authored);assert table(s)==expected and sum(len(items)for _,items in expected)==15
assert len({v for _,items in expected for v,_ in items})==15
assert 'fixedResolutionValues.has(mode)'in s and 'option.disabled=!validSize()||!validDimensions(width,height)'in s
old=git('show',d['baseCommit']+':examples/editor-home/ui/run-windows.js')
# Existing output, command, owner, cancellation, auto, preset/CAS and close paths stay byte-identical.
for a,b in [('async function requestSize(',"const screen="),('presetName.oninput=',"const resize=")]:
 if a in old:assert s.split(a,1)[1].split(b,1)[0]==old.split(a,1)[1].split(b,1)[0],a
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==old[0]and p[2]==old[2];bundle=json.loads(p[1]);before=json.loads(old[1]);assert set(bundle)==set(before)
for n,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),n
 if n!='run-windows.js':assert row==before[n],n
tree=ast.parse((r/'tools/verify_desktop.py').read_text());branches=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'run-resolutions'"];assert len(branches)==3
calls=[ast.unparse(n)for b in branches for statement in b.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-run-resolutions-'","work.run('packaged-run-resolutions'","work.run('restored-run-resolutions'"]:assert sum(token in c for c in calls)==1,token
print('PASS original15 fixed options/groups/order/labels; only menu and canonical asset changed; source/native/public contracts, owner/permissions/CAS/layout untouched; LF/CRLF and fresh package/full restore dispatch')
