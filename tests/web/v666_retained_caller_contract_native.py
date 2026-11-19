"""Valid original and independent plans precede the coupled-contract test."""
import copy,json
import v666_retained_caller_contract_fixture as x
f=x.f
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(x.original_result,'original-retained-caller-contract')
 for row in r['changes']:
  one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original42 and both independent caller-input/native-callee-input plans are valid and preserve source')
 if x.mode=='reproduce':
  v=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(v,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects the same owner coupled retained caller/callee candidate without writes')
 else:
  candidate=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2));rows=candidate['updates']+candidate['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('original-basis contracts compose order-independently with the unchanged retained CSharp and graph context')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
