# 함께 변경하는 C# import 함수의 고급 입력 공동 저장

[고정 7/8행](V536_I5_6_REMAINING.md)의 다음 단위는 기존 Main → 소유 A → 소유 B의 C# import 경로에서 A/B의 scalar 값 입력을 선택한 정보별 구조체로 바꾸고, 두 구현과 Main 본문을 직접 작성하여 한 번에 저장하는 흐름이다. 원래70·편집73을 실제 실행 기준으로 둔다. 두 함수의 네 명시 선택은 세 고유 C# source에 대응한다. A 본문은 자기 계약과 B 호출자 계획 양쪽에서 같은 원래 경로/hash/before/after 선언/text로 검증하며 contract 증거는 함수별로 따로 유지한다.

모든 명시 미래 함수 계약과 각각 검증된 nominal type header를 내부 compiler view에 제공한다. 원래 import alias/native 매개변수 이름·순서·값 역할·scalar 반환을 보존한다. 변경하지 않는 Main의 ABI도 유지한다. 서로 다른 source ID의 같은 물리 경로, 누락·서로 다른 A 본문 계획이나 stale/type scope는 전체 거절한다. 모든 header/body를 기존 buffer에서 후보가 완성될 때까지 보관하고 같은 최종 결과만 한 번 합친다. C# text를 추측·변환하거나 함수를 자동 전환하지 않는다.

기존 UI에서 B의 호출자인 A를 편집할 때 A에서 이미 명시한 자기 본문 계획의 선언을 표시한다. A의 native edit·source ID·경로·hash·원래 선언·선택한 자기 계약이 현재 관측과 일치할 때만 읽고, B의 원래 caller source와 B별 contract 증거는 유지한다. A의 미작성·취소·stale 계획은 새 선언을 제공하지 않는다. 이 연결은 기존 본문 선택기/모달을 사용하며 카드 크기·DOM/CSS 배치를 바꾸지 않는다. 본문은 여전히 각 함수에서 명시 선택·작성하고 서버가 전체 계획을 검증한다.

종료 기준은 원래 실행과 이전 planner 거절 재현, 원래 해시의 순서 독립 후보·상충 A 계획/잘못된 소비 선언·누락/교차 proof 거절, cold·후속 owner/function metadata·재서명한 import/native 선언 변조 방지, Main/A/type의 Review 후 경합과 새 Confirm, 기본/독립 UI·취소·Undo/Redo·실패 재시도·응답 유실·늦은 입력·프로젝트 왕복, LF/CRLF·새 패키지/전체 ZIP 복원이다. 이전 공유/개별 타입 경계·역할 전환과 기존 등록 외부 타입 읽기는 이번 source에 대한 회귀로 구분한다.

직접 소유 동기 native 함수2~8개의 기존 scalar 입력→nominal 단일 값과 기존 C# target 범위다. 고급 반환·reference/array·out/ref·async·private/whole/override·외부 수정 결합은 별도 고정 잔여다. version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64·type64·권한·Review/Confirm·최종 CAS와 정보별 struct·종류 enum·모듈 interface를 유지한다. sync caller는 명시 async 전환 전 오류라는 결정도 유지한다. 구 reader의 새 pending 수용은 온전한 이전 package에서 측정하고 자동 migration/downgrade하지 않는다. Linux .NET/Chromium과 Windows/WebView2·실제 기기·전체 UI 검증을 구분하며 초기 빈 화면 원인은 미확정이다.
