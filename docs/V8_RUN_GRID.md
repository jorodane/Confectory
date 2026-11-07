# V8 실제 영상 위 디버그 그리드

저장소 v666 ZIP `dist/app.js::setupRunDeveloperMenu`의 ‘그리드 표시’와
`dist/style.css`의 `.run-debug-grid`/`.run-show-grid`를 실제 Run 영상에 연결한다.
원래 색·10% 간격·1 CSS px 선·pointer-events:none 규칙을 그대로 사용한다.
실제 검증된 RGBA 영상이 있는 현재 Run 창에서만 선택할 수 있다. 가로/세로 영상의
contain 영역에 맞추며 letterbox에는 그리지 않는다. 크기 요청이 pending이어도 현재
실제 픽셀 크기로 배치하고, 다음 실제 영상이 확인된 뒤에만 새 비율을 따른다.

이는 비율 참고선이며 프로젝트 요소의 경계/좌표 metadata를 만들지 않는다. ‘요소 경계’는
계속 미지원이고, frame ACK를 FPS로 표시하거나 native/GPU 렌더 지원을 추정하지 않는다.
그리드가 픽셀 buffer에 그려지거나 원본 이미지 SHA를 바꾸지 않는다. toggling/resize는
새 API·실행·Step·크기 요청·저장/Review/Confirm을 호출하지 않는다.

선택은 같은 Run view의 휘발성 표시 상태다. 형제 창에는 적용하지 않으며 숨김/접기에서는
검증된 영상과 그리드를 함께 숨긴다. 새 영상이 없는 idle·지원하지 않는 프로젝트에서는
컨트롤을 비활성화한다. DOM의 disabled를 임의로 제거해도 영상이나 권한이 생기지 않는다.
닫기 거절/영상 오류 동안 선택과 기존 입력은 유지하되 그리드는 표시하지 않는다. 기존
정상 관측으로 영상이 복구되면 같은 view의 선택을 다시 표시한다. actual close는 해당
observer/overlay/handler를 폐기하고 cold는 기존 layout/chat만 복원하며 선택/프로세스/
lease를 재생하지 않는다. 실제 사용자 프로젝트 C#·계약/override·권한·부모/외부 원본·
CAS/Undo·입력 저장과 기존3D/권한 팩 경계는 변경하지 않는다.

HD 이상 출력의 전송/메모리 기반, 진행 중 I/O의 비차단 제공 경계, 요소 경계·GPU/FPS·
장치 backend와 기존 신원/권한·자산·참여자/대화는 별도 고정 잔여다. 실제 Windows
WebView2·모바일 기기/DPI/IME·전체 UI·Space/Library 전달은 이 표시에 의해 완료되지 않는다.

[최종 검증 기록](VALIDATION_V666_RUN_GRID.md)을 따른다.
