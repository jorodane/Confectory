# C# import 함수 간 반환 계약·본문 공동 저장 검증

동결 runtime `1b2f1a18f3e7ffc9264abb5c5e07ce8b6feab9c8`의 [반환 계약·본문 공동 저장](V666_NATIVE_RETURN_CHAIN.md)을 **신규 41단계·재사용 0·실패0**으로 검증했다. LF20·CRLF13·새 package/전체 ZIP 복원8이다. 개발 진단은 이 통과 수에 포함하지 않는다.

- C# import로 호출하는 두 직접 소유 함수의 long 반환을 double로 함께 변경했다. 각 native 선언·본문과 기존 반환 소비자의 호환 out count 대응을 직접 선택했다. 순서를 바꿔도 같은 후보와 원래 source hash를 유지했다.
- 원래 실행에서 native 반환42/40·out35/34·공유 caller52를 확인했다. 새 실제 IInvoke는 double1.75/1.25·out38/34를 반환하며 명시적으로 대응한 공유 caller 결과는42였다. 원래 입력·out identity·별칭과 helper 선언·본문 bytes·권한을 보존했다.
- 유효한 단독 A 편집은 변경하지 않은 B의 원래 long 계약을 유지한다. 선택한 두 번째 본문 누락·stale hash·잘못된 새 호출/반환·native 선언·caller 누락·암묵적 소비 대응·입력/out identity 변경·상충 source 계획·혼합 역할은 전체 거절했다.
- 기존 상세/반환 타입/출력 대응/own C# 편집 UI의 취소·Undo/Redo·미저장/저장 cold·한 Save·기본/독립 창·checkpoint 실패/재시도·응답 유실/조회 복구·프로젝트 왕복·늦은 입력과 두 번째 Save를 검사했다. 경합은 기존 trusted Save 관측 검사로 확인했다.
- owner/function metadata Save 후에도 원래 읽기 범위를 유지했다. Save 전 및 Review 뒤 helper header/body·caller graph·native body/header 변경은 원본과 checkpoint를 보존하며 Confirm을 차단했다. 정확히 복원한 뒤 새 Review/Confirm으로 결과42와 원래 helper bytes/inode/mode/mtime 보존을 확인했다.
- 기존 반환 native/guard/API와 이전 입력 import native/guard를 회귀로 검사했다. 새 package 구조/probe·실행 UI, 전체 ZIP 추출/hash/probe·응답 유실·늦은 입력·독립 창·성공/실패 수명을 새로 확인했다.

제품 변경은 InformationFunctionNativeJoint·InformationFunctionNativeReturns·InformationFunctionBatch 세 파일이다. 기존 반환 원본·caller 출력 선택 검증을 joint compiler에 연결하고 기존 출력 overlay로 합성한다. 저장 후 발견은 원래 scalar 입력/반환 전환과 캡처된 function/body/header hash·정확한 signature/import delta를 확인한다. 기존 native buffering과 source text를 유지하며 C# 변환·추측·중간 checkpoint 쓰기는 없다. UI/layout·등록 loader·생성기·권한·Review/Confirm·최종 CAS·version3 receipt와 source/read240·member64를 바꾸지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 16단계 중 실패 1건은 잘못된 부정 fixture 기대였다. A만 선택한 편집의 C# var가 기존 B의 long 값을 유효하게 사용할 수 있으므로 제품을 바꾸지 않고 단독 허용을 긍정 검사로 고쳤다. 대신 선택한 B 본문이 빠진 경우를 거절 검사로 추가했다. 원래 로그를 보존하고 수정된 native/UI와 guard/API/late 검사를 통과했다. 초기 baseline 조회는 원래 빌드 소유자가 실행 중이라 Workspace.load가 거절했고, 완료를 기다린 뒤 미실행 검사만 수행했다. 한 차례 읽기 전용 진행 조회의 exec-server transport가 끊겼으나 상태 조회와 실제 exec 재성공으로 작업 트리와 완료된 결과 보존을 확인했다. 환경을 재생성하거나 진행 중인 작업을 중복 실행하지 않았다. 동결 source 최종 검사는 모두 신규다.

직전 intact package `0268361d99455b85d87e9a183b1338e6476b22c6`의 전체 파일/hash를 별도 추출했다. 원래 실행52는 유효하고 새 공동 반환/import Save는 거절하며 입력·checkpoint·원문을 보존했다. 원래 읽기 hash를 확인한 기존 checkpoint에서 재구성한 순수 pending guard의 이전 reader 수용은 `False`였다. 이를 이전 전체 UI의 cold/Review/Confirm 교환 완료로 확대하지 않는다. 같은 세대 authoring/runtime을 사용하며 자동 migration/downgrade나 구 Reference parser 변경은 없다.

Linux 실제 .NET/portable 실행·Chromium 자동화다. Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 검증하지 않았다. 과거 간헐 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 1b2f1a18f3e7ffc9264abb5c5e07ce8b6feab9c8 | b4aebe41f22004475d6db8f0cae645381e6454b29caa2fb3b0a3ff9faac2c515 | 54134867 |
| rollback | 0268361d99455b85d87e9a183b1338e6476b22c6 | e7ce3661f090cead37dfba11088d72d89a3917d75e1799e2548ffb8b8cd587d8 | 54138304 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/3636cd708fc7435bb14239bf073d44a9.json` · evidence SHA256 `40b597bcdffe33eaf0a4d66bae6786a2366a06d1231d81119e713e60ff5517af`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/59e52aa178744914ba9c3881783828c7.json` · evidence SHA256 `74f57b6a8d61e7ba3cf4719a02fbc26a6a6a7e72c03a9984ad048ad4a3226b47`.
두 package와 두 evidence archive hash를 재확인했다. 이번 등록 소유 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·과거 증거를 보존했다. 디스크 여유 24388530176bytes(22.71GiB)다.

이 직접 소유 동기 scalar 반환·호환 out 소비·native import 호출 한 흐름을 닫는다. 다른 역할/out 타입·고급 타입 결합과 private/whole/상속·override·외부 수정 경계는 이번 완료에 포함하지 않는다. 구 reader 전체 UI 교환과 실제 기기/전체 UI·초기 빈 화면 원인은 위 잔여로 유지한다. main은 사용자 검토/merge에 남긴다.
