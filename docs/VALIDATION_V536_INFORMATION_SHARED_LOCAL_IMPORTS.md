# v536 공유 계약 편집: 변경하지 않는 로컬 호출 — 2026-10-25

기존 정보 창에서 여러 함수의 계약을 편집하고 한 번 저장할 때, 각 함수의
일반 C# 노드와 공유 Blueprint 호출자가 **변경하지 않는 로컬 함수**도 사용하면
Batch의 import 일괄 차단 때문에 저장할 수 없었다. 같은 원래 데이터에 대한
단일 함수 closure 두 개는 유효하고 그룹만 거절되는 것을 수정 전에 재현했다.
이 좁은 결합 경로를 연결하며 원본 v536 UI/CSS·권한·C# 원문·계약 ID는 유지한다.

## 지원 경계

- 기존 2~8개 직접 소유 함수의 공유 계약 단위에서, 선택 밖의 같은 팩에 있는
  직접 함수 선언을 읽기 의존성으로 유지한다. import의 ID·타입/순서/역할/반환이
  원래 선언과 맞아야 한다. 누락·낡은 import·외부 팩·상속 함수 선언은 거절한다.
- 기존 직렬 code/export callee의 C# 노드가 이 계약을 import하거나 call/export
  caller에 선택 밖 로컬 호출이 함께 있어도 된다. C#·alias·노드 ID·실행 순서는
  유지한다. 선택 함수 사이의 callee 의존성과 nested/whole/native/postCall은
  이 경로에 추가하지 않는다.
- 각 closure를 원래 source에서 검증한 뒤 기존 내부 overlay에 합친다. 선택 밖
  호출도 전체 graph 비교에 포함된다. 앞선 생산자의 명시 출력 대응만 기존
  semantic binding으로 전파한다. hash만 갱신하거나 C#·변환을 추측하지 않는다.
- 미선택 로컬 선언의 실제 파일도 기존 closure 관측에 포함하며 실제 변경은
  단일 후보/CAS로 거절한다. 이 fixture의 미선택 helper 함수·구현·본문은
  업데이트나 저장 그룹에 포함하지 않는다. 실제 영향을 받는 caller는 기존의
  명시적 선택과 원래 hash로 검증한다. receipt·Undo·취소·재시작·Review/Confirm은 기존 경계다.

## 격리 fixture와 검사

`v536_information_shared_local_imports_fixture.py`는 기존 두 반환 타입 fixture에
`StableHelper(long)->long`과 일반 C# 구현을 추가한다. 두 C# 노드가 같은 helper를
사용하고 공유 caller의 마지막 별도 호출도 이를 사용한다. B.return(long)을
소비하던 별도 호출은 사용자가 명시한 B.count(long)로 대응한다. 새 double 반환
writer는 각각 root.real을 선택한다. C# 계산/원문·helper 선언/구현/본문·정확한
64비트 값·한글·부모/외부 자료는 보존한다. 사용자 프로젝트·계정은 사용하지 않는다.

순수 검사는 요청/hash 불변·미선택 관측·동일한 역순 결과·호출/원문 보존과,
누락/외부/낡은 import·선택 callee 교차 의존·원래 stable 호출 변경·마지막 writer
오류·미선택 선언의 실제 변경에서 전체 미적용을 확인한다.

새 native 검사와 기존 API/UI harness를 같은 fixture로 재사용한다. API/UI에는
`CONFECTORY_SHARED_LOCAL_IMPORTS=1`을 설정한다. 설정하지 않으면 이전 반환 fixture다.
기본/독립 화면의 취소·Undo/Redo·미저장 복원·Save·쓰기 실패/재시도·물리/live 경합·
응답/결과조회 유실 뒤 settled 조회·프로젝트 전환·cold·Review 취소/Confirm을
검사하고 최종 파일도 다시 읽는다. 원본 460px 정보 창과 `결과` 핀의 실수 표시,
기존 원본 상세창/매핑창을 재사용한다. 새 UI를 만들지 않는다.

첫 빌드는 SDK CLI home 환경 변수를 빠뜨려 읽기 전용 홈에서 시작 실패했다.
stderr를 보존하고 기존 SDK 환경으로 재실행한 Native Release는 warning/error 0이다.
검사를 약화하거나 환경 설정을 바꾸지 않았다.

경합 UI의 제품/checkpoint/입력 검사는 통과했지만 조기 종료 때 진행 중인
Playwright route 콜백이 취소되는 경고가 있었다. test harness에서 조기 종료 전에
자신의 route 완료를 기다리고 browser를 닫도록 정리했다. 제품이나 검증 조건은
바꾸지 않는다. 조기 종료 네 경로의 재검증과 최종 clean checkout/새 교차 패키지
결과는 아래 기록과 evidence JSON에 추가한다.

## 고정 잔여

