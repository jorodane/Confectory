# V8 실제 창 영역에 맞춘 출력

저장소 v666 `dist/app.js::runResolutionOptions`의 ‘창에 맞춤’과 `fitRunPreview`의
`screen.clientWidth/clientHeight` 의미를 기존 Run 메뉴와 opt-in 출력에 연결한다.
CSS 영역의 정수 크기를 그대로 요청한다. DPR·배율을 곱하거나512로 clamp한 결과를
원본 크기로 표시하지 않는다. 현재 provider의240–512px 범위 밖에서는 기존 출력을
유지하고 범위 안내를 표시한다. 큰 출력·고정 대형 해상도는 별도 잔여다.

사용자가 현재 실행에서 명시적으로 선택한 뒤에만 ResizeObserver로 크기를 읽는다.
짧은 변경을 모아 기존 publisher/size sequence/command CAS 경계로 한 번 요청한다.
하나의 미확인 size receipt가 있으면 실제 Present 픽셀/ACK까지 기다리고, 그 뒤의
최신 창 크기만 요청한다. 같은 크기는 반복하지 않는다. 기존 실행당64회 한도와
실제 output min/max, opt-in·소유·scope 검증을 완화하지 않는다.

요청 접수와 실제 적용을 구분한다. paused에서 자동 Resume/Step은 하지 않으며
일반 실행 제어를 잠그지 않는다. 다른 모드를 선택하면 이후 예약만 취소하고 이미
접수한 출력 요청은 보존한다. 늦은 custom/preset 입력을 덮어쓰지 않는다.
전달 결과가 불확실하면 자동 요청을 멈춘다. 기존 상태 재확인은 읽기만 수행하며
재전송하지 않는다. 사용자는 상태 확인 후 창에 맞춤을 명시적으로 다시 선택할 수 있다.

숨김/접기·닫기·소유자 이탈에서는 새 요청을 보내지 않는다. 닫기는 observer/timer를
폐기하고 오래된 handler는 다른 창을 수정하지 못한다. 같은 창의 새 runtime에서는
옛 자동 mode를 재생하지 않으며, cold는 기존 layout/chat만 복원한다. 이 선택은
휘발성 표시 설정이며 C#/프로젝트 원본·override 계약·권한·Review/Confirm·source
CAS/Undo와 분리한다. GPU/FPS·진행 중 IO 관측·물리 장치 지원으로 표현하지 않는다.

[현재 provider 계약](V8_RUN_RESOLUTION.md)과 [검증 기록](VALIDATION_V666_RUN_AUTO.md)을 따른다.

후속: 원본640×360 선택과 축640/총262144픽셀 capability는 [출력 범위 후속](V8_RUN_WIDE.md)에 연결했다. 기존 검증 기록/소유자·실제 ACK 보호와512 provider 지원은 보존한다.
