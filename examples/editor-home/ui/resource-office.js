import {officeExtensions} from './resource-office-zip.js';
const localNodes=(node,name)=>[...node.getElementsByTagNameNS('*',name)];
let views=0;
function builder(){let count=0,characters=0;const make=(tag,text=null,className='')=>{if(++count>20000||(characters+=(text||'').length)>524288)throw Error('office_dom_budget');const node=document.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node;};make.text=text=>{if(++count>20000||(characters+=text.length)>524288)throw Error('office_dom_budget');return document.createTextNode(text);};return make;}
function renderOfficeFiles({files,extension,controls,owns,onError}){
 const parts=new Map(),parsed=new Map();let bytes=0,nodes=0,characters=0;
 if(!Array.isArray(files)||!files.length||files.length>64)throw Error('office_result');
 for(const row of files){if(!Array.isArray(row)||row.length!==2||typeof row[0]!=='string'||!(row[1]instanceof ArrayBuffer)||row[1].byteLength>2097152||parts.has(row[0])||(bytes+=row[1].byteLength)>4194304)throw Error('office_result');parts.set(row[0],row[1]);}
 const xml=path=>{
  if(parsed.has(path))return parsed.get(path);const raw=parts.get(path);if(!raw)return null;const text=new TextDecoder('utf-8',{fatal:true}).decode(raw);if(/<!\s*(DOCTYPE|ENTITY)\b/i.test(text))throw Error('office_xml_entities');
  const doc=new DOMParser().parseFromString(text,'application/xml');if(doc.getElementsByTagName('parsererror').length)throw Error('office_xml');const pending=[[doc,0]];
  while(pending.length){const [node,depth]=pending.pop();if(++nodes>50000||depth>64||(characters+=(node.nodeType===3||node.nodeType===4?node.nodeValue.length:0))>524288)throw Error('office_xml_budget');for(const child of node.childNodes)pending.push([child,depth+1]);}parsed.set(path,doc);return doc;
 };
 const paragraph=(source,make)=>{
  const style=localNodes(source,'pStyle')[0]?.getAttribute('w:val')||'',heading=style.match(/heading\s*([1-6])/i),node=make(heading?'h'+Math.min(6,Number(heading[1])+1):/title/i.test(style)?'h2':'p');if(localNodes(source,'numPr').length)node.classList.add('resource-document-list-item');
  for(const run of localNodes(source,'r')){const span=make('span');for(const child of run.childNodes){if(child.localName==='t')span.append(make.text(child.textContent));else if(child.localName==='br'||child.localName==='cr')span.append(make('br'));else if(child.localName==='tab')span.append(make.text('\t'));}
   const properties=localNodes(run,'rPr')[0];for(const [name,css,value]of[['b','fontWeight','700'],['i','fontStyle','italic'],['u','textDecoration','underline']]){const property=properties&&localNodes(properties,name)[0];if(property&&!['0','false','none'].includes(property.getAttribute('w:val')))span.style[css]=value;}if(span.childNodes.length)node.append(span);
  }if(!node.childNodes.length)node.append(make('br'));return node;
 };
 let content;
 if(extension==='docx'){
  const doc=xml('word/document.xml'),body=doc&&localNodes(doc,'body')[0];if(!body)throw Error('office_body');const make=builder();content=make('article',null,'resource-document');let cells=0;
  for(const child of [...body.children].slice(0,1500)){
   if(child.localName==='p')content.append(paragraph(child,make));
   else if(child.localName==='tbl'){const table=make('table');for(const row of [...child.children].filter(node=>node.localName==='tr').slice(0,200)){const tr=make('tr');for(const cell of [...row.children].filter(node=>node.localName==='tc').slice(0,30)){if(++cells>5000)break;const td=make('td');for(const p of [...cell.children].filter(node=>node.localName==='p').slice(0,30))td.append(paragraph(p,make));tr.append(td);}table.append(tr);}content.append(table);}
  }
 }else if(extension==='xlsx'){
  const workbook=xml('xl/workbook.xml'),relationships=xml('xl/_rels/workbook.xml.rels'),shared=xml('xl/sharedStrings.xml'),strings=shared?localNodes(shared,'si').slice(0,100000).map(node=>localNodes(node,'t').map(text=>text.textContent).join('')):[],relations=new Map();
  for(const relation of relationships?localNodes(relationships,'Relationship'):[]){const target=relation.getAttribute('Target')||'';if(relation.getAttribute('TargetMode')==='External')continue;const path=target.startsWith('/xl/')?target.slice(1):target.startsWith('worksheets/')?'xl/'+target:null;if(path&&/^xl\/worksheets\/sheet\d+\.xml$/.test(path))relations.set(relation.getAttribute('Id'),path);}
  const sheets=(workbook?localNodes(workbook,'sheet'):[]).slice(0,30).map(node=>({name:node.getAttribute('name'),path:relations.get(node.getAttribute('r:id'))})).filter(sheet=>parts.has(sheet.path));if(!sheets.length)throw Error('office_sheets');const make=builder();content=make('div',null,'resource-spreadsheet');const select=make('select');select.setAttribute('aria-label','워크시트');select.dataset.resourceOfficeSheet='';sheets.forEach((sheet,index)=>{const option=make('option',sheet.name||'');option.value=index;select.append(option);});controls.append(select);
  const render=()=>{if(!owns())return;try{const sheet=sheets[Number(select.value)];if(!sheet)throw Error('office_sheet');const doc=xml(sheet.path);if(!doc)throw Error('office_sheet');const create=builder(),table=create('table'),rows=localNodes(doc,'row').slice(0,200);let columns=0;
    const data=rows.map(row=>{const values=new Map();for(const cell of [...row.children].filter(node=>node.localName==='c')){const letters=(cell.getAttribute('r')||'A1').match(/^[A-Z]+/)?.[0]||'A',column=[...letters].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)-1;if(column>=30)continue;columns=Math.max(columns,column+1);const raw=localNodes(cell,'v')[0]?.textContent||'',type=cell.getAttribute('t'),formula=localNodes(cell,'f')[0]?.textContent;values.set(column,type==='s'?strings[Number(raw)]||'':type==='inlineStr'?localNodes(cell,'t').map(node=>node.textContent).join(''):type==='b'?raw==='1'?'TRUE':'FALSE':raw||(formula?'='+formula:''));}return {number:row.getAttribute('r'),values};});
    const head=create('tr');head.append(create('th',''));for(let column=0;column<columns;column++){let n=column+1,label='';while(n){n--;label=String.fromCharCode(65+n%26)+label;n=Math.floor(n/26);}head.append(create('th',label));}table.append(head);for(const row of data){const tr=create('tr');tr.append(create('th',row.number||''));for(let column=0;column<columns;column++)tr.append(create('td',row.values.get(column)||''));table.append(tr);}content.replaceChildren(table);
   }catch{onError();}};select.onchange=render;render();
 }else if(extension==='pptx'){
  const slides=[...parts.keys()].filter(path=>/^ppt\/slides\/slide\d+\.xml$/.test(path)).sort((a,b)=>Number(a.match(/slide(\d+)\.xml/)[1])-Number(b.match(/slide(\d+)\.xml/)[1])).slice(0,30);if(!slides.length)throw Error('office_slides');const make=builder();content=make('article',null,'resource-document');slides.forEach((path,index)=>{const section=make('section',null,'resource-document-slide');section.append(make('small','슬라이드 '+(index+1)));const doc=xml(path);for(const p of localNodes(doc,'p').slice(0,1500)){const text=localNodes(p,'t').map(node=>node.textContent).join('');if(text)section.append(make('p',text));}content.append(section);});
 }else{
  const doc=xml('content.xml');if(!doc)throw Error('office_body');const make=builder();content=make('article',null,'resource-document');for(const p of localNodes(doc,'p').slice(0,1500))content.append(make('p',p.textContent));
 }
 return {content,dispose:()=>{parts.clear();parsed.clear();}};
}
export function mountResourceOffice({preview,toolbar,controls,status,bytes,extension,active,onError,onDetached}){
 if(!officeExtensions.has(extension))return null;if(!active()){onDetached?.();return ()=>{};}if(views>=4)throw Error('office_view_budget');views++;let disposed=false,worker=null,timer=null,observer=null,renderer=null;
 const dispose=()=>{if(disposed)return;disposed=true;views--;clearTimeout(timer);observer?.disconnect();if(worker){worker.onmessage=null;worker.onerror=null;worker.terminate();worker=null;}renderer?.dispose();renderer=null;controls.replaceChildren();preview.replaceChildren();};
 const fail=()=>{if(disposed)return;const current=active();dispose();if(current)onError();else onDetached?.();};
 try{
  worker=new Worker(new URL('./resource-office-worker.js',import.meta.url),{type:'module',name:'resource-office-preview'});timer=setTimeout(fail,5000);
  worker.onerror=event=>{event.preventDefault();fail();};worker.onmessage=event=>{
   if(disposed||!worker)return;if(!active()){dispose();onDetached?.();return;}clearTimeout(timer);worker.onmessage=null;worker.onerror=null;worker.terminate();worker=null;
   try{if(event.data?.ok!==true)throw Error('office_parse');renderer=renderOfficeFiles({files:event.data.files,extension,controls,owns:()=>!disposed&&active(),onError:fail});if(disposed){renderer.dispose();return;}preview.className='resource-preview is-document-preview';preview.replaceChildren(renderer.content);preview.setAttribute('aria-busy','false');toolbar.textContent=extension.toUpperCase()+(extension==='xlsx'?' 값 미리보기':' 텍스트 미리보기');status.textContent=extension==='xlsx'?'워크시트당 최대 200행 · 30열':'문서 내용 미리보기 · 원본 서식과 다를 수 있습니다.';}catch{fail();}
  };
  observer=new MutationObserver(()=>{if(!disposed&&!active()){dispose();onDetached?.();}});observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','class']});worker.postMessage({bytes:bytes.buffer,extension},[bytes.buffer]);return dispose;
 }catch(error){dispose();throw error;}
}
