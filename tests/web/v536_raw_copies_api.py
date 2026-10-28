"""Owned raw+typed+two private copies use a single real candidate/CAS; fixtures only."""
import copy,json
import v536_wide_mixed as f
try:
 f.start(0);f.invoke('select',{'id':f.id});f.invoke('saveDraft',{});f.invoke('schema',{'id':f.id});d=f.state()['schema'];native=f.state()['draft'];rows=[]
 for feature,source,new,text in [('Slot','AliasBody','RawCopy1','slotCount=amount+5;slotReady=true;return amount+70;'),('Slot2','SlotBody2','RawCopy2','slotCount=amount+9;slotReady=true;return amount+90;')]:
  view=f.invoke('blueprint',{'action':'readImplementationCopy','id':f.id,'function':f.n+feature,'source':f.n+source,'target':'common','implementation':f.n+new,'revision':d['revision'],'hash':d['textHash']})['result']['result'];rows.append({'function':f.n+feature,'implementation':f.n+new,'copySource':f.n+source,'copyTarget':'common','fingerprint':view['fingerprint'],'basis':view['basis'],'edits':[{'type':'source','node':'body','text':text}]})
 for row in rows:
  view=f.invoke('blueprint',{'action':'readImplementationCopy','id':f.id,'function':row['function'],'source':row['copySource'],'target':row['copyTarget'],'implementation':row['implementation'],'revision':d['revision'],'hash':d['textHash']})['result']['result'];row.update(basis=view['basis'],fingerprint=view['fingerprint'])
 raw=native['text'].replace('{','{\n// raw 원문 한글 😀\n',1).replace('data MP=4;','data MP= // 정확한 값 주석\n4;')+'\n// 끝 보존\n';changes=[*f.changes,{'type':'data','path':['MP'],'contract':f.shape('general','single','long'),'valueJson':'9007199254740995'}];declaration={'id':f.id,'hash':d['textHash'],'changes':changes,'raw':{'text':raw,'hash':d['textHash'],'sourceIdentity':native['sourceIdentity'],'revision':native['revision'],'surface':'primary'}};request={'action':'applySlots','id':f.id,'rows':rows,'declaration':declaration};checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 for kind in ['last-copy','raw-provider','raw-field','identity']:
  bad=copy.deepcopy(request)
  if kind=='last-copy':bad['rows'][-1]['edits'][0]['node']='not-owned'
  elif kind=='raw-provider':bad['declaration']['raw']['text']=raw[:raw.rfind('}')]+f'provide {f.n}Slot with {f.n}SlotBody;\n'+raw[raw.rfind('}'):]
  elif kind=='raw-field':bad['declaration']['raw']['text']=raw.replace('data MP= // 정확한 값 주석\n4;','data MP=9;')
  else:bad['declaration']['raw']['sourceIdentity']='0'*64
  f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before and f.state()['draft']['text']==native['text'];f.originals()
 peer=f.project/'Slime.celem';original=peer.read_bytes();peer.write_bytes(original+b'\n// isolated peer before candidate save\n')
 try:f.invoke('blueprint',request,False);assert checkpoint.read_bytes()==before and f.state()['draft']['text']==native['text']
 finally:peer.write_bytes(original)
 f.checked('last copy failure, raw provider/typed overlap, actual source conflict and forged source location reject declaration/registration/all copies without any partial checkpoint change')
 f.invoke('blueprint',request);saved=f.state()['draft']['text'];assert '// raw 원문 한글 😀' in saved and '// 끝 보존' in saved and 'data MP= // 정확한 값 주석\n9007199254740995;' in saved;assert 'provide '+f.n+'Slot with '+f.n+'RawCopy1;' in saved and 'provide '+f.n+'Slot2 with '+f.n+'RawCopy2;' in saved;state=json.loads(checkpoint.read_text());assert len([r for r in state['changes'] if r.get('creationOwner')==f.id and r['kind']=='implementation'])==2;assert not state['privateCopies'];f.originals();f.checked('same original raw/typed/copy source closure validates and saves both copied bodies/imports/wrapper/provider/schema/registration with original annotations and exact long')
 query={'action':'settledSlots','id':f.id,'rows':[{k:v for k,v in r.items() if k!='basis'} for r in rows],'declaration':declaration};assert f.invoke('blueprint',query)['result']['result']['settled'];bad=copy.deepcopy(query);bad['rows']=bad['rows'][:1];assert not f.invoke('blueprint',bad)['result']['result']['settled'];f.stop();f.start(1);f.invoke('select',{'id':f.id});assert f.state()['draft']['text']==saved and f.invoke('blueprint',query)['result']['result']['settled'];f.originals();f.checked('cold receipt binds the exact raw declaration and entire copy list; partial receipt cannot authorize the full Save')
except Exception:
 print('EVIDENCE '+str(f.case),flush=True);raise
finally:f.stop()
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'renderer':False,'nativeWindows':False,'accountOrInference':False},ensure_ascii=False))
