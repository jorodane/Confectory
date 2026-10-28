"""Direct function header glyph: bounded presentation candidate, no source writes."""
import json,os,subprocess
import v536_wide_mixed as f
owner=f.n+'Donor';source=(f.project/'Donor.celem').read_text().replace('{','{ // preserve header comment\n',1);request={'project':str(f.project/'project.cproj'),'manifest':f.manifest.read_text(),'id':owner,'text':source,'drafts':[]}
def call(changes,ok=True,**extra):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'functionPresentation',**request,'changes':changes,**extra}),text=True,capture_output=True,check=True,env=f.env);v=json.loads(p.stdout);assert v['ok']==ok,v;return v.get('result')
before=f.metadata('inspect',text=source);result=call([{'type':'icon','text':'🛡️'},{'type':'description','text':'아이콘과 설명'}]);after=f.metadata('inspect',text=result['text']);assert before['signature']==after['signature'] and before['relations']==after['relations'] and after['values']['editorIcon']=='🛡️' and after['description']=='아이콘과 설명' and 'preserve header comment' in result['text'];assert result['manifest']==request['manifest'] and result['updates']==[] and result['additions']==[];f.originals();f.checked('기능 glyph·설명 후보는 기존 함수 identity·계약·관계·주석·등록·typed caller와 C# 원문을 유지한다')
for bad in ['',None,'ab','<','\n',' ']:call([{'type':'description','text':'must not remain'},{'type':'icon','text':bad}],False)
for changes in [[{'type':'icon','text':'★'},{'type':'icon','text':'👑'}],[{'type':'signature','text':'changed'}],[{'type':'icon','text':'★','extra':True}]]:call(changes,False)
f.originals();f.checked('마지막 glyph 오류·중복·계약 변경·알 수 없는 필드는 전체 후보를 거절하고 원문과 입력을 보존한다')
call([{'type':'icon','text':'★'}],False,id=f.n+'Other');call([{'type':'icon','text':'★'}],False,text=source.replace(' {',' extends '+f.n+'Parent {',1));call([{'type':'icon','text':'★'}],False,id='Foreign::Donor',text=source.replace(owner,'Foreign::Donor'));f.originals();f.checked('다른 identity·외부 namespace·상속 함수는 표시 저장의 직접 소유 경계를 넘지 못한다')
print(json.dumps({'checks':f.checks,'evidence':str(f.case),'sourceWritten':False,'projectExecuted':False,'accountOrInference':False},ensure_ascii=False))
