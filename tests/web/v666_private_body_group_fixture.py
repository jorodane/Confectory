"""Explicit qualified private code/helpers and a second native body; unchanged ABIs."""
import copy,json,hashlib
import v666_whole_bodies_fixture as b
for _key in dir(b):
 if not _key.startswith('_'):globals()[_key]=getattr(b,_key)
private_signature={'args':[{'name':'firstValue','type':'long'},{'name':'secondValue','type':'long'}],'return':'long'}
code_signature={'args':[{'name':'firstNative','type':'long'},{'name':'secondNative','type':'long'}],'return':'long'}
private_node='inner/body';whole_node=whole_graph+'/node:inner/node:body'
# A normal Blueprint root owns the public entry ABI; private code owns its own ABI.
(f.project/impl_path).write_bytes(whole_header.replace(b'nativeAmount',b'amount').replace(b'nativeCount',b'count'));whole_header=(f.project/impl_path).read_bytes()
extra_path='private-preserved.node.json';extra_id=whole_graph+'/node:preserve'
code=dict(id='body',kind='code',control='next',intent='명시 편집할 내부 C#',implementation=node_path,signature=copy.deepcopy(code_signature),arguments={a['name']:{'input':v['name']}for a,v in zip(code_signature['args'],private_signature['args'])},x=137,y=221)
child=dict(schema=1,profile='sync-acyclic-methods-v1',nodes=[code],entry='body',edges=[{'from':'body','port':'next','to':'exit:return'}],exits={'return':{'node':'body'}},locals=[dict(id='inner_exact',name='내부 정확한 지역값',type='long',initial={'constant':9223372036854775806})])
box=dict(id='inner',kind='graph',control='next',intent='기존 private 프레임',signature=copy.deepcopy(private_signature),arguments={a['name']:{'input':v['name']}for a,v in zip(private_signature['args'],old['args'])},graph=child,x=439,y=127)
extra=dict(id='preserve',kind='code',control='next',intent='독립 원문 보존',implementation=extra_path,signature={'args':[{'name':'sentinel','type':'long'}],'return':'void'},arguments={'sentinel':{'local':'kept'}},x=71,y=133)
graph=json.loads(b.whole_flow)|dict(schema=1,profile='sync-acyclic-nested-v1',nodes=[extra,box],entry='preserve',edges=[{'from':'preserve','port':'next','to':'inner'},{'from':'inner','port':'next','to':'exit:return'}],exits={'return':{'node':'inner'}},locals=[dict(id='kept',name='상위 정확한 지역값',type='long',initial={'constant':9223372036854775805})])
(f.project/graph_path).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n').encode())
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=whole_implementation,text=(f.project/impl_path).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
sources[whole_function]='return Keep(firstNative+secondNative); // private 원문 😀\n';selected[whole_function]='return Edit(firstNative-secondNative); // 명시 private 편집 😀\n'
original_helpers='static long Keep(long value){return checked(value);} // 원래 보조 함수\n';selected_helpers='static long Edit(long value){return checked(value);} // 명시 보조 함수\n'
record=dict(schema=1,node='body',definitionHash=next(v['definitionHash']for v in defs['nestedNodes']if v['id']==private_node),source=sources[whole_function],helpers=original_helpers)
(f.project/node_path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode())
extra_record=dict(schema=1,node='preserve',definitionHash=next(v['definitionHash']for v in defs['nodes']if v['id']=='preserve'),source='if(sentinel!=9223372036854775805L)throw new System.InvalidOperationException("exact local"); // 원문 보존 😀\r\n')
extra_bytes=(json.dumps(extra_record,ensure_ascii=False,indent=2)+'\r\n').encode();(f.project/extra_path).write_bytes(extra_bytes);extra_mtime=(f.project/extra_path).stat().st_mtime_ns
whole_record=(f.project/node_path).read_bytes();whole_flow=(f.project/graph_path).read_bytes();snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};b.snapshot=snapshot;b._prior.snapshot=snapshot

