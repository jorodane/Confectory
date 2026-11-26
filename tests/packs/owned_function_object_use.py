"""Read-only authoring helper for an exact directly owned object reference."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='cf-object-use-') as folder:
    root=Path(folder);project=root/'project.cpack';source=root/'main.celem';obj=root/'rules.celem'
    original='function Alpha::Main () -> int { // retain\n}\n'
    manifest='project Alpha version "1" { standalone true; entry Alpha::Main; element Main function "main.celem"; element Rules object "rules.celem"; }'
    project.write_text(manifest);source.write_text(original);obj.write_text('object Alpha::Rules {}')
    args=dict(operation='ownedFunctionObjectUse',project=str(project),manifest=manifest,text=original,objectId='Alpha::Rules')
    def call(ok,**changes):
        response=json.loads(subprocess.check_output(host,input=json.dumps(dict(args,**changes)),text=True));assert response['ok']==ok,response;return response.get('result')
    result=call(True);assert 'use object Alpha::Rules;' in result and '// retain' in result
    call(False,objectId='Bravo::Rules');call(False,objectId='Alpha::Main');call(False,text=original+' ');call(False,manifest=manifest+' ')
    assert source.read_text()==original and project.read_text()==manifest
print('PASS own object identity, wrong kind and foreign project refusal, stale input, no write')
