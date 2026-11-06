"""Actual context-bound private preset storage: CAS, exact replay, write failure and restart."""
import json,sys,traceback,uuid,hashlib,os
sys.argv.append('--resizable-output')
import v666_run_fullscreen_fixture as f
view=None
try:
 f.start(0);view=f.mount()
 def load(extra=None,ok=True):
  r=f.raw({'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runPresetRead','input':extra or {}});assert bool(r.get('ok'))==ok,r;return r.get('result')
 def put(revision,item,command=None,ok=True):return f.call('runPresets',{'operation':'add','revision':revision,'command':command or uuid.uuid4().hex,'item':item},ok)
 def remove(revision,id,command=None,ok=True):return f.call('runPresets',{'operation':'remove','revision':revision,'command':command or uuid.uuid4().hex,'id':id},ok)
 first=load();assert first['status']=='ready'and first['revision']=='missing'and not first['items'];project=first['project'];folder=f.root/'profile/run-resolution-presets';file=folder/(hashlib.sha256(project.encode()).hexdigest()+'.json');a={'id':'a'*32,'name':'Phone <화면>','width':320,'height':240};cmd='c'*32;one=put(first['revision'],a,cmd);assert one['selected']==a['id']and len(one['items'])==1 and hashlib.sha256(file.read_bytes()).hexdigest()==one['revision'];saved=file.read_bytes();repeat=put(first['revision'],dict(reversed(list(a.items()))),cmd);assert repeat['replayed']and file.read_bytes()==saved;put(first['revision'],{**a,'width':321},cmd,False);put(first['revision'],{**a,'id':'b'*32,'name':'Another'},ok=False);assert file.read_bytes()==saved;f.checked('actual private profile CAS and canonical last-command replay preserve one stable registration; command collision and stale revision cannot overwrite it')
 tampered=json.loads(saved);tampered['items'][0]['width']=400;file.write_text(json.dumps(tampered));changed_bytes=file.read_bytes();put(first['revision'],a,cmd,False);assert file.read_bytes()==changed_bytes;file.write_bytes(saved);f.checked('receipt cannot confirm a target whose stored dimensions were changed after the original command')
 same=put(one['revision'],{**a,'id':'b'*32,'name':'phone <화면>'});assert same['existing']and same['selected']==a['id']and file.read_bytes()==saved;put(one['revision'],{**a,'id':'b'*32,'width':400},ok=False)
 for patch in [{'width':513},{'height':239},{'name':'bad\nname'},{'name':' '},{'id':'x'},{'unknown':'input'}]:put(one['revision'],{**a,**patch},ok=False)
 for bad in [{'project':project},{'storage':'/tmp'},{'operation':'add'}]:load(bad,False)
 assert file.read_bytes()==saved;f.checked('same-name same-size registration selects existing ID without writing; name/dimension/ID/unknown-field/foreign-path attempts are rejected')
 external=json.loads(saved);external['items'][0]['name']='External owned change';external['receipt']=None;file.write_text(json.dumps(external));external_bytes=file.read_bytes();put(one['revision'],{**a,'id':'b'*32,'name':'B'},ok=False);assert file.read_bytes()==external_bytes;fresh=load();assert fresh['revision']!=one['revision'];f.checked('actual file change after read conflicts at storage CAS; no silent merge or replacement')
 readonly_cmd='d'*32;mode=file.stat().st_mode;file.chmod(0o400)
 try:put(fresh['revision'],{**a,'id':'b'*32,'name':'B'},readonly_cmd,False);assert file.read_bytes()==external_bytes
 finally:file.chmod(mode)
 two=put(fresh['revision'],{**a,'id':'b'*32,'name':'B'},readonly_cmd);assert len(two['items'])==2 and not two['replayed'];saved=file.read_bytes();f.checked('real write refusal preserves all original bytes; same caller-owned command/inputs retry once after restoring owned fixture access')
 for raw in ['{broken',json.dumps({**json.loads(saved),'project':'foreign'})]:
  file.write_text(raw);assert load()['status']=='unavailable';put(two['revision'],{**a,'id':'e'*32,'name':'E'},ok=False);assert file.read_text()==raw
 file.write_bytes(saved);assert load()['revision']==two['revision'];sentinel=f.root/'owned-sentinel';sentinel.write_bytes(b'generated fixture');file.unlink();file.symlink_to(sentinel)
 try:assert load()['status']=='unavailable';put(two['revision'],{**a,'id':'e'*32,'name':'E'},ok=False);assert sentinel.read_bytes()==b'generated fixture'
 finally:file.unlink();file.write_bytes(saved)
 f.checked('malformed/foreign existing storage and symlink are unavailable, never treated as an empty writable registration list')
 state=load()
 for n in range(30):state=put(state['revision'],{**a,'id':format(n+100,'032x'),'name':'Preset '+str(n)})
 assert len(state['items'])==32;put(state['revision'],{**a,'id':'f'*32,'name':'Overflow'},ok=False);state=remove(state['revision'],a['id'],'e'*32);assert len(state['items'])==31
 # Exact removal replay uses the basis captured before that removal.
 stored=json.loads(file.read_text());removed_basis=stored['receipt']['base'];assert remove(removed_basis,a['id'],'e'*32)['replayed'];remove(state['revision'],'f'*32,ok=False);f.checked('bounded 32 registrations and exact removal replay preserve remaining IDs and never execute Run commands')
 f.raw({'op':'dispose','view':view['view']});view=None;f.stop();f.start(1);view=f.mount();restored=load();assert restored['items']==state['items']and restored['revision']==state['revision'];first_listing=f.state()['listingId'];f.call('leaveProject',{});assert not f.raw({'op':'observe','view':view['view'],'scope':view['scope'],'endpoint':'runPresetRead','input':{}})['ok'];f.raw({'op':'dispose','view':view['view']});view=None;f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);view=f.mount();other=load();assert other['project']!=project and other['revision']=='missing'and not other['items'];f.checked('cold reads only committed registrations; no-project and another real ProjectContext cannot read the former project list');f.original()
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc())));raise
finally:
 if view:
  try:f.raw({'op':'dispose','view':view['view']})
  except Exception:pass
 f.save_evidence();f.stop()
print('RUN_PRESETS_API',f.root,flush=True)
