# v536 독립 정보 창의 자체 함수 본문

이 단위는 독립 properties 창에서 직접 소유한 정보 함수의 C# 본문·노드 설명·구현 설명을 기존 본문창으로 편집하는 연결이다. I5 전체와 전체 v536 복원 완료를 뜻하지 않는다. 원본 UI의 CSS/HTML 배치와 실행/계정 권한은 변경하지 않는다.

## 연결과 보호

- 서버는 프로젝트·context·정보 ID·properties 모드와 창의 현재 incarnation을 함께 확인한다. 같은 slot을 닫고 다시 열어도 이전 callback의 요청은 유효하지 않다. 원래 준비 완료나 Agent 동의와 관련된 변경은 없다.
- 창마다 본문 input/저장 journal과 서버 receipt의 surface를 구분한다. 첫 본문은 기존 정보 함수의 명시적인 직접 작성에서 만들고, 목록 조회는 해당 정보의 명시된 provide implementation prefix로 제한한다. 다른 정보/다른 본문/내부 그래프/구조 변경은 이 경로에서 허용하지 않는다.
- 기존 단일 후보·checkpoint CAS·전체 source proof와 소유권 검사를 유지한다. 소유권 검사 때문에 읽은 다른 정보/객체의 미저장 화면 입력을 이 본문에 자동 포함하지 않는다. 그런 의존 소스가 실제로 변경되면 서버는 여전히 저장을 거절한다.
- 확정 후 내부 revision만 바뀐 경우에는 실제 Confirm의 후속 처리에서 현재 bound 정보 hash와 완전한 source ID/hash 집합이 그대로인지를 확인한 뒤 편집창 revision을 갱신한다. 다른 소스가 바뀐 경우 입력을 보존하고 자동 갱신하지 않는다.
- 저장 응답이 불확실하면 같은 surface의 원래 요청 receipt를 조회한다. 조회로 확인하기 전에 새 요청으로 덮어쓰지 않는다. 최종 파일은 별도의 Review/Confirm에서만 반영한다.

## 검증 상태

격리 fixture의 로그와 실패/수정 근거는 `/workspace/scratch/v536-information-view-bodies`에 보존한다. 같은 시작 경로를 반복하는 경계 검사 결과는 중복 합산하지 않는다.

| 검사 | 결과 |
|---|---|
| Linux engine-8 build | 경고/오류 0 |
| 새 서버 API engine-8 | 7 PASS: 위조/타창 basis, view 수명, surface별 완료 receipt, cold 재조회, 실제 readonly 의존 소스/본문 변경 차단 |
| 실제 renderer normal engine-8 | 5 PASS: 직접 작성·C# 취소/Undo/Redo·미저장 cold·Save/cold·Review 취소/명시 Confirm·확정 후 같은 창 재편집 |
| 실제 renderer storage engine-6 | 3 PASS: 공통 열기/미저장 cold 2 + 실제 쓰기 거절 후 명시 재시도 1 |
| 실제 renderer conflict engine-6 | 3 PASS: 공통 열기/미저장 cold 2 + 실제 peer 본문 변경/cold 거절 1 |
| 실제 renderer loss engine-7 | 3 PASS: 공통 2 + 응답/결과 조회 유실 뒤 cold 재조회·중복 미적용 1 |
| 실제 renderer context engine-7 | 3 PASS: 공통 2 + Home A/B/A와 은퇴 callback·프로젝트 입력 보존 1 |
| 기존 독립 properties 후보 API | 5 PASS |
| 기존 기본 정보 함수 UI engine-8 | 7 PASS: 생성·핀/이름·cold·확정후재편집·원본 12영역 DOM 대조 |
| 깨끗한 checkout source `0ffb3d113f766c0cc0ed17361152ecfd9a862cc8` | native SDK/Linux engine 경고·오류 0, 별도 API 7 + 실제 renderer 5 PASS, 실제 CRLF pull/fresh LF 및 73리소스·변조/encoding/BOM/binary/budget 거절 PASS |
| Windows x64 교차 패키지·구성검사 | 2,326파일 구성과 runtime-only 패키지 웹 기동·73리소스·최소 로그인 화면·변조/누락 dependency 거절 PASS |

## 확인한 결함

첫 화면 검사에서 구현 목록 조회가 독립 창에 연결되지 않아 첫 본문 생성 후 편집창을 열 수 없었다. 정보에 직접 provide한 구현의 목록만 읽도록 서버와 proxy를 연결했다.

