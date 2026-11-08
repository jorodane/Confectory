import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {deflateRawSync} from 'node:zlib';
const root=process.argv[2],{officeDirectory,extractOfficeFiles,officeCRC}=await import(pathToFileURL(root+'/examples/editor-home/ui/resource-office-zip.js')),{readEditableOfficeArchive}=await import(pathToFileURL(root+'/examples/editor-home/ui/resource-docx-zip.js')),encoder=new TextEncoder();
function zip(rows,{descriptor=false}={}){
 const locals=[],central=[];let offset=0;
 for(const [name,value,method=8]of rows){const data=typeof value==='string'?encoder.encode(value):value,rawName=Buffer.from(name),packed=method===8?deflateRawSync(data):Buffer.from(data),crc=officeCRC(data),flags=descriptor?8:0,local=Buffer.alloc(30+rawName.length),head=Buffer.alloc(46+rawName.length);local.writeUInt32LE(0x04034b50);local.writeUInt16LE(20,4);local.writeUInt16LE(flags,6);local.writeUInt16LE(method,8);local.writeUInt16LE(rawName.length,26);rawName.copy(local,30);if(!descriptor){local.writeUInt32LE(crc,14);local.writeUInt32LE(packed.length,18);local.writeUInt32LE(data.length,22);}head.writeUInt32LE(0x02014b50);head.writeUInt16LE(20,6);head.writeUInt16LE(flags,8);head.writeUInt16LE(method,10);head.writeUInt32LE(crc,16);head.writeUInt32LE(packed.length,20);head.writeUInt32LE(data.length,24);head.writeUInt16LE(rawName.length,28);head.writeUInt32LE(offset,42);rawName.copy(head,46);const tail=descriptor?Buffer.alloc(16):Buffer.alloc(0);if(descriptor){tail.writeUInt32LE(0x08074b50);tail.writeUInt32LE(crc,4);tail.writeUInt32LE(packed.length,8);tail.writeUInt32LE(data.length,12);}locals.push(local,packed,tail);central.push(head);offset+=local.length+packed.length+tail.length;
 }const body=Buffer.concat(central),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50);end.writeUInt16LE(rows.length,8);end.writeUInt16LE(rows.length,10);end.writeUInt32LE(body.length,12);end.writeUInt32LE(offset,16);return new Uint8Array(Buffer.concat([...locals,body,end]));
}

const noise=new Uint8Array(4194304-1000);let seed=1731;for(let i=0;i<noise.length;i++){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;noise[i]=seed&255;}
for(const[extension,name]of[['docx','word/document.xml'],['xlsx','xl/worksheets/sheet1.xml'],['pptx','ppt/slides/slide1.xml'],['odt','content.xml']]){
 const raw=zip([[name,'<root>exact selected XML 🧪</root>'],['media/generated.bin',noise,0]]);assert(raw.length>1048576&&raw.length<=4194304);
 assert.throws(()=>officeDirectory(raw,extension),/input/);await assert.rejects(extractOfficeFiles(raw,extension),/input/);await assert.rejects(readEditableOfficeArchive(raw,extension),/input/);
 const selected=await extractOfficeFiles(raw,extension,false,4194304);assert.equal(selected.length,1);assert.equal(new TextDecoder().decode(selected[0][1]),'<root>exact selected XML 🧪</root>');
 assert.throws(()=>officeDirectory(raw,extension,true,4194304),/input/);await assert.rejects(extractOfficeFiles(raw,extension,true,4194304),/input/);
 for(const limit of[0,1048577,4194305,Infinity,'4194304'])assert.throws(()=>officeDirectory(raw,extension,false,limit),/input/);
}
const exactBase=zip([['word/document.xml','<root/>'],['media/generated.bin',new Uint8Array(0),0]]),exact=zip([['word/document.xml','<root/>'],['media/generated.bin',new Uint8Array(4194304-exactBase.length),0]]);assert.equal(exact.length,4194304);assert.equal((await extractOfficeFiles(exact,'docx',false,4194304)).length,1);assert.throws(()=>officeDirectory(new Uint8Array(4194305),'docx',false,4194304),/input/);
await assert.rejects(extractOfficeFiles(zip([['word/document.xml',new Uint8Array(2097153)],['media/generated.bin',noise.subarray(0,1048576),0]]),'docx',false,4194304),/decoded_budget/);
await assert.rejects(extractOfficeFiles(zip([['xl/worksheets/sheet1.xml',new Uint8Array(2097152)],['xl/worksheets/sheet2.xml',new Uint8Array(2097152)],['xl/workbook.xml',new Uint8Array(1)],['media/generated.bin',noise.subarray(0,1048576),0]]),'xlsx',false,4194304),/decoded_budget/);
console.log('PASS actual Office read-only4MiB opt-in across four formats; default/edit1MiB unchanged; same selected XML bounds; exact max/over-limit and unknown-limit refusal');
