// Fixed authored renderer assets only. Document bytes never select a fetch URL.
export function pdfAssetURL(input,here){
 const url=new URL(input,here),base=new URL('./assets/vendor/pdfjs-dist-4.10.38/',here);
 if(url.origin!==base.origin||url.search||url.hash||!url.pathname.startsWith(base.pathname))throw Error('pdf_asset_url');
 const name=url.pathname.slice(base.pathname.length);if(!/^(?:cmaps\/[A-Za-z0-9_-]+\.bcmap|standard_fonts\/[A-Za-z0-9_-]+\.(?:pfb|ttf))$/.test(name))throw Error('pdf_asset_url');return url.href;
}
export function pdfCanvasPlan(width,height,available,zoom,dpr){
 if(![width,height,available,dpr].every(Number.isFinite)||width<=0||height<=0||width>14400||height>14400||available<=0||!['fit','1','1.5','2'].includes(zoom))throw Error('pdf_page_budget');
 const scale=zoom==='fit'?Math.max(.1,(available-28)/width):Number(zoom),w=width*scale,h=height*scale;if(!Number.isFinite(w*h)||w<=0||h<=0||w>8192||h>8192||w*h>16777216)throw Error('pdf_page_budget');
 const density=Math.min(Math.max(1,dpr),2,4096/Math.max(w,h),Math.sqrt(4194304/(w*h)));
 // Rounding must stay within the exact canvas budget too.
 let cw=Math.max(1,Math.floor(w*density)),ch=Math.max(1,Math.floor(h*density));if(cw*ch>4194304||cw>4096||ch>4096)throw Error('pdf_canvas_budget');return {scale,width:w,height:h,density,canvasWidth:cw,canvasHeight:ch};
}
