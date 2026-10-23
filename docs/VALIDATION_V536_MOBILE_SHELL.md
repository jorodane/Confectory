# v536 모바일 공통 화면 연결

기준은 사용자 지정 `origin/main` 196c605의 원본 v536 ZIP이다. 기존 엔진 데이터·Agent 공통 승낙·프로젝트 배치·실제 대화·저장/취소/명시적 확정은 유지한다. 이 묶음은 모바일 웹의 공통 셸이며 Android 지원 추가나 전체 v536 적용 완료를 뜻하지 않는다.

`mobile-shell.js`는 원본의 `(max-width: 1100px) and (any-pointer: coarse), (max-width: 760px)` 전환, 작업자/목록/채팅/⋯ 버튼과 패널을 연결한다. 작업자·채팅은 기존 DOM을 보여주므로 패널 전환이나 폭 변경으로 입력을 재생성하지 않는다. 문맥을 바꾸는 새 상단바에는 이전 패널 상태를 가져가지 않는다. 실제 메뉴는 기존 프로젝트·팩·Yogi·증강·설정 동작에 위임한다. 전투 로그/신문고의 아직 없는 계약은 미지원으로 안내하며 데모 성공을 반환하지 않는다.

원본 공통 셸·모달·메뉴 CSS와 `viewport-fit=cover`를 반영한다. 모바일 Blueprint 흐름을 연결하기 전에 그래프 도구를 숨기는 CSS는 적용하지 않았다. visualViewport 높이/offset 및 safe-area 변수를 사용한다. 가상 키보드 표시는 렌더러 모의 검사와 실제 키보드 검증을 구분한다.

원본 모바일 상단바에는 창 제어 버튼이 없다. 따라서 Windows 브리지의 compact 상태에서는 기존 `chrome(false)`를 사용해 OS 제목 표시줄을 복원하며, 데스크톱 폭으로 돌아오면 원본 커스텀 제목 표시줄을 다시 요청한다. 브라우저에는 가짜 최소화/닫기를 만들지 않는다. 이 전환은 통제된 브리지 응답으로만 검사했으며 실제 Win32/WebView2/DPI/스냅 검증은 하지 않았다.

모달은 기존 소유자의 닫기/취소/Escape와 inert·focus 정리를 따른다. 패널 Escape는 모달·IME 소유자를 가로채지 않는다. 브라우저 history를 임의 추가하거나 시스템 Back을 프로젝트 종료/권한 승인으로 바꾸지 않는다. 프로젝트로부터 돌아가기는 기존 프로젝트 나가기 경로를 사용한다. 모바일 Blueprint 팝오버와 터치 그래프/카드 화면은 다음 묶음이다.

## 검사 기록

최종 통제 렌더러 7건(`mobile-renderer-5.log`, `/tmp/confectory-mobile-renderer-20j0rys8`) 통과: 좁은 화면·브리지 OS caption 복귀, 패널/ARIA와 한글 다중 행 입력 보존, busy 중 목록 차단, mouse 760/761 임계점과 높이 변경, 대화상자 Escape 소유자, 새 header 소유자, coarse pointer 1000px 임계점. 실제 엔진/실제 Windows 검사로 계산하지 않는다.

기존 제목 표시줄 렌더러 10건(`mobile-titlebar-regression.log`, `/tmp/confectory-titlebar-ui-r1s_d_rs`) 통과: 원본 desktop 치수·호스트 명령·프로필 저장/실패 입력·교체 경합·중복 제어 방지·드래그 제외·미지원 브라우저 경로. 실제 Windows 실행 아님.

원본을 390×844에서 새로 렌더한 `original-mobile-common.json`/PNG를 보존했다. 상단바 390×40, 탭 390×32, 작업자 패널 280×804(y40), 채팅 390×804(y40), 메뉴 버튼 높이36이다. 참조 화면의 데이터와 실제 엔진 fixture 데이터는 다르며 픽셀 전체 동일성을 주장하지 않는다.

