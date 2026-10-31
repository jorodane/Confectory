"""Explicit owned override body versus the unchanged inherited-source boundary."""
import copy,json,sys,uuid,subprocess
import v666_node_internal_override_fixture as n
x=n.x;f=n.f
try:
 x.build('override-before',7);f.start(0);data=n.read();assert data['diagnostics']['state']=='source-ready';before=x.checkpoint();n.original()
 if '--expect-guard' in sys.argv:
  reply,state=x.any_invoke('blueprint',{'action':'previewNodeInternal','id':n.frame,'node':'calculate','definition':{'nonce':uuid.uuid4().hex}});assert not reply['ok'];(f.case/'owned-override-guard.json').write_text(json.dumps([reply,state],ensure_ascii=False,indent=2));assert x.checkpoint()==before;n.original();f.checked('직접 선언한 자식 body도 Parent 존재만으로 막히는 기존 M11 경계를 재현했다');raise SystemExit(0)
 # Authority requires an observed published ancestry and an own declared target.
 owner={'project':str(x.manifest),'id':x.impl,'text':(f.project/'FlowBody.celem').read_text(),'bodyTarget':'common','ancestorSources':{n.parent:n.parent_text}}
 record=(f.project/'Flow.node.json').read_text();base={'operation':'blueprintNodeFlow','id':x.graph,'privatePath':n.path,'node':'calculate','nonce':uuid.uuid4().hex,'record':record,'graph':n.graph,'ownerRequest':owner}
 for kind in ['missing','changed','inherited','reference','contract']:
  invalid=copy.deepcopy(base)
  if kind=='missing':invalid['ownerRequest'].pop('ancestorSources')
  elif kind=='changed':invalid['ownerRequest']['ancestorSources'][n.parent]+=' '
  elif kind=='inherited':invalid['ownerRequest'].update(id=n.borrower,text=(f.project/'M11Inherited.celem').read_text());invalid['id']=n.borrower+'/body:common'
  elif kind=='reference':invalid['ownerRequest']['id']='External.Parent::Borrowed'
  else:invalid['ownerRequest']['text']=invalid['ownerRequest']['text'].replace('-> long','-> int')
  if kind=='contract':(f.project/'FlowBody.celem').write_text(invalid['ownerRequest']['text'])
  done=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(invalid),text=True,capture_output=True,env=f.env,check=True);reply=json.loads(done.stdout);assert not reply['ok'],(kind,reply)
  if kind=='contract':(f.project/'FlowBody.celem').write_bytes(n.physical[f.project/'FlowBody.celem'])
  (f.case/('refused-'+kind+'.json')).write_text(json.dumps(reply,ensure_ascii=False,indent=2));assert x.checkpoint()==before;n.original()
 f.checked('상속 본문 소유권 사칭·부모 영수증 누락/변조·공개 계약 변경·비소유 참조를 원문 변경 없이 거절한다')
 parent_file=f.project/'M11Parent.celem';parent_file.write_bytes(n.physical[parent_file]+b'\n// peer ancestor change\n')
 req=n.request(data,source='return amount+8;');x.rpc('authorBatch',False,**req);assert x.checkpoint()==before and parent_file.read_bytes()!=n.physical[parent_file];parent_file.write_bytes(n.physical[parent_file]);n.original();f.checked('관측 뒤 부모 변경은 자기 graph와 새 내부 소스를 모두 미적용하며 상대 변경을 덮지 않는다')
 preview=x.rpc('previewNodeInternal',id=n.frame,node='calculate',definition={'nonce':uuid.uuid4().hex});assert preview['privatePath']==(n.path+'/' if n.path else '')+'calculate';assert x.checkpoint()==before;n.original();f.checked('자식이 직접 소유한 override body의 미리보기는 원계약·부모·원문·체크포인트를 보존한다')
 req=n.request(data,source='return amount+8;');x.rpc('authorBatch',**req);assert x.rpc('settledAuthorBatch',**req)['settled'];saved=x.checkpoint();n.original();f.stop();f.start(1);assert x.rpc('settledAuthorBatch',**req)['settled'] and x.checkpoint()==saved;x.rpc('authorBatch',**req);assert x.checkpoint()==saved;n.original();f.checked('소유 override의 원자 그룹과 receipt는 cold에서 같은 경로로 복원된다')
 ready=x.rpc('read',id=n.child);assert ready['diagnostics']['state']=='source-ready';ids=ready['reviewIds'];f.invoke('reviewGroup',{'target':'portable','ids':[root for root in ids if '/node:' in root]},False);n.original()
 review=f.invoke('reviewGroup',{'target':'portable','ids':ids});parent_file.write_bytes(n.physical[parent_file]+b'\n// peer after review\n');reply,state=x.any_invoke('confirmGroup',{'token':review['state']['review']['token'],'ids':ids});assert not reply.get('result',{}).get('sourceConfirmed');assert (f.project/'Flow.graph.json').read_bytes()==n.physical[f.project/'Flow.graph.json'] and parent_file.read_bytes()!=n.physical[parent_file];parent_file.write_bytes(n.physical[parent_file]);f.stop();f.start(2);f.checked('Review 이후 부모 선언 경합은 최종 CAS에서 전체를 거절하고 부모와 자기 원본을 보존한다')
 review=f.invoke('reviewGroup',{'target':'portable','ids':ids});f.invoke('confirmGroup',{'token':review['state']['review']['token'],'ids':ids});n.ancestors_original();x.build('override-after',11);f.checked('Confirm은 자식 구현만 바꾸고 부모·상속 참조·공개 계약과 실제 호출 의미를 보존한다')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
