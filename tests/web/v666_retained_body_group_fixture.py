"""One retained root context with independent helper/ref alias/local, one native body."""
import copy,json,hashlib
import v666_whole_bodies_fixture as b
for _key in dir(b):
 if not _key.startswith('_'):globals()[_key]=getattr(b,_key)
graph=copy.deepcopy(json.loads(whole_flow));graph['profile']='sync-acyclic-methods-v1';context=next(row for row in graph['nodes']if row.get('implementationContext')is not None);writer=next(row for row in graph['nodes']if row['kind']=='export');extra_path='preserved-helper.node.json';extra_id=whole_graph+'/node:preserve'
extra=dict(id='preserve',kind='code',control='next',intent='독립 코드·별칭·정확한 지역값 보존',signature=dict(args=[dict(name='value',type='long',mode='ref'),dict(name='sentinel',type='long')],**{'return':'void'}),arguments=dict(value=dict(local='root_alias'),sentinel=dict(local='kept')),implementation=extra_path,x=431,y=127)
graph['nodes'].insert(1,extra);graph['edges']=[dict(**{'from':context['id']},port='next',to=extra['id']),dict(**{'from':extra['id']},port='next',to=writer['id'])];graph['locals']=[dict(id='root_alias',name='기존 입력 별칭',type='long',source=dict(input='amount')),dict(id='kept',name='정확한 기존 지역값',type='long',initial=dict(constant=9223372036854775806))]
(f.project/graph_path).write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n');defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=(f.project/impl_path).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
record=json.loads(whole_record);record['definitionHash']=next(row['definitionHash']for row in defs['nodes']if row['id']==context['id']);(f.project/node_path).write_text(json.dumps(record,ensure_ascii=False))
extra_record=dict(schema=1,node=extra['id'],definitionHash=next(row['definitionHash']for row in defs['nodes']if row['id']==extra['id']),source='if(sentinel!=9223372036854775806L)throw new System.InvalidOperationException("exact local");value=checked(value+Keep(1)); // 독립 ref 별칭 원문 😀\r\n',helpers='static long Keep(long value) {return value;} // helpers 보존\r\n');extra_bytes=(json.dumps(extra_record,ensure_ascii=False,indent=2)+'\r\n').encode();(f.project/extra_path).write_bytes(extra_bytes);extra_stat=(f.project/extra_path).stat();extra_mtime=extra_stat.st_mtime_ns
whole_record=(f.project/node_path).read_bytes();whole_flow=(f.project/graph_path).read_bytes();snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};b.whole_record=whole_record;b.whole_flow=whole_flow;b.snapshot=snapshot;b._prior.snapshot=snapshot

def unchanged():b.unchanged();assert(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime

def request():
 r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1];r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(old)))
 for index,row in enumerate(r['changes']):
  row.update(name=labels[index],description='');bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id'],includeBlueprintTargets=True);own={key:body for key,body in bodies.items()if not body['caller']};assert len(own)==1,own;key,body=next(iter(own.items()));assert body['sourceKind']==('whole-graph-csharp'if index==0 else'csharp'),body
  plan={k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native),signature=copy.deepcopy(native),contract=copy.deepcopy(old),text=selected[row['id']])
  if index==0:assert key==whole_node;plan.update(whole=copy.deepcopy(body['whole']),outputs={'return':'return'})
  row['mapping']=dict(before=copy.deepcopy(old),args={'amount':'amount','count':'count'},bodies={key:plan})
  if index==0:
   uses=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id']);assert uses;row['mapping']['callers']={key:{k:target[k]for k in ['graph','node','hash']}|dict(inputs={a['name']:a['name']for a in old['args']},disconnect={})for key,target in uses.items()}
 return r

def verify_rows(rows):
 b.verify_rows(rows);assert extra_id not in rows;assert(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,whole_node,functions[1]+'Body/body:common'])<=set(ids);assert extra_id not in ids;return ids

def verify_live():
 b.verify_live();assert(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 f.checked('independent code/helpers/ref alias/exact64 local, graph byte/layout and source mtime remain unchanged; explicit context/native bodies execute20')

# Use the existing body editor and explicit retained-output/caller confirmation.
def after_contract(index):
 if index==1:return b.after_contract(index)
 from playwright.sync_api import expect
 selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])')
 def open_edit():
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+whole_node+'"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');assert sources[functions[index]]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original body absent");el.setSelectionRange(i,i+text.length);}',sources[functions[index]]);f.page.keyboard.insert_text(selected[functions[index]]);f.idle()
 open_edit();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 open_edit();dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);accept=f.page.locator('[data-abi-remap-accept]');expect(accept).to_be_visible();mapping=f.page.locator('[role=dialog]:has([data-abi-remap-accept])');target=mapping.locator('section[data-abi-target="native:'+whole_node+'"]');expect(target).to_be_visible();target.locator('[data-abi-output=return]').select_option('return');f.page.screenshot(path=str(f.case/'retained-original-output-mapping.png'));accept.click();expect(accept).to_have_count(0);f.idle();saved=d.pending()
 trace=[saved]
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z');trace.append(d.pending())
 assert d.pending()==held,trace
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==saved
 f.checked('original retained source editor and explicit identity output/caller map preserve cancellation and two-step Undo/Redo')
