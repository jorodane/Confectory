# 선택 C# import 함수의 입출력 혼합 전환 검증

게시본 `d05c495a356209a415363f3dc4d5cd1a1f42bdcb`와 이전 증거를 보존하고 runtime `f2e72bacdcd800c6554c294981de4a98481f93c1`의 [혼합 IO 공동 저장](V666_NATIVE_IO_MIXED.md)을 **신규48·재사용0·실패0**으로 검증했다. LF27·CRLF13·새 패키지/전체 ZIP 복원8이다. Linux 실제 .NET 실행과 Chromium 자동화이며 물리 기기/전체 UI 검증과 구분한다.

- Main→선택 A→선택 B의 원래70을 보존했다. A의 참조 배열 반환 전환과 B의 참조 배열 입력 전환을 네 명시 선택·세 고유 C# source로 한 Save에 결합했다. A가 실제 객체 둘을 명시 Bind해 만든 같은 배열을 B가 받아 셀40→71을 바꾸고73을 반환했다. A가 같은 셀에73을 기록해 배열을 Main에 반환했다. Target/Owner·셀·배열 동일성·순서와 둘째 셀1을 실행으로 확인했다.
- 반대 방향의 A 입력/B 반환도 원래 상세창·본문 편집으로 검증했다. 두 경계의 독립적인 실제 객체를 명시적으로 읽고 썼으며 Target을 병합하거나 자동 변환하지 않았다. A의 입력·반환 동시 변경과 B 반환도 한 Save·cold·Review/Confirm으로73을 실행했다. 별도 API로 동시 계약의 후속 owner/function 설명 Save와 Review 뒤 원본 충돌도 검증했다. 받은 원래 배열을 Main에 그대로 반환하고 실제 Target/셀·배열 동일성을 확인했다. null·빈 배열·default/unbound 경계는 명시 C#이 그대로 전달했다.
- 단일 정보 값의 A 반환/B 입력에서는 B의 struct 값 복사가 A의 원래40을 바꾸지 않음을 확인하고, A가 명시적으로 작성한73 반환을 Main이 소비했다. 모든 흐름에서 public amount/nativeAmount·인자 수/순서/값 역할·변경하지 않은 입출력·Main ABI·import alias와 원본 bytes를 유지했다. 정보별 struct·종류 enum·모듈 interface 의미, sync caller의 명시 async 전환 전 오류와 override/비소유 쓰기 제한도 유지한다.
- 각 함수의 원래 before/after·pin mapping·원소 타입 proof·등록 import receipt/read set을 독립 검증했다. 같은 source의 두 scope가 원래 hash·native signature·최종 본문에서 정확히 일치할 때만 한 번 반영했고 역순에서도 같은 후보였다. 빠진/교차 증거·상충 본문·stale source·잘못된 C#·누락 caller·새 역할/핀·잘못된 input map·jagged 전환을 쓰기 없이 거절했다. capture 뒤 등록/type read 누락·재서명한 native 이름/import·배열 선언 변조도 거절했다.
- 원래460px 카드/420px 상세창, IO 선택기와 C# 편집기로 취소·Undo/Redo·정상/역순 재개방·미저장/저장 cold·쓰기 실패/재시도·응답 유실/중복 Save 방지·늦은 이름/두 번째 Save·동일 namespace 프로젝트 격리·stale form 거절을 확인했다. 입력·반환 동시 선택의 readonly 선언도 native 인자 이름을 보존하며 C# 본문은 자동 변환하지 않았다. CSS/배치를 변경하지 않았다.
- 후속 owner/function 설명 Save에서도 서로 다른 방향의 두 계약과 모든 증거·세 본문을 유지했다. Review 뒤 Main·공유 A 본문·Leaf 정의가 바뀌면 최종 CAS 전체를 거절하고 peer text/checkpoint를 보존했다. 정확한 복원 뒤 새 Review/Confirm으로73을 실행했다.
- 소유 정보 반환/등록 외부 정보 입력은 같은 실제 handle에 다른 적용 정보의 view를 직접 Bind했다. 별도 원소 proof가 필요하고 외부 write나 새 권한은 없었다. cold Review/Confirm 뒤73을 실행하고 외부 bytes·inode·mode·mtime가 정확히 같았다. 이미 지원하는 기존 단일 방향 참조 입력/반환 API, 값 배열 반환 guard·입력 native·공유 source guard·incremental scope를 수정본에서 새로 검사했다. 이전 API fixture의 blanket mixed 거절 가정은 새 지원에 맞춰 제거했으며 실제 invalid source/proof/구조 경계는 유지했다.

