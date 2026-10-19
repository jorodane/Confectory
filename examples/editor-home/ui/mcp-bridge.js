// Engine connection is independent of the existing project/owned-node capability.
// This panel is rendered inside the existing Codex connection form.
export function createMcpBridge(api){
 const {$,esc}=api;
 function update(){
  for(const root of document.querySelectorAll('[data-mcp-panel]')){
   if(!$('[data-mcp-status]',root))continue;
   const status=api.current.mcpBridge||{state:'stopped'},active=status.state==='ready',scope=status.scope,project=api.current.projectId||'',field=$('[data-mcp-node]',root),readonly=$('[data-mcp-readonly]',root);
   if(root.dataset.project!==project||(root.dataset.scope&&!scope)){
    root.dataset.project=project;const bp=api.windows.get('blueprint'),node=bp?.blueprintData?.nodes.find(n=>n.id===bp.meta.blueprintNode)?.sourceId||(api.current.draft?.kind==='blueprint-node'?api.current.draft.id:'');
    field.innerHTML='<option value="choose">접근 범위를 고르세요</option><option value="">현재 프로젝트 소유 소스</option>'+(node?'<option value="'+esc(node)+'">선택한 Blueprint 노드 · '+esc(node.split('/node:').at(-1))+'</option>':'');field.options[0].textContent='접근 범위를 고르세요';readonly.checked=true;
   }
   if(scope){if(![...field.options].some(o=>o.value===scope.node))field.add(new Option('허용한 노드 · '+scope.node,scope.node));field.value=scope.node||'';readonly.checked=scope.readOnly;}
   root.dataset.scope=scope?.id||'';root.dataset.instance=status.instance||'';root.dataset.scopeVersion=String(status.scopeVersion??0);
   $('[data-mcp-status]',root).textContent=status.message||(api.current.mcpBridgeSupported?'프로젝트를 고르기 전에 엔진부터 연결할 수 있습니다.':'현재 호스트는 로컬 플러그인 연결을 지원하지 않습니다.');
   $('[data-mcp-scope]',root).textContent=scope?scope.title+' · '+(scope.node||'프로젝트 소유 소스')+' · '+(scope.readOnly?'읽기 전용':'기존 초안 편집 도구'):'프로젝트 접근 없음 · 엔진 연결과 별개로 범위를 허용합니다.';
   $('[data-mcp-target]',root).textContent=project?'접근 대상: '+api.current.title:'프로젝트는 나중에 홈에서 직접 선택하세요. 자동으로 열거나 공유하지 않습니다.';
   $('[data-mcp-directory]',root).textContent=status.directory||'';$('[data-mcp-instance]',root).textContent=status.instance||'';
   field.dataset.supported=readonly.dataset.supported=String(active&&!!project&&!scope);
   $('[data-mcp-start]',root).dataset.supported=String(!active&&api.current.mcpBridgeSupported===true);
   $('[data-mcp-stop]',root).dataset.supported=String(active);
   $('[data-mcp-grant]',root).dataset.supported=String(active&&!!project&&!scope&&field.value!=='choose');
   $('[data-mcp-revoke]',root).dataset.supported=String(active&&!!scope);
   const site=status.site||{},paired=site.state==='connected'&&site.expiresAt>Date.now(),nativeSite=typeof globalThis.confectoryWebUI?.connectSite==='function';root.dataset.siteConnection=site.connectionId||'';
   if(active&&!paired)$('[data-mcp-status]',root).textContent='로컬 엔진 준비 완료 · ChatGPT 연결은 아직 완료되지 않았습니다.';
   $('[data-mcp-site-hint]',root).textContent=!nativeSite?(globalThis.confectoryWebUI?.send?'현재 편집기 호스트에는 로그인 창 기능이 없습니다. 편집기를 닫은 뒤 같은 폴더의 Confectory.bat로 다시 실행하세요.':'현재 브라우저 진단 모드에서는 로그인 창을 열 수 없습니다. Windows의 Confectory.bat로 연 편집기에서 연결하세요.'):paired?'ChatGPT에 엔진이 연결됐습니다. 연결 창은 다시 열 수 있고, 연결 해제는 별도 버튼으로 진행합니다. 프로젝트 접근은 아래에서 허용하세요.':site.state==='waiting'?'열린 전용 창에서 ChatGPT 로그인과 연결을 완료하세요.':active?'다음: 2. ChatGPT 로그인 · 엔진 연결을 누르세요. 프로젝트를 먼저 고를 필요는 없습니다.':'1. 엔진 연결 준비 → 2. ChatGPT 로그인 · 엔진 연결 순서로 진행하세요.';
   $('[data-mcp-site-state]',root).textContent=paired?(site.scopeGranted?'개인 플러그인 연결됨 · 선택한 범위 공유 중':'개인 플러그인 연결됨 · 프로젝트 접근 없음'):site.state==='waiting'?'전용 연결 창에서 로그인과 연결을 완료하세요.':'개인 플러그인은 별도 연결 창에서 연결합니다.';
   $('[data-mcp-site-open]',root).dataset.supported=String(active&&nativeSite);
   $('[data-mcp-site-open]',root).textContent=paired?'연결 창 다시 열기':'2. ChatGPT 로그인 · 엔진 연결';
   $('[data-mcp-site-disconnect]',root).dataset.supported=String(active&&['connected','waiting'].includes(site.state)&&typeof globalThis.confectoryWebUI?.disconnectSite==='function');
   $('[data-mcp-site-grant]',root).dataset.supported=String(paired&&!!scope&&!site.scopeGranted);
   $('[data-mcp-site-revoke]',root).dataset.supported=String(paired&&site.scopeGranted===true);
  }
  api.controls();
 }
 function mount(root){
  root.dataset.mcpPanel='';root.innerHTML='<p>ChatGPT 앱의 플러그인으로 이 Confectory 엔진에 연결합니다. 연결한 뒤 대화 중에 접근할 프로젝트와 범위를 따로 고를 수 있습니다.</p><div class="actions"><button data-operation data-mcp-start>엔진 연결 준비</button><button class="primary" data-operation data-mcp-site-open>2. ChatGPT 로그인 · 엔진 연결</button><button data-operation data-mcp-site-disconnect>개인 플러그인 연결 해제</button><button data-operation data-mcp-stop>엔진 연결 닫기</button></div><p data-mcp-status role="status"></p><p data-mcp-site-hint role="status" class="small"></p><fieldset class="mcp-project-scope"><legend>프로젝트 접근</legend><p data-mcp-target></p><label>접근 범위 <select data-operation data-mcp-node></select></label><label class="check"><input type="checkbox" data-operation data-mcp-readonly checked>프로젝트 읽기 전용</label><p class="small">편집을 허용해도 기존 초안에만 적용합니다. 최종 반영은 변경 검토와 Review/Confirm에서 직접 진행합니다.</p><div class="actions"><button data-operation data-mcp-grant>선택한 범위 허용</button><button data-operation data-mcp-revoke>프로젝트 접근 해제</button></div><p data-mcp-scope></p></fieldset><details><summary>개발 패키지와 연결 정보</summary><p><a href="https://github.com/jorodane/Confectory/blob/work/current/docs/MCP_PLUGIN.md" target="_blank" rel="noopener noreferrer">개발 소스 등록·설치 안내</a></p><p class="small">실제 ChatGPT 앱 설치와 연결은 별도 확인이 필요합니다. 여러 엔진이면 instanceId로 선택합니다.</p><p>현재 엔진 instanceId: <code data-mcp-instance></code></p><code data-mcp-directory></code></details>';
  root.querySelector('details').insertAdjacentHTML('beforebegin','<fieldset><legend>개인 ChatGPT 플러그인</legend><p data-mcp-site-state role="status"></p><p class="small">위의 로그인 버튼으로 전용 창을 열고 ChatGPT에 연결하세요. 연결한 뒤에도 프로젝트 접근은 별도로 허용해야 합니다.</p><div class="actions"><button data-operation data-mcp-site-grant>현재 범위를 개인 플러그인에 허용</button><button data-operation data-mcp-site-revoke>개인 플러그인 접근 해제</button></div></fieldset>');
  const call=(action,args={})=>api.work(async()=>{if(!root.isConnected)throw Error('연결 화면이 닫혔습니다. 다시 확인하세요.');if((action==='scope'||action==='site-grant')&&(!root.dataset.project||root.dataset.project!==api.current.projectId))throw Error('접근 대상이 바뀌었습니다.');await api.view.call('mcpBridge',{action,...args});update();},'엔진 연결과 프로젝트 접근 상태를 갱신했습니다.');
  $('[data-mcp-start]',root).onclick=()=>call('start');$('[data-mcp-stop]',root).onclick=()=>call('stop');
  $('[data-mcp-node]',root).onchange=update;
  $('[data-mcp-grant]',root).onclick=()=>call('scope',{instanceId:root.dataset.instance,projectId:root.dataset.project,scopeVersion:Number(root.dataset.scopeVersion),node:$('[data-mcp-node]',root).value,readOnly:$('[data-mcp-readonly]',root).checked});
  $('[data-mcp-revoke]',root).onclick=()=>call('revoke',{instanceId:root.dataset.instance,scopeVersion:Number(root.dataset.scopeVersion)});
  $('[data-mcp-site-open]',root).onclick=()=>api.work(async()=>{if(!root.isConnected)throw Error('연결 화면이 닫혔습니다.');const result=await globalThis.confectoryWebUI.connectSite();if(!result?.ok)throw Error('연결 창을 시작하지 못했습니다.');},'개인 플러그인 연결 창을 열었습니다.');
  $('[data-mcp-site-disconnect]',root).onclick=()=>api.work(async()=>{if(!root.isConnected)throw Error('연결 화면이 닫혔습니다.');const result=await globalThis.confectoryWebUI.disconnectSite();if(!result?.ok)throw Error('연결을 해제하지 못했습니다.');await api.view.update();},'개인 플러그인 연결을 해제했습니다. 저장된 로그인은 연결 창에서 별도로 지울 수 있습니다.');
  $('[data-mcp-site-grant]',root).onclick=()=>call('site-grant',{connectionId:root.dataset.siteConnection,instanceId:root.dataset.instance,scopeVersion:Number(root.dataset.scopeVersion),scopeId:root.dataset.scope});
  $('[data-mcp-site-revoke]',root).onclick=()=>call('site-revoke');
  update();
 }
 return {mount,update};
}
