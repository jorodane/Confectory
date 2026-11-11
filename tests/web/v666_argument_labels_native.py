"""Real native candidate checks for named presentation without changing ABI."""
import copy,hashlib,json,subprocess
import v666_argument_labels_fixture as x
f=x.f;r=x.request()
def prepare(request,ok=True,host=None):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],host or str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 if x.mode=='reproduce':
  baseline=copy.deepcopy(r)
  for row in baseline['changes']:row.pop('argumentNames')
  prepare(baseline);prepare(r,False);x.execute(x.original_result,'original-argument-labels');x.unchanged();f.checked('published host rejects argument presentation metadata while original signatures and actual execution46 remain valid')
 else:
  result=prepare(r)['result'];assert not result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in result['updates']});x.unchanged();f.checked('input labels are metadata only, keep source contracts/callers and native original execution')
  reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert {v['id']:v['text']for v in other['updates']}=={v['id']:v['text']for v in result['updates']};f.checked('two presentation edits form one order-independent candidate')
  for invalid in [None,[],42,{'amount':''},{'amount':'x'*61},{'amount':'bad\nlabel'},{'amount':' bad'},{'amount':42},{'missing':'표시'},{'amount':'count'},{'amount':'같음','count':'같음'}]:
   bad=copy.deepcopy(r);bad['changes'][0]['argumentNames']=invalid;prepare(bad,False);x.unchanged();f.checked('invalid/unknown/ambiguous label map rejects atomically: '+repr(invalid))
  follow=copy.deepcopy(r)
  for row in follow['changes']:
   text=next(v['text']for v in result['updates']if v['id']==row['id']);follow['units'][row['id']]['draft']=text;next(v for v in follow['drafts']if v['id']==row['id'])['text']=text;row.update(hash=hashlib.sha256(text.encode()).hexdigest(),description='후속 설명');row.pop('argumentNames')
  saved=prepare(follow)['result'];x.verify_rows({v['id']:{'draft':v['text']}for v in saved['updates']});x.unchanged();f.checked('legacy request omitting argumentNames keeps the existing aliases during a description edit')
  renamed=copy.deepcopy(follow);renamed['changes']=renamed['changes'][:1];renamed['changes'][0]['signature']['args'][0]['name']='renamedAmount';renamed['changes'][0]['mapping']['args']['amount']='renamedAmount';prepare(renamed,False);x.unchanged();f.checked('display metadata does not bypass original explicit native body/caller review for a real parameter rename')
  reset=copy.deepcopy(follow);reset['changes'][0]['argumentNames']={};cleared=prepare(reset)['result'];first=next(v for v in cleared['updates']if v['id']==x.functions[0]);assert x.metadata_key not in f.metadata('inspect',text=first['text'])['values'];f.checked('explicit reset removes only optional display metadata')
  added=copy.deepcopy(r);signature={'args':[{'name':'input','type':'int'},{'name':'cell','type':'int','mode':'ref'},{'name':'produced','type':'int','mode':'out'}],'return':'int'};added['changes']=[dict(type='function-add',id=x.owner+'_Function_'+'e'*32,name='명시 표시 기능',description='',signature=signature,argumentNames={'input':'입력 값','cell':'공유 저장소','produced':'계산 출력'})];created=prepare(added)['result'];info=f.metadata('inspect',text=created['additions'][0]['text']);assert x.n.canonical(info['signature'])==signature and json.loads(info['values'][x.metadata_key])==added['changes'][0]['argumentNames'];x.unchanged();f.checked('new value/ref/out parameters retain native names/roles and independent Unicode display labels')
  for fault in ['stale','not-owned','extra']:
   bad=copy.deepcopy(r)
   if fault=='stale':bad['changes'][0]['hash']='0'*64
   elif fault=='not-owned':bad['changes'][0]['id']=x.retained
   else:bad['changes'][0]['newPinId']='unauthorized'
   prepare(bad,False);x.unchanged();f.checked('label candidate '+fault+' preserves existing source/permission/exact-key checks')
  if f.env.get('CONFECTORY_ARGUMENT_LABEL_OLD_HOST'):
   legacy=prepare(follow,host=f.env['CONFECTORY_ARGUMENT_LABEL_OLD_HOST'])['result'];x.verify_rows({v['id']:{'draft':v['text']}for v in legacy['updates']});x.unchanged();f.checked('actual previous published authoring binary parses and retains optional string metadata in a legacy same-contract request; old UI display support is not implied')
  if f.env.get('CONFECTORY_ARGUMENT_LABEL_PRETYPED_HOST'):
   generated=f.metadata('informationReferenceType',project=str(f.manifest),id=f.n+'Leaf');typename=generated['clrType'];source='function Probe.Reader::Selected ('+typename+' target) -> void {value editorArgumentNames='+json.dumps(json.dumps({'target':'대상 정보 참조'},ensure_ascii=False))+';}'
   assert f.metadata('inspect',text=source)['signature']['Args'][0]['Type']==typename
   old=subprocess.run([f.env['CONFECTORY_DOTNET'],f.env['CONFECTORY_ARGUMENT_LABEL_PRETYPED_HOST']],input=json.dumps(dict(operation='inspect',text=source)),env=f.env,text=True,capture_output=True,check=True);response=json.loads(old.stdout);assert not response['ok']and response['code']=='TYPE',response;(f.case/'pretyped-reader-rejection.json').write_text(json.dumps(response,ensure_ascii=False,indent=2));x.unchanged();f.checked('actual pre-typed-reference published parser explicitly refuses the new Reference CLR type; optional label metadata does not confer compatibility')
  x.execute(x.original_result,'label-candidate-original-program');x.unchanged()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
