"""Pure saved information-function archive candidates; only a fresh owned fixture is mutated."""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-information-retirement-'));n='Owned.Retirement::';owner=n+'Details';fn=owner+'_Function_'+'a'*32;impl=fn+'BlueprintBody';dotnet=os.environ.get('CONFECTORY_DOTNET','dotnet');tool=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';checks=[]
def rpc(operation,ok=True,**data):
 p=subprocess.run([dotnet,str(tool)],input=json.dumps({'operation':operation,**data},ensure_ascii=False),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok']) is ok,v;return v.get('result')
def write(path,text):p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def h(text):return hashlib.sha256(text.encode()).hexdigest()
def checked(text):checks.append(text);print('PASS '+text,flush=True)
info='schema '+owner+' { // keep my comment\nfield HP single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_HP="9223372036854775806";contain function '+fn+';}'
function='function '+fn+' () -> void {description "자체 실행";value editorName="삭제 복구 😀";}'
scaffold=rpc('blueprintPrepareImplementation',id=fn,text=function,owner=owner,ownerText=info,implementation=impl,graphPath='graphs/work.graph.json',nodePath='work.node.json')
info=rpc('mergeDeclarationText',text=info,typed=scaffold['owner'],raw=info)
body={'schema':1,'node':'body','definitionHash':'0'*64,'source':'return;'}
texts={
 'Details.celem':info,'Method.celem':function,'Impl.celem':scaffold['implementation'].replace('}', 'body linux "other.csbody";}'),
 'Other.celem':'schema '+n+'Other {field Count single general long;}',
 'Main.celem':'function '+n+'Main () -> int {}',
 'graphs/work.graph.json':json.dumps(scaffold['graph'],ensure_ascii=False),'graphs/work.node.json':json.dumps(body),'other.csbody':'return;',
}
fnpath='elements/'+fn.split('::')[1]+'.celem';implpath='elements/'+impl.split('::')[1]+'.celem';texts[fnpath]=texts.pop('Method.celem');texts[implpath]=texts.pop('Impl.celem')
manifest='project Owned.Retirement version "1" {standalone true;entry '+n+'Main;element Details schema "Details.celem";element '+fn.split('::')[1]+' function "'+fnpath+'";element '+impl.split('::')[1]+' implementation "'+implpath+'";element Other schema "Other.celem";element Main function "Main.celem";}'
texts['project.cproj']=manifest
for path,text in texts.items():write(path,text)
original={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
rows=rpc('describe',project=str(root/'project.cproj'))['units'];units={}
for row in rows:
 text=(root/row['path']).read_text();units[row['id']]={**row,'revision':1,'baseline':h(text),'original':text,'draft':text}
node=impl+'/body:common/node:body';units[node]['draft']=json.dumps({**body,'source':'return; // 보존할 미반영 본문'})
base={'project':str(root/'project.cproj'),'namespace':n[:-2],'scope':{'participant':'fixture-owner','context':'fixture-context'},'units':units,'retirements':{},'owner':owner,'function':fn,'ownerHash':h(info),'functionHash':h(function),'checkpointHash':'b'*64}
def run(action,ok=True,**data):return rpc('informationFunctionRetirement',ok,**{**base,'action':action,**data})
def unchanged():assert all((root/path).read_bytes()==text for path,text in original.items()) and {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}==set(original)
plan=run('plan');assert not plan['references'];assert set(plan['ids'])=={fn,impl,impl+'/body:common',node,impl+'/body:linux'};assert 'contain function '+fn not in plan['ownerAfter'] and 'provide '+fn not in plan['ownerAfter'];assert '// keep my comment' in plan['ownerAfter'] and '9223372036854775806' in plan['ownerAfter'] and 'HP' in plan['ownerAfter'];assert plan['entries'][node]['draft']==units[node]['draft'];unchanged();checked('단독 소유 함수·구현·graph/node·다른 target의 완전한 삭제 후보는 주석·정확한 값·미반영 본문을 보관하고 파일을 쓰지 않는다')
for bad in [{'ownerHash':'0'*64},{'functionHash':'0'*64},{'function':n+'Main','functionHash':h(texts['Main.celem'])},{'owner':n+'Other','ownerHash':h(texts['Other.celem'])}]:run('plan',False,**bad)
for bad_id,bad_kind in [(fn,'body'),(owner,'object'),(impl,'blueprint'),(n+'ProjectManifest','schema')]:
 new=copy.deepcopy(units);new[bad_id]['kind']=bad_kind;run('plan',False,units=new)
new=copy.deepcopy(units);new[fn]['baseline']='missing';run('plan',False,units=new);unchanged();checked('오래된 hash·다른 정보·소유하지 않은 함수·기존 파일과 충돌하는 미완료 생성은 전체 거절한다')
for kind,text in [
 ('implementation','implementation '+n+'Caller for '+n+'Main () -> int {import '+fn+' as Call () -> void;}'),
 ('schema','schema '+n+'Caller {field Action single function '+fn+';}'),
 ('module','module '+n+'Caller {require '+fn+' () -> void;}'),
 ('schema','schema '+n+'Caller {provide '+fn+' with '+impl+';}'),
]:
 source=copy.deepcopy(units);source[n+'Caller']={'id':n+'Caller','kind':kind,'path':'Caller.celem','revision':1,'original':text,'draft':text,'baseline':h(text)};write('Caller.celem',text);p=run('plan',units=source);assert p['references'];(root/'Caller.celem').unlink()
unchanged();checked('다른 구현 typed import·함수 값 타입·모듈 요구·공유 provide 참조는 삭제를 차단한다')
applied=run('apply',evidence=plan);assert set(units)-set(applied['units'])==set(plan['ids']);assert applied['units'][owner]['draft']==plan['ownerAfter'] and applied['units'][n+'Other']==units[n+'Other'];receipt=applied['retirements'][plan['token']];assert receipt['entries'][node]['draft']==units[node]['draft'];assert set(applied['units'][owner]['retirementGroup'])=={owner,n+'ProjectManifest'};unchanged();checked('apply는 정보·등록·전체 멤버를 하나의 반환 후보로 다루며 다른 정보와 원본 파일은 보존한다')
changed=copy.deepcopy(units);changed[owner]['draft']+='\n// peer';run('apply',False,evidence=plan,units=changed)
restored=run('recover',units=applied['units'],retirements=applied['retirements'],evidence=receipt);assert not restored['retirements'];assert set(restored['units'])==set(units);assert all(restored['units'][key]['draft']==value['draft'] for key,value in units.items());unchanged();checked('계획 후 실제 peer 수정은 미적용이며 pending 복구는 원래 모든 초안·입력과 등록을 보존한다')
outcome={'version':1,'token':plan['token'],'action':'recover','workspace':plan['workspace'],'phase':'','result':{'state':'staged','owner':owner,'manifest':n+'ProjectManifest','ids':plan['ids'],'checkpointSaved':True,'physicalSourceRemoved':False,'sourceConfirmed':False},'sources':{},'absent':[]}
for id in [*plan['ids'],owner,n+'ProjectManifest']:
 u=restored['units'][id];outcome['sources'][id]={'kind':u['kind'],'path':u['path'],'hash':h(u['draft'])}
run('validate-outcome',outcome=outcome,units=restored['units']);assert run('settled',outcome=outcome,units=restored['units'])['settled'];changed=copy.deepcopy(restored['units']);changed[owner]['draft']+='\n// late input';assert not run('settled',outcome=outcome,units=changed)['settled'];run('settled',False,outcome=outcome,units=restored['units'],scope={'participant':'fixture-owner','context':'other-context'});unchanged();checked('완료 결과의 workspace·모든 source/path/hash/phase를 읽기 검증하며 늦은 입력·다른 context를 완료로 추측하지 않는다')
run('validate',receipt=receipt,units=applied['units']);forged=copy.deepcopy(receipt);forged['ownerAfter']=forged['ownerAfter'].replace('HP','Stolen');run('validate',False,receipt=forged,units=applied['units']);run('validate',False,receipt=receipt,units=applied['units'],scope={'participant':'fixture-owner','context':'other-context'});unchanged();checked('재시작 receipt 검증은 같은 native bundle·locator·owner 변경 증거를 요구하고 변조된 다른 필드 수정을 거절한다')
# Simulate only this fixture's explicit deletion Confirm. Retired source files remain untouched.
confirmed=copy.deepcopy(applied);receipt=confirmed['retirements'][plan['token']];receipt['state']='confirmed'
for key in [owner,n+'ProjectManifest']:
 u=confirmed['units'][key];write(u['path'],u['draft']);u['original']=u['draft'];u['baseline']=h(u['draft']);u.pop('retirementGroup',None)
original={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
run('validate',receipt=receipt,units=confirmed['units']);recovery=run('recover',units=confirmed['units'],retirements=confirmed['retirements'],evidence=receipt);r=recovery['retirements'][plan['token']];assert r['state']=='restoring' and recovery['units'][owner]['draft']==info and recovery['units'][node]['draft']==units[node]['draft'];group=set(plan['ids'])|{owner,n+'ProjectManifest'};assert all(set(recovery['units'][key]['retirementGroup'])==group for key in group);unchanged();checked('확정 삭제 후 복구 후보는 새 전체 Review 그룹을 만들고 보관한 본문·다중 target·정확한 값을 복원하며 자동 반영하지 않는다')
cancelled=run('cancel',units=recovery['units'],retirements=recovery['retirements'],evidence=r);assert set(cancelled['units'])==set(confirmed['units']);assert cancelled['units'][owner]['draft']==confirmed['units'][owner]['draft'] and cancelled['retirements'][plan['token']]['state']=='confirmed';unchanged();new=copy.deepcopy(recovery['units']);new[node]['draft']=json.dumps({**body,'source':'return; // new input'});run('cancel',False,units=new,retirements=recovery['retirements'],evidence=r);unchanged();checked('복구 취소는 확정된 삭제 상태로만 돌아가고 새 본문 입력이 생기면 지우지 않고 거절한다')
print(json.dumps({'checks':checks,'evidence':str(root),'nativePure':True,'renderer':False,'projectExecuted':False,'accountOrInference':False},ensure_ascii=False))
