# v536 여러 함수의 입력 정의·타입 결합 — 2026-10-25

같은 정보 창의 기존 상세창에서 입력 추가/삭제와 scalar 타입 변경을 함께 편집하고
한 번 임시 저장하는 동작이다. 함수마다 다른 종류의 입력 편집을 하는 경우와
같은 함수에서 추가+타입 교체를 하는 경우 모두, 수정 전 단일 후보는 유효하지만
그룹이 거절하는 것을 격리 fixture로 재현했다. 새 UI/레이아웃·ID·권한·C# 원문
변환은 추가하지 않는다.

## 종료 조건과 계약

직접 소유 2~8개 함수의 scalar 입력 정의/타입 편집을 같은 후보에 묶는다. 현재
code/export leaf callee·call/export 직렬 caller와 이미 지원한 고정 로컬 import
범위다. 살아남는 핀의 이름/역할/상대 순서와 out·반환은 유지한다. 기본 scalar는
bool/int/long/float/double/string이며 새 기본값·저장소·형 변환을 추정하지 않는다.

같은 이름의 입력 타입 교체는 `args`에서 null로 표시하고 실제 이전 사용처의
대체를 명시한다. 타입이 그대로인 핀은 원래 identity 대응이어야 한다. 삭제된
핀·추가 핀·타입 교체 핀을 구별하며, 두 종류 그룹의 합이 선택한 모든 함수를
포함해야 한다. 출력/반환 변경을 이 그룹에 섞거나 입력 이름·역할·순서를 바꾸는
경로는 허용하지 않는다. 원래 모든 단일 closure를 먼저 검증한 뒤 내부 overlay에
준비하고 원래 hash/파일 관측·단일 checkpoint CAS·receipt·Review/Confirm을 유지한다.

## 두 실제 fixture

원래 A/B는 `(long amount,double real,out long count)->long`이고
A.count→B.amount, B.count→Caller 반환으로 연결된다.

- 기본 모드: A에 extra(long)를 추가하고 `9223372036854775806`을 명시한다. B의
  amount만 string으로 바꾸며 caller의 한글/emoji literal과 원래 연결 해제를
  선택한다. B의 기존 long code 사용처는 정확한 `9223372036854775800`을 명시한다.
- `joint`: A.amount를 string으로 바꾸고 extra(long)도 추가한다. caller의 새 amount는
  명시 문자열이며, 기존 long amount 바인딩은 extra에 재사용한다. callee의 옛
  long 사용처도 extra를 선택한다. B는 기존 amount를 삭제하고 fresh(long)를 추가해
  caller/본문에 원래 값을 재사용한다. 새 문자열을 long으로 자동 변환하지 않는다.

두 모드에서 기존 값 재사용/해제의 모순은 UI와 backend가 거절한다. C# 매개변수와
본문, node/flow, out writer/공개 출력/최종 소비 및 다른 값·정확한 숫자를 보존한다.
`tests/web/v536_information_shared_input_mix_{fixture,native}.py`와 기존 API/UI harness의
`CONFECTORY_SHARED_INPUT_MIX=1`을 사용한다. 원본 상세 타입 선택기·추가/삭제 버튼과
호출/본문 입력 갱신창을 사용하며 새로운 편집 방식을 만들지 않는다.

실제 기본/독립 창의 편집·취소·Undo/Redo·거절 후 재시도·저장 실패·경합·응답 유실
조회·프로젝트 전환·미저장/저장 재시작·Review 취소/Confirm을 확인한다. 순수 후보의
역순·원래 hash·사용처/값/해제 누락·잘못된 타입과 출력/순서/역할/반환/본문·실제
source 변경은 전체 미적용이어야 한다.

집중 12흐름/31확인, 같은 함수 내 결합의 실제 API/UI 2흐름/5확인, 관련 기존
6흐름/23확인과 이전 입력 정의 UI 2확인이 통과했다. UI/manifest 74리소스는
이전 게시본 그대로며 Native Release는 warning/error0이다. [집중 증거](evidence/v536-information-shared-input-mix/focused-verification.json)에 결과를 기록한다.
추가 런너의 최초 실행은 물려받은 검사 항목과 새 항목의 이름 충돌을 계획 검증이
worker 시작 전에 거절했다. 빈 최초 결과 폴더와 진단을 보존하고 항목 이름만
구별해 새 결과 경로에서 실행했다. 중복 worker/증거 덮어쓰기는 없으며 fail-closed
검사는 유지한다.

## 고정 잔여와 보호

8행 전체 완료는 아니다. 입력 이름/출력/반환 편집의 더 넓은 결합, ref·역할·순서,
수동 C#/혼합 native·nested/private/whole/postCall, 같은 계약 내 copy/상속/등록/
owner 속성 혼합 및 scalar 밖 선택 타입은 별도다. 9행 named 정보/참조/외부 함수
타입과 표시명/native ID 분리, I6/B2·A4~A6·M4/M11/M12와 Helper 실제 작업은 후속이다.

7행 오버라이드는 원본 매개변수·출력 계약을 유지한다. 계약 위반 거절은 정상
보호이며 독립 계약 복제/새 계약 ID는 필수 복원에서 제외한다. 이 정책을 새 함수
생성과 직접 소유 함수 편집까지 막는 근거로 확대하지 않는다. 현재 단위는 7행
전체 완료로 표시하지 않는다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library
전달도 미완료이며 사용자 프로젝트/실제 계정/유료 추론은 사용하지 않는다.

## 커밋 후 독립 checkout·새 교차 패키지

실행 소스는 `8549f5cbb197d96173f91ab59fc9f7d6279a65ec`이다. 독립 checkout의
동일 Git blob과 기존 LF/CRLF 변환을 확인하고 설정 변경 없이 Native Release를
빌드했다. 정상/같은 함수 결합·실제 API·같은 함수 독립 창 UI·오버라이드 보호의
5흐름/16확인이 통과했다. root solution Release와 별도 MCP Release도 모두
warning/error 0이며, 실행 순서를 겹치지 않았다.

이 소스로 새 Windows x64 패키지를 RAM에 교차 생성했다. manifest 2,343항목,
marker 포함 2,344파일/132,757,551바이트이며 전체 파일 목록·해시와 현재 Native
DLL/제품 소스·7개 Core DLL 일치를 확인했다. manifest SHA-256은
`a1a3294583796374ae60f869eb729a3ffbff5d32dec016104faa4b9dad694a30`이다.
SDK 없는 기존 runtime fixture를 읽기 전용으로 재사용해 패키지의 실제 managed
엔진 웹 기동, 무관한 cwd, 74리소스, synthetic profile/override 보존과 변조·의존성
누락 거절을 확인했다. 패키지의 새 backend 후보 검사 4건도 통과했다.

완전한 manifest와 fixture·로그 증거를 보존한 뒤 이번 검사에서 직접 만든 RAM
패키지 복사본만 제거했다. 새 배포 파일을 보관하거나 전달한 결과가 아니다.
이전 보관 패키지·SDK·사용자 자료·기존 파일은 삭제하지 않았다. 최저 디스크 여유
174,153,728바이트, cgroup OOM/oom_kill 0이다. RAM 메모리 제한에는 근접했으므로
후속 대형 검사는 계속 순차 실행한다. Windows apphost/WebView2·모바일 실기기와
Library 전달은 미검증이다. 이 뒤 커밋은 검증 결과 문서만 바꾸며 실행 코드는
위 소스와 동일하다. [checkout·패키지 증거](evidence/v536-information-shared-input-mix/package-clean-verification.json)에 정확한 범위·해시를 기록한다.
