"""Pin the owned native import/body boundary and the existing final receipt lease."""
import ast,hashlib,json,pathlib,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-body-imports-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','examples','*.cpack','*.css','*.html')
n='packs/save/ApplySlotsBody.celem'
assert read(n).replace('import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;\n','')==old(n)
for n in ['packs/change-set/ConfirmReviewed.csbody','targets/element-authoring/InformationFunctionBatch.cs','targets/element-authoring/InformationFunctionContracts.cs','src/Confectory.Core/Parser.cs']:
 # Compare only real original paths; the source lock is enforced by the changed set above.
 if (r/n).is_file():assert read(n)==old(n),n
s=read('targets/element-authoring/InformationFunctionBodyBatch.cs');assert 'd.Imports.Count!=0'not in s and 'dependency.Kind!="function"'in s and '!import.Signature.Matches(dependency.Signature)'in s and 'dependency.Parent is not null'in s
s=read('targets/element-authoring/InformationFunctionBodyGuards.cs')
for term in ['JsonNode.DeepEquals(mapping["before"],row["signature"])','implementation.Parent is not null','implementation.Bodies.Count!=1','units.Count>2048','result.Count is <1 or >240','receipt["version"]?.GetValue<int>()!=3','guards.Count!=expected.Count']:
 assert term in s,term
assert not any(term in s for term in ['File.Read','File.Write','Directory.Get','Process.Start'])
s=read('packs/save/ApplySlots.csbody');assert 'proof.Count+readGuards.Count>240'in s and 'informationBodyGroupGuards'in s
s=read('packs/edit-workspace/ValidateReviewSelection.csbody');assert 'informationBodyGroupGuards'in s and 'calls.Read.Invoke(handle,body.Key[..at])'in s
s=read('packs/change-set/ConfirmReviewed.csbody');assert 'readGuards'in s
p=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(p)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();assert all('function '+n+'('in s for n in ['openOwnFunctionPopover','renderFunctionSignatureEditor','renderFeatureDefinition'])
tree=ast.parse(read('tools/verify_desktop.py'));arms=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'body-imports'"];assert len(arms)==3
print('PASS owned same-contract imported native body group; authored UI/CSS/HTML/JS, ABI/code generation, permission and final source lease unchanged; version3 owned read guards reused')
