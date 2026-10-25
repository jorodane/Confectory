# v536 여러 함수의 출력 정의·타입 결합 — 2026-10-25

기존 정보 함수 상세창에서 출력 추가/삭제·void 전환과 유지 출력/반환의 scalar
타입 편집을 함께 하고 창의 임시 저장을 한 번 누르는 동작이다. 함수 간 다른
종류 편집과 같은 함수 안의 결합 모두 원래 단일 후보는 유효하나 그룹 가드가
거절하는 것을 수정 전에 재현했다. 출력 정의/타입 결합이라는 고정 8행의 기존
범위만 연결하며 새 UI·계약 ID·기본값 추정·C# 변환은 추가하지 않는다.

## 지원 경계와 처리

직접 소유 2~8 함수의 기존 code/export leaf callee·call/export 직렬 caller 및
이미 지원한 고정 로컬 import 경계다. 값 입력은 이름·타입·역할·순서까지 같아야
한다. 유지되는 핀 이름·역할·상대 순서도 보존한다. 삭제한 출력의 전체 writer/
exit, 새 배치의 값·위치·연결 경로, 타입이 바뀐 유지 출력의 모든 기존 writer,
caller의 호환 출력 대응을 각각 명시한다. 새 출력은 자동 공개하지 않는다.

출력 구조 편집 행도 유지 출력 타입/비void 반환 타입 변화를 분류한다. 선택
함수 전체는 구조/출력 타입/반환 타입 편집의 합이어야 하며 입력 변경은 거절한다.
함수별로 필요한 `outputGraphs`와 `outputs`를 구별해 검증한다. 원래 모든 단일
closure를 먼저 검증하고 내부 overlay에만 합성한다. 사용자 원래 source hash와
파일 관측·단일 후보/CAS·receipt·Review/Confirm을 유지하며 중간 저장하지 않는다.

## 고정 fixture

원래 A/B는 `(long amount,double real,out long count,out long stable)`이며 반환은
모드에 따라 long 또는 void다. count에는 원래 배치 두 개가 있고 A.count→B.amount,
B.count→Caller 반환이 실제 연결되어 있다. stable은 기존 출력이다.

- 함수 간: A의 count를 삭제하고 fresh(long)를 추가한다. B의 count와 반환을
  double로 바꾸며 모든 기존 writer를 real(double) 입력으로 명시한다.
- 같은 함수: A/B에서 count→fresh 교체와 stable/반환의 double 변경을 함께 한다.
- void로 전환: A의 count→fresh 교체·반환 전체 삭제와 B의 타입 편집을 결합한다.
- void에서 전환: A의 count→fresh 교체·string 반환 생성과 B의 count 타입 편집·
  string 반환 생성을 결합한다. 여러 새 배치는 명시한 앞선 새 배치 뒤에 연결한다.

기존 long 소비자는 사용자가 선택한 fresh 또는 stable(long)만 읽는다. fresh의
정확한 `9223372036854775806`과 한글/emoji 반환, 원래 C# 노드 매개변수·본문,
제어 경로·식별자·유지 writer·공개 범위를 보존한다. 잘못된 타입으로 변환하거나
연결을 조용히 버리지 않는다. 기존 API/UI harness는 테스트 환경값
`CONFECTORY_SHARED_OUTPUT_DEFINITION_MIX=1`로 이 fixture를 선택한다.

## 집중·영향 검증 완료

집중 18흐름/50확인과 영향 7흐름/26확인이 통과했다. 기본 창·같은 함수 결합의
독립 창·void에서 여러 반환 배치를 만드는 독립 창에서 편집/취소·Undo/Redo·
미저장/저장 재시작·Review 취소·명시적 Confirm을 확인했다. 네 모드 모두 실제
API 저장·재시작·컴파일·Confirm까지 통과했다. checkpoint 쓰기 실패 후 전체
미적용/재시도, 저장·결과 조회 응답 유실 후 receipt 조회와 중복 방지, 실제 파일/
peer 경합 시 원문·입력 보존, 프로젝트 전환과 오래된 창 차단, 불완전 대응
거절→Undo→명시 재시도도 실제 엔진/렌더러로 검증했다.

기존 입력 정의/타입 결합·out/반환 타입 결합·출력 삭제/추가와 양방향 void 전환·
입력/out 타입 혼합·오버라이드 보호 회귀가 통과했다. Native Release는 warning/
error 0이고 UI 74리소스와 WebBundle은 기준 850bc5c 그대로다. 대형 검사는 순차
실행했고 OOM/oom_kill 0이다. 사전48MiB 증가 예산(최근 단위 실증가28.6MiB와 여유)
및64MiB 디스크 reserve를 확인했으며 기존 자료를 삭제하지 않았다.
[집중·영향 증거](evidence/v536-information-shared-output-definition-mix/focused-verification.json)에 결과를 기록한다. 독립 checkout/패키지 검증은 다음 결과로 구분한다.

## 고정 잔여

8행 전체 완료는 아니다. 입력 이름/타입/정의와 출력·반환의 결합, ref·역할·
매개변수 순서, 수동 C#/혼합 native·중첩/private/whole/postCall, 같은 원래 계약
안의 copy/상속/등록/소유 정보 속성 혼합과 scalar 밖 함수 타입은 별도다.
9행 named 정보/참조/외부 함수 타입·표시명/native 식별자 분리도 미완료다.

오버라이드는 원래 매개변수·출력 계약을 유지한다. 위반 거절은 정상 보호이며
독립 계약 복제/새 ID는 필수 복원에서 제외한다. 같은 계약 copy·target·별칭/
import/graph 수용 경계와 나머지 UI는 별도다. 전체 UI·실제 Windows/WebView2·
모바일 기기 실행·Library 전달 완료가 아니며 사용자 프로젝트/실제 계정/유료
추론은 사용하지 않는다.
