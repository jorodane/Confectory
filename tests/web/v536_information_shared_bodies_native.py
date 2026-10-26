"""Exact whole-body native body edits and one CAS candidate; isolated sources only."""
import copy
import hashlib
import json
import v536_information_shared_bodies_fixture as x

r=x.request()
for row in r['changes']:
    one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
x.unchanged();x.f.checked('계약을 유지한 직접 편집 본문의 두 단일 후보는 유효하고 원본은 그대로다')
if x.mode=='reproduce':
    x.n.prepare(r,False);x.unchanged();x.f.checked('기존 그룹만 유효한 계약 그대로 두 C# 본문 결합 저장을 거절한다')
else:
    result=x.n.prepare(r);assert {row['id'] for row in result['linkedUpdates']}=={fn+'Body/body:common' for fn in x.functions};updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']} for row in updates})
    assert len({row['id'] for row in updates})==len(updates) and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse)
    assert {row['id']:row['text'] for row in updates}=={row['id']:row['text'] for row in other['updates']+other['linkedUpdates']}
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();x.f.checked('역순·원래hash·하나의 후보는 그대로인 native/public 계약·직접 편집 원문·caller/import·원문과 경로를 보존한다')
    for fault in ['contract','native','map','caller','missing','path','hash','syntax','compile','boundary','parent','shared']:
        bad=copy.deepcopy(r);row=bad['changes'][1];m=row['mapping'];body=next(iter(m['bodies'].values()))
        if fault=='contract':row['signature']['args'][0]['type']='string'
        elif fault=='native':body['signature']['args'].reverse()
        elif fault=='map':m['args']['count']='amount'
        elif fault=='caller':m['callers']={}
        elif fault=='missing':body.pop('beforeSignature')
        elif fault=='path':body['path']='other.csbody'
        elif fault=='hash':body['hash']='0'*64
        elif fault=='syntax':body['text']='return ('
        elif fault=='compile':body['text']='return missingValue;'
        elif fault=='boundary':body['text']='} public void Escape() {'
        elif fault=='parent':
            key=x.functions[1]+'Body';bad['units'][key]['draft']='implementation '+key+' : External::Parent for '+x.functions[1]+' (long nativeAmount,long nativeCount) -> long {}'
        elif fault=='shared':
            key=x.functions[1]+'Body';bad['units'][key]['draft']=bad['units'][key]['draft'].replace(x.paths[x.functions[1]],x.paths[x.functions[0]])
        else:
            key=x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft']);g['nodes'][0]['intent']='source changed';bad['units'][key]['draft']=json.dumps(g)
        (x.f.case/'fault-current.json').write_text(json.dumps({'fault':fault,'request':bad},ensure_ascii=False))
        x.n.prepare(bad,False);x.unchanged()
    x.f.checked('마지막 계약/본문/원래 서명/해시·구문/컴파일/보호 경계·소유/경로 오류는 전부 미적용이며 입력은 보존된다')
    p=x.f.project/'caller.graph.json';raw=p.read_bytes()
    try:
        g=json.loads(raw);g['nodes'][0]['intent']='peer 변경';p.write_text(json.dumps(g));x.n.prepare(r,False)
        assert all((x.f.project/path).read_bytes()==data for path,data in x.snapshot.items() if path!='caller.graph.json')
    finally:p.write_bytes(raw)
    x.unchanged();x.f.checked('실제 caller source 경합은 원래 기준에서 두 계약을 함께 거절하고 부모/다른 입력을 보존한다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'actualWindows':False,'newContractIds':False},ensure_ascii=False))
