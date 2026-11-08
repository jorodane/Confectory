// Authored list shortcuts. Editing/IME and control activation remain native.
export function resourceKeyboardAction(event){
 const target=event.target;if(event.defaultPrevented||event.isComposing||event.keyCode===229||typeof event.key!=='string'||typeof target?.closest!=='function'||target.closest('input,textarea,select,button,[contenteditable],.browser-tools,.browser-title-path,.browser-folder-tree'))return null;
 if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='a')return 'select-all';
 const actions={Enter:'open',Delete:'delete',F2:'rename',Escape:'clear'},action=Object.hasOwn(actions,event.key)?actions[event.key]:null;return action||null;
}
