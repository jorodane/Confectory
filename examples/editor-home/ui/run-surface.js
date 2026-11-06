// Pixels are inert, bounded RGBA8 from the exact native execution. No source, media URL or commands.
export async function decodeRunSurface(packet,prior,handle){
 if(packet?.available!==true)return null;
 const {runtime,revision,cursor,format,encoding,width,height,sha256,unchanged}=packet;
 if(typeof handle!=='string'||!handle||typeof runtime!=='string'||!/^[a-f0-9]{32}$/.test(runtime)||typeof revision!=='string'||! /^(0|[1-9][0-9]{0,18})$/.test(revision)||BigInt(revision)<=0n||BigInt(revision)>9223372036854775807n||cursor!==runtime+':'+revision||format!=='rgba8'||encoding!=='base64url'||!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||width>512||height>512||typeof sha256!=='string'||!/^[a-f0-9]{64}$/.test(sha256)||typeof unchanged!=='boolean')throw Error('surface_invalid');
 const same=prior?.handle===handle&&prior.runtime===runtime;
 if(same&&BigInt(prior.revision)>BigInt(revision))throw Error('surface_stale');
 if(unchanged){if(!same||prior.cursor!==cursor||prior.width!==width||prior.height!==height||prior.sha256!==sha256||packet.pixels!==undefined)throw Error('surface_unobserved');return prior;}
 if(typeof packet.pixels!=='string'||packet.pixels.length>1398102||! /^[A-Za-z0-9_-]+$/.test(packet.pixels))throw Error('surface_invalid');
 const raw=atob(packet.pixels.replaceAll('-','+').replaceAll('_','/')),pixels=Uint8ClampedArray.from(raw,c=>c.charCodeAt(0));
 if(pixels.length!==width*height*4||btoa(raw).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'')!==packet.pixels)throw Error('surface_invalid');
 const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',pixels)),b=>b.toString(16).padStart(2,'0')).join('');
 if(actual!==sha256||same&&revision===prior.revision&&(sha256!==prior.sha256||width!==prior.width||height!==prior.height))throw Error('surface_hash');
 return Object.freeze({handle,runtime,revision,cursor,width,height,sha256,pixels});
}
