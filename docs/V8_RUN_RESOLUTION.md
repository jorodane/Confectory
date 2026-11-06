# V8 소프트웨어 출력의 명시적 크기 변경

원본 저장소 v666 `dist/app.js::setupRunDeveloperMenu`의 직접 입력·적용 흐름을
실제 선택적 소프트웨어 출력에 연결한다. 원본 form/popover/CSS 배치와 min240 px를
유지하며 현재 RGBA 전송 예산에 맞춰 이 provider의 max는512 px다. 큰 해상도·자동 창
크기·preset 저장/삭제는 이번 지원 경계 밖의 기존 잔여다. 화면만 늘린 결과를 새 렌더
해상도로 표시하지 않는다. GPU/native Window 캡처·FPS·오디오 완료도 뜻하지 않는다.

프로젝트는 별도 RunSurface 팩의 ConfigureSize를 첫 픽셀 전에 명시적으로 한 번 호출하고,
실제 허용된 프레임에서 RequestedSize를 읽어 완전한 픽셀을 제출한다.
`examples/resizable-output`이 재현 예제다. 기존 `software-output`과 사용자 C#은 자동
변환하지 않으며, opt-in하지 않은 출력은 계속 읽기 전용이다. 크기 소비는 owner thread에
속하고 반환 배열은 복사본이다. 초기 크기는 기존1–512 범위이며 사용자 변경은240–512다.

새 public FrameControl 출력 명령 역할은 기존 소유 루프·인증 채널에만 결합한다. 다른 팩의
private state를 읽지 않고 새 socket/권한/환경 grant를 만들지 않는다. 해상도 명령은 원래
실행 frame/ACK·heartbeat와 분리한다. 같은 runtime의 publisher·관측한 size sequence와
고유 command를 검사하고, 하나의 미확인 요청만 허용한다. 같은 command/내용은 중복 적용
하지 않으며 내용 재사용·stale/foreign owner·범위 밖 입력은 거절한다. 실행당64회 예산 뒤에는
명시적인 새 실행이 필요하다. 기존 실행 제어는 이 예산과 독립적이다.

요청 접수는 적용 완료가 아니다. provider는 실제 Present의 크기가 요청과 일치할 때만
size ACK를 갱신한다. native와 브라우저는 이 receipt의 정체성·순서·범위와 실제 SHA 검증
픽셀 크기를 함께 확인한다. 일시정지 중에는 요청을 유지하고 다음 실제 출력을 기다리며,
자동 Resume/Step은 하지 않는다. producer가 요청을 소비하지 않아도 작업을 잠그거나
성공을 추정하지 않는다. 사용자는 기존 제어로 계속/Step/Stop을 선택할 수 있다.

mutating 명령은 기존 invoke 경계로 보내고 관측은 기존 미보관 observe를 사용한다.
전달 실패/응답 유실은 재확인 안내와 입력 보존으로 처리하며 자동 명령 재전송을 하지
않는다. 명시 재확인에서 같은 command receipt를 회수하며, 늦게 작성한 다른 크기는
묵시적으로 적용하지 않는다. 거절된 닫기는 창·실행·새 입력을 보존한다. 새 실행/엔진은
오래된 명령·owner를 재생하지 않는다. 실행 중 폼 초안은 해당 Run 창의 휘발성 UI 상태이며
source/프로젝트 설정·개인 레이아웃에 저장하지 않는다. cold는 기존 layout/chat 입력만
복원한다. Source·override 계약·권한·Review→Confirm·최종 source CAS는 보존한다.

3D는 별도 표시 팩이며 이동은 실행 조건이 아니다. 진행 중 IO의 비차단 제공 경계,
신원/권한·자산·참여자/대화 등 고정 잔여는 이 해상도 연결과 구분한다. 실제 Windows/
모바일·하드웨어·전체 UI·Space/Library 전달은 별도 검증 대상이다.
