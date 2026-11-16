# 선택 C# import 함수의 정보 참조 반환 검증

게시본 `867e001d90f82e6d82f3ebb9395bdab8027a938c`와 이전 증거를 보존하고 runtime `f7672403c7b3d967a726cfdb1e8b08405e077540`의 [참조 반환 공동 저장](V666_NATIVE_REFERENCE_RETURN.md)을 **신규47·재사용0·실패0**으로 검증했다. LF26·CRLF13·새 패키지/전체 ZIP 복원8이다. Linux 실제 .NET 실행과 Chromium 자동화이며 물리 기기/전체 UI 검증과 구분한다.

- Main→선택 A→선택 B의 원래70을 보존했다. 두 scalar 반환을 같은 정보별 readonly 참조 struct의 일차원 배열로 명시 전환했다. scalar 입력int·public amount·nativeAmount·인자 수/순서/값 역할·Main ABI·import alias는 유지했다. 네 명시 선택은 세 고유 source의 원래 hash·선언과 최종 원문이 일치할 때만 결합됐고 역순도 같은 후보였다.
- B의 직접 작성한 C#이 실제 ObjectModel 인스턴스 둘을 만들고 정확한 계약으로 Bind해 반환했다. A는 반환된 같은 handle/셀의 값42→73을 checked Read/Set으로 바꾸고 같은 배열을 Main에 반환했다. Main에서 원래 Target/Owner·carrier 사본·셀73·둘째 셀1·서로 다른 두 객체와 배열 길이/순서를 확인했다. carrier를 보유한 caller의 GC 후에도 같은 실제 객체를 관측했다. null·빈 배열·default/unbound 반환을 자동 생성/정규화하지 않았다. 단일 참조 반환도 원래 scalar 입력/native 이름·default와 실제 셀을 유지하며73을 실행했다.
- 함수별 원본 source scope·원소 타입 proof·기존 등록 import receipt/read set을 독립적으로 검증했다. 누락/교차 scope/type/등록 관측·값 proof로 위장한 참조 key·배열 key 위장·누락 caller·stale/상충 본문·잘못된 C#을 쓰기 없이 거절했다. capture 뒤 재서명한 배열→단일 선언·native 이름/import alias 변조·빠진 타입/등록 read도 거절했다. 입출력 혼합과 jagged 반환은 기존 지원 밖 경계로 유지하며 새 필수 조합을 추가하지 않았다.
- 원래 참조/여러 개 반환 선택기와 C# 편집기로460px 카드·420px 상세창, native 인자 이름, 취소·Undo/Redo·정상/역순 재개방·cold·쓰기 실패/재시도·응답 유실/중복 Save 방지·늦은 이름/두 번째 Save·동일 namespace 프로젝트 격리와 stale form 거절을 확인했다. readonly 선언만 선택한 계약에 연결하고 C# 본문을 자동 변환하거나 CSS/배치를 변경하지 않았다.
- 한 Save 이후 owner/function 설명 저장에서도 두 함수의 증거와 세 본문을 유지했다. Review 뒤 Main·공유 A 본문·Leaf 정의가 바뀌면 최종 CAS 전체를 거절하고 peer text/checkpoint를 보존했다. 정확히 복원한 뒤 새 Review/Confirm으로73을 실행했다.
- 등록 외부 정보를 참조 반환하는 B에는 별도 원소 proof가 필요했다. A는 같은 실제 handle에 이미 적용된 소유 정보의 view를 직접 Bind했으며 자동 cast·ID lookup·provider 선택·새 권한은 없다. 빠진 외부 proof를 거절하고 외부 write가 없는 후보를 확인했다. cold Review/Confirm 뒤73을 실행하고 외부 bytes·inode·mode·mtime가 정확히 같았다.
- 이전 참조 입력 API/native/guard, 값 배열 반환 API/guard, 값 배열 입력 native, 공유 source guard·incremental scope를 수정본에서 새로 검사했다. 이제 지원되는 참조 반환과 이미 지원된 배열 입력을 거절한다고 가정하던 이전 API fixture는 현재 경계에 맞춰 고치고 혼합·jagged·proof 거절을 유지했다. 새 패키지 생성/구조/integrity/probe/UI, 전체 ZIP 복원/probe·응답 유실·늦은 입력·독립 창과 성공/실패 수명 검사도 모두 신규다.

제품 변경은 InformationFunctionNativeTypes의 원소 proof를 공유하는 참조 반환 판정, feature-authoring의 기존 readonly 반환 선언 연결과 해당 WebBundle size/hash뿐이다. 입력 판정·한 그룹의 전환 방향·원본 source/proof·미래 import 사전·명시 C# buffer·한 후보·Review/Confirm·최종 CAS를 유지한다. 새 schema/profile/receipt 필드, reference bridge/CLR 수명, 권한이나 자동 binding/변환은 없다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64/type64, 공개 override/외부 쓰기 금지·명시 async 전환 전 sync caller 오류도 유지한다.

개발13단계와 최종 동결본47단계의 증거는 별도다. 개발 검사 실패는 없었다. 추가 보조 설정 실패는 0건이다. 이전 온전한 패키지 `1169819cf96cb41c96a06f6e9649474ed3ead6b4`를 archive/file/hash/mode까지 확인해 한 번 추출하고 새 fixture의 원래70·완전한 참조 반환 후보 거절을 새로 재현했다. 같은 추출본으로 새 capture의 이전 guard 수용 결과 `False`도 확인했다. 구 세대 authoring/pending guard의 지원 경계이며 모든 기존 참조 ABI 실행이 불가능하다는 뜻은 아니다. 더 오래된 Reference parser·새/구 reader 전체 UI 교환과 자동 migration/downgrade는 별도 범위다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | f7672403c7b3d967a726cfdb1e8b08405e077540 | 51bda1cc1d604e2cfc924906d6c2b077cce3bcc3905c2243edd53eb280d276d3 | 54145737 |
| rollback | 1169819cf96cb41c96a06f6e9649474ed3ead6b4 | 0be4c648b6da03250bd3ee534c45895e15b4d16b6b95afe2138ff9ef2c6d8fb6 | 54149180 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/83b6044dc580425b90255d6f4450f60e.json` · evidence SHA256 `406046d992b92d41c99bf2623369c18c29298dee20f4895f0d121d746b196a9c`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a5e3023fa8914374ae41bdad2a81c49e.json` · evidence SHA256 `21b0a83f1df1cbe99a6838a2e0c136a34b07c01cb1b7c3f4258b339a53cbcce0`.
두 패키지와 두 evidence hash를 재확인했다. 이번 인증된 임시물과 기존 두 세대 package 교대만 정리하고 원본 checkout·867e001 게시본·이전 증거를 보존했다. 이전 미인증 IPC의 `/tmp/cv-5xgaibtx`는 그대로 남겼다. 디스크 여유 24284049408bytes(22.62GiB)다.

이번 유한 흐름은 단일/일차원 참조 반환과 원래 scalar 값 입력이다. 입출력 혼합·다른 opaque 문맥을 완료로 세지 않으며 모든 타입/문맥 조합으로 백로그를 늘리지 않는다. 정보별 struct·종류 enum·모듈 interface 의미를 유지한다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이고 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
