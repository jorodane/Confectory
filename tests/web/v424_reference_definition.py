"""The real metadata host resolves one explicit registered declaration, never code."""
import json,pathlib,subprocess,sys,tempfile

with tempfile.TemporaryDirectory(prefix='confectory-reference-') as directory:
 root=pathlib.Path(directory);pack=root/'api';pack.mkdir();project=root/'project.cpack';manifest='project Owner version "1" {registry Api "api/pack.cpack";registry Unused "/missing-must-not-read.cpack";dependency Api version "1";dependency Missing version "1";element Item object "Item.celem";}'
 project.write_text(manifest);source='object Owner::Item {use function Api::Fn;use implementation Api::Body;use object Missing::Item;use object Unused::Item;}'
 declaration='function Api::Fn (long value) -> long {description "Exact registered metadata";}'
 registered='pack Api version "2" {element Fn function "Fn.celem";element Body implementation "Body.celem";}'
 (pack/'pack.cpack').write_text(registered);(pack/'Fn.celem').write_text(declaration);(pack/'Body.celem').write_text('implementation Api::Body for Api::Fn (long value) -> long {body common "missing-never-read.csbody";}')
 def read(id,**overrides):
  request=dict(operation='referenceDefinition',project=str(project),manifest=manifest,sourceId='Owner::Item',text=source,id=id);request.update(overrides)
  proc=subprocess.run([sys.argv[1],sys.argv[2]],input=json.dumps(request),text=True,capture_output=True,check=True);reply=json.loads(proc.stdout);assert reply['ok'],reply;result=reply['result'];assert result['readOnly'] is True and str(root) not in json.dumps(result);return result
 valid=read('Api::Fn');assert valid['status']=='available' and valid['text']==declaration and valid['version']=='2' and len(valid['textHash'])==64
 assert read('Api::Body')['status']=='available' # Its absent implementation body is never opened.
 assert read('Api::Invented')['code']=='NOT_DECLARED_REFERENCE'
 assert read('Api::Fn',sourceId='Other::Item')['code']=='REFERENCE_OWNER_MISMATCH'
 assert read('Missing::Item')['code']=='UNREGISTERED_NAMESPACE'
 assert read('Unused::Item')['code']=='UNDECLARED_DEPENDENCY'
 (pack/'pack.cpack').write_text(registered.replace('pack Api','pack Wrong'));assert read('Api::Fn')['code']=='REGISTRY_IDENTITY_MISMATCH'
 (pack/'pack.cpack').write_text(registered);(pack/'Fn.celem').write_text(declaration.replace('Api::Fn','Api::Wrong'));assert read('Api::Fn')['code']=='LOCATOR_IDENTITY_MISMATCH'
 outside=root/'outside.celem';outside.write_text(declaration);(pack/'pack.cpack').write_text(registered.replace('"Fn.celem"','"../outside.celem"'));assert read('Api::Fn')['code']=='OWNERSHIP'
 (pack/'pack.cpack').write_text(registered);(pack/'Fn.celem').unlink();(pack/'Fn.celem').symlink_to(outside);assert read('Api::Fn')['code']=='OWNERSHIP'
 (pack/'Fn.celem').unlink();(pack/'Fn.celem').write_text('x'*1048577);assert read('Api::Fn')['code']=='DEFINITION_UNAVAILABLE'
 assert project.read_text()==manifest and not (pack/'missing-never-read.csbody').exists()
 print('PASS registered reference definition: explicit edge/dependency/selected registry/identity/owned path/bounds and no body reads',flush=True)