def unchanged():b.unchanged();assert(f.project/extra_path).stat().st_mtime_ns==extra_mtime
def request():
 r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1];r['changes'].append(dict(type='function-edit',id=fn,hash=hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(old)))
 for index,row in enumerate(r['changes']):
  row.update(name=labels[index],description='');bodies=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id'],includeBlueprintTargets=True);key=whole_node if index==0 else row['id']+'Body/body:common';body=bodies[key];assert body['sourceKind']==('scoped-code-csharp'if index==0 else'csharp'),body
  sig=code_signature if index==0 else native;plan={k:body[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(sig),signature=copy.deepcopy(sig),contract=copy.deepcopy(old),text=selected[row['id']])
  if index==0:assert body['helperEditor']and body['node']==private_node;plan.update(whole=copy.deepcopy(body['whole']),helpers=selected_helpers)
  row['mapping']=dict(before=copy.deepcopy(old),args={'amount':'amount','count':'count'},bodies={key:plan})
 return r

def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 assert json.loads(merged[whole_node]['draft'])==json.loads(whole_record)|dict(source=selected[whole_function],helpers=selected_helpers)
 assert merged[whole_graph]['draft']==whole_flow.decode();assert merged[whole_implementation]['draft']==whole_header.decode();assert(f.project/original_path).read_bytes()==snapshot[original_path]
 assert extra_id not in rows;assert(f.project/extra_path).read_bytes()==extra_bytes and(f.project/extra_path).stat().st_mtime_ns==extra_mtime
 assert merged[functions[1]+'Body/body:common']['draft']==selected[functions[1]]
 assert merged[n.caller+'Body/body:common']['draft']==snapshot[retained_graph].decode();assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for fn in functions:assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set([owner,*functions,whole_node,functions[1]+'Body/body:common'])<=set(ids);assert extra_id not in ids;return ids
def verify_live():
 verify_rows({});allowed={node_path,paths[functions[1]],str(n.a.info.relative_to(f.project)),*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'private-native-group');f.checked('actual private/native bodies execute20; selected helpers exact, qualified frame/root graph/layout/locals, independent source bytes+mtime and original contracts preserved')
def after_contract(index):
 if index==1:return b.after_contract(index)
 from playwright.sync_api import expect
 held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 def open_edit():
  f.owner().locator(selector).click();choice=f.page.locator('[data-information-body="'+whole_node+'"]')
  if mode=='prior-ui':
   import time
   checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();deadline=time.monotonic()+75
   while time.monotonic()<deadline:
    ids={v['invoke']['requestId']for v in f.traffic if v.get('invoke',{}).get('input',{}).get('action')=='readFeature'}
    replies=[v['result']for v in f.traffic if v.get('result',{}).get('requestId')in ids]
    if replies:
     assert replies[-1]['ok']is False and replies[-1]['error']['code']=='consumer_error';break
    f.page.wait_for_timeout(20)
   else:raise AssertionError('Prior UI did not expose its observed Blueprint path result')
   assert choice.count()==0 and dialog.count()==0 and d.pending()==held and checkpoint.read_bytes()==baseline;unchanged();(f.case/'prior-private-picker-observation.json').write_text(json.dumps(dict(traffic=f.traffic[-10:],checkpointPreserved=True,originalsPreserved=True),ensure_ascii=False,indent=2));f.checked('prior packaged UI bypasses known owned private CSharp selection and preserves all input/originals after its Blueprint path refusal');f.browser.close();raise SystemExit(0)
  expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible()
  if choice.count():choice.click()
  expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');assert sources[whole_function]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original private body absent");el.setSelectionRange(i,i+text.length);}',sources[whole_function]);f.page.keyboard.insert_text(selected[whole_function]);assert original_helpers in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',original_helpers);f.page.keyboard.insert_text(selected_helpers);f.idle()
 open_edit();dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 open_edit();f.page.screenshot(path=str(f.case/'private-source-helpers.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert saved!=held
 f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held
 f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 f.checked('existing qualified private body/helper editor preserves cancel, explicit text and one-step Undo/Redo without inferring frame bindings')
