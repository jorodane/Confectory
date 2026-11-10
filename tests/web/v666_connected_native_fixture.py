"""A directly owned C# function plus its direct C# caller; no inferred source."""
import copy,hashlib,json,subprocess
import v666_native_edit_fixture as e
x,f,owner,fn=e.x,e.f,e.owner,e.fn
impl=fn+'Body';body_id=impl+'/body:common';body_path=e.local+'.csbody';impl_path=e.local+'Body.celem';caller_id=f.n+'MainBody/body:common'
e.path.write_text('function '+fn+' (int amount) -> int {value editorName="타입 전환";provide '+fn+' with '+impl+';}')
(f.project/impl_path).write_text('implementation '+impl+' for '+fn+' (int amount) -> int {body common "'+body_path+'";}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+impl.split('::')[1]+' implementation "'+impl_path+'";registry Confectory.Build.DotNet',1))
original='return amount; // 보존한 원래 본문 · 😀\r\n';(f.project/body_path).write_bytes(original.encode())
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+fn+' as Connected (int) -> int;body common "Main.csbody";}')
caller_original='int result=calls.Connected.Invoke(30);Console.WriteLine(result);return result; // 원래 호출자\r\n';(f.project/'Main.csbody').write_bytes(caller_original.encode())
x.original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts}
changes_allowed={'elements/'+e.local+'.celem',impl_path,body_path,'MainBody.celem','Main.csbody'}
def catalog():
 f.invoke('schema',dict(id=owner));s=f.state()['schema'];return f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=s['textHash'],includeNativeTypes=True,nativeFunction=fn,includeFunctionInputs=fn,includeFunctionBodies=True))['result']['result']
def selections(c):
 choices={r['id']:r for r in c['nativeTypes']};payload=choices[f.n+'Payload']['clrType'];leaf=choices[f.n+'Leaf']['clrType'];module_type=choices[f.n+'NativeRules']['clrType'];mood=choices[f.n+'Mood']['clrType'];body='choice='+mood+'Ids.FromId("ready");payload.Value.Count=checked(payload.Value.Count+1);return payload; // 명시 전환 · 😀\r\n';caller='var value=calls.Connected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=30}},global::System.Array.Empty<'+module_type+'>(),default,out var choice);if('+mood+'Ids.ToId(choice)!="ready")throw new Exception("choice lost");int result=checked((int)value.Value.Count);Console.WriteLine(result);return result; // 명시 호출자\r\n';return {body_id:body,caller_id:caller}
def request(c=None,protected=True):
 c=c or catalog();req=x.request(c);row=req['declaration']['changes'][0];method=next(v for v in f.state()['schema']['ownFunctions']if v['id']==fn);signature=row['signature'];texts=selections(c);row.update(type='function-edit',id=fn,hash=method['hash'],mapping=dict(before=dict(args=[dict(name='amount',type='int')],**{'return':'int'}),args=dict(amount=None),bodies={id:{k:entry[k]for k in ['hash','path']}|dict(beforeSignature=entry['signature'],signature=entry['signature']if entry['caller']else signature,contract=signature,text=texts[id])for id,entry in c['functionBodies'].items()}))
 if protected:row['nativeTypes']['$function:'+fn]=copy.deepcopy(c['nativeFunctionEdit']['proof'])
 else:row.pop('nativeTypes')
 return req
def verify(checkpoint,signature):
 ids=e.verify(checkpoint,signature);rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};texts=selections(catalog())
 for id,text in texts.items():assert rows[id]['draft']==text
 receipt=rows[owner]['slotSaveReceipt'];assert {impl_path,'MainBody.celem'}<=set(receipt['readGuards']);assert {body_id,caller_id}<=set(receipt['sources']);assert rows[body_id]['baseline']==hashlib.sha256(x.original[body_path]).hexdigest()and rows[caller_id]['baseline']==hashlib.sha256(x.original['Main.csbody']).hexdigest();return ids

def execute(expected,label):
 out=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(label+'-build.log')).write_text(out.stdout+out.stderr);assert out.returncode==0,out.stdout[-1800:]+out.stderr[-900:];run=subprocess.run(json.loads(out.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(label+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(expected,str(expected)),(run.returncode,run.stdout,run.stderr)
