"""Owned property Read/Set/RefCell receivers, immutable local pack copy only."""
import copy,hashlib,json,re,shutil
import v536_information_input_replacements_fixture as x
f,n,owner,fn=x.f,x.n,x.owner,x.fn
receiver=not x.mode.startswith('value');x.kind='type' if 'type' in x.mode else 'delete'
x.old={'args':[{'name':'amount','type':'object' if receiver else 'long'},{'name':'count','type':'object' if receiver else 'long'},{'name':'number' if receiver else 'target','type':'long' if receiver else 'object'}],'return':'long'}
x.new={'args':([{'name':'amount','type':'string'}] if x.kind=='type' else [])+copy.deepcopy(x.old['args'][1:]),'return':'long'};x.mapping={'before':x.old,'args':{a['name']:None if a['name']=='amount' else a['name'] for a in x.old['args']}}
model=f.case/'object model';shutil.copytree(f.repo/'packs/object-model',model,ignore=shutil.ignore_patterns('.confectory','bin','obj'));model_original={str(p.relative_to(model)):p.read_bytes() for p in model.rglob('*') if p.is_file()}
field_owner=f.n+'Receiver';schema_id=f.n+'ReceiverInfo'
for local,kind,text in [('ReceiverInfo','schema','schema '+schema_id+' {field health single general long;}'),('Receiver','object','object '+field_owner+' {use schema '+schema_id+';}')]:
 (f.project/(local+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' '+kind+' "'+local+'.celem";registry Confectory.Build.DotNet',1))
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','registry Confectory.ObjectModel '+json.dumps(str(model/'pack.cpack'))+';dependency Confectory.ObjectModel version "0.1.0";registry Confectory.Build.DotNet',1))
def fingerprint(id,sig):return hashlib.sha256(json.dumps({'feature':id,'signature':sig},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def header(sig):return '('+','.join(a['type']+' '+a['name'] for a in sig['args'])+') -> '+sig['return']
fnfile=f.project/('elements/'+fn.split('::')[1]+'.celem');fnfile.write_text(re.sub(r'function\s+'+re.escape(fn)+r'\s*\([^)]*\)\s*->\s*long','function '+fn+' '+header(x.old),fnfile.read_text(),count=1))
impl=f.project/(fn.split('::')[1]+'Body.celem');impl.write_text(re.sub(r'(implementation\s+\S+\s+for\s+\S+)\s*\([^)]*\)\s*->\s*long',lambda m:m[1]+' '+header(x.old),impl.read_text(),count=1))
caller_sig={'args':[{'name':'first','type':x.old['args'][0]['type']},{'name':'second','type':x.old['args'][1]['type']},copy.deepcopy(x.old['args'][2])],'return':'long'}
caller_file=f.project/'Caller.celem';caller_file.write_text(re.sub(r'function\s+\S+\s*\([^)]*\)\s*->\s*long','function '+n.caller+' '+header(caller_sig),caller_file.read_text(),count=1))
caller_impl=f.project/'CallerBody.celem';text=re.sub(r'(implementation\s+\S+\s+for\s+\S+)\s*\([^)]*\)\s*->\s*long',lambda m:m[1]+' '+header(caller_sig),caller_impl.read_text(),count=1);types=', '.join(a['type'] for a in x.old['args']);text=re.sub(r'(import\s+'+re.escape(fn)+r'\s+as\s+\S+)\s*\([^)]*\)\s*->\s*long',lambda m:m[1]+' ('+types+') -> long',text,count=1);caller_impl.write_text(text)
cg=json.loads((f.project/'caller.graph.json').read_text());cg['profile']='sync-acyclic-property-ref-v1';cg['contractHash']=fingerprint(n.caller,caller_sig);cg['nodes'][0]['signature']=copy.deepcopy(x.old);cg['nodes'][0]['arguments']={'amount':{'input':'first'},'count':{'input':'second'},x.old['args'][2]['name']:{'input':x.old['args'][2]['name']}};(f.project/'caller.graph.json').write_text(json.dumps(cg))
g=json.loads((f.project/'function.graph.json').read_text());g['profile']='sync-acyclic-property-ref-v1';g['contractHash']=fingerprint(fn,x.old);body=g['nodes'][0];body['arguments']={'amount':{'node':'before'},'count':{'node':'cell'}};g['entry']='before';g['exits']={'return':{'node':'body'}}
descriptor=f.metadata('blueprintPropertyCatalog',project=str(f.manifest),sourceId=fn+'Body',owner=field_owner)['descriptor'];field=descriptor['fields'][0];target={'input':'amount' if receiver else 'target'};properties=[]
for id,kind in [('before','property'),('write','property-set'),('after','property'),('cell','property-ref')]:
 properties.append({'id':id,'kind':kind,'control':'next','intent':'기존 실행 시점의 '+kind,'propertyOwner':field_owner,'field':'health','fieldContractHash':field['hash'],'signature':{'args':[{'name':'target','type':'object'}]+([{'name':'value','type':'long'}] if kind=='property-set' else []),'return':'void' if kind=='property-set' else 'long'},'arguments':{'target':copy.deepcopy(target)}|({'value':{'input':'number' if receiver else 'amount'}} if kind=='property-set' else {})})
g['nodes']=[*properties,body];g['edges']=[{'from':a,'port':'next','to':b} for a,b in [('before','write'),('write','after'),('after','cell'),('cell','body'),('body','exit:return')]]
contracts={}
for name in ['Read','Set','RefCell']:
 id='Confectory.ObjectModel::'+name;source=(model/(name+'.celem')).read_text();contracts[id]=source;alias='fg_call_'+hashlib.sha256(id.encode()).hexdigest()[:24];types='object,string,string,string'+(',object' if name=='Set' else '');ret='void' if name=='Set' else 'object';impl.write_text(impl.read_text().replace('{','{import '+id+' as '+alias+' ('+types+') -> '+ret+';',1))
defs=f.metadata('featureBlueprintNodes',featureSource=fnfile.read_text(),graph=g,propertyContracts={field_owner:descriptor},featureContracts=contracts);assert defs['state']=='node-definitions',defs
record=json.loads((f.project/'function.node.json').read_text());record['definitionHash']=next(v['definitionHash'] for v in defs['nodes'] if v['id']=='body');(f.project/'function.node.json').write_text(json.dumps(record));(f.project/'function.graph.json').write_text(json.dumps(g));original_graph=copy.deepcopy(g)
x.snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
def selections(preview):
 callers={k:{field:t[field] for field in ['graph','node','hash']}|{'inputs':{'count':'count',x.old['args'][2]['name']:x.old['args'][2]['name']}|({'amount':{'valueJson':json.dumps('새 한글 값')}} if x.kind=='type' else {}),'disconnect':{'amount':t['bindings']['amount']}} for k,t in preview['functionInputs'].items()}
 plans={k:{field:t[field] for field in ['graph','node','argument','hash','before','contracts']}|{'value':{'input':'count'} if receiver or x.kind=='type' else {'valueJson':'9223372036854775806'}} for k,t in preview['functionInputUses'].items() if 'amount' in t.get('inputs',[t['input']])}
 return x.mapping|{'callers':callers,'implementations':plans}
x.selections=selections
def expected_caller():return {'count':{'input':'second'},x.old['args'][2]['name']:{'input':x.old['args'][2]['name']}}|({'amount':{'constant':'새 한글 값'}} if x.kind=='type' else {})
x.expected_caller=expected_caller
def select_use(section,correct):
 select=section.locator('[data-abi-input]').first;name=select.get_attribute('data-abi-input')
 if receiver:assert select.locator('option[value=value]').count()==0;select.select_option('pin:count')
 elif x.kind=='type':select.select_option('pin:count' if correct else 'pin:amount')
 else:select.select_option('value');section.locator('[data-abi-value="'+name+'"]').fill('9223372036854775806')
x.select_use=select_use
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};after=json.loads(rows[fn+'Body/body:common']['draft']);expected=copy.deepcopy(original_graph);expected['contractHash']=after['contractHash']
 for node in expected['nodes']:
  if node['kind'].startswith('property'):
   if receiver:node['arguments']['target']={'input':'count'}
   elif node['kind']=='property-set':node['arguments']['value']={'input':'count'} if x.kind=='type' else {'constant':9223372036854775806}
 assert after==expected;assert json.loads(rows[n.caller+'Body/body:common']['draft'])['nodes'][0]['arguments']==expected_caller();assert json.loads(rows[fn+'Body/body:common/node:body']['draft'])['source']==n.record['source'];assert all((model/p).read_bytes()==b for p,b in model_original.items());return rows[owner]['atomicEditGroup']
x.verify=verify

def reselect(popup,select):
 if 'reselect' not in x.mode:return
 from playwright.sync_api import expect
 before=f.pending();popup().get_by_role('button',name='저장',exact=True).click();modal=f.page.get_by_role('dialog',name='입력 연결 갱신',exact=True);expect(modal).to_be_visible();modal.locator('[data-abi-remap-cancel]').click();assert f.pending()==before
 popup().get_by_role('button',name='저장',exact=True).click();select();assert f.pending()==before
 f.checked('같은 계약의 명시적 상세 저장은 재선택을 열고 취소/수락 모두 기존 입력·receipt를 보존한다')
x.reselect=reselect
