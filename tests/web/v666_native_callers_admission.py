"""A retained native caller stays owned, exact and outside the explicit write plan."""
import copy,json
import v666_native_callers_fixture as x
f=x.f;r=x.request()
try:
 for fault in ['missing-caller-body','stale-caller-import','parent-caller','foreign-caller','caller-edit-plan']:
  bad=copy.deepcopy(r);header=bad['units'][x.retained+'Body'];body=bad['changes'][1]['mapping']['bodies']
  if fault=='missing-caller-body':bad['units'].pop(x.retained+'Body/body:common')
  elif fault=='stale-caller-import':header['draft']=header['draft'].replace('as First (long,long)','as First (string,long)')
  elif fault=='parent-caller':header['draft']=header['draft'].replace(' for ', ' : External.Parent::NativeCaller for ',1)
  elif fault=='foreign-caller':header['draft']=header['draft'].replace('implementation '+x.retained+'Body','implementation External.Foreign::NativeCallerBody',1)
  elif fault=='caller-edit-plan':
   body[x.retained+'Body/body:common']=dict(next(iter(body.values())),path=x.retained_file,text='return 0;')
  (f.case/('fault-'+fault+'.json')).write_text(json.dumps(bad,ensure_ascii=False));x.n.prepare(bad,False);x.unchanged();f.checked(fault+' refuses the whole group without rewriting native caller source or discarding authored input')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
