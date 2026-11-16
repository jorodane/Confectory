# 선택 C# import 함수의 정보 배열 입력 검증

게시본 `15f1d8298f35d949707693bc66c684eb26e82888`를 보존하고 runtime `1b4c92264b7f7d78be92b5570cfa50ee41cd3cc2`의 [배열 입력 공동 저장](V666_NATIVE_ARRAY_INPUT.md)을 **신규47·재사용0·실패0**으로 검증했다. LF26·CRLF13·새 패키지/전체 ZIP 복원8이다. 이전 빌드를 반복하는 대신 온전한 게시 패키지에서 기준 흐름을 새로 실행했고, 수정본 개발 검사와 최종 검증은 구분한다.

- Main→선택 A→선택 B의 원래70을 실행한 뒤 두 scalar 값 입력을 정보별 구조체 일차원 배열로 명시 선택했다. 반환int·공개 입력 amount·native 이름 nativeAmount·수/순서/값 역할·Main ABI·import alias를 유지했다. 네 선택의 세 원본 source hash/선언을 인증하고 역순에서도 같은 후보를 만들며 공유 A는 한 번만 합쳤다. Main이 직접 만든 배열을 A의 같은 alias로 수정한 뒤 B에 전달해73을 실행했다. Main에서 원래 배열의 첫 값71·둘째 값1·길이/순서를 확인했다.
- 원소 CLR 타입 key의 proof와 각 함수의 원래 source scope를 유지하고 공개/native 배열 선언을 따로 검증했다. 배열 이름으로 위장한 proof key·누락/교차 source/type proof·상충 본문·잘못된 C#·누락 caller·stale source를 쓰기 없이 거절했다. 재서명한 함수/헤더의 배열→단일 선언 변조도 거절했다. 참조/jagged 배열 및 입력/반환 혼합 계획은 원본과 checkpoint를 보존하며 이번 지원 밖으로 거절했다. 이는 새 필수 조합을 추가하는 것이 아니다.
- 원래 입력 타입 선택기의 “여러 개”와 기존 C# 편집기를 사용했다. 460px 카드와 독립 창의 취소·Undo/Redo·정상/역순 재개방·미저장/저장 cold, 한 Save·쓰기 실패/재시도·응답 유실·늦은 이름/두 번째 Save·동일 namespace 프로젝트 전환과 stale form 거절을 확인했다. 타입 변경 시 원래 native 인자 이름을 표시하고 readonly 인자 draft가 덮지 않게 했다. DOM/CSS와 기존 값/ref/out·추가/삭제·caller coupling 판정은 유지했다.
- 후속 owner/function 설명 Save에서 원소 타입·함수별 source 증거와 세 본문을 유지했다. Review 뒤 Main, 공유 A 본문 또는 Payload 정의가 바뀌면 Confirm 전체가 차단되고 peer text/checkpoint가 남았다. 정확히 복원한 뒤 cold·새 Review/Confirm으로73을 실행했다.
- 첫 함수는 소유 Payload[], 둘째는 이미 등록된 External.Fields::Leaf[]를 입력으로 사용했다. 원소 변환과 외부 배열 생성은 직접 작성한 C#이며 자동 변환하지 않는다. 빠진 외부 proof를 거절하고 후보에 외부 write가 없었다. cold·Review/Confirm 뒤73을 실행하고 외부 파일 bytes·inode·mode·mtime가 동일함을 확인했다.
- 기존 단일 struct 입력을 같은 C# 편집기로 전환하는 별도 회귀도 원래 native 이름과 Main의 값40을 유지하고73을 실행했다. 배열 입력의 같은 handle과 단일 struct의 값 복사를 구분했다. 기존 배열 반환 native/guard·역순 재개방, 기존 입력 native/guard·공유 source guard·incremental scope, scalar 반환 import native를 수정된 runtime에서 새로 검사했다. 새 패키지 생성/구조/probe/UI와 전체 ZIP hash/추출/probe·응답 유실·후속 입력·독립 창, 반복 성공/실패 수명을 새로 검증했다.

