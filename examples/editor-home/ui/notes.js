// Rich notes remain private presentation. Parse incoming HTML inertly and copy only text formatting.
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function cleanNoteHtml(value){
 const source=document.createElement('template'),result=document.createElement('div');source.innerHTML=String(value||'');
 const allowed=new Set(['B','STRONG','I','EM','U','S','STRIKE','UL','OL','LI','P','DIV','BR','SPAN','H1','H2','H3','BLOCKQUOTE','FONT']),blocked=new Set(['SCRIPT','STYLE','IFRAME','OBJECT','EMBED','LINK','META','IMG','VIDEO','AUDIO','SVG','MATH','TEMPLATE']);
 function copy(node,parent){
  if(node.nodeType===Node.TEXT_NODE){parent.append(document.createTextNode(node.textContent));return;}if(node.nodeType!==Node.ELEMENT_NODE||blocked.has(node.tagName))return;
  let target=parent;if(allowed.has(node.tagName)){
   target=document.createElement(node.tagName==='FONT'?'span':node.tagName.toLowerCase());parent.append(target);
   for(const property of ['color','background-color','font-size','font-weight','font-style','text-decoration','text-decoration-line','text-align']){
    const value=node.style.getPropertyValue(property);if(!value)continue;
    if(['color','background-color'].includes(property)&&CSS.supports('color',value))target.style.setProperty(property,value);
    else if(property==='font-size'){const sizes={'xx-small':10,'x-small':10,small:13,medium:16,large:18,'x-large':24,'xx-large':32,'xxx-large':48},pixels=/^([\d.]+)px$/.exec(value),size=sizes[value]??(pixels?Number(pixels[1]):0);if(size>=8&&size<=72)target.style.fontSize=size+'px';}
    else if(property==='font-weight'&&/^(normal|bold|[1-9]00)$/.test(value))target.style.fontWeight=value;
    else if(property==='font-style'&&/^(normal|italic)$/.test(value))target.style.fontStyle=value;
    else if((property==='text-decoration'||property==='text-decoration-line')&&/^(none|underline|line-through)( (underline|line-through))*$/.test(value))target.style.textDecoration=value;
    else if(property==='text-align'&&/^(left|center|right|justify)$/.test(value))target.style.textAlign=value;
   }
   if(node.tagName==='FONT'){const color=node.getAttribute('color'),size=Number(node.getAttribute('size'));if(color&&CSS.supports('color',color))target.style.color=color;if(size>=1&&size<=7)target.style.fontSize=[0,10,13,16,18,24,32,48][size]+'px';}
  }
  for(const child of node.childNodes)copy(child,target);
 }
 for(const node of source.content.childNodes)copy(node,result);return result.innerHTML;
}
export function noteHtml(item){return cleanNoteHtml(typeof item.richText==='string'?item.richText:esc(item.text||'').replace(/\n/g,'<br>'));}
function plainNote(html){const plain=document.createElement('div');plain.innerHTML=html;plain.querySelectorAll('br').forEach(node=>node.replaceWith('\n'));plain.querySelectorAll('p,div,li,h1,h2,h3,blockquote').forEach(node=>node.append('\n'));return plain.textContent.replace(/\n{3,}/g,'\n\n').trimEnd();}
export function noteMarkup(item){
 const commands=[['bold','B','굵게'],['italic','I','기울임'],['underline','U','밑줄'],['strikeThrough','S','취소선'],['insertUnorderedList','•','글머리 목록'],['insertOrderedList','1.','번호 목록'],['removeFormat','T×','글자 서식 지우기']];
 return '<div class="workspace-note-composer"><div class="workspace-note-toolbar" role="toolbar" aria-label="메모 글자 서식">'+commands.map(([command,label,title])=>'<button type="button" data-note-command="'+command+'" aria-label="'+title+'" title="'+title+'"'+(['bold','italic','underline','strikeThrough'].includes(command)?' aria-pressed="false"':'')+'>'+label+'</button>').join('')+'<select data-note-size aria-label="메모 글자 크기">'+[10,13,16,18,24,32,48].map((size,i)=>'<option value="'+(i+1)+'"'+(size===13?' selected':'')+'>'+size+'px</option>').join('')+'</select><input type="color" data-note-color value="#e9d9b9" aria-label="메모 글자 색상"></div><div class="workspace-note-editor" contenteditable="true" role="textbox" aria-multiline="true" aria-label="메모 내용" data-note-editor="'+esc(item.id)+'" data-placeholder="메모를 남겨보세요…">'+noteHtml(item)+'</div></div>';
}
export function bindNoteEditor(root,item,persist,canEdit=()=>true){
 const editor=root.querySelector('[data-note-editor]'),toolbar=root.querySelector('.workspace-note-toolbar');let range=null;
 function capture(){
  const selection=getSelection(),inside=selection.rangeCount&&editor.contains(selection.anchorNode);if(inside)range=selection.getRangeAt(0).cloneRange();
  let sample=inside?selection.anchorNode:null;if(sample?.nodeType===Node.ELEMENT_NODE)sample=sample.childNodes[Math.min(selection.anchorOffset,sample.childNodes.length-1)]||sample;
  if(!sample||sample===editor){const walker=document.createTreeWalker(editor,NodeFilter.SHOW_TEXT);let text;while(text=walker.nextNode())if(text.textContent.trim()){sample=text;break;}}
  const element=sample?.nodeType===Node.TEXT_NODE?sample.parentElement:sample||editor,style=getComputedStyle(element),sizes=[10,13,16,18,24,32,48],nativeSize=inside?Number(document.queryCommandValue('fontSize')):0,size=nativeSize>=1&&nativeSize<=7?sizes[nativeSize-1]:parseFloat(style.fontSize),sizeInput=toolbar.querySelector('[data-note-size]');
  sizeInput.querySelector('[data-note-current-size]')?.remove();const index=sizes.indexOf(size);if(index>=0)sizeInput.value=String(index+1);else{const option=document.createElement('option');option.dataset.noteCurrentSize='';option.disabled=true;option.selected=true;option.value='current';option.textContent=size+'px';sizeInput.append(option);}
  const color=inside?document.queryCommandValue('foreColor')||style.color:style.color,rgb=/rgba?\(\s*(\d+)[, ]+\s*(\d+)[, ]+\s*(\d+)/.exec(color),hex=/^#[0-9a-f]{6}$/i.test(color)?color:rgb?'#'+rgb.slice(1,4).map(n=>Number(n).toString(16).padStart(2,'0')).join(''):null;if(hex)toolbar.querySelector('[data-note-color]').value=hex;
  const decorations=[];for(let node=element;node&&editor.contains(node);node=node.parentElement)decorations.push(getComputedStyle(node).textDecorationLine);
  const states={bold:Number(style.fontWeight)>=600||style.fontWeight==='bold',italic:style.fontStyle==='italic',underline:decorations.some(value=>value.includes('underline')),strikeThrough:decorations.some(value=>value.includes('line-through'))};
  for(const button of toolbar.querySelectorAll('[aria-pressed]'))button.setAttribute('aria-pressed',String(inside?document.queryCommandState(button.dataset.noteCommand):states[button.dataset.noteCommand]));
 }
 function save(){if(!canEdit()){editor.contentEditable='false';return;}item.richText=cleanNoteHtml(editor.innerHTML);item.text=plainNote(item.richText);persist();capture();}
 function run(command,value=null){if(!canEdit()){editor.contentEditable='false';return;}editor.focus({preventScroll:true});if(range&&editor.contains(range.commonAncestorContainer)){const selection=getSelection();selection.removeAllRanges();selection.addRange(range);}document.execCommand('styleWithCSS',false,true);document.execCommand(command,false,value);save();}
 editor.onbeforeinput=event=>{if(!canEdit()){event.preventDefault();editor.contentEditable='false';}};editor.oninput=save;editor.onmouseup=editor.onkeyup=editor.onfocus=capture;
 editor.onkeydown=event=>{if(!((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='f'))event.stopPropagation();};
 toolbar.onpointerdown=event=>{event.stopPropagation();if(event.target.closest('button'))event.preventDefault();};
 for(const button of toolbar.querySelectorAll('[data-note-command]'))button.onclick=event=>{event.stopPropagation();run(button.dataset.noteCommand);};
 toolbar.querySelector('[data-note-size]').onchange=event=>run('fontSize',event.target.value);toolbar.querySelector('[data-note-color]').oninput=event=>run('foreColor',event.target.value);
 editor.onpaste=event=>{event.preventDefault();const html=event.clipboardData.getData('text/html'),text=event.clipboardData.getData('text/plain');run('insertHTML',html?cleanNoteHtml(html):esc(text).replace(/\n/g,'<br>'));};
 editor.ondragover=event=>{event.preventDefault();event.stopPropagation();};editor.ondrop=event=>{event.preventDefault();event.stopPropagation();const html=event.dataTransfer.getData('text/html'),text=event.dataTransfer.getData('text/plain');if(html||text)run('insertHTML',html?cleanNoteHtml(html):esc(text).replace(/\n/g,'<br>'));};
 capture();return {capture};
}
export function applyNoteTitle(element,item){const label=element.querySelector('.workspace-item-name');if(!label)return;const style=item.titleStyle;label.style.fontSize=Number.isFinite(style?.size)&&style.size>=8&&style.size<=72?style.size+'px':'';label.style.color=/^#[0-9a-f]{6}$/i.test(style?.color||'')?style.color:'';}
