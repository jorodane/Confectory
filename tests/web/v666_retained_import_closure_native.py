"""Reproduce the real grouped dependency boundary using valid single plans."""
import copy,json
import v666_retained_import_closure_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(x.original_result,'original-retained-import-closure')
 for row in r['changes']:
  one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
 x.unchanged();f.checked('original program76 and both independent explicit callee/opaque source and peer source plans are valid')
 if x.mode=='reproduce':
  reply=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects their one information-window candidate without source or checkpoint writes')
 else:
  candidate=x.prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2));rows=candidate['updates']+candidate['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent explicit source closure retains original evidence and untouched context/frame contracts')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
