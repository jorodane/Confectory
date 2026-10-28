"""Two same-function calls compose original input receipts before output routing."""
import copy,json
import v536_information_whole_contract_fixture as x
assert x.scenario=='value-out'
x.new['return']='bool';x.selected['return']='bool';x.edited='nativeAmount=1;nativeTotal=2;return true; // 명시 out/반환'
x.outputs={'return':'count','count':'count'}
p=x.f.project/'caller.graph.json';g=json.loads(p.read_text());second=copy.deepcopy(g['nodes'][0]);second['id']='invoke2';second['arguments']['amount']={'node':'invoke'};g['nodes'].append(second);g['edges']=[{'from':'invoke','port':'next','to':'invoke2'},{'from':'invoke2','port':'next','to':'exit:return'}];g['exits']['return']={'node':'invoke2'};p.write_text(json.dumps(g))
x.snapshot={str(p.relative_to(x.f.project)):p.read_bytes() for p in x.f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(x.f.project).parts}
r=x.request();v=x.n.prepare(r);rows={u['id']:u['text'] for u in v['linkedUpdates']};after=json.loads(rows[x.caller+'Body/body:common']);assert all(not n['arguments'] for n in after['nodes']) and after['exits']['return']=={'node':'invoke2','output':'count'}
print('PASS 두 호출의 원래 입력 해제 증거를 먼저 결합한 뒤 출력 이름을 대응하여 중간 graph와 부분 적용을 만들지 않는다',flush=True)
# An upstream return used only by the explicitly removed next-call input may
# disappear; references still present elsewhere must continue to refuse.
x.new['return']='void';x.selected['return']='void';x.edited='nativeAmount=1;nativeTotal=2;return;';x.outputs={'return':None,'count':'count'}
g['exits']['return']={'node':'invoke2','output':'count'};p.write_text(json.dumps(g));x.snapshot={str(p.relative_to(x.f.project)):p.read_bytes() for p in x.f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(x.f.project).parts}
r=x.request();v=x.n.prepare(r);after=json.loads(next(u['text'] for u in v['linkedUpdates'] if u['id']==x.caller+'Body/body:common'));assert after['exits']['return']==g['exits']['return'] and all(not n['arguments'] for n in after['nodes'])
bad=copy.deepcopy(r);next(iter(bad['changes'][0]['mapping']['callers'].values()))['disconnect']={};x.n.prepare(bad,False)
assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
# Removing a return that still feeds the caller itself must remain rejected.
g['exits']['return']={'node':'invoke2'};p.write_text(json.dumps(g));x.snapshot={str(p.relative_to(x.f.project)):p.read_bytes() for p in x.f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(x.f.project).parts};x.n.prepare(x.request(),False)
assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
print('PASS 명시 해제로 사라지는 연결만 제거하며 누락된 해제나 남은 사용처는 전체 미적용으로 원문을 보존한다',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'pureCandidate':True,'projectRun':False},ensure_ascii=False))
