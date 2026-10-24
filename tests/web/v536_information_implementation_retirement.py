"""Implementation lifetime candidates; existing function archive regression plus isolated fixture only."""
import copy,json,pathlib,runpy,sys
m=runpy.run_path(str(pathlib.Path(__file__).with_name('v536_information_function_retirement.py')))
root=m['root'];units=copy.deepcopy(m['units']);owner=m['owner'];fn=m['fn'];impl=m['impl'];n=m['n'];h=m['h'];run=m['run'];node=m['node'];checks=[]
# Reuse only that test's temporary fixture, restoring original bytes before the
# independent lifetime. No user project, engine account or execution is involved.
for unit in units.values():m['write'](unit['path'],unit['original'])
original={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
def unchanged():assert original=={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
def checked(text):checks.append(text);print('PASS '+text,flush=True)
plan=run('plan',mode='implementation-only-v1');assert plan['mode']=='implementation-only-v1' and not plan['references'];assert fn not in plan['ids'] and set(plan['ids'])=={impl,impl+'/body:common',node,impl+'/body:linux'};assert 'contain function '+fn in plan['ownerAfter'] and 'provide '+fn not in plan['ownerAfter'];assert fn.split('::')[1]+' function ' in plan['afterManifest'];assert impl.split('::')[1]+' implementation ' not in plan['afterManifest'];assert plan['functionBefore']==units[fn];unchanged();checked('구현만 후보는 함수 선언·이름·핀·contain/등록을 유지하고 단독 구현과 모든 target 본문만 보관한다')
for field in ['mode','functionBefore']:
 forged=copy.deepcopy(plan)
 if field=='mode':forged[field]='unknown-lifetime'
 else:forged[field]['draft']+=' // forged declaration'
 run('apply',False,evidence=forged)
for kind,text,blocked in [('implementation','implementation '+n+'Caller for '+n+'Main () -> int {import '+fn+' as Call () -> void;}',False),('schema','schema '+n+'Caller {provide '+fn+' with '+impl+';}',True)]:
 altered=copy.deepcopy(units);altered[n+'Caller']={'id':n+'Caller','kind':kind,'path':'Caller.celem','revision':1,'original':text,'draft':text,'baseline':h(text)};m['write']('Caller.celem',text);p=run('plan',mode='implementation-only-v1',units=altered);assert bool(p['references']) is blocked
 if blocked:run('apply',False,units=altered,evidence=p)
 (root/'Caller.celem').unlink()
new=copy.deepcopy(units);new[fn]['draft']+='\n// pending declaration';run('plan',False,mode='implementation-only-v1',units=new);unchanged();checked('함수 호출 참조는 유지하고 공유 구현·변조 모드·미확정 선언은 미적용하며 기존 계약을 임의 변경하지 않는다')
a=run('apply',evidence=plan);receipt=a['retirements'][plan['token']];assert a['units'][fn]==units[fn];assert a['retainedFunction']==fn and a['mode']=='implementation-only-v1';assert set(units)-set(a['units'])==set(plan['ids']);run('validate',receipt=receipt,units=a['units']);forged=copy.deepcopy(receipt);forged['functionBefore']['draft']=forged['functionBefore']['draft'].replace('() -> void','() -> long');forged['functionBefore']['original']=forged['functionBefore']['original'].replace('() -> void','() -> long');run('validate',False,receipt=forged,units=a['units']);restored=run('recover',units=a['units'],retirements=a['retirements'],evidence=receipt);assert not restored['retirements'];assert all(restored['units'][id]['draft']==u['draft'] for id,u in units.items());unchanged();checked('한 apply/pending 복구 후보는 선언·다른 정보·미반영 본문·정확한 값과 원본 파일을 보존한다')
changed=copy.deepcopy(units);changed[owner]['draft']+='\n// peer';run('apply',False,evidence=plan,units=changed);unchanged();checked('계획 후 실제 동시 수정은 구현과 선언 모두 부분 적용하지 않는다')
confirmed=copy.deepcopy(a);receipt=confirmed['retirements'][plan['token']];receipt['state']='confirmed'
for id in [owner,n+'ProjectManifest']:
 unit=confirmed['units'][id];m['write'](unit['path'],unit['draft']);unit['original']=unit['draft'];unit['baseline']=h(unit['draft']);unit.pop('retirementGroup',None)
original={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()};run('validate',receipt=receipt,units=confirmed['units']);run('plan',False,units=confirmed['units'],retirements=confirmed['retirements'],ownerHash=h(confirmed['units'][owner]['draft']))
changed=copy.deepcopy(confirmed['units']);changed[fn]['draft']+='\n// preserve newly edited function';run('validate',receipt=receipt,units=changed);assert not run('unapplied',transition='recover',evidence=receipt,units=changed,retirements=confirmed['retirements'])['unapplied'];run('recover',False,units=changed,retirements=confirmed['retirements'],evidence=receipt);unchanged();checked('확정 뒤 선언의 새 편집은 archive를 손상시키지 않으며 복구나 함수 전체 삭제가 새 선언을 덮어쓰지 못한다')
r=run('recover',units=confirmed['units'],retirements=confirmed['retirements'],evidence=receipt);restoring=r['retirements'][plan['token']];assert r['units'][fn]['draft']==units[fn]['draft'];assert r['units'][node]['draft']==units[node]['draft'];run('validate',receipt=restoring,units=r['units']);c=run('cancel',units=r['units'],retirements=r['retirements'],evidence=restoring);assert c['units'][fn]==confirmed['units'][fn] and c['units'][owner]['draft']==confirmed['units'][owner]['draft'];changed=copy.deepcopy(r['units']);changed[node]['draft']+=' ';run('cancel',False,units=changed,retirements=r['retirements'],evidence=restoring);unchanged();checked('확정 후 복구와 복구 취소는 함수 선언을 바꾸지 않고 새 본문 입력이 있으면 취소를 거절한다')
outcome={'version':1,'token':plan['token'],'action':'recover','workspace':plan['workspace'],'phase':'restoring','result':{'state':'staged','owner':owner,'manifest':n+'ProjectManifest','ids':plan['ids'],'mode':'implementation-only-v1','retainedFunction':fn,'checkpointSaved':True,'physicalSourceRemoved':False,'sourceConfirmed':False},'sources':{},'absent':[]}
for id in [*plan['ids'],owner,n+'ProjectManifest',fn]:
 unit=r['units'][id];outcome['sources'][id]={'kind':unit['kind'],'path':unit['path'],'hash':h(unit['draft'])}
assert run('settled',outcome=outcome,units=r['units'],retirements=r['retirements'])['settled'];changed=copy.deepcopy(r['units']);changed[fn]['draft']+='\n// later input';assert not run('settled',outcome=outcome,units=changed,retirements=r['retirements'])['settled'];bad=copy.deepcopy(outcome);bad['sources'].pop(fn);run('validate-outcome',False,outcome=bad);unchanged();checked('완료 근거는 남겨 둔 함수 source까지 포함하고 응답 유실 뒤 새 선언 입력이나 불완전 proof를 완료로 채택하지 않는다')
print(json.dumps({'newImplementationChecks':checks,'priorFunctionChecks':len(m['checks']),'evidence':str(root),'nativePure':True,'renderer':False,'engineIntegrated':False,'accountOrInference':False,'sourceWrittenOnlyFixture':True},ensure_ascii=False))
