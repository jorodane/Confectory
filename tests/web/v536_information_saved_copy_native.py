"""Saved copy provenance/ownership is required before an editable view exists."""
import copy,json
if 'inherited-copy' in __import__('sys').argv[4:]:
    import v536_information_inherited_contract_fixture as x
else:
    import v536_information_saved_copy_fixture as x
r=x.request();p=x.n.prepare(r);rows={row['id']:row['text'] for row in p['linkedUpdates']}
assert json.loads(rows[x.body_id])['source']==x.edited
graph=json.loads(rows[x.graph_id]);assert graph['copySource']==x.prepared['graph']['copySource']
assert graph['nodes'][0]['arguments']=={'nativeAmount':{'input':'renamed'}}
assert x.donor_id not in rows and x.fn+'Body' not in rows
x.unchanged();print('PASS 소유 copy의 root/수동 본문만 계약 후보로 갱신하고 출처·native donor를 보존한다',flush=True)
for fault in ['missing','owner','provenance','graph','implementation','shared','assignment','unit-provenance','missing-baseline','malformed']:
    bad=copy.deepcopy(r);mapping=bad['changes'][0]['mapping'];proof=mapping['copies'][x.graph_id]
    if fault=='missing':mapping.pop('copies')
    elif fault in ['owner','graph','implementation']:proof[{'owner':'ownerHash','graph':'graphHash','implementation':'implementationHash'}[fault]]='0'*64
    elif fault=='provenance':proof['provenance']['implementation']='Another.Pack::Body'
    elif fault=='shared':
        target=x.f.n+'Slime';bad['units'][target]['draft']=bad['units'][target]['draft'].replace('{','{provide '+x.fn+' with '+x.copy_id+';',1)
    elif fault=='assignment':bad['units'][x.owner]['draft']=bad['units'][x.owner]['draft'].replace('with '+x.copy_id,'with '+x.fn+'Body')
    elif fault=='unit-provenance':bad['units'][x.copy_id]['copySource']={**x.prepared['graph']['copySource'],'implementation':'Another.Pack::Body'}
    elif fault=='missing-baseline':bad['units'][x.graph_id]['baseline']='missing'
    else:
        graph=json.loads(bad['units'][x.graph_id]['draft']);graph['copySource']='unbound';bad['units'][x.graph_id]['draft']=json.dumps(graph);mapping.pop('copies')
    x.n.prepare(bad,False);x.unchanged()
print('PASS 누락·위조·다른 배정/공유·원래 출처 및 저장 기준 변경은 전체 미적용이다',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'pureCandidate':True,'projectRun':False},ensure_ascii=False))
