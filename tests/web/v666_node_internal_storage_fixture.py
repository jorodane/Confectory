"""직접 소유 일반 C#의 ref/out 저장소와 반환·예외 관측 fixture."""
import copy,json,pathlib,subprocess,sys
import v666_node_internal_api as x
f=x.f;feature=x.feature;root=x.graph;private='--private' in sys.argv;local='--local' in sys.argv;array='--array' in sys.argv;out_only='--out-only' in sys.argv;exception='--exception' in sys.argv
kind='int[]' if array else 'int';params=([{'name':'a','type':'int','mode':'out'},{'name':'b','type':'int','mode':'out'}] if out_only else [{'name':'a','type':kind,'mode':'ref'},{'name':'b','type':kind,'mode':'ref'},{'name':'c','type':kind,'mode':'out'}]);signature={'args':params,'return':'int'}
public=copy.deepcopy(signature)
for arg,name in zip(public['args'],['left','right'] if out_only else ['x','y','audit']):arg['name']=name
def declaration(sig):return '('+','.join(a['mode']+' '+a['type']+' '+a['name'] for a in sig['args'])+') -> int'
function='function '+feature+' '+declaration(public)+' {provide '+feature+' with '+x.impl+';}'
implementation='implementation '+x.impl+' for '+feature+' '+declaration(signature)+' {blueprint common "Flow.graph.json";}'
body='a=10;throw new global::System.InvalidOperationException("m11-stop");' if exception else 'a=10;b=20;return a;' if out_only else 'a=new[]{a[0]+1};b[0]+=a[0];c=b;return a[0]+b[0];' if array else 'a=10;b+=a;c=a+b;return a+b+c;'
helper='private static int Mutate('+','.join(a['mode']+' '+a['type']+' '+a['name'] for a in params)+'){'+body+'}'
source='// 원문 저장소 😀\r\nreturn Mutate('+','.join(a['mode']+' '+a['name'] for a in params)+');\r\n'
arguments={a['name']:{'input':p['name']} for a,p in zip(params,public['args']) if a['mode']!='out'}
node={'id':'calculate','kind':'code','control':'next','intent':'명시한 저장소 보존','signature':copy.deepcopy(signature),'arguments':arguments,'implementation':'Flow.node.json'}
if not local:node['forwardCallerStorage']=True
def export(id,output,type,binding):return {'id':id,'kind':'export','intent':'기존 출력 유지','control':'next','output':output,'signature':{'args':[{'name':'value','type':type}],'return':'void'},'arguments':{'value':binding}}
nodes=[node];edges=[];last='calculate'
if local:
 for p,a in zip(public['args'],params):
  if a['mode']!='out':continue
  id='export_'+p['name'];nodes.append(export(id,p['name'],p['type'],{'node':'calculate','output':a['name']}));edges.append({'from':last,'port':'next','to':id});last=id
nodes.append(export('result','return','int',{'node':'calculate'}));edges.append({'from':last,'port':'next','to':'result'})
inner={'schema':1,'profile':'sync-acyclic-methods-v1','entry':'calculate','nodes':nodes,'edges':edges,'exits':{}}
made=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+declaration(public)+' {}',implementation=x.impl,graphPath='Flow.graph.json',nodePath='Flow.node.json')
graph=copy.deepcopy(inner);graph.update(feature=feature,contractHash=made['graph']['contractHash'])
if private:
 frame={'id':'frame','kind':'graph','control':'next','intent':'직접 소유 frame','signature':copy.deepcopy(public),'arguments':{a['name']:{'input':a['name']} for a in public['args'] if a['mode']!='out'},'forwardCallerStorage':True,'graph':copy.deepcopy(inner)}
 graph.update(profile='sync-acyclic-nested-v1',entry='frame',nodes=[frame,export('result','return','int',{'node':'frame'})],edges=[{'from':'frame','port':'next','to':'result'}],exits={})
