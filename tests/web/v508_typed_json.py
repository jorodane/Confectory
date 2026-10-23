"""Lossless value editing, no backend/account calls."""
from pathlib import Path
import subprocess,sys
repo=Path(sys.argv[1]).resolve();script=(repo/'examples/editor-home/ui/typed-json.js').read_text().replace('export ','')
import json
fixture='{"large":9223372036854775804,"array":[9223372036854775807,-9223372036854775808,1.2300e+17],"한글":'+json.dumps('따옴표 "\n',ensure_ascii=False)+',"__proto__":{"safe":true}}'
script+='const input='+json.dumps(fixture,ensure_ascii=False)+';\n'
script+=r'''const assert=(value,reason)=>{if(!value)throw Error(reason)},checks=[];
const source=parseTypedJson(input),initial=printTypedJson(source);assert(initial.includes('9223372036854775804'),'large rounded');const next=replaceTypedAt(source,['array',1],parseTypedJson('17'));assert(printTypedJson(next).includes('[9223372036854775807,17,1.2300e+17]'),'sibling tokens changed');assert(printTypedJson(source)===initial,'source mutated');assert(typedAt(next,['__proto__','safe']).raw==='true','prototype key');checks.push('nested editing preserves long bounds, untouched exponent tokens, escaped Korean, prototype-named data and immutable source');
const list=parseTypedJson('[9223372036854775807,2,3]');list.items.push(parseTypedJson('4'));list.items.splice(1,1);list.items.unshift(list.items.pop());assert(printTypedJson(list)==='[4,9223372036854775807,3]','array rounded');checks.push('array insertion/removal/reordering preserve all untouched numeric tokens');
for(const raw of ['{"x":1,"x":2}','[1,]','[01]','falsex','"'+String.fromCharCode(0)+'"','['.repeat(66)+'0'+']'.repeat(66)]){let failed=false;try{parseTypedJson(raw)}catch{failed=true}assert(failed,'invalid accepted '+raw.slice(0,30))}checks.push('duplicate keys, invalid syntax and excessive nesting reject');
console.log(JSON.stringify({checks,controlledCodec:true},null,2));
'''
p=subprocess.run(['node','--input-type=module','-e',script],capture_output=True,text=True);print(p.stdout);print(p.stderr,end='');raise SystemExit(p.returncode)
