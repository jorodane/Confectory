# v536 공유 함수의 입력/out 타입 동시 편집 — 2026-10-25

정보 한 창에서 여러 함수의 값 입력과 out 출력 타입을 함께 바꾸고 한 번
저장하는 기존 조작을 연결한다. 단일 함수는 이 조합을 처리했지만 기존 Batch는
입력/출력 타입 그룹을 분리하여 거절했다. 같은 격리 데이터에서 단일 closure
두 개의 성공과 그룹 거절을 수정 전에 재현했다. 레이아웃/CSS·메뉴·권한·C# 원문·
함수/계약 ID는 변경하지 않는다. 7행의 독립 copy 정책과 무관하다.

## 이번 종료 조건과 경계

- 직접 소유 함수 2~8개가 각각 값 입력과 일반 out의 scalar 타입을 모두
  변경하는 그룹이다. 이름·위치·핀 수·역할·반환은 유지한다. 기존 bool/int/long/
  float/double/string 검사와 각 함수의 명시적 원래 핀 대응을 사용한다.
- 변경한 callee 입력의 모든 실제 사용처에는 같은 타입의 현재 값/저장소 또는
  명시 literal을 선택한다. 기존 C# 노드의 매개변수·source는 그대로다. 모든
  변경 출력 writer와 caller의 새 값·기존 연결 해제·호환 출력을 명시한다.
- 직렬 code/export callee와 call/export caller 및 이미 검증한 고정 로컬 import
  경계를 유지한다. ref/역할/핀 수·출력 정의·반환 변경이나 수동 C#·중첩·copy
  조합으로 확대하지 않는다. 입력만 바꾼 함수와 출력만 바꾼 함수의 혼합 그룹도
  이번 종료 조건에 포함하지 않으며 입력을 보존하고 거절한다.

각 원래 closure가 독립적으로 유효한 writer/소비 대응을 가져야 하며, 이를
먼저 검증하고 내부 overlay에만 결합한다. 나중에 연결이 해제된다는 이유로
원래 소비 검사를 생략하지 않는다. 앞선 생산자의
명시 출력 대응이 뒤 호출의 **곧 해제할 입력**을 옮길 수 있다. 이 경우 원래
disconnect 문자열을 새 source에 그대로 쓰거나, 무조건 최신 연결로 바꾸지 않는다.

원래 hash와 선택된 호출을 확인하고, 원래 graph 복제본에 이미 검증한 출력 대응만
투영한다. 선택 호출·나머지 graph가 내부 후보와 일치할 때에만 원래 해제 증거가
그 원래 인자와 정확히 일치하는지 재확인하고 내부 계획의 해제 증거를 대응시킨다.
사용자 계획·물리 source 관측·최종 업데이트 hash·단일 CAS는 원래 기준을 유지한다.
최종 후보 하나만 저장하므로 중간 caller나 첫 함수만 반영하지 않는다.

## 격리 fixture

원래 A.count(long)→B.amount(long), B.count(long)→Caller 반환 연결을 사용한다.
두 amount를 string, 두 count를 double로 바꾼다. caller의 새 string literal과
원래 amount 연결의 해제를 각각 명시하고, 기존 long 소비는 각 함수의 유지
return(long)으로 대응한다. 두 count writer는 root.real(double)을 선택한다.
C# 노드의 long amount는 명시한 정확한 `9223372036854775800`으로 교체 연결한다.
코드 매개변수·계산·본문을 string으로 자동 변환하지 않는다. 해당 long 값과 기존
Power `9223372036854775806`, 한글/emoji·실행 순서·원문을 보존한다.

순수 검사는 역순 편집의 같은 최종 후보와 원래 해제 계획/hash 보존, 명시 bool/
string과 string/double의 조합을 확인한다. 이미 투영한 해제 증거, 중간 hash,
누락/잘못된 해제·사용처·writer·소비 대응, 타입·역할/수/반환·본문/문맥과 실제
source 변경은 전체 미적용이어야 한다. 실제 API/UI는 저장·취소·Undo/Redo·실패/
재시도·충돌·응답 유실 조회·프로젝트 전환·미저장/저장 cold·Review 취소/Confirm과
최종 파일을 검사한다. 실제 사용자 프로젝트·계정·유료 추론은 사용하지 않는다.

