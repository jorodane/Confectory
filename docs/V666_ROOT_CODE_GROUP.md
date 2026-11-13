# 독립 root C# 노드와 일반 본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 다음 사용자 흐름은 직접 소유하는 일반 Blueprint의
독립 root C# 노드 본문·보조 함수와 다른 소유 함수의 일반 C# 본문을 한 정보 창에서
명시 편집해 한 Save로 보관하는 것이다. [private 코드 공동 저장](V666_PRIVATE_BODY_GROUP.md)
다음 단위이며, 노드 ABI와 공개/상위 구현 ABI를 구분한다. 정보별 struct·종류 enum·모듈
interface와 명시 async 전환 전 sync caller 오류는 유지한다.

이번 범위는 root implementationContext/forwardCallerStorage가 없는 기존 그래프다.
기존 whole/retained 문맥이 있으면 해당 원래 필수 본문·출력 계획을 계속 요구한다.
공개/상위 native 계약·노드의 타입/인자명/순서/ref/out/반환·graph/연결/배치/locals를 바꾸지
않는다. root 코드 자체가 void/out이고 상위 함수가 long인 서로 다른 ABI도 그대로다.
직접 소유 함수·구현/target 하나와 기존 함수 2~8·member64/source240 예산을 유지한다.
copy/상속·실제 계약 변경 callee/import·외부 관측의 결합을 암묵적으로 추가하지 않는다.

게시본에서 원래 root 코드 프로그램은 실행40이 유효했지만 정보 창의 코드 목록이 독립
root 노드를 제외했고 명시 root 계획은 저장되지 않았다. 이제 직접 소유 구현에서 원래
scoped-code-csharp 선택·본문/보조 함수 보호 편집을 재사용한다. 외부 caller의 root 코드나
whole/retained 문맥을 이 경로로 바꾸지 않는다. UI·레이아웃·리소스 descriptor는 그대로다.

Graphs는 원래 hash/graph/node/정의와 노드 자체 C#·helpers 경계를 검증한다. Contracts의
새 root 명시 분기는 공개/native 계약이 정확히 그대로인 경우만 받는다. 이 검증을 지난
code source ID만 따로 추적해 노드 fragment를 상위 구현 본문처럼 컴파일하지 않으며,
기존 assembled Blueprint compiler가 실제 상위 계약·모든 원문/보조 함수·입출력을 검증한다.
기존 whole/context 검증은 이 분기를 사용하지 않는다. C# 자동 변환·노드 ABI 추측·연결
재작성이나 사용자가 작성하지 않은 helper 삽입은 없다.

WholeBodies는 같은 코드·프레임 조건을 갖는 root 명시 계획과 일반 본문을 한 후보로
결합한다. 기존 version3 nativeBodyContexts·readGuards·Review/Confirm·최종 CAS를 사용한다.
후속 metadata 및 text/helpers Save와 cold에서도 원래 function/source/flow/read 기준을
보존한다. 다른 구조/계약 변경·stale/변조·독립 소스 경합은 입력과 원본을 보존하며 거절한다.

종료 기준은 이 한 일반 root 코드 흐름의 원래 UI 편집·취소·Undo/Redo·Save·cold·실패/재시도·
응답 유실·독립 창·프로젝트 경계·늦은 입력·후속 text/helpers Save와 Review 취소/Confirm,
graph/선택 record/독립 원문의 경합이다. 원래 실행40과 직접 작성한 두 본문의 실행20,
void/out 노드와 long 상위 계약, 원래 graph bytes/배치/정확한 local·독립 source bytes/mtime를
검사한다. LF/CRLF restore/build·새 package·전체 추출본과 기존 private 계획/guard/UI,
등록 helper·retained ABI의 회귀를 구분한다. 타입 조합을 새 완료 조건으로 늘리지 않는다.

남은 실제 계약 변경 callee/import·등록 외부 관측 결합은 별도 유한 작업이다. whole/retained
문맥의 독립 노드를 함께 편집하려면 원래 필수 문맥 계획을 포함하는 별도 결합이 필요하며
이번 일반 root 흐름의 완료로 그 범위까지 완료했다고 하지 않는다. 직전 reader의 새 root
pending 후보 수용은 보장하지 않고 같은 세대의 authoring/runtime을 사용한다. 자동 migration/
downgrade와 구 Reference parser 변경은 없다. Linux 엔진/portable 실행·Chromium 자동화와
실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증은 구분한다. 과거 초기 빈 화면
원인은 미확정이다. 원본·latest/rollback·증거를 보존하고 main은 사용자 검토/merge에 남긴다.

이 독립 root C# 노드/native 본문 공동 저장 단위의 [최종 신규 28·재사용 13·합계 41 검증과 보관](VALIDATION_V666_ROOT_CODE_GROUP.md)을 마쳤다.
