"""A new owned copy, its assignment and one preserved-code wrapping save atomically."""
import copy,json,sys,uuid
import v666_node_internal_copy_creating_fixture as n
f=n.f;x=n.x
try:
 n.build('before');f.start(0);f.invoke('select',{'id':n.owner});f.invoke('saveDraft',{});baseline=n.selection();before=x.checkpoint();n.unchanged();assert n.impl not in n.changes()
 if '--legacy' in sys.argv:
  n.rpc('readImplementationCopy',False,id=n.owner,function=n.feature,source=x.impl,target='common',implementation=n.impl,revision=n.schema()['revision'],hash=n.schema()['textHash'],privatePath=n.node,internalFlow={'node':n.node,'nonce':uuid.uuid4().hex});assert x.checkpoint()==before;n.unchanged();f.checked('실제로 실행 가능한 구형 ref profile은 자동 승격하지 않고 기존 copy 선택과 원문을 보존한다');raise SystemExit(0)
 preview,plan=n.proposal();assert x.checkpoint()==before and n.impl not in n.changes();assert preview['preview']['privatePath']==n.node_key;body=next(r for r in preview['preview']['nodes'] if r['id']=='body');assert body['source']==n.source;
 if n.branch:assert body['helpers']==n.helpers and body['executionEnum']==n.branch.execution and body['executionForwarded']
 n.unchanged();f.checked('등록 전 copy의 내부 미리보기는 source/계약/출처를 보존하며 checkpoint나 원본을 쓰지 않는다')
 for kind in ['binding','missing','path','frame',*(['enum'] if n.branch else [])]:
  bad=copy.deepcopy(plan)
  if kind=='binding':bad['binding']['sourceHash']='0'*64
  elif kind=='missing':bad.pop('binding')
  elif kind=='path':bad['nonce']='../escape'
  elif kind=='frame':bad['node']='peer/'+n.node
  else:bad['executionEnum']=copy.deepcopy(n.branch.execution);bad['executionEnum']['members'][0]['value']=123
  bad_row=n.copy_row(preview,bad);bad_row['edits'][0]['node']=bad['node'];n.rpc('applySlots',False,id=n.owner,rows=[bad_row]);assert x.checkpoint()==before;n.unchanged()
 f.checked('누락/위조 source binding과 경로 입력은 copy 생성·배정·내부 소스를 모두 미적용한다')
 plan['source']=n.edited();
 if n.branch:plan.update(executionEnum=copy.deepcopy(n.branch.execution),helpers=n.helpers+'// explicit preserved helper input\r\n')
 row=n.copy_row(preview,plan);command={'id':n.owner,'rows':[row]};n.rpc('applySlots',**command);assert n.rpc('settledSlots',**command)['settled'];saved=x.checkpoint();rows=n.changes();assert n.impl in rows and n.root in rows and n.leaf in rows;assert n.leaf.rsplit('/node:',1)[0] not in rows
 outer=next(r for r in n.at(json.loads(rows[n.root]['draft']))['nodes'] if r['id']==n.node);assert outer['retainedCode']['definition']['kind']=='code';assert outer['retainedCode']['definition']['id']==n.node;assert outer['kind']=='graph';
 if n.branch:assert outer['executionEnum']==n.branch.execution and outer['executionSource']=='body' and json.loads(rows[n.leaf]['draft'])['helpers']==plan['helpers']
 assert n.read(n.child)['diagnostics']['state']=='source-ready';n.unchanged();f.checked('첫 Save는 copy/manifest/owner 배정/내부 leaf를 하나의 후보로 저장하고 가상 원본 record를 물리 파일로 만들지 않는다')
 f.stop();f.start(1);f.invoke('select',{'id':n.owner});assert x.checkpoint()==saved and n.rpc('settledSlots',**command)['settled'];assert n.read(n.child)['diagnostics']['state']=='source-ready';n.unchanged();f.checked('첫 Save receipt와 전체 원자 그룹은 cold에서 복원되며 같은 요청은 중복 copy를 만들지 않는다')
 if '--compile' in sys.argv:
  def body(text):
   current=n.read(n.child);owner=n.schema();return n.rpc('source',id=n.child,owner=n.owner,ownerHash=owner['textHash'],ownerRevision=owner['revision'],basis=current['basis'],node='body',text=text)
  body('return missingFirstCopyValue;');f.invoke('saveDraft',{});invalid=x.checkpoint();failed,state=x.any_invoke('reviewGroup',{'target':'portable','ids':n.read()['reviewIds']});review=(state or {}).get('review') or {}
  if review.get('status')=='ready':failed,state=x.any_invoke('confirmGroup',{'token':review['token'],'ids':n.read()['reviewIds']})
  (f.case/'compile-failure.json').write_text(json.dumps([failed,state],ensure_ascii=False,indent=2));assert 'missingFirstCopyValue' in json.dumps([failed,state]) and not failed.get('result',{}).get('sourceConfirmed');assert x.checkpoint()==invalid and next(r for r in n.read(n.child)['nodes'] if r['id']=='body')['source']=='return missingFirstCopyValue;';n.unchanged();body(n.edited());f.invoke('saveDraft',{});f.checked('첫 copy의 실제 C# 컴파일 실패는 원본/배정/입력을 보존하고 소유 내부 본문의 명시 수정으로 복구한다')
 ids=n.read()['reviewIds'];f.invoke('reviewGroup',{'target':'portable','ids':[n.root]},False);n.unchanged();review=f.invoke('reviewGroup',{'target':'portable','ids':ids});source=f.project/'FreeInfo.celem';source.write_bytes(n.physical[source]+b' ');failed,_=x.any_invoke('confirmGroup',{'token':review['state']['review']['token'],'ids':ids});assert not failed.get('result',{}).get('sourceConfirmed');assert source.read_bytes()==n.physical[source]+b' ' and (f.project/'project.cproj').read_bytes()==n.physical[f.project/'project.cproj'];assert not (f.project/'elements/M11PendingCopy.celem').exists();source.write_bytes(n.physical[source]);n.unchanged();f.stop();f.start(2);f.invoke('select',{'id':n.owner});f.checked('부분 Review와 Review 이후 owner 원문 경합은 최종 CAS에서 생성·배정·본문 전체를 거절한다')
 review=f.invoke('reviewGroup',{'target':'portable','ids':n.read()['reviewIds']});f.invoke('confirmGroup',{'token':review['state']['review']['token'],'ids':n.read()['reviewIds']});assert all(p.read_bytes()==v for p,v in n.physical.items() if p.name not in ['FreeInfo.celem','project.cproj']);n.build('after',1);f.checked('Confirm 뒤 실제 copy 결과만 명시 편집대로 바뀌고 donor 실행·공개 계약·원문은 유지된다')
 f.stop();f.start(3);f.invoke('select',{'id':n.owner});assert n.read(n.child)['diagnostics']['state']=='source-ready';print('M11_CREATING_COPY_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
