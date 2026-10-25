# v536 여러 함수의 out·비void 반환 타입 결합 — 2026-10-25

정보 창의 기존 함수 상세창에서 out 타입과 비void 반환 타입을 편집하고 창의
임시 저장을 한 번 누르는 동작이다. 함수마다 다른 종류를 편집하는 경우와
같은 함수에서 두 종류를 함께 바꾸는 경우를 고정 수용 단위로 삼는다. 원래
단일 후보가 모두 유효한데 그룹만 거절하는 두 경우를 수정 전에 재현했다.

## 지원 경계와 원자성

직접 소유 일반 Blueprint 2~8개의 기존 code/export leaf callee·call/export
직렬 caller 및 이미 지원한 고정 로컬 import 경계다. 값 입력의 이름·타입·역할·
순서, 핀 수와 out 이름·역할·순서를 유지한다. out/비void 반환의 기본 scalar
타입 변경만 결합하며 새 기본값이나 타입 변환을 추정하지 않는다. 출력 정의
추가/삭제·void 전환·입력 편집·ref·순서 변경은 이 결합 단위에 포함하지 않는다.

반환을 바꾼 함수의 값 입력은 원래 계약과 정확히 같아야 한다. 유지되는 out은
기존 핀 루프와 명시 대응으로 검증한다. 선택 함수 전체가 out 타입/반환 타입
편집의 합에 포함되어야 하며 입력 타입 편집은 이 그룹에서 거절한다. 모든
출력 writer의 원래 before/hash·새 값과 모든 caller의 호환 출력 대응을 기존
단일 closure에서 먼저 검증한다. 그 뒤 내부 overlay에 합성하며 사용자 원래
source hash·파일 관측·한 후보/CAS·receipt·Review/Confirm을 유지한다. live
source나 중간 checkpoint에 순차 저장하지 않는다.

## 실제 fixture와 UI

원래 A/B는 `(long amount,double real,out long count,out long stable)->long`이다.
A.return→B.amount, B.count→Caller 반환이 실제로 연결되어 있다. stable은
원래부터 존재하는 long 출력이며 테스트를 통과하려고 제품에 자동 생성하지 않는다.

- 함수 간 모드: A.return만 double, B.count만 double로 편집한다.
- 같은 함수 모드: A/B 각각 count와 return을 double로 편집한다.
- 바뀐 writer는 사용자가 real(double) 입력을 선택한다. 기존 long 소비자는
  사용자가 stable(long)을 선택한다. 연결 누락·잘못된 타입은 거절한다.

원래 code 노드 매개변수와 C# 본문, stable writer, 값 입력·정확한 64비트 원문,
제어 경로·노드 식별자·다른 함수·부모/외부 원본을 보존한다. 별도의 순수 후보는
명시 bool/한글 string 값도 기존 타입 규칙으로 검사하며 역순 후보가 동일한
최종 결과인지 검증한다. 기존 `CONFECTORY_SHARED_OUTPUT_RETURN_MIX=1` 테스트
선택 분기를 API/UI harness에 추가했으며 제품 화면/메뉴/레이아웃은 바꾸지 않는다.

## 집중·영향 검증 완료

집중 13흐름/36확인과 기존 입력 정의/타입 결합·반환 타입·out 타입·출력 정의·
입력/out 타입 혼합·오버라이드 보호의 영향 6흐름/23확인이 통과했다. 기본/독립
창의 취소·Undo/Redo·미저장 재시작·Save/저장 재시작·Review 취소·명시적 Confirm,
checkpoint 쓰기 실패 후 전체 미적용·재시도, 응답/결과 조회 유실 후 receipt 조회와
중복 방지, 실제 파일/peer 경합 시 원문·입력 보존, 프로젝트 전환과 오래된 창의
오적용 차단, 불완전 대응 거절→Undo→명시 재시도를 실제 엔진/렌더러에서 확인했다.
[집중·영향 증거](evidence/v536-information-shared-output-return-mix/focused-verification.json)에 결과를 기록한다.

