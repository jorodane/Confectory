# 실제 객체 compound 값 접근 검증

[지원 경계](V666_LIVE_COMPOUND.md)의 제품·검사를 `6e5f3e03ea53209f00edb4fae014185bb3a3a599`에서 고정했다.
최종 **신규42단계·동등 재사용0·실패0**을 통과했다. 후속 결과 문서 커밋은 제품·검사·
실행 코드를 바꾸지 않는다. 실제 Windows/모바일·전체 UI 완료로 합산하지 않는다.

게시본 `2406f7ccd14d36399594a15d48b4f6aef47a09f8`에서 실제 native struct ABI는
컴파일되지만 live compound 생성이 거절됨을 CLR로 재현했다. 원본과 선언 data는 바꾸지
않았다. 기존 primitive/reference/enum descriptor와 참조를 포함해 native 값으로 생성할 수
없는 필드의 미지원 descriptor를 golden으로 보관했다. golden 입력과 실행 증거 재사용을
구분한다.

새 native 검사는 전이 값/enum 구조·타입 출처, 실제 Blueprint Read→Set→Read, 반복 호출과
독립 상속 인스턴스를 확인한다. caller 박스·Read 결과 박스·Access-write 결과의 변경이
실제 필드를 바꾸지 않으며 struct 내부 배열과 T[]는 같은 참조를 보존한다. 기존 native
default/null/NaN/enum 값은 정규화하지 않는다. raw ID/object[], 다른 nominal 타입,
같은 이름의 위조 필드 구조, 잘못된 배열·stale hash·mutable ref를 거절하고 유효한 저장소를
보존한다. 표시 변경은 값 계약을 유지하며 깊은 필드 변경은 pinned graph를 거절한다.
정확 복원은 원래 산출물과 실행을 회복한다. 등록된 중첩 타입 locator만 있는 경우의
명시 dependency 거절과 허용된 dependency의 별도 nominal assembly/원문 관측도 확인한다.
이 metadata 검사와 등록 외부 struct의 모든 runtime/UI 조합 완료를 구분한다.

UI는 원래 속성 검색·모바일 값 선택·native 입력·기존 전체 보기와 실제 compiler/engine을
사용한다. 새 읽기·가져오기·receiver·소비 연결·실행 attachment의 한 후보 Save, cold,
기존 C# 후속 편집/취소·저장 실패·Review/Confirm, 깊은 자식 원본의 Save 전·Review 뒤
충돌, 응답/영수증 유실과 늦은 입력을 검사한다. 기존 enum 경로도 같은 driver에서 검사한다.

`tools/verify_desktop.py --suite live-compound`을 공개 SDK
`/workspace/toolchains/dotnet-10.0.401`과 기존 NuGet seed로 실행했다. 살아 있는 AI 계정·
유료 호출·새 외부 접근 권한은 사용하지 않았다.

| 최종 범위 | 신규 실행 | 동등 재사용 |
| --- | ---: | ---: |
| LF 독립 checkout·빌드·compound native/UI·기존 enum native/UI·primitive/ref 회귀 | 16 | 0 |
| CRLF 독립 checkout·빌드·compound native/UI·기존 primitive/authoring/정보 배열 회귀 | 15 | 0 |
| 관리 IPC 수명 | 1 | 0 |
| 새 교차패키지·무결성·패키지 UI·전체 ZIP 복원·native/수명·실패 정리 | 10 | 0 |

native probe의9개 내부 확인과 각 UI의 내부 체크를 별도 단계로 부풀리지 않는다.
기존 검사를 새로 실행한 것과 보관 실행 증거 재사용을 구분하며 이번 최종 검증에는
이전 실행 증거를 가져오지 않았다. 개발 기록 15회도 실패0으로 보관했고
최종42단계에 중복 합산하지 않았다. baseline의 예상 runtime 거절은 probe 자체가
검증한 원래 결함 재현이며 통과 후에도 원래 거절/실행 로그를 보관한다.

단일 native 값은 박스 복사를 통해 이전 출력·실제 필드를 분리하고 내부 배열은 그대로
공유한다. C# 기본값·null/NaN/enum 내용을 새 JSON 검증으로 정규화하지 않는다. 같은
이름의 잘못된 CLR 필드 구조·다른 nominal/잘못된 배열·stale hash·mutable ref를 거절한다.
깊은 자식의 source를 바꾼 UI Save 전·Review 뒤 거절, 정확 복원·새 Review·Confirm,
후속 C# 취소/저장 실패·cold·응답/영수증 유실과 늦은 입력을 패키지 전체 복원본에서도
새로 검사했다. 최상위 enum·primitive/reference/ref 계약과 현재 source/권한/CAS 경계를
보존한다. 등록된 중첩 외부 타입은 dependency 부재 거절과 별도 assembly/source metadata
범위이며 모든 외부 runtime/UI 조합의 실행 완료로 과장하지 않는다.

독립 모듈 compile-closure 실험의 소스·compiler 로그·실제 CLR 결과·파일 SHA는 개발
증거의 `module-bootstrap-prototype/`에 보관했다. 같은 이름의 선행 참조 계약으로 상호
참조 DLL을 컴파일하고 runtime에는 실제 Information_Example/Contracts_Example DLL만 두어 데이터/분기/
module identity를 왕복했고 동기 호출은 CS0619로 거절됐다. 이 prototype을 제품 모듈
async/공개 실행 연결이나 최종42단계의 통과로 합산하지 않는다. 실제 generator·관측/
등록/CAS·기존 모든 계약 closure의 제품 연결은 여전히 잔여다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/e1eeb1a4d5aa4182a73b3b8cb63e82f9.json`
- 개발 증거 ZIP SHA256: `6956c6ef1293818f1ea41edbaec7c625777671f3fc265fb279fddba4a81f9f34`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/9f16263b8b9046b6a30f22299464ab78.json`
- 최종 증거 ZIP SHA256: `7b8fc151b82599411af16b3b294484acf069d943a562f571fadf9d6fe1b2ce3b`
- latest runtime: `6e5f3e03ea53209f00edb4fae014185bb3a3a599`
- latest ZIP SHA256: `e52561803d328fdb507562db1fa3011fb0fbfe03a8d53d5bb33c8e03bfe0d509` (53988947bytes)
- rollback runtime: `549eb40128ea003b3603531b69683bd72f1f58e1`
- rollback ZIP SHA256: `cf182d1884c030645338641054fc8dec027ec4e07df05cc79ba0c329522e440d` (53984799bytes)

관리 store는 `/workspace/artifacts/v536-verification-managed/packages`다. 전체 압축 복원과
실행 후 latest/rollback을 승격하고 durable 증거 archive/무결성 확인 뒤 이 단위가 소유한
임시 workspace만 정리했다. 기존2세대 보관/정리 계약을 넓히지 않았다. 보관 직후 디스크
여유는 25489575936bytes (23.74GiB)다. 원래 checkout
`b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee`와 main
`0d2459b463798d11031c20f46a6c8d1a4ecc35dd`를 보존한다.

Linux/.NET compiler·엔진·Chromium·패키지/전체 복원 자동화 결과다. 실제 Windows/모바일·
물리 화면/오디오·전체 UI와 모든 구 reader 실행은 미검증이다. 초기 빈 화면 원인은
미확정이다. 살아 있는 정보 reference의 나머지 bridge/수명·reference/함수 필드와 모듈
async·공개 실행 결과의 완료로 합산하지 않는다. 정확한 잔여는 지원 문서와 고정9행을 따른다.
