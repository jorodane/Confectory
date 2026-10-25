"""Output labels, writer IDs and consumed values stay distinct from C# names."""
import copy,hashlib,json
import v536_information_shared_outputs_fixture as x
r=x.request();held=copy.deepcopy(r);result=x.n.prepare(r);assert r==held
updates=result['updates']+result['linkedUpdates'];assert len({p['id'] for p in updates})==len(updates)
x.verify_rows({p['id']:{'draft':p['text']} for p in updates})
for p in result['linkedUpdates']:assert p['hash']==hashlib.sha256(r['units'][p['id']]['draft'].encode()).hexdigest()
x.unchanged();x.f.checked('두 out 계약·writer·공개 이름과 A out→B 입력→최종 out 연결은 원래 hash의 한 후보로 결합한다')
reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.n.prepare(reverse)
assert {p['id']:p['text'] for p in updates}=={p['id']:p['text'] for p in other['updates']+other['linkedUpdates']}
x.f.checked('역순 편집도 같은 최종 caller이며 같은 count 이름의 두 출력은 call ID로 구별하고 C#·설명을 유지한다')
for fault in ['type','role','return','remove','map','duplicate','stale','extra-plan','native-context','dependency']:
    bad=copy.deepcopy(r);row=bad['changes'][1]
    if fault=='type':row['signature']['args'][1]['type']='double'
    elif fault=='role':row['signature']['args'][1]['mode']='ref'
    elif fault=='return':row['signature']['return']='void'
    elif fault=='remove':row['signature']['args'].pop();row['mapping']['args']['count']=None
    elif fault=='map':row['mapping']['args']['count']='amount'
    elif fault=='duplicate':row['signature']['args'][1]['name']='amount';row['mapping']['args']['count']='amount'
    elif fault=='stale':row['hash']='0'*64
    elif fault=='extra-plan':row['mapping']['callers']={}
    elif fault=='dependency':
        unit=bad['units'][x.functions[1]+'Body'];unit['draft']=unit['draft'].replace('{','{import '+x.functions[0]+' as Peer (long,out long) -> long;',1)
    else:
        unit=bad['units'][x.n.caller+'Body/body:common'];graph=json.loads(unit['draft']);graph['nodes'][0]['implementationContext']={'implementation':x.n.caller+'Body'};unit['draft']=json.dumps(graph)
    x.n.prepare(bad,False);x.unchanged()
x.f.checked('마지막 타입/역할/반환/삭제/잘못된 대응·중복·오래된 원문 및 본문/의존 혼합은 전부 미적용이다')
print(json.dumps({'checks':x.f.checks,'evidence':str(x.f.case),'copyPolicyUsed':False,'actualWindows':False},ensure_ascii=False))
