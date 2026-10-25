"""A private identity ancestor chain changes only after explicit parent mapping."""
import copy,json
import v536_information_forwarded_fixture as x
r=x.request();p=x.n.prepare(r);rows={v['id']:v['text'] for v in p['linkedUpdates']};g=json.loads(rows[x.caller_id]);assert g['nodes'][2]==x.root['nodes'][2] and g['locals']==x.root['locals'];assert g['nodes'][0]['signature']==x.new and g['nodes'][1]['graph']['nodes'][0]['signature']==x.new
print('PASS 명시 부모 계약과 depth2 forwarded chain·caller·본문을 한 후보에 결합한다',flush=True)
for fault in ['missing','path','hash','output','type','source']:
 bad=copy.deepcopy(r);m=bad['changes'][0]['mapping'];key=next(iter(m['callers']))
 if fault=='missing':m['callers'].pop(key)
 elif fault=='path':m['callers'][key]['node']='right/deep'
 elif fault=='hash':m['callers'][key]['hash']='0'*64
 elif fault=='output':m['callers'][key]['outputs']['return']=None
 elif fault=='type':m['callers'][key]['inputs']['increment']={'valueJson':'true'}
 else:m['bodies'][x.body_id]['text']='return missing;'
 x.n.prepare(bad,False);assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
print('PASS 누락·경계·stale·사용 중 출력·타입·C# 오류는 chain 전체 미적용과 원문 보존이다',flush=True)
if x.computed:
 for fault in ['missing-child','used-child','lost-input']:
  bad=copy.deepcopy(r);plans=bad['changes'][0]['mapping']['callers'];key=x.caller_id+'#left/'+x.leaf_id
  if fault=='missing-child':plans.pop(key)
  elif fault=='used-child':plans[key]['outputs']['return']=None
  elif fault=='lost-input':
   p=plans[x.caller_id+'#left'];p['inputs']['increment']={'valueJson':'5'};p['disconnect']={'value':json.dumps(x.root['nodes'][0]['arguments']['value'],separators=(',',':'))}
  x.n.prepare(bad,False);assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
 print('PASS 계산·별칭의 실제 입력/child출력과 부모출력은 각각 명시 대응하며 누락·유실을 전체 거절한다',flush=True)
 # Unchanged contracts keep ordinary private body edits available. No caller
 # mapping is invented for a C#-only edit of the original public function.
 stable=x.n.request(x.old,{a['name']:a['name'] for a in x.old['args']});preview=x.f.metadata('informationFunctionBodies',id=x.owner,function=x.fn,includeBlueprintTargets=True,units=stable['units'],functionSignature=x.old,functionRemap={a['name']:a['name'] for a in x.old['args']});body=preview[x.body_id];native=body['signature'];stable['changes'][0]['mapping']={'before':x.old,'args':{a['name']:a['name'] for a in x.old['args']},'bodies':{x.body_id:{k:body[k] for k in ['hash','path','whole']}|{'beforeSignature':native,'signature':native,'contract':x.old,'text':body['text']+'\n// 기존 계약의 본문만 편집'}}};p=x.n.prepare(stable);rows={v['id']:v['text'] for v in p['linkedUpdates']};assert json.loads(rows[x.caller_id])==x.root
 print('PASS 부모 계산이 있는 기존 고정 계약의 본문만 편집할 때 불필요한 부모 계약 갱신을 요구하지 않는다',flush=True)

print(json.dumps({'checks':4 if x.computed else 2,'evidence':str(x.f.case),'executed':False},ensure_ascii=False))
