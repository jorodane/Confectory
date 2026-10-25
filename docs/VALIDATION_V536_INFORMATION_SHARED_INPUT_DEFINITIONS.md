# v536 여러 함수의 값 입력 추가·삭제 — 2026-10-25

같은 정보 창에서 여러 직접 소유 함수의 입력을 추가·삭제한 뒤 한 번 임시 저장하는
기존 v536 동작이다. 수정 전 격리 원본에서 추가와 사용 중 입력 삭제/추가가 각각
단일 후보로 유효하지만 그룹 가드가 거절함을 재현했다. 원본 UI/레이아웃·함수 ID·
C# 원문·실행 권한은 변경하지 않는다.

## 이번 종료 조건

직접 소유 함수 2~8개의 scalar 값 입력 추가·삭제·삭제/추가 혼합을 기존 명시적
매핑으로 결합한다. 유지되는 모든 핀의 이름·타입·역할·상대 순서, out 및 반환
계약은 그대로다. 새 입력은 bool/int/long/float/double/string만 선택하며 임의
기본값을 만들지 않는다. 바뀌는 모든 함수가 이 입력 정의 그룹이어야 한다.
기존 이름/타입 전용 그룹을 이 그룹으로 오분류하지 않는다.

원래 `args` 대응으로 삭제/추가된 값 입력을 구별한 뒤, 유지 핀·out·반환을 확인한다.
caller는 현재 모든 값 입력의 명시 값/호환 바인딩과 사용하지 않을 원래 연결의
정확한 해제 증거를 제출한다. callee의 실제 삭제 입력 사용처는 같은 타입의 현재
입력 또는 명시 literal로 대체 선택한다. 사용처가 없으면 그 계획은 생략한다.
새 입력에 재사용하는 기존 바인딩을 동시에 해제하는 모순은 UI와 backend에서
모두 거절한다. 모든 원래 단일 closure를 먼저 검증한 뒤 내부 overlay에만 합치며
원래 해시·실제 파일 관측·단일 checkpoint CAS·receipt·Review/Confirm을 유지한다.
중간 후보나 먼저 처리한 함수만 저장하지 않는다.

## 격리 데이터와 실제 화면

기존 A/B는 `(long amount,double real,out long count)->long`이고
A.count→B.amount, B.count→Caller 반환으로 연결된다. A에 extra(long)를 추가하며
caller 값은 정확한 `9223372036854775806`을 명시한다. B에서는 amount를 삭제하고
fresh(long)를 추가한다. callee의 기존 amount 사용처는 fresh를 명시하며 caller의
원래 amount 바인딩은 fresh에 재사용한다. 기존 값과 계산은 추측해서 변환하지 않는다.
`delete` fixture는 B의 amount만 삭제하고 callee 사용처에 정확한
`9223372036854775800`을 선택하며 caller의 원래 amount 연결 해제를 명시한다.

두 모드 모두 기존 code 매개변수/본문, graph node/flow, out writer·공개 이름/타입과
최종 출력 소비, Power 정확64비트 및 다른 파일을 확인한다. 원본 상세창의 입력
추가/삭제 버튼과 타입 선택기, 기존 caller/본문 입력 갱신창을 사용한다. 새 메뉴나
편집 방식을 만들지 않는다. Native/API/UI는
`tests/web/v536_information_shared_input_definitions_{fixture,native}.py` 및 기존
API/UI harness의 `CONFECTORY_SHARED_INPUT_DEFINITIONS=1`을 사용한다.

기본/독립 창의 취소·Undo/Redo·불완전 대응 거절 후 재시도·저장 실패·응답 유실
조회·경합·프로젝트 전환·미저장/저장 재시작·Review 취소/Confirm과 원래 source를
검사한다. 순수 후보는 역순·원래 hash, 새 값/사용처 누락·타입 오류·재사용/해제
모순·기존 핀/출력/반환/본문 변경과 실제 source 경합의 전체 미적용을 확인한다.
집중 11흐름/27확인과 삭제 전용 3흐름/9확인이 통과했다. 새 literal의 long 범위
초과도 두 최종 순수 검사에서 거절했다. 관련 기존 5흐름/19확인(오버라이드 보호
3확인 포함)과 이전 입력 타입 화면 2확인도 통과했다. [집중 증거](evidence/v536-information-shared-input-definitions/focused-verification.json)에 기록한다.
추가 검사 런너는 8개 고유 worker가 모두 완료된 뒤 동일한 목록 항목을 다시
만나 배타적 로그 생성에서 종료됐다. 새 worker는 시작되지 않았고 증거는
덮어쓰지 않았다. 결과를 회수해 8개 모두 exit0을 확인하고 동일 descriptor만
한 번 예약하도록 런너를 수정했다. 완료 검사는 재실행하지 않았다.
Native Release warning/error0이며 clean checkout/교차 패키지는 다음 검증이다.

## 정책과 고정 잔여

[오버라이드 계약 정책](V536_OVERRIDE_CONTRACT_POLICY.md)에 따라 원본 계약을 깨는
오버라이드 타입/핀 수/역할/반환 변경은 정상 금지다. 독립 계약 복제·새 계약 ID
발급은 필수 복원에서 제외하고 답변 대기로 표시하지 않는다. 이 단위의 직접
소유 함수 편집/기존 새 함수 생성은 별개로 유지한다. 7행 전체 완료로 집계하지
않으며 같은 원래 계약 내 copy/등록/다중 target·본문 문맥의 실제 수용 경계만 남긴다.

8행은 미완료다. 이번 입력 정의와 이름/타입/순서/다른 출력·반환 편집의 결합,
ref/역할/순서, 수동 C#/혼합 native·nested/private/whole/postCall, 같은 계약 내
copy/상속/등록/owner 속성 혼합과 scalar 밖 선택 타입은 별도다. 9행 named 정보/
참조/외부 함수 타입 및 표시명/native ID 분리, I6/B2·A4~A6·M4/M11/M12와 Helper
실제 편집 도구는 후속이다. 전체 UI·실제 Windows/WebView2·모바일 기기 및
Library 전달 완료가 아니며 사용자 자료/계정/유료 추론을 사용하지 않는다.
