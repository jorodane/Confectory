"""Two explicit forwarding entries, including a depth2 private identity chain."""
import copy,json,sys
import v536_information_nested_fixture as base
f,d,n,owner,fn,caller,mode=base.f,base.d,base.n,base.owner,base.fn,base.caller,base.mode
b=base.b
old,new,selected,remap,edited=b.old,b.new,b.selected,b.remap,b.edited
body_id,body_path=b.body_id,b.body_path
scenario,chain=b.scenario,b.chain
cpp=False;post_mode=None;code_control=None;forward=False;callee=False
code_helpers='';edited_records={};record_helpers={};post_source='';post_helpers='';record_ids={'untouched':base.record_ids['untouched']};record_sources=base.record_sources
caller_id=base.caller_id;leaf_id=base.leaf_id
sig={'args':[{'name':'value','type':'long'},{'name':'stored','type':'long','mode':'out'}],'return':'long'}
inner={'args':[{'name':'innerValue','type':'long'},{'name':'innerStored','type':'long','mode':'out'}],'return':'long'}
def graph(signature,kind='call',child=None):
 node=copy.deepcopy(base.original_call) if kind=='call' else {'id':'deep','kind':'graph','graph':child,'intent':'직결 내부 계층'}
 node.update(control='next',forwardCallerStorage=True,signature=copy.deepcopy(old if kind=='call' else inner),arguments={('amount' if kind=='call' else 'innerValue'):{'input':signature['args'][0]['name']}})
 return {'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[node],'entry':node['id'],'edges':[{'from':node['id'],'port':'next','to':'exit:return'}],'exits':{'return':{'node':node['id']},signature['args'][1]['name']:None},'locals':[{'id':'kept','name':'독립 값','type':'long','initial':{'constant':9223372036854775806}}]}
left=graph(sig);deep=graph(inner);right=graph(sig,'graph',deep);root=copy.deepcopy(base.root)
for index,child in enumerate([left,right]):root['nodes'][index]['signature']=copy.deepcopy(sig);root['nodes'][index]['graph']=child
multi='multi' in sys.argv[4:]
linked='linked' in sys.argv[4:]
if linked:assert multi;root['nodes'][1]['arguments']={'value':{'node':'left'}}
computed='computed' in sys.argv[4:] or multi
post_keys=[]
if computed:
 new['return']='long';selected['return']='long';edited='nativeTotal=checked(message.Length+delta);return checked(nativeTotal+1); // 직접 본문·계산 보존\r\n';b.edited=edited;b.outputs['return']='return'
 for child,name in [(left,'left'),(deep,'right')]:
  code=copy.deepcopy(base.left['nodes'][1]);code['implementation']=name+'.node.json';code['arguments']={'item':{'binary':{'operator':'+','type':'long','operands':[{'node':leaf_id},{'input':child['nodes'][0]['arguments']['amount']['input']}]}}};child['nodes'].append(code);child['edges']=[{'from':leaf_id,'port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}];child['exits']['return']={'node':'body'};child['locals'].append({'id':'live','name':'입력 별칭','type':'long','source':{'input':child['nodes'][0]['arguments']['amount']['input']}})
 right['exits']['return']={'binary':{'operator':'+','type':'long','operands':[{'node':'deep'},{'input':'value'}]}}
 if multi:
  for child in [left,deep]:
   child['nodes'][0]['intent']='첫 번째 전달 호출';other=copy.deepcopy(child['nodes'][0]);other.update(id=leaf_id+'2',intent='두 번째 전달 호출');child['nodes'].append(other);child['edges']=[{'from':leaf_id,'port':'next','to':'body'},{'from':'body','port':'next','to':leaf_id+'2'},{'from':leaf_id+'2','port':'next','to':'exit:return'}];child['exits']['return']={'binary':{'operator':'+','type':'long','operands':[{'node':'body'},{'node':leaf_id+'2','output':'count'}]}}
  tail=copy.deepcopy(left['nodes'][0]);tail.update(id='invokeOuter',intent='상위 전달 호출',arguments={'amount':{'input':'value'}});right['nodes'].append(tail);right['edges']=[{'from':'deep','port':'next','to':'invokeOuter'},{'from':'invokeOuter','port':'next','to':'exit:return'}];right['exits']['return']={'binary':{'operator':'+','type':'long','operands':[right['exits']['return'],{'node':'invokeOuter'}]}}
  if 'post' in sys.argv[4:]:
   post_mode='post';post_source='return Read(@context.@total); // 명시한 다중 후처리\r\n';post_helpers='private static long Read(long value){return value;} // 보조 원문\r\n';wrapper=f.metadata('blueprintCallAfter',functionText=b.base.function_file.read_text(),source='return @context.@count;')
   for child,path in [(left,'left'),(deep,'right/deep'),(right,'right')]:
    child['profile']='sync-acyclic-methods-v1';node=child['nodes'][-1];node['postCall']={k:wrapper[k] for k in ['contractHash','source','helpers']};post_keys.append(path+'/'+node['id'])
 (f.project/'caller.graph.json').write_text(json.dumps(root,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=caller+'Body',text=(f.project/'CallerBody.celem').read_text(),bodyTarget='common',graph=root,definitionsOnly=True);assert defs['state']=='node-definitions',defs
 for name,path in [('left','left/body'),('right','right/deep/body')]:
  h=next(row['definitionHash'] for row in defs['nestedNodes'] if row['id']==path);(f.project/(name+'.node.json')).write_text(json.dumps({'schema':1,'node':'body','definitionHash':h,'source':base.record_sources[name]},ensure_ascii=False))
 record_ids.update(left=base.record_ids['left'],right=base.record_ids['right'])
(f.project/'caller.graph.json').write_text(json.dumps(root,ensure_ascii=False));snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
 plan=b.selections(preview);expected={caller_id+'#left',caller_id+'#right'}|({caller_id+'#left/'+leaf_id,caller_id+'#right/deep/'+leaf_id,caller_id+'#right/deep'} if computed else set())
 if multi:expected|={caller_id+'#left/'+leaf_id+'2',caller_id+'#right/deep/'+leaf_id+'2',caller_id+'#right/invokeOuter'}
 assert set(preview['functionInputs'])==expected
 for path in post_keys:
  id=caller_id+'/postCall:'+path;row=preview['functionBodies'][id];plan['bodies'][id]={'wrapper':row['wrapper'],'contract':new,'text':post_source,'helpers':post_helpers}
 for key,row in preview['functionInputs'].items():
  if row.get('privateForwardOutputs'):
   plan['callers'][key]={k:row[k] for k in ['graph','node','hash']}|{'inputs':{},'disconnect':{},'outputs':{'return':'return' if row['node']=='right/deep' else 'total',('innerStored' if row['node']=='right/deep' else 'count'):('return' if multi and row['node'].endswith(leaf_id+'2') else 'total')}};continue
  assert row['privateScope'] and row['before']==sig and row['functionPins']=={'amount':'value','count':'stored'}
  assert len(row['scopeChain'])==(1 if row['node']=='left' else 2)
  plan['callers'][key]={k:row[k] for k in ['graph','node','hash']}|{'inputs':{'text':{'valueJson':json.dumps('왼쪽 부모' if row['node']=='left' else '오른쪽 부모')},'increment':'value'},'outputs':{'return':'total' if linked and row['node']=='left' else 'return' if computed else 'total','stored':None if linked and row['node']=='left' else 'total'},'disconnect':{}}
 return plan

def request():
 r=n.request(new,remap);p={key:f.metadata(op,id=owner,function=fn,includeBlueprintTargets=True,units=r['units'],functionSignature=new,functionRemap=remap) for key,op in [('functionInputs','informationFunctionInputs'),('functionBodies','informationFunctionBodies')]};r['changes'][0]['mapping']=selections(p);return r

def expected_multi():
 g=copy.deepcopy(root)
 def value(v,child_outputs,input_name):
  if isinstance(v,dict):
   if set(v)=={'input'}:return {'input':{'value':'increment','innerValue':'increment'}[v['input']]}
   if v.get('node') in child_outputs:
    result=copy.deepcopy(v);to=child_outputs[v['node']][v.get('output','return')]
    if to=='return':result.pop('output',None)
    else:result['output']=to
    return result
   return {k:(copy.deepcopy(x) if k=='constant' else value(x,child_outputs,input_name)) for k,x in v.items()}
  if isinstance(v,list):return [value(x,child_outputs,input_name) for x in v]
  return v
 def frame(node,path):
  child=node['graph'];maps={}
  for row in child['nodes']:
   if row.get('forwardCallerStorage'):
    maps[row['id']]={'return':'return' if row['kind']=='graph' else 'total',('innerStored' if row['kind']=='graph' else 'count'):'return' if row['id']==leaf_id+'2' else 'total'}
    if row['kind']=='graph':frame(row,path+'/'+row['id'])
    row['signature']=copy.deepcopy(new);row['arguments']={a['name']:{'input':a['name']} for a in new['args'] if a.get('mode')!='out'}
    if 'postCall' in row:
     # Hash is checked from the final function declaration below; text/helpers
     # and all noncontract wrapper fields remain exact in the expected graph.
     row['postCall']['source']=post_source;row['postCall']['helpers']=post_helpers
  # Nonforwarded values can refer to later nodes too. Use the complete map once.
  for row in child['nodes']:
   if not row.get('forwardCallerStorage'):row['arguments']=value(next(r for r in (left if path=='left' else deep if path=='right/deep' else right)['nodes'] if r['id']==row['id'])['arguments'],maps,'')
  child['locals']=[{k:(value(v,maps,'') if k=='source' else copy.deepcopy(v)) for k,v in row.items()} for row in child['locals']];child['exits']={('total' if k in ['stored','innerStored'] else k):value(v,maps,'') for k,v in child['exits'].items()}
  if linked and path=='left':
   child['exits']={'total':child['exits']['return'],'return':None}
   for edge in child['edges']:
    if edge['to']=='exit:return':edge['to']='exit:total'
  node['signature']=copy.deepcopy(new)
 for i,path in enumerate(['left','right']):
  frame(g['nodes'][i],path);g['nodes'][i]['arguments']={'text':{'constant':'왼쪽 부모' if i==0 else '오른쪽 부모'},'increment':{'input':'first' if i==0 else 'second'}}
 if linked:
  g['nodes'][1]['arguments']['increment']={'node':'left','output':'total'};g['exits']['return']['binary']['operands'][0]={'node':'left','output':'total'}
 return g

def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};g=json.loads(rows[caller_id]['draft'])
 if multi:
  expected=expected_multi()
  for path in post_keys:
   def find(tree,path):
    for part in path.split('/'):
     node=next(n for n in tree['nodes'] if n['id']==part);tree=node.get('graph')
    return node
   actual=find(g,path);before=find(expected,path);prepared=f.metadata('blueprintCallAfter',functionText=rows[fn]['draft'],source=post_source,helpers=post_helpers);before['postCall']['contractHash']=prepared['contractHash']
   assert actual['postCall']['contractHash']==prepared['contractHash']
  assert g==expected,(g,expected);assert json.loads(rows[body_id]['draft'])['source']==edited;assert all((f.project/p).read_bytes()==v for p,v in snapshot.items());return rows[owner]['atomicEditGroup']
 assert g['nodes'][2]==root['nodes'][2] and g['locals']==root['locals'] and g['edges']==root['edges']
 for i,name in enumerate(['왼쪽 부모','오른쪽 부모']):
  node=g['nodes'][i];assert node['signature']==new and node['arguments']=={'text':{'constant':name},'increment':{'input':'first' if i==0 else 'second'}}
  while True:
   child=node['graph'];target=child['nodes'][0];assert target['signature']==new and target['arguments']=={'text':{'input':'text'},'increment':{'input':'increment'}} and target['forwardCallerStorage']
   if not computed:assert child['exits']=={'return':{'node':target['id']},'total':None} and child['locals']==left['locals']
   elif target['kind']=='call':
    assert child['nodes'][1]['arguments']=={'item':{'binary':{'operator':'+','type':'long','operands':[{'node':target['id'],'output':'total'},{'input':'increment'}]}}};assert child['locals'][-1]['source']=={'input':'increment'};assert child['exits']=={'return':{'node':'body'},'total':None}
   else:assert child['exits']['return']=={'binary':{'operator':'+','type':'long','operands':[{'node':'deep'},{'input':'increment'}]}}
   if target['kind']=='call':break
   node=target
  assert g['exits']['return']['binary']['operands'][i]==({'node':'left' if i==0 else 'right'} if computed else {'node':'left' if i==0 else 'right','output':'total'})
 assert json.loads(rows[body_id]['draft'])['source']==edited
 assert all((f.project/p).read_bytes()==v for p,v in snapshot.items());return rows[owner]['atomicEditGroup']
