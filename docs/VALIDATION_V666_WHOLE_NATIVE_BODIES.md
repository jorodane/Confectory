# 기존 whole-body·native 본문 공동 저장 검증

동결 runtime `a2a13d272436be9aac4f14d9eb053773765fd9fe`의 [한 원본 사용자 흐름](V666_WHOLE_NATIVE_BODIES.md)을 최종 **신규 41단계·재사용0·실패0**으로 검증했다. 개발·진단 검사를 최종 결과에 합산하지 않는다.

- LF/CRLF 격리 checkout·seed restore·Release/MCP·빈 캐시 엔진 생성과 원래 host/state 검사.
- 원래 상세창·C# 본문 편집·460px 창과 exact64 값, 한 Save·취소·Undo/Redo·실패/재시도·cold·독립 창·프로젝트 경계.
- 두 단일 계획 및 공동 후보·순서 독립성, 잘못된 마지막 C#·원래 source/flow hash·암묵 ABI 변경 거절, receipt/member/path/graph/계획 변조 거절.
- cold 뒤 정보/함수 표시와 후속 명시 본문 Save가 원래 source hash·read scope를 유지한다. 지연된 성공 응답 뒤 늦은 설명, 두 번째 Save·Review 취소/Confirm을 확인했다.
- Save 전 caller 경합, Review 뒤 whole graph·node·caller 원본 변경은 전체 Confirm을 막고 peer·입력·checkpoint를 보존한다. 정확한 복원 후 새 Review/Confirm으로만 실제 실행40→20을 확인했다.
- 기존 등록 helper/guard·native 계약·소유 자식·단일 whole 타입 전환은 별도 회귀다. 새 Windows 교차 package의 정상 UI와 전체 ZIP 추출본의 응답 유실/늦은 입력/독립 창·실패 수명을 검사했다.

제품은 기존 순수 단일 closure를 각 원본에서 검증한 뒤 내부 overlay와 한 checkpoint CAS로 결합한다. version3의 선택적 `nativeBodyContexts`가 원래 계획을 보관하며 조립 후보도 쓰기 전에 검증한다. 원래 whole lift와 공개/native 계약이 같을 때만 authored graph를 그대로 쓰고, 실제 ABI 변경의 기존 return/저장 처리는 유지한다. SlotBatch·CreationOwners·Review/Confirm·최종 source/read lease·C# 생성·등록 helper 조회·authored UI는 byte 동일하다. 정보별 struct·종류 enum·모듈 interface 및 명시 async 전환 전 sync caller 오류·공개 override도 유지한다.

개발은 32회 중 7개 실패/진단을 보존했다. 초기 Main/provider가 실제 공유 caller를 실행하지 않은 fixture, 미등록 잔존 `.csbody`를 새 read로 기대한 fixture, peer 변경 뒤 basis를 준비해 더 이른 단계에서 차단된 fixture를 구분했다. 제품 측에서는 계약 불변 whole의 불필요한 빈 exits 변경을 발견해 보존하도록 고쳤고, 새 replay 요청의 기존 필수 drafts 누락과 정확한 key 검사 컴파일 타입을 수정했다. 격리 진단용 exception 출력은 원래대로 복원했다. 수정 후 최종 41단계를 전부 새로 수행했다.

직전 정상 package `34074819eb78e7fd62a99466eafe0cbe7d437a11`는 전체 파일/hash를 검증해 별도 임시 위치에 추출하고, 원래 UI에서 유효한 두 본문의 공동 Save만 거절하며 입력·원본을 보존하는 것을 새로 재현했다. 그 authoring reader가 새 pending context receipt도 거절하는 것을 확인했다. 이 호환성 진단은 개발 증거이며 최종 41에 재사용하지 않는다. 같은 게시 세대의 authoring/runtime을 사용하고 pending receipt 자동 migration/downgrade를 하지 않는다. 기존 구 Reference parser 제약은 변경하지 않았다.

변환 뒤 미등록 상태로 남은 원래 C# 파일은 쓰지 않고 byte 보존을 검사했다. 새 등록 또는 CAS 감시 대상으로 표현하지 않는다. 실제 Linux 엔진/portable 프로그램·Chromium 자동화와 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 전수는 구분한다. 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | a2a13d272436be9aac4f14d9eb053773765fd9fe | 6f203b0abf39ed151f7b51897a588e686568a909a31d8ce6d10fb8ee4349440f | 54128171 |
| rollback | 34074819eb78e7fd62a99466eafe0cbe7d437a11 | 3f7b6b74a63b551a3ef9b2d0a1e537e5b3607242cb002d57b343b0591fffdd0c | 54118247 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/32a2a309333946349067d1a586d37781.json` · evidence SHA256 `7843229cd07bb728ed38324f56deef58e0c8d67c09a0d72757d9b018ba91104e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/abc3b40394d64b8f809717e4a824a7de.json` · evidence SHA256 `b813a547d16c584e18a09b042a9251ad52f1a596a50f312767388148a822dd11`.
두 package와 두 실행 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대 및 이번 등록 소유 임시물만 정리했으며 원본 checkout·기존 보관물·과거 증거를 보존했다. 디스크 여유 24505966592bytes(22.82GiB)다.

이 계약 불변 whole/native 공동 저장 단위를 닫는다. 유한 잔여는 private/독립/retained whole의 명시 계획 결합과 실제 계약 변경 callee/import·등록 외부 관측 결합이다. 가능한 타입/문맥 조합을 새 의무로 늘리지 않고 M11/M12/M4 전체 완료로 과장하지 않는다. main은 사용자 검토/merge에 남긴다.
