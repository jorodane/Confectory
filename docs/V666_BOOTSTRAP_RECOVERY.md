# 작업실 초기 로딩 실패 안내

게시 `6bdd6c3`의 실제 관리형 엔진과 Chromium에서 `v508-views.js` 요청 하나를
차단하면 `#app`은 비어 있고 API mount도 안내도 없었다. 정적 import 실패로
runtime 평가가 시작되지 않는 재현이다. 과거 간헐적 빈 화면에는 요청 기록이
없으므로 **과거 사건의 원인은 여전히 미확정**이다.

`ui/app.js`가 동적 import의 실패를 관측한다. 앱 루트가 완전히 비어 있을 때만
기존 welcome 스타일로 실패 안내와 **다시 불러오기**를 표시한다. 버튼은 문서
전체를 새로고침한다. 부분 runtime을 같은 문서에서 재실행하거나 module map을
우회하지 않는다. 자동 재시도·mount/저장/실행 요청 재전송은 없다.

이미 화면이 만들어졌다면 owner DOM을 그대로 두고 기존 status/toast에 입력을
확인한 뒤 새로고침하라는 안내만 표시한다. 이 경우 새로고침 버튼을 주입하지
않는다. pending import 중 pagehide가 발생하면 늦은 오류를 게시하지 않는다.
정상 시작의 화면·소유자·transport 계약은 그대로다.

오류 원문은 경로·세션 URL을 포함할 수 있어 DOM에 삽입하지 않는다. 고정 console
표식 `editor_bootstrap_failed`와 실제 요청 실패 기록으로 구별한다. 이 오류를
프로젝트 손상·구 reader 타입 오류로 분류하지 않는다. entry `app.js` 자체가
다운로드되지 않는 경우, 끝나지 않는 요청, import 완료 이후의 임의 오류까지
복구하는 watchdog은 아니다.

## 표시 문맥과 고정7/8행 재대조

원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`dist/app.js::renderFunctionSignatureEditor`와 `openOwnFunctionPopover`는
필드 ID와 표시 이름을 분리한다([정보 인자 표시명](V666_ARGUMENT_LABELS.md)).
다음 표는 기존 수용 목록의 실제 조작을 유지한다.

| 사용자 흐름 | 현재 근거와 남은 경계 |
|---|---|
| 정보 입력/out 표시 이름과 native 이름 구분 | 직전 게시의 명시 메뉴·metadata·원자 저장을 유지한다. 이번 단위에서는 정상 편집 회귀를 검사한다. |
| standalone·module/caller/graph의 다른 표시 | 공통 창을 임의 opt-in하거나 계약 이름을 별칭으로 바꾸지 않았다. 각 원래 화면의 표시/계약 갱신 의미를 확인해 연결할 기존 잔여다. 위치별 모든 조합을 새 필수로 만들지 않는다. |
| copy의 원본 계약 갱신과 다른 frame 계약·본문 명시 대응 | [고정7행](V536_ROW7_REMAINING_BOUNDARY.md)의 forwarded/opaque 영향 source closure가 잔여다. ordinary private/frame/wrapper 저장과 등록 receipt는 이미 지원한다. |
| 여러 함수의 계약·본문과 공유 caller를 한 번에 저장 | [고정8행](V536_I5_6_REMAINING.md)의 실제 계약/source closure 범위다. 같은 계약 native 다중 본문·target·ordinary/copy caller 보존은 완료 근거가 있다. 그 밖 실제 계약 변경·forward/opaque 영향 후보를 자동 C# 재작성으로 우회하지 않는다. |

이번에는 재현된 빈 화면의 무안내 실패를 우선 연결했다. 7/8행을 완료로 닫거나
M11/M12/M4를 다시 열지 않는다. 공개 override 변경·donor/부모/외부 쓰기 거절은
보호 정책이며 새 복제/변환 요구로 추가하지 않는다.

## 타입별 Reference의 reader 호환성

[직전 최종 검증](VALIDATION_V666_ARGUMENT_LABELS.md)의 보관된 바이너리 검사에서
pretyped `bf147947…` reader는 `Confectory.Reference.*`를 `TYPE`으로 거절하고
현재 reader는 같은 선언을 읽었다. 문자열 표시 metadata를 읽는 `0437c391…`의
호환성과 이 타입 지원은 서로 다른 근거다. 이번에 구 바이너리를 다시 실행하거나
구 설치본이 새 안내를 표시한다고 주장하지 않는다.

새 Reference가 있는 프로젝트에는 해당 타입/profile을 지원하는 **동일 게시 세대의
reader·authoring·runtime**을 사용한다. 기존 ID·선언·원문을 보존하며 타입명을
일반 값/객체로 치환하거나 profile을 삭제·자동 downgrade하지 않는다. `TYPE`
하나만으로 구 reader라고 단정할 수 없다. 실행한 reader의 실제 게시본과 거절한
선언을 먼저 확인하며 일반 타입 오류를 버전 오류로 숨기지 않는다. 구 reader 자체의
안내 변경은 그 바이너리 재배포가 필요하다. 새 manifest 문법·권한 정책·자동
migration은 도입하지 않는다.

## 검증 경계

실제 관리형 엔진·Chromium에서 명명한 모듈/첫 mount 요청을 차단하거나 보류한다.
API 성공 응답을 만들어내지 않는다. 반복 실패·키보드 재시도·다른 창 입력 보존·
cold·부분 초기화·pagehide의 늦은 실패와 기존 전송 정체/표시명/타입 선택을 검사한다.
최종 LF/CRLF·새 패키지·전체 ZIP 복원은 [검증 기록](VALIDATION_V666_BOOTSTRAP_RECOVERY.md)에
남긴다. 실제 Windows apphost/WebView2·물리 기기·모든 UI 경로의 전수 검증과
구 reader의 실행 지원을 뜻하지 않는다.

이 초기 로딩 실패 단위의 [최종 신규 37단계·재사용0 검증과 보관](VALIDATION_V666_BOOTSTRAP_RECOVERY.md)을 마쳤다.
