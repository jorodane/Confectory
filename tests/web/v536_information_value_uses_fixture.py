"""Five semantic use positions in one owned graph; all copies are fixtures."""
import copy,json
import v536_information_call_inputs_fixture as c
x,f,n,owner,fn=c.x,c.f,c.n,c.owner,c.fn
binary=lambda op,a,b:{'binary':{'operator':op,'operands':[a,b]}}
original_graphs={}
for target,path,record in [('common','function.graph.json','function.node.json')]+([('windows','function-windows.graph.json','function-windows.node.json')] if x.mode=='multi' else []):
 g=json.loads((f.project/path).read_text());g['profile']='sync-acyclic-alias-locals-v1'
 g['locals']=[{'id':'root_alias','name':'기존 입력 저장소','type':'long','source':{'input':'amount'}},{'id':'kept','name':'보존할 정확한 값','type':'long','initial':{'constant':9223372036854775805}}]
 inner=next(v for v in g['nodes'] if v['id']=='inner');body=next(v for v in g['nodes'] if v['id']=='body');export={'id':'assigned','kind':'export','control':'next','intent':'원래 출력에 대입','output':'return','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':None}};g['nodes'].append(export)
 inner['arguments']['amount']=binary('+',{'input':'amount'},{'input':'count'})
 body['arguments']={'amount':binary('+',{'input':'amount'},{'node':'inner'}),'count':{'local':'root_alias'}}
 export['arguments']['value']=binary('-',{'input':'amount'},{'constant':1})
 g['exits']['return']=binary('+',{'input':'amount'},{'input':'count'});g['edges']=[{'from':'inner','port':'next','to':'body'},{'from':'body','port':'next','to':'assigned'},{'from':'assigned','port':'next','to':'exit:return'}]
 source=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text();impl=(f.project/(fn.split('::')[1]+'Body.celem')).read_text();defs=f.metadata('featureBlueprintNodes',featureSource=source,graph=g,featureContracts={c.leaf:c.leaf_source});assert defs['state']=='node-definitions',defs
 r=json.loads((f.project/record).read_text());r['definitionHash']=next(v['definitionHash'] for v in defs['nodes'] if v['id']=='body');(f.project/path).write_text(json.dumps(g));(f.project/record).write_text(json.dumps(r));original_graphs[target]=copy.deepcopy(g)
x.snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def selections(preview):
 result=original_selections(preview)
 for key,t in preview['functionInputUses'].items():
  if 'amount' in t.get('inputs',[t['input']]) and t.get('storageOnly'):result['implementations'][key]={k:t[k] for k in ['graph','node','argument','hash','before']}|{'value':{'input':'count'}}
 return result
original_selections=x.selections;x.selections=selections
def extra_cases(request):
 cases=[];plans=request['declaration']['changes'][0]['mapping']['implementations'];alias=next(k for k in plans if '#$alias:' in k);exit=next(k for k in plans if '#$exit:' in k)
 for key,field,value in [(alias,'value',{'valueJson':'4'}),(alias,'value',{'input':'missing'}),(exit,'before','{"input":"amount"}')]:
  bad=copy.deepcopy(request);bad['declaration']['changes'][0]['mapping']['implementations'][key][field]=value;cases.append(bad)
 for key in [alias,exit]:
  bad=copy.deepcopy(request);del bad['declaration']['changes'][0]['mapping']['implementations'][key];cases.append(bad)
 return cases
x.extra_cases=extra_cases
def inspect_picker(modal):
 uses=modal.locator('section[data-abi-target^="use:"]');assert uses.count()==5
 alias=modal.locator('section[data-abi-target*="#$alias:"]');assert alias.locator('[data-abi-input=source] option[value=value]').count()==0
 assert '기존 저장소: 입력 amount' in alias.locator('[data-abi-original]').inner_text()
 assert any('(입력 amount + 입력 count)' in row.inner_text() for row in uses.locator('[data-abi-original]').all())
x.inspect_picker=inspect_picker
def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};outer=json.loads(rows[n.caller+'Body/body:common']['draft'])['nodes'][0];assert outer['signature']==x.new and outer['arguments']==x.expected_caller()
 for target,old in original_graphs.items():
  g=json.loads(rows[fn+'Body/body:'+target]['draft']);nodes={v['id']:v for v in g['nodes']}
  for before in old['nodes']:
   node=nodes[before['id']];assert node['signature']==before['signature']
   if before['id'] in ['inner','body']:assert node['arguments']['amount']==x.expected_callee()
   if before['kind']=='export':assert node['arguments']['value']==x.expected_callee()
  assert nodes['body']['arguments']['count']=={'local':'root_alias'} and g['exits']['return']==x.expected_callee()
  assert g['locals']==[{**old['locals'][0],'source':{'input':'count'}},old['locals'][1]];assert g['entry']==old['entry'] and g['edges']==old['edges']
  assert json.loads(rows[fn+'Body/body:'+target+'/node:body']['draft'])['source']==n.record['source']
 for path in ['InputLeaf.celem','InputLeafBody.celem','InputLeaf.csbody']:assert (f.project/path).read_bytes()==x.snapshot[path]
 ids=rows[owner]['atomicEditGroup'];assert {owner,fn,fn+'Body',fn+'Body/body:common',n.caller+'Body/body:common'}<=set(ids)
 return ids
x.verify=verify
