"""Atomic same-owner declaration and new-copy candidate API, isolated real engine; no account/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-private-checkpoint-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
items={
'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Slot as Slot (long,out long,out bool) -> long in '+id+';body common "Main.csbody";}'),
'Unit':('object','object '+n+'Unit {}'),'Monster':('object','object '+id+' extends '+n+'Unit {module '+n+'Rules;}'),'Slime':('object','object '+n+'Slime extends '+id+' {}'),
'Slot':('function','function '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {provide '+n+'Slot with '+n+'SlotBody;}'),
'SlotBody':('implementation','implementation '+n+'SlotBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {body common "Slot.csbody";}'),
'Donor':('function','function '+n+'Donor (long input,out long count,out bool active) -> long {description "참조할 기능 한글";provide '+n+'Donor with '+n+'DonorBody;}'),
'DonorBody':('implementation','implementation '+n+'DonorBody for '+n+'Donor (long input,out long count,out bool active) -> long {body common "Donor.csbody";}'),
'Wrong':('function','function '+n+'Wrong (long input,ref long count,out bool active) -> long {}'),
'Rules':('module','module '+n+'Rules {require '+n+'Slot (long,out long,out bool) -> long;default '+n+'Slot with '+n+'SlotBody;}')}
items['Slot2']=('function','function '+n+'Slot2 (long amount,out long slotCount,out bool slotReady) -> long {provide '+n+'Slot2 with '+n+'SlotBody2;}')
items['SlotBody2']=('implementation','implementation '+n+'SlotBody2 for '+n+'Slot2 (long amount,out long slotCount,out bool slotReady) -> long {body common "Slot.csbody";}')
items['Rules']=('module','module '+n+'Rules {require '+n+'Slot (long,out long,out bool) -> long;default '+n+'Slot with '+n+'SlotBody;require '+n+'Slot2 (long,out long,out bool) -> long;default '+n+'Slot2 with '+n+'SlotBody2;}')
items['AliasBody']=('implementation','implementation '+n+'AliasBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long extends '+n+'SlotBody {}')
items['Monster']=('object','object '+id+' extends '+n+'Unit {module '+n+'Rules;provide '+n+'Slot with '+n+'AliasBody;}')
items['Unit']=('object','object '+n+'Unit {use schema '+n+'Vitals;data HP=100;provide '+n+'Donor with '+n+'DonorBody;}')
items['DefaultChild']=('object','object '+n+'DefaultChild extends '+n+'Unit {module '+n+'Rules;}')
items['SlotBody']=('implementation','implementation '+n+'SlotBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {description "원본 구현 한글";import '+n+'Donor as Gift (long,out long,out bool) -> long in '+n+'Unit;body common "Slot.csbody";body windows "SlotWindows.csbody";}')
items['MainBody']=('implementation',items['MainBody'][1].replace(' in '+id+';',' in '+n+'Slime;'))
items['Vitals']=('schema','schema '+n+'Vitals {field HP single general long;}')
for name,(kind,text) in items.items():(project/(name+'.celem')).write_text(text)
(project/'Main.csbody').write_text('return checked((int)calls.Slot.Invoke(5,out long count,out bool ready));');(project/'Slot.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'Donor.csbody').write_text('count=input*2;active=true;return input+20;');(project/'project.cproj').write_text('project Owned.Elements version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;}')
(project/'Slot2.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'SlotBody2.celem').write_text((project/'SlotBody2.celem').read_text().replace('Slot.csbody','Slot2.csbody'));(project/'Slot.csbody').write_text('return calls.Gift.Invoke(amount,out slotCount,out slotReady);');(project/'SlotWindows.csbody').write_text('slotCount=amount+100;slotReady=false;return amount+200;')
original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(i):
 global host,log,origin,token,url
 file=case/f'host-{i}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in file.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,file.read_text()[-1000:];time.sleep(.05)
 raise AssertionError('startup timeout')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(300):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('busy transport')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body,success=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(600):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok')) is success,rows;return {'result':rows[0],'state':u.get('state')}
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission failed')
def checked(text):checks.append(text);print('PASS '+text,flush=True)
try:
 start(0);owner=n+'Slime';invoke('select',{'id':owner});invoke('saveDraft',{});checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=json.loads(checkpoint.read_text());invoke('select',{'id':n+'Wrong'});invoke('inspectDeclaration',{'id':n+'Wrong'});d=state()['declaration'];invoke('editDescription',{'id':n+'Wrong','revision':d['revision'],'hash':d['textHash'],'value':'서버의 다른 미저장 입력'});invoke('select',{'id':n+'Wrong'});invoke('inspectDeclaration',{'id':n+'Wrong'});assert state()['declaration']['description']=='서버의 다른 미저장 입력';invoke('select',{'id':owner});invoke('schema',{'id':owner});d=state()['schema'];new=n+'PrivateSeed';prepared=invoke('blueprint',{'action':'readImplementationCopy','id':owner,'function':n+'Slot','source':n+'AliasBody','target':'common','implementation':new,'revision':d['revision'],'hash':d['textHash']})['result']['result'];saved=json.loads(checkpoint.read_text());assert saved['changes']==before['changes'] and saved['history']==before['history'];assert len(saved['privateCopies'])==1;seed=saved['privateCopies'][new];assert seed['snapshot']['hash']==prepared['seedHash'];assert all((project/k).read_bytes()==v for k,v in original.items());invoke('select',{'id':n+'Wrong'});invoke('inspectDeclaration',{'id':n+'Wrong'});assert state()['declaration']['description']=='서버의 다른 미저장 입력';checked('새 seed의 metadata CAS는 다른 서버 미저장 draft를 Save하거나 버리지 않고 저장된 source/history만 그대로 유지한다')
 invoke('blueprint',{'action':'discardImplementationCopies','id':owner,'copies':[{'implementation':new,'function':n+'Slot','source':n+'AliasBody','target':'common','seedHash':prepared['seedHash']}]});saved=json.loads(checkpoint.read_text());assert saved['changes']==before['changes'] and saved['history']==before['history'] and not saved['privateCopies'];invoke('select',{'id':n+'Wrong'});invoke('inspectDeclaration',{'id':n+'Wrong'});assert state()['declaration']['description']=='서버의 다른 미저장 입력';assert all((project/k).read_bytes()==v for k,v in original.items());checked('정확한 seed 정리는 source/다른 draft/history를 삭제하거나 부분 등록하지 않는다')
 invoke('select',{'id':owner});invoke('schema',{'id':owner});d=state()['schema'];second=n+'LegacySelection';request={'action':'readImplementationCopy','id':owner,'function':n+'Slot','source':n+'AliasBody','target':'common','implementation':second,'revision':d['revision'],'hash':d['textHash']};before_bytes=checkpoint.read_bytes();invoke('blueprint',{**request,'expectedContentFingerprint':'0'*64},False);assert checkpoint.read_bytes()==before_bytes;assert not json.loads(checkpoint.read_text()).get('privateCopies');restored=invoke('blueprint',{**request,'expectedContentFingerprint':prepared['contentFingerprint']})['result']['result'];assert restored['contentFingerprint']==prepared['contentFingerprint'];assert list(json.loads(checkpoint.read_text())['privateCopies'])==[second];checked('이전 private 선택의 content proof는 현재 내용과 같을 때만 seed로 보관하고 바뀐/알 수 없는 기준은 seed 생성 전 거절한다')
except Exception:
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
print(json.dumps({'checks':checks,'actualEngine':True,'renderer':False,'windowsNative':False,'accountOrInference':False,'evidence':str(case)},ensure_ascii=False))
