"""One original Save combines owner presentation with explicit native contracts."""
import copy,hashlib,json,os,pathlib,runpy,sys
import v666_native_header_contracts_fixture as x
f=x.f;check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
if check=='native':
 try:
  x.execute(x.original_result,'original-return-runtime');r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));contracts=[row for row in r['changes']if row['type']=='function-edit'];presentation=[row for row in r['changes']if row['type']!='function-edit']
  for rows in [[row]for row in contracts]+[contracts,presentation]:
   one=copy.deepcopy(r);one['changes']=copy.deepcopy(rows);x.n.prepare(one)
  x.unchanged();f.checked('original runtime'+str(x.original_result)+', both explicit native singles, their body/ABI-only group and owner description/icon are independently valid')
  if x.mode=='reproduce':x.n.prepare(r,False);x.unchanged();f.checked('published candidate rejects only the combined owner presentation and two valid native ABI/body changes')
  else:
   p=x.n.prepare(r);updates=p['updates']+p['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in updates}|{x.owner:{'draft':p['text']}});assert len({row['id']for row in updates})==len(updates)and all(row['hash']==hashlib.sha256(r['units'][row['id']]['draft'].encode()).hexdigest()for row in updates)
   one=copy.deepcopy(r);one['changes']=copy.deepcopy(contracts);body_only=x.n.prepare(one);assert{v['id']:v['text']for v in updates}=={v['id']:v['text']for v in body_only['updates']+body_only['linkedUpdates']}
   reverse=copy.deepcopy(r);reverse['changes'].reverse();q=x.n.prepare(reverse);assert p['text']==q['text']and{row['id']:row['text']for row in updates}=={row['id']:row['text']for row in q['updates']+q['linkedUpdates']};x.unchanged();f.checked('one order-independent original-hash candidate joins both native ABI/body/caller changes with description/icon; no new source closure or conversion')
   for fault in ['duplicate-description','duplicate-icon','extra-description-key','oversized-description','invalid-icon','structural-change','foreign-function','missing-body','missing-caller','wrong-output','stale-body','unknown-row','extra-description']:
    bad=copy.deepcopy(r);row=bad['changes'][0]
    if fault=='duplicate-description':bad['changes'].append(dict(type='description',text='duplicate'))
    elif fault=='duplicate-icon':bad['changes'].append(dict(type='icon',text='▢'))
    elif fault=='extra-description-key':bad['changes'][1]['grant']=True
    elif fault=='oversized-description':bad['changes'][1]['text']='x'*16385
    elif fault=='invalid-icon':bad['changes'][-1]['text']='not one glyph'
    elif fault=='structural-change':bad['changes'].append(dict(type='property-add',name='inferred',kind='long'))
    elif fault=='foreign-function':row['id']='Other.Pack::Unowned'
    elif fault=='missing-body':row['mapping']['bodies'].clear()
    elif fault=='missing-caller':row['mapping']['callers'].clear()
    elif fault=='wrong-output':next(iter(row['mapping']['callers'].values()))['outputs']={'return':'missing'}
    elif fault=='stale-body':next(iter(row['mapping']['bodies'].values()))['hash']='0'*64
    elif fault=='unknown-row':bad['changes'].append(dict(type='grant',text='inferred'))
    else:bad['changes'][1]['path']='../outside'
    x.n.prepare(bad,False);x.unchanged()
   f.checked('duplicate/malformed/oversized presentation, invalid icon, structural/unknown rows and incomplete/stale/foreign contract plans reject the entire candidate without losing source/input')
 finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
elif check in ['api','guards','late','conflict','ui']:
 runpy.run_path(str(pathlib.Path(__file__).with_name('v666_native_header_contracts_'+check+'.py')),run_name='__main__')
else:raise ValueError(check)
