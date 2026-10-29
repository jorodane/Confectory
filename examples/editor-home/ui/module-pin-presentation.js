// Display metadata is scoped to the module's existing qualified requirement and
// positional pin. Neither this key nor an icon is an executable pin identity.
export const modulePinKey=(fn,pin)=>'editorModulePinIcon_f'+[...new TextEncoder().encode(fn)].map(byte=>byte.toString(16).padStart(2,'0')).join('')+'_'+pin;
export const modulePinContract=s=>({args:(s?.args||s?.Args||[]).map(a=>({type:a.type??a.Type,mode:a.mode??a.Mode??''})),return:s?.return??s?.Return??'void'});
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
// Receipt-only schema projections omit relations; attested is supplied after
// the existing native journal has verified the complete settled source twice.
export function modulePinValue(schema,edit,attested=false){
 const edge=schema?.relations?.edges?.find(e=>e.role==='require'&&e.target===edit.function);
 if(schema?.kind!=='module'||(edge?!same(modulePinContract(edge.signature),edit.signature):!attested))return {valid:false};
 const value=schema.values?.[modulePinKey(edit.function,edit.pin)];if(value===undefined)return {valid:true,icon:''};
 try{const stored=JSON.parse(value);return stored.function===edit.function&&stored.pin===edit.pin&&same(stored.signature,edit.signature)&&typeof stored.icon==='string'?{valid:true,icon:stored.icon}:{valid:false};}catch{return {valid:false};}
}