`tests/web/v536_information_shared_io_{fixture,native}.py`와 기존 API/UI harness를
사용한다. API/UI에는 `CONFECTORY_SHARED_IO=1`을 설정하고 REPO, ENGINE_REPORT,
기존 mode 및 선택적인 `view`를 전달한다. 설정하지 않으면 기존 반환/local-import
fixture 선택을 유지한다. 원본 460px 창·상세 타입 선택기·입력 연결 갱신창을
재사용한다. 새 레이아웃이나 편집 방식을 만들지 않는다.

## 재검증 중 발견한 검사 기대 오류

첫 순수 검사는 원래 반환 binding의 명시적 `output: return`을 기대값에서 빠뜨려
실패했다. 원래 graph에서도 해당 표기가 존재함을 확인하고 반환 노드 전체가
원래와 같은지 확인하도록 수정했다. 다음 UI 검사는 실제 창 제목이 기존의
`입력 연결 갱신`인데 출력 전용 `호출 계약 갱신`을 찾던 선택자 오류였다. 이
조합의 정확한 기존 제목을 선택하도록 바꿨으며 UI나 기능 검사는 바꾸지 않았다.
실패 로그와 fixture/화면은 로컬 scratch에 보존한다.

응답 유실과 Undo 재시도 검사 준비에서 Browser Enter로 정보 창이 나타나지
않는 실패를 두 번 관측했다. 진단 로그를 보강해 선택 요청 자체가 없었음을
확인하고 실제 배경 상태 응답을 지연하는 격리 검사로 재현했다. 검색 후 카드에
포커스를 둔 상태에서 응답을 풀면, 목록이 다시 그려져 이전 카드는 분리되고
포커스는 BODY가 됐다. Enter가 선택 요청으로 전달되지 않는 실제 화면 결함이다.

`renderObjects`에서 재렌더 전 정확히 카드 자체에 있던 포커스만 기억한다. 같은
프로젝트/창이고 그 카드가 계속 보이며 현재 BODY에 포커스가 있을 때만 같은 ID의
새 카드에 복원한다. 다른 입력이나 창으로 옮긴 포커스를 빼앗지 않고 Data 셀
처리는 변경하지 않는다. 레이아웃/메뉴는 그대로이며 `v508-runtime.js` 한 리소스와
고정 manifest hash를 갱신했다. 수정 후 같은 실제 지연 응답에서 단일 Enter 열기,
검색 입력으로 옮긴 포커스/caret/검색어·checkpoint/원문 보존 두 검사가 통과했다.
자동 재클릭이나 선택/CAS 검사 완화로 통과시키지 않았다.

새 Linux 엔진 생성의 첫 명령은 manifest 확장자를 잘못 지정해 MISSING_FILE로
종료됐다. stderr를 보존하고 실제 `project.cpack`으로 빌드해 warning 없이 통과했다.
기존 빌드·자료를 삭제하거나 설정을 바꾸지 않았다.

## 고정 잔여

8행 전체 완료가 아니다. 입력/out/반환/출력 정의의 더 넓은 동시 편집,
입력 전용/출력 전용 함수 혼합, 값 입력 수·ref/역할·순서, 수동 최종 C#·혼합
native target, nested/private/whole/postCall, copy/상속/등록/owner 속성의 여러
closure 및 현재 scalar 밖 선택 타입은 남는다. 기존 단일 함수 지원과 구분한다.

7행 새 독립 copy 계약/ID/기능/호출 재지정은 별도 답변 대기다. 9행 named 정보/
참조/외부 함수 타입과 표시명/native ID 분리, I6/B2·A4~A6·M4/M11/M12 및 Helper
실제 편집 도구는 별도다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library
전달 완료를 의미하지 않는다. 최종 집중/clean checkout/교차 패키지 결과는 아래
기록과 evidence JSON에 추가한다.

## 집중 검증 결과

