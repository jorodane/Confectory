"""Finite original GIF path, byte preservation of decoder/layout/storage/permission contracts."""
import pathlib,json,subprocess,hashlib,zipfile,ast,sys
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-gif-parts-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
expected={'examples/editor-home/WebBundle.csbody','examples/editor-home/ui/resource-images.js','packs/project-resources/Layout.csbody','packs/project-resources/README.md'}
assert set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())==set(d['productFiles'])==expected
for name,digest in d['productFiles'].items():assert hashlib.sha256((r/name).read_text().encode()).hexdigest()==digest,name
js='||bytes[0]===71&&bytes[1]===73&&bytes[2]===70&&bytes[3]===56&&(bytes[4]===55||bytes[4]===57)&&bytes[5]===97'
native='||raw.Length>=6&&raw[0]==71&&raw[1]==73&&raw[2]==70&&raw[3]==56&&(raw[4]==55||raw[4]==57)&&raw[5]==97'
old=git('show',d['baseCommit']+':examples/editor-home/ui/resource-images.js');new=(r/'examples/editor-home/ui/resource-images.js').read_text();assert new==old.replace('bytes[11]===80))','bytes[11]===80'+js+'))');assert new.split(' const view=',1)[1]==old.split(' const view=',1)[1]
old=git('show',d['baseCommit']+':packs/project-resources/Layout.csbody');new=(r/'packs/project-resources/Layout.csbody').read_text();assert new==old.replace('Only bounded PNG/JPEG/BMP/WebP\n','Only bounded PNG/JPEG/BMP/WebP/GIF\n').replace('raw[11]==80)rasterBytes=raw;','raw[11]==80'+native+')rasterBytes=raw;')
old=git('show',d['baseCommit']+':packs/project-resources/README.md');new=(r/'packs/project-resources/README.md').read_text();assert new==old.replace('Large stored PNG/JPEG/BMP/static WebP copies','Large stored PNG/JPEG/BMP, static WebP and bounded GIF copies').replace('docs/V7_RESOURCE_WEBP_PARTS.md for compatibility','docs/V7_RESOURCE_WEBP_PARTS.md and docs/V7_RESOURCE_GIF_PARTS.md for compatibility')
assert not git('diff','--name-only',d['baseCommit'],'--','*.celem','*.cpack')
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');before=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==before[0]and p[2]==before[2];bundle=json.loads(p[1]);prior=json.loads(before[1]);assert set(bundle)==set(prior)
for name,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),name
 if name!='resource-images.js':assert row==prior[name],name
ref=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(ref.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(ref)as z:
 s=z.read('Confectory-v666/dist/resource-preview.js').decode();assert 'blob.size>64*1024*1024'in s and "if(item.kind==='image'){url=URL.createObjectURL(blob)"in s
 app=z.read('Confectory-v666/dist/app.js').decode();at=app.index('function resourceKind');assert 'gif'in app[at:at+1600]
branches=[n for n in ast.walk(ast.parse((r/'tools/verify_desktop.py').read_text()))if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-gif-parts'"];assert len(branches)==3
calls=[ast.unparse(n)for b in branches for statement in b.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-resource-gif-parts-boundary'","work.run('packaged-resource-gif-parts'","work.run('restored-resource-gif-parts'"]:assert sum(token in c for c in calls)==1
subprocess.run(['node','--check',str(r/'examples/editor-home/ui/resource-images.js')],check=True)
print('PASS exact3runtime+README additive GIF87a/89a encoded transport; original GIF parser/frame-weighted budgets/bitmap lifetime/pixel lease/DOM, bundle keys and native permissions/fullSHA/final-read/storage/CAS/public/override source contracts unchanged; canonical assets and three final suite routes')
