# 작업실 초기 로딩 실패 안내 검증

제품 동결 `67663dc8f36060cb1f424f5ae5e2f7b7f7705db9`의 [한정 지원 경계](V666_BOOTSTRAP_RECOVERY.md)를 **신규 37단계·재사용0·실패0**으로 검증했다.
독립 Git 객체/no-hardlinks·HOME/NuGet·빈 엔진 cache에서 LF/CRLF Release/MCP·실제 엔진,
새 Windows 교차 패키지의 구조·무결성 및 전체 ZIP 복원을 실행했다. 과거 검사 코드의
새 실행과 결과 재사용을 구분하며 개발 실행은 최종 수에 합산하지 않는다.

- 실제 Chromium에서 의존 module 하나만 차단하면 실패 안내가 보인다. API mount나 source
  mutation 없이 다른 창의 입력·DOM을 보존한다. 자동 재시도는 없고 키보드/버튼 재시도는
  전체 새 문서 하나를 연다. 반복 실패·닫기/재진입·복구 후 단일 mount와 저장된 private
  입력 복원, 새 실제 엔진의 cold 재시작을 확인했다.
- 첫 mount 요청을 차단한 부분 초기화는 기존 welcome owner DOM을 유지하며 status/toast에
  안내한다. 앱 교체·초기화·자동 mount 재전송이나 새로고침 버튼 주입은 없다. pending
  module 중 pagehide 뒤의 늦은 실패가 다음 문서에 게시되지 않는다. 위 네 모드를 LF/CRLF와
  패키지/복원에 나눠 총12개 실제 UI 실행으로 확인했다. API 성공 응답은 합성하지 않았다.
- 기존 느린 이미지 소켓·부분 POST 중 실제3D reload는 LF8회/CRLF4회 모두 초기화됐다.
  연결 단절·child/root·프로젝트 A/B/A·cold와 원문 보존을 확인했다. 기존 인자 표시명
  정상 Save/Review/Confirm·Undo/cold 및 타입별 참조 선택은 최종 코드로 새로 회귀 검사했다.
  이 두 회귀가 과거 모든 CAS·타입·저장 문맥을 전수 재실행했다는 뜻은 아니다.

개발 11단계·실패0에는 게시본 재현과 네 수정 UI 검사가 포함된다.
기존 static import에서 module 하나 실패 시 빈 앱·안내 없음·API 요청 없음이 확인됐다.
첫 최종 시도는9개 선행 단계를 통과한 뒤 새 UI fixture가 아직 등록되지 않은 flush hook을
호출해 실패했다. 화면은 첫 state callback에서 그려지고 해당 hook은 top-level 초기화의
마지막에 등록된다. hook 등록을 실제로 기다리도록 fixture만 고쳤고 app.js·bundle·runtime은
26391aaf와 동일하다. 첫 record `/workspace/artifacts/v536-verification-managed/runs/c023f023cf954622959f658067234a48.json`의 전체 결과와 evidence SHA256
`a5a8defdfb3053ff0acbabf9b21618a1163d5a3272604d382a124805761d0f66`를 보존했다. 그9개 단계를 재사용하지 않고 최종 코드에서 새로 실행했다.
두 번째 시도는 LF 전체와 CRLF normal/lifecycle/partial까지26단계를 통과한 뒤 retired
준비의 문자열 평가가 기존 CSP에 거절됐다. 두 predicate를 함수 형태로 명시하고 CSP나
제품 코드는 그대로 유지했다. 두 번째 record `/workspace/artifacts/v536-verification-managed/runs/216d6ec71a0a418db3749892813de66d.json` · evidence SHA256
`612287ca0d805f39bcee0fa1762acd89c32784b8e404ddff43e0d209b47ed73d`도 보존했으며26개 통과 결과를 재사용 수에 넣지 않고 최종
검사를 새로 실행했다. 두 실패 모두 검사 준비 코드의 실패다.
과거 간헐적 빈 화면에는 해당 요청 증거가 없어 그 원인은 여전히 미확정이다.
entry app.js 자체 로딩 실패·끝나지 않는 요청·import 완료 후 임의 오류는 이번 복구 밖이다.
검증 중 읽기 명령2회가 exec-server transport disconnected로 거절됐다. 이후 실제 읽기로
같은 checkout/HEAD와 계속 진행한 동일 검증 record를 확인했으며 환경·검사를 재생성하지 않았다.

구 reader 비교는 [직전 검증](VALIDATION_V666_ARGUMENT_LABELS.md)의 보관 근거를 참고했으며
이번 최종 실행 수나 재사용 단계 수에 포함하지 않았다. pretyped reader의 Reference `TYPE`
거절을 데이터 손상으로 바꾸어 표현하지 않고 실제 reader 세대/선언을 확인한다. 구 reader
자체가 새 안내를 표시하거나 자동 migration/downgrade를 제공한다고 주장하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 67663dc8f36060cb1f424f5ae5e2f7b7f7705db9 | 15b7f952c245e8df261d6b842804ba48ccb89497fb145f0a94dfa025e0e60a67 | 54066392 |
| rollback | bb2437841e507c93fc5637a281e92e935977f790 | f5a5eeb1b586ede50451faa4c3c60f839f73c9105787777fc53899c5a1670fc4 | 54065759 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/553e8e89148e4dc0af472e45f48b8b67.json` · evidence SHA256 `0e71e1fba2dfcefd7696f068b5dcc18aef1ee65314fa1bd0079a759c94759be2`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/bfe3ab93ff5c4cdcb17bb261e8dd0bb0.json` · evidence SHA256 `03ed8514628835fb63595a3ade0bc2631718175de8de408e17ee248125983be0`.
개발/최종 evidence와 두 관리 package를 SHA로 재확인했다. 기존 latest/정상 rollback2세대
교대와 이번 소유 RAM 임시물 정리만 적용했다. 과거 비관리 자료·원래 checkout/main을
보존했으며 교대된 세 번째 관리 package 전체도 보관한다고 주장하지 않는다.
완료 시 여유 25370447872bytes (23.63GiB)다.

다른 표시 문맥·고정7/8행의 실제 계약/source closure는 [유한 잔여](V666_BOOTSTRAP_RECOVERY.md)에
유지한다. M11/M12/M4는 다시 열지 않는다. 기존 데이터·계약·권한·Review/Confirm·최종 CAS는
변경하지 않았다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio와 전체 UI는 미검증이다.
라이브 AI·새 자격증명/외부 grant/과금·main 변경은 없다.