집중 11흐름 28체크(순수5/API5/UI18), 기존 일곱 공유 경로 영향 26체크,
실제 지연 응답의 Browser 포커스 회귀 2체크가 통과했다. 마지막 두 준비 실패는
재시도 성공만으로 닫지 않고 포커스 손실을 결정적으로 재현/수정한 뒤 응답 유실·
프로젝트 전환·Undo 재시도 전체를 새 엔진에서 완주했다. 반환 기대/창 제목 오류와
잘못된 빌드 경로를 포함한 모든 실패 로그는 보존했다. 현재 남은 실행 실패는 없다.

Native Release warning/error 0, 새 Linux 엔진 warning 없음, JS syntax 검사 통과.
74개 리소스의 canonical hash/size가 맞았고 변경한 리소스는 포커스 처리의
`v508-runtime.js` 하나다. CSS·레이아웃은 그대로다. 원본 구조와 460px 치수,
실제 명시 값/해제/출력 대응 화면을 확인했다.

200ms 샘플 메모리 최대 17024270336 B, workspace 최소 328507392 B.
OOM/oom_kill 0, 모든 검사 순차 실행이며 순간 절대 peak를 보장하는 수치는 아니다.
이번 새 RAM fixture는 source/profile/draft/로그/화면 증거를 보존한 뒤 자신의
경로만 정리했다. 기존 파일·cache/보관 빌드는 삭제하지 않았다.
근거는 `docs/evidence/v536-information-shared-io/`, 전체 로컬
`/workspace/scratch/v536-shared-io/`다. clean checkout/새 교차 패키지는 이어서 기록한다.

## Clean checkout 및 새 교차 패키지

구현 `567e8a9e610e71db3dea62c0949699f75085706a`를 기존 독립 checkout에
fast-forward했다. Native Release warning/error 0, 새 Linux 엔진 warning 없음.
포커스2/순수5/API3/독립 UI2의 12체크가 통과했고 두 checkout은 clean이며
각각 74개 고정 리소스 hash/size가 맞았다. 새 전체 clone은 만들지 않았다.

같은 구현에서 solution/별도 MCP Release(warning/error 0) 후 새 Windows x64
교차 패키지를 만들었다. 2,343개 선언 파일+marker 총 2,344개, 132749402 B,
manifest SHA-256 `f53f6ade21b5d9a2795c993ccbdb89880e4627d8a02278ae3661d0c61341ac66`.
전체 file set/hash·현재 Core DLL 7개 복사본·Native DLL·제품 CS와 포커스 JS/
WebBundle source가 맞고 symlink는 없다. 패키지 안의 Native로 순수 5체크가 통과했다.

SDK 없는 재사용 runtime/별도 cwd에서 패키지 관리형 엔진을 실제 기동해 74개
리소스와 최소 로그인 렌더를 확인했다. 변조/의존 DLL 누락 거절과 격리 프로필/
명시 override 보존도 통과했다. Windows apphost/WebView2, 실제 모바일 기기,
실제 로그인·추론 또는 Library 전달 검증은 아니다.

이번 RAM 패키지는 전체 manifest와 source/profile/로그/화면 증거 보존 후 정확한
새 경로의 identity/dir_fd 경계로 정리했다. 다운로드나 전달 가능한 보관 빌드가
아니다. 기존 보관 패키지(e827a52 코드, manifest `9d8f3fa8…`), SDK/runtime와
기존 cache/outputs는 유지했다. 새 Linux/Windows 엔진 출력은 일반 builder가
디스크에 남기며 이 출력 세대를 무단 정리하지 않았다. 최종 여유 약 289 MiB,
200ms 샘플 메모리 최대 17097392128 B/limit17179869184 B, OOM/oom_kill 0이다.
모든 검사는 순차 실행했으며 샘플이 순간 절대 peak를 보장하지는 않는다.

새 renderer 검사는 이 단위의 `engine-report.json` 및 `clean-engine-report.json`을
쓴다. 이전 inherited-contract의 엔진 보고서는 옛 UI manifest를 포함하므로 새
리소스 검증에 재사용하지 않는다. 전체 로컬 증거는 scratch에 보존한다.
최종 검증 기록 추가는 문서/JSON만 바꾸며 위 커밋의 실행 코드/UI와 동일하다.