parent=root+('/graph:frame' if private else '');path='frame' if private else '';child=parent+'/graph:calculate';key=('frame/' if private else '')+'calculate';original_id=root+'/node:'+key.replace('/','/node:');leaf=original_id+'/node:body'
context={'implementation':x.impl,'feature':feature,'signature':signature,'imports':{}}
definitions=f.metadata('featureBlueprintNodes',featureSource=function,implementationContext=context,bodyTarget='common',graph=graph)
row=next(r for r in definitions['nestedNodes' if private else 'nodes'] if r['id']==key);record={'schema':1,'node':'calculate','definitionHash':row['definitionHash'],'source':source,'helpers':helper}
callargs='out int,out int' if out_only else 'ref '+kind+',ref '+kind+',out '+kind
if exception:
 main='int n=5;try{calls.Flow.Invoke(ref n,ref n,out n);}catch(global::System.InvalidOperationException e){global::System.Console.WriteLine(n+","+e.Message);}int a=5,b=6,c=17;try{calls.Flow.Invoke(ref a,ref b,out c);}catch(global::System.InvalidOperationException e){global::System.Console.WriteLine(a+","+b+","+c+","+e.Message);}return 7;';expected='10,m11-stop\n10,6,17,m11-stop'
elif out_only:
 main='int v=calls.Flow.Invoke(out int n,out n);global::System.Console.WriteLine(v+","+n);v=calls.Flow.Invoke(out int a,out int b);global::System.Console.WriteLine(v+","+a+","+b);return 7;';expected='20,20\n10,10,20'
elif array:
 main='int[] n=new[]{5};int v=calls.Flow.Invoke(ref n,ref n,out n);global::System.Console.WriteLine(v+","+n[0]);int[] a=new[]{5},b=new[]{6};v=calls.Flow.Invoke(ref a,ref b,out int[] c);global::System.Console.WriteLine(v+","+a[0]+","+b[0]+","+c[0]);return 7;';expected='24,12\n18,6,12,12'
else:
 main='int n=5;int v=calls.Flow.Invoke(ref n,ref n,out n);global::System.Console.WriteLine(v+","+n);int a=5,b=6;v=calls.Flow.Invoke(ref a,ref b,out int c);global::System.Console.WriteLine(v+","+a+","+b+","+c);return 7;';expected=('80,40\n52,10,16,26' if local else '120,40\n52,10,16,26')
for name,text in [('Flow.celem',function),('FlowBody.celem',implementation),('Flow.graph.json',json.dumps(graph,ensure_ascii=False)),('Flow.node.json',json.dumps(record,ensure_ascii=False)),('MainBody.celem','implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow ('+callargs+') -> int;body common "Main.csbody";}'),('Main.csbody',main)]: (f.project/name).write_text(text)
x.physical={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':parent,**kw},ok)['result'].get('result')
def read(id=parent):return rpc('read',id=id)
def request(data,nonce=None,source=None):
 r=x.request(data,nonce,source);r['id']=parent;node=next(n for n in data['nodes'] if n['id']=='calculate');observed=next(s for s in data['sources'] if s['id']==node['sourceId']);r['edits'][0]['definition']['binding']={'graph':parent,'root':root,'node':'calculate','source':node['sourceId'],'definitionHash':node['definitionHash'],'sourceHash':observed['hash']};return r
def at(document):return document['nodes'][0]['graph'] if private else document
def build(name,edited=False):
 run=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(x.manifest),'portable'],capture_output=True,text=True,env=f.env);(f.case/(name+'-build.log')).write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr[-2500:]+run.stdout[-2500:];report=json.loads(run.stdout);result=subprocess.run(report['run'],capture_output=True,text=True,env=f.env);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}));wanted=expected
 if edited:wanted='\n'.join(str(int(row.split(',')[0])+int(edited))+','+row.split(',',1)[1] for row in expected.splitlines())
 assert result.returncode==7 and result.stdout.strip()==wanted,(result.returncode,result.stdout,result.stderr,wanted)
 return result.stdout
