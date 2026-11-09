"""Bound retained native callers without changing UI, native ABI, ownership or final lease."""
import ast,hashlib,json,pathlib,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-native-callers-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True);read=lambda n:(r/n).read_text();old=lambda n:git('show',d['baseCommit']+':'+n)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed
for n,h in d['productFiles'].items():assert hashlib.sha256(read(n).encode()).hexdigest()==h,n
assert not git('diff','--name-only',d['baseCommit'],'--','src','examples','*.celem','*.cpack','*.css','*.html')
for n in ['targets/element-authoring/InformationFunctionContracts.cs','packs/save/ApplySlots.csbody','packs/change-set/ConfirmReviewed.csbody','targets/element-authoring/Program.cs']:assert read(n)==old(n),n
s=read('targets/element-authoring/InformationFunctionBodyBatch.cs');before=old('targets/element-authoring/InformationFunctionBodyBatch.cs');part='''    if(body.Value.SourceKind=="csharp"){
     if(units[d.Id+"/body:"+body.Key]?["kind"]?.ToString()!="body"||units[d.Id+"/body:"+body.Key]?["draft"] is null)throw new InvalidOperationException("Read every retained native caller body; no C# source is inferred");
     continue;
    }
''';assert s.replace(part,'')==before
s=read('targets/element-authoring/InformationFunctionBodyGuards.cs');assert 'functions.Contains(import.Id)'in s and 'body.SourceKind=="csharp"'in s and not any(t in s for t in ['File.Read','File.Write','Directory.Get','Process.Start']);assert 'receipt["version"]?.GetValue<int>()!=3'in s and 'result.Count is <1 or >240'in s
s=read('packs/edit-workspace/ValidateReviewSelection.csbody');assert 'unit.Key.StartsWith(state["namespace"]'in s and 'calls.Read.Invoke(handle,implementation.Key)'in s
p=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(p)as z:
 s=z.read('Confectory-v666/dist/app.js').decode();assert 'function renderFeatureDefinition('in s and 'function openOwnFunctionPopover('in s
s=read('examples/editor-home/ui/feature-authoring.js');assert "api.modal('구현 선택'"in s and 'button.dataset.informationBody=id'in s
assert "pathlib.Path(__file__).with_name('v536_information_shared_return_types_ui.py')"in read('tests/web/v666_native_callers_ui.py')
tree=ast.parse(read('tools/verify_desktop.py'));assert len([n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'native-callers'"])==3
print('PASS exact retained native caller branch and existing readGuard/cold header connection only; authored layout/chooser, ABI, source compiler, permission, save schema and final lease unchanged')