다음 검사에서는 본문과 무관한 primary 창의 미저장 설명까지 소유권 의존 source로 간주하여 Save를 막았다. 화면의 관련 입력과 읽기 전용 검사 의존성을 구분하되 서버 전체 source CAS는 유지했고 실제 의존 소스 변경 거절을 API로 확인했다.

최종 Confirm 후에는 Info source bytes가 같은데 내부 revision이 바뀌어 같은 본문창 재편집이 차단됐다. 실제 Confirm 이후 완전한 source identity/hash 확인으로만 갱신하도록 수정했다. 이어 등록부만 creation 완료 후 의존 목록에서 사라지는 사실도 확인하여 detached read/BatchRead의 등록부 의존성을 계속 유지했다. API에서 실제 Confirm 전후 완전한 ID/hash 동일을 확인했으며 화면의 마지막 재편집/새 checkpoint 저장도 통과했다. 실패 로그는 보존하며 통과로 합산하지 않는다.

응답 유실 fixture의 첫 실패는 실제 의도한 transport-interrupted 대신 한국어 입력 안내를 기대한 assertion 오류였다. 정확한 injected error와 저장 횟수·checkpoint·입력 보존·읽기 재조회 여부를 검사하도록 고쳤다. 보호나 저장 assertion은 제거하지 않았다.

## 원본 대조와 패키지

기존 v536 레퍼런스 함수 카드와 실제 DOM의 12영역 치수·폰트·padding이 정확히 같음을 확인했다. 독립 정보 창은 기존 460px, 본문창은 기존 마크업을 재사용하며 새 레이아웃이나 CSS를 추가하지 않았다. [원본](evidence/v536-information-view-bodies/function-original.png) · [실제](evidence/v536-information-view-bodies/function-engine.png) · [정밀 측정](evidence/v536-information-view-bodies/function-geometry.json) · [독립 본문창](evidence/v536-information-view-bodies/independent-body.png).

로컬 Windows x64 패키지는 `/workspace/artifacts/v536-information-view-bodies/Windows-x64`다. 전체 폴더를 함께 사용하며 Confectory.exe가 진입점이다. 패키지 probe는 Windows PE 구성 확인과 Linux의 실제 managed 엔진 웹 기동이다. Windows apphost/WebView2 실행을 뜻하지 않으며 Library 전달도 하지 않았다. 생성 패키지와 프로필/로그는 Git에 넣지 않는다.

## 재현과 게시 범위

구현 snapshot은 `0ffb3d113f766c0cc0ed17361152ecfd9a862cc8`다. 기존 깨끗한 checkout을 이 snapshot으로 정상 fast-forward한 뒤 native SDK와 Linux 엔진을 다시 만들고 API 7 및 본문 UI 5를 별도로 완주했다. 재현 결과를 root suite와 중복 합산하지 않는다. 원래 source/초안·권한 보호를 약화하지 않았고 생성 패키지·프로필·로그·사용자 자료를 커밋하지 않는다.

Windows 패키지 manifest SHA-256은 `514e117990c3f862a9316a8d738bc84a6d45d96d17a52685ff89849f8339fcf7`다. runtime은 위 구현 snapshot과 같은 코드이며 후속 검증 문서 커밋은 runtime에 포함하지 않는다.

기존 기본 정보 함수 UI의 첫 회귀 실행은 이전 게시 `5521859`에서 이미 활성화한 저장된 함수 삭제 버튼을 여전히 disabled로 기대하던 fixture 때문에 실패했다. 기본 창은 enabled, 아직 미지원인 독립 창은 disabled라는 현재 계약을 확인하도록 고쳤고 생성·핀 편집·재시작·Review/Confirm·12영역 비교 7건을 다시 통과했다. 실제 삭제 보호를 제거하지 않았다.

## 정확한 남은 I5 조작

전체 목록과 완료 조건은 [V536_I5_COMPLETION_CHECKLIST.md](V536_I5_COMPLETION_CHECKLIST.md)에 있다. 독립 모듈 슬롯의 본문 편집/선택/복사, 함수 선언을 남기는 구현만 삭제·복구, 독립 창 함수 전체 삭제·복구, 자체 함수 순서, 연결된 함수의 전체 ABI 변경은 아직 완료가 아니다. Helper의 설명으로 작성은 UI 이후 별도 도구 구현 단계다. 이 단위에서 미지원 버튼을 임의 활성화하지 않는다.

실제 Windows apphost/WebView2, 모바일 기기, 실제 로그인/추론/권한부여 및 Library 전달을 검증하지 않았다. 테스트는 격리 프로젝트/프로필과 Chromium만 사용하며 사용자 자료를 실행·삭제하지 않는다.
