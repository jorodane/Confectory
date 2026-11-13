# 정보 소유 영역의 거절된 Undo를 입력 기록과 분리

이전 scalar/native 공동 저장 검증에서 미확정이었던 경계를 게시8b67197a에서 재현했다.
함수 영역 버튼에 포커스가 있고 신뢰된 Ctrl+Z도 그 버튼에 전달됐지만, 앱의 history가 없거나
나중에 생긴 속성 입력과 snapshot이 달라 거절된 키를 소비하지 않았다.
브라우저는 다른 새 scalar 값 입력에 신뢰된 beforeinput/historyUndo를 보내 정확한64비트 기본값을0으로 바꿨다.
버튼 포커스는 유지됐다. 최소 조작과 두 native 편집 후 새 속성 작성의 원래 순서에서 모두 관측했다.
재현은 원문·checkpoint를 바꾸거나 Confirm하지 않았다.

이번 경계는 원래 정보 창의 함수·속성 영역 및 헤더 아이콘의 비텍스트 Undo/Redo다.
이미 처리하던 Ctrl+Z/Ctrl+Y/Ctrl+Shift+Z를 먼저 소비한 뒤, 기존 history 유무·scope/window/schema,
hash/revision·busy·정확한 입력 snapshot 검사를 그대로 적용한다. 함숫값의 기존 Meta 처리도 유지한다.
앱이 거절한 키가 다른 입력의 기본 브라우저 history나 상위 단축키로 흐르지 않게 한다.
기록을 병합하거나 입력이 바뀐 snapshot을 억지로 적용하지 않으며 다른 소유자·권한·저장 기준을 만들지 않는다.
유효한 기존 앱 history의 Undo/Redo와 텍스트·조합 중 키 제외 규칙은 유지한다.

텍스트 자체 Ctrl+Z 및 Ctrl+Shift+Z의 native Undo/Redo를 실제 Chromium으로 확인한다.
기존 전역 Ctrl+Y는 Yogi 열기이므로 텍스트 Ctrl+Y를 native Redo로 재정의하지 않는다.
합성 isComposing Ctrl+Z/Shift+Z 검사는 원래 guard를 확인하며 실제 OS IME나 전역 Yogi의 조합/입력 정책 변경을 뜻하지 않는다.
관측기는 trusted 이벤트의 버블 처리까지 끝난 뒤 defaultPrevented를 읽는다.
원인 증거는 실제 beforeinput/historyUndo·값 변경·버튼 포커스·입력/원문/checkpoint다.

원래 두 native 계약·본문을 먼저 편집하고, scalar 타입·값/표시·삭제·생성까지 나중에 입력한10개 셀을 검사한다.
거절된 함수·속성·아이콘 키는 세 입력 영역과 정확한 버튼 포커스를 유지하고 다른 필드의 native history를 실행하지 않아야 한다.
Save 응답 중 늦은 설명을 입력한 뒤 활성 owner 컨트롤에서 같은 키를 눌러도 captured Save와 새 입력을 보존해야 한다.
기본/독립 창·미저장 cold·취소/반복·실패/재시도·응답 유실·경합·A/B/A,
기존 정상 타입 포커스·함수/헤더 history와 기존 scalar/native 드라이버의 회귀,
LF/CRLF·새 package/전체 복원을 별도 검증한다. 해당 조작을 종료 기준으로 삼고 모든 에디터/문맥 조합으로 늘리지 않는다.

제품은 elements.js·element-functions.js와 두 canonical size/SHA256 pin만 바꾼다.
다른 resource pin과 WebBundle의 JSON 바깥 C# bytes, authored CSS/레이아웃·동작 C#·함수/필드 계약·소유권·권한,
Review/Confirm·최종 CAS 및 serialization/receipt 버전을 유지한다. migration·새 credential/grant·과금은 없다.
정보별 struct·종류 enum·모듈 interface와 sync caller의 명시 async 전환 전 오류 정책을 유지한다.

같은 정보 소유 영역의 이번 native history 유출 원인은 확정하되, 다른 편집기의 전수 history/focus·전역 Ctrl+Y 재설계는 완료로 세지 않는다.
초기 간헐 빈 화면 원인은 여전히 미확정이다. 구 Reference reader 제약과 실제 Windows/WebView2·기기·OS IME·전체 UI 전수 미검증도 구별한다.
고정7/8행의 다른 복합 구조·opaque/private 명시 계획·native callee 및 기존 import/등록 외부 의존성 결합은 같은 원래 잔여다.
M11/M12/M4를 회귀 없이 다시 열지 않으며 main은 사용자 검토/merge에 남긴다.
