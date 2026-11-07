# V8 실제 소프트웨어 출력의 요소 경계

원본 v666 `dist/app.js`의 `setupRunDeveloperMenu`/`data-run-debug="bounds"`와
`dist/style.css`의 `.run-show-bounds .run-scene>:is(.run-entity,strong,small)` 점선 accent를
실제 RGBA8 출력에 연결한다. 원본 모의 scene의 라벨을 실제 요소로 간주하지 않는다.

## 현재 지원

명시 RunSurface producer는 기존 `Present(owner,width,height,rgba)` 대신 선택적으로
`PresentBounds(owner,width,height,rgba,int[] rectangles)`를 호출할 수 있다. 기존 함수·출력
계약은 유지한다. 배열은 실제 프레임 픽셀 좌표의 `[x,y,width,height]`이며 최대 16개다.
좌표는 비음수, 크기는 양수이고 프레임 안에 있어야 한다. producer가 가시 영역으로
자른 경계를 제공한다. 렌더러의 자동 요소 탐지나 보안 검증 증명이 아니다.

배열 크기를 먼저 제한하고 복사·검증한 뒤 픽셀과 경계를 한 프레임 revision으로 발행한다.
실패 시 기존 픽셀·경계·revision·크기 ACK를 보존한다. 빈 배열은 유효한 빈 scene이다.
새 프레임의 기존 Present는 경계를 생략할 수 있다. 같은 publisher/revision에서 경계를
변경·추가·삭제하면 native와 browser가 거절한다. 알 수 없는 private metadata는 노출하지 않는다.

기존 동일 사용자 FrameControl pipe, Run 소유 handle/lease/view, stale/retired publisher와
픽셀 SHA 검증을 재사용한다. 축 640·총 262144픽셀·1MiB RGBA·기존 packet 예산은 유지한다.
경계 관측/체크박스는 실행·Step·heartbeat·ACK·권한 부여를 하지 않는다.

원본 개발 메뉴의 ‘요소 경계 표시’는 유효한 경계가 있는 현재 출력에서만 켤 수 있다.
영상의 contain 영역과 같은 배율/letterbox에 점선으로 표시하고 마우스 입력을 가로채지 않는다.
창 숨김·닫기·실패·publisher 변경·재시작에서는 이전 경계를 제거한다. 선택은 창별 일시 상태이며
프로젝트 source나 개인 presentation에 저장하지 않는다. 늦은 응답은 다른 창에 적용하지 않는다.
`examples/bounds-output`은 실제 사각형 픽셀과 같은 좌표를 발행하는 생성 테스트 예제다.

## 남은 경계

기존 C#·공개 override 계약·Review→Confirm·CAS 저장 경로는 바꾸지 않는다.
GPU/native Window 캡처·자동 scene 탐지·HD 이상·물리 화면/오디오·전체 UI/실제 Windows·모바일은
이번 완료 범위가 아니다. 초기화 간헐 빈 화면의 원인은 계속 미확정으로 유지한다.
검증 수치와 새 패키지/전체 복원·임시물/최신·롤백 보관은 별도 최종 검증 문서에 기록한다.
