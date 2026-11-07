const wordNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main',xmlNS='http://www.w3.org/XML/1998/namespace';
const wordAll=(parent,name)=>[...parent.getElementsByTagNameNS(wordNS,name)];
function wordAtoms(paragraph){const atoms=[];let length=0;const visit=parent=>{for(const child of parent.children){if(child.namespaceURI===wordNS&&['t','tab','br','cr'].includes(child.localName)){const text=child.localName==='t'?child.textContent:child.localName==='tab'?'\t':'\n';atoms.push({node:child,text,start:length,end:length+text.length});length+=text.length}else if(child.localName!=='drawing'&&child.localName!=='object')visit(child)}};visit(paragraph);return atoms}
const wordText=paragraph=>wordAtoms(paragraph).map(atom=>atom.text).join('');
const protectedParagraph=paragraph=>{if(['fldChar','instrText','delText','ins','del','sdt'].some(name=>wordAll(paragraph,name).length))return true;for(let node=paragraph;node;node=node.parentElement)if(node.namespaceURI===wordNS&&node.localName==='sdt')return true;return false;};
function setWordText(textNode,text){
 const document=textNode.ownerDocument,parts=text.split(/(\n|\t)/),fragment=document.createDocumentFragment();
 for(const part of parts){const child=document.createElementNS(wordNS,part==='\n'?'w:br':part==='\t'?'w:tab':'w:t');if(part!=='\n'&&part!=='\t'){child.textContent=part;child.setAttributeNS(xmlNS,'xml:space','preserve')}fragment.append(child)}textNode.replaceWith(fragment);
}
function changeWordParagraph(paragraph,next){
 const atoms=wordAtoms(paragraph),previous=atoms.map(atom=>atom.text).join('');if(previous===next)return;
 let prefix=0;while(prefix<previous.length&&prefix<next.length&&previous[prefix]===next[prefix])prefix++;
 if(prefix&&/[\uD800-\uDBFF]/.test(previous[prefix-1]))prefix--;
 let suffix=0;while(suffix<previous.length-prefix&&suffix<next.length-prefix&&previous[previous.length-1-suffix]===next[next.length-1-suffix])suffix++;
 if(suffix&&/[\uDC00-\uDFFF]/.test(previous[previous.length-suffix]))suffix--;
 const end=previous.length-suffix,inserted=next.slice(prefix,next.length-suffix),anchor=atoms.find(atom=>atom.node.localName==='t'&&prefix>=atom.start&&prefix<=atom.end);let insertedAtAnchor=false;
 for(const atom of atoms){if(atom.node.localName==='t'){const before=atom.text.slice(0,Math.max(0,Math.min(atom.text.length,prefix-atom.start))),after=atom.text.slice(Math.max(0,Math.min(atom.text.length,end-atom.start))),text=before+(atom===anchor?inserted:'')+after;if(atom===anchor)insertedAtAnchor=true;if(text!==atom.text)setWordText(atom.node,text)}else if(atom.start>=prefix&&atom.end<=end)atom.node.remove()}
 if(!insertedAtAnchor&&inserted){const document=paragraph.ownerDocument,run=document.createElementNS(wordNS,'w:r'),text=document.createElementNS(wordNS,'w:t');run.append(text);paragraph.append(run);setWordText(text,inserted)}
}

export function docxDocument(bytes){
 if(!(bytes instanceof Uint8Array)||bytes.length>2097152)throw Error('docx_xml_budget');const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);if(/<!\s*(DOCTYPE|ENTITY)\b/i.test(text))throw Error('docx_entities');const xml=new DOMParser().parseFromString(text,'application/xml');if(xml.getElementsByTagName('parsererror').length)throw Error('docx_xml');let count=0,characters=0;const pending=[[xml,0]];while(pending.length){const [node,depth]=pending.pop();if(++count>50000||depth>64||(characters+=node.nodeType===3||node.nodeType===4?node.nodeValue.length:0)>524288)throw Error('docx_xml_budget');for(const child of node.childNodes)pending.push([child,depth+1]);}const body=wordAll(xml,'body')[0];if(!body)throw Error('docx_body');return {xml,body,paragraphs:wordAll(body,'p')};
}
export function editedDocxXML(bytes,changes){
 const {xml,paragraphs}=docxDocument(bytes);let changed=false;
 for(const [key,value]of Object.entries(changes)){if(!/^p:(?:0|[1-9][0-9]{0,2}|1[0-4][0-9]{2})$/.test(key)||typeof value!=='string')throw Error('docx_changes');const paragraph=paragraphs[Number(key.slice(2))];if(!paragraph||protectedParagraph(paragraph))throw Error('docx_protected');for(const c of value){const n=c.codePointAt(0);if(n<32&&![9,10,13].includes(n)||n>=0xd800&&n<=0xdfff||n===0xfffe||n===0xffff)throw Error('docx_characters');}if(wordText(paragraph)!==value){changeWordParagraph(paragraph,value);changed=true;}}
 if(!changed)return null;const output=new TextEncoder().encode('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+new XMLSerializer().serializeToString(xml).replace(/^\s*<\?xml[^?]*\?>\s*/,''));docxDocument(output);return output;
}
export function renderDocxEditor(bytes,changes,onInput){
 const {body,paragraphs}=docxDocument(bytes),indices=new Map(paragraphs.map((p,i)=>[p,i])),root=document.createElement('article');root.className='resource-document resource-word-editor';let count=0,characters=0,tableNumber=0;const make=(tag,text)=>{if(++count>20000||(characters+=(text||'').length)>524288)throw Error('docx_dom_budget');const node=document.createElement(tag);if(text!=null)node.textContent=text;return node;};
 const field=(paragraph,label)=>{const index=indices.get(paragraph),key='p:'+index,wrapper=make('label'),input=make('textarea'),original=wordText(paragraph);wrapper.className='resource-paragraph-field';wrapper.append(make('span',label),input);input.setAttribute('aria-label',label);input.dataset.resourceDocxParagraph=key;input.rows=Math.min(8,Math.max(2,Math.ceil(original.length/45)));input.maxLength=98304;input.readOnly=index>=1500||protectedParagraph(paragraph);if(input.readOnly)input.setAttribute('aria-description','복잡한 문서 필드는 원본 프로그램에서 수정할 수 있습니다.');input.value=Object.hasOwn(changes,key)?changes[key]:original;input.oninput=()=>{if(!input.readOnly)onInput(key,input.value);};return wrapper;};
 for(const child of [...body.children].slice(0,1500))if(child.namespaceURI===wordNS&&child.localName==='p')root.append(field(child,'문단 '+(indices.get(child)+1)));else if(child.namespaceURI===wordNS&&child.localName==='tbl'){tableNumber++;const table=make('table');let rowNumber=0;for(const row of [...child.children].filter(n=>n.namespaceURI===wordNS&&n.localName==='tr').slice(0,200)){rowNumber++;const tr=make('tr');let column=0;for(const cell of [...row.children].filter(n=>n.namespaceURI===wordNS&&n.localName==='tc').slice(0,30)){column++;const td=make('td');let number=0;for(const p of [...cell.children].filter(n=>n.namespaceURI===wordNS&&n.localName==='p').slice(0,30))td.append(field(p,'표 '+tableNumber+' · '+rowNumber+'행 '+column+'열 · 문단 '+(++number)));tr.append(td);}table.append(tr);}root.append(table);}
 return root;
}
