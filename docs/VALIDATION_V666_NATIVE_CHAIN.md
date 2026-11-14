# 선택 native 함수의 import 계약·본문 공동 저장 검증

동결 runtime `0268361d99455b85d87e9a183b1338e6476b22c6`의 [함께 변경하는 native 함수 import 계약·본문](V666_NATIVE_CHAIN.md)을 최종 **신규 26단계·재사용 15·합계 41·실패0**으로 검증했다. LF20·CRLF13·새 package/전체 ZIP 복원8을 포함한다. 개발 진단은 이 수에 포함하지 않는다.

- 두 소유 함수의 long→string 입력·명시 native 선언/본문·공유 ordinary Blueprint caller 계획을 한 후보로 결합했다. 첫 함수의 C# import가 함께 변경한 둘째 함수의 새 계약을 호출한다. 편집 순서를 바꿔도 결과와 원래 source hash는 같았다.
- 원래 실제 실행85와 편집 후34를 확인했다. 소유 helper와 등록 외부 helper/부모도 사용하며, import 별칭·호출 edge·helper/provider bytes·권한을 보존했다. 외부 write member는 없다.
- 부분 선택·stale body/hash·새 호출의 타입 오류·잘못된 native signature·빠진 caller/등록 proof·중복 상충 계획·foreign owned-unit 주장은 전체 거절했다. 캡처된 header/import 범위 변조와 body/function hash 변경도 거절했다.
- 기존 실제 상세/타입/본문 UI의 취소·Undo/Redo·미저장/저장 cold·한 Save·기본/독립 창·checkpoint 실패/재시도·응답 유실/조회 복구·프로젝트 왕복을 확인했다. 늦은 설명 입력과 두 번째 Save도 검사했다.
- cold와 owner/function metadata Save 이후 원래 nativeBodyDependencies/nativeBodyDependencyReads/readGuards를 유지했다. Save 전 및 Review 뒤 외부 함수·부모·등록 manifest와 소유 helper 경합은 원래 자료와 checkpoint를 보존하며 차단했다. 정확한 원문 복원 뒤 새 Review/Confirm으로 실행34와 외부 bytes/mode/inode/mtime 보존을 확인했다.
- 기존 scalar 입력 native/guard/API와 직전 helper 관측 native/guard를 회귀로 확인했다. 새 package 구조/probe/UI와 전체 ZIP 추출/hash/probe·유실 응답·늦은 입력·독립 창·실패 수명을 검사했다.

내부 request-local joint compiler 문맥만 추가했다. 각 함수의 원래 명시 본문/선언 계획을 동일하게 재사용하고 선택된 새 공개 계약/import를 함께 컴파일한다. native header/body는 모든 행의 원래 source 기준 검증이 끝날 때까지 staging하지 않는다. 같은 소스의 최종 결과는 byte 동일해야 한다. 저장 뒤 발견/후속 Save는 원래 scalar 입력 전환과 캡처한 function/body/header hash 및 정확한 signature/import delta를 인증한다. C# 텍스트 변환·추측·중간 checkpoint 쓰기는 없다.

기존 version3 receipt와 source/read240·member64·소유권/권한·Review/Confirm·최종 CAS를 유지했다. UI/layout·C# 생성기·등록 loader·외부 body 관측·private/whole/override 보호는 변경하지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 21단계 중 실패 2건은 모두 첫 제품 검증에서 기존 callee+consumer 금지 조건이 저장 후 Review와 후속 metadata Save를 거절한 결과다. 순수 graph 발견 진단으로 원인을 확인했고 캡처된 소스/정확한 헤더 delta 인증을 연결한 뒤 해당 UI/API 및 guard 변조 검사를 다시 통과했다. 최초 로그와 수정 전후 진단을 보존했다.

첫 최종 실행에서는 31단계 통과 뒤 CRLF 경합의 Save 발행 관측이 Ready 상태에서 시간 초과됐다. applySlots 요청은 없었고 입력 두 개와 checkpoint를 보존했다. 제품은 변경하지 않고 해당 모드만 실제 trusted 클릭/요청을 관측하도록 보완했다. 요청과 trusted 클릭이 모두 없는 미전달 UI 동작만 한 번 다시 시도할 수 있다. 보호 assertion은 유지한다. 변경된 경합 검사는 새로 통과했다. 실제 trusted 클릭은 1회였고, 입력 기준 거절 메시지와 두 입력·checkpoint 보존을 확인했다.

같은 제품·SDK/nuget·LF/CRLF·Python 의존성 및 변경되지 않은 실행 분기를 봉인 archive/hash와 대조해 15개 통과 검사만 재사용했다. SDK/제품 drift 거절도 검사하며 실패 단계와 모든 build/package/restore는 새로 수행했다. 이 결과는 신규26·재사용15·합계41이며 최초 실패를 최종 통과로 바꾸지 않았다.

직전 intact package `d2f0f488634c2e01b1c7c96442752949bce3a04c`의 전체 파일/hash를 별도로 추출했다. 원래 실행85는 유효하며 새 공동 import Save는 거절하고 입력·checkpoint·외부 원문/권한을 보존한다. 직전 reader의 새 pending 후보 순수 guard 수용은 `True`였다. 이 진단을 이전 전체 UI의 cold/Review/Confirm 교환 완료로 확대하지 않는다. 같은 세대 authoring/runtime을 사용하며 자동 migration/downgrade나 구 Reference parser 변경은 없다.

Linux 실제 .NET/portable 실행·Chromium 자동화다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 검증하지 않았다. 과거 간헐 초기 빈 화면의 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 0268361d99455b85d87e9a183b1338e6476b22c6 | e7ce3661f090cead37dfba11088d72d89a3917d75e1799e2548ffb8b8cd587d8 | 54138304 |
| rollback | d2f0f488634c2e01b1c7c96442752949bce3a04c | 24bb1710d9415e7e4f705e96ba556605f19307beab4c1c0f9f816501f387570f | 54132868 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/719c50aaa8214da886385b17fca1b983.json` · evidence SHA256 `8d9f7345db36d16f60f96501c9d6e10ba1fb4bae23baee6f9a8f9e8124fcad0a`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/bdbde9c2af4c4019af3ec21d44734a34.json` · evidence SHA256 `f488f1a99e2d5022f2c57cd2973d806a48d506afee9ca4d3f8984504b338eab6`.
첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/821fae269dcc4b1e8eae5dc03b6ff57b.json` · evidence SHA256 `e985e78d8f592459ffb9e79f5ee470ee38b3baf19748611a587ba55d112c2c99`. 재사용 source는 `364236c762e71aa99e2a9a4448b0cd0669970cbf`이며 native-chain-reuse.json에 정규화 명령·검사별 원본과 의존성 대조를 보존했다.
두 package와 개발·첫 최종 실패·최종 evidence archive hash를 재확인했다. 이번 등록 소유 임시물과 기존 latest/직전 정상 rollback 교대만 정리했으며 원본 checkout·과거 증거는 보존했다. 디스크 여유 24401428480bytes(22.73GiB)다.

이 명시 scalar 입력·선택 native import 호출 한 흐름을 닫는다. 지원 범위는 직접 소유 동기 함수2~8개·함수당 단일 C# target·scalar 입력 계획·ordinary Blueprint caller다. 역할·반환·고급 타입의 실제 호출 계약 변경 결합과 private/whole/상속·override 문맥은 이번 완료로 포함하지 않으며 기존 거절 경계를 유지한다. 구 reader의 전체 UI 교환, 실제 기기·전체 UI 및 초기 빈 화면 원인은 위 잔여로 남긴다. main은 사용자 검토/merge에 남긴다.
