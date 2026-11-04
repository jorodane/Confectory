"""Restore only an exact unpublished declaration into the same owned draft.

The fixture exercises the actual editor engine. Restoration does not save a
checkpoint, write a source file or grant access to another project/source.
"""
import copy,json
import v666_async_new_function_fixture as x

f=x.f
def inspect():
 f.invoke('select',dict(id=x.feature))
 return f.invoke('inspectDeclaration',dict(id=x.feature))['state']['declaration']
def restore(snapshot,ok=True):return x.rpc('restoreFeatureDeclaration',ok,id=x.feature,declaration=snapshot)
try:
 f.start(0);f.invoke('saveDraft',{});before=x.checkpoint()
 f.invoke('createDeclaration',dict(id=x.feature,kind='function'));info=inspect()
 signature=dict(args=[dict(name='input',type='int'),dict(name='count',type='long',mode='out')],**{'return':'int'})
 f.invoke('editFunctionContract',dict(id=x.feature,revision=info['revision'],hash=info['textHash'],edit=dict(signature=signature,description='복구할 새 계약 😀')))
 info=inspect();observed_signature=copy.deepcopy(info['signature']);preview=x.rpc('readFeature',id=x.feature,revision=info['revision'],hash=info['textHash']);snapshot=preview['creationDeclaration'];assert snapshot and 'out long count'in snapshot['text']and 'int input'in snapshot['text'],(info,snapshot)
 destination=f.project/snapshot['path'];assert not destination.exists() and before==x.checkpoint();x.original();f.stop();f.start(1)
 for field,value in [('schema',2),('project',str(f.case/'foreign.cproj')),('id',f.n+'Main'),('path','../escape.celem'),('path',str(f.case/'escape.celem')),('manifest',f.n+'Unit'),('manifestHash','0'*64),('manifestBaseline','0'*64),('checkpointHash','0'*64)]:
  bad=copy.deepcopy(snapshot);bad[field]=value;restore(bad,False);assert before==x.checkpoint() and not destination.exists();x.original()
 for kind in ['extra','duplicate-source','wrong-source','wrong-text','malformed']:
  bad=copy.deepcopy(snapshot)
  if kind=='extra':bad['access']='allow'
  elif kind=='duplicate-source':bad['sources'][1]=copy.deepcopy(bad['sources'][0])
  elif kind=='wrong-source':bad['sources'][0]['hash']='0'*64
  elif kind=='wrong-text':bad['text']='function '+f.n+'Main () -> void {}'
  else:bad['text']+=' invalid'
  restore(bad,False);assert before==x.checkpoint() and not destination.exists();x.original()
 f.checked('다른 프로젝트/ID/경로·변조된 선언/등록/checkpoint/중복 관측을 전체 거절하고 원본과 저장 초안을 보존한다')
 manifest=f.project/'project.cproj';raw=manifest.read_bytes();manifest.write_bytes(raw+b' ')
 try:restore(snapshot,False)
 finally:manifest.write_bytes(raw)
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));raw=checkpoint.read_bytes();checkpoint.write_bytes(raw+b' ')
 try:restore(snapshot,False)
 finally:checkpoint.write_bytes(raw)
 destination.parent.mkdir(parents=True,exist_ok=True);destination.symlink_to(manifest)
 try:restore(snapshot,False)
 finally:destination.unlink()
 destination.write_text('peer-owned collision')
 try:restore(snapshot,False);assert destination.read_text()=='peer-owned collision'
 finally:destination.unlink()
 assert before==x.checkpoint();x.original();f.checked('실제 등록/checkpoint 충돌·링크·새 목적지 충돌은 복구하지 않고 동료 파일을 보존한다')
 result=restore(snapshot);assert result['restored']and result['matching']and not result['sourceWritten'];info=inspect();assert info['signature']==observed_signature and f.state()['draft']['text']==snapshot['text'];assert restore(snapshot)['matching']and not restore(snapshot)['restored'];assert before==x.checkpoint()and not destination.exists();x.original()
 f.invoke('editFunctionContract',dict(id=x.feature,revision=info['revision'],hash=info['textHash'],edit=dict(description='동료의 메모리 초안')));changed=f.state()['draft']['text'];result=restore(snapshot);assert result['existing']and not result['matching'];assert f.state()['draft']['text']==changed and before==x.checkpoint();x.original()
 f.checked('같은 원래 관측만 헤더/입출력/본문을 메모리 초안으로 정확히 복구하고 반복 호출·기존 변경 보존에서 쓰기를 하지 않는다')
 print('ASYNC_CREATION_RESTORE_FIXTURE',f.case,flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
