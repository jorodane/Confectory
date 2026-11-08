"""Finite accumulated-copy scope; immutable original/ABI/UI and atomic boundary preserved."""
import sys,pathlib,json,subprocess,hashlib,ast,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-resource-total-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles'])=={'packs/project-resources/Request.csbody','packs/project-resources/Layout.csbody','packs/project-resources/README.md'},changed
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
old=lambda n:git('show',d['baseCommit']+':'+n);current=lambda n:(r/n).read_text()
n='packs/project-resources/Layout.csbody';assert current(n)==old(n).replace('Snapshot.Invoke(filesPath,6291456)','Snapshot.Invoke(filesPath,12582912)')
n='packs/project-resources/Request.csbody';s=current(n);before=old(n)
# Existing item canonical bytes/hash/import proof, source/project identity, replay and final CAS are exact.
for start,end in [('System.Text.Json.Nodes.JsonObject Item(', 'System.Text.Json.Nodes.JsonObject Validate('),('var input=System.Text.Json.Nodes.JsonNode.Parse(payload)', 'bool prepare='),('string ImportReply(', 'string serialized=candidate.ToJsonString();Validate(serialized);')]:
 a=s.split(start)[1].split(end)[0];b=before.split(start)[1].split(end)[0]
 if start=='string ImportReply(':a=a.split('// Only an explicit successful import')[0]
 assert a==b,(start,end)
assert s.split('string serialized=candidate.ToJsonString();Validate(serialized);')[1]==before.split('string serialized=candidate.ToJsonString();Validate(serialized);')[1]
for token in ['fileLimit=4194304,importLimit=4194304,legacyTotalLimit=4194304,totalLimit=8388608','storeLimit=12582912','version is not (1 or 2)','version==1?legacyTotalLimit:totalLimit','["importBytes"]=importLimit','batch&&selectedBytes>importLimit','>legacyTotalLimit)candidate["version"]=2','payload.Length>(operation is "import" or "import-many" or "prepare-import-many"?6000000:1500000)']:assert token in s,token
assert 'plan.Length>16777216'in current('packs/file-stream/CommitPlan.csbody')
assert not git('diff','--name-only',d['baseCommit'],'--','*.celem','*.cpack','packs/file-stream','src','targets','examples')
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:app=z.read('Confectory-v666/dist/app.js').decode();assert 'importResourceFiles'in app and'resourceDatabase'in app
p=current('tools/verify_desktop.py');t=ast.parse(p);branches=[n for n in ast.walk(t)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'resource-total'"];assert len(branches)==3
for token in ['v666_resource_total_copy.py','resource_total_cas','resource_total_compatibility','v666_resource_total_ui.py','v666_resource_xlsx_parts_ui.py']:assert token in'\n'.join(ast.unparse(n)for n in branches),token
print('PASS explicit accumulated8MiB/v2 only, v1 unchanged4MiB and no downgrade; per-file/selection4MiB64, upload6MB/RPC2MiB/CommitPlan16MiB, immutable bytes/IDs/receipts, finalCAS/source ownership/UI/permissions and independent final dispatch preserved')
