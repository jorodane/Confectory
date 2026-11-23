const yogiDragType = 'application/x-yogibox';
const messageId = () => crypto.randomUUID().replaceAll('-', '');
const eyUnsupported = 'EY가 담긴 YogiBox는 게스트가 보낼 수 없습니다. 기존 상자는 그대로 유지됩니다.';

function publicComposer({call, alive, label, refresh, attachment, relay}) {
 const form = document.createElement('form');
 form.className = 'chat-compose local-public-compose';
 form.setAttribute('aria-label', label);
 form.innerHTML = '<textarea maxlength="2048" aria-label="공용 메시지 입력" placeholder="로컬 공용 채팅에 보낼 메시지" autocomplete="off"></textarea><button type="submit" class="primary">공용으로 보내기</button><small data-public-send-status aria-live="polite"></small>';
 const input = form.querySelector('textarea'), button = form.querySelector('button');
 if (relay) input.placeholder = '공용 채팅에 보낼 메시지';
 const status = form.querySelector('[data-public-send-status]');
 let enabled = false, sending = false, retired = false, pending = null, selection = null, selecting = false;
 let attachButton, cancelButton;
 function paint() {
  const busy = sending || selecting;
  button.disabled = !enabled || busy || !input.value.trim();
  input.readOnly = !enabled || busy;
  if (attachment) {
   attachButton.hidden = !!selection;
   attachButton.disabled = !enabled || busy || !attachment.canAttach();
   cancelButton.hidden = !selection;
   cancelButton.disabled = !enabled || busy;
  }
 }
 if (attachment) {
  const controls = document.createElement('div');
  controls.className = 'local-public-attachment';
  controls.innerHTML = '<button type="button" data-attach-box>봉인 YogiBox 첨부</button><button type="button" data-cancel-box hidden>YogiBox 첨부 취소</button>';
  form.insertBefore(controls, status);
  attachButton = controls.querySelector('[data-attach-box]');
  cancelButton = controls.querySelector('[data-cancel-box]');
  async function prepare() {
   if (!alive() || retired || attachButton.disabled || selection) return;
   selecting = true;
   paint();
   const id = messageId();
   try {
    const reply = await call({action:'prepare-attachment', id});
    if (!alive() || retired) return;
    if (reply.status === 'ey-unsupported') {
     status.textContent = eyUnsupported;
     return;
    }
    if (reply.status !== 'ready') throw new Error('box_unavailable');
    selection = id;
    pending = null;
    status.textContent = '봉인된 YogiBox 첨부 준비됨';
   } catch {
    if (alive() && !retired) status.textContent = '봉인된 YogiBox를 첨부할 수 없습니다.';
   } finally {
    selecting = false;
    if (!retired) paint();
   }
  }
  attachButton.onclick = prepare;
  cancelButton.onclick = async () => {
   if (!alive() || retired || cancelButton.disabled || !selection) return;
   selecting = true;
   paint();
   try {
    const reply = await call({action:'cancel-attachment', id:selection});
    if (!alive() || retired) return;
    if (reply.status !== 'cancelled') throw new Error('box_unavailable');
    selection = null;
    pending = null;
    status.textContent = 'YogiBox 첨부를 취소했습니다.';
   } catch {
    if (alive() && !retired) status.textContent = '첨부 취소를 확인하지 못했습니다.';
   } finally {
    selecting = false;
    if (!retired) paint();
   }
  };
  form.ondragover = event => {
   if (!attachment.dragging() || !event.dataTransfer.types.includes(yogiDragType) || attachButton.disabled || selection) return;
   event.preventDefault();
   event.dataTransfer.dropEffect = 'copy';
  };
  form.ondrop = event => {
   if (!attachment.dragging() || !event.dataTransfer.types.includes(yogiDragType) || attachButton.disabled || selection) return;
   event.preventDefault();
   attachment.dropped();
   void prepare();
  };
 }
 input.oninput = paint;
 form.onsubmit = async event => {
  event.preventDefault();
  if (!alive() || retired || button.disabled) return;
  const text = input.value;
  if (!pending || pending.text !== text) pending = {id:selection ?? messageId(), text};
  sending = true;
  status.textContent = '';
  paint();
  try {
   const reply = await call({action:selection ? 'send-attachment' : 'send', ...pending});
   if (!alive() || retired) return;
   if (reply.status === 'committed') {
    pending = null;
    selection = null;
    input.value = '';
    refresh?.();
   } else if (reply.status === 'ey-unsupported') {
    status.textContent = eyUnsupported;
   } else if (reply.status === 'denied') {
    status.textContent = '저장이 거절되었습니다. 입력은 유지됩니다.';
   } else {
    enabled = false;
    status.textContent = '공용 채팅 연결이 종료되었습니다. 입력은 유지됩니다.';
   }
  } catch {
   if (alive() && !retired) status.textContent = '전송을 확인하지 못했습니다. 입력은 유지됩니다.';
  } finally {
   sending = false;
   if (!retired) paint();
  }
 };
 paint();
 return {
  form,
  paint,
  enable(value) { enabled = value; paint(); },
  close() { retired = true; pending = null; selection = null; input.value = ''; form.remove(); }
 };
}

