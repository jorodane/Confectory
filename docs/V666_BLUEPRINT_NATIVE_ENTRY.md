# 정보 기능 Blueprint 구현의 고급 입력·반환 전환

고정 [정보 편집9행](V536_I5_6_REMAINING.md)과 원본 v666
`dist/app.js::choosePropertyType`의 함수 입출력 선택을 기존 명시 Root 계약 대응에 연결한다.
원본 ZIP SHA256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.
정보별 struct·종류 enum·모듈 interface라는 사용자 결정과 원래 카드/상세창 배치를 유지한다.

직접 소유한 일반 동기 정보 기능의 직렬 call/export Blueprint 구현에서 입력과 명시 출력
writer/반환 exit의 고급 타입 전환을 연결한다. 기존 상세창의 타입 선택 뒤 현재 root 입력·
노드 결과·지역값 중 정확히 같은 타입의 출력을 명시 선택한다. 변경한 writer/exit 하나라도
계획에서 빠지면 전체 저장을 거절한다. 새 기본값·형변환·출력 배치나 실행선을 추정하지 않는다.
기존 함수/구현/노드/핀 ID·좌표·entry·실행선·반환 위치는 유지한다.

영향받는 C# 구현/호출자는 기존 보호된 편집기로 각 본문을 명시 작성한다. 일반 Blueprint
구현이 이미 있다는 읽기 정보 `blueprintImplementation`으로 첫 구현 생성과 구별하여,
변경 중인 native 계약의 C# 호출자 계획을 기존 chooser에서 편집할 수 있다. 이 정보는
편집 권한이나 Confirm이 아니며 backend의 정확한 소유·원본 검증이 계속 권위다.
Graph 타입을 고른 사실로 기존 C# 원문을 자동 변환하지 않는다.

`native-information-function-blueprint-entry-v1`은 원래 header/manifest/graph 증거와
직접 구현의 graph ID를 같은 v2 보호 초안에 결부한다. 이전 선언 전용/C# 전용/Blueprint
호출자 scope의 shape는 그대로다. 내부 graph/copy·opaque code/whole-body·상속/부모/외부
원본·require/default/함수 필드·async/공개 실행 분기 전환은 이 선택 범위에 승격하지 않는다.
새 permission·override 계약·저장 문법·migration을 만들지 않는다.

검증된 native 타입 증거가 있는 그래프는 순수 후보에서도 실제 조립 C#과 기존 정보/enum/
interface 타입 closure로 컴파일 검증한다. 새 파일/assembly를 emit하거나 provider를 실행하지
않는다. 최종 source 컴파일과 Review/Confirm·원자 CAS는 원래대로 별도로 수행한다.
취소·Undo/Redo·별도 창·재시작·checkpoint 실패·응답 유실·늦은 입력 보존을 재사용한다.
선택/Review 이후 의미가 같은 공백만 바뀌어도 정확한 원본 기준을 유지하며 거절한다.

확정 뒤 원래 Blueprint 편집기로 다시 열어 수락한 entry와 원래 export 노드를 표시한다.
그 조작으로 원본을 추가 생성하거나 다시 쓰지 않는다. call 뒤 실제 반환 exit로 연결된
경로도 같은 명시 출력 계획으로 처리한다. 비어 있는 entry에 원래 없는 실행선을 자동으로
만들어 반환 값을 평가하게 바꾸지 않는다.

이 단위는 위 일반 직렬 그래프의 입력·반환 metadata 전환과 명시 C# 호출자 대응을
저장·복원·컴파일·실행하고 UI/실패/CAS 회귀를 확인하면 마감한다. opaque/일반 C# code 노드가
있는 Blueprint의 명시적 고급 ABI 대응은 같은9행의 남은 흐름이며 조합별 새 필수 행으로
늘리지 않는다. M11/M12/M4를 새 회귀 없이 다시 열지 않는다.

살아 있는 reference의 실제 객체/접근자 연결, module async/공개 실행 결과의 계약-only
closure와 DLL 순환 처리, 기존 multiple/함수 필드 native 생성도 남는다. 선언 data/default/
객체 ID를 runtime 값 snapshot으로 쓰거나 기존 결과 ABI를 복제/생략하지 않는다.
동기 호출자는 명시적 async 전환 전 오류라는 확정 정책을 유지한다. 현재 이 전환에
추가 사용자 결정은 필요하지 않다.

구 nominal/enum parser·reader의 제한과 직전 scope의 명시 거절을 유지한다. 이전 전체
workspace reader 실행/자동 migration이나 실제 Windows/모바일·전체 UI 완료를 뜻하지 않는다.
초기 빈 화면의 원인은 미확정이다. 원본·latest/rollback·증거의 기존 보관/정리 규칙을 유지한다.
