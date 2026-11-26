"""Bounded project-entry authoring parser regression (no canonical files written)."""
import json,os,subprocess,sys
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
manifest='''project Local.Game version "1" {
  standalone true;
  // keep entry annotation
  entry Local.Game::Main; // keep trailing annotation
  element Main function "main.celem";
  element Game function "game.celem";
  element Object object "object.celem";
}
'''
def call(id,feature,ok,current=None):
    response=json.loads(subprocess.run(host,input=json.dumps(dict(operation='setProjectEntry',manifest=manifest,feature=feature,id=id,**({'current':current} if current is not None else {}))),text=True,capture_output=True,check=True,timeout=20).stdout)
    assert response['ok']==ok,response
    return response.get('result')
for return_type in ('int','void'):
    assert call('Local.Game::Game',f'function Local.Game::Game () -> {return_type} {{}}',True)==manifest.replace('entry Local.Game::Main;','entry Local.Game::Game;')
# A prior entry-only draft can be superseded; unrelated manifest edits cannot.
staged=manifest.replace('entry Local.Game::Main;','entry Local.Game::Game;')
assert call('Local.Game::Main','function Local.Game::Main () -> int {}',True,staged)==manifest
call('Local.Game::Game','function Local.Game::Game () -> int {}',False,manifest.replace('version "1"','version "2"'))
call('Local.Game::Game','function Local.Game::Game (int n) -> int {}',False)
call('Local.Game::Game','function Local.Game::Game () -> long {}',False)
call('Local.Game::Object','object Local.Game::Object {}',False)
call('Other.Game::Game','function Other.Game::Game () -> int {}',False)
call('Local.Game::Missing','function Local.Game::Missing () -> int {}',False)
call('Local.Game::Game','function Local.Game::Main () -> int {}',False)
print('PASS exact entry-only merge, int/void contracts and invalid/foreign/unregistered IDs refused')
