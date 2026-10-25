"""Registered declarations are immutable receipts, never editable dependencies."""
import copy,json
import v536_information_registered_fixture as x
r=x.request();p=x.n.prepare(r)
rows={row['id']:row['text'] for row in p['linkedUpdates']}
assert json.loads(rows[x.caller_id])['source']==x.caller_text
assert not any(id.startswith('External.Fields::') for id in rows)
assert {row['path'] for row in p['observations']}>={str(x.pack),str(x.registered/'Echo.celem')}
assert str(x.registered/'EchoBody.celem') not in {row['path'] for row in p['observations']}
x.unchanged()
print('PASS 등록 함수와 소유 caller 수동 C#·import를 한 후보에 담고 외부 선언/manifest만 관측한다',flush=True)
for fault in ['missing','forged','caller','extra','signature','compile']:
    bad=copy.deepcopy(r);mapping=bad['changes'][0]['mapping'];proof=mapping['dependencies'][x.caller+'Body']
    if fault=='missing':mapping.pop('dependencies')
    elif fault=='forged':proof['contracts'][x.foreign]['manifestHash']='0'*64
    elif fault=='caller':proof['callerHash']='0'*64
    elif fault=='extra':mapping['dependencies']['External.Fields::EchoBody']=copy.deepcopy(proof)
    elif fault=='signature':bad['units'][x.caller+'Body']['draft']=bad['units'][x.caller+'Body']['draft'].replace('Registered (long)','Registered (string)')
    else:mapping['bodies'][x.caller_id]['text']='return calls.Registered.Invoke("not a long");'
    x.n.prepare(bad,False);x.unchanged()
print('PASS 누락·위조·다른 소유·오래된 typed import와 C# 오류를 전체 거절한다',flush=True)
for path in [x.pack,x.registered/'Echo.celem']:
    original=path.read_bytes()
    try:
        path.write_bytes(original+' // 실제 등록 계약 변경\n'.encode())
        x.n.prepare(r,False)
    finally:path.write_bytes(original)
    x.unchanged()
print('PASS 등록 manifest/선언 변경은 입력 후보를 재사용하지 않고 전체 거절한다',flush=True)
body=x.registered/'Echo.csbody';original=body.read_bytes()
try:
    body.unlink()
    x.n.prepare(r)
finally:body.write_bytes(original)
x.unchanged()
print('PASS 등록 provider 본문 없이 계약 검증을 수행하며 외부 구현을 편집 대상으로 삼지 않는다',flush=True)
print(json.dumps({'checks':4,'evidence':str(x.f.case),'pureCandidate':True,'projectRun':False},ensure_ascii=False))
