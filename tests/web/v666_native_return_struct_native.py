"""Original snapshot and order-independent explicit nominal shared caller."""
import copy,json,sys,hashlib
import v666_native_return_struct_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});x.execute(70,'original-nominal-shared');r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));out=x.prepare(r,'reproduce'not in sys.argv);(f.case/'candidate.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 if'reproduce'not in sys.argv:
  rows=out['result']['updates']+out['result']['linkedUpdates'];values={r['id']:r['text']for r in rows};assert len(values)==len(rows);expected=set(x.functions)|set(x.paths)|{x.c.impl,x.second+'Body',x.consumer_body};assert expected<=set(values)<=expected|{x.owner};assert all(values[id]==plan['text']for row in r['changes']for id,plan in row['mapping']['bodies'].items());assert all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in rows)
  reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert values=={row['id']:row['text']for row in other['updates']+other['linkedUpdates']};f.checked('both nominal plans authenticate the selected A body exactly once; reversed edit order retains identical source and original hashes')
 x.unchanged();f.checked('original selected native import program executes70; explicit candidate outcome retained without writing original data')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
