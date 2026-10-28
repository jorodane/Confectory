"""Two equal leaf IDs in different private frames remain disjoint."""
import copy,json
import v536_information_nested_fixture as x
r=x.request();p=x.n.prepare(r);rows={v['id']:v['text'] for v in p['linkedUpdates']};g=json.loads(rows[x.caller_id]);assert g['nodes'][2]==x.root['nodes'][2] and g['exits']==x.root['exits']
assert g['nodes'][0]['graph']['nodes'][0]['arguments']['text']=={'constant':'왼쪽'}
assert g['nodes'][1]['graph']['nodes'][0]['graph']['nodes'][0]['arguments']['text']=={'constant':'오른쪽'}
if x.cpp:
 bad=copy.deepcopy(r);bad['changes'][0]['mapping']['bodies'].pop(x.record_ids['left']);x.n.prepare(bad,False)
 bad=copy.deepcopy(r);bad['changes'][0]['mapping']['bodies'][x.record_ids['left']]['whole']['node']='right/deep/body';x.n.prepare(bad,False)
if x.post_mode:
 bad=copy.deepcopy(r);bad['changes'][0]['mapping']['bodies'].pop(x.caller_id+'/postCall:left/'+x.leaf_id);x.n.prepare(bad,False)
print('PASS qualified private 호출·depth2·동명 leaf를 고유 frame에서 대응하고 부모/형제/원문을 보존한다',flush=True)
for fault in ['missing','flat','wrong-path','graph','source']:
 bad=copy.deepcopy(r);m=bad['changes'][0]['mapping'];key=next(iter(m['callers']));row=m['callers'][key]
 if fault=='missing':m['callers'].pop(key)
 elif fault=='flat':row['node']=x.leaf_id
 elif fault=='wrong-path':row['node']='right/'+x.leaf_id
 elif fault=='graph':row['hash']='0'*64
 else:
  id=x.record_ids['left'];record=json.loads(bad['units'][id]['draft']);record['definitionHash']='0'*64;bad['units'][id]['draft']=json.dumps(record)
 x.n.prepare(bad,False);assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
print('PASS 누락·경계/동명 혼동·stale graph/source 증거는 전체 미적용이며 입력을 유지한다',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'executed':False,'cpp':x.cpp,'postMode':x.post_mode,'callee':x.callee},ensure_ascii=False))
