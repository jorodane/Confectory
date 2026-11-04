"""An authored async result node with existing completion/result rails and outputs."""
import json,sys,uuid
import v666_async_completion_fixture as base
f=base.f
feature,impl,graph=base.feature,base.impl,base.graph
node='fresh';port='case:positive' if '--result-line'in sys.argv else 'completion'
new_source='// 명시적으로 작성한 분기선 Task 😀\nawait global::System.Threading.Tasks.Task.Yield();\nglobal::System.Console.WriteLine("work:"+value);\n'
original,unchanged,read,proof,rpc,checkpoint=base.original,base.code_unchanged,base.read,base.proof,base.rpc,base.checkpoint
source_id=lambda n:graph+'/node:'+n
def request(d,edits):return dict(id=graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=proof(d),edits=edits)
def draft_unit():return next(u for u in json.loads(next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes']if u['id']==source_id(node))
new_path=None
def path():
 global new_path
 if new_path is None:new_path=f.project/draft_unit()['path']
 return new_path
def build(name,created=False):
 expected='callee:1\n'+('work:10\ncompleted:10\n'if created and port=='completion'else'completed:10\n')+('work:10\n'if created and port=='case:positive'else'')+'after:10'
 base.build(name,10,expected if created else'callee:1\ncompleted:10\nafter:10')
def stage(x,panel):
 p=panel();p.locator('[data-bp-overview-node=choose]').click()
 # Select the authored rail, create in that region, then explicitly retain its
 # old successor using the original execution ports. No state injection.
 from v666_async_root_io_fixture import pan
 pan(x,panel)
 rail=p.locator('.bp-exec-line-out[data-node=choose][data-port="'+port+'"]')
 rail.click();box=p.locator('.bp-viewport').bounding_box();p.locator('.bp-viewport').click(button='right',position={'x':box['width']*.7,'y':box['height']*.75});f.page.get_by_role('button',name='동작 만들기',exact=True).click()
 global node
 node=next(v['node']for _,v in f.pending()['blueprint']if v['type']=='create');x.node=node
 p=panel();p.locator('[data-bp-overview-node="'+node+'"]').click();p.locator('[data-bp-node="'+node+'"] [data-inline-description]').fill('완료/결과선의 새 비동기 동작')
 # Existing pin plan/value UI is unnecessary here; use an explicit argument-free
 # Task in UI, while the API covers published output consumption before routing.
 x.new_source=new_source.replace('"work:"+value','"work:10"')
 cells=f.pending()['blueprint'];definition=json.loads(next(v['text']for _,v in cells if v['type']=='create'));assert definition['branchOwner']=='choose'
 assert any(v['type']=='route:'+port and v['node']=='choose'and v['text']==node for _,v in cells)
 destination=next(e['to']for e in base.initial_edges if e['from']=='choose'and e['port']==port)
 p.locator('[data-bp-overview-node="'+node+'"]').click();pan(x,panel);p.locator('[data-bp-node="'+node+'"] .bp-exec-line-out[data-port=next]').click();p.locator('[data-bp-overview-node="'+destination+'"]').click();pan(x,panel);p.locator('[data-bp-node="'+destination+'"] .bp-exec-header-in').click()
 cells=f.pending()['blueprint'];assert any(v['type']=='route'and v['node']==node and v['text']==destination for _,v in cells)
 original()
 f.checked('원래 분기선의 새 동작은 소유 영역·분기 ID를 보존하고 명시 연결로 기존 목적지를 유지한다')
