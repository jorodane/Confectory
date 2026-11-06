# V8 Run의 명시적 소프트웨어 영상 출력

이 문서는 최초 출력 단위다. 명시적으로 허용한 출력의 직접 크기 변경은
[후속 크기 요청·실제 프레임 확인](V8_RUN_RESOLUTION.md)을 따른다.

저장소 v666 ZIP의 `Confectory-v666/dist/app.js` 내 `openRunViewport`와
`setupRunDeveloperMenu`에 있는 Run 출력 영역을 실제 프로젝트 영상에 연결한다.
원본 viewport·개발 메뉴·창 배치는 유지한다. 원본의 모의 장면/FPS/WebAudio를
실제 실행 결과로 사용하지 않는다.

`Confectory.RunSurface`는 선택적 출력 팩이다. 프로젝트가 직접 소유한 FrameControl
루프의 owner를 `Open(frameOwner)`에 명시하고 렌더 경계에서 `Present`를 호출한다.
자동 Window 선택·캡처나 기존 프로젝트 C# 재작성은 없다. `examples/software-output`은
자체 코드로 실제 64×36 RGBA 프레임을 생성하는 재현 프로젝트다. 기존 프로젝트는
명시적으로 출력 팩을 연결하기 전까지 원래 미지원 표시를 유지한다.

출력 계약은 top-down/straight-alpha/sRGB RGBA8, 가로·세로 각각 1–512, 최대 1MiB다.
canonical base64 입력을 복사·크기 검증·SHA256 검증하여 완전한 최신 프레임 하나만
원자적으로 공개한다. wire는 JSON escaping 증가를 피한 unpadded base64url이다.
제출 revision은 FrameControl의 완료 frame/ACK나 렌더 FPS가 아니다. 실제 해상도만
읽기 전용으로 개발 메뉴에 표시한다. 해상도 변경/preset·GPU/native Window 캡처·
렌더 FPS·오디오는 아직 지원하지 않는다.

출력은 기존 CurrentUserOnly 인증 FrameControl 채널에서만 관측한다. 새 socket이나
환경 권한을 만들지 않는다. 정확한 세션/프로젝트/view/lease/handle과 관측한 frame
runtime을 검증한다. 이미지 읽기는 실행 heartbeat·ACK·Step·실행 권한을 갱신하지
않는다. producer callback은 공개 AttachOutput/DetachOutput 역할로만 연결하며 다른
팩의 private state를 읽지 않는다. 한 frame owner의 두 번째 활성 출력은 거절한다.

부모 reader는 packet 길이·형태·정체성·순서·전체 픽셀 SHA와 retired publisher epoch을
확인하고 공개 필드만 내보낸다. 내부 handle/secret/request/frameRuntime은 영상 DTO에
노출하지 않는다. metadata만 보관하고 원본 픽셀은 부모의 이력에 복제하지 않는다.
잘못된/없는 출력은 unavailable이며 기존 실행 제어와 소스는 유지한다.

WebUI의 bundle-declared `observe`는 별도 읽기 경계다. mutation endpoint와 겹칠 수
없고 view/scope를 전후 재검증하며 입력 8KiB/결과 2MiB의 한계를 갖는다. request ID,
완료 결과 행·재전송 이력을 만들지 않는다. EditorHome은 `runWindowRead`/`runSurface`
두 고정 관측만 선언한다. Start/Stop/Review/Confirm 등의 기존 invoke 경계는 그대로다.
실행 gate가 바쁘면 읽기는 거절 후 다음 관측에서 재시도하며, gate를 잡고 실행을
기다리지 않는다. dispose/Close는 진행 중 관측을 취소·격리한 뒤 자원을 정리한다.

브라우저는 같은 크기/형식/전체 SHA/순서/owner를 다시 확인한 뒤 canvas에 표시한다.
숨김/접기/닫기/소유자 이탈은 진행 중 영상 전달을 취소한다. 늦은 영상·digest 결과는
다른 창/실행에 반영하지 않는다. Stop·오류·미지원은 이전 영상을 지운다. 영상과
cursor/owner는 레이아웃이나 개인 입력에 저장하지 않으며 재시작은 자동 실행하지
않는다. 기존 입력·소유권·권한·Review→Confirm·최종 CAS 계약을 바꾸지 않는다.

3D는 별도 표시 팩이고 이동은 실행 조건이 아니다. 진행 중 IO의 비차단 관측은 별도
V3 잔여다. V4/V5 실제 신원/권한·가시성, V6/V7 소유 자산/미리보기, V9 참여자/대화도
기존 고정 잔여이며 이번 출력 기능과 혼동하지 않는다. 실제 Windows apphost/WebView2,
모바일, GPU/오디오 하드웨어, 전체 UI, Space/Library 전달은 검증 완료가 아니다.
