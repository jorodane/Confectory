// Typed values keep numeric source tokens. Never round an unedited long through Number.
export function parseTypedJson(source){
 if(typeof source!=='string'||source.length>1048576)throw Error('값의 크기를 확인해 주세요.');let at=0,nodes=0;
 const whitespace=()=>{while(/[\t\n\r ]/.test(source[at]||'!'))at++;};
 const string=()=>{const start=at++;while(at<source.length){const c=source[at++];if(c==='\\'){at++;continue;}if(c==='"'){const raw=source.slice(start,at);return {kind:'string',raw,value:JSON.parse(raw)};}}throw Error('글자 값을 확인해 주세요.');};
 function value(depth=0){whitespace();if(depth>64||++nodes>4096)throw Error('값의 구조가 너무 큽니다.');const c=source[at];
  if(c==='"')return string();
  if(c==='['){at++;const items=[];whitespace();if(source[at]!==']')for(;;){items.push(value(depth+1));whitespace();if(source[at]!==',')break;at++;}if(source[at++]!==']')throw Error('배열 값을 확인해 주세요.');return {kind:'array',items};}
  if(c==='{'){at++;const entries=[],names=new Set();whitespace();if(source[at]!=='}')for(;;){whitespace();if(source[at]!=='"')throw Error('속성 이름을 확인해 주세요.');const key=string();if(names.has(key.value))throw Error('중복된 속성 이름이 있습니다.');names.add(key.value);whitespace();if(source[at++]!==':')throw Error('속성 값을 확인해 주세요.');entries.push([key.value,value(depth+1)]);whitespace();if(source[at]!==',')break;at++;}if(source[at++]!=='}')throw Error('복합값을 확인해 주세요.');return {kind:'object',entries};}
  const token=source.slice(at).match(/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/)?.[0];if(!token)throw Error('값을 확인해 주세요.');at+=token.length;return {kind:token==='null'?'null':token==='true'||token==='false'?'boolean':'number',raw:token};
 }
 const result=value();whitespace();if(at!==source.length)throw Error('값 뒤의 내용을 확인해 주세요.');return result;
}
export const printTypedJson=node=>node.kind==='array'?'['+node.items.map(printTypedJson).join(',')+']':node.kind==='object'?'{'+node.entries.map(([key,value])=>JSON.stringify(key)+':'+printTypedJson(value)).join(',')+'}':node.raw;
export function typedAt(node,path){for(const key of path){node=typeof key==='number'&&node?.kind==='array'?node.items[key]:typeof key==='string'&&node?.kind==='object'?node.entries.find(([name])=>name===key)?.[1]:undefined;}return node;}
export function replaceTypedAt(node,path,value){const root=structuredClone(node);if(!path.length)return structuredClone(value);const parent=typedAt(root,path.slice(0,-1)),key=path.at(-1);if(typeof key==='number'&&Number.isInteger(key)&&parent?.kind==='array'&&key>=0&&key<parent.items.length)parent.items[key]=structuredClone(value);else if(typeof key==='string'&&parent?.kind==='object'){const entry=parent.entries.find(([name])=>name===key);if(entry)entry[1]=structuredClone(value);else parent.entries.push([key,structuredClone(value)]);}else throw Error('현재 값의 경로를 확인해 주세요. 입력은 유지됩니다.');return root;}
