# V8 명시적 FHD 소프트웨어 출력

원본 v666 ZIP `Confectory-v666/dist/app.js::runPreviewResolutions`의
`FHD · 1920 × 1080`, `FHD · 1080 × 1920`을 기존 Run 개발 메뉴에 연결한다.
현재 고정 잔여 중 실제 소프트웨어 출력의 FHD 누락을 닫는 단위다. 기존 실행창·select 그룹·
크기/개인 등록·전체 화면·개발 표시 배치를 유지한다. QHD/4K/FHD+와 장치/GPU는 별도 잔여다.

프로젝트가 선택 팩 `Confectory.RunSurface::OpenFHD(frameOwner)`를 명시 선택하고
첫 Present 전에 ConfigureSize를 호출한다. RequestedSize의 실제 요청을 읽어 완전한
RGBA8을 제출해야 size ACK가 바뀐다. `examples/fhd-output`은 생성 가능한 재현 예제다.
기존 프로젝트의 C#·입출력/override 계약은 자동 변경하지 않는다. 기존 Open의640축/
262144픽셀 및 OpenHD의1280축/921600픽셀은 동일하며 각 함수 ID/시그니처도 유지한다.
OpenConfigured(string,bool)는 같은 default/HD profile로 전달하며 새 OpenProfile의 알려진
0/1/2 선택만 허용한다. 실행·출력 소유자 연결과 thread·중복 publisher 검증은 그대로다.

FHD는 축1920·2073600픽셀·8294400 RGBA8 bytes다. 창 크기/CSS 확대가 아닌 실제
producer pixels를 읽는다. 기본/HD 프로젝트에 FHD를 묵시적으로 허용하지 않는다.
기존 CurrentUserOnly 인증 FrameControl 채널과 handle/secret/request/frameRuntime을
재사용하며 새 접근권한이나 캡처 socket을 만들지 않는다. 전역 RPC2MiB·관측2MiB·
child packet1400000B·native 읽기300ms 한도를 유지한다.

불변 publisher/revision/크기/전체 SHA/resize/rate/bounds snapshot의 최대11개 조각을 읽는다.
각 raw 조각은786432B이고 마지막 길이는 남은 bytes다. child와 parent/browser는 동일한
전체 metadata·순서·canonical encoding·길이·전체 SHA를 확인한다. index10도 정수 cursor로
처리한다. 지원 cap의 max/maxPixels 쌍이 맞아야 큰 프레임을 받아들이며, 잘못되거나 혼합된
조각은 마지막 신뢰 revision이나 size receipt를 바꾸지 않는다. 이전512/640/HD provider는
각 기존 실제 한도 안에서 읽는다. 큰 transfer는 실행당 최신 하나만 보관하고 마지막 조각·
새 전송·Stop/종료에 해제한다. bytes/secret/미결 전송을 개인 layout·원문·이력에 저장하지 않는다.

브라우저는 전체 SHA가 맞은 완전한 프레임만 교체한다. 닫기/숨김/다른 view·프로젝트·
실행 변경과 늦은 응답/digest는 기존 owner token으로 격리한다. 프레임 진행·Step·실제 작업은
표시나 3D 이동 완료를 기다리지 않는다. 일시정지 중 size 접수는 자동 Resume/Step이 아니며,
명시한 다음 프레임에서만 ACK한다. 읽기는 다음 관측으로 복구하고 command 응답 유실은
기존 명시 확인으로만 회수한다. 늦은 크기·preset 이름/chat 입력과 Review→Confirm·최종 CAS는
변경하지 않는다. 3D 표시 팩·권한 팩 경계도 유지한다.

FHD 개인 preset도 기존 버전1 JSON/ID·영수증·프로젝트별 CAS 안에 저장한다. 새 reader는
작은 기존 목록을 이행 없이 읽지만, 이전1280 한도 reader는 FHD 항목이 있는 전체 목록을
거절할 수 있다. 등록 데이터를 비우거나 자동 축소/이행하지 않는다. 새 reader의 기본/HD
출력에서 FHD preset을 읽어도 실제 적용은 관측된 provider max/maxPixels로 거절한다.
등록 자체는 실행 권한이나 더 큰 출력 허용이 아니다. 새 OpenFHD symbol/조각과 preset은
짝맞춘 provider/native reader/UI가 필요하며 구버전에서 FHD 지원을 주장하지 않는다.

실제 UI·native API·interruption/late-input/cold·LF/CRLF·새 교차 패키지/전체 복원과
최신/롤백 수명 보관을 최종 코드에 맞춰 마감한다. 생성한 테스트 프로젝트만 사용하며
실계정/AI 자격증명·유료호출이나 새로운 환경/기존 자료 삭제는 하지 않는다.
초기 빈 #app 원인은 미확정이다. 실제 Windows/WebView2·모바일·DPI/IME·GPU/모니터 FPS·
물리 오디오·전체 UI·Space/Library 전달은 이번 소프트웨어 자동화/교차 생성과 구분한다.
