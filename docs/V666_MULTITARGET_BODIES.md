# 여러 함수의 플랫폼별 C# 본문 공동 저장

고정 [정보 편집8행](V536_I5_6_REMAINING.md)의 한 정보 창·한 Save에서, 직접 소유한
여러 함수의 기존 플랫폼별 본문을 각각 명시 편집하는 흐름을 연결한다. 기준은 저장소
v666 ZIP `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`app.js::renderFeatureDefinition`, `openOwnFunctionPopover`와 기존 구현 선택/본문
편집기 및 native target 계약이다. 새로운 target이나 모든 플랫폼 자동 복제 기능은 아니다.

게시 `6a2eeb70`에서 공통·Linux 두 target의 각 함수 후보와 원래 프로그램40/44는
유효하다. 기존 구현 선택창에서 네 본문을 모두 명시 편집할 수 있지만, 두 함수를
함께 Save하면 단일 native target 제한으로 전체 거절되는 경로를 재현했다.

같은 계약을 유지하는 직접 소유 정보 함수2–8개와 각 소유 구현의 기존 C# target1–8개를
대상으로 한다. 모든 영향 native target을 명시 검토하는 기존 계약은 유지한다.
하나라도 검토를 빠뜨리거나 source/signature/소유가 다르면 전체 입력을 보존·거절한다.
native/public/override 계약·인자 ID/이름/타입/역할·원래 provider/target 연결은 유지한다.
다른 target으로 source를 복제하거나 C# 본문을 자동 재작성하지 않는다.

기존 전체 후보 검증·원자 checkpoint/CAS·공유 이력과 Review→Confirm을 재사용한다.
각 target의 원래 소스와 구현 헤더를 같은 version3 readGuards에 결부한다. 저장 후
peer 헤더가 target을 줄여도 저장된 그룹을 작은 구 영수증으로 재해석하지 않는다.
후속 owner 설명/아이콘 Save와 cold Review도 모든 기존 target과 읽기 해시를 유지한다.
이미 저장한 target의 선언/locator 자체가 없어지면 기존 Restore 소유 검증이 강제
프로젝트 시작을 거절한다. checkpoint/네 본문을 유지하며 정확한 원본을 먼저 복구한
후 다시 연다. 없어진 ID를 추정·이행하거나 그 거절을 새 migration 요구로 바꾸지 않는다.
후속 설명 Save 뒤 영수증의 target 증거 하나를 제거하면 Review 요청이 접수되는
검증 누락도 재현했다. 실제 typed 그룹 멤버로 native 그룹을 식별하고, 불완전한 증거를
다른 영수증 종류로 넘기지 않고 거절한다. Confirm은 실행하지 않았고 원본 source
hash가 모두 그대로임을 확인했다. 신규 권한이나 더 넓은 source footprint는 만들지 않는다.
그룹은 기존64-member Review·240 read/write·2048 known unit 예산 안에서만 수용한다.
별도 신규 정책이나 예산 확대 없이 저장 전에 검토 불가능한 큰 그룹을 거절한다.

기존 단일 target/빈 readGuards의 호환과 직접 소유 일반/분기/C# 호출자 보존을
유지한다. copy/상속/등록·private/whole/wrapper 및 다른 실제 ABI/source closure는
기존7/8행 잔여와 구별하며 경우의 수별 새 필수 요구로 늘리지 않는다. 닫힌 M11/M12/M4를
다시 열지 않는다. UI 레이아웃·권한·receipt 문법·실행 계약은 바꾸지 않는다.

고급 정보·참조 핀의 C# 표현 선택은 답변 대기이며 이 단위에서 확정하지 않는다.
일반 입력/out 표시명·기존 신원/그룹 backend와 종류 CLR/사용 중 삭제 정책도 별도다.
초기 빈 화면 원인은 미확정이며 실제 Windows/WebView2·기기·전체 UI 검증은 Linux
native/Chromium·격리 fixture·교차 패키지 검사와 구별한다.

확정 검증과 보관 결과는 이 단위 마감 기록에서 구분한다.
