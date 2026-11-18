"""Explicit callee, opaque caller and another native body share one owner Save."""
import copy,hashlib,json,re,subprocess
import v666_retained_callers_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)

callee,peer=functions;olds=[copy.deepcopy(old),copy.deepcopy(old)];nexts=copy.deepcopy(olds);nexts[0]['args'][1]['mode']='out'
native_before=copy.deepcopy(native);native_after=copy.deepcopy(native);native_after['args'][1]['mode']='out'
selected[callee]='nativeCount=5; return checked(nativeAmount-5); // 明示 out・원래 별칭 😀\r\n'
opaque=f.n+'Opaque';opaque_impl=opaque+'Body';opaque_header='OpaqueBody.celem';opaque_graph='Opaque.graph.json';opaque_path='Opaque.node.json';opaque_original='opaque original.csbody'
opaque_function='function '+opaque+' (long first,long second) -> long {provide '+opaque+' with '+opaque_impl+';}'
opaque_implementation='implementation '+opaque_impl+' for '+opaque+' (long left,long right) -> long {import '+callee+' as Selected (long,long) -> long;body common "'+opaque_original+'";}'
opaque_source='// 원래 opaque C# · CRLF 😀\r\nreturn calls.Selected.Invoke(left,right);\r\n'
opaque_selected='// 직접 작성한 호출 대응 · CRLF 😀\r\nlong assigned; return checked(calls.Selected.Invoke(left,out assigned)-1);\r\n'
for name,kind,text in [('Opaque','function',opaque_function),('OpaqueBody','implementation',opaque_implementation)]:
 (f.project/(name+'.celem')).write_bytes(text.encode());f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/opaque_original).write_bytes(opaque_source.encode())
lift=f.metadata('blueprintConversion',project=str(f.manifest),id=opaque_impl,text=opaque_implementation,target='common',graphPath=opaque_graph,nodePath=opaque_path)
(f.project/opaque_header).write_bytes(lift['implementation'].encode());(f.project/opaque_graph).write_bytes((json.dumps(lift['graph'],ensure_ascii=False,indent=2)+'\r\n').encode())
defs=f.metadata('featureBlueprintNodes',featureSource=opaque_function,implementationContext=lift['context'],bodyTarget='common',featureContracts={fn:(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text()for fn in functions},graph=lift['graph']);assert defs['state']=='node-definitions',defs
record=copy.deepcopy(lift['node']);record['definitionHash']=next(v['definitionHash']for v in defs['nodes']if v['id']==record['node']);assert record['source']==opaque_source
(f.project/opaque_path).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode());opaque_node=opaque_impl+'/body:common/node:'+record['node'];opaque_graph_id=opaque_impl+'/body:common'
p=f.project/'MainBody.celem';p.write_text(p.read_text().replace('{','{import '+opaque+' as Opaque (long,long) -> long;',1));(f.project/'Main.csbody').write_text('int result=checked((int)(calls.SharedCaller.Invoke(30,5)+calls.Opaque.Invoke(30,5)));global::System.Console.WriteLine(result);return result;')
original_result=76;edited_result=45;retained_file=opaque_graph
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};mtimes={p:(f.project/p).stat().st_mtime_ns for p in snapshot};changed_source_paths=set(paths.values())|{opaque_path}

def unchanged():assert all((f.project/p).read_bytes()==raw for p,raw in snapshot.items())
def execute(expected,name):
 build=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(build.stdout+build.stderr);assert build.returncode==0,build.stdout[-2000:]+build.stderr[-2000:];out=subprocess.run(json.loads(build.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=out.returncode,stdout=out.stdout,stderr=out.stderr)));assert(out.returncode,out.stdout.strip())==(expected,str(expected)),(out.returncode,out.stdout,out.stderr)
