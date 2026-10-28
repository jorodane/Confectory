"""Owned information body checkpoint candidates and replay/forgery guards; isolated engine only."""
import copy,json,uuid
import v536_field_definitions_ui as d
f=d.f;owner=d.owner;fn=owner+'_Function_'+'9'*32

def rpc(action,ok=True,**request):return f.invoke('blueprint',{'action':action,**request},ok)['result'].get('result')
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def binding():
 s=schema();return {'owner':owner,'ownerHash':s['textHash'],'ownerRevision':s['revision']}
def read():return rpc('read',id=graph,**binding())
def request(data,edits):return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':json.dumps(sorted([[row['id'],row['revision'],row['hash']] for row in data['sources']])),'edits':edits,**binding()}
try:
 f.start(0);f.invoke('select',{'id':owner});s=schema();basis=rpc('readOwnerEdits',id=owner,hash=s['textHash']);rpc('applySlots',id=owner,rows=[],basis=basis['basis'],declaration={'id':owner,'hash':s['textHash'],'changes':[{'type':'function-add','id':fn,'name':'원자 본문','description':'정보 전용'}]});row=next(row for row in schema()['ownFunctions'] if row['id']==fn);preview=rpc('readFeature',id=fn,hash=row['hash'],revision=row['revision'],**binding());graph=rpc('createFeature',id=fn,basis=preview['basis'])['id'];data=read();assert data['slotContext']['checkpointPlain'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();original=next(row for row in data['nodes'] if row['id']=='body')['source'];edits=[{'action':'source','node':'body','text':'return; // complete candidate'},{'action':'implementationDescription','node':'$implementation','text':'같은 정보의 본문 설명'}];req=request(data,edits)
 for wrong in [{k:v for k,v in req.items() if not k.startswith('owner')},{**req,'ownerHash':'0'*64},{**req,'owner':f.n+'RefTarget'},{**req,'edits':[{'action':'removeNode','node':'body'}]}]:
  rpc('authorBatch',False,**wrong);assert checkpoint.read_bytes()==before;assert next(row for row in read()['nodes'] if row['id']=='body')['source']==original
 f.originals();f.checked('누락·다른 owner·위조 hash·범위 밖 구조 편집은 정보 본문 저장 후보를 전부 거절하며 원본과 checkpoint를 쓰지 않는다')
 result=rpc('authorBatch',**req);assert result['checkpointSaved'] and result['slotOwnerUpdate']['owner']==owner;current=read();assert next(row for row in current['nodes'] if row['id']=='body')['source']==edits[0]['text'] and current['implementationDescription']==edits[1]['text'];saved=checkpoint.read_bytes();f.originals();f.checked('본문과 구현 설명은 하나의 검증 후보·checkpoint CAS로 함께 저장하며 정보/함수 소유 및 원래 source를 보존한다')
 again=rpc('authorBatch',**req);assert again['settled'] and checkpoint.read_bytes()==saved;assert rpc('settledAuthorBatch',**req)['settled'];forged=copy.deepcopy(req);forged['edits'][0]['text']='return; // forged replay';assert not rpc('settledAuthorBatch',**forged)['settled'];rpc('authorBatch',False,**forged);assert checkpoint.read_bytes()==saved;f.originals();f.checked('원래 receipt 재조회·동일 재시도는 중복 저장 없이 복구하고 변조한 계획은 오래된 checkpoint로 재사용하지 못한다')
 f.stop();f.start(1);f.invoke('select',{'id':owner});assert rpc('settledAuthorBatch',**req)['settled'];assert checkpoint.read_bytes()==saved;current=read();stale=request(current,[{'action':'source','node':'body','text':'return; // stale user input'},{'action':'implementationDescription','node':'$implementation','text':'must not partly apply'}]);rpc('source',id=graph,basis=current['basis'],node='body',text='return; // peer live change');rpc('authorBatch',False,**stale);now=read();assert next(row for row in now['nodes'] if row['id']=='body')['source']=='return; // peer live change' and now['implementationDescription']==edits[1]['text'];assert checkpoint.read_bytes()==saved;f.originals();f.checked('cold의 technical revision 변화는 동일 receipt를 복구하고 실제 peer source 변경은 전체 거절하여 동료 본문과 이전 설명을 보존한다')
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
