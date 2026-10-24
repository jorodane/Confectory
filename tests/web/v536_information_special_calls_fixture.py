"""Existing branch/enum/After forms with immutable owned callees and C#."""
import copy,json,re
import v536_information_call_inputs_fixture as c
x,f,n,owner,fn=c.x,c.f,c.n,c.owner,c.fn
x.kind='type' if 'type' in x.mode else 'delete';x.new={'args':([{'name':'amount','type':'string'}] if x.kind=='type' else [])+[{'name':'count','type':'long'}],'return':'long'}
refs='refs' in x.mode
leaf_source=c.leaf_source
if refs:
 leaf_source='function '+c.leaf+' (long amount,ref long count,out long copied) -> long {provide '+c.leaf+' with '+c.leaf+'Body;}'
 (f.project/'InputLeaf.celem').write_text(leaf_source);(f.project/'InputLeafBody.celem').write_text('implementation '+c.leaf+'Body for '+c.leaf+' (long amount,ref long count,out long copied) -> long {body common "InputLeaf.csbody";}');(f.project/'InputLeaf.csbody').write_text('count+=1;copied=count;return amount; // 그대로 보존')
boolean=f.n+'BooleanLeaf';boolean_source='function '+boolean+' (long amount) -> bool {provide '+boolean+' with '+boolean+'Body;}'
for local,kind,source in [('BooleanLeaf','function',boolean_source),('BooleanLeafBody','implementation','implementation '+boolean+'Body for '+boolean+' (long amount) -> bool {body common "BooleanLeaf.csbody";}')]:
 (f.project/(local+'.celem')).write_text(source);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' '+kind+' "'+local+'.celem";registry Confectory.Build.DotNet',1))
(f.project/'BooleanLeaf.csbody').write_text('return amount>0; // 호출 원문 유지')
impl=f.project/(fn.split('::')[1]+'Body.celem');g=json.loads((f.project/'function.graph.json').read_text());g['profile']='sync-acyclic-switch-v1'
if refs:
 impl.write_text(re.sub(r'(import\s+'+re.escape(c.leaf)+r'\s+as\s+\S+)\s*\([^)]*\)\s*->\s*long',lambda m:m[1]+' (long, ref long, out long) -> long',impl.read_text(),count=1));next(v for v in g['nodes'] if v['id']=='inner')['arguments'].update(count={'input':'count'});next(v for v in g['nodes'] if v['id']=='inner')['signature']={'args':[{'name':'amount','type':'long'},{'name':'count','type':'long','mode':'ref'},{'name':'copied','type':'long','mode':'out'}],'return':'long'}
after=f.metadata('blueprintCallAfter',functionText=leaf_source);inner=next(v for v in g['nodes'] if v['id']=='inner');inner['postCall']={k:after[k] for k in ['contractHash','source','helpers']}
for id,source,control,feature in [('gateCall',boolean_source,'branch',boolean),('enumCall',leaf_source,'next',c.leaf)]:
 out=f.metadata('blueprintPrepareCall',id=fn+'Body',text=impl.read_text(),targetText=source,graph=g,definition={'id':id,'feature':feature,'intent':'기존 호출 형태 보존','control':control});impl.write_text(out['implementation']);g=out['graph'];call=next(v for v in g['nodes'] if v['id']==id);call['arguments']={'amount':{'input':'amount'}}|({'count':{'input':'count'}} if refs and id=='enumCall' else {})
execution={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'done','name':'Done','value':7}]}
wrapped=f.metadata('blueprintCallWrapper',functionText=leaf_source,executionEnum=execution,source='return Pick();',helpers='private static Result Pick(){return Result.Done;}',returnMapping='native-return-out-v1');enum_call=next(v for v in g['nodes'] if v['id']=='enumCall');enum_call.update(control='switch',executionEnum=copy.deepcopy(execution),postCall={k:wrapped[k] for k in ['mode','contractHash','source','helpers','returnMapping']})
extra_sources={}
for id,control,signature,arguments,source,helpers,branch in [
 ('gateCode','branch',{'args':[{'name':'amount','type':'long'}],'return':'bool'},{'amount':{'input':'amount'}},'return amount>0;','',None),
 ('enumCode','switch',{'args':[{'name':'amount','type':'long'}],'return':'void'},{'amount':{'input':'amount'}},'return Pick(amount);','private static Result Pick(long value){return value>0?Result.Done:Result.NoBranch;}',None),
 ('codeRegion','next',{'args':[],'return':'void'},{},'return;','', 'enumCode'),
 ('callRegion','next',{'args':[],'return':'void'},{},'return;','', 'enumCall')]:
 path=id+'.node.json';node={'id':id,'kind':'code','control':control,'intent':'기존 실행 경로와 본문 보존','signature':signature,'arguments':arguments,'implementation':path}
 if branch:node['branchOwner']=branch
 if control=='switch':node['executionEnum']=copy.deepcopy(execution)
 g['nodes'].append(node);extra_sources[id]=(path,source,helpers)
g['entry']='gateCode';g['edges']=[{'from':a,'port':port,'to':b} for a,port,b in [('gateCode','true','gateCall'),('gateCode','false','gateCall'),('gateCall','true','enumCode'),('gateCall','false','enumCode'),('enumCode','next','inner'),('enumCode','case:done','codeRegion'),('codeRegion','next','return:enumCode'),('inner','next','enumCall'),('enumCall','case:done','callRegion'),('callRegion','next','return:enumCall'),('enumCall','next','body'),('body','next','exit:return')]]
next(v for v in g['nodes'] if v['id']=='body')['arguments']['amount']={'node':'enumCall'}
contracts={c.leaf:leaf_source,boolean:boolean_source};defs=f.metadata('featureBlueprintNodes',featureSource=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text(),graph=g,featureContracts=contracts);assert defs['state']=='node-definitions',defs
records={}
for node in g['nodes']:
 if node['kind']!='code':continue
 if node['id']=='body':path='function.node.json';source=n.record['source'];helpers=''
 else:path,source,helpers=extra_sources[node['id']]
 record={'schema':1,'node':node['id'],'definitionHash':next(v['definitionHash'] for v in defs['nodes'] if v['id']==node['id']),'source':source}|({'helpers':helpers} if helpers else {});records[node['id']]=copy.deepcopy(record);(f.project/path).write_text(json.dumps(record))
(f.project/'function.graph.json').write_text(json.dumps(g));original_graph=copy.deepcopy(g);x.snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts};x.extra_allowed={p for p,_,_ in extra_sources.values()}
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};graph=json.loads(rows[fn+'Body/body:common']['draft']);expected=copy.deepcopy(original_graph);expected['contractHash']=graph['contractHash']
 for node in expected['nodes']:
  if node['id'] in ['gateCode','gateCall','enumCode','inner','enumCall']:node['arguments']['amount']={'input':'count'} if x.kind=='type' else {'constant':9223372036854775806}
 assert graph==expected
 for id,old in records.items():
  r=json.loads(rows[fn+'Body/body:common/node:'+id]['draft']);assert r['source']==old['source'] and r.get('helpers','')==old.get('helpers','')
 for path in ['InputLeaf.celem','InputLeafBody.celem','InputLeaf.csbody','BooleanLeaf.celem','BooleanLeafBody.celem','BooleanLeaf.csbody']:assert (f.project/path).read_bytes()==x.snapshot[path]
 call=json.loads(rows[n.caller+'Body/body:common']['draft'])['nodes'][0];assert call['arguments']==x.expected_caller() and call['signature']==x.new;return rows[owner]['atomicEditGroup']
x.verify=verify
