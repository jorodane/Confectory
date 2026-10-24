"""Used ordinary root inputs with explicit callee/caller replacements only."""
import copy,json
import v536_information_function_contracts_native as n
f,d,owner,fn=n.f,n.a.d,n.owner,n.fn
mode=n.a.mode
kind='type' if mode.startswith('type') else 'mixed' if mode.startswith('mixed') else 'delete'
old={'args':[{'name':'amount','type':'long'},{'name':'count','type':'long'}],'return':'long'}
new={'args':([{'name':'amount','type':'string'}] if kind=='type' else [])+[{'name':'count','type':'long'}]+([{'name':'fresh','type':'long'}] if kind=='mixed' else []),'return':'long'}
mapping={'before':old,'args':{'amount':None,'count':'count'}}
if mode=='multi':
 p=f.project/(fn.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace('}','blueprint windows "function-windows.graph.json";}'))
 g=json.loads((f.project/'function.graph.json').read_text());next(r for r in g['nodes'] if r['id']=='body')['implementation']='function-windows.node.json'
 source=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text();defs=f.metadata('featureBlueprintNodes',featureSource=source,graph=g);rec={**n.record,'definitionHash':next(r['definitionHash'] for r in defs['nodes'] if r['id']=='body')};(f.project/'function-windows.graph.json').write_text(json.dumps(g));(f.project/'function-windows.node.json').write_text(json.dumps(rec))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def selections(preview):
 callers={}
 for key,t in preview['functionInputs'].items():
  values={'count':'count'}
  if kind=='type':values['amount']={'valueJson':json.dumps('새 한글 값',ensure_ascii=False)}
  if kind=='mixed':values['fresh']='amount'
  callers[key]={k:t[k] for k in ['graph','node','hash']}|{'inputs':values,'disconnect':{} if kind=='mixed' else {'amount':t['bindings']['amount']}}
 implementations={}
 for key,t in preview['functionInputUses'].items():
  if t['input']!='amount':continue
  value={'input':'count' if kind=='type' else 'fresh'} if kind in ['type','mixed'] else {'valueJson':'9223372036854775806'}
  implementations[key]={k:t[k] for k in ['graph','node','argument','hash','before']}|{'value':value}
 return mapping|{'callers':callers,'implementations':implementations}
def expected_caller():
 return {'count':{'input':'second'}}|({'amount':{'constant':'새 한글 값'}} if kind=='type' else {'fresh':{'input':'first'}} if kind=='mixed' else {})
def expected_callee():return {'input':'count' if kind=='type' else 'fresh'} if kind in ['type','mixed'] else {'constant':9223372036854775806}
def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
 graph=json.loads(rows[n.caller+'Body/body:common']['draft']);assert graph['nodes'][0]['signature']==new and graph['nodes'][0]['arguments']==expected_caller()
 for target in ['common']+(['windows'] if mode=='multi' else []):
  graph=json.loads(rows[fn+'Body/body:'+target]['draft']);node=next(r for r in graph['nodes'] if r['id']=='body');assert node['signature']==old and node['arguments']=={'amount':expected_callee(),'count':{'input':'count'}}
  assert json.loads(rows[fn+'Body/body:'+target+'/node:body']['draft'])['source']==n.record['source']
 ids=rows[owner]['atomicEditGroup'];required={owner,fn,fn+'Body',fn+'Body/body:common',n.caller+'Body/body:common'}
 if kind!='mixed':required.add(n.caller+'Body')
 else:
  assert (f.project/'CallerBody.celem').read_bytes()==snapshot['CallerBody.celem']
  if n.caller+'Body' in rows:assert rows[n.caller+'Body']['draft']==snapshot['CallerBody.celem'].decode()
 assert required<=set(ids)
 return ids