def request():
 r=n.request(copy.deepcopy(nexts[0]),{'amount':'amount','count':'count'});r['changes'].append(dict(type='function-edit',id=peer,hash=hashlib.sha256(r['units'][peer]['draft'].encode()).hexdigest(),name=labels[1],description='',signature=copy.deepcopy(old)))
 for index,row in enumerate(r['changes']):
  fn=functions[index];row.update(name=labels[index],description='');catalog=f.metadata('informationFunctionBodies',**{k:r[k]for k in ['project','manifest','id','units']},function=fn,includeBlueprintTargets=True);key=fn+'Body/body:common';entry=catalog[key]
  plan={k:entry[k]for k in ['hash','path']}|dict(beforeSignature=copy.deepcopy(native_before),signature=copy.deepcopy(native_after if index==0 else native_before),contract=copy.deepcopy(nexts[index]),text=selected[fn]);bodies={key:plan}
  if index==0:
   context=catalog[opaque_node];assert context['caller']and context['sourceKind']=='whole-caller-csharp',context
   bodies[opaque_node]={k:context[k]for k in ['hash','path','whole']}|dict(beforeSignature=copy.deepcopy(context['signature']),signature=copy.deepcopy(context['signature']),contract=copy.deepcopy(nexts[0]),text=opaque_selected)
  row['mapping']=dict(before=copy.deepcopy(old),args={'amount':'amount','count':'count'},bodies=bodies)
  if index==0:
   callers=f.metadata('informationFunctionInputs',**{k:r[k]for k in ['project','manifest','id','units']},function=fn);assert len(callers)==1,callers
   row['mapping']['callers']={key:{k:v[k]for k in ['graph','node','hash']}|dict(inputs={'amount':'amount'},disconnect={'count':json.dumps(graph['nodes'][0]['arguments']['count'],separators=(',',':'),ensure_ascii=False)},outputs={'return':'return'})for key,v in callers.items()}
 return r
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
def expected_graph(raw):
 g=json.loads(raw)
 for node in g['nodes']:
  if node.get('feature')==callee:node['signature']=copy.deepcopy(nexts[0]);node['arguments'].pop('count')
 return g
def verify_rows(rows):
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for index,fn in enumerate(functions):
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index];assert merged[fn+'Body/body:common']['draft']==selected[fn]
 assert n.canonical(f.metadata('inspect',text=merged[callee+'Body']['draft'])['signature'])==native_after
 assert merged[peer+'Body']['draft']==snapshot[peer.split('::')[1]+'Body.celem'].decode()
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected_graph(snapshot[retained_graph])
 assert json.loads(merged[opaque_node]['draft'])==record|dict(source=opaque_selected,definitionHash=json.loads(merged[opaque_node]['draft'])['definitionHash'])
 old_graph=json.loads(snapshot[opaque_graph]);after=json.loads(merged[opaque_graph_id]['draft']);before_context=next(v for v in old_graph['nodes']if v.get('implementationContext'));after_context=next(v for v in after['nodes']if v.get('implementationContext'));expected=copy.deepcopy(before_context['implementationContext']);expected['imports']['Selected']['signature']['args'][1]['mode']='out';assert after_context['implementationContext']==expected;before_context['implementationContext']=expected;assert old_graph==after
 header=f.metadata('inspect',text=merged[opaque_impl]['draft']);assert n.canonical(header['signature'])=={'args':[{'name':'left','type':'long'},{'name':'right','type':'long'}],'return':'long'}
 assert merged[opaque]['draft']==snapshot['Opaque.celem'].decode()
 for path in [opaque_original,'retained-code.node.json']:
  assert(f.project/path).read_bytes()==snapshot[path]and(f.project/path).stat().st_mtime_ns==mtimes[path]
def verify(checkpoint):
 doc=json.loads(checkpoint.read_text());rows={v['id']:v for v in doc['changes']};verify_rows(rows);unchanged();receipt=rows[owner]['slotSaveReceipt'];assert receipt['version']==3 and len(receipt['nativeBodyContexts'])==2;assert{opaque_header,opaque_graph,opaque_path,retained_graph,'retained-code.node.json'}<=set(receipt['readGuards']);ids=rows[owner]['atomicEditGroup'];assert{owner,*functions,callee+'Body',callee+'Body/body:common',peer+'Body/body:common',opaque_impl,opaque_graph_id,opaque_node,n.caller+'Body',n.caller+'Body/body:common'}<=set(ids);return ids
