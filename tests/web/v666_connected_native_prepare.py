"""Pure candidate diagnostic over the same complete owned source snapshot."""
import hashlib,json,subprocess
import v666_connected_native_fixture as c
f=c.f
try:
 f.start(0);f.invoke('select',dict(id=c.owner));catalog=c.catalog();change=c.request(catalog)['declaration']['changes'][0];units={}
 for row in f.metadata('describe',project=str(f.manifest))['units']:
  raw=(f.project/row['path']).read_bytes();text=raw.decode('utf-8-sig');units[row['id']]={**row,'draft':text,'original':text,'revision':1,'baseline':hashlib.sha256(raw).hexdigest()}
 request=dict(operation='informationDefinitions',project=str(f.manifest),manifest=f.manifest.read_text(),id=c.owner,text=(f.project/'FreeInfo.celem').read_text(),changes=[change],units=units,drafts=[dict(id=id,text=row['draft'])for id,row in units.items()if row['kind']in['object','schema','function','implementation','module','category','concept','enum']and id!=c.owner]);out=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);(f.case/'pure-result.json').write_text(out.stdout);v=json.loads(out.stdout);print(json.dumps(dict(ok=v.get('ok'),code=v.get('code'),message=v.get('message'),error=v.get('error')),ensure_ascii=False));assert v['ok'],v;updates=v['result']['updates']+v['result']['linkedUpdates'];assert {c.body_id,c.caller_id}<={r['id']for r in updates};assert not any(r['id'].startswith('External.Fields::')for r in updates);assert any(row['path']==str(c.x.external/'Leaf.celem')for row in v['result']['observations']);c.x.unchanged();f.checked('pure candidate retains both explicit bodies and selected external type observations without adding external writes or executing any provider')
finally:f.stop()
