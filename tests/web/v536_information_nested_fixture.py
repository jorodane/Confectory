"""Qualified duplicate leaf calls, depth2 and independent sibling sources."""
import copy,json,re,sys
import v536_information_whole_contract_fixture as b
f,d,n,owner,fn,caller,mode=b.f,b.d,b.n,b.owner,b.fn,b.caller,b.mode
old,new,selected,remap,edited=b.old,b.new,b.selected,b.remap,b.edited
body_id,body_path=b.body_id,b.body_path
scenario,chain=b.scenario,b.chain
cpp='source' in sys.argv[4:]
forward='forward' in sys.argv[4:]
if forward:assert cpp
callee='callee' in sys.argv[4:]
post_mode='enum' if 'enum' in sys.argv[4:] else 'post' if 'post' in sys.argv[4:] else None
if post_mode:
 file=b.base.function_file;file.write_text(file.read_text().replace('{','{value blueprintPublishedOutputs='+json.dumps(json.dumps(['count']))+';',1))
alias=re.search(r'\bas (\w+)\s*\(', (f.project/'CallerBody.celem').read_text())[1]
post_source='return Read(@context.@total)>0&&@originalResult; // 직접 작성한 후처리\r\n'
post_helpers='private static long Read(long value){return value;} // 보조 원문\r\n'
caller_id=caller+'Body/body:common';root=json.loads((f.project/'caller.graph.json').read_text());original_call=copy.deepcopy(root['nodes'][0]);leaf_id=original_call['id']
private_signature={'args':[{'name':'value','type':'long',**({'mode':'ref'} if forward else {})}],'return':'long'}
record_sources={}
def private(name):
 code={'id':'body','kind':'code','control':'next','implementation':name+'.node.json','intent':'동명 원문·범위 보존 '+name,'signature':{'args':[{'name':'item','type':'long'}],'return':'long'},'arguments':{'item':{'node':leaf_id}}}
 if forward:code['signature']['args'][0]['mode']='ref';code['forwardCallerStorage']=True;code['arguments']={'item':{'input':'value'}}
 call=copy.deepcopy(original_call);call['arguments']={'amount':{'input':'value'}}
 graph={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[call,code],'entry':leaf_id,'edges':[{'from':leaf_id,'port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'binary':{'operator':'+','type':'long','operands':[{'node':'body'},{'node':leaf_id,'output':'count'}]}}},'locals':[{'id':'kept','name':'정확한 지역값','type':'long','initial':{'constant':9223372036854775806}}]}
 if cpp:
  code['imports']=[fn]
  source='return '+alias+'.Invoke(item,out long count); // '+name+' 원래 opaque C#\r\n'
 else:source='return checked(item+1); // '+name+' 원문 😀\r\n'
 if post_mode:
  if post_mode=='enum':
   graph['profile']='sync-acyclic-switch-v1';execution={'primary':'done','members':[{'id':'done','name':'Done','value':0},{'id':'next','name':'Next','value':1}]};call.update(control='switch',executionEnum=execution);wrapper=f.metadata('blueprintCallWrapper',functionText=b.base.function_file.read_text(),executionEnum=execution,returnMapping='native-return-out-v1',source='return Result.Done;');call['postCall']={k:wrapper[k] for k in ['mode','contractHash','source','helpers','returnMapping']};graph['edges']=[{'from':leaf_id,'port':'case:done','to':'exit:return'}];graph['exits']['return']['binary']['operands'][0]={'node':leaf_id}
  else:
   graph['profile']='sync-acyclic-methods-v1'
   wrapper=f.metadata('blueprintCallAfter',functionText=b.base.function_file.read_text(),source='return @context.@count;');call['postCall']={k:wrapper[k] for k in ['contractHash','source','helpers']}
 record_sources[name]=source
 return graph
def box(name,graph,binding):return {'id':name,'kind':'graph','control':'next','intent':'내부 '+name,'signature':copy.deepcopy(private_signature),'arguments':{'value':binding},'graph':graph}
left=private('left');deep=private('right');right={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[box('deep',deep,{'input':'value'})],'entry':'deep','edges':[{'from':'deep','port':'next','to':'exit:return'}],'exits':{'return':{'node':'deep'}},'locals':[]}
untouched={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[{'id':'body','kind':'code','control':'next','intent':'다른 형제 원문','implementation':'untouched.node.json','signature':{'args':[{'name':'item','type':'long'}],'return':'long'},'arguments':{'item':{'input':'value'}}}],'entry':'body','edges':[{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'node':'body'}},'locals':[]};record_sources['untouched']='return checked(item+7); // 다른 형제 원문\r\n'
root.update(profile='sync-acyclic-nested-v1',nodes=[box('left',left,{'input':'first'}),box('right',right,{'input':'second'}),box('untouched',untouched,{'input':'first'})],entry='left',edges=[{'from':'left','port':'next','to':'right'},{'from':'right','port':'next','to':'untouched'},{'from':'untouched','port':'next','to':'exit:return'}],exits={'return':{'binary':{'operator':'+','type':'long','operands':[{'node':'left'},{'node':'right'}]}}},locals=[{'id':'outer','name':'상위 값 보존','type':'long','initial':{'constant':9223372036854775805}}])
(f.project/'caller.graph.json').write_text(json.dumps(root,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=caller+'Body',text=(f.project/'CallerBody.celem').read_text(),bodyTarget='common',graph=root,definitionsOnly=True)
assert defs['state']=='node-definitions',defs
for row in defs.get('nestedNodes',[]):
 if row['definition']['kind']=='code':
  name={'left/body':'left','right/deep/body':'right','untouched/body':'untouched'}[row['id']];(f.project/(name+'.node.json')).write_text(json.dumps({'schema':1,'node':'body','definitionHash':row['definitionHash'],'source':record_sources[name]},ensure_ascii=False))
if post_mode=='enum':post_source='return Read(@context.@total)>0?Result.Done:Result.Next; // enum 후처리\r\n'
edited_records={name:'bool ready='+alias+'.Invoke(\"직접 쓴 '+name+'\",out long count,item);return count; // 수동 C# 원문 😀\r\n' for name in ['left','right']}
record_ids={name:caller_id+'/node:'+path.replace('/','/node:') for name,path in [('left','left/body'),('right','right/deep/body'),('untouched','untouched/body')]}
if callee:
 callee_graph=json.loads((f.project/'function.graph.json').read_text());sig={'args':[{'name':'value','type':'long'},{'name':'count','type':'long','mode':'out'}],'return':'long'};child={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[{'id':'body','kind':'code','control':'next','intent':'private callee 원문','implementation':'inner.node.json','signature':copy.deepcopy(sig),'arguments':{'value':{'input':'value'}}}],'entry':'body','edges':[{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'node':'body'},'count':{'node':'body','output':'count'}},'locals':[]};parent=box('inner',child,{'input':'amount'});parent['signature']=copy.deepcopy(sig);callee_graph.update(profile='sync-acyclic-nested-v1',nodes=[parent],entry='inner',edges=[{'from':'inner','port':'next','to':'exit:return'}],exits={'return':{'node':'inner'},'count':{'node':'inner','output':'count'}},locals=[])
 (f.project/'function.graph.json').write_text(json.dumps(callee_graph));defs2=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=fn+'Body',text=b.base.implementation_file.read_text(),bodyTarget='common',graph=callee_graph,definitionsOnly=True);assert defs2['state']=='node-definitions',defs2;h=next(v['definitionHash'] for v in defs2['nestedNodes'] if v['id']=='inner/body');(f.project/'inner.node.json').write_text(json.dumps({'schema':1,'node':'body','definitionHash':h,'source':'count=checked(value+1);return value; // 내부 callee 원문\r\n'}))
if callee:callee_child=copy.deepcopy(child);callee_sig=copy.deepcopy(sig)
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
 plan=({'before':old,'args':remap,'callers':{key:{k:row[k] for k in ['graph','node','hash']}|{'inputs':copy.deepcopy(b.inputs),'outputs':copy.deepcopy(b.outputs),'disconnect':{}} for key,row in preview['functionInputs'].items()},'implementations':{key:{k:row[k] for k in ['graph','node','argument','hash','before']}|{'value':{'input':'increment'}} for key,row in preview['functionInputUses'].items()},'outputs':{key:{k:row[k] for k in ['graph','node','name','hash','before']}|{'type':'bool','source':{'valueJson':'true'}} for key,row in preview['functionOutputs'].items() if row['name']=='return'},'bodies':{}} if callee else b.selections(preview));assert set(preview['functionInputs'])=={caller_id+'#left/'+leaf_id,caller_id+'#right/deep/'+leaf_id}
 for key,row in preview['functionInputs'].items():
  assert row['scope'] in ['left','right/deep'] and row['scopeSignature']==private_signature
  plan['callers'][key]['inputs']['text']={'valueJson':json.dumps('왼쪽' if row['scope']=='left' else '오른쪽')}
 if cpp:
  for name in ['left','right']:
   row=preview['functionBodies'][record_ids[name]];sig={'args':[{'name':'item','type':'long',**({'mode':'ref'} if forward else {})}],'return':'long'};plan['bodies'][record_ids[name]]={k:row[k] for k in ['hash','path','whole']}|{'beforeSignature':sig,'signature':sig,'contract':new,'text':edited_records[name]}
 if post_mode:
  for path in ['left','right/deep']:
   id=caller_id+'/postCall:'+path+'/'+leaf_id;row=preview['functionBodies'][id];plan['bodies'][id]={'wrapper':row['wrapper'],'contract':new,'text':post_source,'helpers':post_helpers}
 return plan

def request():
 r=n.request(new,remap);p={key:f.metadata(op,id=owner,function=fn,includeBlueprintTargets=True,units=r['units'],**({'functionSignature':new,'functionRemap':remap} if key=='functionBodies' else {})) for key,op in [('functionInputs','informationFunctionInputs'),('functionBodies','informationFunctionBodies'),('functionInputUses','informationFunctionInputUses'),('functionOutputs','informationFunctionOutputs')]};r['changes'][0]['mapping']=selections(p);return r

def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};g=json.loads(rows[caller_id]['draft']);assert g['locals']==root['locals'] and g['edges']==root['edges'] and g['exits']==root['exits'] and g['nodes'][2]==root['nodes'][2]
 for node in [0,1]:assert g['nodes'][node]['signature']==private_signature and g['nodes'][node]['arguments']==root['nodes'][node]['arguments']
 children=[g['nodes'][0]['graph'],g['nodes'][1]['graph']['nodes'][0]['graph']]
 for child,name,original in zip(children,['왼쪽','오른쪽'],[left,deep]):
  call=child['nodes'][0];assert call['signature']==new and call['arguments']=={'text':{'constant':name},'increment':{'input':'value'}}
  assert child['locals']==original['locals'] and child['edges']==original['edges']
  assert child['nodes'][1]['arguments']==({'item':{'input':'value'}} if forward else {'item':{'node':leaf_id,'output':'total'}}) and child['nodes'][1]['signature']==original['nodes'][1]['signature']
  if post_mode:assert call['postCall']['source']==post_source and call['postCall']['helpers']==post_helpers
  assert child['exits']['return']['binary']['operands'][1]=={'node':leaf_id,'output':'total'}
 for name,id in record_ids.items():assert json.loads(rows[id]['draft'] if id in rows else (f.project/(name+'.node.json')).read_text())['source']==(edited_records[name] if cpp and name in edited_records else record_sources[name])
 if callee:
  after=json.loads(rows[fn+'Body/body:common']['draft']);assert after['nodes'][0]['signature']==callee_sig and after['nodes'][0]['arguments']=={'value':{'input':'increment'}} and after['nodes'][0]['graph']==callee_child
  assert after['exits']=={'total':{'node':'inner','output':'count'},'return':{'constant':True}}
 assert all((f.project/p).read_bytes()==v for p,v in snapshot.items());return rows[owner]['atomicEditGroup']
