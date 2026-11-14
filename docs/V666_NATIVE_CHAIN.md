# 함께 변경하는 native 함수의 import 계약·본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 남은 실제 callee/import 결합을 다룬다. [입력 계약·안정된 helper 관측 공동 저장](V666_INPUT_IMPORT_OBSERVATIONS.md) 다음으로, 선택 함수 A의 C# 본문이 함께 선택한 함수 B의 바뀌는 계약을 직접 호출하는 한 흐름이다. 두 함수의 long 입력을 string으로 명시 변경하고 각자의 native 선언·C# 본문·ordinary 공유 Blueprint caller 값을 직접 작성한다. 원래 프로그램85와 편집 후34가 기준이다. 기존 소유 helper와 등록 외부 helper/부모도 함께 사용한다.

게시 기준은 각 함수를 원래 계약 사전에서 따로 검증하므로 이 공동 편집을 거절한다. 새 내부 request-local 컴파일 문맥은 선택된 각 함수의 원래 소스 계획을 한 번씩 확인하고, 다른 선택 함수의 native consumer 검증에 그 동일한 명시 본문/선언 계획을 재사용한다. 최종 C# 검증에는 선택된 새 공개 계약과 원래 별칭/호출 edge의 새 typed import를 함께 제공한다. caller가 직접 작성한 C# 문자열은 변환하거나 추측하지 않는다.

중간 native header/body를 요청 units에 덮어쓰지 않고 버퍼에 보관한다. 모든 선택 행의 관측·before signature·source hash는 원래 소스를 가리킨다. 같은 native 소스가 둘 이상의 callee 검증에 나타나면 byte 동일한 최종 결과만 허용한다. ordinary Blueprint caller는 기존 overlay로 순차 합성하며 최종 후보 전체를 다시 검사한다. 준비 도중 소스 파일이나 checkpoint는 쓰지 않는다.

기존 직접 소유 동기 scalar 입력 그룹2~8개·구현당 하나의 native target·원래 명시 input/value/disconnect 계획을 유지한다. 선택하지 않은 native consumer, override/상속·private/whole-body·외부 쓰기를 자동 전환하지 않는다. 실제 source/hash/identity/권한·등록 proof/부모·caller 검증은 계속 필요하다. registered 선언은 readonly compiler 관측이며 외부 owned-unit/write member가 아니다.

저장 후 header/graph 발견은 원래 callee+consumer 구조와 캡처된 공개 계약·본문·헤더 hash를 확인한다. 원래 헤더에서 명시 native signature와 선택된 import 계약만 반영한 결과가 저장 헤더 bytes와 같아야 하며 별칭·다른 멤버나 읽기 범위는 바꿀 수 없다.

새 저장 필드나 receipt version은 없다. 기존 version3 nativeBodyDependencies/nativeBodyDependencyReads·readGuards·source/read240·member64와 원래 Review/Confirm·최종 CAS를 사용한다. cold/후속 owner·function 표시 Save와 늦은 입력의 두 번째 Save도 원래 외부 proof/read set과 소유 관측을 유지해야 한다. 별칭·helper/provider 원문·권한·구현 소유권과 authored v666 UI/layout을 보존한다. 정보별 struct·종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류 규칙을 유지한다.

이 단위의 종료 기준은 위 한 실제 import 호출 흐름에서 순서 독립적 공동 후보, 잘못된/누락된 C#·signature·body hash·caller·dependencies의 원자 거절, 기존 상세/타입/본문 UI의 취소·Undo/Redo·cold·Save 실패/재시도·응답 유실·프로젝트 왕복·늦은 입력, Save 전 및 Review 뒤 원본/외부 경합, LF/CRLF와 새 package/전체 ZIP 복원이다. 기존 scalar 입력 및 직전 helper 관측 경로는 회귀로 검사한다. 타입/문맥별 모든 조합을 새 완료 의무로 늘리지 않는다.

이전 intact package의 원래 실행·공동 Save 거절과 새 pending receipt의 순수 guard 수용 여부는 별도 실제 진단으로 기록한다. 자동 migration/downgrade나 구 Reference parser 변경은 없다. 같은 세대 authoring/runtime을 사용한다. Linux 실제 .NET/portable 실행·Chromium 자동화와 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI를 구분한다. 과거 간헐 초기 빈 화면의 원인은 미확정이며 main은 사용자 검토/merge에 남긴다.
