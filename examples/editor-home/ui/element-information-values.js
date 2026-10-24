import {createTypedValueWidgets} from './element-values.js';

// Reuse the original linked-information value rows. The whole new definition
// remains one private cell, including invalid child input and exact JSON numbers.
export function renderInformationValues(api,w,schema,key,value,field,refresh){
 const {$,esc,inputs}=api,virtual=w.elementScope+'|'+schema.id+'|element|'+JSON.stringify([value.nativeKey||value.name]);
 const local={get:k=>k===virtual?inputs.get(key):undefined,set(k,data){if(k!==virtual)throw Error('새 정보 속성의 편집 범위가 달라요.');const prior=inputs.get(key);if(!prior)return;inputs.set(key,{...prior,text:data.text,wireJson:true,invalidChildren:data.invalidChildren||{}});return this;},*entries(){const v=inputs.get(key);if(v)yield [virtual,v];},[Symbol.iterator](){return this.entries();}};
 const widgets=createTypedValueWidgets(Object.assign(Object.create(api),{inputs:local,refresh:()=>refresh(w,schema)})),view={...schema,types:{...(schema.types||{}),...value.information.types}},row={name:value.name,path:[value.nativeKey||value.name],kind:'compound',cardinality:'single',type:value.information.id,writable:true,localOverride:true,valueJson:value.text};
 const child=(container,row,_inherited,ctx)=>{const el=document.createElement('section');el.className='object-property-row editable-property-row inherited-property-row';el.dataset.propertyPath=JSON.stringify(row.path);el.innerHTML='<div class="property-content-box inherited-value-box"><strong class="inherited-property-name"><span class="property-label-icon" aria-hidden="true"><span class="icon-placeholder">−</span></span>'+esc(row.displayName||row.name)+'</strong><div class="object-property-default"></div><p class="property-error" role="alert"></p></div>';container.append(el);widgets.render(w,view,row,el,child,ctx);};
 $('.object-property-default',field).replaceChildren();widgets.render(w,view,row,field,child);
}
