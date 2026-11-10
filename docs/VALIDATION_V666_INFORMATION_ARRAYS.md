# 정보 구조체 배열 필드 검증

[지원 경계](V666_INFORMATION_ARRAYS.md)의 제품·테스트를
`b775adde470c9ce2aac079362ab0a07d878264b2`에서 고정했다. 최종 **46단계 신규 실행·재사용0·실패0**을 통과했다.
후속 결과 문서 커밋은 제품·테스트·실행 코드를 바꾸지 않는다. 실제 Windows/모바일·전체
UI 수용으로 합산하지 않는다.

개발 재현에서는 게시본 `acbdc08fa7139d45dc51b06b2a39b4e11b8b5ad2`의 실제 생성기가
multiple 필드 C# ABI를 `INFORMATION_CLR_FIELD`로 거절하고 원본을 보존함을 확인했다.
같은 게시본에서 얻은 primitive·compound·enum·기본/nominal 동기 module의 source/hash/profile
5개를 golden 입력으로 보관한다. 최종 검사 때 새로 생성한 descriptor와 비교하며,
golden 입력 사용은 과거 실행 증거의 재사용이 아니다.

실제 native 실행은 long/bool/string·중첩 struct·enum 배열, exact64 숫자, Unicode/null,
기본 배열 null 및 일반 C# struct/배열 대입 규칙을 확인한다. 이미 지원하는 동기 module
interface 구현은 fixture의 명시 C# Reflection.Emit 객체다. provider 선택이나 제품의
새 live-reference 객체 생성/접근 정책으로 표현하지 않는다. 배열 원소 shape 변경의 key
무효화, 배열→scalar와 다른 nominal 원소의 C# 불일치, 미선언 dependency, reference/함수
필드·구조 순환 거절과 정확한 복원도 실제 compiler로 검사한다.

UI는 원래460px 정보 본문 편집기와 실제 엔진·checkpoint·compiler를 사용한다. 본문 편집,
취소·Undo/Redo·미저장 cold 복원, 원자 Save, 중복 Save 금지, 저장 실패, apply/receipt 응답
유실과 중복 apply 없는 cold 정산, 응답 중 늦은 이름의 후속 Save를 검사한다. schema 원소
변경 전 Save 거절/Review 뒤 최종 CAS 거절, 등록 read guard 누락·추가·native proof 변조의
cold Review 거절 및 등록 원문 변경 후 Confirm 거절을 구분한다. 실패와 peer 원문을
보존하고 정확한 원문 복원·새 Review 후 실제 결과31을 실행한다.

최종 검증은 독립 LF/CRLF checkout·공개 SDK/NuGet seed·빈 engine cache에서 실행하고,
기존 scalar 정보/compound native/module API·module UI·선언/헤더 receipt 회귀를 포함한다.
새 Windows 교차패키지의 구조·무결성, 패키지 안 engine의 실제 Linux/.NET UI 실행,
전체 ZIP 복원 뒤 동일 계약·수명 흐름과 package 실패 수명관리를 별도로 확인한다.
main·기존 checkout·latest/rollback·증거 및 cleanup 한도를 유지한다.

최종 실행은 `tools/verify_desktop.py --suite information-arrays`이며 공개 SDK
`/workspace/toolchains/dotnet-10.0.401`과 기존 NuGet seed를 사용했다. 살아 있는 AI 계정·
유료 호출·새 접근 권한은 사용하지 않았다.

| 최종 범위 | 신규 실행 | 동등 재사용 |
| --- | ---: | ---: |
| LF 독립 checkout·빌드·native/API/UI·기존 scalar/compound/module 회귀 | 17 | 0 |
| CRLF 독립 checkout·빌드·native/API/UI·기존 scalar/module 회귀 | 16 | 0 |
| 관리 IPC 수명 | 1 | 0 |
| 새 교차패키지·구조/무결성·패키지 UI·전체 ZIP 복원·native/API/수명·실패 정리 | 12 | 0 |

native probe의13개 내부 확인과 각 UI/API의 내부 체크는 별도 단계로 부풀리지 않는다.
LF/CRLF Release 빌드는 경고·오류0이다. 기존 테스트 코드를 실행한 것과 과거 실행 증거
재사용을 구분하며, 이 최종 실행에는 과거 통과 증거를 가져오지 않았다.

개발 기록은 23회 실행 중 6회 실패를 그대로 보관했다.
제품 실패는 본문/native 타입 영수증의 등록 읽기 범위 불일치와 같은 계약의 이름 후속
Save가 본문 read guard를 누락한 두 결함이다. 나머지는 enum metadata operation,
기존 순환 진단 코드, fixture tuple 및 정상적인 `sourceConfirmed=false` 응답의 검사 기대값
오류다. 실패 검사를 수정 후 다시 실행했으며 실패를 통과로 세지 않았다. 진단용 driver의
누락 import도 보존했고, 완료된 진단 빌드를 중복 실행하지 않고 driver만 복구했다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/af2453657f8a4c5e8098e25059426367.json`
- 개발 증거 ZIP SHA256: `60577249d46ac54621bfa9d43fca82d9159416044d276265b82caa89f28e093b`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/df3b584ae3a3490f965cffc9ea445eed.json`
- 최종 증거 ZIP SHA256: `87ddee1e7fdbf3e7aa7464f5e5a913a77b5011dd8308533ea3a97016f22fd413`
- latest runtime: `b775adde470c9ce2aac079362ab0a07d878264b2`
- latest ZIP SHA256: `b194696b9663edb134e2d0fb97628d679bce4c6ca428f16a9d5058fd032339e8` (53981519bytes)
- rollback runtime: `b63020847c70faa18a9e60f48fae812b5caeaf57`
- rollback ZIP SHA256: `5aefba4e38afafe7e96295cae19d7d4d7bf8a972979c1086b5d2c954cf830828` (53979632bytes)

관리 store는 `/workspace/artifacts/v536-verification-managed/packages`다. 전체 압축 복원과
실행이 끝난 뒤에만 latest/rollback을 승격하고, 증거의 durable archive/무결성을 확인한 뒤
이 단위가 소유한 임시 workspace만 정리했다. 기존2세대 관리 보관 계약을 넓히지 않았다.
보관 직후 디스크 여유는 25514283008bytes (23.76GiB)다. 원래 checkout
`b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`와 main
`0d2459b463798d11031c20f46a6c8d1a4ecc35dd`는 보존 대상이다.

실제 Windows/모바일·물리 화면/오디오·전체 UI와 모든 구 reader 실행은 미검증이다.
Linux/.NET compiler·엔진·브라우저 및 패키지/전체 복원 자동화 결과만 주장한다.
초기 빈 화면 원인은 미확정이다. 배열 값 필드 밖의 고급 ABI 전체 완료, 살아 있는 참조
접근과 모듈 async/공개 실행 계약의 완료로 합산하지 않으며 정확한 잔여는 지원 문서를 따른다.
