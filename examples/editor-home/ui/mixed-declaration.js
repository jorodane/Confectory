import {parseTypedJson,printTypedJson} from './typed-json.js';

// Data adapters only. The original controls and the server's ownership/CAS
// validation remain authoritative; this module creates no grants or writes.
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export const mixedFieldContract=row=>row?{kind:row.kind,cardinality:row.cardinality,type:row.type}:null;
const rowAt=(schema,path)=>schema.rows?.find(row=>same(row.path,path));
export function captureMixedCell(value,schema,valueJson){
 if(value.revision!==schema.revision||value.hash!==schema.textHash||Object.keys(value.invalidChildren||{}).length)throw Error('편집 기준이나 입력 형식을 확인해 주세요. 모든 입력은 유지됩니다.');
 if(value.kind==='schema-field')return {type:'schema-field',path:structuredClone(value.path),contract:structuredClone(value.contract),schema:value.schema,schemaHash:value.schemaHash,nativeType:value.nativeType};
 if(value.kind==='description')return {type:'description',text:value.text};
 if(value.kind==='parent')return {type:'parent',value:value.value};
 if(value.kind==='modules')return {type:'modules',ids:structuredClone(value.value)};
 if(value.kind==='definition'){if(!/^[A-Za-z_][A-Za-z_0-9]*$/.test(value.name))throw Error('새 속성 이름을 확인해 주세요. 입력은 유지됩니다.');return {type:'definition',name:value.name,nativeType:value.type,valueJson:valueJson({value:value.text,type:value.type==='bool'?'checkbox':'text',checked:value.text==='true'},{type:value.type,inputKind:value.type==='bool'?'boolean':value.type==='string'?'text':'number',kind:'general',cardinality:'single'})};}
 if(value.dataType==='bool'&&!['true','false'].includes(value.text))throw Error('조건 값은 true 또는 false로 입력해 주세요. 원문은 유지됩니다.');
 const row=rowAt(schema,value.path);if(!['field','unset'].includes(value.kind)||!row?.writable||!['general','compound','reference'].includes(row.kind)||value.kind==='unset'&&!row.localOverride)throw Error('이 속성 입력은 함께 저장할 수 없어요. 입력은 유지됩니다.');
 const change={type:value.kind==='unset'?'unset':'data',path:structuredClone(value.path),contract:mixedFieldContract(row)};
 if(value.kind==='field')change.valueJson=value.wireJson?printTypedJson(parseTypedJson(value.text)):valueJson({value:value.text,type:(value.dataType?value.dataType==='bool'?'boolean':value.dataType==='string'?'text':'number':row.inputKind)==='boolean'?'checkbox':'text',checked:value.text==='true'},value.dataType?{...row,type:value.dataType,inputKind:value.dataType==='bool'?'boolean':value.dataType==='string'?'text':'number'}:row);return change;
}
function capturedValue(value,type){if(value.wireJson)return printTypedJson(parseTypedJson(value.text));if(type==='string')return JSON.stringify(value.text);if(type==='bool'){if(!['true','false'].includes(value.text))throw Error('조건 값 확인');return value.text;}const parsed=parseTypedJson(value.text.trim());if(parsed.kind!=='number')throw Error('숫자 값 확인');return printTypedJson(parsed);}
export function mixedCellMatches(key,value,change,start){
 if(!change||!key.startsWith(start))return false;
 if(value.kind==='schema-field')return key===start+'schema:'+JSON.stringify(value.path)&&same(change,{type:'schema-field',path:value.path,contract:value.contract,schema:value.schema,schemaHash:value.schemaHash,nativeType:value.nativeType});
 if(value.kind==='description')return key===start+'description'&&change.type==='description'&&change.text===value.text;
 if(value.kind==='parent')return key===start+'parent'&&change.type==='parent'&&same(change.value,value.value);
 if(value.kind==='modules')return key===start+'modules'&&change.type==='modules'&&same(change.ids,value.value);
 if(value.kind==='definition')return key.startsWith(start+'definition:')&&change.type==='definition'&&change.name===value.name&&change.nativeType===value.type&&typeof value.text==='string'&&change.valueJson===capturedValue(value,value.type);
 return ['field','unset'].includes(value.kind)&&key===start+JSON.stringify(value.path)&&same(value.path,change.path)&&(value.kind==='unset'?change.type==='unset':['scalar','data'].includes(change.type)&&typeof value.text==='string'&&change.valueJson===capturedValue(value,value.dataType??change.nativeType??change.contract?.type));
}
export function receiptFieldProof(value,change,schema){
 if(value.kind==='description'&&change?.type==='description')return {hash:schema.textHash,kind:'description'};
 if(!['field','unset'].includes(value.kind)||!same(value.path,change?.path))return null;const row=rowAt(schema,value.path),contract=change.type==='scalar'?{kind:'general',cardinality:'single',type:change.nativeType}:change.contract;
 if(!row?.writable||value.kind==='unset'&&!row.localOverride||!same(mixedFieldContract(row),contract))return null;return {hash:schema.textHash,kind:value.kind,path:structuredClone(value.path),contract:structuredClone(contract)};
}
export function restoredMixedProof(value,schema){
 const proof=value.copySavedBasis;if(!proof||proof.hash!==schema.textHash||value.hash!==proof.hash||proof.kind!==value.kind)return false;if(value.kind==='description')return true;
 const row=rowAt(schema,value.path),contract=proof.contract??{kind:'general',cardinality:'single',type:proof.nativeType};return ['field','unset'].includes(value.kind)&&same(proof.path,value.path)&&row?.writable&&(value.kind!=='unset'||row.localOverride)&&same(mixedFieldContract(row),contract);
}
