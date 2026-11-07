# 초기화 중 HTTP 전송 정체 복구

과거 배치 검사에서 reload 후 `#app`이 비어 있었던 실패의 직접 원인은 미확정이다.
그 실패에는 모듈 요청/응답 기록이 없어 특정 transport 결함과 동일하다고 단정하지 않는다.
동일 runtime의 보관 패키지에서 실제 3D reload 24회는 정상 초기화됐으며 증거를 보존했다.

별도 실제 소켓 검사에서는 다른 결함을 재현했다. 클라이언트가 큰 정적 응답을 읽지 않으면
기존 BrowserHost의 동기 쓰기가 단일 host loop를 막아 다른 창도 초기화되지 않았다.
그 연결을 끊으면 오류 응답을 다시 쓰다가 Broken pipe가 host loop 밖으로 전파돼
프로세스가 종료됐다. 부분 POST를 기다리는 동기 입력도 같은 실행 스레드를 점유했다.

입력/출력 소켓 대기만 비동기로 분리한다. `Request`/`Resource`와 실제 소유자 호출은
여전히 host loop 한 스레드에서 직렬로 실행한다. 새 thread에서 원본·초안·권한을 조작하거나
실패한 요청을 재전송하지 않는다. 소켓 실패는 해당 연결만 닫으며 API 결과의 응답 유실은
기존 request ID/수명 복구 계약을 따른다. 이미 실행된 mutation을 취소·재실행하지 않는다.

미완료 transfer는 최대32개, 각 수명은30초다. 초과 연결은 owner 호출 전에503/종료한다.
세션·Origin·Authority·메서드·기존2MiB 본문 제한을 먼저 검사한다. 원래 CSP/캐시/MIME/ETag와
리소스 검증·API envelope·CAS/Review→Confirm·원문 bytes 및 UI 레이아웃은 보존한다.
종료 시 모든 소유 연결을 취소·해제하고 I/O task의 실패를 관측한 뒤 기존 owner를 닫는다.
실행 중인 owner 자체를 중단하거나 그 실행 시간을 제한하는 기능은 아니다.

검사는 실제 HTTP와 exact Serve body의 test-double owner를 쓰는 fault probe, 실제 편집기
엔진/Chromium의 전송 정체 중 reload·입력·프로젝트·cold 복구, 기존 저장/배치 회귀로 나눈다.
Windows 교차 패키지와 전체 ZIP 복원도 Linux 관리형 엔진에서 실행한다.
Windows apphost/WebView2·모바일·전체 UI 및 과거 간헐 실패 원인 전체의 해결을 뜻하지 않는다.
최종 실행·보관 근거는 [검증 기록](VALIDATION_V666_STARTUP_TRANSPORT.md)에 남긴다.
