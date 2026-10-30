// Text edits preserve raw untouched spans, including newlines inside C# literals.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const source=fs.readFileSync(process.argv[2]+'/examples/editor-home/ui/feature-authoring.js','utf8');
const start=source.indexOf('function mountBlueprintScriptEditor('),end=source.indexOf('function blueprintControlIconMarkup',start);assert(start>=0&&end>start);
const input={value:'',selectionStart:0,selectionEnd:0,scrollLeft:0,scrollTop:0,setSelectionRange(a,b){this.selectionStart=a;this.selectionEnd=b;},focus(){}},highlight={style:{}},status={},error={hidden:true},root={querySelector(key){return {'[data-code-source]':input,'[data-code-highlight]':highlight,'[data-code-status]':status,'[data-code-error]':error}[key];}};
const scope={esc:s=>s};vm.createContext(scope);vm.runInContext(source.slice(start,end),scope);
const original='// 😀\r\nstring s=@"a\r\nb";\nreturn 1;\r\n';
const editor=scope.mountBlueprintScriptEditor(root,[{text:'public long Invoke()\n{\n'},{id:'body',text:original},{text:'\n}'}]);assert.equal(editor.sections().body,original);
function replace(before,after){const at=input.value.indexOf(before);assert(at>=0);input.setSelectionRange(at,at+before.length);input.onbeforeinput({inputType:'insertText',preventDefault(){throw Error('editable range blocked');}});input.value=input.value.slice(0,at)+after+input.value.slice(at+before.length);input.setSelectionRange(at+after.length,at+after.length);input.oninput();}
replace('return 1;','return 2;');assert.equal(editor.sections().body,original.replace('return 1;','return 2;'));
const key=k=>input.onkeydown({ctrlKey:true,key:k,preventDefault(){},stopPropagation(){}});key('z');assert.equal(editor.sections().body,original);key('y');assert.equal(editor.sections().body,original.replace('return 1;','return 2;'));
replace('string s=@"a\nb";','string s=@"a\nNEW\nb";');assert.equal(editor.sections().body,'// 😀\r\nstring s=@"a\r\nNEW\nb";\nreturn 2;\r\n');key('z');assert.equal(editor.sections().body,original.replace('return 1;','return 2;'));
const prior=editor.sections().body;input.value=input.value.replace('public long','private long');input.oninput();assert.equal(editor.sections().body,prior);assert(input.value.startsWith('public long'));
console.log('PASS partial text edits and Undo/Redo retain raw CRLF/mixed endings and literal bytes; fixed declarations remain protected');
