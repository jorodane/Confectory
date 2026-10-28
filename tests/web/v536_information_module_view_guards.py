"""Bound module candidates and receipts across real isolated information windows."""
import json,uuid
import v536_field_definitions_ui as d
f=d.f;owner=d.owner
p=f.project/'FreeInfo.celem';p.write_text(p.read_text().replace('FreeInfo {','FreeInfo {module '+f.n+'Rules;',1))
f.original={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file()}
def open_view(slot='1',id=owner):
 f.invoke('openEditorView',{'view':slot,'id':id,'viewMode':'properties'});return row(slot)
def row(slot='1'):return next(r for r in f.state()['editorViews'] if r['view']==slot)
def surface(slot='1'):return {'view':slot,'viewBinding':row(slot)['authorBinding'],'owner':row(slot)['id']}
def rpc(action,ok=True,slot='1',**args):return f.invoke('blueprint',{'action':action,**surface(slot),**args},ok)['result'].get('result')
def basis():
 s=row()['schema'];return {'id':owner,'hash':s['textHash'],'revision':s['revision']}
def primary():assert f.state()['draft']['id']==f.id and f.state()['draft']['text']==original_primary;f.originals()
try:
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});original_primary=f.state()['draft']['text'];open_view();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 request={'action':'implementationCallables',**surface(),'id':owner,'function':f.n+'Slot2','scope':'owned','query':'Donor','page':0}
 for bad in [{k:v for k,v in request.items() if k!='viewBinding'},{**request,'viewBinding':'0'*32},{**request,'id':f.n+'Monster'},{**request,'uiSurface':'view:1'}]:f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;primary()
 found=rpc('implementationCallables',id=owner,function=f.n+'Slot2',scope='owned',query='Donor',page=0);assert [r['id'] for r in found['rows']]==[f.n+'Donor'];primary();f.checked('모듈 선택은 현재 정보/프로젝트/창 nonce만 허용하며 누락·위조·타 owner·client surface는 미적용한다')
 implementation=f.n+'ViewImport_'+uuid.uuid4().hex;plan=rpc('readImplementation',**basis(),function=f.n+'Slot2',implementation=implementation,reference=f.n+'Donor');selected={'function':f.n+'Slot2','implementation':implementation,'reference':f.n+'Donor','basis':plan['basis']};open_view('2');rpc('applySlots',False,slot='2',id=owner,rows=[selected]);assert checkpoint.read_bytes()==before;primary();rpc('applySlots',id=owner,rows=[selected]);primary();saved=checkpoint.read_bytes()
 intent={'function':f.n+'Slot2','implementation':implementation,'reference':f.n+'Donor','fingerprint':plan['contractFingerprint']};assert rpc('settledSlots',id=owner,rows=[intent])['settled'];assert not rpc('settledSlots',slot='2',id=owner,rows=[intent])['settled'];assert not f.invoke('blueprint',{'action':'settledSlots','id':owner,'rows':[intent]})['result']['result']['settled'];assert checkpoint.read_bytes()==saved;f.checked('한 창의 import 후보와 완료 receipt는 다른 창/primary가 적용하거나 완료로 채택하지 못하고 primary 원문을 보존한다')
 old=surface();f.invoke('closeEditorView',{'view':'1','id':owner});open_view();assert old['viewBinding']!=surface()['viewBinding'];f.invoke('blueprint',{'action':'settledSlots',**old,'id':owner,'rows':[intent]},False);assert rpc('settledSlots',id=owner,rows=[intent])['settled'];assert checkpoint.read_bytes()==saved;primary();f.checked('닫힘/reopen은 오래된 nonce를 거절하고 새 명시 창에서 기존 저장 결과만 읽어 확인한다')
 s=row()['schema'];graph=implementation+'/body:common';data=rpc('read',id=graph,ownerHash=s['textHash'],ownerRevision=s['revision']);open_view('2');before=checkpoint.read_bytes();rpc('intent',False,slot='2',id=graph,basis=data['basis'],node='imported',text='wrong view');assert checkpoint.read_bytes()==before;primary();rpc('intent',id=graph,basis=data['basis'],node='imported',text='현재 정보의 선택한 import 설명');primary();f.checked('직접 본문 편집은 같은 정보라도 실제로 관찰한 view basis와 독점 provide가 필요하고 타창 basis로 변경할 수 없다')
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
except Exception:
 try:(f.case/'module-view-guards-failure.json').write_text(json.dumps({'state':f.state(),'checks':f.checks},ensure_ascii=False,indent=2))
 except Exception:pass
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
