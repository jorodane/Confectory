"""Read-only positional projection, malformed metadata and compiler stamp invariance."""
import json,copy,pathlib,subprocess,ast
import v666_call_pin_labels_fixture as t
x=t.x;f=t.f
helper=pathlib.Path(__file__).with_name('v666_standalone_labels_native.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='request'],type_ignores=[]),str(helper),'exec'))
def query(text=t.function,signature=t.sig,id=t.callee,ok=True):return request('functionPinPresentation',ok,id=id,text=text,signature=signature)
try:
 result=query();assert result['status']=='available'and result['argumentNames']=={t.parameter:t.input_label}and result['returnName']==t.return_label and result['signature']==t.sig and result['sourceWritten']is False and result['executed']is False;x.original();f.checked('already observed callee amount maps by existing position to caller supplied; native signature/IDs, C# and files remain unchanged')
 for bad in [dict(args=t.sig['args'],**{'return':'void'}),dict(args=[dict(name='supplied',type='long')],**{'return':'int'}),dict(args=[dict(name='supplied',type='int',mode='out')],**{'return':'int'})]:
  value=query(signature=bad);assert value['status']=='signature-mismatch'and 'argumentNames'not in value and 'returnName'not in value
 query(id='Other.Owner::Missing',ok=False)
 for raw in ['null','[]','5','{"missing":"보존"}','{"amount":"bad\\nlabel"}']:
  text=t.base.function.rstrip()[:-1]+'value editorArgumentNames='+json.dumps(raw)+';}';value=query(text=text);assert value['status']=='invalid-labels'and 'argumentNames'not in value
 plain=query(text=t.base.function);assert plain['status']=='available'and plain['argumentNames']=={}and plain['returnName']=='결과';x.original();f.checked('wrong identity rejects; different return/type/role or malformed labels never acquire a guessed alias, and unlabeled legacy declarations remain native')
 labels={'amount':'입력 😀','count':'출력 β'};source='function '+t.callee+' (int amount,out long count) -> bool {value editorArgumentNames='+json.dumps(json.dumps(labels,ensure_ascii=False),ensure_ascii=False)+';value editorReturnName="판정";}'
 for name in ['constructor','toString','__proto__']:
  sig=dict(args=[dict(name=name,type='int'),dict(name='collected',type='long',mode='out')],**{'return':'bool'});value=query(text=source,signature=sig);assert value['argumentNames']=={name:labels['amount'],'collected':labels['count']}and value['returnName']=='판정'and value['signature']==sig
 collision='function '+t.callee+' (int a,int b) -> void {value editorArgumentNames='+json.dumps(json.dumps({'a':'second'}))+';}'
 value=query(text=collision,signature=dict(args=[dict(name='first',type='int'),dict(name='second',type='int')],**{'return':'void'}));assert value['status']=='ambiguous-labels'and 'argumentNames'not in value
 plain=f.metadata('featureBlueprintNodes',featureSource=t.main_text,graph=t.g,featureContracts={t.callee:t.base.function});named=f.metadata('featureBlueprintNodes',featureSource=t.main_text,graph=t.g,featureContracts={t.callee:t.function});assert plain['nodes'][0]['definitionHash']==named['nodes'][0]['definitionHash']and plain['nodes'][0]['definition']==named['nodes'][0]['definition']and plain['nodes'][0]['outputs']==named['nodes'][0]['outputs'];x.original();f.checked('input/out/return labels and JS prototype-shaped native names preserve positional roles; label metadata never enters compiler node definitions, outputs or hashes')
finally:(f.case/'call-labels-native-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
