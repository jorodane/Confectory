"""Explicit original output choices, not latest hashes or guessed connections."""
import copy,hashlib,json
import v536_information_shared_return_types_fixture as x
r=x.request();held=copy.deepcopy(r);result=x.n.prepare(r);assert r==held
updates=result['updates']+result['linkedUpdates'];assert len({p['id'] for p in updates})==len(updates)
x.verify_rows({p['id']:{'draft':p['text']} for p in updates})
for p in result['linkedUpdates']:assert p['hash']==hashlib.sha256(r['units'][p['id']]['draft'].encode()).hexdigest()
x.unchanged();x.f.checked('두 반환 타입·writer와 명시된 생산자→소비자 대응을 원래 hash 한 개씩 가진 후보로 결합한다')
reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse)
assert {p['id']:p['text'] for p in updates}=={p['id']:p['text'] for p in other['updates']+other['linkedUpdates']}
x.f.checked('역순도 같은 최종 import/call/writer이며 C# 원문·정확한 입력·제어 경로를 보존한다')
scalars=copy.deepcopy(r)
for row,typ,literal in zip(scalars['changes'],['bool','string'],['true','"한글 새 출력 😀"']):
    row['signature']['return']=typ
    for writer in row['mapping']['outputs'].values():writer.update(type=typ,source={'valueJson':literal})
scalar_result=x.n.prepare(scalars)
for fn,typ,value in zip(x.functions,['bool','string'],[True,'한글 새 출력 😀']):
    leaf=json.loads(next(p['text'] for p in scalar_result['linkedUpdates'] if p['id']==fn+'Body/body:common'));writer=next(p for p in leaf['nodes'] if p['kind']=='export' and p['output']=='return')
    assert writer['arguments']['value']=={'constant':value} and writer['signature']['args'][0]['type']==typ
x.unchanged();x.f.checked('명시 bool/한글 string 반환도 기존 scalar 타입 검사와 호환 소비 대응으로 준비한다')
single=copy.deepcopy(r);single['changes']=single['changes'][:1];partial=x.n.prepare(single)
intermediate=next(p['text'] for p in partial['linkedUpdates'] if p['id']==x.n.caller+'Body/body:common')
for fault in ['intermediate-hash','writer-before','writer-source','missing-output','drop-consumed','wrong-return-type','input-plan','return','role','remove','body','source']:
    bad=copy.deepcopy(r);row=bad['changes'][1];mapping=row['mapping'];plan=next(iter(mapping['callers'].values()));writer=next(iter(mapping['outputs'].values()))
    if fault=='intermediate-hash':plan['hash']=hashlib.sha256(intermediate.encode()).hexdigest()
    elif fault=='writer-before':writer['before']='null'
    elif fault=='writer-source':writer['source']={'input':'amount'}
    elif fault=='missing-output':mapping['outputs']={}
    elif fault=='drop-consumed':plan['outputs']['return']=None
    elif fault=='wrong-return-type':plan['outputs']['return']='return'
    elif fault=='input-plan':plan['inputs']['amount']='real'
    elif fault=='return':row['signature']['return']='long';row['signature']['args'][2]['type']='double'
    elif fault=='role':row['signature']['args'][2]['mode']='ref'
    elif fault=='remove':row['signature']['args'].pop();mapping['args']['count']=None
    elif fault=='body':mapping['bodies']={}
    else:
        unit=bad['units'][x.n.caller+'Body/body:common'];g=json.loads(unit['draft']);g['nodes'][1]['intent']='선택 후 바뀐 문맥';unit['draft']=json.dumps(g)
    x.n.prepare(bad,False);x.unchanged()
x.f.checked('중간 hash 재사용·writer/값/소비 대응 누락·타입/역할/반환/본문·문맥 변경은 첫 함수도 적용하지 않는다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'copyPolicyUsed':False,'actualWindows':False},ensure_ascii=False))
