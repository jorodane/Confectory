"""Unpublished root proof never treats old, inherited or aliased sources as new."""
import copy,json,pathlib,subprocess
import v666_async_new_function_fixture as x
f=x.f
try:
 f.start(0);x.create();units={u['id']:u for u in x.units()};group=[x.feature,x.impl,x.graph];request=dict(operation='blueprintNewRootGroup',function=x.feature,group=group,units=units)
 def check(body,accepted):
  result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(body),text=True,capture_output=True,env=f.env);reply=json.loads(result.stdout);assert bool(reply['ok'])==accepted,(body['group'],reply)
 check(request,True);before=x.checkpoint()
 for kind in ['old-baseline','old-original','owner','alias-path','missing-registration','duplicate','wrong-order','copy']:
  bad=copy.deepcopy(request)
  if kind=='old-baseline':bad['units'][x.feature]['baseline']='0'*64
  elif kind=='old-original':bad['units'][x.impl]['original']=bad['units'][x.impl]['draft']
  elif kind=='owner':bad['units'][x.feature]['creationOwner']='Owned.Elements::Monster'
  elif kind=='alias-path':bad['units'][x.feature]['path']='Main.celem'
  elif kind=='missing-registration':bad['units'].pop(next(k for k,v in bad['units'].items()if v['kind']=='project'))
  elif kind=='duplicate':bad['group'][2]=x.impl
  elif kind=='wrong-order':bad['group'][1:]=bad['group'][:0:-1]
  else:bad['units'][x.impl]['copySource']={}
  check(bad,False);assert x.checkpoint()==before;x.original()
 f.checked('새 root proof는 실제 미출판 등록만 허용하고 원래 baseline/본문·다른 owner·경로 별칭·등록 누락·중복/역순·copy 위조를 거절한다')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
