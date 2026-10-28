"""Exact whole-body value -> out and one CAS candidate; isolated sources only."""
import copy
import hashlib
import json
import v536_information_shared_value_out_fixture as x

r=x.request()
for row in r['changes']:
    one=copy.deepcopy(r);one['changes']=[row];x.n.prepare(one)
x.unchanged();x.f.checked('명시 값→out 본문과 제거 caller 입력의 두 단일 후보는 유효하고 원본은 그대로다')
if x.mode=='reproduce':
    x.n.prepare(r,False);x.unchanged();x.f.checked('기존 그룹만 유효한 전체 C# 값→out 결합 저장을 거절한다')
else:
    result=x.n.prepare(r);updates=result['updates']+result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']} for row in updates})
    assert len({row['id'] for row in updates})==len(updates) and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest() for row in updates)
    reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse)
    assert {row['id']:row['text'] for row in updates}=={row['id']:row['text'] for row in other['updates']+other['linkedUpdates']}
    (x.f.case/'prepared-candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();x.f.checked('역순·원래hash·하나의 후보는 native/public out·명시 입력 해제·caller/import·원문과 경로를 보존한다')
    for fault in ['type','order','count','return','role','map','inputs','disconnect','disconnect-value','outputs','bodies','body-mode','receipt','body-read-before-assign','source','context','copy']:
        bad=copy.deepcopy(r);row=bad['changes'][1];m=row['mapping'];body=next(iter(m['bodies'].values()));call=next(iter(m['callers'].values()))
        if fault=='type':row['signature']['args'][0]['type']='string'
        elif fault=='order':row['signature']['args'].reverse()
        elif fault=='count':row['signature']['args'].append({'name':'extra','type':'long'})
        elif fault=='return':row['signature']['return']='void'
        elif fault=='role':row['signature']['args'][1]['mode']='ref'
        elif fault=='map':m['args']['count']=None
        elif fault=='inputs':call['inputs']['count']='count'
        elif fault=='disconnect':call['disconnect']={}
        elif fault=='disconnect-value':call['disconnect']['count']='null'
        elif fault=='outputs':call['outputs']['return']='count'
        elif fault=='bodies':m['bodies']={}
        elif fault=='body-mode':body['signature']['args'][1]['mode']='ref'
        elif fault=='receipt':body['whole']['hash']='0'*64
        elif fault=='body-read-before-assign':body['text']='nativeTotal=checked(nativeTotal+nativeAmount);return nativeTotal;'
        elif fault in ['context','copy']:
            key=x.functions[1]+'Body/body:common';g=json.loads(bad['units'][key]['draft'])
            if fault=='context':g['locals']=[{'id':'held','name':'기존 지역값','type':'long','source':{'input':'amount'}}]
            else:g['copySource']={'id':'External::Source'}
            bad['units'][key]['draft']=json.dumps(g);body['whole']['hash']=hashlib.sha256(bad['units'][key]['draft'].encode()).hexdigest()
        else:
            key=x.n.caller+'Body/body:common';g=json.loads(bad['units'][key]['draft']);g['nodes'][0]['intent']='source changed';bad['units'][key]['draft']=json.dumps(g)
        x.n.prepare(bad,False);x.unchanged()
    x.f.checked('마지막 타입/역할/대응·해제/출력·본문/receipt/컴파일·다른 문맥 오류는 전부 미적용이며 입력은 보존된다')
    p=x.f.project/'caller.graph.json';raw=p.read_bytes()
    try:
        g=json.loads(raw);g['nodes'][0]['intent']='peer 변경';p.write_text(json.dumps(g));x.n.prepare(r,False)
        assert all((x.f.project/path).read_bytes()==data for path,data in x.snapshot.items() if path!='caller.graph.json')
    finally:p.write_bytes(raw)
    x.unchanged();x.f.checked('실제 caller source 경합은 원래 기준에서 두 계약을 함께 거절하고 부모/다른 입력을 보존한다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'actualWindows':False,'newContractIds':False},ensure_ascii=False))
