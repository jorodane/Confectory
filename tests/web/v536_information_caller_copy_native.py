import copy,json
import v536_information_caller_copy_fixture as x
r=x.request();p=x.n.prepare(r);rows={row['id']:row['text'] for row in p['linkedUpdates']}
assert json.loads(rows[x.body_id])['source']==x.edited
assert json.loads(rows[x.graph_id])['copySource']==x.prepared['graph']['copySource']
assert x.donor_impl not in rows and x.donor_id not in rows
x.unchanged();print('PASS 다른 소유 객체의 caller copy는 callee와 같은 후보로 갱신하며 native donor/배정을 보존한다',flush=True)
for fault in ['proof','source','owner']:
    bad=copy.deepcopy(r)
    if fault=='proof':bad['changes'][0]['mapping']['copies']={}
    elif fault=='source':bad['changes'][0]['mapping']['bodies'][x.body_id]['text']='return unknown;'
    else:bad['units'][x.copy_owner]['draft']=bad['units'][x.copy_owner]['draft'].replace('with '+x.copy_id,'with '+x.donor_impl)
    x.n.prepare(bad,False);x.unchanged()
print('PASS caller copy의 소유·원래 코드·receipt 오류는 callee와 caller 모두 미적용이다',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'pureCandidate':True,'projectRun':False},ensure_ascii=False))
