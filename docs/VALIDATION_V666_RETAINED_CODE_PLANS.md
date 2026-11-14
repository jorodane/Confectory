# retained 필수 계획과 독립 코드 공동 저장 검증

동결 runtime `ea57f92f3662f24de130936cd839510cb042487e`의 [retained 필수 계획 공동 저장](V666_RETAINED_CODE_PLANS.md)을 최종 **신규 41단계·재사용 0·실패0**으로 검증했다. LF20·CRLF13·package/전체 복원8이다. 개발 재현과 직전 package 진단은 최종 통과 수에 합산하지 않는다.

- 기존 retained 문맥 본문·출력 identity와 독립 root C# 본문/helpers를 모두 명시하고 두 번째 소유 함수의 일반 본문과 한 후보로 결합했다. 후보의 함수 순서 독립성을 검사했다.
- 원래 실행41과 직접 편집한 세 본문의 실행22를 확인했다. 공개/native 인자 이름이 다른 원래 위치 계약, long 상위와 void/out 노드의 서로 다른 ABI, graph bytes·배치·exact64 local·공유 caller·독립 원문 bytes/mtime를 유지했다.
- 필수 context/output 계획 누락·출력 재대응·stale source/flow·임의 ABI/공개 계약·helper 경계 침범·존재하지 않는 helper와 잘못된 마지막 본문은 원자 거절했다. 누락/변조 receipt·source·member·locator·group·read 및 frame을 검사했다.
- 원래 선택/보호 편집 UI의 취소·Undo/Redo·미저장/저장 cold·한 Save·기본/독립 창·실패/재시도·응답 유실/조회 복구·프로젝트 경계를 검사했다.
- metadata 후속 Save와 늦은 설명/두 번째 Save는 원래 계획·읽기 기준을 유지한다. 본문 후속 Save는 두 필수 계획과 현재 draft hash를 모두 명시해야 하며 부분 계획은 거절했다.
- Save 전 caller header와 Review 뒤 graph·context record·독립 code record·독립 원문 경합에서 Confirm을 차단했다. 원문 복원 후 새 Review/Confirm으로 실행22를 확인했다.
- 기존 일반 root 후보/guard, retained UI, 등록 helper, retained ABI를 회귀로 검사했다. 새 package의 구조/probe·정상 UI와 전체 ZIP 추출/hash/probe·응답 유실·늦은 입력·독립 창·실패 수명을 검사했다.

제품 변경은 authoring 네 파일이다. Graphs는 명시 retained 원래 context/source/output 계획을 확인하고 독립 노드 목록·본문 검증에 연결한다. Contracts는 공개·native 계약 불변과 두 source 계획을 요구하며 기존 전체 assembled compiler를 유지한다. Retained는 원래 root/output/binding 검증 뒤 독립 source도 확인해 추가 null exit 표기만 생기는 경우 authored graph bytes를 보존한다. WholeBodies는 한 구현/target의 명시 본문1~8개를 기존 version3 nativeBodyContexts·readGuards에 결합한다. 원래 단독 retained 편집도 목록에서 문맥을 명시 선택하는 회귀 fixture로 검사했다.

UI/레이아웃/리소스·C# 생성·SlotBatch/CreationOwners·Review/Confirm·최종 CAS·권한은 byte 동일하다. 자동 C# 치환·helper 삽입·암묵적인 필수 source 보충·새 receipt version/접근 권한은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 15단계와 실패 0건의 결과/로그를 보존했다. 게시 기준에서 원래 실행41과 일반 native 단독 검증은 유효했지만 paired retained/code 후보가 거절되는 것을 먼저 재현했다. 보존된 원래 계획에서 구현하고 최종 동결 source로 전부 새로 검사했다. 환경 연결 중단 뒤에도 파일로 출력을 보관하는 기존 검증기가 남은 검사를 완료했다. 복구 후 실제 명령으로 종료0·41개 결과·패키지 승격과 archive hash를 확인했고 검증을 중복 실행하지 않았다.

직전 package `dc6254024e43647fdb970cc90712df1a695ae3b9`의 전체 파일/hash를 별도 추출해 검사했다. 그 runtime은 원래 프로그램41을 실행하고 일반 native 단독을 검증하지만 paired retained/code 단독·공동 계획을 거절하며 독립 root source를 선택 목록에 제공하지 않는다. 기존 context 편집 입력·checkpoint·원문은 보존한다. 새 다중 source pending receipt는 직전 reader가 거절한다. 같은 세대 authoring/runtime을 사용하며 자동 migration/downgrade나 구 Reference parser 변경은 없다.

Linux 실제 .NET 엔진/portable 실행·Chromium 자동화다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증은 하지 않았다. 과거 간헐 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | ea57f92f3662f24de130936cd839510cb042487e | 1baf60e794bfc8d902527161a8464678bf2139e720529597380e74d49b06bebf | 54133144 |
| rollback | dc6254024e43647fdb970cc90712df1a695ae3b9 | 3654495854924d6d649eb04bfa6d0ed2a4d4c0a86d17adc4a6cd15aae06b40a9 | 54129218 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/ddc4cd13377a42198d8b4a5474f2607b.json` · evidence SHA256 `9e21277c711b58baa6038024725ff009ae0f81262d2bb1a15a1f8477d455d95f`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/6ffc210a221a45d4acb961effc0cc057.json` · evidence SHA256 `1b748709813844eaab94926b90c8f0e57379755283e42f4c56076514922c0768`.
두 package와 두 evidence archive hash를 재확인했다. 등록된 이번 소유 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·과거 증거를 보존했다. 디스크 여유 24434307072bytes(22.76GiB)다.

이번 필수 retained 계획·독립 코드·일반 본문 한 흐름을 닫는다. 남은 유한 흐름은 실제 계약 변경 callee/import와 등록 외부 관측 결합이다. 타입/문맥별 모든 조합을 새 완료 조건으로 늘리지 않는다. main은 사용자 검토/merge에 남긴다.