제품 변경은 InformationFunctionNativeTypes의 단일/vector 값 계약 판정, feature-authoring의 native 입력 이름·readonly 인자 판정, 해당 WebBundle 리소스 size/hash다. 반환 전환 판정은 같은 의미를 유지하며 입력에서 기존 원소 proof와 T[]를 연결한다. 수/이름/순서/값 역할·scalar 반환과 한 그룹의 전환 방향, 원래 타입/소스 증거·미래 import 사전·명시 buffer·한 후보·Review/Confirm·최종 CAS를 유지한다. 새 JSON flag·receipt 필드·schema 문법·권한·등록·배열/객체/provider 자동 생성은 없다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64/type64, 정보별 struct·종류 enum·모듈 interface 및 명시 async 전환 전 sync caller 오류도 유지한다.

개발14단계·실패0의 기록을 보관했다. 동결 전 패키지 보조 사전검사1건은 manifest의 디렉터리를 일반 파일로 가정해 중단됐고, 확인한2755파일·158디렉터리의 종류/모드는 모두 원본과 같았다. 보조 검사만 명시 directory flag에 맞게 고쳐 종류/해시/모드를 검증했다. source·권한·추출본을 변경하거나 기준 실행을 중복하지 않았고 최초 오류/수정 근거를 별도 보존했다. 이전 패키지 `327ab490e995fca9533047469840c161b7c3272f`를 전체 file/hash/mode와 함께 한 번 추출해 원래70·새 배열 입력 계획 거절·Save 전 native 인자 이름 유실을 새로 재현했다. 이 UI 재현은 checkpoint/원본을 쓰지 않았으며 이전 빌드를 다시 실행하지 않았다. 같은 추출본의 원래 file/hash/mode와 archive hash를 확인하고 새 capture의 이전 pending guard 수용 결과 `False`를 별도 측정했다. 기존 배열 ABI 전체의 실행 불가로 일반화하지 않는다. 새 전환/초안 guard는 같은 세대 도구가 필요하며 구 Reference parser·구 reader 전체 UI cold/Review/Confirm 교환과 자동 migration/downgrade는 별도 범위다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 1b4c92264b7f7d78be92b5570cfa50ee41cd3cc2 | f50718ed7e9772f16ef353a186945c11345accfbc60f1ba95babdd735880a92c | 54147154 |
| rollback | 327ab490e995fca9533047469840c161b7c3272f | ef9e2b57e8c022cf55d11336181dd9a82872f1d11e2b5eecd8ea486bc9679583 | 54147624 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/aad521c7b42e411a9fa68f76da43346d.json` · evidence SHA256 `d2ebfe6a49a63363dcc7a0dd4a7265616b2c0e8bb569ce9c7473150a6e4d1336`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/75ef6efbbf2d40c1acdd2c5159018e78.json` · evidence SHA256 `b57ec374be0d35672daa8f8810ec7a0d213d255735f8735cf8a75fcbebaedf9e`.
두 패키지와 두 evidence archive hash를 재확인했다. 인증된 이번 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·15f1d82 게시본·기존 증거를 보존했다. 이전 단위의 미인증 IPC 때문에 남긴 `/tmp/cv-5xgaibtx`는 그대로 보존하며 이번 정리 완료와 혼동하지 않는다. 디스크 여유 24304033792bytes(22.63GiB)다.

이번 실제 전환은 scalar 입력→정보 struct의 일차원 값 배열이며 기존 단일 값 흐름은 회귀로 확인했다. 참조 배열·입출력 혼합·기존 opaque 문맥과 모든 enum/interface 조합을 완료로 세지 않는다. jagged 등 새 조합을 필수 백로그로 늘리지 않는다. override 공개 계약 구조 변경 금지·외부 쓰기 권한은 그대로다. Linux 실제 .NET/portable 실행과 Chromium 자동화가 검증 범위이며 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면 원인은 미확정이며 main은 사용자 검토/merge에 남긴다.
