"""Exact current owner presentation candidate and legacy signature preservation."""
import copy,json,pathlib,subprocess,sys
import v666_root_input_name_recovery_fixture as t
x=t.x;f=t.f
def request(operation,success=True,**values):
 payload={'operation':operation,**values};result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(payload,ensure_ascii=False),text=True,capture_output=True,env=f.env,check=True);reply=json.loads(result.stdout);assert reply['ok'] is success,(payload,reply);return reply.get('result')
base=dict(project=str(f.project/'project.cproj'),manifest=(f.project/'project.cproj').read_text(),id=t.feature,text=t.function,drafts=[])
labels={'amount':'計算 수량 😀'};change={'type':'function-argument-names','text':json.dumps(labels,ensure_ascii=False,separators=(',',':'))}
try:
 prepared=request('functionPresentation',**base,changes=[change,{'type':'description','text':'원자 표시 설명'},{'type':'icon','text':'◇'}]);assert prepared['sourceWritten']is False and prepared['compiled']is False and prepared['manifest']==base['manifest']and not prepared['additions']and not prepared['updates']
 parsed=request('inspect',text=prepared['text']);assert json.loads(parsed['values']['editorArgumentNames'])==labels;assert parsed['description']=='원자 표시 설명';assert [(a['Name'],a['Type'],a.get('Mode'))for a in parsed['signature']['Args']]==[('amount','int',None)];x.original();f.checked('one current owned function candidate accepts label/description/icon with exact signature and no source, registration or implementation writes')
 for value in [None,[],5,{'unknown':'이름'},{'amount':''},{'amount':' 끝 '},{'amount':'x'*61},{'amount':'line\nname'},{'amount':5}]:
  request('functionPresentation',False,**base,changes=[{'type':'function-argument-names','text':json.dumps(value,ensure_ascii=False)}])
 for bad in [[{**change,'extra':True}],[change,copy.deepcopy(change)],[change,{'type':'signature','text':'bad'}],[change]*4]:request('functionPresentation',False,**base,changes=bad)
 bad_source=t.function[:-1]+'value editorArgumentNames = '+json.dumps(json.dumps({'unknown':'읽히지 않는 기존 이름'},ensure_ascii=False),ensure_ascii=False)+';}';request('functionPresentation',False,**{**base,'text':bad_source},changes=[{'type':'function-argument-names','text':'{}'}]);
 request('functionPresentation',False,**{**base,'id':'Other.Owner::Pair'},changes=[change]);request('functionPresentation',False,**{**base,'text':t.function.replace('function '+t.feature,'object '+t.feature,1)},changes=[change]);x.original();f.checked('null/array/number, unknown parameters, invalid labels, extra/duplicate/cross-kind edits and non-owned identity are refused before shared drafts')
 same={'args':[{'name':'amount','type':'int'}],'return':'int'};renamed={'args':[{'name':'units','type':'int'}],'return':'int'}
 old=request('functionSignature',text=t.function,signature=renamed);assert request('inspect',text=old)['signature']['Args'][0]['Name']=='units'
 request('functionSignature',False,text=prepared['text'],signature=renamed)
 kept=request('functionSignature',text=prepared['text'],signature=same);assert json.loads(request('inspect',text=kept)['values']['editorArgumentNames'])==labels
 for name in ['constructor','toString','__proto__']:
  signature={'args':[{'name':name,'type':'int'}],'return':'int'};header=request('functionSignature',text=t.function,signature=signature);named=request('functionPresentation',**{**base,'text':header},changes=[{'type':'function-argument-names','text':json.dumps({name:'표시 이름'},ensure_ascii=False)}]);assert json.loads(request('inspect',text=named['text'])['values']['editorArgumentNames'])=={name:'표시 이름'}
 reset=request('functionPresentation',**{**base,'text':prepared['text']},changes=[{'type':'function-argument-names','text':'{}'}]);assert 'editorArgumentNames'not in request('inspect',text=reset['text'])['values'];request('functionSignature',text=reset['text'],signature=renamed);x.original();f.checked('legacy no-label edits and unchanged label-bearing contracts remain compatible; orphaning is refused, explicit metadata reset removes only labels')
finally:(f.case/'standalone-native-checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
