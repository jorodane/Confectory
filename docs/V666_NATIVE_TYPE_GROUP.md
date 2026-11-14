# 두 고급 native 입력 계약과 명시 C# 본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 다음 한 흐름은 같은 정보의 두 함수 입력을 정보별 C# 구조체로 전환하면서, 각각의 직접 C# 구현·호출자 본문을 명시 작성해 한 Save로 보관하는 것이다. 원래 실제 프로그램70, 구조체 입력과 네 본문을 직접 선택한 프로그램73이 기준이다. 공개/native 인자 이름·개수·순서·역할과 scalar 반환, 호출자 ABI·원래 import alias·소유 locator를 유지한다. 정보별 struct·종류 enum·모듈 interface라는 확정 표현을 재사용하며 새 값/참조/종류 의미를 만들지 않는다.

기존 함수별 타입 선택과 `$function:<ID>` 출처 증거를 모두 원래 snapshot에서 먼저 검증한다. 직접 소유 동기 함수2~8개, 원래 scalar 값 입력→정확한 기존 nominal 단일 타입, 원래 scalar 반환, 겹치지 않는 C# 구현/직접 호출자 소스만 분류한다. reference·배열·out/ref·async·새 입출력 정의·반환 타입 변경, 같은 소스를 공유하거나 서로 호출하는 선택 함수는 이 단위에 포함하지 않는다. 각 단일 전환의 기존 검증기가 정확한 original native 선언·source hash·명시 본문을 검증한다. 순서를 바꿔도 같은 후보이며 source를 생성하거나 자동 변환하지 않는다.

기존 단일 함수의 타입 전환 receipt는 원래 함수별 타입/읽기 lease 경로로 cold 복원한다. 임의의 readGuards만으로 공동 native 본문 그룹으로 분류하지 않는다. 한 함수를 임시 저장한 뒤 두 번째 scope를 덧붙이는 요청은 거절하며, 다중 scope는 원래의 완전한 공동 계획 또는 캡처된 동일 scope 집합만 허용한다.

기존 `native-type-source-guards-v1`/version2 workspace와 version3 slot receipt에 함수별 증거를 함께 보관한다. 각 scope를 따로 재조회하고 전체 읽기를 기존 read240·member64 예산 아래 합집합으로 확인한다. 새 receipt 필드나 권한·등록이 없다. 외부 선언·manifest는 원래 선택 증거에 따른 읽기 관측이며 쓰기 대상이 아니다. 후속 owner/function metadata Save와 cold 발견은 캡처된 function/header/body hash·선택한 타입 proof, 원래 native 별칭·호출자 ABI, signature/import 외 헤더 bytes를 검증한다. 저장 선언을 인정하는 경로도 이 캡처 검사를 거친다.

종료 기준은 원래 실행과 이전 planner 거절 재현, 순서 독립 후보·누락/교차/변조 증거·소스 공유·잘못된 C# 거절, 기존 원본 UI의 두 타입 선택·네 본문·취소·Undo/Redo·미저장/저장 cold·쓰기 실패/재시도·응답 유실·후속 입력·프로젝트 왕복, metadata Save·Review 뒤 caller/type 원본 경합·새 Review/Confirm, LF/CRLF·새 package·전체 ZIP 복원이다. 직전 역할 import와 기존 단일 고급 전환을 별도 회귀로 확인한다. 고급 타입/역할/문맥별 무한 조합을 새 의무로 늘리지 않는다.

공유 C# caller·선택 함수 간 고급 import 계약, 고급 반환·reference/array·private/whole/override 결합은 기존 고정 잔여와 구분한다. 구 reader의 새 pending 수용은 온전한 이전 package에서 실제 측정하며 자동 migration/downgrade하지 않는다. 명시 async 전환 전 sync caller 오류·Review/Confirm·최종 CAS·원본 UI 레이아웃을 유지한다. Linux .NET/portable 실행·Chromium 자동화와 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증을 구분하며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