8행 전체 완료가 아니다. 입력/out/반환/구조의 동시 변경, 값 입력 수·ref/역할/순서,
수동 최종 C# 본문·혼합 native target, 중첩/private/whole/postCall,
copy/상속/등록/owner 속성이 섞인 여러 closure, 현재 scalar 밖 타입은 남는다.
기존 여러 직접 Blueprint target 한도를 native target 지원으로 표현하지 않는다.
다음 복합 경계는 모든 최종 계약과 **동일한 사용자의 수동 C# 본문**을 결합
검증하는 것이다. 자동 재작성/무조건 hash 갱신을 하지 않으며 기존 구현 요구를
사용자 설계 결정 탓으로 돌리지 않는다.

7행 독립 copy 새 계약/ID/기능/호출 재지정은 별도 답변 대기다. 이번 구현은 그
정책을 사용하지 않는다. 9행 named 정보/참조/외부 함수 타입·표시명/native ID 분리,
I6/B2·A4~A6·M4/M11/M12와 Helper 실제 편집 도구도 별도다. 전체 UI·실제
Windows/WebView2·모바일 기기 실행·Library 전달은 미완료다.

## 집중 결과

11흐름 27체크(순수4/API5/UI18)와 기존 다섯 공유 경로 영향 18체크가
통과했다. 조기 종료 정리 뒤 네 경로 8체크도 경고 없이 재검증했다. 제품
assert를 대체하거나 낮추지 않았다. 기본/독립 창의 460px 크기, 원본 카드 및
상세창/매핑창을 실제 화면과 비교했다. UI/CSS 원본은 미변경이며 74개 고정
리소스 hash/size가 맞았다. source/profile/draft/로그/스크린샷은 로컬 scratch에
보존했고 공개 근거에는 검증 JSON과 격리 화면 두 장만 포함한다.

200ms 샘플 메모리 최대 16944295936 B, workspace 최소 378572800 B였다.
OOM/oom_kill은 0이다. 순간 전체 peak를 보장하는 수치는 아니다. 기존 파일을
추가 삭제하지 않았으며 이번 실행의 RAM fixture는 재생성 cache/output을 제외한
source/profile/증거 보존 후 자신의 새 RAM 경로만 정리했다. 새 교차 패키지와
clean checkout 결과는 최종 기록으로 덧붙인다.

## Clean checkout 및 새 교차 패키지

구현 commit `a08949fa2ff2c35633cae8bef4f80af3f3c0ee9b`를 기존 독립 checkout에
fast-forward하고 Native Release를 다시 빌드했다(warning/error 0). 순수4/API3/
독립 UI2의 9체크가 통과했고 두 checkout은 clean, 각각 74개 리소스의 고정
hash/size가 맞았다. 새 전체 clone이나 기존 파일 정리는 하지 않았다.

같은 commit에서 solution 및 별도 MCP Release(warning/error 0), 새 Windows x64
교차 패키지를 생성했다. 2,343개 선언 파일+marker 총 2,344개, 132746581 B이며
manifest SHA-256은 `0339eb04538fabe2f5d1bc22845079ce0dc4177d7bb87e09d785f0b1df9ace5a`다.
전체 file set/hash, 현재 Core DLL 7개 복사본·Native DLL·제품 소스가 일치하고
symlink는 없다. 패키지 안의 Native로 새 순수 검사 4체크도 통과했다.

별도 cwd/SDK 없는 정확한 runtime에서 패키지의 관리형 엔진 웹을 실제 기동했다.
74개 리소스·최소 로그인 화면, 변조/의존 DLL 누락 거절과 기존 fixture 프로필/
명시 override를 확인했다. Windows apphost/WebView2 실행이나 실제 로그인을
했다는 뜻은 아니다. 실제 Windows·모바일 기기·Library 전달은 여전히 미검증이다.

이번 새 RAM 패키지는 전체 manifest와 fixture/profile/로그/화면 증거를 보존한 후
정확한 새 경로의 identity/dir_fd 경계로 정리했다. 다운로드/전달 가능한 보관
패키지가 아니다. 기존 보관 패키지(e827a52 코드, manifest `9d8f3fa8…`)와 SDK/
재사용 runtime·기존 cache/outputs는 그대로다. 일반 builder는 이번 Windows 엔진
생성물을 디스크에 남기며 이를 무단 정리하지 않았다. 패키지 단계에서 workspace
약 13.3 MB가 사용됐고 최종 여유는 약 344 MiB였다. 샘플 메모리 최대
17014001664 B/limit17179869184 B, OOM/oom_kill 0이며 모든 검사는 순차 수행했다.

근거: `docs/evidence/v536-information-shared-local-imports/`의 focused/package-clean
JSON과 화면 두 장. 전체 실행 로그/프로필/fixture/manifest는 로컬
`/workspace/scratch/v536-shared-local-imports/`에 보존한다. 최종 검증 기록 추가는
문서/JSON만 변경하며 테스트한 구현과 UI 실행 소스는 위 commit과 같다.
