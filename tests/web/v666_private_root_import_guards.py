"""Existing context guards and every stable helper read path."""
import pathlib,runpy,sys,copy,json
import v666_private_root_import_fixture as x
sys.modules['v666_private_scalar_return_fixture']=x
saved=runpy.run_path(str(pathlib.Path(__file__).with_name('v666_private_scalar_return_guards.py')),run_name='__main__')
f=x.f;request=json.loads((f.case/'captured-guard-request.json').read_text())
for path in [x.impl_path,*x.helper_paths]:
 bad=copy.deepcopy(request['units']);bad[x.owner]['slotSaveReceipt']['readGuards'].pop(path);saved['validate'](bad,False);x.unchanged();f.checked('dropping original helper read '+path+' rejects the complete mixed source group')
(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
