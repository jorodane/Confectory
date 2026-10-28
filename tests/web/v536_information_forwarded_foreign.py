"""A valid sibling callee is read-only outside the edited function's closure."""
import copy,hashlib,json,shutil,subprocess
import v536_information_forwarded_fixture as x
f=x.f;original_project,original_manifest=f.project,f.manifest
try:
 r=x.request();other=f.case/'other forwarding project';shutil.copytree(original_project,other,ignore=shutil.ignore_patterns('.confectory'));f.project=other;f.manifest=other/original_manifest.name
 foreign=f.n+'OtherForward';provider=foreign+'Body';text='function '+foreign+' (long amount,out long count) -> long {provide '+foreign+' with '+provider+';}'
 (other/'OtherForward.celem').write_text(text);(other/'OtherForwardBody.celem').write_text('implementation '+provider+' for '+foreign+' (long amount,out long count) -> long {body common "OtherForward.csbody";}');(other/'OtherForward.csbody').write_text('count=amount;return amount; // 독립 원본')
 manifest=f.manifest.read_text();f.manifest.write_text(manifest[:-1]+'element OtherForward function "OtherForward.celem";element OtherForwardBody implementation "OtherForwardBody.celem";}')
 body=other/'CallerBody.celem';body.write_text(body.read_text().replace('{','{import '+foreign+' as OtherForward (long,out long) -> long in '+x.owner+';',1))
 graph=copy.deepcopy(x.root);graph['nodes'][1]['graph']['nodes'][-1]['feature']=foreign;(other/'caller.graph.json').write_text(json.dumps(graph,ensure_ascii=False))
 definitions=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=x.caller+'Body',text=(other/'CallerBody.celem').read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert definitions['state']=='node-definitions',definitions
 bad=x.n.request(x.new,x.remap);bad['changes'][0]['mapping']=copy.deepcopy(r['changes'][0]['mapping']);hash=hashlib.sha256(bad['units'][x.caller_id]['draft'].encode()).hexdigest()
 for row in bad['changes'][0]['mapping']['callers'].values():row['hash']=hash
 before={p.relative_to(other):p.read_bytes() for p in other.rglob('*') if p.is_file()}
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'informationDefinitions',**bad}),text=True,capture_output=True,check=True,env=f.env);reply=json.loads(result.stdout);assert reply['ok'] is False and 'Every forwarded sibling' in json.dumps(reply),reply
 assert {p.relative_to(other):p.read_bytes() for p in other.rglob('*') if p.is_file()}==before
 assert all((original_project/p).read_bytes()==v for p,v in x.snapshot.items())
 print('PASS 기존 정의가 유효한 다른 callee의 forwarded 형제는 계약을 추측 수정하지 않고 전체 후보와 양쪽 원본을 보존한다',flush=True)
 print(json.dumps({'checks':1,'evidence':str(f.case),'executed':False,'foreignContractExpanded':False},ensure_ascii=False))
finally:f.project,f.manifest=original_project,original_manifest
