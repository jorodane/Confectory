// The bridge borrows the existing project/owned-node capability. No new editor,
// proposal queue, final-source writer or account setup lives in this panel.
export function createMcpBridge(api){
 const {$,esc}=api;
 function update(){
  const w=api.windows.get('mcp-bridge');if(!w?.el.isConnected||!$('[data-mcp-status]',w.body))return;
  const status=api.current.mcpBridge||{state:'stopped'},active=status.state==='ready';
  $('[data-mcp-status]',w.body).textContent=status.message||(api.current.mcpBridgeSupported?'아직 연결을 준비하지 않았습니다.':'현재 호스트는 로컬 플러그인 연결을 지원하지 않습니다.');
  $('[data-mcp-scope]',w.body).textContent=active?(status.title+' · '+(status.node||'프로젝트 소유 소스')+' · '+(status.readOnly?'읽기 전용':'기존 초안 편집 도구')):'ChatGPT 플러그인은 앱에서 준비한 범위만 조회할 수 있습니다.';
  $('[data-mcp-directory]',w.body).textContent=status.directory||'';
  const field=$('[data-mcp-node]',w.body),readonly=$('[data-mcp-readonly]',w.body);if(active){if(status.node&&![...field.options].some(o=>o.value===status.node))field.add(new Option('연결 중인 노드 · '+status.node,status.node));field.value=status.node||'';readonly.checked=status.readOnly;}field.dataset.supported=readonly.dataset.supported=String(!active);
  $('[data-mcp-start]',w.body).dataset.supported=String(!active&&!!api.current.projectId&&api.current.mcpBridgeSupported===true);
  $('[data-mcp-stop]',w.body).dataset.supported=String(active);api.controls();
 }
 function open(remember=true){
  if(!api.current.projectId){api.toast('먼저 연결할 프로젝트를 여세요. 프로젝트 메뉴에서 ChatGPT 플러그인 연결을 선택할 수 있습니다.');return null;}
  const w=api.openWindow('mcp-bridge','ChatGPT 플러그인 연결',640,540,{refresh:true}),scope=api.current.projectId,bp=api.windows.get('blueprint'),node=bp?.blueprintData?.nodes.find(n=>n.id===bp.meta.blueprintNode)?.sourceId||(api.current.draft?.kind==='blueprint-node'?api.current.draft.id:'');
  w.title='ChatGPT 플러그인 연결';$('.caption strong',w.el).textContent=w.title;w.el.setAttribute('aria-label',w.title);
  w.body.innerHTML=`<div class="window-content"><p>Confectory 개발 플러그인을 ChatGPT 앱에 별도로 추가한 뒤 이 창에서 연결 범위를 준비하세요. 플러그인의 설정 절차가 실행 중인 엔진을 찾아 연결합니다.</p><p>${scope?'현재 연 프로젝트만 공유합니다.':'먼저 연결할 프로젝트를 여세요.'}</p><label>연결 범위<select data-operation data-mcp-node><option value="">현재 프로젝트 소유 소스</option>${node?`<option value="${esc(node)}">선택한 Blueprint 노드 · ${esc(node.split('/node:').at(-1))}</option>`:''}</select></label><p class="small">노드 범위를 쓰려면 Blueprint에서 C# 노드를 선택하고 이 창을 다시 여세요.</p><label class="check"><input type="checkbox" data-operation data-mcp-readonly checked>읽기 전용으로 연결</label><p class="small">읽기 전용을 해제하면 기존 초안 편집 도구를 사용합니다. 최종 파일 반영은 기존 변경 검토와 Confirm에서 직접 진행합니다.</p><div class="actions"><button data-operation data-mcp-start>연결 준비</button><button data-operation data-mcp-stop>연결 닫기</button></div><p data-mcp-status role="status"></p><p data-mcp-scope></p><details><summary>개발 패키지와 연결 정보</summary><p>개발용 패키지·온보딩·지원 표면: <a href="https://github.com/jorodane/Confectory/blob/work/current/docs/MCP_PLUGIN.md" target="_blank" rel="noopener noreferrer">Confectory 플러그인 안내</a></p><p class="small">ChatGPT 앱의 실제 설치와 연결은 별도 확인이 필요합니다. 여러 엔진이 보이면 플러그인 설정 절차에서 연결할 instanceId를 선택하세요.</p><code data-mcp-directory></code></details></div>`;
  $('[data-mcp-start]',w.body).onclick=()=>api.work(async()=>{if(api.current.projectId!==scope)throw Error('프로젝트가 바뀌었습니다. 연결 창을 다시 여세요.');await api.view.call('mcpBridge',{action:'start',projectId:scope,node:$('[data-mcp-node]',w.body).value,readOnly:$('[data-mcp-readonly]',w.body).checked});update();},'선택한 범위의 플러그인 연결을 준비했습니다.');
  $('[data-mcp-stop]',w.body).onclick=()=>api.work(async()=>{await api.view.call('mcpBridge',{action:'stop'});update();},'연결을 닫았습니다. 기존 초안은 유지됩니다.');
  update();if(remember){api.focus(w);api.persist();}return w;
 }
 return {open,restore:()=>open(false),update};
}
