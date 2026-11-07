import {pdfCanvasPlan} from './resource-pdf-policy.js';
let library,views=0;
export function mountResourcePDF({preview,toolbar,controls,status,bytes,item,active,onError,onDetached}){
 if(!(bytes instanceof Uint8Array)||bytes.length>1048576||new TextDecoder('ascii').decode(bytes.subarray(0,5))!=='%PDF-')throw Error('pdf_input');
 if(!active()){onDetached?.();return ()=>{};}if(views>=2)throw Error('pdf_view_budget');views++;
 let disposed=false,worker=null,bridge=null,documentTask=null,pdf=null,renderTask=null,canvas=null,observer=null,visibility=null,frame=0,timer=null,releaseTimer=null,version=0,pageNumber=1,zoom='fit',lastWidth=0,released=false;
 const owns=()=>!disposed&&active(),clearCanvas=node=>{if(node){node.width=0;node.height=0;node.remove();}},release=()=>{if(released)return;released=true;clearTimeout(releaseTimer);try{bridge?.destroy();}catch{}bridge=null;if(worker){worker.onerror=null;worker.terminate();worker=null;}views--;};
 const dispose=()=>{
  if(disposed)return;disposed=true;version++;clearTimeout(timer);cancelAnimationFrame(frame);observer?.disconnect();visibility?.disconnect();renderTask?.cancel();renderTask=null;clearCanvas(canvas);canvas=null;controls.replaceChildren();preview.replaceChildren();pdf=null;
  const task=documentTask;documentTask=null;releaseTimer=setTimeout(release,500);if(task){try{Promise.resolve(task.destroy()).catch(()=>{}).finally(release);}catch{release();}}else release();
 };
 const fail=reason=>{if(disposed)return;const current=active();dispose();if(current)onError(reason);else onDetached?.();};
 const deadline=()=>{clearTimeout(timer);timer=setTimeout(()=>fail('timeout'),10000);};
 const make=(tag,text=null)=>{const node=document.createElement(tag);if(text!=null)node.textContent=text;return node;};
 const load=async()=>{
  const lib=await(library??=import('./assets/vendor/pdfjs-dist-4.10.38/build/pdf.min.mjs').catch(error=>{library=null;throw error;}));if(!owns())return dispose();
  worker=new Worker(new URL('./resource-pdf-worker.js',import.meta.url),{type:'module',name:'resource-pdf-preview'});worker.onerror=event=>{event.preventDefault();fail('worker');};bridge=new lib.PDFWorker({port:worker});
  documentTask=lib.getDocument({data:bytes,worker:bridge,cMapUrl:new URL('./assets/vendor/pdfjs-dist-4.10.38/cmaps/',import.meta.url).href,cMapPacked:true,standardFontDataUrl:new URL('./assets/vendor/pdfjs-dist-4.10.38/standard_fonts/',import.meta.url).href,useWorkerFetch:true,isEvalSupported:false,enableXfa:false,disableRange:true,disableStream:true,disableAutoFetch:true,withCredentials:false,maxImageSize:16777216,canvasMaxAreaInBytes:16777216,isImageDecoderSupported:false,stopAtErrors:true});
  pdf=await documentTask.promise;if(!owns())return dispose();if(!Number.isInteger(pdf.numPages)||pdf.numPages<1||pdf.numPages>1000)throw Error('pdf_page_count');
  const previous=make('button','‹'),next=make('button','›'),pages=make('span'),select=make('select');previous.type=next.type='button';previous.setAttribute('aria-label','이전 페이지');next.setAttribute('aria-label','다음 페이지');pages.setAttribute('aria-live','polite');pages.dataset.resourcePdfPages='';select.setAttribute('aria-label','미리보기 배율');
  for(const[value,label]of[['fit','너비 맞춤'],['1','100%'],['1.5','150%'],['2','200%']]){const option=make('option',label);option.value=value;select.append(option);}controls.append(previous,pages,next,select);preview.className='resource-preview is-pdf-preview';
  const render=async()=>{
   if(!owns())return;const token=++version;renderTask?.cancel();renderTask=null;clearCanvas(canvas);canvas=null;preview.replaceChildren();preview.setAttribute('aria-busy','true');previous.disabled=pageNumber===1;next.disabled=pageNumber===pdf.numPages;pages.textContent=pageNumber+' / '+pdf.numPages;deadline();let page=null,task=null,paint=null;
   try{
    page=await pdf.getPage(pageNumber);if(!owns()||token!==version)return;const natural=page.getViewport({scale:1}),plan=pdfCanvasPlan(natural.width,natural.height,preview.clientWidth,zoom,devicePixelRatio||1),viewport=page.getViewport({scale:plan.scale});paint=make('canvas');paint.className='resource-pdf-canvas';paint.dataset.resourcePdfCanvas='';paint.width=plan.canvasWidth;paint.height=plan.canvasHeight;paint.style.width=plan.width+'px';paint.style.height=plan.height+'px';paint.setAttribute('role','img');paint.setAttribute('aria-label',item.name+' · '+pageNumber+'페이지');
    task=page.render({canvasContext:paint.getContext('2d'),viewport,transform:[plan.density,0,0,plan.density,0,0],annotationMode:lib.AnnotationMode.DISABLE});renderTask=task;await task.promise;if(!owns()||token!==version)return;
    clearTimeout(timer);canvas=paint;paint=null;const wrapper=make('div');wrapper.className='resource-pdf-page';wrapper.append(canvas);preview.replaceChildren(wrapper);preview.setAttribute('aria-busy','false');toolbar.textContent='PDF 미리보기';status.textContent=pdf.numPages+'페이지 · 읽기 전용';
   }catch(error){if(owns()&&token===version&&error.name!=='RenderingCancelledException')fail(error.name==='PasswordException'?'password':'render');}
   finally{if(renderTask===task)renderTask=null;clearCanvas(paint);try{page?.cleanup();}catch{}}
  };
  const schedule=()=>{if(!owns())return;cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{frame=0;void render();});};
  previous.onclick=()=>{if(owns()&&pageNumber>1){pageNumber--;schedule();}};next.onclick=()=>{if(owns()&&pageNumber<pdf.numPages){pageNumber++;schedule();}};select.onchange=()=>{if(owns()){zoom=select.value;schedule();}};
  lastWidth=preview.clientWidth;observer=new ResizeObserver(()=>{const width=preview.clientWidth;if(owns()&&zoom==='fit'&&Math.abs(width-lastWidth)>1){lastWidth=width;schedule();}});observer.observe(preview);await render();
 };
 try{visibility=new MutationObserver(()=>{if(!disposed&&!active()){dispose();onDetached?.();}});visibility.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','class']});deadline();void load().catch(error=>{if(!disposed)fail(error.name==='PasswordException'?'password':'load');});return dispose;}catch(error){dispose();throw error;}
}
