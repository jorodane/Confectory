# 여러 자료 선택의 제한된 분할 전송

v666 `app.js`의 명시 File·multiple 선택을 기존 자료 추가/카테고리/폴더 드롭 경로에 연결한다. 이번 단위는 **선택 합계 4MiB, 파일당 1MiB, 기존 전체 보관 4MiB/64개**다. 단일 큰 파일, 보관 용량 확대나 새 형식 지원을 뜻하지 않는다. 기존 레이아웃과 메뉴를 재사용한다.

1MiB 이하 선택은 기존 요청을 쓴다. 더 큰 선택은 같은 프로젝트·원래 목적지·명령/항목 ID·revision을 캡처하여 UTF-8 JSON과 SHA256을 만들고 1MiB 이하 청크로 전송한다. 글로벌 RPC 2MiB 한도를 늘리지 않는다. 클라이언트의 취소/실패/응답 유실 재시도는 같은 File 입력·해시·명령을 유지한다. 중복 청크는 같은 위치와 바이트일 때만 인정한다.

EditorHome 세션 하나당 최대 6,000,000 bytes의 휘발 MemoryStream 하나만 허용한다. begin/chunk/commit/cancel의 정확한 필드, 활성 ProjectContext/Identity, 원래 대상 import-many 또는 layout-import-files를 검증한다. 경로나 임의 실행/쓰기 계획은 받지 않는다. SHA 및 엄격한 UTF-8 검증 뒤 기존 provider가 전체 입력을 다시 검증하고 기존 최종 CommitPlan/CAS에 **한 번 원자 저장**한다. 카테고리 배치도 기존 layout+bytes 원자 거래를 유지한다. begin/청크만으로 파일을 만들지 않는다.

성공 응답을 잃었을 때도 동일 완료 버퍼로 기존 durable 영수증을 다시 검증한다. 이미 삭제한 사본을 되살리지 않는다. 완료 버퍼는 같은 6MB 한도 내에 남고 다음 begin에서 교체된다. 실패한 최종 CAS를 새 revision으로 자동 rebase하지 않는다. 명시 취소는 임시 입력만 버리고 확인된 보관본을 삭제하지 않는다. 프로젝트 열기/나가기/세션 종료는 버퍼를 해제한다. cold restart 뒤 미확정 File/버퍼는 사라지고 자동 재실행하지 않는다. bytes/전송 ID는 presentation에 넣거나 별도 디스크에 보관하지 않는다.

기존 `resources.v1.json` 문법·파일당 제한·ID·항목별 영수증·전체 용량은 바뀌지 않는다. 직전 생산 Request 본문으로 정확 4MiB 새 그룹을 load/read하는 호환 검사를 수행한다. 구버전 reader는 읽을 수 있지만 구버전 UI의 선택 한도는 여전히 1MiB다. 공개 함수 시그니처·override·계정 권한·외부 원본과 Review→Confirm은 변경하지 않는다. 개인 파일 대신 생성한 fixture만 쓴다.

검증은 `tools/verify_desktop.py --suite resource-transfer`의 독립 LF/CRLF, 실제 native protocol/UI, 기존 배치·목적지·편집·BMP 회귀, 새 교차패키지와 전체 압축복원을 따른다. 실제 Windows/WebView2/mobile 실행·OS native 파일 드롭·전체 UI 완료와 구분한다. 초기 빈 화면의 원인은 미확정으로 유지한다.

숨겨진 자료 창은 공유 목록의 로딩 상태를 선점하지 않으며, 읽기 중 창 수명이 끝나면 다른 현재 창이 다시 로딩할 수 있도록 상태를 갱신한다. 창별 File 입력은 다른 새 창에 빌려주지 않는다. 닫힌 창의 미완성 native 버퍼는 다른 begin으로 덮어쓰지 않으며 명시 취소 또는 Home/프로젝트 전환·세션 종료 때 해제된다.

[최종 검증과 보관 기록](VALIDATION_V666_RESOURCE_TRANSFER.md).
