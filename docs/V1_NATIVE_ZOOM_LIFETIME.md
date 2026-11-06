# V1 일반 Blueprint의 읽기·배율 수명

고정 v666의 기존 Blueprint 확대 흐름과 native 일반 Blueprint의 기존 화면 진입을
연결한다. 직렬 작성기(`feature-authoring.js`)·Workspace의 마감과 구분한다. 새 화면이나
레이아웃·확대 규칙·원문 변환·실행 기능을 추가하지 않는다.

게시 `afeaf23`와 제품 코드가 같은 최신 실행 패키지 `5304b65`에서 두 결함을 확인했다.
일반 Blueprint 진입의 읽기가 Browser 갱신과 겹치면 `stale_revision`으로 끝났고, 읽기
실패 증거를 보존했다. 별도 실제 엔진 재현에서는 닫힌 팝오버의 slider callback이
재개방한 viewport의 500%를 200%로 바꿨다. 콜백 지연은 검사에서 직접 전달했다.

- `blueprint.js`의 명시적 열기만 현재 프로젝트를 확인하고 view를 갱신해 `list/read`를
  관측한다. 실제 `stale_revision` 거절에 한해 최대 세 번 읽는다. 다른 오류·scope 변경은
  자동 재시도하지 않으며 어떤 변경/저장/확정/실행 요청도 재생하지 않는다.
- `blueprint-viewport.js`는 기존 `active()`를 zoom/전체 보기/팝오버 열기에 적용한다.
  입력·slider·preset·fit·Escape는 정확한 현재 팝오버인지 확인한다. 숨김·폐기·동일 DOM
  remount·stale 소유 문맥의 callback은 배율/카메라/저장을 바꾸거나 팝오버를 열지 않는다.
- 기존 3.125–500%·포인터/중심 기준·wheel·카메라·fit 계산·markup·CSS는 보존한다.
  소스/C#·계약/ID/핀/연결·부모/외부 원본·권한·Review→Confirm·최종 CAS·Undo는
  바꾸지 않는다. [정확한 허용 delta](v666-native-zoom-lifetime-delta.json)로 검사한다.

최종 검증은 `tools/verify_desktop.py --suite native-zoom-lifetime`를 사용한다. 실제
생성 fixture/managed engine/Chromium의 stale 관측 재시도·한도/명시 재시도·정상 열기,
팝오버 반복/취소/늦은 입력·cold·창 종료와 개인 입력/물리 원본 보존을 확인한다.
동일 DOM의 폐기/remount와 소유권 변경은 통제된 실제 viewport 모듈 검사로 구분한다.
기존 Workspace 프로젝트 왕복도 영향 회귀로 실행한다. LF/CRLF 독립 빌드·새 교차
패키지·전체 복원과 성공/실패/예외 수명관리를 완료한 결과만 마감 기록에 반영한다.

이 단위는 일반 Blueprint 표시 수명이다. 독립 정보 창의 모든 확대 문맥·DPI/IME,
실제 Windows/WebView2·모바일 기기·전체 UI·Library/Space 전달은 별도 미검증이다.
V3–V7 실제 상태/권한/자산 backend와 V8의 실제 surface/audio provider 및 V9 신원/
가시성 adapter 잔여를 유지한다. M11/M12/M4의 실행 의미를 다시 확장하지 않는다.

[최종 검증·보관 기록](VALIDATION_V666_NATIVE_ZOOM_LIFETIME.md): 31단계, 신규 31·재사용 0.
