// Human declaration editing over the consumer's scoped draft operations.
export function createDeclarationEditors(api){
 const {$,$$,esc,inputs}=api,types=['bool','int','long','float','double','string'],returns=['void',...types,...types.map(t=>t+'[]')],argumentsTypes=returns.filter(t=>t!=='void');
 const roleNames={module:'적용 모듈',include:'포함 모듈',require:'필요 기능',default:'기본 구현',provide:'제공 구현',use:'사용 관계',contain:'소속 관계',import:'가져온 기능'};
 const signature=value=>({args:(value?.Args||value?.args||[]).map(p=>({type:p.Type??p.type,name:p.Name??p.name})),return:value?.return||'int'});
 const key=(info,row)=>api.current.projectId+'|'+(row?.view||'primary')+'|'+info.id;
 const fresh=(id,row)=>row?(api.current.editorViews||[]).find(v=>v.view===row.view&&v.id===id)?.declaration:api.current.declaration?.id===id?api.current.declaration:null;
 const typed=(selected,list)=>list.map(type=>`<option ${type===selected?'selected':''} value="${esc(type)}">${esc(type)}</option>`).join('');
 function local(info,row,section,value){const id=key(info,row),record=inputs.get(id)||{};record[section]??={revision:info.revision,hash:info.textHash,value:structuredClone(value)};inputs.set(id,record);return record[section];}
 function persist(){api.persist();}
 function show(info=api.current.declaration,row=null,force=false){
  if(!info)return null;const scope=api.current.projectId,cacheKey=key(info,row),panelKey=row?'editor-'+row.view:'declaration',old=api.windows.get(panelKey),stamp=JSON.stringify(info);
  if(old&&!force&&old.meta.declarationStamp===stamp)return old;
  const w=api.openWindow(panelKey,(info.values?.editorName||info.id.split('::').at(-1))+' · 선언',640,510,{refresh:!!old});w.meta.id=info.id;w.meta.view=row?.view||'';w.meta.mode='declaration';w.meta.declarationStamp=stamp;w.meta.revision=info.revision;const title=(info.values?.editorName||info.id.split('::').at(-1))+' · 선언';w.title=title;$('.caption strong',w.el).textContent=title;w.el.setAttribute('aria-label',title);
  const cache=inputs.get(cacheKey)||{},common=cache.properties?.value||{},display={displayName:info.values?.editorName||'',icon:info.values?.editorIcon||'',description:info.description||'',parent:info.parent||''};
  w.body.innerHTML=`<div class="window-content" data-declaration-kind="${esc(info.kind)}"><h2 data-declaration-id>${esc(info.id)}</h2><p>${esc(info.kind)} · revision ${esc(info.revision)} · 선언에 직접 설정하는 내용</p><p data-declaration-notice></p><form data-declaration-properties class="stack"><div class="fields"><label>표시 이름<input data-decl-property="displayName" maxlength="256" placeholder="${esc(info.id.split('::').at(-1))}"></label><label>아이콘 문자<input data-decl-property="icon" maxlength="64"></label></div><label>직접 설명<textarea data-decl-property="description" rows="3" maxlength="16384"></textarea></label><label>부모 선언 ID<input data-decl-property="parent" placeholder="Namespace::Declaration"></label><div class="actions"><button data-operation type="submit" data-properties-apply>내용을 공유 초안에 적용</button><button data-operation type="button" data-unset-description data-supported="${info.descriptionDefined===true}">직접 설명 지우기</button></div><p class="small">표시 이름은 선언 ID를 유지합니다. 부모를 비우면 직접 설정한 상속 관계가 제거됩니다.</p></form>${info.signature?'<section data-signature-editor></section>':''}<section data-relation-editor></section><div class="actions"><button data-operation data-declaration-save>Save · 작업 사본</button><button data-operation data-declaration-review ${row?'hidden':''}>Review</button><button data-operation data-declaration-current>현재 초안 다시 읽기</button>${row?'<button data-operation data-declaration-release>창 해제</button>':'<button data-operation data-declaration-keep>독립 선언창 유지</button>'}</div><p class="small">Apply와 Save 후에도 최종 파일은 유지됩니다. 최종 반영은 별도의 묶음 Review / Confirm을 사용합니다.</p></div>`;
  const notice=()=>{const records=Object.values(inputs.get(cacheKey)||{}),stale=records.some(v=>v.revision!==info.revision||v.hash!==info.textHash);$('[data-declaration-notice]',w.body).textContent=records.length?(stale?'초안 리비전이 바뀌었습니다. 미적용 입력은 유지됩니다. 현재 초안을 확인하고 다시 편집하세요.':'아직 공유 초안에 적용하지 않은 입력이 있습니다.'):'공유 초안의 현재 내용입니다.';};
  async function stage(edit,section,revision){
   const saved=section?JSON.stringify(inputs.get(cacheKey)?.[section]):null;
   const exactHash=section&&inputs.get(cacheKey)?.[section]?inputs.get(cacheKey)[section].hash:info.textHash;
   const exactRevision=revision??(section?inputs.get(cacheKey)?.[section]?.revision:undefined)??info.revision;
   await api.work(async()=>{
    if(api.current.projectId!==scope||(!row&&api.current.draft?.id!==info.id))throw Error('선언 편집 대상이 바뀌었습니다. 입력은 유지됩니다.');
    if(api.dirty)throw Error('소스의 미적용 입력을 먼저 Apply하세요.');if(!exactHash)throw Error('입력의 기준 정보가 없습니다. 현재 초안을 확인하세요. 입력은 유지됩니다.');
    await api.view.call(row?'editViewDeclaration':'editDeclaration',{...(row?{view:row.view}:{}),id:info.id,revision:exactRevision,hash:exactHash,edit:structuredClone(edit)});
    if(section&&JSON.stringify(inputs.get(cacheKey)?.[section])===saved){const record=inputs.get(cacheKey);delete record[section];if(!Object.keys(record).length)inputs.delete(cacheKey);}
    if(row)await api.view.call('openEditorView',{view:row.view,id:info.id,viewMode:'declaration'});else await api.view.call('inspectDeclaration',{id:info.id});
    show(fresh(info.id,row),row,true);persist();
   },'선언 공유 초안 갱신 · 최종 반영 전');
  }
  for(const field of $$('[data-decl-property]',w.body)){
   const name=field.dataset.declProperty;field.value=Object.hasOwn(common,name)?common[name]??'':display[name];field.oninput=()=>{local(info,row,'properties',{}).value[name]=name==='parent'?(field.value.trim()||null):field.value;persist();notice();};
  }
  $('[data-declaration-properties]',w.body).onsubmit=e=>{e.preventDefault();const changes=inputs.get(cacheKey)?.properties;if(!changes||!Object.keys(changes.value).length){api.toast('적용할 입력이 없습니다.');return;}stage({action:'properties',values:changes.value},'properties');};
  $('[data-unset-description]',w.body).onclick=()=>stage({action:'unset-description'},null);
  function renderSignature(){
   const root=$('[data-signature-editor]',w.body);if(!root)return;const value=cache.signature?.value||signature(info.signature);
   root.innerHTML=`<h3>기능 입출력 계약</h3><div data-arguments></div><button data-operation data-add-argument>입력 추가</button><label>반환 타입<select data-return>${typed(value.return,returns)}</select></label><button data-operation data-signature-apply>계약을 공유 초안에 적용</button><p class="small">선언 언어가 지원하는 primitive와 배열 타입을 사용합니다. 연결된 구현과 함께 검토할 수 있습니다.</p>`;
   const changed=()=>{const item=local(info,row,'signature',value);item.value=structuredClone(value);cache.signature=item;persist();notice();};
   value.args.forEach((arg,index)=>{const line=document.createElement('div');line.className='declaration-argument';line.dataset.argument=String(index);line.innerHTML=`<select aria-label="입력 ${index+1} 타입" data-arg-type>${typed(arg.type,argumentsTypes)}</select><input aria-label="입력 ${index+1} 이름" data-arg-name maxlength="64"><button data-operation data-arg-up ${index===0?'disabled data-supported="false"':''}>↑</button><button data-operation data-arg-down ${index===value.args.length-1?'disabled data-supported="false"':''}>↓</button><button data-operation data-arg-remove>제거</button>`;root.querySelector('[data-arguments]').append(line);$('[data-arg-name]',line).value=arg.name;
    $('[data-arg-name]',line).oninput=e=>{arg.name=e.target.value;changed();};$('[data-arg-type]',line).onchange=e=>{arg.type=e.target.value;changed();};
    $('[data-arg-remove]',line).onclick=()=>{value.args.splice(index,1);changed();renderSignature();api.controls();};
    for(const [name,delta] of [['up',-1],['down',1]])$('[data-arg-'+name+']',line).onclick=()=>{const next=index+delta;if(next<0||next>=value.args.length)return;[value.args[index],value.args[next]]=[value.args[next],value.args[index]];changed();renderSignature();api.controls();};
   });
   $('[data-add-argument]',root).dataset.supported=String(value.args.length<64);$('[data-add-argument]',root).onclick=()=>{if(value.args.length>=64)return;value.args.push({type:'int',name:'input'+(value.args.length+1)});changed();renderSignature();api.controls();};$('[data-return]',root).onchange=e=>{value.return=e.target.value;changed();};$('[data-signature-apply]',root).onclick=()=>stage({action:'signature',value},'signature');
  }
  function renderRelations(){
   const root=$('[data-relation-editor]',w.body),roles=['module','provide','use','contain',...(info.kind==='module'?['include','require','default']:[]),...(info.kind==='implementation'?['import']:[])];
   root.innerHTML='<h3>직접 선언한 연결</h3>';
   for(const role of roles){
    const section='relations:'+role,record=cache[section],entries=record?.value||((info.relations?.edges||[]).filter(edge=>edge.role===role).map(edge=>({id:edge.target,...(edge.function?{function:edge.function}:{}),...(edge.kind?{kind:edge.kind}:{}),...(role==='import'?{alias:edge.alias,scope:edge.scope}:{}),...(edge.signature?{signature:signature(edge.signature)}:{})})));
    const group=document.createElement('details');group.dataset.relationRole=role;group.innerHTML=`<summary>${esc(roleNames[role])} · ${entries.length}</summary><div data-relation-rows></div><div class="actions"><button data-operation data-add-relation>연결 추가</button><button data-operation data-apply-relations>이 연결 목록 적용</button></div>`;root.append(group);
    const changed=()=>{const item=local(info,row,section,entries);item.value=structuredClone(entries);cache[section]=item;persist();notice();};
    const rows=()=>{const target=$('[data-relation-rows]',group);target.replaceChildren();entries.forEach((entry,index)=>{
     const line=document.createElement('div');line.className='declaration-relation';line.dataset.relationIndex=String(index);
     const binding=role==='provide'||role==='default',contract=role==='require'||role==='import';
     line.innerHTML=`${binding?'<label>기능 ID<input data-relation-field="function"></label>':''}<label>${binding?'구현 ID':'대상 ID'}<input data-relation-field="id"></label>${role==='use'||role==='contain'?'<label>선언 종류<select data-relation-field="kind">'+['object','schema','function','implementation','module','category','concept','stage','view'].map(kind=>`<option ${kind===entry.kind?'selected':''}>${kind}</option>`).join('')+'</select></label>':''}${role==='import'?'<label>별칭<input data-relation-field="alias"></label><label>호출 범위 ID · 선택<input data-relation-field="scope"></label>':''}${contract?'<label>입력 타입 · 쉼표 구분<input data-relation-arguments></label><label>반환 타입<select data-relation-return>'+typed(entry.signature?.return||'int',returns)+'</select></label>':''}<button data-operation data-remove-relation>이 연결 제거</button>`;
     target.append(line);for(const field of $$('[data-relation-field]',line)){const name=field.dataset.relationField;field.value=entry[name]||'';field.oninput=field.onchange=()=>{entry[name]=name==='scope'?field.value.trim()||null:field.value;changed();};}
     if(contract){const input=$('[data-relation-arguments]',line);input.value=(entry.signature?.args||[]).map(arg=>arg.type).join(', ');input.oninput=()=>{entry.signature??={args:[],return:'int'};entry.signature.args=input.value.split(',').map(type=>type.trim()).filter(Boolean).map(type=>({type}));changed();};$('[data-relation-return]',line).onchange=e=>{entry.signature??={args:[],return:'int'};entry.signature.return=e.target.value;changed();};}
     $('[data-remove-relation]',line).onclick=()=>{entries.splice(index,1);changed();rows();api.controls();};
    });};rows();
    $('[data-add-relation]',group).dataset.supported=String(entries.length<128);$('[data-add-relation]',group).onclick=()=>{if(entries.length>=128)return;entries.push({id:'',...(role==='provide'||role==='default'?{function:info.kind==='function'?info.id:''}:{}),...(role==='use'||role==='contain'?{kind:'object'}:{}),...(role==='import'?{alias:'',scope:null}:{}),...(role==='require'||role==='import'?{signature:{args:[],return:'int'}}:{})});changed();rows();api.controls();};$('[data-apply-relations]',group).onclick=()=>stage({action:'relations',role,entries},section);
   }
  }
  renderSignature();renderRelations();notice();
  const references=[...new Set((info.relations?.edges||[]).flatMap(edge=>[edge.target,edge.function,edge.scope]).filter(Boolean))];
  if(references.length){const list=document.createElement('details');list.dataset.declarationReferences='';list.innerHTML='<summary>참조한 선언의 정의 · '+references.length+'</summary>';for(const id of references){const button=document.createElement('button');button.dataset.operation='reference-definition';button.dataset.referenceTarget=id;button.textContent=id;button.onclick=()=>api.reference(info,id);list.append(button);}w.body.querySelector('.window-content').append(list);}

  $('[data-declaration-current]',w.body).onclick=()=>api.work(async()=>{if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다.');const saved=JSON.stringify(inputs.get(cacheKey));if(row)await api.view.call('openEditorView',{view:row.view,id:info.id,viewMode:'declaration'});else await api.view.call('inspectDeclaration',{id:info.id});if(fresh(info.id,row)&&JSON.stringify(inputs.get(cacheKey))===saved)inputs.delete(cacheKey);show(fresh(info.id,row),row,true);persist();},'현재 선언 초안 다시 읽음');
  $('[data-declaration-save]',w.body).onclick=()=>api.work(()=>api.view.call(row?'saveEditorView':'saveDraft',row?{view:row.view,id:info.id}:{}),'Draft saved; final sources unchanged');
  $('[data-declaration-review]',w.body).onclick=()=>{if(Object.keys(inputs.get(cacheKey)||{}).length){api.toast('미적용 입력을 먼저 적용하세요.');return;}api.review(info.id);};
  $('[data-declaration-keep]',w.body)?.addEventListener('click',()=>api.keep());
  $('[data-declaration-release]',w.body)?.addEventListener('click',()=>api.work(async()=>{if(Object.keys(inputs.get(cacheKey)||{}).length)throw Error('미적용 입력을 적용하거나 현재 초안으로 되돌리세요.');await api.view.call('closeEditorView',{view:row.view,id:info.id});api.release(w);},'독립 선언창 해제 · 공유 초안 유지'));
  if(info.editable!==true)for(const control of $$('input,textarea,select,button',w.body)){control.disabled=true;control.dataset.supported='false';}
  api.controls();return w;
 }
 function open(info=api.current.declaration,row=null){const w=show(info,row);if(w)api.focus(w);return w;}
 return {show,open};
}
