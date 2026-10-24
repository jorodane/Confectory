"""Owned ordinary scalar input closure; temporary project and unchanged code."""
import copy,json
import v536_information_function_contracts_native as n
f,d,owner,fn=n.f,n.a.d,n.owner,n.fn
mode=n.a.mode
old={'args':[{'name':'amount','type':'long'},{'name':'count','type':'long'}],'return':'long'}
extra={'name':'extra','type':'long'}
new=copy.deepcopy(old)
if mode.startswith('delete'):
 old['args'].append(extra)
 function=f.project/('elements/'+fn.split('::')[1]+'.celem')
 function.write_text(function.read_text().replace('long count)', 'long count,long extra)'))
 impl=f.project/(fn.split('::')[1]+'Body.celem')
 impl.write_text(impl.read_text().replace('long count)', 'long count,long extra)'))
 g=json.loads((f.project/'function.graph.json').read_text())
 g['contractHash']=f.metadata('blueprintPrepareFeature',id=fn,text=function.read_text().replace('provide '+fn+' with '+fn+'Body;',''),implementation=fn+'Body',graphPath='function.graph.json',nodePath='function.node.json')['graph']['contractHash']
 desc=f.metadata('featureBlueprintNodes',featureSource=function.read_text(),graph=g)
 assert desc['state']=='node-definitions',desc
 (f.project/'function.graph.json').write_text(json.dumps(g))
 rec=json.loads((f.project/'function.node.json').read_text())
 rec['definitionHash']=next(row['definitionHash'] for row in desc['nodes'] if row['id']=='body')
 (f.project/'function.node.json').write_text(json.dumps(rec))
 cp=f.project/'CallerBody.celem'
 cp.write_text(cp.read_text().replace('(long, long) -> long','(long, long, long) -> long'))
 g=json.loads((f.project/'caller.graph.json').read_text())
 g['nodes'][0]['signature']=copy.deepcopy(old)
 g['nodes'][0]['arguments']['extra']={'constant':9223372036854775806}
 (f.project/'caller.graph.json').write_text(json.dumps(g))
else:new['args'].append(extra)
mapping={'before':old,'args':{a['name']:a['name'] if any(b['name']==a['name'] for b in new['args']) else None for a in old['args']}}
if mode=='two':
 p=f.project/'caller.graph.json';g=json.loads(p.read_text());node=copy.deepcopy(g['nodes'][0]);node['id']='invoke2';g['nodes'].append(node);g['edges']=[{'from':'invoke','port':'next','to':'invoke2'},{'from':'invoke2','port':'next','to':'exit:return'}];g['exits']['return']={'node':'invoke2'};p.write_text(json.dumps(g))
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def plans(targets):
 result={}
 for key,t in targets.items():
  values={a['name']:a['name'] for a in new['args'] if a['name']!='extra'}
  if not mode.startswith('delete'):values['extra']={'valueJson':'9223372036854775806'}
  if mode=='binding':values['count']={'valueJson':'7'};values['extra']='count'
  result[key]={k:t[k] for k in ['graph','node','hash']}|{'inputs':values,'disconnect':{'extra':t['bindings']['extra']} if mode.startswith('delete') else {}}
 return result
