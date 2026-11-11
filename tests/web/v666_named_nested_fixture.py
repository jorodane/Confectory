"""Explicit native name/body edits preserve owned private caller frames."""
import copy,json
import v666_named_body_group_fixture as _named
for _key in dir(_named):
 if not _key.startswith('_'):globals()[_key]=getattr(_named,_key)
retained_header='CallerBody.celem';retained_file='retained-code.node.json';retained_graph='caller.graph.json'
original_result=41;edited_result=21
_signature={'args':[{'name':'first','type':'long'},{'name':'second','type':'long'}],'return':'long'}
def _box(name,child):return {'id':name,'kind':'graph','control':'next','intent':'기존 내부 '+name,'signature':copy.deepcopy(_signature),'arguments':{name:{'input':name}for name in ['first','second']},'graph':child}
def _frame(nodes,entry,exits):return {'schema':1,'profile':'sync-acyclic-nested-v1','nodes':nodes,'entry':entry,'edges':[{'from':entry,'port':'next','to':'exit:return'}],'exits':{'return':{'node':exits}},'locals':[{'id':'exact','name':'프레임별 정확한 지역값','type':'long','initial':{'constant':9223372036854775805}}]}
_inner={key:copy.deepcopy(graph[key])for key in ['schema','profile','nodes','entry','edges','exits']}
_inner['profile']='sync-acyclic-nested-v1';_inner['locals']=[{'id':'bonus','name':'기존 보정','type':'long','initial':{'constant':1}},{'id':'exact','name':'원문 정확한 지역값','type':'long','initial':{'constant':9223372036854775806}}]
_code={'id':'preserved_code','kind':'code','control':'next','intent':'호출자의 기존 계산','implementation':retained_file,'signature':{'args':[{'name':'value','type':'long'},{'name':'bonus','type':'long'}],'return':'long'},'arguments':{'value':{'node':'invoke_second'},'bonus':{'local':'bonus'}}}
_inner['nodes'].append(_code);_inner['edges']=[{'from':'invoke','port':'next','to':'invoke_second'},{'from':'invoke_second','port':'next','to':'preserved_code'},{'from':'preserved_code','port':'next','to':'exit:return'}];_inner['exits']={'return':{'node':'preserved_code'}}
_outer=_frame([_box('inner',_inner)],'inner','inner');_sibling=copy.deepcopy(_inner);_sibling['nodes']=[copy.deepcopy(_code)];_sibling['nodes'][0]['implementation']='sibling-code.node.json';_sibling['nodes'][0]['arguments']={'value':{'input':'first'},'bonus':{'constant':0}};_sibling['entry']='preserved_code';_sibling['edges']=[{'from':'preserved_code','port':'next','to':'exit:return'}]
graph=copy.deepcopy(graph);graph.update(_frame([_box('outer',_outer),_box('sibling',_sibling)],'outer','outer'));graph['locals']=[];graph['edges']=[{'from':'outer','port':'next','to':'sibling'},{'from':'sibling','port':'next','to':'exit:return'}]
(f.project/retained_graph).write_bytes((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
_defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=n.caller+'Body',text=(f.project/retained_header).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert _defs['state']=='node-definitions',_defs
for _path,_id in [(retained_file,'outer/inner/preserved_code'),('sibling-code.node.json','sibling/preserved_code')]:
 _record=json.loads((f.project/'function.node.json').read_text());_record.update(node='preserved_code',definitionHash=next(row['definitionHash']for row in _defs['nestedNodes']if row['id']==_id),source='return checked(value+bonus); // 기존 계산 원문 9223372036854775806 😀'+chr(13)+chr(10));(f.project/_path).write_bytes((json.dumps(_record,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def caller_arguments(index):return copy.deepcopy(graph['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])
def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode()}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 expected=copy.deepcopy(graph);calls=expected['nodes'][0]['graph']['nodes'][0]['graph']['nodes']
 for index in range(2):calls[index].update(signature=nexts[index],arguments={a['name']:copy.deepcopy(_inner['nodes'][index]['arguments'][b['name']])for a,b in zip(nexts[index]['args'],olds[index]['args'])})
 assert json.loads(merged[n.caller+'Body/body:common']['draft'])==expected
 assert merged[n.caller+'Body']['draft']==snapshot[retained_header].decode()
 for _id,path in [('outer/node:inner/node:preserved_code',retained_file),('sibling/node:preserved_code','sibling-code.node.json')]:assert merged[n.caller+'Body/body:common/node:'+_id]['draft']==snapshot[path].decode(),path
 for index,fn in enumerate(functions):
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==nexts[index]
  assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body/body:common'])<=set(ids);return ids
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),retained_graph}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'named-private-caller');f.checked('actual program21 preserves qualified private/sibling C# bytes, native declarations, frame locals/exact64, IDs/routes and explicit nested public-input remap')

def after_contract(index):
 from playwright.sync_api import expect
 fn=functions[index];selector='[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]';held=d.pending()
 def open_editor():
  f.owner().locator(selector).click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(chooser).to_be_visible();chooser.locator('[data-information-body="'+fn+'Body/body:common"]').click();expect(chooser).to_have_count(0);dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
 def fill(dialog):
  field=dialog.locator('[data-code-source]');assert sources[fn]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original native body absent");el.setSelectionRange(i,i+text.length);}',sources[fn]);f.page.keyboard.insert_text(selected[fn]);f.idle()
 dialog=open_editor();fill(dialog);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('native-private-caller-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
