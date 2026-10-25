"""Composed caller updates keep one original hash and never mutate sources."""
import copy
import hashlib
import json
import v536_information_shared_callers_fixture as x

r=x.request();held=copy.deepcopy(r);result=x.n.prepare(r)
assert r==held
updates=result['updates']+result['linkedUpdates']
ids=[row['id'] for row in updates];assert len(ids)==len(set(ids))
rows={row['id']:{'draft':row['text']} for row in updates}
x.verify_rows(rows)
for row in result['linkedUpdates']:
    assert row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()
x.unchanged()
x.f.checked('두 계약과 공유 호출자 입력/연결을 원래 hash 한 개씩 가진 순수 결합 후보로 준비한다')
reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse)
assert {row['id']:row['text'] for row in updates}=={row['id']:row['text'] for row in other['updates']+other['linkedUpdates']}
x.f.checked('편집 순서를 뒤집어도 최종 공유 caller와 각 callee 원문이 같은 후보가 된다')
for fault in ['last-type','last-map','missing-source','copy','native-context']:
    bad=copy.deepcopy(r)
    if fault=='last-type':bad['changes'][1]['signature']['args'][0]['type']='string'
    elif fault=='last-map':bad['changes'][1]['mapping']['args']['amount']='count'
    elif fault=='missing-source':del bad['units'][x.functions[1]+'Body/body:common']
    else:
        unit=bad['units'][x.n.caller+'Body/body:common'];g=json.loads(unit['draft'])
        if fault=='copy':g['copySource']={'implementation':'Other.Pack::Donor'}
        else:g['nodes'][0]['implementationContext']={'implementation':x.n.caller+'Body'}
        unit['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
x.f.checked('마지막 함수 타입/대응 오류·snapshot 누락·copy/whole 문맥은 첫 계약도 적용하지 않고 거절한다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'pureCandidate':True,
                  'actualWindows':False,'copyIdentityDecisionUsed':False},ensure_ascii=False))
