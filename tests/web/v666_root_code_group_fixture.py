"""One explicit independent root code/helper plan and one ordinary native body."""
import copy,json,hashlib
import v666_private_body_group_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
b=_base
whole_node=whole_graph+'/node:body';private_node='body'
code_signature=copy.deepcopy(code_signature);code_signature['args'].append(dict(name='rootResult',type='long',mode='out'));code_signature['return']='void'
graph=copy.deepcopy(b.graph);code=copy.deepcopy(graph['nodes'][1]['graph']['nodes'][0]);code['signature']=copy.deepcopy(code_signature);code['arguments']={a['name']:{'input':v['name']}for a,v in zip(code_signature['args'],old['args'])}
graph.update(profile='sync-acyclic-methods-v1',nodes=[graph['nodes'][0],code],edges=[{'from':'preserve','port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}],exits={'return':{'node':'body','output':'rootResult'}})
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode())
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=(f.project/impl_path).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
sources[whole_function]='rootResult=Keep(firstNative+secondNative); // root code 원문 😀\n';selected[whole_function]='rootResult=Edit(firstNative-secondNative); // 명시 root code 편집 😀\n'
record=json.loads(b.whole_record);record.update(definitionHash=next(v['definitionHash']for v in defs['nodes']if v['id']=='body'),source=sources[whole_function]);(f.project/node_path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
extra_record=json.loads(b.extra_bytes);extra_record['definitionHash']=next(v['definitionHash']for v in defs['nodes']if v['id']=='preserve');extra_bytes=(json.dumps(extra_record,ensure_ascii=False,indent=2)+'\r\n').encode();(f.project/extra_path).write_bytes(extra_bytes);extra_mtime=(f.project/extra_path).stat().st_mtime_ns
whole_record=(f.project/node_path).read_bytes();whole_flow=(f.project/graph_path).read_bytes();snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
for _key in ['whole_node','private_node','graph','whole_record','whole_flow','extra_record','extra_bytes','extra_mtime','snapshot']:setattr(b,_key,globals()[_key])
b.b.snapshot=snapshot;b.b._prior.snapshot=snapshot

def request():
 r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1];r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(old)))
 for index,row in enumerate(r['changes']):
  row.update(name=labels[index],description='');bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id'],includeBlueprintTargets=True);key=whole_node if index==0 else row['id']+'Body/body:common';unit=r['units'][key]
  if index==0:
   available=key in bodies
   if mode not in ['reproduce','prior-ui']:assert available,bodies
   if available:assert bodies[key]['sourceKind']=='scoped-code-csharp'and bodies[key]['node']=='body'and bodies[key]['helperEditor'],bodies[key]
   plan=dict(hash=hashlib.sha256(unit['draft'].encode()).hexdigest(),path=unit['path'],beforeSignature=copy.deepcopy(code_signature),signature=copy.deepcopy(code_signature),contract=copy.deepcopy(old),text=selected[row['id']],helpers=selected_helpers,whole=dict(graph=whole_graph,hash=hashlib.sha256(r['units'][whole_graph]['draft'].encode()).hexdigest(),node='body',returnNode=None))
   if available:assert plan['whole']==bodies[key]['whole']and plan['hash']==bodies[key]['hash']
  else:
   body=bodies[key];assert body['sourceKind']=='csharp';plan={k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native),signature=copy.deepcopy(native),contract=copy.deepcopy(old),text=selected[row['id']])
  row['mapping']=dict(before=copy.deepcopy(old),args={'amount':'amount','count':'count'},bodies={key:plan})
 return r

def _sync():b.selected_helpers=selected_helpers
def verify_rows(rows):_sync();return b.verify_rows(rows)
def verify(checkpoint):_sync();return b.verify(checkpoint)
def verify_live():
 _sync();b.verify_live();f.checked('root code/helper plan retains its own ABI, original root bindings/graph, other independent code bytes+mtime and executes20')
