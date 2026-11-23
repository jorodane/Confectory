export function createLocalChatDevelopment({modal, makeView, scope}) {
 let dialog = null;
 const close = () => dialog?.close();
 function update() {
  if (dialog && dialog.scope !== scope()) close();
 }

 function open(mode) {
  const issuing = mode === 'issue';
  modal(issuing ? '로컬 채팅 초대' : '로컬 초대 참가', issuing
   ? `<p class="small">같은 컴퓨터의 게스트 창에만 이 초대를 전달하세요. 5분 안에 한 번 사용할 수 있습니다. 이 창을 닫으면 초대와 연결이 종료됩니다.</p>
      <div class="field" data-invite-result hidden><label for="local-issued-invite">일회용 초대</label><textarea id="local-issued-invite" rows="3" readonly spellcheck="false" autocomplete="off"></textarea></div>
      <p data-local-chat-status aria-live="polite"></p>
      <div class="actions"><button type="button" data-issue class="primary" disabled>일회용 초대 발급</button><button type="button" data-select-invite hidden>초대 텍스트 선택</button></div>`
   : `<p class="small">이 컴퓨터의 호스트 창에서 직접 전달받은 초대만 입력하세요. 참가 중 받은 공용 채팅을 읽을 수 있습니다.</p>
      <form autocomplete="off"><div class="field"><label for="local-invite">일회용 초대</label><textarea id="local-invite" rows="3" maxlength="4096" required spellcheck="false" autocomplete="off"></textarea></div>
      <div class="field"><label for="local-guest-name">참가 이름</label><input id="local-guest-name" maxlength="64" required autocomplete="off"></div>
      <div class="actions"><button type="submit" class="primary" disabled>참가</button></div></form>
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
   let timer = null;
   root._ownedCleanup = () => {
    if (dialog === owner) dialog = null;
    clearTimeout(timer);
    input.value = '';
    messages?.replaceChildren();
    abort.abort();
    void view.dispose().catch(() => {});
   };

   async function call(input) {
    for (let attempt = 0; alive(); attempt++) {
     try { return await view.transient('localChatDevelopment', input, abort.signal); }
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
     messages.replaceChildren();
     for (const message of reply.messages) {
      const row = document.createElement('div');
      row.className = 'message';
      const name = document.createElement('strong'), text = document.createElement('span');
      name.textContent = message.sender;
      text.textContent = message.text;
      row.append(name, text);
      messages.append(row);
     }
     status.textContent = reply.messages.length ?
      (reply.omitted ? '참가 중 받은 최근 128개 메시지' : '연결됨') : '새 메시지가 없습니다.';
    } catch (error) {
     if (!alive()) return;
     if (error.message !== 'busy') {
      messages.replaceChildren();
      status.textContent = '연결이 종료되었습니다. 창을 닫고 새 초대로 참가하세요.';
      void view.dispose().catch(() => {});
      return;
     }
    }
    timer = setTimeout(poll, 1000);
   }

   if (issuing) {
    const select = root.querySelector('[data-select-invite]');
    select.onclick = () => { input.focus(); input.select(); };
    button.onclick = async () => {
     button.disabled = true;
     try {
      const reply = await call({action:'issue'});
      if (!alive()) return;
      if (reply.status !== 'issued') throw new Error('invitation_unavailable');
      input.value = reply.card;
      root.querySelector('[data-invite-result]').hidden = false;
      select.hidden = false;
      status.textContent = '게스트 창으로 직접 복사해 전달하세요.';
      timer = setTimeout(() => {
       input.value = '';
       select.hidden = true;
       root.querySelector('[data-invite-result]').hidden = true;
       status.textContent = '초대가 만료되었습니다.';
      }, 300000);
     } catch {
      if (alive()) {
       status.textContent = '초대를 발급할 수 없습니다. 원본 프로젝트를 만든 호스트만 발급할 수 있습니다.';
       button.disabled = false;
      }
     }
    };
   } else {
    const form = root.querySelector('form');
    form.onsubmit = async event => {
     event.preventDefault();
     if (button.disabled) return;
     button.disabled = true;
     const name = root.querySelector('#local-guest-name').value;
     const request = {action:'join', name, card:input.value.trim()};
     input.value = '';
     status.textContent = '연결 중…';
     try {
      const reply = await call(request);
      if (!alive()) return;
      if (reply.status !== 'joined') throw new Error('invitation_unavailable');
      form.remove();
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
 return {open, update};
}
