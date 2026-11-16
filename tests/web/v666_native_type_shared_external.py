"""A shared caller compiles each independently selected nominal type proof."""
import copy,json,stat
import v666_native_type_shared_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();cats=x.catalogs();r=x.request(cats);a,b=r['changes'];choice=next(v for v in cats[x.second]['nativeTypes']if v['id']=='External.Fields::Leaf');remote=choice['clrType'];payload=a['signature']['args'][0]['type'];leaf=next(v['clrType']for v in cats[x.first]['nativeTypes']if v['id']==f.n+'Leaf');b['signature']['args'][0]['type']=remote;b['nativeTypes']={remote:copy.deepcopy(choice['proof']),'$function:'+x.second:copy.deepcopy(cats[x.second]['nativeFunctionEdit']['proof'])};shared='int result=calls.Connected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=30}})+calls.SecondSelected.Invoke(new '+remote+' {HP=40});Console.WriteLine(result);return result; // 같은 명시 본문, 독립 타입 증거 😀\r\n'
 for row in r['changes']:
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id==x.callers[x.first]:plan['text']=shared
   elif row['id']==x.second:plan['signature']=copy.deepcopy(row['signature']);plan['text']='return checked((int)amount.HP+2); // 직접 선택한 등록 구조체 😀\r\n'
 bad=copy.deepcopy(r);bad['changes'][1]['nativeTypes'].pop(remote);x.prepare(bad,False);assert checkpoint.read_bytes()==before;x.unchanged();out=x.prepare(r)['result'];assert any(v['path']==str(x.c.x.external/'Leaf.celem')for v in out['observations']);assert not any(v['id'].startswith('External.')for v in out['updates']+out['linkedUpdates']);x.unchanged();f.checked('future compiler sees both separately selected nominal definitions; missing external type proof fails and no external write enters the candidate')
 foreign={p:(p.read_bytes(),p.stat().st_ino,p.stat().st_mode,p.stat().st_mtime_ns)for p in x.c.x.external.iterdir()if p.is_file()};f.invoke('blueprint',dict(action='applySlots',id=x.owner,rows=[],basis=cats[x.first]['basis'],declaration=dict(id=x.owner,hash=f.state()['schema']['textHash'],changes=r['changes'])));ids=x.verify(checkpoint);f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed'],(out,f.state().get('logs'));x.verify_live()
 for p,old in foreign.items():s=p.stat();assert(p.read_bytes(),s.st_ino,s.st_mode,s.st_mtime_ns)==old
 f.checked('shared owned/registered nominal calls actually execute73 after cold and explicit Review/Confirm; external bytes, inode, mode and mtime are exact')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
