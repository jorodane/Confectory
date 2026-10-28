"""Retained native body, ref alias/local and extra owned code; isolated project."""
import copy,json
import v536_information_whole_contract_fixture as b
f,d,n,owner,fn,caller,mode=b.f,b.d,b.n,b.owner,b.fn,b.caller,b.mode
old,new,selected,remap,edited=b.old,b.new,b.selected,b.remap,b.edited
scenario,chain=b.scenario,b.chain
body_id,body_path=b.body_id,b.body_path
storage='storage' in __import__('sys').argv[4:]
post_mode='enum' if 'enum' in __import__('sys').argv[4:] else 'post' if 'post' in __import__('sys').argv[4:] else None
graph_path=f.project/'function.graph.json';g=json.loads(graph_path.read_text());g['profile']='sync-acyclic-alias-locals-v1'
if storage:g['nodes'][0].pop('implementationContext');g['nodes'][0]['forwardCallerStorage']=True
extra={'id':'extra','kind':'code','control':'next','intent':'기존 별칭의 저장소를 보존한다','implementation':'extra.node.json','signature':{'args':[{'name':'value','type':'long','mode':'ref'}],'return':'void'},'arguments':{'value':{'local':'root_alias'}}}
g['locals']=[{'id':'root_alias','name':'기존 별칭','type':'long','source':{'input':'amount'}},{'id':'kept','name':'정확한 지역값','type':'long','initial':{'constant':9223372036854775806}}]
ret=next(row['id'] for row in g['nodes'] if row['kind']=='export');g['nodes'].insert(1,extra);g['edges']=[{'from':'body','port':'next','to':'extra'},{'from':'extra','port':'next','to':ret}]
graph_path.write_text(json.dumps(g,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=fn+'Body',text=b.base.implementation_file.read_text(),bodyTarget='common',graph=g,definitionsOnly=True)
assert defs['state']=='node-definitions',defs
record=json.loads((f.project/body_path).read_text());extra_record=copy.deepcopy(record);extra_record['node']='extra';extra_record['source']='value=checked(value+1); // 별칭 셀·독립 원문 보존\r\n'
for row in defs['nodes']:
 if row['id']=='body':record['definitionHash']=row['definitionHash']
 if row['id']=='extra':extra_record['definitionHash']=row['definitionHash']
(f.project/body_path).write_text(json.dumps(record,ensure_ascii=False));(f.project/'extra.node.json').write_text(json.dumps(extra_record,ensure_ascii=False))
post_id=caller+'Body/body:common/postCall:invoke'
post_source='return Read(@context.@total)>0&&@originalResult; // 후속 코드 직접 편집 😀\r\n'
post_helpers='private static long Read(long value){return value;} // 보조 함수 원문\r\n'
if post_mode:
 function_file=b.base.function_file;text=function_file.read_text().replace('{','{value blueprintPublishedOutputs='+json.dumps(json.dumps(['count']))+';',1);function_file.write_text(text)
 caller_graph=json.loads((f.project/'caller.graph.json').read_text());call=caller_graph['nodes'][0];post_id=caller+'Body/body:common/postCall:'+call['id']
 if post_mode=='enum':
  caller_graph['profile']='sync-acyclic-switch-v1';execution={'primary':'done','members':[{'id':'done','name':'Done','value':0},{'id':'next','name':'Next','value':1}]};call.update(control='switch',executionEnum=execution);wrapper=f.metadata('blueprintCallWrapper',functionText=text,executionEnum=execution,returnMapping='native-return-out-v1',source='return Result.Done;');call['postCall']={k:wrapper[k] for k in ['mode','contractHash','source','helpers','returnMapping']};caller_graph['edges']=[{'from':call['id'],'port':'case:done','to':'exit:return'}];post_source='return Read(@context.@total)>0?Result.Done:Result.Next; // enum 후처리\r\n'
 else:
  caller_graph['profile']='sync-acyclic-methods-v1';wrapper=f.metadata('blueprintCallAfter',functionText=text,source='return @context.@count;');call['postCall']={k:wrapper[k] for k in ['contractHash','source','helpers']}
 (f.project/'caller.graph.json').write_text(json.dumps(caller_graph,ensure_ascii=False))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
 row=preview['functionBodies'][body_id];assert row['sourceKind']=='whole-graph-csharp'
 plan={'before':old,'args':remap,'bodies':{body_id:{k:row[k] for k in ['hash','path','whole']}|{'beforeSignature':b.before_native,'signature':selected,'contract':new,'text':edited,'outputs':{'return':'nativeTotal','nativeTotal':'nativeTotal'}}}}
 plan['callers']=b.selections({'functionBodies':{body_id:{**row,'sourceKind':'whole-csharp'}},'functionInputs':preview['functionInputs']})['callers']
 plan['implementations']={key:{k:r[k] for k in ['graph','node','argument','hash','before']}|{'value':{'input':'increment'}} for key,r in preview['functionInputUses'].items() if r['node']=='$alias:root_alias'}
 assert len(plan['implementations'])==1
 if post_mode:
  row=preview['functionBodies'][post_id];plan['bodies'][post_id]={'wrapper':row['wrapper'],'contract':new,'text':post_source,'helpers':post_helpers}
 r=next((key,row) for key,row in preview['functionOutputs'].items() if row['name']=='return')
 plan['outputs']={r[0]:{k:r[1][k] for k in ['graph','node','name','hash','before']}|{'type':'bool','source':{'node':'body','output':'return'}}}
 return plan

def request():
 r=n.request(new,remap);preview={key:f.metadata(op,id=owner,function=fn,includeBlueprintTargets=True,units=r['units'],**({'functionSignature':new,'functionRemap':remap} if key=='functionBodies' else {})) for key,op in [('functionBodies','informationFunctionBodies'),('functionInputs','informationFunctionInputs'),('functionInputUses','informationFunctionInputUses'),('functionOutputs','informationFunctionOutputs'),('functionOutputGraphs','informationFunctionOutputGraphs')]};r['changes'][0]['mapping']=selections(preview);return r

def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};graph=json.loads(rows[fn+'Body/body:common']['draft']);assert graph['edges']==g['edges'] and graph['entry']==g['entry'] and [v['id'] for v in graph['nodes']]==[v['id'] for v in g['nodes']]
 assert graph['locals'][1]==g['locals'][1] and graph['locals'][0]=={**g['locals'][0],'source':{'input':'increment'}}
 assert next(v for v in graph['nodes'] if v['id']=='extra')==extra
 assert json.loads(rows[body_id]['draft'])['source']==edited
 assert json.loads(rows[fn+'Body/body:common/node:extra']['draft'])['source']==extra_record['source']
 assert next(v for v in graph['nodes'] if v['id']==ret)['arguments']['value']=={'node':'body','output':'return'}
 if post_mode:
  post=json.loads(rows[caller+'Body/body:common']['draft'])['nodes'][0]['postCall'];assert post['source']==post_source and post['helpers']==post_helpers
 assert all((f.project/p).read_bytes()==v for p,v in snapshot.items());ids=rows[owner]['atomicEditGroup'];assert fn+'Body/body:common/node:extra' in ids;return ids
