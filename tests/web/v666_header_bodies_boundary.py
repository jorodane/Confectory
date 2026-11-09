"""Pin the mixed presentation boundary while preserving source/ABI/permission leases."""
import ast,hashlib,json,pathlib,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-header-bodies-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','examples','*.celem','*.cpack','*.css','*.html')
for n in ['targets/element-authoring/InformationDefinitions.cs','targets/element-authoring/InformationFunctionContracts.cs','packs/change-set/ConfirmReviewed.csbody','targets/element-authoring/Program.cs']:assert read(n)==old(n),n
s=read('targets/element-authoring/InformationFunctionBodyBatch.cs');assert 'value.Count==2'in s and '"description" or "icon"'in s and 'edits.Length is >=2 and <=8'in s
s=read('targets/element-authoring/InformationFunctionBodyGuards.cs');assert 'InformationFunctionBodyBatch.Edits(changes)'in s and 'receipt["version"]?.GetValue<int>()!=3'in s and 'result.Count is <1 or >240'in s and not any(t in s for t in ['File.Read','File.Write','Process.Start','Directory.Get'])
s=read('packs/edit-workspace/ValidateReviewSelection.csbody');assert '["action"]="headers"'in s and 'calls.Read.Invoke(handle,implementation!.ToString())'in s
s=read('packs/save/ApplySlots.csbody');assert 'OriginalRawSources();OriginalNativeSources();try{calls.WriteChecked.Invoke'in s and 'calls.Snapshot.Invoke(path)[2]!=source["hash"]!.ToString()'in s and 'Native source cannot traverse links'in s and 'proof.Count+readGuards.Count>240'in s
p=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(p)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();assert all('function '+n+'('in s for n in ['renderFeatureDefinition','openOwnFunctionPopover','renderFunctionSignatureEditor'])
tree=ast.parse(read('tools/verify_desktop.py'));assert len([n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'header-bodies'"])==3
print('PASS only original owner description/icon compose with same-contract native bodies; authored UI, public/native ABI, permissions, save receipt version and final source lease unchanged')
