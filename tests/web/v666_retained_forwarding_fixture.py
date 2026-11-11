"""Unchanged forwarded private and lifted opaque callers are source observations."""
import copy,json
import v666_retained_callers_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
_base=_prior._prior._base
original_result=81;edited_result=41
graph=copy.deepcopy(graph);graph['profile']='sync-acyclic-nested-v1'
for index in range(2):
 call=copy.deepcopy(graph['nodes'][index]);parent_id=call['id'];call.update(id='forwarded',forwardCallerStorage=True,arguments={a['name']:{'input':a['name']}for a in old['args']})
 child={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[call],'entry':'forwarded','edges':[{'from':'forwarded','port':'next','to':'exit:return'}],'exits':{'return':{'node':'forwarded'}},'locals':[{'id':'exact','name':'원래 전달 프레임 값','type':'long','initial':{'constant':9223372036854775806}}]}
 if index==1:
  inner={'id':'inner','kind':'graph','control':'next','intent':'원래 두 번째 전달 계층','signature':copy.deepcopy(old),'arguments':{a['name']:{'input':a['name']}for a in old['args']},'forwardCallerStorage':True,'graph':child}
  child={'schema':1,'profile':'sync-acyclic-nested-v1','nodes':[inner],'entry':'inner','edges':[{'from':'inner','port':'next','to':'exit:return'}],'exits':{'return':{'node':'inner'}}}
 graph['nodes'][index]={'id':parent_id,'kind':'graph','control':'next','intent':'기존 전달 호출 '+str(index),'signature':copy.deepcopy(old),'arguments':copy.deepcopy(_prior.graph['nodes'][index]['arguments']),'graph':child}
(f.project/retained_graph).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
opaque=f.n+'Opaque';opaque_header='OpaqueBody.celem';opaque_graph='Opaque.graph.json';opaque_record='Opaque.node.json'
opaque_function='function '+opaque+' (long first,long second) -> long {provide '+opaque+' with '+opaque+'Body;}'
opaque_implementation='implementation '+opaque+'Body for '+opaque+' (long left,long right) -> long {import '+functions[0]+' as First (long,long) -> long;import '+functions[1]+' as Second (long,long) -> long;body common "opaque original.csbody";}'
opaque_source='// 원래 opaque C# · CRLF 😀\r\nlong Sum(long value)=>calls.Second.Invoke(value,right);\r\nreturn Sum(calls.First.Invoke(left,right));\r\n'
for name,kind,text in [('Opaque','function',opaque_function),('OpaqueBody','implementation',opaque_implementation)]:
 (f.project/(name+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/'opaque original.csbody').write_bytes(opaque_source.encode())
lift=f.metadata('blueprintConversion',project=str(f.manifest),id=opaque+'Body',text=opaque_implementation,target='common',graphPath=opaque_graph,nodePath=opaque_record)
(f.project/opaque_header).write_text(lift['implementation']);(f.project/opaque_graph).write_bytes((json.dumps(lift['graph'],ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
defs=f.metadata('featureBlueprintNodes',featureSource=opaque_function,implementationContext=lift['context'],bodyTarget='common',featureContracts={fn:(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text()for fn in functions},graph=lift['graph']);assert defs['state']=='node-definitions',defs
record=copy.deepcopy(lift['node']);record['definitionHash']=next(r['definitionHash']for r in defs['nodes']if r['id']==record['node']);assert record['source']==opaque_source
(f.project/opaque_record).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
# The retained ordinary calculation gets its hash from the new qualified tree.
defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=n.caller+'Body',text=(f.project/retained_header).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
record=json.loads((f.project/retained_file).read_text());record['definitionHash']=next(r['definitionHash']for r in defs['nodes']if r['id']=='preserved_code');(f.project/retained_file).write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
p=f.project/'MainBody.celem';p.write_text(p.read_text().replace('{','{import '+opaque+' as Opaque (long,long) -> long;',1));(f.project/'Main.csbody').write_text('int result=checked((int)(calls.SharedCaller.Invoke(30,5)+calls.Opaque.Invoke(30,5)));global::System.Console.WriteLine(result);return result;')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot;_base.graph=graph
retained_paths=[retained_header,retained_graph,retained_file,'Opaque.celem',opaque_header,opaque_graph,opaque_record]
def verify_rows(rows):
 # Preserve raw CRLF in the assertions too; Path.read_text normalizes it.
 entries=f.metadata('describe',project=str(f.manifest))['units'];merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode('utf-8-sig')}for row in entries}|rows
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==graph
 assert merged[n.caller+'Body/body:common']['draft']==snapshot[retained_graph].decode()
 assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for fn in functions:
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
  assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
 for path in [retained_file,opaque_header,opaque_graph,opaque_record]:
  row=merged[next(u['id']for u in entries if u['path']==path)]
  assert row['draft']==snapshot[path].decode(),path
_base.verify_rows=verify_rows
def verify(checkpoint):return _base.verify(checkpoint)
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'retained-forwarded-opaque');f.checked('actual program41 retains both forwarded private chains and opaque imported C# source/record/context, declarations, routes, native parameters and exact64 unchanged')
def caller_arguments(index):return copy.deepcopy(graph['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])
def after_contract(index):
 from playwright.sync_api import expect
 fn=functions[index];held=d.pending();selector='[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]'
 def open_editor():
  f.owner().locator(selector).click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(chooser).to_be_visible();chooser.locator('[data-information-body="'+fn+'Body/body:common"]').click();expect(chooser).to_have_count(0);dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
 def fill(dialog):
  field=dialog.locator('[data-code-source]');assert sources[fn]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original native source missing");el.setSelectionRange(i,i+text.length);}',sources[fn]);f.page.keyboard.insert_text(selected[fn]);f.idle()
 dialog=open_editor();fill(dialog);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('forwarded-opaque-body-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
