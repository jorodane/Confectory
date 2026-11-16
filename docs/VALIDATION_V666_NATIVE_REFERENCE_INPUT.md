# 선택 C# import 함수의 정보 참조 배열 입력 검증

게시본 `fcca1997fb26bcc0f027edcf67be470ae561d6ba`와 이전 증거를 보존하고 runtime `1169819cf96cb41c96a06f6e9649474ed3ead6b4`의 [참조 입력 공동 저장](V666_NATIVE_REFERENCE_INPUT.md)을 **신규47·재사용0·실패0**으로 검증했다. LF26·CRLF13·새 패키지/전체 ZIP 복원8이다. Linux 실제 .NET 실행과 Chromium 자동화이며 물리 기기/전체 UI 검증으로 세지 않는다.

- Main→선택 A→선택 B의 원래70을 실행했다. 두 scalar 입력을 같은 정보별 readonly 참조 struct 배열로 명시 전환하고 반환int·public amount·nativeAmount·인자 수/순서/값 역할·Main ABI·import alias를 유지했다. 네 명시 선택은 세 고유 source의 원래 hash와 최종 원문이 일치할 때만 결합되고 역순에서도 같은 후보였다.
- 직접 작성한 Main C#이 ObjectModel 실제 인스턴스 둘을 만들고 정확한 정보 계약으로 Bind했다. A는 checked Read/Set으로 첫 셀40→71을 바꾸고 같은 배열을 B에 전달했다. B는 같은 실제 handle에서 값을 읽어73을 반환했다. Main은 두 Target·Owner·원래 셀·배열 길이/순서와 둘째 셀1을 확인했다. null·빈 배열·default/unbound carrier도 직접 전달해 자동 객체 생성/정규화가 없음을 확인했다. 단일 참조 입력도 원래 native 이름·실제 객체 alias·default를 유지하며73을 실행했다.
- 각 함수의 source scope·기존 등록 import receipt와 원소 CLR 타입 proof를 요구하고 배열 여부를 공개/native 선언·captured source에 결합했다. 누락/교차 scope/type/등록 관측·참조 key에 값 proof 대입·배열 key 위장·누락 caller·stale/상충 본문·잘못된 C#을 거절했다. capture 뒤 재서명한 배열→단일 선언, native 이름/import alias 변조와 빠진 read 관측도 쓰기 없이 거절했다. 참조 반환·입출력 혼합·jagged 입력은 기존 지원 밖 경계로 유지했으며 새 필수 조합을 추가하지 않았다.
- 기존 참조/여러 개 입력 선택과 C# 편집기를 사용했다. 원래460px 카드/420px 상세창, 취소·Undo/Redo·정상/역순 본문 재개방·미저장/저장 cold·한 Save·checkpoint 쓰기 실패/재시도·응답 유실/중복 Save 방지·늦은 이름/두 번째 Save·프로젝트 격리/stale form 거절을 확인했다. UI 레이아웃/CSS는 변경하지 않았다.
- 후속 owner/function metadata Save에서도 두 함수의 proof/본문을 유지했다. Review 뒤 Main·공유 A 본문 또는 Leaf 정보 정의가 바뀌면 최종 CAS 전체를 거절하고 peer text/checkpoint를 보존했다. 정확히 복원한 뒤 새 Review/Confirm으로73을 실행했다.
- 등록 외부 정보의 참조 배열을 받는 B는 별도 원소 proof가 필요했다. 같은 실제 handle에 원래부터 적용된 다른 정보의 view는 사용자가 작성한 C#에서 명시 Bind했다. 자동 cast·ID lookup·provider 선택·새 접근 권한이 없다. 빠진 외부 proof를 거절하고 외부 write가 없는 후보를 확인했다. cold Review/Confirm 뒤73을 실행하고 외부 bytes·inode·mode·mtime가 정확히 같았다.
- 기존 값 배열 입력의 실제 UI/API/guard, 값 배열 반환 native/guard, 단일 nominal 입력 native, 공유 source guard와 incremental scope를 수정본에서 새로 검사했다. 예전 API의 참조 배열 입력 거절 검사는 이번 지원에 맞춰 제거하고 jagged·proof 거절을 유지했다. 새 패키지 생성/구조/integrity/probe/UI, 전체 ZIP 복원/probe·응답 유실·늦은 입력·독립 창과 성공/실패 수명 검사는 모두 신규다.

