# 독립 root C# 노드 공동 저장 검증

동결 runtime `dc6254024e43647fdb970cc90712df1a695ae3b9`의 [일반 root 코드 사용자 흐름](V666_ROOT_CODE_GROUP.md)을 최종 **신규 28단계·재사용 13단계·합계 41·실패0**으로 검증했다. 개발 검사와 직전 패키지 진단은 최종 통과 수에 합산하지 않는다.

- LF 빌드 준비 6단계·미실행 private UI 1단계, CRLF 13단계, package/전체 복원 8단계를 신규 수행했다. 동일 동결 소스의 LF 공통·기능 검사 13개는 무결성을 검증한 중단 실행 증거에서 재사용했다.
- 직접 소유 root 코드·일반 native 본문의 단독/공동 후보·순서 독립성, stale source/flow·ABI·C# 및 helpers 경계 침범의 전체 거절을 검사했다.
- 노드는 void/out, 공개/상위 native 함수는 long인 원래 서로 다른 계약을 유지한다. 원래 코드의 실행40과 직접 편집한 두 본문의 실행20, graph/연결/배치/정확한 local 및 다른 독립 소스 bytes/mtime를 검사했다.
- 기존 소스 선택·보호 편집 UI·취소·Undo/Redo·미저장 cold·한 Save·기본/독립 창·저장 실패/재시도·응답 유실/조회 복구와 프로젝트 경계를 검사했다.
- metadata 및 후속 명시 text/helpers Save·늦은 설명/두 번째 Save에서도 원래 function/source/flow/read 기준을 유지했다. 변조·누락된 member/receipt/경로/읽기 범위와 implicit graph/ABI 변경은 입력을 보존하며 거절한다.
- Save 전 caller와 Review 뒤 graph·선택 record·독립 원문 경합을 차단하고 원문 복원 후 새 Review/Confirm으로 계속했다. 기존 private 후보/guard/UI·등록 helper·retained ABI를 회귀로 포함했다.
- 새 package의 구조/probe·정상 UI 및 전체 ZIP 추출/hash/probe·응답 유실·늦은 입력·독립 창과 실패 수명을 새로 검사했다.

제품 변경은 authoring 네 파일이다. Bodies는 직접 소유 구현의 일반 root 코드 목록을 기존 scoped code 방식으로 읽는다. Graphs는 whole/forwarded 문맥이 없는 root와 기존 private 코드의 자체 ABI·source/helpers 경계를 검증한다. Contracts의 명시 root 분기는 공개/native 계약 불변만 받으며, Graphs.Text를 통과한 code ID만 별도로 추적한다. 노드 fragment를 상위 구현 본문처럼 따로 컴파일하지 않고 전체 assembled Blueprint를 실제 상위 계약으로 컴파일한다. WholeBodies는 이 root 계획과 일반 본문을 기존 version3 nativeBodyContexts·readGuards에 결합한다.

기존 whole/context에 대한 별도 검증과 필수 본문/출력 계획을 유지한다. UI·리소스·C# 생성·원래 whole/retained 코드·SlotBatch·CreationOwners·Review/Confirm·최종 CAS 및 권한/레이아웃은 byte 동일하다. 자동 C# 변환·helper 삽입·ABI/연결 추측·새 receipt version/접근 권한은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 19회·실패 2건을 보존했다. 재현 fixture의 모듈 alias가 re-export 중 바뀌는 오류를 고친 뒤 기준을 확인했다. 첫 root 후보는 보조 함수를 가진 노드 fragment를 상위 구현 본문으로 검증해 CS0103으로 거절됐다. 원래 노드 경계와 전체 assembled compiler의 역할을 구분하고, 실제 서로 다른 void/out 노드·long 상위 계약으로 검증했다. 수정 후 동결 소스의 최종 검증을 진행했다. 환경 재연결 뒤 출력 파이프 오류로 첫 실행기가 19단계 완료 후 종료했고, 오류 정리가 임시 checkout을 정리했다. 그 19개 통과 기록과 증거 ZIP은 보존됐다. 전체 소스/검증기/SDK·의존성 동일성과 ZIP/명령 일치를 확인해 기능 검사 13개를 재사용하고, 사라진 LF 빌드 준비 6개와 나머지 22개를 신규 실행했다. 최종 신규28+재사용13이며, 제품 검사 실패를 재사용하지 않았다. 후속 실행기는 출력을 파일에 보관했다.

직전 정상 package `50cfd5a09aa32dbe7eafed2bc0db5e9f1fc06574`의 전체 파일/hash를 검증해 별도 위치에 추출했다. 그 runtime은 원래 void/out root 코드 프로그램40을 실행하지만 정보 편집 목록에 root 코드를 제공하지 않고 명시 root 단독/공동 계획도 거절한다. 직전 UI는 Blueprint 경로의 거절 뒤 입력/원문을 보존하며, 새 root pending receipt도 직전 reader가 거절함을 확인했다. 이 진단은 개발 증거다. 같은 세대의 authoring/runtime을 사용하고 자동 migration/downgrade를 하지 않는다. 구 Reference parser 제약은 유지한다.

Linux 실제 엔진/portable 실행과 Chromium 자동화이며 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증은 하지 않았다. 과거 초기 빈 화면 원인은 미확정이다. 변환 뒤 미등록 잔존 csbody는 새 감시/관측 대상으로 주장하지 않고 byte 보존만 검사했다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | dc6254024e43647fdb970cc90712df1a695ae3b9 | 3654495854924d6d649eb04bfa6d0ed2a4d4c0a86d17adc4a6cd15aae06b40a9 | 54129218 |
| rollback | 50cfd5a09aa32dbe7eafed2bc0db5e9f1fc06574 | 5a1206bcb39dda971ad9ce3a6be4aa091951abe7a60f8fe325825a910a09160c | 54129889 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/923329d87fce416a9e3cf88916b4600c.json` · evidence SHA256 `36240ba3864607e93cbc4140846721556405439f6cf743b15244c270cba328e7`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/3034a5c28ead44eb8de51db1a44896af.json` · evidence SHA256 `d1bf22b15b8cd8fa2fac4d72fa488450d27da24789acb3a82545f33ed0d8d733`.
중단 record `/workspace/artifacts/v536-verification-managed/runs/08ac07983e204faea24ab9f3c90b1eb3.json` · evidence SHA256 `4ee1fa564b8df3ceb38c21abef0e0a11a323fd667bf392ac87a0c5e090ed7778`.
재사용 근거는 최종 증거의 continued-verification.json 및 root-code-group-reuse.json에 기록했다.
두 package와 최종·개발·중단 실행의 세 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대와 이번 등록 소유 임시물만 정리했고 원본 checkout·기존 보관·과거 증거를 보존했다. 디스크 여유 24451928064bytes(22.77GiB)다.

이번 일반 root 코드 한 흐름을 닫는다. 남은 유한 흐름은 whole/retained 문맥의 필수 계획을 포함한 독립 코드 결합, 실제 계약 변경 callee/import 및 등록 외부 관측 결합이다. 가능한 타입/문맥 조합을 새 의무로 늘리지 않는다. main은 사용자 검토/merge에 남긴다.
