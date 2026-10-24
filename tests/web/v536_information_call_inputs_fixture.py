"""A real owned call consumes the edited root input; leaf source stays intact."""
import json
import v536_information_input_replacements_fixture as x
f,n,owner,fn=x.f,x.n,x.owner,x.fn
leaf=f.n+'InputLeaf'
leaf_source='function '+leaf+' (long amount) -> long {provide '+leaf+' with '+leaf+'Body;}'
for local,kind,text in [('InputLeaf','function',leaf_source),('InputLeafBody','implementation','implementation '+leaf+'Body for '+leaf+' (long amount) -> long {body common "InputLeaf.csbody";}')]:
 (f.project/(local+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' '+kind+' "'+local+'.celem";registry Confectory.Build.DotNet',1))
(f.project/'InputLeaf.csbody').write_text('return amount+3; // 다른 callee 원문 유지')
for target,path,record_path in [('common','function.graph.json','function.node.json')]+([('windows','function-windows.graph.json','function-windows.node.json')] if x.mode=='multi' else []):
 impl=f.project/(fn.split('::')[1]+'Body.celem');graph=json.loads((f.project/path).read_text());made=f.metadata('blueprintPrepareCall',id=fn+'Body',text=impl.read_text(),targetText=leaf_source,graph=graph,definition={'id':'inner','feature':leaf,'intent':'현재 입력을 사용하는 기존 호출','control':'next'})
 impl.write_text(made['implementation']);graph=made['graph'];next(v for v in graph['nodes'] if v['id']=='inner')['arguments']={'amount':{'input':'amount'}};next(v for v in graph['nodes'] if v['id']=='body')['arguments']['amount']={'node':'inner'};graph['entry']='inner';graph['edges'].append({'from':'inner','port':'next','to':'body'})
 source=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text();defs=f.metadata('featureBlueprintNodes',featureSource=source,graph=graph,featureContracts={leaf:leaf_source});assert defs['state']=='node-definitions',defs
 record=json.loads((f.project/record_path).read_text());record['definitionHash']=next(v['definitionHash'] for v in defs['nodes'] if v['id']=='body');(f.project/path).write_text(json.dumps(graph));(f.project/record_path).write_text(json.dumps(record))
x.snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def verify(checkpoint):
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};outer=json.loads(rows[n.caller+'Body/body:common']['draft'])['nodes'][0];assert outer['signature']==x.new and outer['arguments']==x.expected_caller()
 for target in ['common']+(['windows'] if x.mode=='multi' else []):
  g=json.loads(rows[fn+'Body/body:'+target]['draft']);inner=next(v for v in g['nodes'] if v['id']=='inner');code=next(v for v in g['nodes'] if v['id']=='body');assert inner['feature']==leaf and inner['signature']=={'args':[{'name':'amount','type':'long'}],'return':'long'} and inner['arguments']=={'amount':x.expected_callee()};assert code['signature']==x.old and code['arguments']=={'amount':{'node':'inner'},'count':{'input':'count'}};assert g['entry']=='inner' and {'from':'inner','port':'next','to':'body'} in g['edges'];assert json.loads(rows[fn+'Body/body:'+target+'/node:body']['draft'])['source']==n.record['source']
 body=rows[fn+'Body']['draft'];imports=f.metadata('inspect',text=body)['relations']['edges'];assert any(v['role']=='import' and v['target']==leaf for v in imports),imports
 for path in ['InputLeaf.celem','InputLeafBody.celem','InputLeaf.csbody']:assert (f.project/path).read_bytes()==x.snapshot[path]
 ids=rows[owner]['atomicEditGroup'];required={owner,fn,fn+'Body',fn+'Body/body:common',n.caller+'Body/body:common'}
 if x.kind!='mixed':required.add(n.caller+'Body')
 else:
  assert (f.project/'CallerBody.celem').read_bytes()==x.snapshot['CallerBody.celem']
  if n.caller+'Body' in rows:assert rows[n.caller+'Body']['draft']==x.snapshot['CallerBody.celem'].decode()
 assert required<=set(ids);return ids
x.verify=verify
