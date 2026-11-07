# Run 소프트웨어 출력 FPS

원본 v666 `dist/app.js::openRunViewport/setupRunDeveloperMenu`의 FPS·해상도 진단을
실제 명시 출력에 연결한다. 프로토타입의 requestAnimationFrame 기반30fps 연출은 사용하지 않는다.
이번 값은 성공한 `Confectory.RunSurface::Present`의 발행 빈도다. GPU/모니터 표시·브라우저
canvas 재그리기 FPS나 FrameControl 완료/ACK 횟수를 계측한 값이 아니다. 생산자가 보고한 성공 발행 수이며
다른 출력 구현의 내부 렌더링 비용이나 사용자 코드의 계측 정확성을 증명하지 않는다.

생산자의 monotonic Stopwatch와100ms 버킷10개만 사용한다. 최근900–999ms의 실제 구간에
속하는 성공 발행 수를 세고 첫1초는 집계 중으로 표시한다. 잘못된 Present·조회·제어 명령은
수를 늘리지 않는다. 정지하면 실제 최근 구간에서0으로 줄고, 새 publisher는 새 계측을 시작한다.
새 timer/프레임 실행/가상 진행이나 화면 표시를 위한 실행 대기를 추가하지 않는다.

기존 CurrentUserOnly FrameControl 채널·정확한 session/project/view/lease/handle과 원래
publisher/픽셀 SHA/순서 검증을 그대로 사용한다. 선택 metadata는 basis·관측 순서·집계 준비·
성공 수·실제 구간 길이뿐이다. native/browser는 canonical Int64·유효 구간·발행 revision
이하의 수·관측 순서와 같은 관측의 불변성을 대조한다. 추가 private 필드는 내보내지 않는다.
같은 publisher의 계측 소실/준비 역행·변조는 거절하며 유효 native 기준 관측을 덮지 않는다.
이전 계측 없는 producer도 원래 영상을 읽으며 FPS 미지원으로 표시한다.

진단만 달라진 unchanged 프레임은 같은 검증된 pixels를 재사용하고 canvas에 다시 그리지
않는다. 숨김/닫기/교체/소유자 이탈·오류는 기존 관측 수명에 따라 샘플을 폐기한다. 늦은 응답이
새 창/실행을 바꾸지 않고, cold는 개인 창/입력만 복원한다. 계측과 픽셀을 레이아웃/이력에
복제하지 않는다. 읽기는 heartbeat·ACK·자동 Step/Resume이나 작업 권한을 갱신하지 않는다.

공개 Present/Invoke·override 계약·C# 원문과 권한, 원자 저장/CAS/Review→Confirm 및
기존640축/262144픽셀·1MiB 프레임/packet 예산은 보존한다. 프로젝트는 기존처럼 출력 팩을
명시 연결해야 하며 자동 Window 캡처나 기존 사용자 C# 재작성은 없다. HD 이상·GPU/FPS·
요소 경계·물리 오디오/실제 Windows·모바일·전체 UI는 별도 잔여다. 초기화 간헐 빈 화면의
직접 원인은 미확정이며 이 계측으로 해결됐다고 보지 않는다.

[검증 기록](VALIDATION_V666_RUN_RATE.md) · [고정 제품 delta](v666-run-rate-delta.json).
