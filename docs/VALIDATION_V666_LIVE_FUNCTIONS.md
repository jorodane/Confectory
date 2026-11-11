# live 함수 속성 검증

제품 동결은 `354716abd90701e34c7b89ec235be82691ed7591`다. [지원 범위](V666_LIVE_FUNCTIONS.md)의 최종 독립 검증은
**신규 42단계·재사용 0·실패 0**이다. LF/CRLF checkout의 Release·MCP·실제 편집기,
native/API/UI와 기존 함수 필드/일반·reference·ref/compound 회귀, 새 Windows 교차 패키지와
전체 압축 복원, 실패 수명 관리가 포함된다. 기존 검사 코드를 다시 실행한 것과 과거
통과 증거를 재사용하는 것은 구분한다. 개발 회귀를 이 최종 단계에 합산하지 않았다.

실제 CLR에서 함수와 배열의 동일성·상태·GC, 원래 반환/out/공개 분기·Task 결과 및 반복
Blueprint Read→Set→Read를 확인했다. 메타데이터 검사는 provider를 호출하지 않는다.
잘못된 함수·서명·매개변수 역할·async DTO·owner/hash·ID/null/배열 및 mutable ref를
거절하고 원래 값을 보존했다. nativeFunction 없는 옛 descriptor도 자동 승격하지 않는다.
기존 기본형/reference/enum/compound descriptor와 inline 함수 compound의 unsupported
경계, IInvoke/IAsyncInvoke 및 동기 caller 오류 규칙을 유지했다.

기존 460px 본문 편집에서 명시적 함수 Read/Set·실행31을 저장했다. 취소·Undo/Redo·
미저장 cold 복원·저장 실패 후 입력/원문 보존·재시도·중복 Save 비활성, 실제로 apply와
settled 응답을 가린 후 재시작 복구, 응답 중 늦은 입력과 두 번째 Save를 확인했다.
Save 전·Review 후 함수 선언 변경은 전체 거절하고 정확 복원·새 Review/Confirm 후
실행했다. UI 배치와 외부/부모 쓰기 권한을 바꾸지 않는다.

개발 중 property 계약 후보에서 관찰한 정보 타입을 Review 후 바꿔도 Confirm이 진행되는
실제 CAS 누락을 재현했다. propertySourceScope/propertySourceReads를 원래 receipt에
보존하고, 원래 등록/함수/graph에서 유도한 정확한 읽기 범위만 Review와 최종 lease에
다시 전달하도록 수정했다. 소유 source는 readGuards, 등록 외부 source는 기존 CommitPlan의
읽기 검사다. 로컬/등록 외부 타입의 Save 전·Review 후 변경, 누락/변조 receipt, 미생성
프로젝트를 건드리지 않는 비관련 Save, 후속 설명 Save의 같은 관측 hash 보존 및 cold
복원·재시도·새 Review/Confirm을 검증했다. 외부 타입/pack 원본과 C# 기록은 보존했다.
새 패키지/전체 복원에서도 native/API/UI·저장 실패/응답 유실/늦은 입력과 등록 타입 CAS를
새로 실행했다. 새 UI 타입 선택기나 객체 조회/provider 선택 완료로 세지 않는다.

개발은 37개 실행 중 12개 실패를 포함한다.
한 실제 최종 CAS 누락은 위 수정으로 마감했다. 나머지는 초기 문법, pack 복사/explicit
owner·가짜 interface 바인딩·편집기 report·등록 receipt와 변경 없는 기록/receipt 종류·
설명 text 키/외부 source 소유권에 대한 fixture 가정을 수정한 기록이다. 실패·진단과
최종 입력, 로그/화면/원본/hash를 보관했다. 정상 검사는 중단하거나 중복 실행하지 않았다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/0ab981c36604483995e81db934b71bc0.json`
- 개발 증거 ZIP SHA256: `b72ab01838af4ad225d9b0be3032d3649e6446b010bd9a5cd715f0b257031890`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/5d66cb946b544b38956d739243a9c2a5.json`
- 최종 증거 ZIP SHA256: `70a811f7c1e7c44fe80f011a1d18dd4781cd0f3a5dd048800e1183d65175f2aa`
- latest runtime: `354716abd90701e34c7b89ec235be82691ed7591`
- latest ZIP SHA256: `9f8adbd8ea25cf5f87bd8b59d345321679576534924a1b3dee3ed49882c553e4` (54031183bytes)
- rollback runtime: `cad5653e603e5bd29ee2e3a5f3d0ffbfe4a46054`
- rollback ZIP SHA256: `2441ac98ab1dfb9bdfe7da28776472a48133190263c2e1ad5af8efbfbb9e4528` (54017825bytes)

store는 `/workspace/artifacts/v536-verification-managed/packages`다. 두 보관본과 증거 무결성을 확인한 뒤 이번 소유 임시 workspace만
정리했다. 보관 후 여유 공간은 25456807936bytes (23.71GiB)다. 원래 checkout
b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee와 main을 보존하며 사용자가 work/current를
검토하고 main에 병합한다.

객체 참조 bridge/수명과 reference 필드, 선언 구현과 실제 함수 인스턴스의 명시적 binding은
같은 고정9행의 유한 잔여다. 함수가 들어 있는 compound live 값의 기존 지원 경계를
전체 참조 접근 완료로 세지 않는다. M11/M12/M4는 회귀 근거 없이 다시 열지 않는다.
Linux/.NET/Chromium 자동화 결과이며 실제 Windows·물리 기기·전체 UI·모든 구 reader는
미검증이다. 초기 빈 화면의 원인은 미확정이다.
