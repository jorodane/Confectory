"""Observed copy authority, original raw source and full-candidate checkpoint/Confirm."""
import copy,json,uuid,pathlib
import v666_node_internal_copy_fixture as n
f=n.f;x=n.x
try:
 n.build('before');f.start(0);f.invoke('select',{'id':n.owner});f.invoke('saveDraft',{});d=n.read();before=x.checkpoint();nonce=uuid.uuid4().hex
 if '--shared' in __import__('sys').argv:
  assert not d['nodeFlowCopyAvailable'];n.rpc('previewNodeInternal',False,node='calculate',definition={'nonce':nonce});n.rpc('authorBatch',False,**n.request(d,nonce));assert x.checkpoint()==before;n.original();f.checked('다른 정보에도 직접 배정된 공유 copy는 단독 래핑을 거절하고 두 owner와 원본을 보존한다');raise SystemExit(0)
 if n.parts and len(n.parts)==8:
  n.rpc('previewNodeInternal',False,node='calculate',definition={'nonce':nonce});n.rpc('authorBatch',False,**n.request(d,nonce));assert x.checkpoint()==before;n.original();f.checked('엔진의 기존 최대 깊이를 넘는 copy 래핑은 전체 후보/원문/입력을 보존하며 거절한다');raise SystemExit(0)
 assert d['nodeFlowCopyAvailable']
 if n.parts:
  req=n.request(d,nonce);bad=copy.deepcopy(req);bad['edits'][0]['definition'].pop('binding');n.rpc('authorBatch',False,**bad);bad=copy.deepcopy(req);bad['id']=n.graph+'/graph:peer';n.rpc('authorBatch',False,**bad)
  for target in [n.graph,n.graph+'/graph:'+n.parts[0]]:assert n.rpc('previewNodeInternal',node='calculate',frame=target,definition={'nonce':nonce})['id']==target
  n.rpc('previewNodeInternal',False,node='calculate',frame=n.graph+'/graph:peer',definition={'nonce':nonce});assert x.checkpoint()==before;n.original();f.checked('copy의 전체 private 경로와 정확한 조상만 미리보며 같은 local ID의 형제 retarget·누락 binding은 전체 거절한다')
 bad=n.request(d);bad['ownerHash']='0'*64;n.rpc('authorBatch',False,**bad);bare=n.request(d);bare.pop('owner');bare.pop('ownerHash');bare.pop('ownerRevision');f.invoke('blueprint',{'action':'authorBatch',**bare},False);n.rpc('previewNodeInternal',False,id=x.graph,node='calculate',definition={'nonce':uuid.uuid4().hex});bad=n.request(d);bad['edits'][0]['definition']['signature']={'args':[],'return':'void'};n.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;n.original();f.checked('잘못된 owner·슬롯 없는 copy·donor 재지정·공개 계약 변경 요청은 원본/입력/체크포인트를 보존하며 거절한다')
 if n.storage:
  selected=next(row for row in d['nodes'] if row['id']=='calculate');assert selected['signature']==n.storage.signature
 p=n.rpc('previewNodeInternal',node='calculate',definition={'nonce':nonce});assert p['nodeFlowPreview'] and p['slotContext']['owner']==n.owner;assert x.checkpoint()==before;n.original();f.checked('저장된 단독 소유 copy의 선택 C# 미리보기는 원본·공개 계약·checkpoint를 쓰지 않는다')
 if n.storage:
  inner=next(row for row in p['nodes'] if row['id']=='body');assert inner['signature']==n.storage.signature and inner['forwardCallerStorage'];assert {a['name'] for a in inner['arguments']}=={a['name'] for a in n.storage.params if a['mode']!='out'}
 req=n.request(d,nonce);n.rpc('authorBatch',**req);v=n.read(n.child);assert v['diagnostics']['state']=='source-ready',v['diagnostics'];assert n.rpc('settledAuthorBatch',**req)['settled'];saved=x.checkpoint();assert n.rpc('authorBatch',**req)['settled'] and x.checkpoint()==saved;n.original();f.checked('같은 copy ID/출처/배정과 기존 계약을 유지하여 내부 leaf/guard를 한 후보 CAS에 저장한다')
 rows={r['id']:r for r in json.loads(next(iter(x.checkpoint().values())))['changes']};g=json.loads(rows[n.graph]['draft']);assert g['copySource']==n.provenance;assert n.at(g)['nodes'][0]['retainedCode']['definition']==n.at(n.prepared['graph'])['nodes'][0];assert rows[n.original_id]['draft']==n.physical[f.project/rows[n.original_id]['path']].decode();assert set(v['reviewIds'])>=set([n.owner,n.impl,n.graph,n.original_id,n.leaf])
 f.stop();f.start(1);f.invoke('select',{'id':n.owner});assert n.read(n.child)['diagnostics']['state']=='source-ready';n.original();f.checked('cold 재시작은 copy 소유 경계와 원래 코드 guard를 복원한다')
 if n.storage:
  def body_save(text):
   data=n.read(n.child);return n.rpc('authorBatch',id=n.child,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[{'action':'source','node':'body','text':text}])
  body_save('return 1;');bad=x.checkpoint();failed,state=x.any_invoke('reviewGroup',{'ids':n.read()['reviewIds']});review=(state or {}).get('review') or {}
  if review.get('status')=='ready':failed,state=x.any_invoke('confirmGroup',{'token':review['token'],'ids':n.read()['reviewIds']})
  (f.case/'copy-storage-compile-failure.json').write_text(json.dumps([failed,state],ensure_ascii=False));assert 'CS0177' in json.dumps([failed,state]);assert not failed.get('result',{}).get('sourceConfirmed') and x.checkpoint()==bad;n.original();assert next(row for row in n.read(n.child)['nodes'] if row['id']=='body')['source']=='return 1;';body_save(n.storage.source);f.checked('copy 내부 out 미할당은 실제 C# 컴파일에서 거절하고 실패한 입력·원문을 유지하며 명시 수정으로 복구한다')
 view=n.read();f.invoke('reviewGroup',{'ids':[n.graph]},False);review=f.invoke('reviewGroup',{'target':'portable','ids':view['reviewIds']})['state']['review'];assert not review.get('errors'),review;n.original();guard=n.guard;checkpoint=x.checkpoint();guard.write_bytes(n.physical[guard]+b' ');failed,state=x.any_invoke('confirmGroup',{'token':review['token'],'ids':view['reviewIds']});(f.case/'copy-final-cas-refusal.json').write_text(json.dumps([failed,state],ensure_ascii=False));assert not failed.get('result',{}).get('sourceConfirmed') and x.checkpoint()==checkpoint;assert all(p.read_bytes()==v for p,v in n.physical.items() if p!=guard);guard.write_bytes(n.physical[guard]);f.stop();f.start(2);f.invoke('select',{'id':n.owner});view=n.read();n.original();f.checked('Review 이후 원래 copy C# 경합은 최종 CAS에서 전체 미반영하며 저장 입력을 보존한다');review=f.invoke('reviewGroup',{'target':'portable','ids':view['reviewIds']})['state']['review'];f.invoke('confirmGroup',{'token':review['token'],'ids':view['reviewIds']});assert all(p.read_bytes()==v for p,v in n.physical.items() if p!=f.project/n.graph_path);published=json.loads((f.project/n.graph_path).read_text());expected=copy.deepcopy(n.prepared['graph']);n.at(expected)['nodes'][0]=copy.deepcopy(n.at(published)['nodes'][0]);assert published==expected;n.build('after');f.checked('명시 Review/Confirm 뒤 copy만 활성화하며 원래 C#·donor/owner/공개 ABI와 실제 호출 결과를 보존한다')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('M11_COPY_API '+str(f.case),flush=True)
