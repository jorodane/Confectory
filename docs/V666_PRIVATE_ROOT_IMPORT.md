# Private 구현의 원래 일반 helper 호출·import 보존

고정 v666 [정보7/8행](V536_I5_6_REMAINING.md)의 기존 private C# 본문/helpers 편집과 다른 소유 native 함수의 명시 scalar 반환 변경을 한 정보 창·한 Save에 연결한다. [기존 native helper import](V666_PRIVATE_RETURN_IMPORT.md)에 이어 private 구현의 원래 일반 Blueprint helper 호출·typed import를 보존하는 유한 단위다.

원래 private 구현은 root의 private 계산 결과를 기존 일반 helper 호출에 전달한다. helper 반환이 그 함수의 원래 반환값이 되며, 이 graph·호출·입출력·locals·좌표·root/private/code ABI는 편집하지 않는다. 원래 프로그램40과 두 단독 계획은 유효하지만 기존 패키지의 공동 후보·실제 UI Save만 거절되는 경로다. 수동 본문/helpers와 명시 반환→호환 out 대응 뒤 caller20·직접 double 반환25.5·long out25를 확인한다.

허용하는 private 구현은 직접 소유 단일 Blueprint target이다. 이미 읽은 같은 프로젝트의 선택되지 않은 부모 없는 helper 함수와 정확한 typed import가 있어야 한다. 기존 `FeatureBlueprint.ImportAlias`의 고정 `fg_call_…` 별칭과, 그 계약에 맞는 실제 ordinary `call/next` 노드를 확인한다. retained/forwardCallerStorage 문맥·선택 callee·외부/부모 계약·미사용 import는 별도 명시 계획의 경계다. 새 호출·별칭·C#·연결·저장소를 만들거나 추론하지 않는다. 기존 Core 별칭·graph 문법은 변경하지 않는다.

기존 단독 Contracts/Graphs·assembled C# 검증, version3 nativeBodyContexts·프로젝트 전체 readGuards·Review/Confirm·최종 CAS를 재사용한다. root import header와 graph·일반 helper 호출은 원래 bytes로 유지하고 helper 함수·구현·BOM/CRLF 본문은 쓰기 그룹 밖의 읽기 의존성으로 보존한다. 기존 helper inode·mode·mtime도 유지한다. 새 schema/receipt/profile·권한·외부 탐색·등록은 없다.

종료 기준은 이 원래 한 흐름의 순서 독립 후보, 원래 UI의 취소/Undo·cold·저장 실패/재시도·응답 유실·늦은 입력·후속 Save·창/프로젝트 경계와 실제 확정 실행이다. root import header·graph와 helper 함수/구현/본문의 Review 이후 실제 원본 경합 및 읽기 누락을 거절한다. LF/CRLF·새 package·전체 ZIP 복원과 기존 private/반환/역할·struct·whole/retained·등록 helper 회귀를 구분한다. 이전 guard의 새 pending 거절과 이전 CLI의 확정 source 실행도 별도 측정한다.

정보별 C# struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류 정책을 유지한다. 다른 역할/반환 구조·함께 바뀌는 선택 callee·private ABI·retained/opaque import·외부 관측은 잔여다. 조합별 새 필수 매트릭스를 추가하지 않는다. 구 Reference reader 일반 호환성·자동 migration/downgrade, 실제 Windows/WebView2·물리 기기·전체 UI는 별도이며 초기 빈 화면 원인은 미확정이다. 원본·latest/rollback·증거·main을 보호한다.
