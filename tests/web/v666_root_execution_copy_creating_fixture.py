"""A sealed new copy returns an existing public branch on its first Save."""
import copy,json,uuid
import v666_root_execution_fixture as x
f=x.f;f.manifest=x.manifest;owner=f.n+'FreeInfo';module=f.n+'M12CreatingRules';implementation=f.n+'M12CreatingCopy';graph=implementation+'/body:common'
units={}
for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
prepared=f.metadata('blueprintRootExecution',namespace=f.n[:-2],id=x.graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}))
for row in prepared['units'].values():(f.project/row['path']).write_text(row['draft'])
(f.project/'FreeInfo.celem').write_text('schema '+owner+' {module '+module+';}');(f.project/'M12CreatingRules.celem').write_text('module '+module+' {require '+x.feature+' '+x.import_signature+' -> '+x.native_return+';default '+x.feature+' with '+x.impl+';}')
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element FreeInfo schema "FreeInfo.celem";element M12CreatingRules module "M12CreatingRules.celem";registry Confectory.Build.DotNet',1));p=f.project/'MainBody.celem';p.write_text(p.read_text().replace(' -> '+x.native_return+';',' -> '+x.native_return+' in '+owner+';',1))
caller=json.loads((f.project/'Main.graph.json').read_text());caller['nodes'].append({'id':'failed','kind':'code','control':'next','intent':'기존 실패 분기 소비','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'Failed.node.json','branchOwner':'invoke'});caller['edges'] += [x.edge('invoke','failed','case:failure'),x.edge('failed','return:invoke')]
definitions=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Main.celem').read_text(),graph=caller,featureContracts={x.feature:(f.project/'Flow.celem').read_text()});assert definitions['state']=='node-definitions',definitions
(f.project/'Main.graph.json').write_text(json.dumps(caller));(f.project/'Failed.node.json').write_text(json.dumps({'schema':1,'node':'failed','definitionHash':next(n['definitionHash'] for n in definitions['nodes'] if n['id']=='failed'),'source':'global::System.Console.WriteLine("failure");'}))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
f.original={str(p.relative_to(f.project)):v for p,v in physical.items()}
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def retained():assert all(p.read_bytes()==v for p,v in physical.items() if p.name not in ['FreeInfo.celem','project.cproj'])
def binding():
 s=f.invoke('schema',{'id':owner})['state']['schema'];return {'revision':s['revision'],'hash':s['textHash']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':owner,**kw},ok)['result'].get('result')
def selection():return rpc('readImplementationCopy',function=x.feature,source=x.impl,target='common',implementation=implementation,**binding())
def row(selected,branch='failure'):
 d=selected['preview'];exits={r['name']:json.loads(r['valueJson']) for r in d['exits']};exits['yes']['executionBranch']=branch
 return {'function':x.feature,'implementation':implementation,'copySource':x.impl,'copyTarget':'common','basis':selected['basis'],'fingerprint':selected['fingerprint'],'edits':[{'type':'branch-exits','node':'$branches','text':json.dumps({'entry':d['entry'],'edges':copy.deepcopy(d['edges']),'exits':exits})}]}
def read():
 b=binding();return rpc('read',id=graph,owner=owner,ownerHash=b['hash'],ownerRevision=b['revision'])
def checkpoint():return x.checkpoint()
def confirm(ids):
 review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not review['state']['review'].get('errors');return f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result']
def build(label,branch=None):x.build(label,stdout='callee:1' if branch is None or branch=='success' else 'callee:1\n'+('failure\n' if branch=='failure' else '')+x.initial_stdout.split('\n',1)[1])