제품 변경은 InformationFunctionNativeTypes의 함수별 입력·반환/동시 타입 전환 판정과 그룹·cold 재검증, feature-authoring의 동시 입력·반환 readonly 선언 연결, 해당 WebBundle size/hash뿐이다. 기존 미래 public/type 사전·canonical source·명시 buffer·한 후보·Review/Confirm·최종 CAS를 사용한다. 새 JSON flag·schema/profile/receipt 필드·reference bridge/CLR 수명·권한·자동 binding/객체 생성/변환은 없다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64/type64와 인자 수·이름·순서·역할의 기존 제한을 유지한다.

개발17단계와 최종 동결본48단계는 별도 증거다. 개발 중 실패·정정 근거는 {"dev-native-io-mixed-both-api": "Negative fixture selected B, whose input remained scalar in the simultaneous case; replacing its already-correct amount identity map was a valid no-op and the product correctly checkpointed it without source writes. Preserve this accepted request, checkpoint and failure log. Select the actual input-changing function A for the unmapped-input rejection and rerun only that API with the corrected fixture, followed by the not-yet-run value UI."}로 보존했다. 추가 보조 설정 실패는 0건이다. 이전 온전한 패키지 `f7672403c7b3d967a726cfdb1e8b08405e077540`를 archive/file/hash/mode까지 확인해 한 번 추출하고 새 fixture의 원래70·완전한 혼합 후보 거절을 새로 재현했다. 같은 추출본으로 새 capture의 이전 pending guard 수용 결과 `False`도 확인했다. 구 세대 authoring/pending guard의 범위이며 모든 기존 ABI 실행이 불가능하다는 뜻은 아니다. 구 Reference parser·새/구 reader 전체 UI 교환과 자동 migration/downgrade는 별도 범위다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | f2e72bacdcd800c6554c294981de4a98481f93c1 | 6d85a7d00a96eacc8f8e617e0f9a548134f311a611a3e181ed2c7ad723abecd7 | 54145011 |
| rollback | f7672403c7b3d967a726cfdb1e8b08405e077540 | 51bda1cc1d604e2cfc924906d6c2b077cce3bcc3905c2243edd53eb280d276d3 | 54145737 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/53e45b2d53cd406694ed61223d32f4a4.json` · evidence SHA256 `a3604c0ccccddc25eb6b0762846ab85984c76da230b01f5fddf32d740d4754d8`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/cec6fc3931d649adbeaec6149cdbfaba.json` · evidence SHA256 `8b5dc2cd2cf1143753f7a0e601c4f62cc7be1c3c589f2bbd7ead2a25c4b5dbc7`.
두 패키지와 두 evidence hash를 재확인했다. 이번 인증된 임시물과 기존 두 세대 package 교대만 정리하고 원본 checkout·d05c495 게시본·이전 증거를 보존했다. 이전 미인증 IPC의 `/tmp/cv-5xgaibtx`는 그대로 남겼다. 디스크 여유 24273645568bytes(22.61GiB)다.

이번 유한 종료 기준은 두 방향의 혼합, 한 함수의 입력·반환 동시 선택, 단일 값 복사와 기존 등록 view의 실제 저장/실행이다. 모든 타입/문맥 조합으로 백로그를 늘리지 않는다. 새 역할·핀 구조·nominal→다른 nominal 변환·jagged·새 opaque/private/whole 문맥을 완료로 세지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이고 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
