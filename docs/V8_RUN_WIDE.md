# V8 640×360 소프트웨어 출력

원본 v666 `dist/app.js::runPreviewResolutions`의 ‘PC · 가로 / 640 × 360’을
실제 opt-in Run 출력에 연결한다. 현재 backend는 축별1–640 및 총262,144픽셀,
실제1MiB RGBA8 바이트/기존 base64·pipe packet 예산을 유지한다. 640×360은921,600bytes다.
512×512도 그대로 허용하지만640×410/640×640은 같은 픽셀 예산을 넘어 거절한다.
HD/FHD/4K/모든 원본 해상도를 지원한다는 뜻은 아니다.

새 provider의 size receipt는 기존 min240/max에 max640/maxPixels262144를 선언한다.
native와 browser는 실제 픽셀·요청의 축/면적과 immutable capability를 확인한다.
같은 publisher에서 max/maxPixels의 변경·소실·임의 확대는 거절하고 기존 유효 관측을
대체하지 않는다. 새 UI/native reader는 이전512 provider를 읽고 그 출력에는512 한도를
적용한다. 640 provider/UI/reader는 짝맞춘 버전이어야 한다. 이전 롤백/혼합 binary의 새
capability 지원은 보장하지 않으며, 구버전은 새 자료를 거절할 수 있다.

원래 선택 메뉴에서640×360을 고르면 기존 소유자/publisher/size sequence/command CAS를
사용한다. 실제 Present 픽셀과 size ACK 전에는 완료를 표시하지 않는다. paused에서
자동 Step/Resume은 없다. 기존64회 예산·소유/권한·원본 Review/Confirm/source CAS를 유지한다.
서버/클라이언트/폼 모두 축 한도와 총 픽셀 수를 확인한다. 거절된 입력은 지우지 않는다.
직접 입력·개인 등록도 같은 hard ceiling을 따르고, 선택 가능한 항목은 현재 관측 provider의
허용 범위와 대조한다. 자동 맞춤도 실제 client 영역에 같은 축/면적 한도를 적용하며
clamp/화면 배율을 실제 렌더 크기로 주장하지 않는다.

기존 개인 등록 파일의 구조/ID/receipt/CAS는 보존한다. 새640 등록은 과거512 전용
binary가 목록 전체를 읽지 못할 수 있으며, 그 경우 기존 unavailable/입력 보존 보호를 따른다.
자동 다운스케일·삭제·이름/값 변환이나 선택적 migration은 추가하지 않는다.

이 변경은 원본 C#·공개 Invoke/override 계약·scope/권한·frame heartbeat/ACK·3D 실행
조건을 바꾸지 않는다. 기존 FrameControl 전송/관측 예산과 인증 채널을 사용한다.
전달 실패/응답 유실은 읽기 재확인으로만 회수하고 늦은 입력·닫기·재시작 보호를 유지한다.
진행 중 I/O·GPU/FPS·큰 출력/물리 장치 및 전체 UI 검증은 별도 고정 잔여다.

[최종 검증 기록](VALIDATION_V666_RUN_WIDE.md)을 따른다.
