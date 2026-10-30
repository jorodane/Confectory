"""기존 실행 선택기와 별개로 종료점에서 분기 ID를 직접 반환한다."""
import copy,json,subprocess,uuid
import v666_node_internal_branch_fixture as n
x=n.x;f=n.f;root=n.root;parent=n.parent;child=n.child
def read():return n.read(child)
def plan(swapped=False):
 return {'entry':'body','exits':{'finish':{'executionBranch':'next' if swapped else 'alternate'},'proceed':{'executionBranch':'alternate' if swapped else 'next'}},'edges':[n.edge('body','exit:proceed'),n.edge('body','exit:finish','case:alternate')]}
def native(value):
 draft=json.loads(next(iter(x.checkpoint().values())));rows=draft['changes'];raw=json.loads(next(r['draft'] for r in rows if r['id']==n.root));outer=next(r for r in n.at(raw)['nodes'] if r['id']=='calculate');outer['graph'].update(copy.deepcopy(value));outer['graph']['executionExitMode']=True;outer['graph']['schema']=2;records={r['id'].split('/node:',1)[1].replace('/node:','/'):json.loads(r['draft']) for r in rows if r['kind']=='blueprint-node' and '/node:' in r['id']};return f.metadata('featureBlueprintDescribe',featureSource=n.function,graph=raw,implementations=records,implementationContext={'implementation':x.impl},bodyTarget='common')
def batch(value,ok=True,attempt=None):
 d=read();return n.rpc('authorBatch',ok,id=child,attempt=attempt or uuid.uuid4().hex,sourceProof=x.proof(d),checkpointHash=d['checkpointHash'],edits=[{'action':'branchExits','node':'$branches','definition':value}])
def wrap():
 d=n.read();n.rpc('authorBatch',**n.request(d));assert read()['executionEnum']==n.execution
def review():
 d=n.read();ids=d['reviewIds'] or [s['id'] for s in d['sources']];return ids,f.invoke('reviewGroup',{'target':'portable','ids':ids})['state']['review']['token']
def confirm():
 ids,token=review();f.invoke('confirmGroup',{'token':token,'ids':ids})
def run(name,swapped=False,early=False):
 build=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(x.manifest),'portable'],capture_output=True,text=True,env=f.env);(f.case/(name+'-build.log')).write_text(build.stdout+build.stderr);assert build.returncode==0,build.stdout[-4000:]+build.stderr[-4000:]
 report=json.loads(build.stdout);done=subprocess.run(report['run'],capture_output=True,text=True,env=f.env);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':done.returncode,'stdout':done.stdout,'stderr':done.stderr}));assert done.returncode==7,done.stderr
 if n.refs:wanted='41\n41\n11,16,26' if swapped else '42\n42\n12,16,26'
 else:
  lines=[]
  for mode in [-2,17,99]:
   chosen=(mode!=17 if swapped else mode==17) if not early else swapped
   for i in [1,2]:lines.append(str(mode)+':42,'+str(0 if early else mode+i)+':'+','.join(map(str,[0 if early else i,i if chosen else 0,0,i])))
  wanted='\n'.join(lines)
 assert done.stdout.strip()==wanted,(done.stdout,wanted)
