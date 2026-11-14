# C# import 함수 간 값→ref 계약·본문 공동 저장 검증

동결 runtime `c5a2cc4d4ca6c47e0b0c7ce3b9639d78fb54b740`의 [값→ref 계약·본문 공동 저장](V666_NATIVE_ROLE_CHAIN.md)을 **신규 41단계·재사용 0·실패0**으로 검증했다. LF20·CRLF13·새 package/전체 ZIP 복원8이다. 개발 진단은 이 통과 수에 포함하지 않는다.

- C# import로 호출하는 두 직접 소유 함수의 동일 값 입력을 ref로 함께 변경했다. 첫 본문의 ref 호출을 직접 작성하고 기존 공유 caller의 ref 입력 셀과 return 출력을 명시 유지했다. 순서를 바꿔도 같은 후보와 원래 source hash를 유지했다.
- 원래 native 함수는 값 인수5를 보존하고 결과38, 공유 caller 반환46·셀5였다. 편집 후 실제 native 함수는 ref 인수를38로 바꾸며 공유 caller 반환79·셀79였다. 공개/native 별칭·타입·순서·반환·기존 helper를 보존했다. 원문과 같은 둘째 C# 본문은 검토된 atomic 읽기 멤버이며 BOM·CRLF bytes와 파일 inode/size/mode/mtime를 보존했다.
- 선택 본문 누락·stale hash·ref 없는 호출·native role/별칭 변경·caller 누락·ref 저장소 대신 literal 또는 다른 입력·출력 identity 변경·상충 source·혼합 방향을 전체 거절했다. cold graph 발견에서 캡처 hash를 재서명한 import 별칭/역할 변경 및 혼합 family도 거절했다.
- 기존 own C# source/계약 대응 UI의 취소·Undo/Redo·미저장/저장 cold·한 Save·기본/독립 창·checkpoint 실패/재시도·응답 유실/조회 복구·프로젝트 왕복·늦은 입력과 두 번째 Save를 검사했다. 원본 경합은 기존 trusted Save 관측 검사로 확인했다.
- 후속 owner/function metadata Save도 원래 읽기 범위를 유지했다. Save 전 및 Review 뒤 helper header/body·caller graph·native body/header 변경은 원본과 checkpoint를 보존하며 Confirm을 차단했다. 정확히 복원한 뒤 새 Review/Confirm으로 결과79와 수정하지 않은 B/helper 파일 메타데이터 보존을 확인했다.
- 기존 값→ref native/guard/API와 이전 반환 import native/guard를 회귀로 검사했다. 새 package 구조/probe·실행 UI, 전체 ZIP 추출/hash/probe·응답 유실·늦은 입력·독립 창·성공/실패 수명을 새로 확인했다.

제품 변경은 InformationFunctionNativeJoint·InformationFunctionNativeRoles·InformationFunctionBatch 세 파일이다. 기존 역할 계획의 원본/native/caller 검증을 request-local joint compiler와 기존 출력 overlay에 연결한다. 저장 후 발견은 같은 역할 방향과 캡처된 function/body/header hash·정확한 signature/import delta를 확인한다. 기존 native buffering과 직접 작성한 C# text를 유지하고, 원문과 같은 명시 본문은 기존 retained-body proof에 둔다. UI/layout·생성기·권한·Review/Confirm·최종 CAS·version3 receipt·source/read240·member64를 바꾸지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 16단계 중 실패 1건은 기존 독립 값→ref fixture에서 가져온 파일 보존 기대의 오류였다. 실제 Confirm과 결과79 및 모든 경합 거절을 통과한 뒤 사용자가 직접 수정한 A 본문까지 원문 불변으로 비교했다. 보존 검사를 변경 없는 B/helper로 한정하고 제품 수정 없이 API와 미실행 late 검사를 통과했다. 원래 실패 로그를 보존했다. 읽기 전용 ps 조회도 종료된 worker를 가리켜 exit1이었으며 completion JSON으로 결과를 확인했다. 중복 빌드/실행이나 환경 초기화는 없었다. 동결 source 최종 검사는 모두 신규다.

직전 intact package `1b2f1a18f3e7ffc9264abb5c5e07ce8b6feab9c8`의 전체 파일/hash를 별도 추출했다. 원래 실행46·셀5는 유효하고 새 공동 값→ref/import Save는 거절하며 두 입력·checkpoint·원문을 보존했다. 이 단위의 실제 저장 캡처를 그대로 전달한 순수 pending guard의 이전 reader 수용은 `False`였다. 이를 이전 전체 UI의 cold/Review/Confirm 교환 완료로 확대하지 않는다. 같은 세대 authoring/runtime을 사용하며 자동 migration/downgrade나 구 Reference parser 변경은 없다.

Linux 실제 .NET/portable 실행·Chromium 자동화다. Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 검증하지 않았다. 과거 간헐 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | c5a2cc4d4ca6c47e0b0c7ce3b9639d78fb54b740 | d4cf81e4a1d94d749b3e6fed0fa8e95ef0d370bcb3aad79c9f83cd668e0eebdf | 54137967 |
| rollback | 1b2f1a18f3e7ffc9264abb5c5e07ce8b6feab9c8 | b4aebe41f22004475d6db8f0cae645381e6454b29caa2fb3b0a3ff9faac2c515 | 54134867 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/ef358be4e1434e1dab7365ae94ed033b.json` · evidence SHA256 `9c667caa545c09c9b2d5d0d52eeb9adb5578dc681a52e94973a628e32a40184f`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/b27fbc27a4934a1794634787880c1e87.json` · evidence SHA256 `b5c3aca2fc858b961c5c519437646e9fbf58479dd1410a4f0b7cc8e4e69642e5`.
두 package와 두 evidence archive hash를 재확인했다. 이번 등록 소유 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·과거 증거를 보존했다. 디스크 여유 24375521280bytes(22.70GiB)다.

이 직접 소유 동기 scalar 값→ref·기존 ref 저장소·native import 호출 한 흐름을 닫는다. 다른 역할 방향·고급 타입 결합과 private/whole/상속·override·외부 수정 경계는 이번 검증으로 대신하지 않는다. 구 reader 전체 UI 교환과 실제 기기/전체 UI·초기 빈 화면 원인은 위 잔여로 유지한다. main은 사용자 검토/merge에 남긴다.
