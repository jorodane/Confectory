# 선택 C# import 함수의 정보 배열 반환 검증

게시본 `3a910171ba73abd2fbcc0de0b2f2c1367b48124a`를 보존하고, runtime `327ab490e995fca9533047469840c161b7c3272f`의 [배열 반환 공동 저장](V666_NATIVE_RETURN_ARRAY.md)을 **신규47·재사용0·실패0**으로 검증했다. LF26·CRLF13·새 패키지/전체 ZIP 복원8이다. 개발 재현·fixture 실패·수정 후 재검사는 아래에서 구분한다.

- Main→선택 A→선택 B의 원래 scalar 반환을70으로 실행한 뒤 두 함수의 반환만 정보별 구조체 일차원 배열로 선택했다. 두 구현과 Main의 본문을 직접 작성했고 공개 입력 amount/int·native 별칭 nativeAmount·값 역할·Main ABI와 import alias를 유지했다. 네 명시 선택의 세 고유 원본 hash/선언을 인증하고 역순에서도 같은 후보를 만들며 공유 A는 한 번만 반영됐다. 직접 생성한 두 원소의 순서·두 번째 값과 같은 배열 alias를 통한 첫 값 수정을 확인하고73을 실행했다.
- 원소 CLR 타입 key의 proof를 유지하며 공개/native 선언의 T[] cardinality를 별도로 검증했다. 배열 이름으로 바꾼 proof key·누락/교차 source/type proof·상충 A 본문·잘못된 C#·stale body·누락 caller를 쓰기 없이 거절했다. 재서명한 함수/헤더의 배열→단일 선언 변조도 거절했다. 참조/jagged 배열·배열 입력 전환·입력/반환 혼합 계획은 입력과 원래 checkpoint를 유지하며 이번 지원 밖으로 거절했다.
- 원래 반환 타입 선택기의 “여러 개”와 기존 C# 편집기를 사용했다. 460px 카드와 독립 창의 취소·Undo/Redo·정상/역순 재개방·미저장/저장 cold, 한 Save·쓰기 실패/재시도·응답 유실·늦은 이름/두 번째 Save·프로젝트 전환과 stale form 거절을 확인했다. 배열 반환에도 원래 C# 인자 이름을 표시하고 readonly 인자 draft가 덮지 않게 했다. DOM/CSS·카드 배치와 직접 작성한 C# 본문을 유지했다.
- 후속 owner/function 설명 Save에서 원소 타입·함수별 source 증거와 세 본문을 유지했다. Review 뒤 Main, 공유 A 본문 또는 Payload 정의 변경 시 Confirm 전체가 차단되고 peer text/checkpoint가 보존됐다. 정확히 복원한 뒤 cold·새 Review/Confirm으로73을 실행했다.
- 첫 함수는 소유 Payload[], 둘째는 이미 등록된 External.Fields::Leaf[]를 반환하는 별도 경계도73으로 실행했다. 빠진 외부 원소 proof를 거절하고 후보에 외부 write를 넣지 않았다. cold·Review/Confirm 후 외부 파일 bytes·inode·mode·mtime가 동일했다.
- 기존 단일 값 반환의 native/guard·역순 재개방, nominal 입력 native/guard·공유 source guard·incremental scope, scalar 반환 import native/guard를 수정된 runtime에서 새로 검사했다. 새 패키지 생성/구조/probe/UI와 전체 ZIP file hash/추출/probe·응답 유실·후속 입력·독립 창, 반복 성공/실패 수명을 새로 검증했다.

제품 변경은 InformationFunctionNativeTypes의 반환 판정, feature-authoring의 기존 native 인자 보존 판정과 해당 WebBundle 리소스 size/hash뿐이다. 기존 single nominal 입력 판정은 그대로이며 새 반환 helper는 single 또는 한 단계의 값 배열만 인정한다. 각 함수의 원래 타입/소스 증거·미래 import 사전·명시 buffer·한 후보·Review/Confirm·최종 CAS를 유지한다. 원소 proof를 재사용하며 새 JSON flag·receipt 필드·schema 문법·권한·등록·객체/provider 선택을 만들지 않는다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64/type64, 정보별 struct·종류 enum·모듈 interface 및 명시 async 전환 전 sync caller 오류를 유지한다.

개발 기록은 19단계이며 실패1건을 보존했다. 최초 API fixture가 부정 사례마다 카탈로그를 다시 조회해 기존 16개 owner-edit basis 보관 한도를 넘긴 뒤 오래된 basis로 정상 Save를 시도했다. 실패한 checkpoint는 v1/변경0이었고, 정상 Save만 분리한 진단은 통과했다. 제품의 한도·동시 변경 보호를 바꾸지 않고 fixture가 하나의 원래 카탈로그와 basis를 사용하도록 수정한 뒤 API 전체를 새로 통과시켰다. 원래 실패·진단·재검사 기록은 분리했고 최종 위47단계는 수정된 fixture/동결 source에서 모두 새로 통과했다. 보조 스크립트 준비/상태 출력 오류 3건도 별도 진단에 남기며 제품 검사 실패로 혼합하지 않는다.

온전한 이전 패키지 `ae0c9cdffd2d0eb8c0ab1e53d65b34a5054b4387`를 모든 file/hash/mode와 함께 별도 추출했다. 원래70 실행과 새 배열 반환 계획의 planner 거절, Save 전 기존 UI가 nativeAmount 대신 공개 amount를 표시하는 재현을 확인했다. 이 이전 UI 재현은 본문 Save 전에 끝나며 원본을 쓰지 않는다. 새 capture의 이전 pending guard 수용 결과는 `False`였다. 기존 배열 ABI 실행 전체의 비호환으로 일반화하지 않고, 새 전환/초안 guard 기능은 같은 세대 도구를 사용한다. 구 Reference parser·구 reader 전체 UI cold/Review/Confirm 교환과 자동 migration/downgrade는 별도 잔여다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 327ab490e995fca9533047469840c161b7c3272f | ef9e2b57e8c022cf55d11336181dd9a82872f1d11e2b5eecd8ea486bc9679583 | 54147624 |
| rollback | ae0c9cdffd2d0eb8c0ab1e53d65b34a5054b4387 | 85adaa7ef8508ec519a61dcbfcc87a646a1f10a02cbe6160c97bda125389d6a0 | 54146288 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/945579175df345e38f87702e4a6b1632.json` · evidence SHA256 `bd726e82857323c46da6745006dec4e34e51700d6533e36d56068fc1eaa49b6e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/8c1b02daedb64b6fb0c9807a1b627a08.json` · evidence SHA256 `fa6560365c5b7b9af02b479f4c942a4ca6bf7cde43016efd233dc379082e37ee`.
두 패키지와 두 evidence archive hash를 재확인했다. 인증된 이번 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·3a91017 게시본·기존 증거를 보존했다. 이전 단위의 미인증 IPC 때문에 보관한 `/tmp/cv-5xgaibtx`는 그대로 두며 이번 정리 완료와 혼동하지 않는다. 디스크 여유 24313511936bytes(22.64GiB)다.

이번 실제 반환은 정보별 구조체 일차원 값 배열이다. 참조 배열·배열 입력·혼합/다른 역할·jagged·async·private/whole 결합과 모든 enum/interface 반환 조합을 완료로 분류하지 않는다. override 공개 계약 구조 변경 금지·외부 쓰기 권한은 그대로다. Linux 실제 .NET/portable 실행과 Chromium 자동화가 검증 범위이며 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. 초기 빈 화면 원인은 미확정이며 main은 사용자 검토/merge에 남긴다.
