"""Selected retained v480 C# editing contracts, with explicit fixture callbacks. No C# execution."""
import argparse,hashlib,json,pathlib,re,subprocess,zipfile
ZIP_SHA='0489844c8c6d90f7cdc8ea0e80628f487dcfb27f2c871b19367a635212d3c5bd'
FUNCTIONS=['blueprintExecutionOutputs','blueprintCSharpIdentifier','blueprintCSharpContract','blueprintCSharpDefaultBody','blueprintCSharpRegionStamp','blueprintCSharpSections','blueprintCSharpSource','blueprintCSharpBody','blueprintCSharpList','blueprintParseCSharpRegions']
def run(repo):
 archive=repo/'reference/site-ui/Confectory-Editor-Prototype-v480.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==ZIP_SHA
 with zipfile.ZipFile(archive) as z:raw=z.read('Confectory-v480/dist/blueprint.js')
 source=raw.decode();selected={};ranges={}
 for name in FUNCTIONS:
  match=re.search(r'^function '+re.escape(name)+r'\(',source,re.M);assert match,name
  following=re.search(r'^function ',source[match.end():],re.M);end=match.end()+following.start() if following else len(source)
  selected[name]=source[match.start():end];ranges[name]=[source[:match.start()].count('\n')+1,source[:end].count('\n')]
 script=r'''
const fs=require('node:fs'),vm=require('node:vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const context=vm.createContext({structuredClone,project:{objects:[]}});
vm.runInContext(`let nextID=0;function uid(){return 'new-'+(++nextID)}function blueprintSignatureFields(def,side){return def[side]||[]}function serializeFunctionSignature(def,inputs,outputs){def.inputs=inputs;def.outputs=outputs}const checks=[];function check(name,ok){if(!ok)throw Error(name);checks.push(name)}`,context);
for(const code of Object.values(input.functions))vm.runInContext(code,context,{timeout:1000});
const result=vm.runInContext(String.raw`
const node={id:'code-node',kind:'action',definition:{inputs:[{id:'input-id',name:'value',type:'정수'}],outputs:[{id:'out-id',name:'audit',type:'조건'}],executionOutputs:[{id:'next',name:'Continue',scriptValue:-2},{id:'success',name:'Completed',scriptValue:17}]}};
const contract=blueprintCSharpContract(node);check('execution enum maps stable port IDs to explicit int32 values',contract.enumMembers.map(m=>m.id+':'+m.value).join(',')==='next:-2,success:17');check('data outputs are out parameters; Result is execution return',contract.returnType==='Result'&&contract.parameters[1].modifier==='out');
const reordered=structuredClone(node);reordered.branchOrder=['success'];reordered.definition.scriptEnumOrder=['success','next'];const order=blueprintCSharpContract(reordered);check('visual enum order preserves IDs and numeric values',order.enumMembers.map(m=>m.id+':'+m.value).join(',')==='success:17,next:-2');
const parts=blueprintCSharpSections(contract,'audit=true;return Result.Continue;');check('scaffolding is fixed and four regions are editable',parts.filter(p=>p.id).map(p=>p.id).join(',')==='enum,parameters,body,helpers');check('helpers follow the closing Execute brace',parts.findIndex(p=>p.id==='helpers')>parts.findIndex(p=>p.id==='body'));
const helpers='\nstatic int Twice(int x) => x*2;\n',sections={enum:'Completed = 17,\nProceed = -2,',parameters:'out bool audit, ref int value',body:'    audit = true;\n    return Result.Proceed;',helpers};const parsed=blueprintParseCSharpRegions(node,sections);
check('enum rename/reorder retains stable IDs by value',parsed.definition.executionOutputs.find(p=>p.id==='next').scriptName==='Proceed'&&parsed.definition.executionOutputs.find(p=>p.id==='success').scriptValue===17);check('parameter reorder retains IDs by names and ref/out roles',parsed.definition.scriptParameterOrder.join(',')==='out-id,input-id'&&parsed.definition.inputs[0].passMode==='ref');check('helper region is retained as source, not executed',parsed.definition.scriptRegions.helpers===helpers&&parsed.definition.scriptSource.includes(helpers));check('body indentation is separated from source',parsed.definition.body==='audit = true;\nreturn Result.Proceed;');
function refuses(text){try{blueprintParseCSharpRegions(node,{...sections,enum:text});return false}catch{return true}}
check('duplicate enum values rejected',refuses('Continue = 1, Completed = 1'));check('out of int32 enum rejected',refuses('Continue = 2147483648, Completed = 17'));check('removing primary execution port rejected',refuses('Completed = 17'));check('duplicate enum names rejected',refuses('Continue = 0, Continue = 1'));
const more=structuredClone(node);more.definition.executionOutputs.push({id:'stable-other',name:'Other'});const before=blueprintCSharpContract(more);more.branchOrder=['stable-other','success'];const after=blueprintCSharpContract(more);check('unassigned enum numeric identity follows port ID, not visual order',before.enumMembers.find(m=>m.id==='stable-other').value===after.enumMembers.find(m=>m.id==='stable-other').value);
({checks,observations:{referenceEditorExplicitlySaysCompilerNotConnected:true,generatedExecutionReturn:contract.returnType,dataReturnRepresentation:'out parameters',unknownEnumValueRuntimePolicyNotDefinedByTheseFunctions:true,externalHelperRuntimeScopeNotExecuted:true}})
`,context,{timeout:1000});process.stdout.write(JSON.stringify(result));
'''
 process=subprocess.run(['node','-e',script],input=json.dumps({'functions':selected}),text=True,capture_output=True)
 if process.returncode:raise RuntimeError(process.stderr)
 result=json.loads(process.stdout)
 return {'schema':1,'referenceZIP':str(archive.relative_to(repo)),'referenceZIPsha256':ZIP_SHA,'entry':'Confectory-v480/dist/blueprint.js','entrySha256':hashlib.sha256(raw).hexdigest(),'sourceRanges':ranges,'scope':'Selected actual reference C# contract/region parsing functions; fixture signature serialization/field lookup and ID allocation; no prototype browser, compiler or runtime execution','passed':len(result['checks']),**result}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('repo',type=pathlib.Path);parser.add_argument('--output',type=pathlib.Path);args=parser.parse_args();value=run(args.repo.resolve());text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 if args.output:args.output.write_text(text)
 else:print(text,end='')
 print('PASS selected v480 C# editing contracts:',value['passed'])
