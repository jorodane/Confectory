# 기존 scalar 속성·native 계약 공동 저장 검증

제품 동결 `54c342d880ec909336691315ea1dcf5ecb5c9972`의 [지원 범위](V666_NATIVE_SCHEMA_CONTRACTS.md)를 최종 **신규 50단계·재사용0·실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet와 기존 seed 복원,
Release/MCP·빈 cache의 실제 Linux 엔진, 새 Windows 교차 package·구조/무결성과 ZIP 전체 복원을 검사했다.
개발 단계와 최종 단계를 합산하지 않는다.

- 게시 aaf9ef53에서 단독 scalar 필드 타입 편집과 native ABI/body/caller·정보 설명/아이콘은 각각 유효하나
  결합 후보와 원래 UI Save는 거절됨을 재현했다. 원본·다섯 입력·checkpoint를 보존했고 Confirm하지 않았다.
- 수정 뒤 기존 Scale long→double과 정보 설명/아이콘, 두 native out·반환/본문/caller가 한 Save로 결합된다.
  행 순서와 무관한 후보와 원래 hash를 확인했다. 필드 편집 전후의 native/caller 변경 bytes가 같다.
  기본값7과 Power의64비트 기본값·다른 필드/참조·비선택 C# 원문을 유지하고 실제 실행 결과40을 확인했다.
- 기존 nativeType과 현재 scalar definition/sources-null 형식의 write 후보는 같다.
  현재 타입 목록 조회가 추가 관측한 기존 등록 Leaf 파일은 읽기 증거에서 제거하지 않았다.
  같은 계약의 본문 그룹과 scalar 입력 ABI 그룹도 기존 원본 읽기 범위를 유지한다.
- stale/foreign/중첩/중복/지원 밖 속성 정의·부적합 기본값·불완전한 ABI 계획을 전체 거절했다.
  같은 계약에서 본문 편집을 생략하여 원문을 유지하는 기존 유효 경로는 보존한다.
  기존 속성 표시/정의 편집과 사용 중 속성의 정상 보호, native 후속 표시 저장의 읽기 범위를 회귀 검사했다.
- 원래460px 기본 정보 창의 취소·Undo/Redo·미저장/저장 cold·checkpoint 실패/재시도·응답 유실·반복과
  owner 경합·지연 Save 뒤 늦은 설명의 후속 저장/직전 경합을 검사했다.
  Save/Review/Confirm 사이 helper·native 선언/본문·caller 변경은 입력·checkpoint·peer 원문을 보존하며 거절된다.
  정확히 복원한 뒤 새 Review/Confirm과 실행, 비선택 C# inode/mode/mtime 보존을 확인했다.
- 새 package·전체 추출본에서 UI Save/Confirm·응답 유실·늦은 입력·실행과 실패 정리 수명을 검사했다.

개발 기록은 총 27단계다. 초기 검사 실패5건은 기존 UI 경계와 검사 기대값 문제를 구별해 보관했다.
첫째는 기존 속성 타입 Undo가 BODY로 포커스를 옮겨 연속 Redo를 전달하지 못한 실제 UI 경계다.
버튼을 명시한 Undo/Redo의 입력 보존은 검증했지만 자동 포커스 복원은 별도 잔여로 유지한다. 둘째는 실제 definition 셀을 legacy nativeType 키로 비교한 종료 검사다.
셋째는 현재 타입 목록의 추가 읽기 관측까지 legacy 결과와 같아야 한다고 비교한 검사,
넷째는 같은 계약의 본문 편집 생략에도 불완전한 ABI 교체의 거절을 기대한 검사다.
다섯째는 성공한 후속 설명 Save의 기대값을 상위 header 검사에 전달하지 않은 검사다.
각 실행 입력의 hash/원본과 당시 로그·관측 JSON, 수정 뒤 통과 결과를 보존했다. 이 단위의 C# 패치는 공동 저장 결합에 한정하며 타입 Undo의 포커스 복원은 완료로 세지 않는다.
첫 메모리 사전검사 차단은 빌드 시작 전의 자원 검사다. 검증 보관물37개의 해시/메타데이터를 확인하며 해당 읽기 캐시만 반환했고,
삭제·전역 캐시 변경·예산 축소 없이 같은 사전검사가 통과했다. 이후 결과와 별도 기록한다.
최종 단계는 동결 코드와 최종 검사에서 모두 새로 실행했으며 위 개발 검사 결과를 재사용하지 않았다.

과거 구 Reference reader 증거는 해시 확인한 재사용 자료이며 신규 단계에 포함하지 않는다.
새 문법/receipt 버전·자동 migration/downgrade를 추가하지 않았다. 같은 게시 세대의 저장·재편집·검토 기준이다.
시작 화면 전송8회 관측은 과거 간헐 빈 화면 원인 확정으로 세지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 54c342d880ec909336691315ea1dcf5ecb5c9972 | c70e509b3603ddd18a118efb0c82eb16673fec22abe898aef031f817f7ba6e46 | 54104531 |
| rollback | 4b152d523cd6e30fbb1eebd1f75f5b7f08cc26a2 | f2a043797a2d664ecef0262b099f70246c274fef245e8f4fea49a3ddca5b34cf | 54100646 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/d662a9c0be9148a9b3975cab4f190a93.json` · evidence SHA256 `0b0b4f7df1d9526523e931b770fd9f766b28c2f1f25c7dbecbaf463c7e6d5d70`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/f295855437f04a2aa76a8bccd94418f6.json` · evidence SHA256 `44a5bc0b46d3b7f2e9eecea5ad3d15f4d9077ec096f282db974b10b734cd31ef`.
보관 package2개와 증거 SHA를 확인했다. 기존 latest/직전 정상 rollback 교대와 이번 소유 임시물 정리만 적용했다.
원래 checkout/main·비관리 자료·과거 증거는 보존한다. 퇴역한 세 번째 관리 ZIP의 전체 보존을 주장하지 않는다.
여유 24789860352bytes(23.09GiB)다.

남은 다른 복합 계약·속성 생성/삭제·구조 편집, opaque/private 명시 C# 계획,
선택 native callee 의존성과 기존 import/등록 외부 원본 결합은 같은 고정7/8행에 유지한다.
원래 사용자 조작의 정상/거절·입력/원문 보존·실제 저장/실행 증거를 종료 기준으로 삼고 optional 타입/문맥 조합을 늘리지 않는다.
M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 struct·종류 enum·모듈 interface·소유권·권한·override·authored layout·최종 CAS를 유지한다.
이번 새 조합의 독립 정보 창 UI를 별도 재검증하지 않았다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio 및 전체 UI 전수 검증은 수행하지 않았다.
초기 빈 화면 원인은 미확정이며 새 credential/grant·과금·main 변경은 없다.
