"""직접 소유 private graph의 명시적 경로·혼합 profile·동일 local ID fixture."""
import copy,json,sys
import v666_node_internal_api as x
f=x.f;root=x.graph;feature=x.feature;implementation=x.impl
argument=next((a.split('=',1)[1] for a in sys.argv[3:] if a.startswith('--depth=')),'2');depth=int(argument);assert 1<=depth<=8
parts=['frame'+str(i) for i in range(depth)];path='/'.join(parts);parent=root+''.join('/graph:'+p for p in parts);child=parent+'/graph:calculate';original_id=root+'/node:'+path.replace('/','/node:')+'/node:calculate';leaf=original_id+'/node:body'
signature={'args':[{'name':'amount','type':'long'}],'return':x.return_type}
base=copy.deepcopy(x.g);base.pop('feature',None);base.pop('contractHash',None);base['profile']='sync-acyclic-methods-v1'
def frame(name,graph):return {'id':name,'kind':'graph','control':'next','intent':'직접 소유 frame '+name,'signature':copy.deepcopy(signature),'arguments':{'amount':{'input':'amount'}},'graph':copy.deepcopy(graph)}
def enclosing(name,graph):
 p=copy.deepcopy(base);p.update(profile='sync-acyclic-nested-v1',entry=name,nodes=[frame(name,graph)],edges=[{'from':name,'port':'next','to':'exit:return'}],exits={'return':{'node':name}});return p
inner=base
for name in reversed(parts):inner=enclosing(name,inner)
graph=inner;graph['feature']=x.g['feature'];graph['contractHash']=x.g['contractHash']
peer=copy.deepcopy(base);peer['nodes'][0]['implementation']='Peer.node.json';graph['nodes'].append(frame('peer',peer))
context={'implementation':implementation,'feature':feature,'signature':signature,'imports':{}}
definitions=f.metadata('featureBlueprintNodes',featureSource=x.function,implementationContext=context,bodyTarget='common',graph=graph)
selected=next(row for row in definitions['nestedNodes'] if row['id']==path+'/calculate');record=copy.deepcopy(x.record);record['definitionHash']=selected['definitionHash'];peer_record=copy.deepcopy(record);peer_record['definitionHash']=next(row for row in definitions['nestedNodes'] if row['id']=='peer/calculate')['definitionHash'];peer_record['source']='return amount+1000;'
(f.project/'Flow.graph.json').write_text(json.dumps(graph,ensure_ascii=False));(f.project/'Flow.node.json').write_text(json.dumps(record,ensure_ascii=False));(f.project/'Peer.node.json').write_text(json.dumps(peer_record,ensure_ascii=False));x.physical={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':parent,**kw},ok)['result'].get('result')
def read(id=parent):return rpc('read',id=id)
def request(data,nonce=None,source=None):
 r=x.request(data,nonce,source);r['id']=parent;row=next(n for n in data['nodes'] if n['id']=='calculate');observed=next(s for s in data['sources'] if s['id']==row['sourceId']);r['edits'][0]['definition']['binding']={'graph':parent,'root':root,'node':'calculate','source':row['sourceId'],'definitionHash':row['definitionHash'],'sourceHash':observed['hash']};return r

def at(document,parts=parts):
 result=document
 for name in parts:result=next(n for n in result['nodes'] if n['id']==name)['graph']
 return result

def assert_wrapper(wrapper):
 before=next(row for row in at(graph)['nodes'] if row['id']=='calculate')
 assert {k:v for k,v in wrapper.items() if k not in ['kind','graph','retainedCode']}=={k:v for k,v in before.items() if k not in ['kind','implementation']}
 assert wrapper['retainedCode']['definition']==before
 body=next(row for row in wrapper['graph']['nodes'] if row['id']=='body')
 stored=json.loads((f.project/body['implementation']).read_text())
 assert stored['helpers']==record['helpers']
