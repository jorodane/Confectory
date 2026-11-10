# 기존 독립 노드·지역값을 보존하는 whole-body 고급 ABI

고정 [정보 편집9행](V536_I5_6_REMAINING.md)의 고급 함수 입출력 선택을 기존 retained
whole-body 계약에 연결한다. 원본 v666 `dist/app.js::choosePropertyType`와 내부 흐름 진입,
[기존 retained 계약](VALIDATION_V536_INFORMATION_RETAINED.md)의 명시 대응을 따른다.
원본 ZIP SHA256은 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.

직접 소유 동기 함수의 직렬 root에서 한 C# 문맥과 기존 code/call/export·지역값을 유지한 채
공개 입출력과 실제 native 서명/본문·일반 C# 호출자를 명시 편집한다. 기존 native 이름,
노드·반환 배치·entry·경로·좌표·정확한 local 값을 보존한다. 독립 C# code/helper record는
전체 bytes와 mtime를 유지하며 저장 쓰기 목록에서 제외하고 읽기 의존성으로 보관한다.
원래 `.csbody` 파일도 다시 쓰지 않는다. 전체 C#을 자동 변환하거나 그래프를 단일 노드로
접어 독립 동작/저장소/연결을 버리지 않는다.

반환 타입이 바뀌면 기존 전체 본문 출력 대응과 root writer/exit의 새 source를 각각 명시
선택한다. backend는 이미 정확한 root 출력 교체 슬롯만 이전 출력의 소비자에서 제외하고,
나머지 소비자는 같은 타입 대응을 요구한다. UI도 원래 `outputConsumers` 슬롯 목록을 읽어
**모든** 소비자가 명시 root 출력 교체 대상일 때만 이전 출력의 미연결 선택을 허용한다.
독립 노드·local·교체하지 않은 exit 등에 소비자가 하나라도 남으면 기존 같은 타입 대응을
요구한다. 목록이 없는 이전 metadata도 보수적으로 사용 중인 출력 검사를 유지한다.
이 정보는 쓰기 권한이 아니며 순수 후보/컴파일·Review/Confirm·최종 CAS가 계속 권위다.
출력 교체 계획 누락이나 다른 소비자 잔존을 backend에서 묵시적으로 무시하지 않는다.

`native-information-function-retained-whole-v1`은 한 직접 소유 root 문맥과 graph/code/header/
manifest의 원래 읽기 증거를 기존 v2 초안에 결부한다. 이전 unused/C#/call/export/고정 code/
단일 whole lift의 scope hash와 저장 문법은 유지한다. 저장된 후보의 새 헤더와 물리 원본의
이전 문맥을 혼동하지 않으며, 새 후보 전체는 별도 compiler 검증으로 확인한다. 코드나
헤더가 달라지면 입력을 유지하며 거절하고 새 원본을 자동 수락하지 않는다.

종료 기준은 위 직렬 retained 그래프에서 struct 입력/반환과 명시 본문·호출자·출력 선택을
원래 UI로 저장·cold 복원·실행하고, 독립 노드/helpers/local/연결·실패/충돌/취소/Undo/Redo/
응답 유실·늦은 입력을 검증하는 것이다. 별도 소비자가 남는 출력의 해제는 UI/API 양쪽에서
거절한다. 독립 code 노드 자체의 서명·private frame·여러 문맥/분기·copy/상속/참조 전환을
이 단위에 임의 승격하지 않는다. 부모/참조 원본·override 계약·권한과 원래 v666 배치를 유지한다.

살아 있는 참조 객체/접근자·수명, 모듈 async/공개 실행 결과의 계약-only closure/DLL 순환,
multiple/함수 필드 native 생성은 같은 유한 잔여다. ID/$ref를 runtime snapshot으로 바꾸지
않고 동기 호출자는 명시 async 전환 전 오류라는 확정 정책을 유지한다. 이번 범위에 추가
사용자 결정은 없다. 구 nominal/enum parser·reader 비호환과 이전 scope의 명시 거절,
자동 migration 없음은 유지한다. 실제 Windows/모바일·전체 UI는 미검증이고 초기 빈 화면
원인은 미확정이다. 원본·latest/rollback·증거의 기존 보관/정리 규칙을 유지한다.
