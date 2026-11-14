"""Captured nominal function/type scopes remain exact after metadata Save."""
import copy,hashlib,json,subprocess
import v666_native_type_group_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();catalog=x.catalogs();f.invoke('blueprint',x.apply_request(catalog));checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));ids=x.verify(checkpoint);units=copy.deepcopy(r['units'])
 for row in json.loads(checkpoint.read_text())['changes']:units[row['id']]=row
 saved=checkpoint.read_bytes()
 def check(selected,ok,action='validate'):
  command=dict(operation='informationBodyGroupGuards',action=action,project=str(f.manifest),namespace=f.n[:-2],units=selected,selected=[x.owner]);p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(command),env=f.env,text=True,capture_output=True,check=True);value=json.loads(p.stdout);assert bool(value['ok'])==ok,value;return command
 check(units,True,'graphs');command=check(units,True);(f.case/'captured-guard-request.json').write_text(json.dumps(command,ensure_ascii=False,indent=2))
 for fault in ['missing-scope','crossed-scope','missing-type','missing-read','alias','native-name','body-hash','function-hash','foreign-path']:
  bad=copy.deepcopy(units);receipt=bad[x.owner]['slotSaveReceipt'];proof=receipt['sources'];header=x.c.impl;source=x.bodies[x.first]
  if fault=='missing-scope':receipt['nativeTypeProofs'].pop('$function:'+x.second)
  elif fault=='crossed-scope':receipt['nativeTypeProofs']['$function:'+x.second]=copy.deepcopy(receipt['nativeTypeProofs']['$function:'+x.first])
  elif fault=='missing-type':receipt['nativeTypeProofs']={k:v for k,v in receipt['nativeTypeProofs'].items()if k.startswith('$function:')}
  elif fault=='missing-read':receipt['nativeTypeReads'].pop()
  elif fault in ['alias','native-name']:
   key=f.n+'MainBody'if fault=='alias'else header;bad[key]['draft']=bad[key]['draft'].replace('as Connected','as Renamed',1)if fault=='alias'else bad[key]['draft'].replace(' amount',' renamedAmount',1);proof[key]['hash']=hashlib.sha256(bad[key]['draft'].encode()).hexdigest()
  elif fault=='body-hash':bad[source]['draft']+='\n// forged captured body'
  elif fault=='function-hash':bad[x.first]['draft']+='\n// forged captured function'
  else:bad[source]['path']='../outside.csbody';proof[source]['path']='../outside.csbody'
  check(bad,False);assert checkpoint.read_bytes()==saved;x.unchanged()
 f.checked('cold type/read/header/body validation retains both exact function scopes; missing/crossed proofs, re-signed alias/native-name, stale captures and relocated body fail without writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
