"""An explicit selected callee receives only already-existing caller ref storage."""
import copy,json,pathlib,subprocess,sys
import v666_private_callee_value_ref_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(115,'original-private-value-ref')
 if x.mode=='constant-original':
  assert json.loads(x.snapshot[x.retained_graph])['nodes'][1]['arguments']['count']=={'constant':5}
  x.prepare(r,False);x.unchanged();f.checked('original value program executes115/ref5 with a literal5 binding; new ref refuses that non-storage original without inventing a cell')
 else:
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
  x.unchanged();f.checked('original115/ref5 executes; private and value-ref native single plans validate independently')
  if x.mode=='reproduce':
   result=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));x.unchanged();f.checked('published package rejects combined private/callee value-ref without original writes')
  else:
   result=x.prepare(r)['result'];rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('order-independent value-ref candidate retains both original ref storage bindings and explicit private sources')
   for fault in ['missing-callers','missing-private-caller','missing-shared-caller','missing-ref-input','literal-ref-input','wrong-ref-input','extra-disconnect','drop-return','extra-output','native-alias','private-role','bad-code','second-role','return-type']:
    bad=copy.deepcopy(r);a,b=bad['changes'];plan=next(iter(b['mapping']['bodies'].values()));caller=next(iter(b['mapping']['callers'].values()))
    if fault=='missing-callers':b['mapping'].pop('callers')
    elif fault in ['missing-private-caller','missing-shared-caller']:
     plans=b['mapping']['callers'];keys=[key for key,value in plans.items()if(value['graph']==x.whole_graph)==(fault=='missing-private-caller')];assert len(keys)==1;plans.pop(keys[0])
    elif fault=='missing-ref-input':caller['inputs'].pop('count')
    elif fault=='literal-ref-input':caller['inputs']['count']={'valueJson':'5'}
    elif fault=='wrong-ref-input':caller['inputs']['count']='amount'
    elif fault=='extra-disconnect':caller['disconnect']['count']='input:count'
    elif fault=='drop-return':caller['outputs']['return']=None
    elif fault=='extra-output':caller['outputs']['count']='return'
    elif fault=='native-alias':plan['signature']['args'][1]['name']='inferredCount'
    elif fault=='private-role':next(iter(a['mapping']['bodies'].values()))['signature']['args'][1]['mode']='ref'
    elif fault=='bad-code':plan['text']='return MissingRoleValue;'
    elif fault=='second-role':b['signature']['args'][0]['mode']='ref';plan['signature']['args'][0]['mode']='ref';plan['contract']=copy.deepcopy(b['signature'])
    elif fault=='return-type':b['signature']['return']='double';plan['signature']['return']='double';plan['contract']=copy.deepcopy(b['signature'])
    x.prepare(bad,False);x.unchanged();f.checked(fault+' refuses missing/changed original storage, caller or ABI evidence without original writes')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
if x.mode=='normal':
 subprocess.run([sys.executable,str(pathlib.Path(__file__).resolve()),*sys.argv[1:3],'constant-original'],check=True)
