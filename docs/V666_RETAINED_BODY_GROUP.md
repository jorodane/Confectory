# retained C# 문맥·일반 C# 본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 한 정보 창·한 Save를 기존 retained root 문맥에
연결한다. [whole/native 공동 저장](V666_WHOLE_NATIVE_BODIES.md)의 다음 단위이며,
[기존 retained 명시 대응](V666_NATIVE_RETAINED.md)과 원래 출력/caller 선택창을 재사용한다.
게시 `ab73df3ef9a893e513a7f76e305e9c08de25d3c3`에서 두 단일 계획과 실행40은 유효하나
공동 후보만 거절되는 것을 재현했다. 새로운 타입/문맥 조합을 계속 추가하는 작업이 아니다.

이번 사용자 흐름은 한 원래 root C# 문맥과 독립 code/helper·ref alias·정확한 local이 남은
직렬 그래프, 다른 일반 native C# 본문을 함께 명시 편집하는 것이다. 함수 2~8개·함수당
직접 소유 구현/target 하나와 기존 64-member/240-source 예산을 유지한다. 공개/native
계약·인자명·타입·순서·역할·반환·async/공개 실행·override를 바꾸지 않는다. selected
구현의 copy/상속/import·여러 native 문맥이나 private 노드 자체의 ABI 변경은 별도 계획이다.

retained 본문 출력은 기존 UI에서 각 원래 출력에 동일한 출력을 명시 대응해야 한다.
그 창이 보내는 원래 caller 계획도 기존 입력/출력 identity·빈 disconnect만 허용한다.
전체 원래 hash/graph/node/binding·컴파일 검증은 기존 단일 closure가 권위다. source-only
저장에서 다른 소비자 재연결이나 출력 해제·C# 자동 변환을 추측하지 않는다. 행 순서와
무관한 한 후보/CAS를 만들며 실제 선택한 context record와 native 본문만 바뀐다.

원래 retained root/output/binding 검증을 모두 수행한 뒤, 계약·native 선언·출력 대응이
그대로이고 유일한 그래프 차이가 누락된 출력의 null exit 정규화이면 원래 그래프를 쓴다.
빈 `exits`를 `return: null`로 불필요하게 바꾸지 않으며 배치·entry·경로·locals/alias를
보존한다. 실제 ABI 변경·writer 교체/연결 계획에는 원래 처리와 계약을 유지한다.
독립 code/helper record는 write member가 아니며 bytes·mtime를 보존하고 원래 readGuards로
Review/Confirm의 최종 CAS까지 보호한다. 변환 뒤 미등록 원래 `.csbody`는 새 read 대상으로
주장하지 않고 쓰지 않으며 byte 보존을 따로 검사한다.

이미 있는 version3 `nativeBodyContexts`·readGuards와 쓰기 전 후보 검증을 재사용한다.
새 저장 문법·receipt version·권한을 만들지 않는다. cold와 정보/함수 표시 Save, 후속 명시
본문 Save는 원래 plan/source/flow/read hash를 유지한다. 사용자가 다시 쓴 text만 갱신하고
독립 graph/helper/alias나 물리 원본을 새로운 기준으로 받아들이지 않는다. 독립 helper와
선택 node·graph가 Review 뒤 바뀌면 전체 Confirm을 차단하고 정확한 원문 복원 후 새
Review로 계속한다. 다른 source/구조 편집을 끼워 넣으면 입력을 보존하며 거절한다.

종료 기준은 이 한 흐름의 원래 UI 정상·취소·출력/caller 명시 대응·Undo/Redo·실패/재시도·
cold·응답 유실·반복·프로젝트 전환·늦은 입력/후속 Save·Review 취소/Confirm과 독립
원본 경합이다. 두 본문의 사용자가 작성한 뺄셈으로 실제 실행40→20을 검사한다.
LF/CRLF 격리 restore/build, 새 package 및 전체 추출본을 검증하고 개발/신규/재사용 결과를
구분한다. 기존 pure whole/native 및 guard·등록 helper·실제 retained ABI 변경·단일 whole
전환은 회귀로 포함한다. 가능한 모든 타입 조합을 새 완료 조건으로 늘리지 않는다.

같은 게시 세대의 authoring/runtime을 사용한다. 직전 reader의 새 retained pending scope
수용을 보장하지 않으며 자동 migration/downgrade를 하지 않는다. 구 Reference parser 제약은
유지한다. Linux 엔진/portable 실행·Chromium 자동화와 실제 Windows/WebView2·물리 기기·
IME/GPU/audio·전체 UI 검증을 구분한다. 과거 초기 빈 화면 원인은 미확정이다.

남은 유한 갈래는 (1) private/독립 node 자체 명시 계획 결합, (2) 실제 계약 변경 callee/import·
등록 외부 관측 결합이다. 이번 root retained source-only 경로를 그 전체 완료로 표현하지
않는다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를
유지한다. 원본·latest/rollback·증거와 기존 정리 범위를 보존하고 main은 사용자 검토/merge에 남긴다.

이 retained/native 본문 공동 저장 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_RETAINED_BODY_GROUP.md)을 마쳤다.
