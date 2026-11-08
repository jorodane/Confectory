# V8 명시적 HD 소프트웨어 출력

기준은 저장소 v666 ZIP의 `dist/app.js::runPreviewResolutions`에 있는
`HD · 1280 × 720`, `HD · 720 × 1280`, `4:3 · 1024 × 768`이다.
기존 실행창·해상도 select/그룹·직접 입력·개인 등록·개발 표시 배치는 유지한다.
CSS로 늘린 화면이나 원본 모의 장면을 실제 고해상도 출력으로 표시하지 않는다.

프로젝트가 `Confectory.RunSurface::OpenHD(frameOwner)`를 명시적으로 선택하고 첫 Present
전에 ConfigureSize를 호출한다. 실제 허용 프레임에서 RequestedSize를 읽어 완전한 RGBA8을
Present한다. `examples/hd-output`이 재현 예제다. 기존 Open은 축640/262144픽셀/1MiB의
동일한 기본값과 public signature를 유지한다. 기존 프로젝트 C#은 자동으로 바꾸지 않는다.
HD profile은 축1280/921600픽셀/3,686,400B이며 FHD/QHD/4K나 GPU/native 캡처 지원은 아니다.
HD는 이 단위에서 명시적 ConfigureSize/RequestedSize 흐름으로만 opt-in한다.

기존 CurrentUserOnly/handle/secret/request/frameRuntime 인증 채널을 사용한다. 전역
RPC2MiB·관측 입력8KiB/결과2MiB·child packet1,400,000B 한도를 늘리지 않는다.
1MiB를 넘는 프레임은 불변 publisher/revision/크기/SHA/resize/rate/bounds snapshot의
최대5개 조각으로 읽는다. child는 같은 snapshot을 제공하고 native는 하나의300ms 읽기
deadline 안에서 전체를 모아 길이·canonical base64·전체 SHA·정체성을 검증한다.
잘못되거나 섞인 조각은 trusted revision/resize receipt를 대체하지 않는다.

browser에는 검증된 ephemeral snapshot을 최대786432B 조각으로 관측한다.
처음의 snapshot과 이어지는 `slice:`는 같은 세션/프로젝트/view/lease/handle을 매번 확인한다.
browser도 순서·전체 metadata·길이·전체 SHA 확인 뒤에만 canvas를 교체한다. 부모는 실행당
최신 전송 한 개만 보관하며 마지막 조각·새 전송·Stop·자연 종료 때 해제한다.
이 배열은 소스/개인 layout/실행 이력에 저장하지 않는다. abandon된 전송은 실행 수명 안의
한 개 cache 한도이며, 새 실행/다른 view/종료 뒤에 재사용할 수 없다.

모든 조각은 읽기 전용 observe이며 명령 결과/재전송 이력·frame heartbeat/ACK를 만들지 않는다.
프레임 진행·Step·실제 작업은 browser의 표시 완료를 기다리지 않는다. 크기 요청 접수와 실제
Present의 size ACK는 구별하며 일시정지 중 자동 Resume/Step은 없다. 관측 실패는 다음 읽기로
회복하고 명령 응답 유실은 기존 명시 재확인으로만 회수한다. 늦은 크기/이름/chat 입력과
닫기/프로젝트 전환/cold 경계 및 기존 Review→Confirm/source CAS는 유지한다.

짝맞춘 새 provider/native reader/UI가 필요하다. 이전 binary는 새 OpenHD 심볼이나1280
capability/조각을 거절할 수 있다. 새 reader는512/640 provider를 그대로 읽으며 그 출력에는
이전 실제 axis/area 한도를 적용한다. 큰 개인 preset은 기존 JSON 구조/ID/receipt/CAS 안에
저장하지만 이전640 전용 reader가 전체 목록을 읽지 못할 수 있다. 기존 unavailable/입력 보존
보호를 유지하고 preset을 삭제·축소하거나 자동 migration하지 않는다. 등록이 출력 권한을
부여하지 않으며 실제 적용은 관측한 provider의 max/maxPixels로 다시 제한한다.

3D는 별도 표시 팩, 권한은 별도 팩이며 이동/표시는 실행 조건이 아니다. native 권한·원본·
공개/override 계약·C# 의미를 바꾸지 않는다. 큰 자료/실제 신원 backend/더 큰 GPU·물리 출력과
장치 검증은 기존 잔여다. 초기 빈 #app 원인은 미확정이며 실제 Windows/WebView2/모바일/
전체 UI/Space 전달은 교차 패키지나 Linux Chromium 검증과 구분한다.

[최종 신규/재사용·패키지/복원·수명·공간 기록](VALIDATION_V666_RUN_HD.md).
