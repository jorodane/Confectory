"""One callee candidate with two explicit copies at distinct targets/owners."""
import copy,json
import v536_information_copy_targets_fixture as x
r=x.request();before=copy.deepcopy(r);p=x.n.prepare(r);rows={v['id']:v['text'] for v in p['linkedUpdates']}
assert r==before
for body,text in x.expected_text.items():assert json.loads(rows[body])['source']==text
for graph,prepared in zip(x.graphs,[x.first.prepared,x.second]):assert json.loads(rows.get(graph,r['units'][graph]['draft']))['copySource']==prepared['graph']['copySource']
assert x.first.donor_impl not in rows and x.first.donor_id not in rows and x.donor_windows not in rows
x.unchanged();print('PASS common/windows의 서로 다른 명시 copy와 한 callee를 한 후보로 검증하며 두 배정·원본·정확한 원문을 보존한다',flush=True)
for fault in ['last-source','missing-copy','last-proof','last-owner']:
 bad=copy.deepcopy(r);mapping=bad['changes'][0]['mapping']
 if fault=='last-source':mapping['bodies'][x.second_body]['text']='return unknown;'
 elif fault=='missing-copy':del mapping['copies'][x.second_graph]
 elif fault=='last-proof':mapping['copies'][x.second_graph]['target']='common'
 else:bad['units'][x.second_owner]['draft']=bad['units'][x.second_owner]['draft'].replace(x.second_copy,x.first.donor_impl)
 x.n.prepare(bad,False);x.unchanged()
print('PASS 마지막 copy 본문/target/소유 증거 오류는 앞선 copy·callee 모두 미적용이며 원래 요청을 변경하지 않는다',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'pureCandidate':True,'projectRun':False},ensure_ascii=False))