export function createLocalChatDevelopment({modal, makeView, scope, hostTarget, refreshHost, sealedYogi, rgbCanvas}) {
 let dialog = null, yogiDrag = null;
 const close = () => dialog?.close();
 function update() {
  if (dialog && dialog.scope !== scope()) close();
  dialog?.guestComposer?.paint();
  const composer = dialog?.hostComposer;
  if (!composer) return;
  const target = hostTarget();
  if (target && target.previousElementSibling !== composer.form) target.before(composer.form);
  else if (!target) composer.form.remove();
  composer.paint();
 }

 function open(mode) {
  const lan = mode.startsWith('lan-'), relay = mode.startsWith('relay-'), issuing = mode.endsWith('issue');
  const confirmTarget = lan || relay;
  const title = relay ? (issuing ? '인터넷 채팅 초대 (시험)' : '인터넷 초대 참가 (시험)') :
   lan ? (issuing ? 'LAN 채팅 초대' : 'LAN 초대 참가') : (issuing ? '로컬 채팅 초대' : '로컬 초대 참가');
  modal(title, issuing
   ? `<p class="small">${relay ? '사전에 신뢰를 설정한 시험 중계를 사용합니다. 이 초대는 최대 5분 동안 한 번 쓸 수 있습니다. 철회하거나 이 창을 닫으면 연결이 종료됩니다.' : lan ? '같은 네트워크에서 연결할 두 PC의 사설 IPv4 주소를 입력하세요. 이 초대는 지정한 PC에서 5분 안에 한 번 사용할 수 있습니다. 이 창을 닫으면 초대가 철회되고 연결이 종료됩니다.' : '같은 컴퓨터의 게스트 창에만 이 초대를 전달하세요. 5분 안에 한 번 사용할 수 있습니다. 발급 후 채팅 탭에서 공용으로 보낼 수 있습니다. 이 창을 닫으면 초대와 연결이 종료됩니다.'}</p>
      ${lan ? '<div class="field"><label for="lan-host-address">내 PC IPv4</label><input id="lan-host-address" maxlength="15" required autocomplete="off" spellcheck="false"></div><div class="field"><label for="lan-guest-address">참가 PC IPv4</label><input id="lan-guest-address" maxlength="15" required autocomplete="off" spellcheck="false"></div>' : ''}
      <div class="field" data-invite-result hidden><label for="local-issued-invite">일회용 초대</label><textarea id="local-issued-invite" rows="3" readonly spellcheck="false" autocomplete="off"></textarea></div>
      <p data-local-chat-status aria-live="polite"></p>
      <div class="actions"><button type="button" data-issue class="primary" disabled>일회용 초대 발급</button><button type="button" data-select-invite hidden>초대 텍스트 선택</button>${relay ? '<button type="button" data-revoke-invite hidden>초대 철회 및 연결 종료</button>' : ''}</div>`
   : `<p class="small">${relay ? '원본 프로젝트 호스트가 직접 전달한 초대를 입력하고, 이 에디터에 설정된 시험 중계와 호스트를 확인하세요.' : lan ? '원본 프로젝트 호스트에게 직접 받은 초대를 입력하고, 연결 대상과 프로젝트를 확인하세요.' : '이 컴퓨터의 호스트 창에서 직접 전달받은 초대만 입력하세요. 참가 중 읽거나 보낸 메시지는 이 프로젝트의 공용 채팅에 속합니다.'}</p>
      <form autocomplete="off"><div class="field"><label for="local-invite">일회용 초대</label><textarea id="local-invite" rows="3" maxlength="4096" required spellcheck="false" autocomplete="off"></textarea></div>
      <div class="field"><label for="local-guest-name">참가 이름</label><input id="local-guest-name" maxlength="64" required autocomplete="off"></div>
      ${confirmTarget ? '<div data-lan-review aria-live="polite" hidden></div>' : ''}<div class="actions"><button type="submit" class="primary" disabled>${confirmTarget ? '연결 대상 확인' : '참가'}</button></div></form>
      <p data-local-chat-status aria-live="polite"></p><section data-local-chat-messages aria-label="참가 중 받은 공용 채팅"></section>`,
  (root, dismiss) => {
   const view = makeView(), abort = new AbortController();
   const owner = {scope: scope(), close: dismiss};
   dialog = owner;
   const alive = () => dialog === owner && scope() === owner.scope;
   const status = root.querySelector('[data-local-chat-status]');
   const button = root.querySelector(issuing ? '[data-issue]' : 'button[type=submit]');
   const input = root.querySelector('textarea');
   const messages = root.querySelector('[data-local-chat-messages]');
   const attachment = {
    canAttach:sealedYogi, dragging:() => yogiDrag?.owner === owner,
    dropped:() => { yogiDrag.dropped = true; }
   };
   let timer = null, expiryTimer = null, guestComposer = null, guestViewer = null;
   root._ownedCleanup = () => {
    if (dialog === owner) dialog = null;
    clearTimeout(timer);
    clearTimeout(expiryTimer);
    input.value = '';
    messages?.replaceChildren();
    guestViewer?.close();
    owner.hostComposer?.close();
    guestComposer?.close();
    abort.abort();
    void view.dispose().catch(() => {});
   };

   async function call(input) {
    for (let attempt = 0; alive(); attempt++) {
     try { return await view.transient(confirmTarget ? 'localProjectChat' : 'localChatDevelopment', input, abort.signal); }
     catch (error) {
      if (error.message !== 'busy' || attempt >= 5) throw error;
      await new Promise(resolve => setTimeout(resolve, 80));
     }
    }
    throw new Error('view_closed');
   }

   async function mount() {
    for (let attempt = 0; alive(); attempt++) {
     try { return await view.mount(); }
     catch (error) {
      if (error.message !== 'busy' || attempt >= 5) throw error;
      await new Promise(resolve => setTimeout(resolve, 80));
     }
    }
   }

   async function poll() {
    try {
     const reply = await call({action:'read'});
     if (!alive()) return;
     if (reply.status !== 'joined') throw new Error('connection_closed');
     guestComposer.enable(true);
     if (guestViewer && !reply.messages.some(row => row.id === guestViewer.id && row.attachmentId === row.id))
      guestViewer.close();
     messages.replaceChildren();
     for (const message of reply.messages) {
      const row = document.createElement('div');
      row.className = 'message';
      const name = document.createElement('strong'), text = document.createElement('span');
      name.textContent = message.sender;
      text.textContent = message.text;
      row.append(name, text);
      if (message.attachmentId === message.id) {
       const show = document.createElement('button');
       show.type = 'button';
       show.className = 'tag amber';
       show.textContent = 'YogiBox 보기';
       show.onclick = () => openAttachment(message.id);
       row.append(show);
      }
      messages.append(row);
     }
     status.textContent = reply.messages.length ?
      (reply.omitted ? '참가 중 받은 최근 128개 메시지' : '연결됨') : '새 메시지가 없습니다.';
    } catch (error) {
     if (!alive()) return;
     if (error.message !== 'busy') {
      guestComposer.enable(false);
      guestViewer?.close();
      messages.replaceChildren();
      status.textContent = '연결이 종료되었습니다. 창을 닫고 새 초대로 참가하세요.';
      void view.dispose().catch(() => {});
      return;
     }
    }
    timer = setTimeout(poll, 1000);
   }

   function openAttachment(id) {
    guestViewer?.close();
    const box = document.createElement('section');
    box.className = 'yogi-readonly-items';
    box.setAttribute('aria-label', 'YogiBox 보기');
    box.innerHTML = '<div aria-live="polite"></div><button type="button">YogiBox 보기 닫기</button>';
    const body = box.firstElementChild;
    const owner = {id, close:() => { if (guestViewer === owner) guestViewer = null; box.remove(); }};
    guestViewer = owner;
    box.lastElementChild.onclick = owner.close;
    messages.after(box);
    const current = () => alive() && guestViewer === owner;
    const denied = () => { if (current()) body.textContent = '이 연결에서 YogiBox를 열 수 없습니다.'; };
    body.textContent = 'YogiBox 읽는 중…';
    call({action:'attachment', id}).then(reply => {
     if (!current()) return;
     if (reply.status !== 'available') return denied();
     const description = document.createElement('p');
     description.textContent = reply.description;
     body.replaceChildren(description);
     for (const item of reply.items) {
      const row = document.createElement('p');
      if (item.kind === 'image') {
       const preview = document.createElement('button');
       preview.type = 'button';
       preview.textContent = '이미지 보기';
       preview.onclick = async () => {
        preview.disabled = true;
        try {
         const image = await call({action:item.image === 0 ? 'first-image' : 'second-image', id});
         if (!current()) return;
         if (image.status !== 'available') return denied();
         preview.replaceWith(rgbCanvas(image.capture));
        } catch { denied(); }
       };
       row.append(preview);
      } else row.textContent = '현재 열 수 없는 EY';
      body.append(row);
     }
    }).catch(denied);
   }

   if (issuing) {
    const select = root.querySelector('[data-select-invite]');
    select.onclick = () => { input.focus(); input.select(); };
    const revoke = root.querySelector('[data-revoke-invite]');
    if (revoke) revoke.onclick = () => dismiss();
    function clearInvitation() {
     input.value = '';
     select.hidden = true;
     root.querySelector('[data-invite-result]').hidden = true;
    }
    async function checkHosting() {
     try {
      const reply = await call({action:'status'});
      if (!alive()) return;
      if (reply.status !== 'hosting') throw new Error('connection_closed');
      owner.hostComposer.enable(true);
     } catch (error) {
      if (!alive()) return;
      if (error.message !== 'busy') {
       owner.hostComposer.enable(false);
       clearTimeout(expiryTimer);
       clearInvitation();
       status.textContent = relay ? '공용 채팅 연결이 종료되었습니다.' : '로컬 공용 채팅 연결이 종료되었습니다.';
       if (revoke) revoke.hidden = true;
       void view.dispose().catch(() => {});
       return;
      }
     }
     timer = setTimeout(checkHosting, 1500);
    }
    button.onclick = async () => {
     let request = {action:relay ? 'issue-relay' : 'issue'};
     if (lan) {
      const host = root.querySelector('#lan-host-address'), guest = root.querySelector('#lan-guest-address');
      if (!host.reportValidity() || !guest.reportValidity()) return;
      request = {action:'issue-lan', host:host.value.trim(), guest:guest.value.trim()};
     }
     button.disabled = true;
     try {
      const reply = await call(request);
      if (!alive()) return;
      if (reply.status !== 'issued') throw new Error('invitation_unavailable');
      input.value = reply.card;
      root.querySelector('[data-invite-result]').hidden = false;
      select.hidden = false;
      if (revoke) revoke.hidden = false;
      status.textContent = relay ? '초대 텍스트를 시험 참가자에게 직접 전달하세요.' : lan ? '지정한 참가 PC의 사용자에게 초대 텍스트를 직접 전달하세요.' : '게스트 창으로 직접 복사해 전달하세요.';
      if (lan) for (const field of root.querySelectorAll('#lan-host-address,#lan-guest-address')) field.readOnly = true;
      owner.hostComposer = publicComposer({call, alive, label:'호스트 공용 채팅', refresh:refreshHost, attachment, relay});
      owner.hostComposer.enable(true);
      update();
      timer = setTimeout(checkHosting, 1500);
      expiryTimer = setTimeout(() => {
       clearInvitation();
       status.textContent = '초대가 만료되었습니다.';
      }, 300000);
     } catch {
      if (alive()) {
       status.textContent = relay ? '초대를 발급할 수 없습니다. 원본 프로젝트와 시험 중계 설정을 확인하세요.' : lan ? '초대를 발급할 수 없습니다. 프로젝트 소유권과 같은 사설망에 연결된 두 IPv4 주소를 확인하세요.' : '초대를 발급할 수 없습니다. 원본 프로젝트를 만든 호스트만 발급할 수 있습니다.';
       button.disabled = false;
      }
     }
    };
   } else {
    const form = root.querySelector('form');
    const reviewPanel = root.querySelector('[data-lan-review]');
    let review = null;
    function resetReview() {
     if (!confirmTarget) return;
     review = null;
     reviewPanel.hidden = true;
     reviewPanel.replaceChildren();
     button.textContent = '연결 대상 확인';
    }
    if (confirmTarget) input.oninput = resetReview;
    form.onsubmit = async event => {
     event.preventDefault();
     if (button.disabled) return;
     button.disabled = true;
     const name = root.querySelector('#local-guest-name').value;
     const card = input.value.trim();
     if (confirmTarget && !review) {
      try {
       const result = await call({action:relay ? 'inspect-relay' : 'inspect-lan', card});
       if (!alive() || card !== input.value.trim()) return;
       if (result.status !== 'review') throw new Error('invitation_unavailable');
       review = result.review;
       for (const text of [
        relay ? '사전에 설정한 시험 중계 ' + result.relay : '호스트 ' + result.host + ':' + result.port + ' · 내 주소 ' + result.guest,
        '프로젝트 ' + result.title + ' (' + result.project + ')',
        '호스트 인증서 SHA-256 ' + result.fingerprint
       ]) {
        const row = document.createElement('p');
        row.textContent = text;
        reviewPanel.append(row);
       }
       reviewPanel.hidden = false;
       button.textContent = '이 프로젝트에 참가';
       status.textContent = relay ? '초대를 준 호스트와 프로젝트가 맞는지 확인하세요.' : '초대를 준 호스트의 주소와 프로젝트가 맞는지 확인하세요.';
      } catch {
       if (alive()) status.textContent = relay ? '초대와 사전에 설정된 시험 중계가 일치하는지 확인해 주세요.' : '초대 정보 또는 이 PC의 사설망 연결을 확인해 주세요.';
      } finally { if (alive()) button.disabled = false; }
      return;
     }
     const request = confirmTarget ? {action:relay ? 'join-relay' : 'join-lan', name, card, review} : {action:'join', name, card};
     input.value = '';
     resetReview();
     status.textContent = '연결 중…';
     try {
      const reply = await call(request);
      if (!alive()) return;
      if (reply.status !== 'joined') throw new Error('invitation_unavailable');
      form.remove();
      guestComposer = publicComposer({call, alive, label:'참가 프로젝트 공용 채팅', attachment, relay});
      owner.guestComposer = guestComposer;
      messages.after(guestComposer.form);
      void poll();
     } catch {
      if (alive()) {
       status.textContent = '연결할 수 없습니다. 초대가 잘못되었거나 이미 사용·만료되었는지 확인하세요.';
       button.disabled = false;
      }
     } finally { request.card = ''; }
    };
   }

   void mount().then(() => { if (alive()) button.disabled = false; }).catch(() => {
    if (alive()) status.textContent = '로컬 채팅 창을 열 수 없습니다.';
   });
  }, {presentation:'floating'});
 }
 return {
  open, update, hosting:() => !!dialog?.hostComposer,
  startYogiDrag() {
   const composer = dialog?.hostComposer ?? dialog?.guestComposer;
   yogiDrag = composer?.form.isConnected && sealedYogi() ? {owner:dialog, dropped:false} : null;
   return !!yogiDrag;
  },
  endYogiDrag() {
   const dropped = yogiDrag?.dropped;
   yogiDrag = null;
   return dropped;
  }
 };
}
