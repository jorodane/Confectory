"""중첩 frame의 단일 코드 전환, 부모·형제·원문·활성 호출 및 최종 CAS."""
import copy,json,uuid
import v666_node_internal_nested_fixture as n
x=n.x;f=n.f
try:
 x.build('nested-before',7);f.start(0);baseline=n.read();assert baseline['privatePath']==n.path and baseline['diagnostics']['state']=='source-ready';original_checkpoint=x.checkpoint();nonce=uuid.uuid4().hex
 if n.depth==8:
  n.rpc('previewNodeInternal',False,node='calculate',definition={'nonce':nonce});n.rpc('authorBatch',False,**n.request(baseline,nonce));assert x.checkpoint()==original_checkpoint;x.original();f.checked('기존 엔진의 실제 최대 깊이를 넘는 전환은 원본과 체크포인트를 보존하며 전체 거절한다')
 else:
  preview=n.rpc('previewNodeInternal',node='calculate',definition={'nonce':nonce});assert preview['privatePath']==n.path+'/calculate';assert next(row for row in preview['nodes'] if row['id']=='body')['source']==n.record['source'];assert x.checkpoint()==original_checkpoint;x.original()
  for target in [n.root,n.parent,n.root+'/graph:'+n.parts[0]]:
   view=n.rpc('previewNodeInternal',node='calculate',frame=target,definition={'nonce':nonce});assert view['id']==target and view['nodeFlowPreview']
  n.rpc('previewNodeInternal',False,node='calculate',frame=n.root+'/graph:peer',definition={'nonce':nonce});assert x.checkpoint()==original_checkpoint;x.original();f.checked('선택한 중첩 경로와 정확한 조상만 미리보고 동일 local ID의 형제와 원본 파일을 보존한다')
  req=n.request(baseline,nonce);missing=copy.deepcopy(req);missing['edits'][0]['definition'].pop('binding');n.rpc('authorBatch',False,**missing);assert x.checkpoint()==original_checkpoint;x.original();bad=copy.deepcopy(req);bad['id']=n.root+'/graph:peer';n.rpc('authorBatch',False,**bad);assert x.checkpoint()==original_checkpoint;x.original();f.checked('다른 frame으로 옮긴 저장 시도는 원래 receipt/원문이 다르므로 전체 거절한다')
  n.rpc('authorBatch',**req);assert n.rpc('settledAuthorBatch',**req)['settled'];current=n.read();inner=n.read(n.child);assert inner['diagnostics']['state']=='source-ready';assert next(row for row in current['nodes'] if row['id']=='calculate')['kind']=='graph';assert current['edges']==baseline['edges'];assert set(current['reviewIds'])>=set([n.root,n.original_id,n.leaf]);x.original();f.checked('부모 private 계약·기존 연결·원문 guard와 새 leaf를 동일 후보/최종 checkpoint CAS로 저장한다')
  saved=x.checkpoint();f.stop();f.start(1);assert n.read(n.child)['diagnostics']['state']=='source-ready' and x.checkpoint()==saved;x.original();f.invoke('reviewGroup',{'ids':[n.root]},False);f.checked('cold 복원과 부분 Review 거절은 전체 중첩 소유 그룹을 유지한다')
  view=f.invoke('reviewGroup',{'ids':n.read()['reviewIds']});token=view['state']['review']['token'];source=f.project/'Flow.node.json';source.write_bytes(x.physical[source]+b' ');failed,_=x.any_invoke('confirmGroup',{'token':token,'ids':n.read()['reviewIds']});assert not failed.get('result',{}).get('sourceConfirmed');assert (f.project/'Flow.graph.json').read_bytes()==x.physical[f.project/'Flow.graph.json'];source.write_bytes(x.physical[source]);f.stop();f.start(2);x.original();f.checked('Review 뒤 원문 경합을 최종 파일 CAS에서 막아 부모·형제·새 leaf를 부분 반영하지 않는다')
  view=f.invoke('reviewGroup',{'ids':n.read()['reviewIds']});f.invoke('confirmGroup',{'token':view['state']['review']['token'],'ids':n.read()['reviewIds']});published=json.loads((f.project/'Flow.graph.json').read_text());selected=next(row for row in n.at(published)['nodes'] if row['id']=='calculate');expected=copy.deepcopy(n.graph);index=next(i for i,row in enumerate(n.at(expected)['nodes']) if row['id']=='calculate');n.at(expected)['nodes'][index]=copy.deepcopy(selected);assert published==expected;assert selected['graph']['profile']=='sync-acyclic-methods-v1';n.assert_wrapper(selected);new=next(row for row in selected['graph']['nodes'] if row['id']=='body');assert json.loads((f.project/new['implementation']).read_text())['source']==n.record['source'];assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];assert (f.project/'Peer.node.json').read_bytes()==x.physical[f.project/'Peer.node.json'];x.build('nested-after',7);f.checked('혼합 profile·부모/형제 동일 ID·helper를 유지하며 선택한 동작만 Confirm하고 CLR 결과를 보존한다')
  f.stop();f.start(3);assert n.read(n.child)['diagnostics']['state']=='source-ready';f.checked('확정 뒤 재시작은 전체 중첩 경로의 새 활성 구현을 정확히 복원한다')
 print('M11_NESTED_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
