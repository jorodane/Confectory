# 고정 8행: 기존 저장소의 값/ref 전달과 공유 호출자

기준은 `eb914a53cfd9a7f6eff443098790b7798eff29a5`의 기존 v536 정보 상세창·
C# 본문 편집·호출 대응 UI와 고정 I5-6 8행이다. 이번 단위는 직접 소유
retained `forwardCallerStorage` code/next 본문의 값↔ref 전달을 같은 후보에
연결한다. 핀 이름 편집을 함께 할 수 있으나 위치별 타입·핀 수·순서·out 역할과
반환을 유지한다. 원래 호출자가 선택한 실제 저장소를 바꾸거나 새 셀/별칭을
만들지 않는다. 오버라이드 원계약 구조 변경은 정상 금지이며 독립 계약 복제는
필수 범위에서 제외한다.

## 원본 조작과 고정 종료 조건

정보 상세창에 없는 순서·역할 제어를 추가하지 않는다. 상세창에서 핀 이름을
편집하고 기존 C# 본문의 밝은 매개변수 영역에서 값/ref를 명시한 뒤 코드 저장,
기존 호출 계약 갱신의 원래 입력·출력 선택을 확인한다. 공개 핀 순서와 C# 내부
형식 매개변수 편집은 별개다. 이번에는 공개 순열 지원을 주장하지 않는다.

- down: 두 `long amount, ref long count`를 값 전달로 바꾼다.
- up: 기존 retained 본문의 `long amount, long count`를 ref 전달로 바꾼다.
  값 본문에도 기존 storage marker/profile이 남는 이전 ref→값 저장 상태를 사용한다.
- mixed: 첫 함수는 값→ref, 둘째는 ref→값이다. 동일 caller의 입력 second는
  이미 소유한 ref 저장소이며 두 호출 모두 그 바인딩을 명시 선택한다.

각 경우 기존 C# 원문·native 이름 amount/count와 caller 실행 경로를 보존한다.
본보기의 공개 이름 left/rightAmount, left/rightCount는 원래 위치별 핀 대응이다.
정확한 값 9223372036854775806, 다른 입력·함수·부모/외부 원본은 보존한다.
기본/독립 460px 화면의 취소·불완전 대응/재진입·Undo/Redo·저장/재시작·
실패/충돌/응답 유실·프로젝트 전환·Review 취소/Confirm으로 닫는다.

## 구현과 보호

`InformationFunctionBatch`의 기존 ref 핀 그룹에서 위치별 타입/수/반환과
명시 핀 대응을 고정하고 null/ref 사이의 역할만 허용한다. out 역할 전환은
이 경계에 포함하지 않는다. 호출자 계획은 원래 핀 이름의 기존 바인딩만
선택해야 하며 연결 해제·새 값·다른 저장소·출력 재선택은 허용하지 않는다.

원래 graph/node/body hash·native/public 선언·본문·출력/graph receipt와 컴파일은
기존 단일 closure가 모두 검증한다. caller typed import도 현재 mode와 함께
변경하지만 별도 native 헤더·본문·다른 import는 보존한다. 모든 원래 선택을
먼저 검증하고 내부 overlay에서 합친 다음 원래 source hash/한 후보 CAS를
사용한다. `MappingFor`·`ProjectOutputs`·`Merge` 및 원래 CAS 본문은 변경하지 않는다.

원래 copy/private/implementationContext/postCall·native target·local/alias·선택
callee 간 의존 guard는 유지한다. 새 UI·레이아웃·계약 ID·권한이나 자동 C#
재작성은 없다. 같은 타입이어도 원래 저장소 재선택을 허용하는 의미는 아니다.

## 조사와 검사 기록

제품 수정 전 down/up/mixed의 단일 후보는 각각 유효하지만 원래 그룹이
거절됨을 재현했다. 초기 up fixture의 낡은 graph 계약 hash/typed import는
기존 검증이 정상 차단했다. 원래 hash와 import를 native scaffold/선언에 맞춰
fixture만 바로잡았으며 실패 로그/ZIP은 보존한다. 저장 후보에서 공개 구현
헤더와 내부 C# 이름을 같게 기대했던 검사도 분리했다. Confirm 뒤 mode가
변한 typed import를 원문 그대로 기대했던 검사는 정확한 import 변화만
대조하도록 바꾸고 나머지 caller 선언 전체 바이트를 확인한다.

C# 매개변수 입력을 보관한 transient bodyDraft가 코드 저장의 Undo-before에
섞여 앞선 상세 편집 Undo의 객체 동일성 검사를 막는 실제 화면 결함도 확인했다.
세 번 Undo 중 두 번째 이후 입력이 그대로 남는 trace를 보존했다. 본문 commit은
그 편집창을 열기 전의 정확한 입력을 Undo 기준으로 사용하도록 좁게 수정했다.
기존 미저장 draft와 다른 함수/창의 입력을 포함한 시작 상태를 보존하며 기존
history·소유권 guard를 완화하지 않는다. 각 코드 저장/호출 확인 Undo 두 번과
완전한 마지막 함수 Undo 세 번, 정확한 Redo를 함께 검사한다.

수정한 리소스의 pinned manifest를 갱신했으며 이전 manifest가 내장된 검사 엔진의
기동 거절도 로그로 보존한다. 현재 소스의 엔진을 새로 빌드하고 기존 리소스
무결성 검사를 그대로 사용한다. JS는 이 Undo 변경만, manifest는 해당 entry만
다르며 다른 리소스·markup·CSS는 같다. 새 레이아웃은 없다.

