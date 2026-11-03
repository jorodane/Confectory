"""Full explicit return update, retained copy/ancestry and final source CAS."""
import copy,json,hashlib
import v666_root_execution_owned_update_fixture as o
f=o.f;x=o.x;c=o.c
try:
 o.build('owned-before');f.start(0);d=o.read();q=d['rootExecution'];assert q is not None,d.get('rootExecutionError');targets={t['graph'] for t in q['targets']};assert targets=={x.graph,c.graph,o.parent+'/body:common',o.child+'/body:common'};assert not any(o.inherited in id for id in targets);observed=set(q['observedContracts']);assert {o.parent,o.child,o.inherited,c.owner,c.module,o.child_owner}<=observed
 req=o.request(d);before=x.checkpoint()
 for reason in ['missing-target','missing-caller','wrong-branch','wrong-value','stale-proof']:
  bad=copy.deepcopy(req);p=bad['edits'][0]['definition']
  if reason=='missing-target':p['targets'].pop()
  elif reason=='missing-caller':p['callers']=[]
  elif reason=='wrong-branch':p['targets'][0]['exits']['yes']['executionBranch']='unknown'
  elif reason=='wrong-value':p['branches'][0]['value']=99
  else:bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;o.original()
 f.checked('copy·자식의 직접 소유 target만 전체 명시 대응하고 inherited-only는 관측하며 누락/잘못된 대응·서명 증거를 전체 거절한다')
 p=f.project/'FreeInfo.celem';p.write_bytes(o.physical[p]+b' ')
 try:x.rpc('authorBatch',False,**req)
 finally:p.write_bytes(o.physical[p])
 assert x.checkpoint()==before;o.original();saved=x.rpc('authorBatch',**req);assert saved['checkpointSaved'] and saved['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];o.original();cp=x.checkpoint();f.stop();f.start(1);assert x.rpc('settledAuthorBatch',**req)['settled'];d=o.read();assert d['diagnostics']['state']=='source-ready';assert x.checkpoint()==cp
 f.checked('owner 배정 원문 경합은 미적용하고 정상 전체 후보는 한 checkpoint/cold/receipt 재조회로 중복 없이 복원한다')
 saved=json.loads(next(iter(cp.values())));units={r['id']:r for r in saved['changes']};
 for row in d['sources']:
  if row['id'] not in units:
   path=f.project/row['path'];text=path.read_text();units[row['id']]={'kind':row['kind'],'path':row['path'],'draft':text,'original':text,'baseline':hashlib.sha256(path.read_bytes()).hexdigest()}
 checks=f.metadata('blueprintRootExecutionGuards',namespace=f.n[:-2],units=units)['checks'];assert {'FreeInfo.celem','M12Rules.celem','M12ChildInfo.celem','M12Parent.celem','M12Child.celem','M12Inherited.celem','project.cproj'}<={r['path'] for r in checks}
 for reason in ['owner','module','parent','borrower','provenance','manifest','missing-source']:
  bad=copy.deepcopy(units)
  if reason=='missing-source':bad.pop(o.inherited)
  elif reason=='provenance':g=json.loads(bad[c.graph]['draft']);g['copySource']['implementation']=f.n+'Other';bad[c.graph]['draft']=json.dumps(g)
  elif reason=='manifest':row=next(r for r in bad.values() if r['kind']=='project');row['draft']+=' '
  else:
   id={'owner':c.owner,'module':c.module,'parent':o.parent,'borrower':o.inherited}[reason];bad[id]['draft']+=' '
  try:f.metadata('blueprintRootExecutionGuards',namespace=f.n[:-2],units=bad)
  except AssertionError:pass
  else:raise AssertionError('Corrupt full ownership closure accepted: '+reason)
 f.checked('전체 owner/module/project·local ancestry receipt와 copy provenance의 누락·변조는 순수 그룹/최종 guard에서 거절한다')
 ids=d['reviewIds'];f.invoke('reviewGroup',{'ids':[x.graph]},False);view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');review_cp=x.checkpoint();p=f.project/'M12ChildInfo.celem';p.write_bytes(o.physical[p]+b' ')
 try:assert not f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']})['result']['result']['sourceConfirmed']
 finally:p.write_bytes(o.physical[p])
 o.original();assert x.checkpoint()==review_cp;f.stop();f.start(2);f.checked('부분 Review와 Review 뒤 새/shared owner 관측 경합은 최종 CAS에서 전체 미반영하고 재시작 입력을 보존한다')
 ids=o.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');assert f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']})['result']['result']['sourceConfirmed'];o.retained();assert json.loads((f.project/c.graph_path).read_text())['copySource']==c.provenance;o.build('owned-after',True)
 f.checked('전체 Confirm은 기존 C#/IO/배정·donor provenance와 inherited-only 선언을 보존하며 선택한 copy/자식의 out10→실패 분기→다음 실행을 실제 수행한다')
 f.stop();f.start(3);d=o.read();assert d['diagnostics']['state']=='source-ready';o.retained();f.checked('확정 후 cold에서도 같은 ID·공개 계약·모든 target 반환과 원래 상속 소유권을 보존한다')
 print('M12_OWNED_UPDATE_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
