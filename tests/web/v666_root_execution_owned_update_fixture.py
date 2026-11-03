"""One public definition update includes saved copies and declared child bodies."""
import copy,json,pathlib,sys,uuid
import v666_root_execution_copy_fixture as c
f=c.f;x=c.x;child_mode='--child-dispatch' in sys.argv;inherited_mode='--inherited-dispatch' in sys.argv
parent=f.n+'M12Parent';child=f.n+'M12Child';inherited=f.n+'M12Inherited';child_owner=f.n+'M12ChildInfo'
for name,id,ancestor in [('M12Parent',parent,None),('M12Child',child,parent),('M12Inherited',inherited,parent)]:
 text='implementation '+id+' for '+x.feature+' '+x.signature+' -> '+x.native_return+(' extends '+ancestor if ancestor else '')+' {'
 if name!='M12Inherited':
  text+='blueprint common "'+name+'.graph.json";';g=json.loads((f.project/'Flow.graph.json').read_text());next(n for n in g['nodes'] if n['id']=='choose')['implementation']=name+'.node.json';(f.project/(name+'.graph.json')).write_text(json.dumps(g));(f.project/(name+'.node.json')).write_bytes((f.project/'Flow.node.json').read_bytes())
 (f.project/(name+'.celem')).write_text(text+'}');x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' implementation "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/'M12ChildInfo.celem').write_text('schema '+child_owner+' {module '+c.module+';provide '+x.feature+' with '+(inherited if inherited_mode else child)+';}');x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element M12ChildInfo schema "M12ChildInfo.celem";registry Confectory.Build.DotNet',1))
if child_mode or inherited_mode:
 p=f.project/'MainBody.celem';p.write_text(p.read_text().replace(' in '+c.owner+';',' in '+child_owner+';'))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};f.original={str(p.relative_to(f.project)):v for p,v in physical.items()}
mutable={f.project/'Flow.celem',f.project/'Flow.graph.json',f.project/'Main.graph.json',f.project/c.graph_path,f.project/'M12Parent.graph.json',f.project/'M12Child.graph.json'}
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def retained():assert all(p.read_bytes()==v for p,v in physical.items() if p not in mutable)
def read():return x.read(x.graph)
def plan(d,branch='failure'):
 q=d['rootExecution'];assert q is not None,d.get('rootExecutionError');p={'branches':copy.deepcopy(q['branches']),'entry':d['entry'],'edges':copy.deepcopy(d['edges']),'exits':{r['name']:json.loads(r['valueJson']) for r in d['exits']},'targets':[],'callers':[{'graph':r['graph'],'node':r['node'],'routes':[]} for r in q['callers']]};p['branches'][0]['name']='같은 계약 전체 갱신';p['branches'].append({'id':'extra','name':'추가 공개 분기','value':3});p['exits']['yes']['executionBranch']=branch
 for t in q['targets']:
  if t['graph']==x.graph:continue
  row={k:copy.deepcopy(t[k]) for k in ['graph','entry','edges','exits']};row['exits']['yes']['executionBranch']=branch;p['targets'].append(row)
 return p
def request(d,p=None):return {'id':x.graph,'attempt':uuid.uuid4().hex,'checkpointHash':d['checkpointHash'],'sourceProof':x.proof(d),'edits':[{'action':'rootExecution','node':'$root','definition':p or plan(d)}]}
def build(label,after=False):c.build(label,after=after)
