import {createPrivateDeletionHistory} from './workspace-history.js';
import {createWindowDocuments} from './window-documents.js';
import {createNoteDocuments} from './note-documents.js';
import {createWorkspaceRuntime} from './workspace.js';

// The runtime owns nodes/selection/geometry. This adapter retains domain window
// DOM while it is detached, and persists only private presentation data.
export function createActualWorkspace(api) {
  let project=null,scope='',loading=false,scheduled=null,saving=null,changed=0,saved=0;
  const projects=new Map(),detached=new Map(),checkpoints=new Map();let inputStarted=0;let panelWorkspace='root';
  // Browser Data borrows an editor owner once it has an explicit field definition.
  const keepsEditing=(key,meta)=>key==='blueprint'||key.startsWith('blueprint-code:')||key==='source'||key.startsWith('editor-')||key.startsWith('table:')||((key==='browser'||key.startsWith('browser:')||key.startsWith('browser-tree:'))&&!!meta?.tableDefinition);
  const host={
    get isRestoring(){return loading},canNavigate:()=>!loading,preserveLifecycle:true,$:api.$,$$:api.$$,esc:api.esc,
    get project(){return project},get page(){return api.page},
    groups:{concept:'개념',feature:'기능',module:'모듈'},
    uid:()=>crypto.randomUUID(),toast:api.toast,modal:api.modal,contextMenu:api.contextMenu,
    persist:()=>schedule('layout'),get running(){return false},closeRun:()=>{},
    openNoteDocument:item=>noteDocuments.open(item),activateWorkspaceView:()=>{const changed=noteDocuments.deactivate();return windowDocuments.deactivate()||changed;},beforeRenderTabs:tabs=>windowDocuments.rememberTabs(tabs),renderDocumentTabs:tabs=>{noteDocuments.renderTabs(tabs);windowDocuments.renderTabs(tabs);windowDocuments.arrangeTabs(tabs);},refreshNoteDocuments:()=>{noteDocuments.render();windowDocuments.render();},noteChanged:(item,source)=>noteDocuments.changed(item,source),pruneNoteDocuments:()=>noteDocuments.prune(),
    revealWorkspaceForWindow:()=>{if(!loading){noteDocuments.deactivate();windowDocuments.deactivate();}},
    openWindowDocument:(w,opts)=>windowDocuments.open(w,opts),openWindowDocuments:windows=>windowDocuments.openMany(windows),focusWindowDocument:w=>{if(!loading)windowDocuments.activate(w.key);},closeWindowDocument:key=>windowDocuments.close(key),windowDocumentDropAt:(x,y)=>windowDocuments.tabDropAt(x,y),
    takeDetachedWindow:key=>{const w=detached.get(scope+'|'+key);detached.delete(scope+'|'+key);return w},
    detachWindow:w=>{if(w.overlay)return;detached.set(scope+'|'+w.key,w);capture()},
    foregroundZ:node=>node.key==='ai-preview'&&api.$('.augment-overlay')?271:undefined,
    hideWindowOnClose:key=>keepsEditing(key,runtime.state.windows.get(key)?.meta),
    layoutMetadata:w=>Object.fromEntries(['id','view','mode','group','density','query','sort','mainWorkspace','namespace','catalogue','kind','parent','queryInput','browserLocations','closedNamespaces','workerId','blueprintGraph','blueprintNode','blueprintPropertyAccess','blueprintPropertyNode','blueprintCodeMode','blueprintEnumDraft','blueprintOutputWidth','blueprintOutputCollapsed','blueprintZoom','blueprintPositions','blueprintCamera','blueprintViews','nodeTaskNode','nodeTaskQuery','nodeTaskPage','nodeTaskReason','buildJob','buildPage','conflictSourceId','referenceRequest','mapQuery','mapRoles','mapFocus','mapSelected','mapPositions','mapCamera','mapDidFit','mapFocusId','mapFocusPositions','tableDefinition','tableName','tableQuery','tableSort','tableSelected','tableInputs','tableFill','tableBuilder','tableColumnOrder','tableWidths','tableValueSort'].filter(key=>w.meta[key]!==undefined).map(key=>[key,w.meta[key]])),
    restoreActualWindow:layout=>restore(layout),
    afterSwitchWorkspace:()=>{const panels=structuredClone(runtime.workspaceRecord().participants||[]);api.clearPanels();api.clearYogi();panelWorkspace=runtime.state.activeWorkspaceId;api.restorePanels(panels);api.restoreYogi(runtime.workspaceRecord().yogiPresentation);api.render();schedule()},
    beforePrivateDelete:()=>deletionHistory.before(),recordPrivateDelete:before=>deletionHistory.record(before),privateHistoryMenu:()=>deletionHistory.menu(),
    beforeDeleteWorkspaces:ids=>{
      // Closing a child presentation must never release the domain editor view.
      const parent=runtime.workspaceRecord();
      for(const child of project.workspaces.filter(child=>ids.has(child.id)))
        for(const layout of child.layout||[])
          if(keepsEditing(layout.key,layout.meta)){
            if(!parent.layout.some(row=>row.key===layout.key))parent.layout.push({...layout,hidden:true});
            if(!runtime.state.windows.has(layout.key)){
              const cached=detached.get(scope+'|'+layout.key);
              const w=runtime.openWindow(layout.key,cached?.title||'보존된 편집 입력',layout.width,layout.height,{refresh:true,meta:layout.meta});
              if(!cached)w.body.innerHTML='<div class="window-content">닫힌 편집창의 입력을 보존했습니다. 실제 객체를 다시 열어 복원하세요.</div>';
              w.el.hidden=true;runtime.unregisterWorkspaceNode(w.key);
            }
          }
    },
    browserCanEnter:row=>api.projection.children(row.id).length>0,browserHierarchyParent:row=>api.projection.parent(row?.id),
    selectObject:id=>api.openDeclaration(id),openEditor:id=>{api.openDeclaration(id);return null},
    openBrowser:(...args)=>api.openBrowser(...args),renderBrowser:()=>api.renderObjects(),
    browserTreeCreateMenu:()=>api.unsupported('분류 편집','실제 계층 편집 계약은 아직 연결되지 않았습니다.'),
    browserCreateMenu:()=>api.unsupported('생성','실제 브라우저의 + 버튼에서 기존 선언 생성 계약을 사용하세요.'),
    duplicateChildBrowser:w=>api.duplicateBrowser(w),
    objectContext:(event,object)=>api.objectContext(object.id,event),
  };
  const runtime=createWorkspaceRuntime(host);
  const noteDocuments=createNoteDocuments({get project(){return project},get scope(){return scope},get loading(){return loading},canvas:()=>api.$('#workspace'),persist:()=>schedule('input'),refreshWindows:()=>windowDocuments.render(),toast:api.toast,renderTabs:()=>runtime.renderWorkspaceTabs(),renderDecorations:()=>runtime.renderWorkspaceDecorations(),editTitle:(item,owns)=>runtime.editWorkspaceTitle(item,owns,true)});
  const windowDocuments=createWindowDocuments({get project(){return project},get loading(){return loading},canvas:()=>api.$('#workspace'),runtime,persist:()=>schedule('layout'),toast:api.toast,contextMenu:api.contextMenu,renderTabs:()=>runtime.renderWorkspaceTabs(),refreshNotes:()=>noteDocuments.render(),retain:w=>host.detachWindow(w)});
  const deletionHistory=createPrivateDeletionHistory({project:()=>project,ready:()=>!!project&&!loading&&!api.isBusy,capture:()=>{capture();runtime.saveLayouts();},restore:restorePrivate,toast:api.toast,persist:()=>schedule('layout')});
  function restorePrivate(apply,reveal=[]){
    capture();runtime.cancelInteractions();loading=true;
    try{
      for(const w of [...runtime.state.windows.values()]){if(w.documentDocked)continue;host.detachWindow(w);w.el.remove();runtime.state.windows.delete(w.key);}
      runtime.state.workspaceNodes.clear();runtime.state.selectedWorkspaceNodeKeys.clear();apply();
      if(!runtime.workspaceRecord())runtime.state.activeWorkspaceId='root';
      runtime.state.visitedWorkspaceTabs=(project.visitedWorkspaceTabs||['root']).filter(id=>runtime.workspaceRecord(id));
      runtime.renderWorkspaceDecorations();runtime.renderWorkspaceTabs();
      for(const row of runtime.workspaceRecord().layout.map(row=>structuredClone(row)))runtime.restoreWindow(row);
      windowDocuments.restore();noteDocuments.render();runtime.links.schedule();const restored=reveal.map(key=>runtime.state.windows.get(key)).filter(w=>w&&!w.el.hidden&&!w.documentDocked);if(restored.length){runtime.setWindowSelection(restored);runtime.focusWorkspaceNode(restored.at(-1));}
    }finally{loading=false;api.controls?.();}
    runtime.saveLayouts();schedule('layout');
  }
  document.addEventListener('keydown',event=>{if(!project||loading||api.page!=='work'||event.altKey||event.isComposing||!(event.ctrlKey||event.metaKey)||!['z','y'].includes(event.key.toLowerCase())||event.target.isContentEditable||event.target.closest?.('input,textarea,select,.modal,.tab-document,.note-document'))return;const undo=event.key.toLowerCase()==='z'&&!event.shiftKey;if((undo?project.privateHistory?.undo:project.privateHistory?.redo)?.length){event.preventDefault();event.stopImmediatePropagation();undo?deletionHistory.undo():deletionHistory.redo();}},true);
  function capture(){if(project){windowDocuments.capture();if(!loading&&!project.recoveryFailed){project.selectedObjectId=api.current.draft?.id;project.editorBindings=api.current.editorViews.map(({view,id,mode})=>({view,id,mode}));}project.inputs=api.captureInputs(detached.get(scope+'|source'));const owner=runtime.workspaceRecord();if(owner&&!loading&&panelWorkspace===runtime.state.activeWorkspaceId){owner.participants=api.capturePanels();owner.yogiPresentation=api.captureYogi();}if(owner){if(runtime.state.activeWorkspaceId==='root')project.rootWorkspaceView={...project.workspaceView};else owner.view={...project.workspaceView};}if(owner)for(const w of runtime.state.windows.values()){if(w.overlay)continue;const row=owner.layout.find(row=>row.key===w.key);if(row)Object.assign(row,runtime.windowLayout(w));}}}
  function snapshot(){capture();project.activeWorkspaceId=runtime.state.activeWorkspaceId;project.visitedWorkspaceTabs=[...runtime.state.visitedWorkspaceTabs];const value=JSON.parse(JSON.stringify(project));delete value.selectedNodeKeys;
    // Persist fresh input while a pointer gesture is provisional, using its last
    // committed geometry. A cancel can never leave an intermediate disk layout.
    const gesture=runtime.state.gesture;if(gesture?.project===project){const owner=gesture.workspaceId==='root'?value:value.workspaces.find(space=>space.id===gesture.workspaceId);if(owner)for(const item of gesture.entries){const row=item.kind==='window'?owner.layout.find(row=>row.key===item.key):(gesture.workspaceId==='root'?owner.workspaceItems:owner.items).find(row=>row.id===item.itemId);if(row)Object.assign(row,item.geometry);}}
    return value;}
  function inputKey(value){const notes=[];for(const item of value.workspaceItems||[])if(item.kind==='note')notes.push([item.id,item.text,item.richText,item.titleStyle]);for(const child of value.workspaces||[])for(const item of child.items||[])if(item.kind==='note')notes.push([item.id,item.text,item.richText,item.titleStyle]);return JSON.stringify([value.inputs,value.selectedObjectId,value.editorBindings,notes]);}
  function same(left,right){return JSON.stringify(left)===JSON.stringify(right);}
  function pending(){if(!project||loading)return false;return !same(snapshot(),checkpoints.get(scope));}
  function failure(error){api.setWorkspaceStatus('배치 저장 실패');api.toast('작업 공간 저장 실패 · '+error.message+' · 입력과 배치는 유지됩니다.');}
  function schedule(hint='input'){
    if(!project||loading)return;const value=snapshot(),checkpoint=checkpoints.get(scope);if(same(value,checkpoint))return;
    changed++;api.setWorkspaceStatus('배치 변경 있음');
    if(hint==='input'&&inputKey(value)!==inputKey(checkpoint||{})){
      if(!inputStarted)inputStarted=Date.now();clearTimeout(scheduled);
      const attempt=()=>{if(api.isBusy){scheduled=setTimeout(attempt,100);return;}flushInputs().catch(failure);};
      scheduled=setTimeout(attempt,Math.max(0,Math.min(750,2000-(Date.now()-inputStarted))));
    }
  }
  async function persist(all){
    if(!project||loading)return;if(saving){await saving;return persist(all);}
    const value=snapshot(),checkpoint=checkpoints.get(scope);if(same(value,checkpoint))return;
    if(!all&&inputKey(value)===inputKey(checkpoint||{}))return;
    const owner=scope;
    saving=(async()=>{await api.save(value,owner);checkpoints.set(owner,value);if(scope===owner){saved=changed;inputStarted=0;api.setWorkspaceStatus(pending()?'배치 변경 있음':'');}})();
    try{await saving;}finally{saving=null;}
  }
  async function flush(){clearTimeout(scheduled);await persist(true);if(pending())return flush();if(project&&!loading)api.setWorkspaceStatus('');}
  async function flushInputs(){clearTimeout(scheduled);await persist(false);if(project&&!loading&&inputKey(snapshot())!==inputKey(checkpoints.get(scope)||{}))schedule();}
  // Durable placement/camera changes are dirty in memory until the next periodic checkpoint.
  setInterval(()=>{if(project&&!loading&&!api.isBusy&&pending()&&inputKey(snapshot())===inputKey(checkpoints.get(scope)||{}))flush().catch(failure);},15000);
  function findOwner(key){
    if(!project)return null;
    if(project.layout.some(row=>row.key===key))return 'root';
    return project.workspaces.find(child=>child.layout.some(row=>row.key===key))?.id??null;
  }
  function shouldRender(key){const owner=findOwner(key);return !owner||owner===runtime.state.activeWorkspaceId;}
  function restore(layout){
    const cached=detached.get(scope+'|'+layout.key);
    if(cached)return runtime.openWindow(layout.key,cached.title,cached.width,cached.height,{refresh:true});
    if(layout.key==='source'){api.editor();return runtime.state.windows.get('source');}
    if(layout.key==='browser'||layout.key.startsWith('browser:')||layout.key.startsWith('browser-tree:')){const w=api.browser(layout.meta?.group||'concept',layout.key);Object.assign(w.meta,layout.meta);w.browserFilterRestored=false;w.browserFilterError=false;return api.browser(w.meta.group,layout.key);}
    if(layout.key==='blueprint')return api.blueprint(layout.meta||{});
    if(layout.key.startsWith('blueprint-code:'))return api.blueprintCode(layout.meta||{});
    if(layout.key==='node-tasks')return api.nodeTasks(layout.meta||{});
    if(layout.key==='builds')return api.builds(layout.meta||{});
    if(layout.key==='history')return api.history(layout.meta||{});
    if(layout.key==='conflict')return api.conflict(layout.meta||{});
    if(layout.key==='definition')return api.definition(layout.meta||{});
    if(layout.key==='map')return api.map(layout.meta||{});
    if(layout.key.startsWith('table:')&&layout.meta?.tableDefinition)return api.table(layout.meta.tableDefinition,layout.meta||{});
    if(layout.key==='custom')return api.custom(layout.meta||{});
    if(layout.key==='schema'){api.schema();return runtime.state.windows.get('schema');}
    if(layout.key==='declaration'){api.declaration(layout.meta?.id);return runtime.state.windows.get('declaration');}
    if(layout.key==='worker')return api.worker(layout.meta?.workerId);
    if(layout.key==='connections'){api.connections();return runtime.state.windows.get('connections');}
    if(layout.key==='packs')return api.packs();
    if(layout.key==='run')return api.run();
    if(layout.key==='targets'){api.targets();return runtime.state.windows.get('targets');}
    if(layout.key.startsWith('editor-')){api.renderViews();return runtime.state.windows.get(layout.key);}
    // Unsupported/restale views are retained as presentation records, never
    // represented as successful domain editors or discarded silently.
    const w=runtime.openWindow(layout.key,'편집창 복원',420,220,{refresh:true,meta:layout.meta});
    w.body.innerHTML='<div class="window-content"><p>이 창의 실제 기능을 다시 연결해야 합니다. 저장된 입력은 유지됩니다.</p></div>';
    return w;
  }
  function attach(state){
    loading=true;
    if(project){capture();projects.set(scope,project);}
    scope=state.projectId;inputStarted=0;
    project=projects.get(scope)||state.presentation||{version:1,layout:[],workspaces:[],workspaceItems:[],workspaceView:{x:0,y:0,scale:1},rootWorkspaceView:{x:0,y:0,scale:1},activeWorkspaceId:'root',visitedWorkspaceTabs:['root'],inputs:{}};
    Object.defineProperty(project,'objects',{configurable:true,enumerable:false,get:()=>api.projection.workspaceRows()});
    project.workspaceView??={x:0,y:0,scale:1};project.rootWorkspaceView??={...project.workspaceView};
    runtime.state.windows.clear();runtime.state.workspaceNodes.clear();runtime.state.selectedWorkspaceNodeKeys.clear();
    runtime.state.activeWorkspaceId=runtime.workspaceRecord(project.activeWorkspaceId)?project.activeWorkspaceId:'root';
    runtime.state.visitedWorkspaceTabs=(project.visitedWorkspaceTabs||['root']).filter(id=>runtime.workspaceRecord(id));
    Object.assign(project.workspaceView,runtime.state.activeWorkspaceId==='root'?project.rootWorkspaceView:runtime.workspaceRecord().view);
    if(!checkpoints.has(scope)){const baseline=JSON.parse(JSON.stringify(project));delete baseline.selectedNodeKeys;checkpoints.set(scope,baseline);}project.selectedNodeKeys=[];api.restoreInputs(project.inputs||{});
    runtime.setupWorkspaceNavigation();runtime.setupWindowSelection();runtime.renderWorkspaceTabs();runtime.renderWorkspaceDecorations();
    const layouts=runtime.workspaceRecord().layout.map(row=>structuredClone(row));
    for(const layout of layouts)runtime.restoreWindow(layout);windowDocuments.restore();
    runtime.setWorkspaceNodeSelection((project.selectedNodeKeys||[]).map(key=>runtime.state.workspaceNodes.get(key)).filter(Boolean));
    loading=false;changed=0;saved=0;panelWorkspace=runtime.state.activeWorkspaceId;api.restorePanels(runtime.workspaceRecord().participants||[]);api.restoreYogi(runtime.workspaceRecord().yogiPresentation);
    api.$('#workspace').addEventListener('input',()=>schedule());
    const bindings=project.editorBindings||[],selected=project.selectedObjectId;
    const missing=bindings.filter(binding=>!state.editorViews.some(row=>row.view===binding.view&&row.id===binding.id&&row.mode===binding.mode));
    if(missing.length||(selected&&selected!==state.draft?.id)){
      loading=true;api.setWorkspaceStatus('편집창 복원 중');const owner=scope;
      (async()=>{
        while(api.isBusy&&scope===owner)await new Promise(resolve=>setTimeout(resolve,50));
        if(scope!==owner)return;
        try{await api.restoreBindings(missing,selected);if(scope!==owner)return;project.recoveryFailed=false;api.setWorkspaceStatus('편집창 복원됨');
          const layouts=runtime.workspaceRecord().layout.map(row=>structuredClone(row));
          for(const row of layouts)runtime.restoreWindow(row);windowDocuments.restore();runtime.setWorkspaceNodeSelection((project.selectedNodeKeys||[]).map(key=>runtime.state.workspaceNodes.get(key)).filter(Boolean));
        }catch(error){if(scope===owner){project.recoveryFailed=true;api.setWorkspaceStatus('편집창 복원 실패');api.toast('실제 편집창 복원 실패 · 입력과 원래 배치는 유지됩니다.');}}
        finally{if(scope===owner){loading=false;api.controls?.();if(!project.recoveryFailed)runtime.saveLayouts();}}
      })();
    }
  }
  function detach(){if(!project)return;runtime.cancelInteractions();capture();loading=true;api.clearPanels();api.clearYogi();clearTimeout(scheduled);runtime.saveLayouts();capture();for(const w of runtime.state.windows.values())host.detachWindow(w);projects.set(scope,project);noteDocuments.detach();windowDocuments.detach();project=null;scope='';loading=false;changed=0;saved=0;}
  function reveal(key){const owner=findOwner(key);if(owner&&owner!==runtime.state.activeWorkspaceId)runtime.switchWorkspace(owner);let w=runtime.state.windows.get(key);if(!w){const layout=runtime.workspaceRecord()?.layout.find(row=>row.key===key);if(layout)w=runtime.restoreWindow(layout);}if(w){w.el.hidden=false;runtime.registerWorkspaceNode(w);runtime.focusWindow(w);runtime.saveLayouts();}return w;}
  return {runtime,noteDocuments,windowDocuments,deletionHistory,attach,detach,flush,flushInputs,schedule,shouldRender,reveal,get project(){return project},get loading(){return loading}};
}
