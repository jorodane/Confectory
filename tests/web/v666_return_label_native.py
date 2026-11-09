"""Return presentation is not an ABI rename or a native source rewrite."""
import copy,hashlib,json,subprocess
import v666_return_label_fixture as x
f=x.f;r=x.request()
def prepare(request,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**request)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 if x.mode=='reproduce':
  baseline=copy.deepcopy(r)
  for row in baseline['changes']:row.pop('returnName')
  prepare(baseline);prepare(r,False);x.execute(x.original_result,'original-return-label');x.unchanged();f.checked('unchanged native contracts execute46; published native writer rejects only the new presentation field')
 else:
  result=prepare(r)['result'];assert not result['linkedUpdates'];x.verify_rows({row['id']:{'draft':row['text']}for row in result['updates']});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert{v['id']:v['text']for v in result['updates']}=={v['id']:v['text']for v in other['updates']};x.unchanged();f.checked('two return labels produce one order-independent metadata candidate without any body or caller update')
  for value in ['', 'x'*61,'bad\nname','bad\u0085name',42,None]:
   bad=copy.deepcopy(r);bad['changes'][0]['returnName']=value;prepare(bad,False);x.unchanged();f.checked('invalid return label '+repr(value)+' rejects the complete candidate and retains originals')
  follow=copy.deepcopy(r)
  for row in follow['changes']:
   text=next(v['text']for v in result['updates']if v['id']==row['id']);follow['units'][row['id']]['draft']=text
   next(v for v in follow['drafts']if v['id']==row['id'])['text']=text
   row.update(hash=hashlib.sha256(text.encode()).hexdigest(),description='후속 설명');row.pop('returnName')
  saved=prepare(follow)['result'];x.verify_rows({row['id']:{'draft':row['text']}for row in saved['updates']});x.unchanged();f.checked('an old request omitting returnName retains existing labels while editing the original description')
  added=copy.deepcopy(r);added['changes']=[dict(type='function-add',id=x.owner+'_Function_'+'e'*32,name='새 표시 기능',description='',signature=copy.deepcopy(x.old),returnName=x.labels[0])];created=prepare(added)['result'];assert len(created['additions'])==1 and f.metadata('inspect',text=created['additions'][0]['text'])['values'][x.metadata_key]==x.labels[0];x.unchanged();f.checked('the same optional presentation field is accepted in an owned first-creation candidate without replacing existing IDs or code')
  for fault in ['stale','non-owned','extra-field']:
   bad=copy.deepcopy(r)
   if fault=='stale':bad['changes'][0]['hash']='0'*64
   elif fault=='non-owned':bad['changes'][0]['id']=x.retained
   else:bad['changes'][0]['newPinId']='replacement'
   prepare(bad,False);x.unchanged();f.checked('return label '+fault+' rejects without expanding editable ownership or contract fields')
  reset=copy.deepcopy(r);reset['changes'][0]['returnName']='결과';result=prepare(reset)['result'];first=next(row for row in result['updates']if row['id']==x.functions[0]);assert x.metadata_key not in f.metadata('inspect',text=first['text'])['values'];f.checked('the default label removes only optional presentation metadata; no native identifier is introduced')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
