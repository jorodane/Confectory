"""Read retained v480 source and exercise selected editing/validation functions.

This is a contract probe with fixture schema/ancestry/serialization callbacks,
not a prototype browser run, graph execution or C# compiler implementation.
No reference file is changed and no account, app or network is used.
"""
import argparse,hashlib,json,pathlib,re,subprocess,zipfile

ZIP_SHA='0489844c8c6d90f7cdc8ea0e80628f487dcfb27f2c871b19367a635212d3c5bd'
FUNCTIONS=['functionBlueprintTarget','blueprintSignatureFields','blueprintForSignature','blueprintExecutionScope','blueprintExecutionOutputs','blueprintExecutionPlan','blueprintBuildStamp','blueprintPropertyNeedsTarget','blueprintResourceField','blueprintFieldsCompatible','blueprintLocalField','blueprintLocalValueValid','blueprintExpressionVariables']

def run(repo):
    archive=repo/'reference/site-ui/Confectory-Editor-Prototype-v480.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==ZIP_SHA,'Reference ZIP changed'
    with zipfile.ZipFile(archive) as z:raw=z.read('Confectory-v480/dist/blueprint.js')
    source=raw.decode('utf-8');selected={};ranges={}
    for name in FUNCTIONS:
        matches=list(re.finditer(r'^function '+re.escape(name)+r'\(',source,re.M));assert len(matches)==1,name
        start=matches[0].start();following=re.search(r'^function ',source[matches[0].end():],re.M);end=matches[0].end()+following.start() if following else len(source)
        selected[name]=source[start:end];ranges[name]=[source[:start].count('\n')+1,source[:end].count('\n')]
    line=next(line.strip() for line in source.splitlines() if line.lstrip().startswith('function openInternal('))
    start=source.index(' const saveDefinition=()=>{');end=source.index("\n q('[data-bp-save]').onclick=saveDefinition;",start)
    selected['openInternal']=line;selected['saveDefinition']='globalThis.saveDefinition='+source[start:end].split('=',1)[1].strip()
    ranges['openInternal']=[source[:source.index(line)].count('\n')+1]*2
    ranges['saveDefinition']=[source[:start].count('\n')+1,source[:end].count('\n')]
    script=r'''
const vm=require('node:vm'),fs=require('node:fs');const input=JSON.parse(fs.readFileSync(0,'utf8'));
const context=vm.createContext({structuredClone,project:{objects:[{id:'base',group:'concept',name:'Base'},{id:'derived',group:'concept',name:'Derived',base:'base'},{id:'other',group:'concept',name:'Other'},{id:'feature',group:'feature',name:'Feature'}]}});
vm.runInContext(`
const checks=[];function check(name,value){if(!value)throw Error(name);checks.push(name)}
const schemas={base:[{id:'field-hp',name:'HP',type:'정수'}]};
function inheritedPropertySources(owner){return owner.base?[project.objects.find(o=>o.id===owner.base)]:[]}
function tableEffectiveSchema(owner){return schemas[owner.id]||inheritedPropertySources(owner).flatMap(p=>schemas[p.id]||[])}
function functionSignatureFields(definition,side){return definition[side]||[]}
function serializeFunctionSignature(definition,inputs,outputs){definition.inputs=structuredClone(inputs);definition.outputs=structuredClone(outputs)}
let renders=0,saves=0;function renderFunctionBlueprint(){renders++}function saveLayouts(){saves++}function remember(){}function closePinEditor(){return true}
`,context);
for(const code of Object.values(input.functions))vm.runInContext(code,context,{timeout:1000});
const result=vm.runInContext(`
let object=project.objects[0];
const child={name:'Private child',description:'before',inputs:[{id:'in-stable',name:'Input',type:'정수'}],outputs:[{id:'out-stable',name:'Output',type:'정수'}],blueprint:{nodes:[{id:'child-entry',kind:'entry'}],links:[]}};
const parentGraph={nodes:[{id:'entry',kind:'entry'},{id:'child',kind:'action',definition:structuredClone(child)},{id:'sibling',kind:'action',definition:{name:'Sibling',inputs:[],outputs:[]}}],links:[{from:'entry',port:'next',to:'child'}]};
const originalParent={name:'Root',inputs:[],outputs:[],blueprint:structuredClone(parentGraph)};
object.functionDefinition=originalParent;
const originalText=JSON.stringify(originalParent),siblingText=JSON.stringify(parentGraph.nodes[2]);
let view={meta:{objectId:object.id,name:'Root',graphDraft:structuredClone(parentGraph),authorDraft:structuredClone(originalParent)}};
const previousMeta=view.meta;
const rootStamp=blueprintBuildStamp(originalParent);
openInternal(view.meta.graphDraft.nodes[1],false);
check('private child keeps outer object owner',view.meta.objectId==='base'&&view.meta.internalNodeId==='child'&&view.meta.internalContext);
check('enter child clones parent draft',view.meta.parentMeta!==previousMeta&&view.meta.parentMeta.graphDraft!==previousMeta.graphDraft);
check('internal target uses child draft',functionBlueprintTarget(object,view.meta).definition===view.meta.authorDraft);
let definition=view.meta.authorDraft;definition.description='changed child';let inputs=definition.inputs,outputs=definition.outputs;
let graph=structuredClone(definition.blueprint);graph.nodes[0].text='changed entry';
check('save child returns to parent',saveDefinition()===true&&!view.meta.internalContext);
const saved=view.meta.graphDraft.nodes[1].definition;
check('save child changes only owned parent node',saved.description==='changed child'&&JSON.stringify(view.meta.graphDraft.nodes[2])===siblingText);
check('child and pin IDs remain stable',saved.blueprint.nodes[0].id==='child-entry'&&saved.inputs[0].id==='in-stable'&&saved.outputs[0].id==='out-stable');
check('child save leaves root object definition unchanged',JSON.stringify(object.functionDefinition)===originalText&&view.meta.graphDirty===true);
const candidate={...originalParent,blueprint:view.meta.graphDraft};check('child edit invalidates parent semantic stamp',blueprintBuildStamp(candidate)!==rootStamp);
const moved=structuredClone(candidate);moved.blueprint.nodes[1].x=123;moved.blueprint.nodes[1].y=456;moved.blueprint.nodes[1].definition.compiled={stamp:'presentation ignored'};
check('layout and completion marker do not change stamp',blueprintBuildStamp(moved)===blueprintBuildStamp(candidate));
const mapped=blueprintForSignature({nodes:[{id:'e',kind:'entry'},{id:'o',kind:'export',outputId:'old-out'}],links:[{kind:'data',from:'e',port:'field:old-in',to:'o',toPort:'value'}],localVariables:[{id:'local-id',nodeId:'e',port:'field:old-in',name:'Input'}]},{inputs:[{id:'old-in'}],outputs:[{id:'old-out'}]},{inputs:[{id:'new-in'}],outputs:[{id:'new-out'}]});
check('signature remap is positional and retains graph IDs',mapped.nodes[0].id==='e'&&mapped.nodes[1].outputId==='new-out'&&mapped.links[0].port==='field:new-in'&&mapped.localVariables[0].id==='local-id'&&mapped.localVariables[0].port==='field:new-in');
check('concept default property uses self',blueprintPropertyNeedsTarget({},'base')===false);
check('feature default property requires target',blueprintPropertyNeedsTarget({},'feature')===true);
check('explicit target requires target even on concept',blueprintPropertyNeedsTarget({scope:'target'},'base')===true);
check('property field resolves stable field ID',blueprintResourceField({objectId:'derived',fieldId:'field-hp'}).id==='field-hp');
check('derived target is compatible with base target',blueprintFieldsCompatible({type:'객체',typeId:'derived'},{type:'객체',typeId:'base'}));
check('unrelated target type is incompatible',!blueprintFieldsCompatible({type:'객체',typeId:'other'},{type:'객체',typeId:'base'}));
const prop={source:'property',objectId:'base',fieldId:'field-hp'};
check('self property local accepts inherited owner',blueprintLocalValueValid(prop,'derived'));
check('self property local rejects unrelated or feature owner',!blueprintLocalValueValid(prop,'other')&&!blueprintLocalValueValid(prop,'feature'));
const plan=blueprintExecutionPlan(candidate.blueprint);
check('own graph termination is return',plan.onUnconnected==='return');
({checks,editingCallbacks:{renders,saves},observations:{explicitSelfFlagNeedsTargetOnFeature:blueprintPropertyNeedsTarget({scope:'self'},'feature'),planActionCarriesOnlyIdAndKind:Object.keys(plan.nodes.find(n=>n.id==='child')).sort(),noRuntimeObjectReferenceOrCallFrameExecuted:true}})
`,context,{timeout:1000});
process.stdout.write(JSON.stringify(result));
'''
    process=subprocess.run(['node','-e',script],input=json.dumps({'functions':selected}),text=True,capture_output=True,check=True)
    result=json.loads(process.stdout)
    return {'schema':1,'referenceZIP':str(archive.relative_to(repo)),'referenceZIPsha256':ZIP_SHA,'entry':'Confectory-v480/dist/blueprint.js','entrySha256':hashlib.sha256(raw).hexdigest(),'sourceRanges':ranges,'scope':'Selected actual reference editing/validation functions with declared fixture helpers; no prototype browser, graph runtime or C# execution','fixtureHelpers':['schema lookup','concept ancestry','signature fields/serialization','render/save callbacks'],'passed':len(result['checks']),**result}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('repo',type=pathlib.Path);parser.add_argument('--output',type=pathlib.Path);args=parser.parse_args();result=run(args.repo.resolve())
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    else:print(text,end='')
    print('PASS v480 selected nested/property contracts:',result['passed'])