실제 엔진 3차에서 기본 8건 통과 후 재시작 목록 클릭이 실패했다. 새 모바일 공통 CSS 일부만 연결하면서 원본 후반의 프로젝트 Home 높이/스크롤 보정 두 줄을 빠뜨려 기존 `height:0`이 남았다. 원본 보정 그대로 연결하고 재검증 중이다. 같은 조사에서 발견한 원본 500px 이하 제목 규칙 누락·모바일 목록의 문서 탭 연결·busy 중 메뉴 무응답도 수정했다. 실패를 사용자 Windows 원인으로 단정하지 않는다. 4차에서는 기본 8건 및 수정한 Home 목록 클릭을 통과한 뒤 cold 채팅 입력 표시가 비어 실패했다. 격리 프로필의 presentation에 한글 초안이 보존된 것을 확인했다. `drawWork`가 `showChat`을 먼저 호출하고 그 뒤 `actualWorkspace.attach`에서 입력 맵을 복원하여 이미 만든 textarea를 갱신하지 않던 순서 결함이다. 입력 복원 후 최초 렌더하도록 순서만 수정했으며, 실제 저장 유실이라고 설명하지 않는다. 이후 최종 전체 통합 검사 9건을 모두 통과했다. 정확한 결과는 아래 최종 기록과 evidence에 남긴다. 최초 renderer HTML MIME 누락과 실제 엔진 Home에 없는 패널 shade를 눌렀던 검사는 fixture 오류로 보존했다. Home은 원본처럼 작업자 버튼으로 접는다. 실패를 제품 해결/통과로 소급 기록하지 않는다.

전체 UI·다중 창·이미지/삭제·Blueprint/Browser 잔여·전투 로그/신문고·창별 실행·Windows 교차 패키지·checkout·게시가 아직 남는다. 실제 계정·토큰·유료 추론·사용자 프로젝트를 사용하지 않는다.


## 최종 결과 (2026-10-22 22:38 UTC)

- 실제 생성된 Linux 엔진 + Chromium 통합 **9건 PASS**, session 78466 exit0, `mobile-engine-5.log`, `/tmp/confectory-mobile-engine-p2ygb8i8/evidence.json`. Helper 모달 취소/재열기 입력 보존, 전역 Helper 생성, 실제 프로젝트 생성·배치/전역 분리, 한글 다중 행 채팅 초안, Project Browser 문서 탭/검색 입력, 설정 모달 inert/focus 정리, touch 메뉴 닫기, desktop 복귀, 높이600 viewport, 프로젝트 나가기, 실제 프로세스 재시작 후 목록 클릭·배치와 초안 표시 복원을 확인했다. 테스트 전용 native 생성 경계는 격리 fixture에만 있다. 실제 계정 로그인/모델 응답·과금이나 Windows 폴더 선택 성공을 검증한 결과가 아니다.
- 마지막 재시작 표시 순서 수정 후 9건 전체를 다시 실행했다. 따라서 이전 run3/4의 실패를 assertion 완화로 감추거나, 저장 데이터를 새로 만들어 통과시키지 않았다. 취소·재시작에 사용한 같은 격리 프로필과 파일을 그대로 썼다. 전역 Helper와 프로젝트의 생성 및 Agent 소속은 테스트 중 명시적 실제 UI 동작으로만 설정했다.
- 최종 renderer **7건 PASS** 및 기존 titlebar renderer **10건 PASS**의 범위는 위 기록과 같다. body/메뉴·IME 소유자, busy 목록 차단, 760/761px 및 coarse1000px 분기를 확인했다. 실제 가상 키보드·Android Back·Win32/DPI/터치 하드웨어 검사는 아니다.
- 최종 source와 생성 Linux 빌드 `mobile-build-5.log`/session21703 exit0, manifest **60개 / canonical text 51개** 해시·크기, JS/Python 구문, `git diff --check` 통과. 기존 통과한 백엔드 전체 회귀를 불필요하게 반복하지 않았다.
- 원본 390×844와 최종 실제 엔진의 `geometry.json`에서 topbar/tabs/네 버튼의 x/y/폭/높이가 모두 같았다. 실제 모바일 Home·Workspace·Browser·채팅·재시작 및 desktop PNG를 열어 확인했다. 전체 Browser 내부/다중 창/Blueprint의 픽셀 일치나 기능 완성을 주장하지 않는다. 테스트 중 표시한 일시적 toast도 screenshot에 남아 있다.
- 현재 `work/current` HEAD `cf2fcaef2788eab256e65f171b42e0579d7b1fbd`, WIP202 보존. commit/push/새 Windows 패키지/checkout 미실행. 현재 실행 중 검사·환경 차단·불확실한 push 없음. main/Android/원본 ZIP과 사용자 프로젝트는 보존했다.

다음은 `NEXT_DOCUMENT_WINDOWS.txt`의 원본 문서 분리·일괄 닫기·Pack Manager 위 floating 및 창별 문맥/입력 보존이다. 그다음 모바일 Blueprint 카드/터치와 고정된 나머지 화면을 연결한다. 공통 셸 첫 묶음 완료와 전체 UI/배포 완료를 구분한다.