제품 변경은 InformationFunctionNativeTypes의 참조 입력·기존 등록 증거 허용 판정, feature-authoring의 기존 native 입력 선언 연결, 해당 WebBundle size/hash뿐이다. 반환 전환 판정·그룹의 단일 전환 방향·원래 source/proof·미래 import 사전·명시 C# buffer·한 후보·Review/Confirm·최종 CAS를 유지한다. 새 receipt/profile/schema 필드, runtime bridge/참조 수명, 권한이나 자동 binding/변환은 추가하지 않았다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64/type64와 공개 override/외부 쓰기 금지·명시 async 전환 전 sync caller 오류도 유지한다.

개발20단계 중 네 차례 진단 실패를 보존했다. 첫 fixture bytes 비교는 새 ObjectModel import 전 상위 모듈 snapshot을 참조해 잘못 실패했고, 실제 fixture 구성 후의 snapshot으로 비교 함수를 한정했다. 그다음 후보 거절은 실제 객체 생성/Read/Set import의 기존 dependencies 증거를 요청에서 빠뜨린 상태였다. 완전한 원래 등록 증거를 요청에 보관하고 nominal 그룹 분류기가 기존 dependencies 필드를 받도록 연결했다. 기존 dependency reader/receipt 검증을 그대로 유지하며 빠진/교차 증거는 계속 거절한다. 완전한 요청의 이전 패키지 거절과 수정본 수용을 새로 확인했다. 세 번째는 정상 Confirm에서 기존 nullable 경고를 오류로 처리해 의도적인 null 전달 C# fixture를 거절한 것이다. 해당 null 호출에 명시 null-forgiving 표기를 더했으며 runtime null 의미와 컴파일러 규칙은 유지했다. 실패/후보 진단을 보존하고 해당 검사부터 새로 실행했다. 네 번째는 UI 검사 선택자의 부분 문자열 Leaf가 Leaf2/LeafChild까지 일치한 strict-mode 오류로, 타입 선택 전에 중단됐다. 원래 title/정보 ID로 정확히 선택하도록 검사만 고치고 해당 UI부터 재실행했다. 이후 최종 동결본47단계는 전부 신규 통과했고 별도 검사 설정 실패는 없었다.

이전 온전한 패키지 `1b4c92264b7f7d78be92b5570cfa50ee41cd3cc2`를 archive/file/hash/mode까지 확인하고 한 번 추출해 새 fixture의 원래70·참조 입력 후보 거절을 새로 재현했다. 같은 추출본으로 현재 capture의 이전 guard 수용 결과 `False`도 확인했다. 이는 구 세대 authoring/pending guard의 지원 경계이며 기존 모든 참조 배열 실행을 거절한다는 뜻은 아니다. 더 오래된 Reference 이름을 모르는 parser·새/구 reader 전체 UI 교환과 자동 migration/downgrade는 별도 미지원 범위다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 1169819cf96cb41c96a06f6e9649474ed3ead6b4 | 0be4c648b6da03250bd3ee534c45895e15b4d16b6b95afe2138ff9ef2c6d8fb6 | 54149180 |
| rollback | 1b4c92264b7f7d78be92b5570cfa50ee41cd3cc2 | f50718ed7e9772f16ef353a186945c11345accfbc60f1ba95babdd735880a92c | 54147154 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/729916e457214230b9688533a1597b10.json` · evidence SHA256 `be58ba36696fd0b8b9910db96190ba5c40f2ed3bacac1e9a25b7ef2b0305b996`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/188054c9a91d480ca2087d348d29bb1a.json` · evidence SHA256 `dad26b0c3422e744f0fff43723ba4edc6a628c86e257bf3138e645b2e9bc57d8`.
두 패키지와 두 evidence hash를 재확인했다. 이번 인증된 임시물과 기존 두 세대 package 교대만 정리하고 기존 checkout·fcca199 게시본·원본/보관 증거를 보존했다. 이전 미인증 IPC의 `/tmp/cv-5xgaibtx`는 그대로 남겼다. 디스크 여유 24293785600bytes(22.63GiB)다.

이번 유한 흐름은 참조 배열 입력과 같은 proof 경로의 단일 참조 입력이다. 참조 반환·입출력 혼합·다른 opaque 문맥을 완료로 세지 않는다. 기존 정보별 struct·종류 enum·모듈 interface 의미를 유지하고 모든 조합으로 백로그를 늘리지 않는다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
