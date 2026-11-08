// A bounded, self-contained static SVG display profile. Never insert asset XML in the page.
// Reject unsupported features rather than stripping them or changing the stored project copy.
const NS='http://www.w3.org/2000/svg',XMLNS='http://www.w3.org/2000/xmlns/';
const shape=new Set(['rect','circle','ellipse','line','polyline','polygon','path']);
const common='id fill stroke color opacity fill-opacity stroke-opacity stroke-width stroke-linecap stroke-linejoin stroke-miterlimit stroke-dasharray stroke-dashoffset fill-rule clip-rule clip-path transform display visibility vector-effect'.split(' ');
const specific={svg:'width height viewBox preserveAspectRatio version',g:'',defs:'',title:'',desc:'',rect:'x y width height rx ry',circle:'cx cy r',ellipse:'cx cy rx ry',line:'x1 y1 x2 y2',polyline:'points',polygon:'points',path:'d',linearGradient:'x1 y1 x2 y2 gradientUnits gradientTransform spreadMethod',radialGradient:'cx cy r fx fy fr gradientUnits gradientTransform spreadMethod',stop:'offset stop-color stop-opacity',clipPath:'clipPathUnits',text:'x y dx dy text-anchor font-family font-size font-weight font-style letter-spacing word-spacing',tspan:'x y dx dy text-anchor font-family font-size font-weight font-style letter-spacing word-spacing'};
const idPattern=/^[A-Za-z_][A-Za-z0-9_.:-]{0,63}$/;
export function resourceSvgSignature(bytes){
 let start=bytes[0]===239&&bytes[1]===187&&bytes[2]===191?3:0;while([9,10,13,32].includes(bytes[start]))start++;
 return bytes[start]===60;
}
export function resourceSvgInfo(bytes){
 if(!(bytes instanceof Uint8Array)||bytes.length>4194304)throw Error('resource_image_bytes');
 if(!resourceSvgSignature(bytes))return null;
 const fail=()=>{throw Error('resource_svg_static_profile');};
 let text;try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch{fail();}
 // Check before XML parsing, so DTD/entity expansion is never attempted.
 const declaration=text.replace(/^\s*<\?xml\s+[^?]*\?>/,'');let source;
 if(bytes.length>262144){
  // Scan large comments once; an unterminated sequence must not trigger repeated regex searches.
  const parts=[];let at=0,comments=0;
  while(true){const start=declaration.indexOf('<!--',at);if(start<0){parts.push(declaration.slice(at));break;}const end=declaration.indexOf('-->',start+4);if(end<0||++comments>1024)fail();parts.push(declaration.slice(at,start));at=end+3;}
  source=parts.join('');let markup=0;for(let at=source.indexOf('<');at>=0;at=source.indexOf('<',at+1))if(++markup>4096)fail();
 }else source=declaration.replace(/<!--[\s\S]*?-->/g,'');
 if(source.includes('<!')||source.includes('<?')||(source.match(/</g)||[]).length>4096||/encoding\s*=\s*["'](?!utf-8["'])/i.test(text.slice(0,text.indexOf('?>')+2)))fail();
 if(!/^\s*<svg\s/.test(source)||!/^\s*<svg\s[^>]*\bxmlns\s*=\s*["']http:\/\/www\.w3\.org\/2000\/svg["']/.test(source))return null;
 if(typeof DOMParser!=='function'||typeof XMLSerializer!=='function')throw Error('resource_svg_decoder_unsupported');
 const doc=new DOMParser().parseFromString(text,'application/xml'),root=doc.documentElement;
 if(doc.doctype||doc.getElementsByTagName('parsererror').length)fail();
 if(root?.localName!=='svg'||root.namespaceURI!==NS)return null;
 const nodes=[{node:root,depth:0,clip:false}],ids=new Map(),references=[];let count=0,numbers=0,segments=0,characters=0;
 const list=(value,min=1,max=1,percent=false)=>{if(value.length>65536)fail();const tokens=value.trim().split(/[\s,]+/);if(tokens.length<min||tokens.length>max)fail();const result=tokens.map(token=>{if(!(percent?/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?%?$/:/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/).test(token))fail();const number=Number(token.replace(/%$/,''));if(!Number.isFinite(number)||Math.abs(number)>1000000||++numbers>32768)fail();return number;});return result;};
 const color=value=>{if(value.length>100||!(/^(?:#[0-9a-fA-F]{3,8}|[A-Za-z]{1,32}|(?:rgb|rgba|hsl|hsla)\([\d+.,%\s/-]+\))$/.test(value))||!CSS.supports('color',value))fail();};
 const paint=value=>{const ref=/^url\(#([A-Za-z_][A-Za-z0-9_.:-]{0,63})\)$/.exec(value);if(ref)references.push({id:ref[1],type:'gradient'});else if(value!=='none'&&value!=='currentColor')color(value);};
 const transform=value=>{let end=0,operations=0;const expression=/(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^()]*)\)/g;for(const match of value.matchAll(expression)){if(value.slice(end,match.index).trim()||++operations>32)fail();const arity={matrix:[6],translate:[1,2],scale:[1,2],rotate:[1,3],skewX:[1],skewY:[1]}[match[1]],n=list(match[2],1,6);if(!arity.includes(n.length)||match[1]==='scale'&&n.some(v=>Math.abs(v)>1024))fail();end=match.index+match[0].length;}if(!operations||value.slice(end).trim())fail();};
 const path=value=>{value=value.trim();const chunks=[...value.matchAll(/([MmZzLlHhVvCcSsQqTtAa])([^MmZzLlHhVvCcSsQqTtAa]*)/g)];if(!chunks.length||chunks.map(v=>v[0]).join('')!==value.trim()||chunks[0][1].toUpperCase()!=='M')fail();for(const chunk of chunks){const command=chunk[1].toUpperCase(),arity={M:2,L:2,H:1,V:1,C:6,S:4,Q:4,T:2,A:7,Z:0}[command],raw=chunk[2].trim();if(!arity){if(raw||++segments>4096)fail();continue;}const tokens=raw.match(/[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/g)||[];if(raw.replace(/[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/g,'').replace(/[\s,]/g,'')||!tokens.length||tokens.length%arity)fail();const n=list(tokens.join(' '),arity,32768);segments+=n.length/arity;if(segments>4096)fail();if(command==='A')for(let i=0;i<n.length;i+=7)if(n[i]<0||n[i+1]<0||![0,1].includes(n[i+3])||![0,1].includes(n[i+4]))fail();}};
 while(nodes.length){const {node,depth,clip}=nodes.pop(),tag=node.localName;if(++count>1024||depth>24||node.namespaceURI!==NS||node.prefix||!Object.hasOwn(specific,tag)||tag==='svg'&&node!==root||node.attributes.length>32)fail();
  if(tag==='clipPath'&&clip)fail();const inClip=clip||tag==='clipPath';if(clip&&!shape.has(tag)&&tag!=='g')fail();
  const allowed=new Set([...common,...specific[tag].split(' ')]);
  for(const attribute of node.attributes){const key=attribute.name,value=attribute.value.trim();
   if(attribute.namespaceURI===XMLNS){if(key!=='xmlns'||value!==NS)fail();continue;}
   if(attribute.namespaceURI||!allowed.has(key)||value.length>65536)fail();
   if(key==='id'){if(!idPattern.test(value)||ids.has(value))fail();ids.set(value,tag);}
   else if(['fill','stroke'].includes(key))paint(value);
   else if(['color','stop-color'].includes(key))color(value);
   else if(key==='clip-path'){const ref=/^url\(#([A-Za-z_][A-Za-z0-9_.:-]{0,63})\)$/.exec(value);if(inClip||!ref)fail();references.push({id:ref[1],type:'clipPath'});}
   else if(['transform','gradientTransform'].includes(key))transform(value);
   else if(key==='d')path(value);
   else if(key==='points'){const n=list(value,4,8192);if(n.length%2)fail();segments+=n.length/2;if(segments>4096)fail();}
   else if(key==='viewBox'){const n=list(value,4,4);if(n[2]<=0||n[3]<=0)fail();}
   else if(key==='preserveAspectRatio'){if(!/^(?:none|x(?:Min|Mid|Max)Y(?:Min|Mid|Max)(?:\s+(?:meet|slice))?)$/.test(value))fail();}
   else if(key==='version'){if(value!=='1.1'&&value!=='2.0')fail();}
   else if(['gradientUnits','clipPathUnits'].includes(key)){if(!['userSpaceOnUse','objectBoundingBox'].includes(value))fail();}
   else if(key==='spreadMethod'){if(!['pad','reflect','repeat'].includes(value))fail();}
   else if(['fill-rule','clip-rule'].includes(key)){if(!['nonzero','evenodd'].includes(value))fail();}
   else if(key==='stroke-linecap'){if(!['butt','round','square'].includes(value))fail();}
   else if(key==='stroke-linejoin'){if(!['miter','round','bevel'].includes(value))fail();}
   else if(key==='display'){if(!['inline','none'].includes(value))fail();}
   else if(key==='visibility'){if(!['visible','hidden','collapse'].includes(value))fail();}
   else if(key==='vector-effect'){if(!['none','non-scaling-stroke'].includes(value))fail();}
   else if(key==='font-family'){if(!/^[A-Za-z0-9 ,'-]{1,100}$/.test(value))fail();}
   else if(key==='font-weight'){if(!/^(?:normal|bold|[1-9]00)$/.test(value))fail();}
   else if(key==='font-style'){if(!['normal','italic','oblique'].includes(value))fail();}
   else if(key==='text-anchor'){if(!['start','middle','end'].includes(value))fail();}
   else if(node===root&&['width','height'].includes(key)){if(!/^[1-9][0-9]{0,4}(?:px)?$/.test(value))fail();}
   else if(key==='stroke-dasharray'&&value==='none'){}
   else {const n=list(value,1,['x','y','dx','dy'].includes(key)&&['text','tspan'].includes(tag)?128:key==='stroke-dasharray'?128:1,true);if(['width','height','r','rx','ry','fr','stroke-width','stroke-miterlimit','font-size'].includes(key)&&n.some(v=>v<0))fail();}
  }
  for(const child of node.childNodes){if(child.nodeType===1)nodes.push({node:child,depth:depth+1,clip:inClip});else if(child.nodeType===3){characters+=child.data.length;if(characters>65536||child.data.trim()&&!['text','tspan','title','desc'].includes(tag))fail();}else if(child.nodeType!==8)fail();}
 }
 for(const ref of references){const tag=ids.get(ref.id);if(ref.type==='gradient'?!['linearGradient','radialGradient'].includes(tag):tag!=='clipPath')fail();}
 let width=root.getAttribute('width'),height=root.getAttribute('height');
 if(!width&&!height){if(!root.hasAttribute('viewBox'))fail();const box=list(root.getAttribute('viewBox'),4,4);width=Math.ceil(box[2]);height=Math.ceil(box[3]);}else if(!width||!height)fail();else {width=Number(width.replace(/px$/,''));height=Number(height.replace(/px$/,''));}
 if(!width||!height||width>16384||height>16384||width*height>16777216)throw Error('resource_image_dimensions');
 // Give viewBox-only files an explicit bounded intrinsic viewport in the display derivative.
 // The immutable project bytes/hash and all artwork remain unchanged.
 root.setAttribute('width',String(width));root.setAttribute('height',String(height));
 const displayBytes=new TextEncoder().encode(new XMLSerializer().serializeToString(root));
 return {width,height,type:'image/svg+xml',pixels:width*height,displayBytes};
}