Native Release는 warning/error 0이다. 최초 빌드 호출은 기존 SDK 홈 환경값
누락으로 `/home/agent/.dotnet` 읽기 전용 오류가 나 컴파일 전에 종료했다. stderr를
보존하고 기존 writable CLI 홈/캐시 환경값으로 정정했으며 저장소·환경 설정을
변경하지 않았다. 최초 메모리 사전 확인도 기존 900MiB free 기준에서 worker 시작
전에 멈춰 점검했다. 단계별 여유와 커널 회수 가능 파일 캐시를 기록하고 대형
검사를 순차 수행했다. 제한 근접 샘플은 있었으나 OOM/oom_kill 0이다. 제품 UI
74리소스와 WebBundle은 기준 a1204ea 그대로다. 독립 checkout/패키지 결과는 아래에 기록한다.

## 고정 잔여

8행 전체 완료는 아니다. 입력 이름/타입/정의와 출력·반환의 더 넓은 결합,
출력 정의 추가/삭제·void 전환과 타입 편집의 혼합, ref·역할·순서, 수동 C#/
혼합 native·중첩/private/whole/postCall, 같은 계약 내 copy/상속/등록/소유
정보 속성 혼합 및 scalar 밖 함수 타입은 별도다. 9행 named 정보/참조/외부
함수 타입과 표시명/native 식별자 분리도 미완료다.

오버라이드는 원래 매개변수·출력 계약을 유지한다. 계약 위반 거절은 정상
보호이며 독립 계약 복제/새 계약 ID는 필수 복원에서 제외한다. 7행의 같은
계약 copy·target·별칭/import/graph 수용 경계와 다른 후속 UI는 별도로 유지한다.
전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달 완료를 뜻하지 않는다.
사용자 프로젝트·실제 계정·유료 추론은 사용하지 않는다.

## 커밋 후 독립 checkout·새 교차 패키지 완료

실행 소스는 `12d252e8e413c01cfa90c07db83ef191f2eb03f7`이다. 독립 checkout에서
기존 LF/CRLF 설정을 유지한 동일 Git blob·clean 상태를 확인했고 Native Release는
warning/error 0이다. 같은 함수 결합 후보·실제 API·독립 창 UI·오버라이드 보호의
4흐름/13확인이 통과했다. root solution Release와 별도 MCP Release도 warning/error
0이다. 대형 검사는 모두 순차 실행했다.

같은 소스로 새 Windows x64 패키지를 RAM에 생성했다. manifest 2,343항목,
marker 포함 2,344파일/132,758,267바이트의 파일 집합·전체 해시, 현재 Native DLL/
제품 소스와 7개 Core DLL 일치를 확인했다. manifest SHA-256은
`7e1ae8584596aac3caae9aa782ee80435971118a3bf15859a5d7f35e5e69eeb2`다.
기존 SDK 없는 runtime fixture를 읽기 전용 재사용해 패키지의 managed 엔진 웹
기동·무관한 cwd·74리소스·synthetic profile/override 보존과 변조·DLL 누락 거절을
확인했다. 패키지 안의 새 backend 후보 검사 5건도 통과했다.

전체 manifest·fixture·로그 증거를 보존한 뒤 이번 검사가 직접 만든 RAM 패키지만
제거했다. 이전 보관 패키지/SDK·기존 자료를 삭제하지 않았으며 새 배포 파일을
보관·전달한 결과가 아니다. 패키지 단계 최저 디스크 여유 144,142,336바이트,
OOM/oom_kill 0이다. 이후 커밋은 결과 문서만 바꾸므로 실행 코드는 위 소스와
동일하다. 실제 Windows apphost/WebView2·모바일 기기 실행·Library 전달은 미검증이다.
[checkout·패키지 증거](evidence/v536-information-shared-output-return-mix/package-clean-verification.json)에 정확한 단계·소스·해시·한계를 기록한다.
