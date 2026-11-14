"""A pending single transition cannot acquire another nominal scope by appending it."""
import copy,json,subprocess
import v666_native_type_group_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});original=x.request();one=x.apply_request();one['declaration']['changes']=one['declaration']['changes'][:1];f.invoke('blueprint',one);checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes();x.unchanged();f.stop();f.start(1);f.invoke('select',dict(id=x.owner));f.checked('an existing single nominal input transition cold-restores with its original one-scope type/read lease')
 next_request=x.apply_request();next_request['declaration']['changes']=next_request['declaration']['changes'][1:];units=copy.deepcopy(original['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 request=dict(operation='informationTypeGuards',action='prepare',project=str(f.manifest),namespace=f.n[:-2],units=units,declaration=next_request['declaration']);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);value=json.loads(p.stdout);(f.case/'incremental-guard.json').write_text(json.dumps(value,ensure_ascii=False,indent=2));assert value['ok']is False and'confirm an existing single transition'in value.get('message',''),value
 f.invoke('blueprint',next_request,False);assert checkpoint.read_bytes()==saved;x.unchanged();f.checked('an appended second scope is refused before checkpoint or source writes; only a complete original nominal group or unchanged captured scope set is accepted')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
