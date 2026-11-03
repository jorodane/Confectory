"""기존 IO/원문을 유지하는 async 후보와 복원 영수증 경계 검사."""
import copy,hashlib,json,os,pathlib,subprocess,sys
c=pathlib.Path(sys.argv[1]);sdk=os.environ['CONFECTORY_DOTNET'];tool=c/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';ns='Owned.Async';units={}
def m(op,ok=True,**req):
 r=subprocess.run([sdk,str(tool)],input=json.dumps(dict(operation=op,**req)),text=True,capture_output=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;return v.get('result',v)
def unit(id,kind,path,text):units[id]=dict(kind=kind,path=path,original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest(),revision=0)
def scaffold(local,sig):
 fn=ns+'::'+local;impl=fn+'Body';v=m('blueprintPrepareFeature',id=fn,text='function '+fn+' '+sig+' {}',implementation=impl,graphPath=local+'.graph.json',nodePath=local+'.node.json');return fn,impl,impl+'/body:common',v
fn,impl,gid,a=scaffold('A','(int value,out int total) -> int');a['graph']['profile']='sync-acyclic-switch-v1';node=a['graph']['nodes'][0];node['id']='a';node['implementation']='A.node.json';a['graph']['entry']='a'
for e in a['graph']['edges']:
 if e['from']=='body':e['from']='a'
for n in a['graph']['nodes']:
 for v in n.get('arguments',{}).values():
  if v.get('node')=='body':v['node']='a'
defs=m('featureBlueprintNodes',featureSource=a['function'],graph=a['graph']);rec=dict(schema=1,node='a',definitionHash=next(n['definitionHash'] for n in defs['nodes'] if n['id']=='a'),source='total=value*2;return value+1;')
unit(fn,'function','A.celem',a['function']);unit(impl,'implementation','ABody.celem',a['implementation']);unit(gid,'blueprint','A.graph.json',json.dumps(a['graph']));unit(gid+'/node:a','blueprint-node','A.node.json',json.dumps(rec))
fb,ib,gb,caller=scaffold('B','() -> int');caller['graph']['profile']='sync-acyclic-switch-v1';caller['graph']['entry']='call';caller['graph']['nodes']=[dict(id='call',kind='call',control='next',intent='Explicit caller',feature=fn,signature=node['signature'],arguments={'value':{'constant':5}})];caller['graph']['edges']=[{'from':'call','port':'next','to':'exit:return'}];caller['graph']['exits']={'return':{'node':'call'}};alias='fg_call_'+hashlib.sha256(fn.encode()).hexdigest()[:24];caller['implementation']='implementation '+ib+' for '+fb+' () -> int {import '+fn+' as '+alias+' (int,out int) -> int;blueprint common "B.graph.json";}'
unit(fb,'function','B.celem',caller['function']);unit(ib,'implementation','BBody.celem',caller['implementation']);unit(gb,'blueprint','B.graph.json',json.dumps(caller['graph']))
q=dict(namespace=ns,units=units,id=gid);candidate=m('blueprintAsyncCandidates',**q);assert not candidate['enabled'];first=m('blueprintAsyncTransition',**q,plan=dict(enabled=True,nodes=[dict(node='a',enabled=True)]));current=copy.deepcopy(units);current.update(first['units']);assert 'blueprintAsync' not in current[fb]['draft'];assert json.loads(current[gid+'/node:a']['draft'])['source']==rec['source'];assert m('blueprintAsyncGuards',namespace=ns,units=current)['valid'];print('PASS first explicit transition; original C# and sync caller retained',flush=True)
d=m('featureBlueprintDescribe',featureSource=current[fb]['draft'],graph=json.loads(current[gb]['draft']),featureContracts={fn:current[fn]['draft']});assert d['state']=='invalid' and d['diagnostics'][0]['code']=='GRAPH_ASYNC_CALLER_REQUIRED',d;print('PASS sync caller is a real error before explicit conversion',flush=True)
second=m('blueprintAsyncTransition',namespace=ns,units=current,id=gb,plan=dict(enabled=True,nodes=[]));current.update(second['units']);assert 'blueprintAsync' in current[fb]['draft'];assert m('blueprintAsyncGuards',namespace=ns,units=current)['valid'];assert len(second['group'])==len(set(second['group']));print('PASS explicit caller conversion merges exact atomic groups',flush=True)
bad=copy.deepcopy(current);bad[gid+'/node:a']['draft']=json.dumps({**json.loads(bad[gid+'/node:a']['draft']),'definitionHash':'0'*64});m('blueprintAsyncGuards',False,namespace=ns,units=bad);print('PASS tampered code receipt rejected',flush=True)

for kind in ['member','original','read','group','primary','empty-reads']:
 bad=copy.deepcopy(current)
 if kind=='member':bad.pop(gid+'/node:a')
 elif kind=='original':bad[fn]['original']+=' '
 elif kind=='read':bad[fn]['asyncTransition']['reads'][impl]['hash']='0'*64
 elif kind=='group':bad[fn]['atomicEditGroup'].pop()
 elif kind=='primary':bad[fn]['asyncTransition'].pop('graphs')
 else:bad[fn]['asyncTransition']['reads']={}
 m('blueprintAsyncGuards',False,namespace=ns,units=bad)
print('PASS missing member/original/read/group tampering refused',flush=True)
