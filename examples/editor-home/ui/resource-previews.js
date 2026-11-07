import {mountResourcePDF} from './resource-pdf.js';
import {mountResourceOffice} from './resource-office.js';
import {mountResourceImage} from './resource-images.js';
import {createResourceContent} from './resource-content.js';
import {bindResourceFileNames} from './resource-browser.js';

// Authored text editing and bounded static PNG/JPEG display. Other image,
// PDF/mesh and remaining image renderers still need their lifetime integration.
const textExtensions=/\.(txt|md|markdown|json|jsonl|csv|tsv|yaml|yml|xml|html?|css|js|mjs|ts|tsx|jsx|log|ini|toml|obj|gltf|svg)$/i;
const element=(tag,text,className)=>{const node=document.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node};
export function createResourcePreviews(api){
 const content=createResourceContent(api);
 const prefix='resource-file:',idPattern=/^[a-f0-9]{32}$/,hashPattern=/^[a-f0-9]{64}$/;
 const scope=()=>api.current?.projectId||'';
 const alive=(w,token)=>w.resourcePreview===token&&token.generation===api.view.generation&&scope()===token.owner&&api.windows.get(w.key)===w&&w.el.isConnected&&!w.el.hidden;
 function retire(w){const token=w.resourcePreview;if(!token)return;w.resourcePreview=null;token.controller.abort();token.imageCleanup?.();token.officeCleanup?.();token.pdfCleanup?.();token.contentCleanup?.();token.cleanup?.();w.body.replaceChildren();}
 function title(w,item){
  w.title=item.name;w.el.setAttribute('aria-label',item.name);const caption=w.el.querySelector(':scope > .window-title .caption');
  if(caption){caption.querySelector('strong')?.remove();caption.querySelector('.resource-editor-heading')?.remove();const heading=element('span',null,'resource-editor-heading'),name=element('strong'),filename=element('span',item.name,'resource-filename');filename.dataset.resourceFullName=item.name;filename.dataset.resourceKind=item.kind;name.dataset.resourceTitle='';name.title=item.name;name.append(filename);heading.append(name,element('small',item.size+' B · 프로젝트 사본'));caption.append(heading);}
 }
 function mount(w){
  retire(w);const token={owner:scope(),generation:api.view.generation,id:w.meta.resourceId,hash:w.meta.resourceHash,name:w.resourceExpectedName??null,controller:new AbortController()};w.resourcePreview=token;
  w.el.classList.add('resource-file-editor');w.body.classList.add('resource-editor-body');
  w.body.innerHTML='<section class="resource-preview-panel" aria-label="미리보기 패널"><header class="resource-preview-toolbar"><strong data-resource-preview-title>미리보기</strong><div data-resource-preview-controls></div><div class="resource-content-actions" data-resource-content-actions></div></header><div class="resource-preview is-preview-message" aria-label="자료 미리보기" tabindex="0"><p>내용을 불러오고 있습니다…</p></div><footer class="resource-preview-status" aria-live="polite"></footer></section><aside class="resource-settings" aria-label="자료 설정"><h3>자료 설정</h3><label class="resource-name-label">파일 이름<input data-resource-setting-name aria-label="파일 이름" maxlength="180" readonly></label><small class="resource-storage-note">프로젝트에 보관된 사본입니다. 원본 파일은 바뀌지 않습니다.</small></aside>';
  const preview=w.body.querySelector('.resource-preview'),toolbar=w.body.querySelector('[data-resource-preview-title]'),status=w.body.querySelector('.resource-preview-status'),actions=w.body.querySelector('[data-resource-content-actions]');
  const message=text=>{preview.className='resource-preview is-preview-message';preview.replaceChildren(element('p',text));preview.setAttribute('aria-busy','false');};
  const target={project:w.meta.resourceOwner,id:w.meta.resourceId,hash:w.meta.resourceHash};
  const valid=()=>idPattern.test(target.id||'')&&hashPattern.test(target.hash||'')&&target.project===token.owner&&w.key===prefix+target.id;
  const read=async()=>{
   if(!alive(w,token)||token.loading)return;actions.replaceChildren();token.loading=true;preview.setAttribute('aria-busy','true');message('내용을 불러오고 있습니다…');preview.setAttribute('aria-busy','true');status.textContent='';
   try{
    if(!valid())throw Error('resource_view_owner');
    let result;for(let attempt=0;attempt<3;attempt++){try{result=await api.view.observe('readProjectResource',target,token.controller.signal);break;}catch(error){if(error.message!=='busy'||attempt===2)throw error;await new Promise(resolve=>setTimeout(resolve,50));if(!alive(w,token))return;}}if(!alive(w,token))return;
    const item=result?.item;if(result?.status!=='ready'||result.project!==token.owner||item?.id!==target.id||item.hash!==target.hash||result.encoding!=='base64url'||typeof result.data!=='string'||result.data.length>1398104||typeof item.name!=='string'||item.name.length>180||!Number.isInteger(item.size)||item.size<0||item.size>1048576)throw Error('resource_read_integrity');
    const binary=atob(result.data.replaceAll('-','+').replaceAll('_','/')),bytes=Uint8Array.from(binary,c=>c.charCodeAt(0)),digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');if(!alive(w,token))return;
    if(bytes.length!==item.size||digest!==target.hash||btoa(binary).replaceAll('+','-').replaceAll('/','_')!==result.data)throw Error('resource_read_integrity');
    token.contentGeneration=item.contentGeneration;token.contentRevision=item.contentRevision||0;token.name=item.name;w.resourceExpectedName=item.name;title(w,item);w.body.querySelector('[data-resource-setting-name]').value=item.name;token.cleanup?.();token.cleanup=bindResourceFileNames(w.el);
    if(item.kind==='image'){
     const failedImage=()=>{if(!alive(w,token))return;message('그림을 표시하지 못했습니다.');status.textContent='지원 범위의 정지 PNG/JPEG인지 확인해 주세요. 보관된 사본은 그대로예요.';const retry=element('button','다시 확인','secondary');retry.type='button';retry.dataset.resourcePreviewRetry='';retry.onclick=()=>{if(alive(w,token)){token.imageCleanup?.();token.imageCleanup=null;void read();}};actions.replaceChildren(retry);};
     try{token.imageCleanup=mountResourceImage({preview,toolbar,status,bytes,item,active:()=>alive(w,token),onError:failedImage,onDetached:()=>{token.imageDetached=true;}});if(!token.imageCleanup){message('이 그림 형식의 미리보기는 아직 연결되지 않았어요. 보관된 사본은 그대로예요.');status.textContent='현재 정지 PNG/JPEG 그림 미리보기를 지원합니다.';}}catch{failedImage();}return;
    }
    const mime=item.type||'',extension=mime.includes('wordprocessingml')?'docx':mime.includes('spreadsheetml')?'xlsx':mime.includes('presentationml')?'pptx':mime.includes('opendocument.text')?'odt':item.name.split('.').at(-1).toLowerCase();
    if(extension==='pdf'||mime==='application/pdf'){
     const failedPDF=reason=>{if(!alive(w,token))return;message(reason==='password'?'암호가 필요한 PDF입니다.':'PDF를 표시하지 못했습니다.');status.textContent=reason==='pdf_view_budget'?'PDF 미리보기는 최대 2개입니다. 다른 PDF 창을 닫고 다시 확인해 주세요.':'보관된 사본은 그대로예요. 지원 범위와 문서 크기를 확인하고 다시 시도할 수 있어요.';const retry=element('button','다시 확인','secondary');retry.type='button';retry.dataset.resourcePreviewRetry='';retry.onclick=()=>{if(alive(w,token)){token.pdfCleanup?.();token.pdfCleanup=null;void read();}};actions.replaceChildren(retry);};
     try{token.pdfCleanup=mountResourcePDF({preview,toolbar,controls:w.body.querySelector('[data-resource-preview-controls]'),status,bytes,item,active:()=>alive(w,token)&&preview.getClientRects().length>0,onError:failedPDF,onDetached:()=>{token.pdfDetached=true;}});}catch(error){failedPDF(error.message);}return;
    }
    if(['docx','xlsx','pptx','odt'].includes(extension)){
     const failedOffice=()=>{if(!alive(w,token))return;message('문서 내용을 표시하지 못했습니다.');status.textContent='지원 범위의 Office 사본인지 확인해 주세요. 보관된 사본은 그대로예요.';const retry=element('button','다시 확인','secondary');retry.type='button';retry.dataset.resourcePreviewRetry='';retry.onclick=()=>{if(alive(w,token)){token.officeCleanup?.();token.officeCleanup=null;void read();}};actions.replaceChildren(retry);};
     try{token.officeCleanup=mountResourceOffice({preview,toolbar,controls:w.body.querySelector('[data-resource-preview-controls]'),status,bytes,extension,active:()=>alive(w,token)&&preview.getClientRects().length>0,onError:failedOffice,onDetached:()=>{token.officeDetached=true;}});}catch{failedOffice();}return;
    }
    if(item.kind==='image'||['pdf','docx','xlsx','pptx','odt'].includes(extension)||mime==='application/pdf'||!(mime.startsWith('text/')||textExtensions.test(item.name))){message('이 형식의 미리보기는 아직 연결되지 않았어요. 보관된 사본은 그대로예요.');status.textContent='현재 텍스트·코드 파일의 읽기 전용 미리보기를 지원합니다.';return;}
    const encoding=bytes[0]===255&&bytes[1]===254?'utf-16le':bytes[0]===254&&bytes[1]===255?'utf-16be':'utf-8',pre=element('pre',new TextDecoder(encoding).decode(bytes),'resource-document-text');preview.className='resource-preview is-text-preview';preview.replaceChildren(pre);preview.setAttribute('aria-busy','false');toolbar.textContent='텍스트 미리보기';status.textContent='읽기 전용 미리보기';
    if(extension!=='svg')token.contentCleanup=await content.mount({w,item,result,bytes,alive:()=>alive(w,token),refresh:()=>mount(w),status,preview,actions,toolbar});
   }catch(error){if(!alive(w,token))return;message('원본 파일을 불러오지 못했습니다.');status.textContent='보관본과 선택 기준은 그대로예요. 같은 파일을 다시 확인할 수 있어요.';const retry=element('button','다시 확인','secondary');retry.type='button';retry.dataset.resourcePreviewRetry='';retry.onclick=()=>{if(alive(w,token))void read();};actions.replaceChildren(retry);}
   finally{token.loading=false;}
  };
  if(valid())void read();else message('이 프로젝트의 보관된 자료를 다시 선택해 주세요.');return w;
 }
 function open(item,owns=()=>true){
  if(!scope()||!owns()||!idPattern.test(item.id||'')||!hashPattern.test(item.hash||''))return null;
  const w=api.openWindow(prefix+item.id,item.name,760,520,{meta:{resourceOwner:scope(),resourceId:item.id,resourceHash:item.hash}});if(!w)return null;
  const same=w.resourcePreview?.owner===scope()&&w.resourcePreview.id===item.id&&w.resourcePreview.hash===item.hash&&w.resourcePreview.contentGeneration===item.contentGeneration;
  w.resourceExpectedName=item.name;Object.assign(w.meta,{resourceOwner:scope(),resourceId:item.id,resourceHash:item.hash});if(w.resourcePreview?.name!==item.name||!same||!w.resourcePreview||w.resourcePreview.generation!==api.view.generation)mount(w);api.persist();return w;
 }
 function restore(meta){if(!scope()||!meta||!idPattern.test(meta.resourceId||'')||!hashPattern.test(meta.resourceHash||''))return null;const w=api.openWindow(prefix+meta.resourceId,'자료 미리보기',760,520,{refresh:true,meta});if(!w)return null;Object.assign(w.meta,meta);return mount(w);}
 function metadata(items){const files=new Map(items.filter(item=>item.kind!=='folder').map(item=>[item.id,item]));for(const w of api.windows.values()){if(!w.key.startsWith(prefix)||w.meta.resourceOwner!==scope())continue;const item=files.get(w.meta.resourceId);if(!item){content.forget(scope(),w.meta.resourceId);w.resourceContentBeforeClose=null;retire(w);api.close(w);continue;}const changed=w.resourcePreview?.contentGeneration!==item.contentGeneration||item.hash!==w.meta.resourceHash||w.resourcePreview?.name!==item.name||(w.resourcePreview?.contentRevision||0)!==(item.contentRevision||0);w.meta.resourceHash=item.hash;w.resourceExpectedName=item.name;if(changed&&w.resourcePreview&&!w.el.hidden&&w.el.isConnected)mount(w);}}
 function update(){for(const w of api.windows.values())if(w.key.startsWith(prefix)&&w.resourcePreview&&(w.resourcePreview.owner!==scope()||w.resourcePreview.generation!==api.view.generation||w.resourcePreview.imageDetached||w.resourcePreview.officeDetached||w.resourcePreview.pdfDetached)){if((w.resourcePreview.imageDetached||w.resourcePreview.officeDetached||w.resourcePreview.pdfDetached)&&w.resourcePreview.owner===scope()&&w.resourcePreview.generation===api.view.generation&&(w.el.hidden||!w.el.isConnected||(w.resourcePreview.officeDetached||w.resourcePreview.pdfDetached)&&!w.body.getClientRects().length))continue;retire(w);if(w.meta.resourceOwner===scope()&&!w.el.hidden&&w.el.isConnected)mount(w);}}
 return {open,restore,update,metadata,beforeClose:w=>{if(w.key.startsWith(prefix)){if(w.resourceContentBeforeClose?.())return true;retire(w);}return false;},retireAll:()=>{for(const w of api.windows.values())if(w.key.startsWith(prefix))retire(w);}};
}
