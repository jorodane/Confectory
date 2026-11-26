"""Exact read-only combined variation proposal; unchanged legacy transformations."""
import json, os, subprocess, sys
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
def call(operation,**request):
    return json.loads(subprocess.check_output(host,input=json.dumps(dict(operation=operation,**request)),text=True))
def result(operation,**request):
    reply=call(operation,**request);assert reply['ok'],reply;return reply['result']
parent='Alpha::Rules';child='Alpha::Child'
source='object Alpha::Rules { use schema Alpha::Fields; data Phase = 5; }'
manifest='project Alpha version "1" { standalone true; element Rules object "elements/Rules.celem"; element Fields schema "elements/Fields.celem"; }'
request=dict(parent=parent,parentText=source,id=child,manifest=manifest)
def proposal(**changes):return call('prepareExistingSchemaObjectVariation',**(request|changes))
assert result('inspect',text=source)['id']==parent
empty=result('create',kind='object',id=child)
text=result('editDeclaration',text=empty,edit=dict(action='parent',value=parent))
registered=result('register',text=manifest,id=child,kind='object',path='elements/Child.celem')
assert proposal()==dict(ok=True,result=dict(eligible=True,text=text,registered=registered))
# Registration is the last operation: a duplicate still yields no partial result.
duplicate=proposal(manifest=registered);assert not duplicate['ok'] and 'result' not in duplicate,duplicate
for changes in (dict(parent='Alpha::Other'),dict(id='Alpha::Bad!'),dict(parentText='object Alpha::Rules {')):
    failed=proposal(**changes);assert not failed['ok'] and 'result' not in failed,failed
for changes in (dict(id='Beta::Child'),dict(parentText='object Alpha::Rules {}'),dict(parentText='object Alpha::Rules extends Alpha::Base {}'),dict(manifest=manifest.replace('element Fields schema "elements/Fields.celem";',''))):
    assert proposal(**changes)==dict(ok=True,result=dict(eligible=False))
print('PASS combined proposal matches all legacy transformations; duplicate, invalid input and unsupported shapes produce no partial result')
