"""Manual whole-body caller and changed callee are one candidate, no execution."""
import copy,json
import v536_information_context_fixture as x
r=x.request();p=x.n.prepare(r);rows={v['id']:v['text'] for v in p['linkedUpdates']};assert json.loads(rows[x.caller_id])['source']==x.caller_text
assert x.n.canonical(x.f.metadata('inspect',text=rows[x.caller+'Body'])['signature'])==x.caller_signature
fntext=next(v['text'] for v in p['updates'] if v['id']==x.fn)
checked=x.f.metadata('blueprintDescribeOwned',project=str(x.f.manifest),id=x.caller+'Body',text=rows[x.caller+'Body'],bodyTarget='common',graph=json.loads(rows[x.caller+'Body/body:common']),draftContracts={x.fn:fntext},definitionsOnly=True)
assert checked['state']=='node-definitions',checked
print('PASS callee 계약과 caller 수동 본문·import/context를 한 후보에 결합하고 caller own ABI를 유지한다',flush=True)
for fault in ['missing','source','graph','own-signature','contract','compile']:
    bad=copy.deepcopy(r);plans=bad['changes'][0]['mapping']['bodies'];b=plans[x.caller_id]
    if fault=='missing':plans.pop(x.caller_id)
    elif fault=='source':b['hash']='0'*64
    elif fault=='graph':b['whole']['hash']='0'*64
    elif fault=='own-signature':b['signature']=x.new
    elif fault=='contract':b['contract']=x.old
    else:b['text']=x.original_caller
    x.n.prepare(bad,False);assert all((x.f.project/p).read_bytes()==v for p,v in x.snapshot.items())
print('PASS caller 기준·명시 source 누락/형식/컴파일 오류는 전체 미적용이며 원래 ABI·원문을 보존한다',flush=True)
print(json.dumps({'checks':2,'evidence':str(x.f.case),'pureCandidate':True,'projectRun':False},ensure_ascii=False))
