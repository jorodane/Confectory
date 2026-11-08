import {readEditableOfficeArchive,rewriteOfficeArchive} from './resource-docx-zip.js';
const wanted=name=>/^xl\/(workbook\.xml|_rels\/workbook\.xml\.rels|sharedStrings\.xml|worksheets\/sheet\d+\.xml)$/.test(name);
let used=false;
onmessage=async event=>{if(used)return;used=true;try{
 const{action,bytes,xml,maximumBytes=1048576}=event.data;if(!(bytes instanceof ArrayBuffer))throw Error('xlsx_input');let output;
 if(action==='read'){
  const {files}=await readEditableOfficeArchive(new Uint8Array(bytes),'xlsx',maximumBytes),parts=[];let total=0;
  for(const[name,data]of files)if(wanted(name)){if(data.byteLength>2097152||(total+=data.byteLength)>4194304||parts.length>=64)throw Error('xlsx_xml_budget');parts.push([name,new TextDecoder('utf-8',{fatal:true}).decode(data)]);}
  output=new TextEncoder().encode(JSON.stringify(parts)).buffer;
 }else if(action==='write'&&xml instanceof ArrayBuffer){
  if(xml.byteLength>12582912)throw Error('xlsx_xml_budget');const parts=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(xml)),changes=new Map();let total=0;
  if(!Array.isArray(parts)||parts.length>64)throw Error('xlsx_parts');for(const part of parts){if(!Array.isArray(part)||part.length!==2||typeof part[0]!=='string'||typeof part[1]!=='string'||!/^xl\/(workbook\.xml|worksheets\/sheet\d+\.xml)$/.test(part[0])||changes.has(part[0]))throw Error('xlsx_parts');const data=new TextEncoder().encode(part[1]);if(data.length>2097152||(total+=data.length)>4194304)throw Error('xlsx_xml_budget');changes.set(part[0],data);}
  output=(await rewriteOfficeArchive(new Uint8Array(bytes),changes,'xlsx',maximumBytes)).buffer;
 }else throw Error('xlsx_operation');postMessage({ok:true,bytes:output},[output]);
 }catch(e){postMessage({ok:false,error:['docx_signed_or_macro','docx_output_budget'].includes(e.message)?e.message:'xlsx_archive'});}finally{close();}};
