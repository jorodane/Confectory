"""Fixed return identity, existing optional metadata and exact owned transaction."""
import copy,json,sys
import v666_root_input_name_recovery_fixture as t
x=t.x;f=t.f
# Reuse only the native JSON invocation helper, with this fixture's paths/env.
import ast,pathlib
helper=pathlib.Path(__file__).with_name('v666_standalone_labels_native.py')
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='request'],type_ignores=[]),str(helper),'exec'))
import subprocess
base=dict(project=str(f.project/'project.cproj'),manifest=(f.project/'project.cproj').read_text(),id=t.feature,text=t.function,drafts=[])
label='計算 결과 😀';change={'type':'function-return-name','text':label}
try:
 if sys.argv[3]=='baseline':
  request('functionPresentation',False,**base,changes=[change]);x.original();f.checked('published candidate refuses standalone fixed return label cell without draft/source writes')
 else:
  cells=[change,{'type':'function-argument-names','text':'{"amount":"수량"}'},{'type':'description','text':'동일 함수 표시'},{'type':'icon','text':'◇'}]
  result=request('functionPresentation',**base,changes=cells);parsed=request('inspect',text=result['text']);assert parsed['values']['editorReturnName']==label and json.loads(parsed['values']['editorArgumentNames'])=={'amount':'수량'};assert parsed['description']=='동일 함수 표시';assert parsed['signature']==request('inspect',text=t.function)['signature'];assert result['sourceWritten']is False and result['compiled']is False and not result['updates']and not result['additions']and result['manifest']==base['manifest'];x.original();f.checked('four exact cells atomically prepare return/argument labels, description and icon without changing signature, registration or C#')
  for bad in ['', ' '*4, 'x'*61,'line\nname']:
   request('functionPresentation',False,**base,changes=[{**change,'text':bad}])
  for bad in [[{**change,'extra':True}],[change,copy.deepcopy(change)],[change,{'type':'signature','text':'bad'}],cells+[change],[{**change,'text':None}]]:request('functionPresentation',False,**base,changes=bad)
  request('functionPresentation',False,**{**base,'id':'Other.Owner::Pair'},changes=[change]);request('functionPresentation',False,**{**base,'text':t.function.replace('function '+t.feature,'object '+t.feature,1)},changes=[change]);x.original();f.checked('invalid, duplicate, extra, over-budget, cross-kind and non-owned return edits refuse before shared draft mutation')
  reset=request('functionPresentation',**{**base,'text':result['text']},changes=[{**change,'text':' 결과 '}]);reset_values=request('inspect',text=reset['text'])['values'];assert 'editorReturnName'not in reset_values and json.loads(reset_values['editorArgumentNames'])=={'amount':'수량'}
  sig={'args':[{'name':'amount','type':'int'}],'return':'void'};hidden=request('functionSignature',text=result['text'],signature=sig);assert request('inspect',text=hidden)['values']['editorReturnName']==label;sig['return']='int';shown=request('functionSignature',text=hidden,signature=sig);assert request('inspect',text=shown)['values']['editorReturnName']==label
  for raw in ['5',json.dumps('invalid\nlabel')]:
   bad=t.function.rstrip()[:-1]+'value editorReturnName = '+raw+';}';fixed=request('functionPresentation',**{**base,'text':bad},changes=[change]);assert request('inspect',text=fixed['text'])['values']['editorReturnName']==label
  x.original();f.checked('existing trimmed default-reset, explicit malformed metadata replacement and void retention policy preserve unrelated argument labels; no inferred IDs or C# rewrites')
finally:(f.case/'standalone-return-native-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
