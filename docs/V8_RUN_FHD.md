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
child packet1400000B·native 파이프 I/O300ms 한도를 유지한다.

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


첫 최종 실행06d1d5a1은 LF18단계를 통과한 뒤 첫 정상 관측이 `surface-unavailable`을
반환해 중단됐다. 원인은 미확정이며 픽셀 손상/초기 빈 #app와 같은 문제로 단정하지 않는다.
실패 신호 뒤의 읽기 재관측은 기존 계약이다. API 검사 정상 모드의 첫 프레임만20회/50ms
안에서 재관측하고 invoke 수 불변을 확인한다. native300ms/패킷·UI 정책은 바꾸지 않으며
손상 주입 모드의 각 거절/신뢰 revision 검사는 그대로다. 두 번째 실행에서 이전11개 LF
native/projection 통과를 봉인 SHA·동일 제품/C#검사/SDK·dependency/정규화 명령으로 확인해
재사용했으나, 이후 제품 source를 변경했으므로 최종에는 이 재사용을 적용하지 않는다.
실패·개발 검사와 최종 전체 신규 검증을 구분한다.


두 번째 최종 실행bdae2cc8도 정상 초기 재관측20회가 모두 unavailable이어서 중단했다.
진단용 복사본(aee943f0)에서는7/8번째 조각 연결 시 누적302–307ms의 TaskCanceledException을
기록했다. 큰 pixel 노드를 담은 JsonObject를 반복 DeepClone하는 작업을 metadata만 복사하고
하나의 불변 encoded 문자열을 보관하는 방식으로 바꿨다. native 조립/전달 metadata도 pixel을
제외해 복사한다. 처음/마지막/새 snapshot/Close의 소유와 해제 의미는 유지한다.

전체 wire 문자열의 중복 정규식 스캔은 기존 canonical URL roundtrip으로 검증한다.
변환한 bytes의 정확한 길이·원래 URL alphabet/무패딩 표기와 재인코딩 동등성·전체 SHA를
모두 유지한다. 원래 SHA를 가진 `+`·`/` 치환과 공백/Unicode 삽입도 거절하는 native 검사를
추가했다. 큰 noncanonical 입력을 허용하거나 hash 검사를 생략하지 않는다.

300ms는 파이프 I/O cancellation 예산이며 이후 CPU 검증/직렬화까지 포함한 전체 wall-clock
보장은 아니다. 진단의 소수 시간 표본을 고정 지연/FPS나 실제 기기 성능으로 표현하지 않는다.
선행 generic unavailable만으로 모든 실패가 동일 원인임을 단정하지도 않는다. 수정 후 계측
코드를 제거한 제품 경로를 반복 검증하며 최종에서는 제품 source 변경으로 선행11개 native/
projection 재사용을 적용하지 않는다. 실패·진단·최종 새 검증을 구분해 보존한다.

이어 응답 전에 클라이언트를 끊거나 큰 응답의 본문 일부만 읽고 끊는 결정적 native 회귀를
추가했다. 기존 FrameControl은 broken 상태의 `IsConnected == false` 때문에 Disconnect를
건너뛰어 다음 정상 관측도 회복하지 못했다(기존 코드의 phase5 실패). 연결 상태와 무관하게
finally에서 Disconnect를 시도하고 이미 종료된 상태의 예외를 처리한다. 인증·소유권·명령·
ACK·pipe I/O 예산은 바꾸지 않는다. 같은 runtime/frame0/ACK0와 기존 reader를 유지하고
자동 Step/명령 재실행/새 owner 없이 다음 읽기가 회복되는 검사가 수정 후3회 통과했다.
계측을 제거한 제품의 독립 API·UI 반복과 최종 새 source 검증도 별도로 수행한다.
이 확인된 pipe 수명 결함과 초기 빈 #app의 미확정 원인은 구분한다.

최종 c62ef89a 실행은 새 회귀의 긴 pipe 이름과 독립 LF TMPDIR 경로의 합이 Linux domain
socket108자 한도를 넘어 검사 본문 전 실패했다. 검사 이름의 고정 prefix만 짧게 하고 무작위
ID·중단/재접속·owner/ACK 검증과 제품 코드는 그대로 유지한다. 이 fixture 실패도 보존하며
수정한 최종 검사 source에서 LF/CRLF·패키지/복원을 다시 검증한다.
