"""Actual authoring host's installed pack/closure proposal; no source writes."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]];installation=Path(sys.argv[2]).resolve()
def call(op,ok,**args):
    row=json.loads(subprocess.run(host,input=json.dumps(dict(operation=op,**args)),text=True,capture_output=True,check=True,timeout=30).stdout)
    assert row['ok']==ok,row
    return row.get('result')
with tempfile.TemporaryDirectory(prefix='cf-pack-registration-') as t:
    project=Path(t)/'project.cpack'
    original='project Alpha version "1" { standalone true; entry Alpha::Main; // keep comment\n element Main function "main.celem"; }\n'
    project.write_text(original)
    opts=call('installedPackOptions',True,installation=str(installation),project=str(project))['options']
    assert {'Confectory.Window','Confectory.RenderInput'}<=set(p['id'] for p in opts)
    def prepare(id,base=original,current=None,ok=True):
        return call('addProjectPack',ok,installation=str(installation),project=str(project),manifest=base,current=base if current is None else current,id=id)
    next=prepare('Confectory.Window')
    assert 'dependency Confectory.Window version' in next and 'registry Confectory.RenderInput ' in next
    assert 'dependency Confectory.RenderInput ' not in next and '// keep comment' in next
    assert prepare('Confectory.Window',current=next)==next
    both=prepare('Confectory.RenderInput',base=next)
    assert both.count('registry Confectory.RenderInput ')==1 and 'dependency Confectory.RenderInput version' in both
    prepare('Unknown.Pack',ok=False)
    prepare('Confectory.Window',current=original.replace('version "1"','version "2"'),ok=False)
    prepare('Confectory.Window',base=original.replace('entry Alpha::Main;', 'entry Alpha::Main; registry Confectory.RenderInput "other.cpack";'),ok=False)
    assert project.read_text()==original
print('PASS installed identity, closure, exact retry, direct dependency and conflict refusal')
