"""Reproduced own-node ABI boundary and compiler-backed explicit-name guards."""
import copy,json
import v666_private_node_names_fixture as x
f=x.f
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));x.execute(40,'original-private-node-names')
 unchanged=copy.deepcopy(r);plan=next(iter(unchanged['changes'][0]['mapping']['bodies'].values()));plan['signature']=copy.deepcopy(x.code_signature);plan['text']=plan['text'].replace('deltaNative','firstNative');x.prepare(unchanged);x.unchanged();f.checked('published unchanged-ABI private/native group validates; original program executes40')
 if x.mode=='reproduce':
  reply=x.prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('published authority rejects own private-code parameter rename without writing originals')
 else:
  for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];x.prepare(one)
  result=x.prepare(r)['result'];rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=x.prepare(reverse)['result'];assert {v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('single/group explicit own name validates order independently and rekeys only its original positional binding')
  for fault in ['source-hash','flow-hash','wrong-before','type','role','return','count','permutation','duplicate','second-name','public-contract','missing-source','helpers-boundary','last-body']:
   bad=copy.deepcopy(r);a,b=bad['changes'];p=next(iter(a['mapping']['bodies'].values()))
   if fault=='source-hash':p['hash']='0'*64
   elif fault=='flow-hash':p['whole']['hash']='0'*64
   elif fault=='wrong-before':p['beforeSignature']['args'][0]['name']='wrong'
   elif fault=='type':p['signature']['args'][0]['type']='double'
   elif fault=='role':p['signature']['args'][0]['mode']='ref'
   elif fault=='return':p['signature']['return']='double'
   elif fault=='count':p['signature']['args'].pop()
   elif fault=='permutation':p['signature']['args'].reverse()
   elif fault=='duplicate':p['signature']['args'][0]['name']='secondNative'
   elif fault=='second-name':p['signature']['args'][1]['name']='otherNative'
   elif fault=='public-contract':a['signature']['args'][0]['name']='changedPublic'
   elif fault=='missing-source':p['text']=x.sources[x.whole_function]
   elif fault=='helpers-boundary':p['helpers']='} class Escape {'
   elif fault=='last-body':next(iter(b['mapping']['bodies'].values()))['text']='return MissingLastBody;'
   x.prepare(bad,False);x.unchanged();f.checked(fault+' rejects without changing originals')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
