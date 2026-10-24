"""Pure candidate gates over real parsed owned call/import declarations."""
import copy,json,re
import v536_information_call_inputs_fixture as c
x,f,n,owner,fn=c.x,c.f,c.n,c.owner,c.fn
gid=fn+'Body/body:common';key=gid+'#inner#amount'
def preview(r):
 return {name:f.metadata(operation,id=owner,function=fn,units=r['units']) for name,operation in [('functionInputs','informationFunctionInputs'),('functionInputUses','informationFunctionInputUses')]}
def candidate():
 r=n.request(x.new,x.mapping['args']);p=preview(r);assert key in p['functionInputUses'];r['changes'][0]['mapping']=x.selections(p);return r
def changed(r,edit):
 g=json.loads(r['units'][gid]['draft']);node=next(v for v in g['nodes'] if v['id']=='inner');edit(r,node);r['units'][gid]['draft']=json.dumps(g)
 selected=r['changes'][0]['mapping']['implementations'][key];selected['hash']=n.h(r['units'][gid]['draft']);return r
try:
 good=candidate();out=n.prepare(good);rows={v['id']:v for v in out['linkedUpdates']};g=json.loads(rows[gid]['text']);assert next(v for v in g['nodes'] if v['id']=='inner')['arguments']['amount']==x.expected_callee();f.checked('정확한 소유 callee/typed import의 일반 call 직접 인자만 명시 후보에 포함한다')
 cases=[]
 cases.append(changed(copy.deepcopy(good),lambda r,node:node.update(postCall={'source':'return;'})))
 cases.append(changed(copy.deepcopy(good),lambda r,node:node.update(feature=fn)))
 cases.append(changed(copy.deepcopy(good),lambda r,node:node.update(feature='Other::InputLeaf')))
 cases.append(changed(copy.deepcopy(good),lambda r,node:node['signature']['args'][0].update(type='string')))
 bad=copy.deepcopy(good);bad['units'][fn+'Body']['draft']=re.sub(r'import\s+'+re.escape(c.leaf)+r'\s+[^;]*;','',bad['units'][fn+'Body']['draft']);cases.append(bad)
 bad=copy.deepcopy(good);bad['units'][c.leaf]['draft']=bad['units'][c.leaf]['draft'].replace('(long amount)','(ref long amount)');cases.append(bad)
 for bad in cases:
  assert key not in preview(bad)['functionInputUses'];n.prepare(bad,False)
 assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items())
 f.checked('wrapper·재귀·다른 namespace·서명 불일치·import 누락·ref 계약은 조회/위조 선택 모두 거절하고 원문 보존')
finally:
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'pureCandidate':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False));f.stop()