집중 15흐름·40확인과 영향 8흐름·25확인이 통과했다. 타입/out 역할/순서/수/
반환·본문/receipt/출력 대응 오류, 원래 caller 재선택과 실제 source 경합은
전체 미적용이다. 정방향/역순 후보의 원래 hash·정확한 native/public 서명·전체
caller 헤더/import와 graph·C# 원문·실제 ref 셀을 대조했다.

기본/독립 화면에서 양방향/혼합 전환, 핀 이름을 바꾸지 않는 전달 방식만의 편집,
본문 취소·완전한 Undo/Redo·미저장/저장 재시작·검토 취소/Confirm을 통과했다.
checkpoint 실패/재시도, 저장/조회 응답 유실 뒤 cold receipt 확인과 중복 방지,
실제 peer 경합·프로젝트 분리/오래된 창 제출 차단, 마지막 함수의 불완전 대응
거절·Undo 재시도를 확인했다. 기존 입력/출력 정의·반환·이름·오버라이드 보호도 회귀했다.
추가 UI 1건의 실제 범위는 아래 검사 범위 정정을 참조한다. 기존 whole-body 화면에서는 cold에서 복원한
불완전 원문을 Undo 두 번으로 정확히 복구하고 Redo/저장/Confirm을 확인했다.

새 증거 ZIP38개의 파일 집합·권한·전체 바이트/SHA-256을 재검증했다. 원본/
사용자 자료 삭제나 기존 로그/증거 변환은 없다. 초기 실패와 수정 근거를
[집중·회귀 근거](evidence/v536-information-shared-ref-roles/focused-verification.json)에
구분했으며 현재 미해결 실패는 없다. 독립 checkout·새 교차 패키지는 이후 별도 기록한다.

## 정확한 잔여

8행 전체 완료가 아니다. out 역할·순서·타입/정의/반환의 이 단위 밖 결합,
선택 함수 간 의존, C#/native mixed·중첩/private·whole/postCall·동일계약
copy/상속/등록·소유 정보 속성·scalar 밖 타입의 그룹 연결은 고정 잔여다.
상세창에 없는 새로운 순서 UI를 만들어 닫지 않는다.

7행은 원래 계약 유지 copy의 구체적인 편집/배정 경계, 9행은 정보/참조/외부
함수 타입과 표시명/native 식별자 분리다. I6/B2·A4~A6·M4/M11/M12는 별도다.
Helper 작업 도구는 UI 다음 단계이며 이미지/협의/렌더 새 backend는 범위 밖이다.
실제 Windows/WebView2·모바일 기기 실행과 Library 전달은 교차 패키지/managed/
브라우저 검증과 구분한다.

## 독립 checkout·새 교차 패키지 완료

실행 소스는 `cb4a0cd8ff6a9239268c8560da03105d9c81fd78`다. 기존 독립 checkout을 정상 fast-forward하고
12개 Git blob·기존 LF/CRLF 설정·clean 상태를 확인했다. Native Release 경고/
오류 0, 후보·API·독립 UI·기존 경로·오버라이드 보호 5흐름·13확인이 통과했다.
root solution 및 별도 MCP Release도 경고·오류 0이다.

새 Windows x64 교차 패키지의 manifest 2,343항목/marker 포함
2,344파일, 132,775,377바이트의 집합·전체 해시 및
현재 제품 소스·Native DLL과 7개 Core DLL 일치를 확인했다. manifest SHA-256은
`d4159465bc837f1accf389d266b757e4d7e53592adbb1edded53a494c81ee5dd`, Native DLL SHA-256은
`9d4d5dbdc1098a2539735e89623e6141ed9bb39cf690bc7a150858c84525f582`이다.

SDK 없는 새 소유 runtime에서 무관한 cwd의 Linux managed 엔진 웹 기동,
74리소스·synthetic profile/명시 override 보존·변조/DLL 누락 거절과 패키지
backend 후보 4확인이 통과했다. 검사 6단계를 순차 수행했으며 OOM/oom_kill은 0이다.
실제 Windows apphost/WebView2·모바일 기기 실행 및 Library 전달과 구별한다.

새 증거 ZIP 45개의 파일 집합·권한·전체 바이트·해시를 재검증하고 전체 manifest와
fixture 증거를 보존한 뒤 이번 소유 임시 RAM 패키지만 종료 cleanup했다.
기존 자료 삭제·압축 변환이나 새 영구 배포 파일 보관·전달은 하지 않았다.
패키지 단계 최저 디스크 여유는 1,914,765,312바이트다. 후속 결과 문서 커밋은
실행 소스를 바꾸지 않는다.
[checkout·패키지 근거](evidence/v536-information-shared-ref-roles/package-clean-verification.json)에 단계·소스·해시·검증 한계를 기록했다.

## 후속 감사: UI 회귀 플래그 정정

다음 ref→out 단위에서 검사 래퍼의 환경 초기화 순서를 감사했다. 이 문서의
`impact-ref-ui` 1건은 플래그 재설정 때문에 실제로 ref 이름 편집 대신 값/ref
역할 UI를 실행했다. 당시 ZIP의 확정 선언은 leftCount가 값 전달인 것을 확인했다.
원래 8흐름/25확인은 실제 실행 수지만 해당 1건을 ref 이름 UI 근거로 사용하지
않는다. 별도 native ref 이름 검사는 올바르게 실행됐으며 기존 증거는 보존한다.

현재 동일한 JS/레이아웃에서 플래그를 먼저 초기화하고 종류별 값을 설정한 뒤
실제 이름 UI를 재검증했고 취소·Undo/Redo·cold·저장·Review/Confirm을 통과했다. 실행 환경 플래그와 원래 ZIP SHA는
[후속 검증](VALIDATION_V536_INFORMATION_SHARED_REF_OUT.md)과 그 집중/회귀
JSON에 기록한다. 이 정정은 제품 검증을 완화하거나 과거 증거를 교체하지 않는다.
