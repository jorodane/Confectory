"""Owned and registered element-array input choices retain separate original proofs."""
import copy,json
import v666_native_array_input_fixture as x
f=x.f
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();cats=x.catalogs();r=x.request(cats);a,b=r['changes'];choice=next(v for v in cats[x.second]['nativeTypes']if v['id']=='External.Fields::Leaf');remote=choice['clrType'];b['signature']['args'][0]['type']=remote+'[]';b['nativeTypes']={remote:copy.deepcopy(choice['proof']),'$function:'+x.second:copy.deepcopy(cats[x.second]['nativeFunctionEdit']['proof'])};shared='var alias=nativeAmount;alias[0].Value.Count=checked(alias[0].Value.Count+31);var values=new '+remote+'[] {new '+remote+' {HP=alias[0].Value.Count},new '+remote+' {HP=alias[1].Value.Count}};return calls.Selected.Invoke(values); // 직접 작성한 외부 원소 변환과 배열 호출 😀\r\n'
 for row in r['changes']:
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id==x.bodies[x.first]:plan['text']=shared
   elif id==x.bodies[x.second]:plan['signature']['args'][0]['type']=remote+'[]';plan['text']='return checked((int)nativeAmount[0].HP+2); // 명시 등록 배열 입력 소비 😀\r\n'
 bad=copy.deepcopy(r);bad['changes'][1]['nativeTypes'].pop(remote);x.prepare(bad,False);assert checkpoint.read_bytes()==before;x.unchanged();out=x.prepare(r)['result'];assert any(v['path']==str(x.c.x.external/'Leaf.celem')for v in out['observations']);assert not any(v['id'].startswith('External.')for v in out['updates']+out['linkedUpdates']);x.unchanged();f.checked('independently selected owned/registered array inputs require original element proofs and produce no foreign writes')
 foreign={p:(p.read_bytes(),p.stat().st_ino,p.stat().st_mode,p.stat().st_mtime_ns)for p in x.c.x.external.iterdir()if p.is_file()};f.invoke('blueprint',dict(action='applySlots',id=x.owner,rows=[],basis=cats[x.first]['basis'],declaration=dict(id=x.owner,hash=f.state()['schema']['textHash'],changes=r['changes'])));ids=x.verify(checkpoint);f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==ids;f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;out=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert out['sourceConfirmed'],(out,f.state().get('logs'));x.verify_live()
 for p,old in foreign.items():stat=p.stat();assert(p.read_bytes(),stat.st_ino,stat.st_mode,stat.st_mtime_ns)==old
 f.checked('owned/registered array inputs execute73 after cold and explicit Review/Confirm; external bytes, inode, mode and mtime exact')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
