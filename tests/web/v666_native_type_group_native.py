"""Original-source native nominal group baseline and candidate proof."""
import copy,json,sys
import v666_native_type_group_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});x.execute(70,'original-type-group');r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));result=x.prepare(r,'reproduce'not in sys.argv)
 if 'reproduce'not in sys.argv:
  rows=result['result']['updates']+result['result']['linkedUpdates'];updates={row['id']:row['text']for row in rows};expected=set(x.functions)|set(x.paths)|{x.c.impl,x.second+'Body',f.n+'MainBody',x.consumer_body};assert expected<=set(updates);assert set(updates)<=expected|{x.owner};assert all(updates[id]==plan['text']for row in r['changes']for id,plan in row['mapping']['bodies'].items());reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert updates=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('reverse declaration order yields the same exact authored native nominal candidate and original hash/source closure')
 (f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('original native functions and disjoint C# callers execute70; nominal transition result captured without changing source')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
