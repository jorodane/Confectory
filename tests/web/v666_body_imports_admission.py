"""Local exact imported-contract admission, with no opaque/source rewriting."""
import copy,json,subprocess
import v666_body_imports_fixture as x
f=x.f;r=x.request()
for fault in ['stale-public','pin-map','native-contract','body-contract','missing-dependency','wrong-import','external-import','wrong-dependency-kind']:
 bad=copy.deepcopy(r);row=bad['changes'][1];m=row['mapping'];body=next(iter(m['bodies'].values()));impl=row['id']+'Body'
 if fault=='stale-public':m['before']['args'][0]['type']='string'
 elif fault=='pin-map':m['args']['amount']='count'
 elif fault=='native-contract':body['signature']['args'][0]['type']='string'
 elif fault=='body-contract':body['contract']['return']='void'
 elif fault=='missing-dependency':bad['units'].pop(x.helper)
 elif fault=='wrong-import':bad['units'][impl]['draft']=bad['units'][impl]['draft'].replace('StableHelper (long)','StableHelper (string)')
 elif fault=='external-import':
  external='External.Foreign::StableBodyHelper';bad['units'][impl]['draft']=bad['units'][impl]['draft'].replace(x.helper,external);bad['units'][external]=dict(kind='function',draft='function '+external+' (long value) -> long {}')
 elif fault=='wrong-dependency-kind':bad['units'][x.helper]['draft']='object '+x.helper+' {}'
 (f.case/'fault-current.json').write_text(json.dumps(dict(fault=fault,request=bad),ensure_ascii=False));x.n.prepare(bad,False);x.unchanged();f.checked(fault+' rejected for the whole candidate; both authored inputs and every original file retained')
print('BODY_IMPORTS_ADMISSION',f.case,flush=True)
