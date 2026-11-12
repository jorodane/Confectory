# 명시 native out·반환 타입 공동 저장

고정7/8행의 scalar out·비void 반환 타입 편집을 함수 간 또는 같은 함수에서 명시하고,
직접 소유 동기 C# 함수2..8개와 일반 Blueprint 공유 caller를 한 후보/CAS에 연결한다.
원래 단일 raw native target·값 입력·입출력 이름/역할/수/순서·caller ABI/profile·노드 ID·실행선은 유지한다.
기존 상세창에서 타입을 선택하고 C# 선언에 맞는 본문을 직접 저장한다. 본문을 자동 재작성하지 않는다.

기존 호출 계약 창에서 타입이 바뀐 각 원래 출력의 소비를 정확히 같은 원래 타입의 유지된 출력으로 직접 대응한다.
타입이 유지된 출력과 모든 입력은 identity다. 새 변환·기본값·자동 연결 삭제는 없다.
모든 함수의 원래 증거·본문·caller 선택을 먼저 독립 검증하고, 같은 원래 해시의 공유 graph 후보를 합친다.
함수별 변경의 순서를 뒤집어도 같은 결과여야 한다. 다른 멤버의 변경을 빌려 단독 계획을 유효하게 만들지 않는다.

검사는 out long count와 long 반환을 double로 함께 바꾸고 out long saved를 유지한다.
원래 count/return 소비를 saved로 명시 대응한다. 입력 amount/real과 helper 원문은 그대로 두고
count=real; saved=helper(amount+2); return real+0.5 본문을 직접 작성한다.
실제 IInvoke 반환40L→1.75D, out34L/37L→1.25D/35L와 공유 caller38→40을 검사한다.
함수 하나의 out만 변경하고 다른 함수의 반환만 변경하는 원래 명시 계획도 별도로 독립 검증·합성한다.

누락/틀린 소비 대응·유지 출력 변경·입력/역할/핀 수/순서/이름 변경·void 전환·stale 선언/본문/caller와
잘못된 C#은 전체 거절한다. 기존 receipt/readGuards·후속 설명 Save·cold·Review/Confirm·최종 CAS를 유지한다.
현재 editor UI와 레이아웃은 변경하지 않는다. 공개 실행·out 추가/삭제·ref·override/copy/opaque/private 및
선택 native 의존성 결합은 이 지원 단위 밖이다. 원래 source/소유권·권한·계약을 추측하지 않는다.

남은 고정7/8행은 원래 UI의 복합 계약/본문·다른 속성 공동 편집(입력·출력 동시 편집 및 출력 정의/void·타입 결합 포함),
opaque/private 호출자의 명시 C# 계획, 선택 native callee 의존성과 기존 import/등록 외부 관측 결합으로 묶어 대조한다.
원래 조작의 재현·지원/정상 거절 경계와 회귀 증거를 종료 기준으로 삼고 모든 타입·역할·문맥의 곱을 필수 작업으로 만들지 않는다.
가능한 타입/문맥 조합을 새 필수 목록으로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다.
정보별 구조체·종류 enum·모듈 interface, 기존 authored layout·예산을 유지한다.
같은 게시 세대의 저장/재편집 기준이며 구 Reference reader·이전 authoring으로의 migration/downgrade는 바꾸지 않는다.
초기 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·물리 기기 및 전체 UI 전수 검증은 자동화와 구분한다.