def verify_live():
 verify_rows({});allowed={str(n.a.info.relative_to(f.project)),opaque_header,opaque_graph,opaque_path,retained_header,retained_graph,callee.split('::')[1]+'Body.celem',*paths.values(),*['elements/'+fn.split('::')[1]+'.celem'for fn in functions]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 execute(edited_result,'retained-import-closure');f.checked('manual callee/out, opaque source and peer body execute45; caller/frame ABI, original csbody, independent code/local, routes/layout and outside bytes retained')
def caller_arguments(index):return copy.deepcopy(expected_graph(snapshot[retained_graph])['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(expected_graph(snapshot[retained_graph])['exits'])
def has_mapping_dialog(index):return False
def edit_contract(popover,index):pass
def verify_pins(panel,index):
 from playwright.sync_api import expect
 method=panel.locator('[data-inline-method="'+functions[index]+'"]');expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=amount]')).to_have_count(1)
 expect(method.locator('[data-pin-side=inputs] [data-function-pin-name=count]')).to_have_count(0 if index==0 else 1)
 if index==0:expect(method.locator('[data-pin-side=outputs] [data-function-pin-name=count]')).to_have_attribute('data-function-pin-type','정수')
def validate_history():
 held=d.pending();trace=[copy.deepcopy(held)];steps=0
 while d.pending()and steps<16:
  f.owner().locator('[data-own-functions-toggle]').press('Control+z');steps+=1;trace.append(copy.deepcopy(d.pending()))
 assert not d.pending(),trace
 for _ in range(steps):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==held;(f.case/'explicit-closure-history.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2));f.checked('original shared history undoes and redoes all explicit callee/caller/peer inputs without source writes')
def after_contract(index):
 global opaque_selected
 from playwright.sync_api import expect
 fn=functions[index];selected[fn]=selected[fn].replace('\r\n','\n');opaque_selected=opaque_selected.replace('\r\n','\n').removesuffix('\n')+'\r\n';selector='[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]';dialog=f.page.locator('[role=dialog]:has([data-code-source])')
 def open_source(key):
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+key+'"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();return dialog.locator('[data-code-source]')
 def replace(field,before,after):
  assert before in field.input_value(),field.input_value()[:600];field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);el.setSelectionRange(i,i+text.length);}',before);f.page.keyboard.insert_text(after);f.idle()
 key=fn+'Body/body:common';held=d.pending();field=open_source(key)
 if index==0 and mode=='reproduce-ui':
  text=field.input_value();assert dialog.locator('[data-code-region=parameters]').count()==0;field.evaluate("el=>{el.focus();const i=el.value.indexOf('long nativeCount');el.setSelectionRange(i,i);}");f.page.keyboard.insert_text('out ');assert field.input_value()==text and d.pending()==held;unchanged();f.page.screenshot(path=str(f.case/'prior-opaque-caller-role-protected.png'));dialog.locator('[data-code-cancel]').click();assert d.pending()==held;(f.case/'prior-opaque-caller-role.json').write_text(json.dumps(dict(protectedHeader=True,roleInputRejected=True,inputRetained=True,originalsRetained=True,header=text.split('\n')[0]),ensure_ascii=False,indent=2));f.checked('published UI cannot author the native role with its existing opaque caller; original header and user inputs remain protected');f.browser.close();raise SystemExit(0)
 def fill(field):
  if index==0:
   assert dialog.locator('[data-code-region=parameters]').count()==1;field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, out long nativeCount')
  replace(field,sources[fn].replace('\r\n','\n'),selected[fn])
 fill(field);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 field=open_source(key);fill(field);f.page.screenshot(path=str(f.case/('explicit-native-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0)
 if index==0:
  remap=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(remap).to_be_visible();assert remap.locator('section[data-abi-target]').count()==1;remap.locator('[data-abi-input=amount]').select_option('pin:amount');remap.locator('[data-abi-disconnect=count]').select_option('disconnect');remap.locator('[data-abi-output=return]').select_option('return');remap.locator('[data-abi-remap-accept]').click();expect(remap).to_have_count(0);f.idle()
  retained=d.pending();field=open_source(opaque_node);assert dialog.locator('[data-code-region=parameters]').count()==0;replace(field,opaque_source.replace('\r\n','\n'),opaque_selected);dialog.locator('[data-code-cancel]').click();assert d.pending()==retained
  field=open_source(opaque_node);replace(field,opaque_source.replace('\r\n','\n'),opaque_selected);f.page.screenshot(path=str(f.case/'explicit-opaque-caller.png'));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();assert d.pending()!=retained
  before=d.pending();field=open_source(key);assert field.input_value().startswith('public long Invoke(long nativeAmount, out long nativeCount)');dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();assert d.pending()==before
 f.checked('callee source/native role and removal, explicitly selected opaque caller body and peer source use original dialogs; Cancel/reentry retain native aliases and unchanged opaque frame')
