"""Original extra nodes/aliases remain while explicit native/public mappings change."""
import copy,json
import v536_information_retained_fixture as x
r=x.request();p=x.n.prepare(r);rows={v['id']:v['text'] for v in p['linkedUpdates']};g=json.loads(rows[x.fn+'Body/body:common']);assert g['edges']==x.g['edges'] and g['locals'][1]==x.g['locals'][1] and g['locals'][0]['source']=={'input':'increment'}
assert next(v for v in g['nodes'] if v['id']=='extra')==x.extra
assert json.loads(rows[x.fn+'Body/body:common/node:extra'])['source']==x.extra_record['source']
if x.post_mode:
 post=json.loads(rows[x.caller+'Body/body:common'])['nodes'][0]['postCall'];assert post['source']==x.post_source and post['helpers']==x.post_helpers
 bad=copy.deepcopy(r);bad['changes'][0]['mapping']['bodies'].pop(x.post_id);x.n.prepare(bad,False)
 bad=copy.deepcopy(r);bad['changes'][0]['mapping']['bodies'][x.post_id]['text']='return missing;';x.n.prepare(bad,False)
 bad=copy.deepcopy(r);key=x.caller+'Body/body:common';graph=json.loads(bad['units'][key]['draft']);graph['copySource']={'unreviewed':True};bad['units'][key]['draft']=json.dumps(graph);bad['changes'][0]['mapping']['bodies'][x.post_id]['wrapper']['hash']=__import__('hashlib').sha256(bad['units'][key]['draft'].encode()).hexdigest();x.n.prepare(bad,False)
print('PASS 추가 코드·ref 별칭·정확한 지역값·경로·원문을 보존한 명시 계약 후보',flush=True)
for fault in ['alias','outputs','receipt','source','public-output']:
 bad=copy.deepcopy(r);m=bad['changes'][0]['mapping']
 if fault=='alias':m['implementations']={}
 elif fault=='outputs':m['bodies'][x.body_id]['outputs']['nativeTotal']=None
 elif fault=='receipt':m['bodies'][x.body_id]['whole']['hash']='0'*64
 elif fault=='source':m['bodies'][x.body_id]['text']='nativeTotal=0;return unknown;'
 else:m['outputs']={}
 # Missing out mapping is valid only when no extra node actually consumes it.
 if fault=='outputs':
  m['bodies'][x.body_id]['outputs']['return']='return'
 x.n.prepare(bad,False)
 assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
print('PASS 별칭·현재 출력·원래 graph·원문/컴파일 오류는 전체 미적용',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'storage':x.storage,'postMode':x.post_mode,'executed':False},ensure_ascii=False))
