"""Graph presentation cannot change callable/body contracts or accept unsafe images."""
import copy,json,os,pathlib,subprocess,sys,hashlib,zipfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ['CONFECTORY_DOTNET'];checks=[]
def rpc(op,ok=True,**body):
 r=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation=op,**body)),text=True,capture_output=True,check=True);v=json.loads(r.stdout)
 if ok:assert v['ok'],v;return v['result']
 return v
def check(text):checks.append(text);print('PASS '+text,flush=True)
archive=repo/'reference/site-ui/Confectory-Editor-Prototype-v666.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23'
with zipfile.ZipFile(archive) as reference:
 source=reference.read('Confectory-v666/dist/blueprint.js').decode();start=source.index('function bindResourceNode(');end=source.index("element.querySelector('[data-function-icon]').onclick",start);guard=source[start:end]
 assert "if(node.definition?.wrapper){bindWrapperNode(element,node);return}" in guard and "if(node.kind==='call')" in guard and 'const def=node.definition' in guard
 assert 'icon=>{def.icon=icon;remember();drawNodes()}' in source[end:end+350]
check('repository v666 edits the local action definition only; call/wrapper guards precede the original handler')
feature='function Owned.Icon::Action (long amount) -> long {}'
g=rpc('blueprintPrepareFeature',id='Owned.Icon::Action',text=feature,implementation='Owned.Icon::Body',graphPath='Action.graph.json',nodePath='Action.node.json')['graph']
def describe(graph,ok=True):return rpc('featureBlueprintNodes',ok,featureSource=feature,graph=graph)
before=describe(g);changed=copy.deepcopy(g);changed['nodes'][0]['icon']='🛡️';after=describe(changed)
assert before==after,(before,after);check('glyph presentation leaves exact root definition/body hashes, signatures, arguments and generated contract metadata unchanged')
for icon in ['', 'ab','<','https://example.invalid/a.png','data:image/svg+xml;base64,PHN2Zy8+','data:image/webp;base64,AAAA',True,{},'★'*65501]:
 bad=copy.deepcopy(g);bad['nodes'][0]['icon']=icon;r=describe(bad,False);assert not r['ok'] or r['result'].get('state')=='invalid',r
check('empty/multiple glyphs, markup, remote/SVG/malformed/oversize images and non-string metadata fail validation')
outer=copy.deepcopy(g);outer['profile']='sync-acyclic-nested-v1';outer['nodes'][0]['kind']='graph';outer['nodes'][0].pop('implementation');outer['nodes'][0]['graph']=copy.deepcopy(g)
original=describe(outer);nested=copy.deepcopy(outer);nested['nodes'][0]['graph']['nodes'][0]['icon']='🔥';nested['nodes'][0]['icon']='★';assert describe(nested)==original
check('nested graph presentation is stripped only at declared node positions; parent/private execution contracts stay unchanged')
print(json.dumps(dict(checks=checks,sourceWritten=False,actualWindows=False),ensure_ascii=False))
