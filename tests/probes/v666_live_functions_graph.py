"""Existing property nodes retain opaque caller function identities."""
import hashlib,json,subprocess

def prepare(p,n,r,d,author,dotnet,write):
 model='Confectory.ObjectModel';fn=n+'Calc';body=n+'CalcBody';owner=n+'Node';field=next(row for row in d['fields']if row['name']=='Apply')
 source='function '+fn+' (object target,object replacement) -> object {provide '+fn+' with '+body+';}'
 write('Calc','function',source)
 reader='fg_call_'+hashlib.sha256((model+'::Read').encode()).hexdigest()[:24];setter='fg_call_'+hashlib.sha256((model+'::Set').encode()).hexdigest()[:24]
 write('CalcBody','implementation','implementation '+body+' for '+fn+' (object target,object replacement) -> object {import '+model+'::Read as '+reader+' (object,string,string,string) -> object;import '+model+'::Set as '+setter+' (object,string,string,string,object) -> void;blueprint common "Calc.graph.json";}')
 manifest=p/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Calc function "Calc.celem";element CalcBody implementation "CalcBody.celem";registry Confectory.Build.DotNet',1))
 path=p/'MainBody.celem';path.write_text(path.read_text().replace('body common','import '+fn+' as Calc (object,object) -> object;body common',1))
 def metadata(operation,**data):
  proc=subprocess.run([dotnet,str(author)],input=json.dumps(dict(operation=operation,**data)),text=True,capture_output=True,check=True);reply=json.loads(proc.stdout);assert reply['ok'],reply;return reply['result']
 graph=metadata('blueprintPrepareFeature',id=fn,text=source.replace('provide '+fn+' with '+body+';',''),implementation=body,graphPath='Calc.graph.json',nodePath='consume.node.json')['graph'];graph['profile']='sync-acyclic-property-set-v1';graph['entry']='before'
 sig=lambda ret,args:dict(args=[dict(name=name,type=kind)for name,kind in args],**{'return':ret})
 def prop(id,write=False):return dict(id=id,kind='property-set'if write else'property',control='next',intent='실제 함수 객체 '+id,propertyOwner=owner,field='Apply',fieldContractHash=field['hash'],signature=sig('void'if write else'object',[('target','object')]+([('value','object')]if write else[])),arguments=dict(target=dict(input='target'))|({'value':dict(input='replacement')}if write else{}))
 graph['nodes']=[prop('before'),prop('write',True),prop('after'),dict(id='consume',kind='code',control='next',intent='함수 객체 동일성 보존',signature=sig('object',[('before','object'),('after','object'),('replacement','object')]),arguments=dict(before=dict(node='before'),after=dict(node='after'),replacement=dict(input='replacement')),implementation='consume.node.json')]
 graph['edges']=[dict(**{'from':a},port='next',to=b)for a,b in [('before','write'),('write','after'),('after','consume'),('consume','exit:done')]];graph['exits']=dict(done=dict(node='consume'))
 contracts={model+'::'+name:(r/'packs/object-model'/(name+'.celem')).read_text()for name in ['Read','Set']}
 definitions=metadata('featureBlueprintNodes',featureSource=source,graph=graph,propertyContracts={owner:d},featureContracts=contracts);assert definitions['state']=='node-definitions',definitions
 (p/'Calc.graph.json').write_text(json.dumps(graph,ensure_ascii=False));(p/'consume.node.json').write_text(json.dumps(dict(schema=1,node='consume',definitionHash=next(v for v in definitions['nodes']if v['id']=='consume')['definitionHash'],source='if(!Object.ReferenceEquals(after,replacement))throw new Exception("live function identity lost");return before; // opaque original handle 😀'),ensure_ascii=False))
 return 'if(!Object.ReferenceEquals(calls.Calc.Invoke(receiver,source.Apply),source.Apply)||!Object.ReferenceEquals(calls.Calc.Invoke(receiver,source.Apply),source.Apply))throw new Exception("repeated Blueprint property call lost handle");'
