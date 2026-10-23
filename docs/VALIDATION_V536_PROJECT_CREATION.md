# v536 프로젝트 생성·사이드바 Helper 연결

`196c605`의 v536 원본 `setupProjectCreationSurface`/`createProject`와 프로젝트 생성 스타일을 기준으로 연결했다. 다른 화면과 전체 v536 UI, Windows 배포 완료를 의미하지 않는다. main/Android/원본 ZIP과 기존 미게시 엔진 작업은 보존했다.

## 연결 범위

- 원본의 탭·가운데 스크롤 본문·고정 하단 제어와, 사용 가능한 Helper → 배치 영역의 순서를 사용한다. 탭별 스크롤 위치를 보관한다. 현재 엔진의 실제 부모 폴더 선택·생성·등록/동의 확인·Helper 배치 API를 유지하며 프로토타입의 가짜 경로나 추천 팩을 적용하지 않는다.
- 사이드바 Helper의 실제 HTML 드롭과 클릭은 이 폼의 사적 선택에만 적용된다. 현재 프로젝트를 바꾸거나 채팅을 열지 않는다. Agent/컨텍스트 메뉴 동작은 선택 중 차단하고, 엔진의 고정 채팅·즐겨찾기용 이중 클릭/키보드 핸들러로 새지 않도록 수명을 한정했다. 닫은 뒤에는 원래 동작이 복구된다.
- 원본처럼 sidebar를 이용할 수 있도록 `#app` 전체 대신 중앙 영역을 차단한다. 아직 v508 형태인 엔진의 `#workspace`/chatbar도 v536의 중앙 열에 해당하는 영역으로 처리한다. 각 DOM과 이전 inert/draggable 값을 기록하며 해당 폼이 소유한 상태만 복원한다. 새 화면으로 렌더되면 새 sidebar/중앙 DOM에도 같은 소유권을 적용한다.
- 성공한 native 생성 영수증을 보관한다. Helper 배치 단계 실패의 재시도는 동일 프로젝트의 배치만 진행하며 native 생성을 반복하지 않는다. 자동 Main Helper 생성 식별자도 같은 요청 안에서 유지한다. 실제 생성됐지만 취소/이동으로 배치하지 않은 프로젝트를 삭제하지 않는다. 선택한 프로젝트가 영수증과 다르면 다른 프로젝트에 자동 배치하지 않는다.
- 자체 생성 때문에 발생하는 동일 영수증의 화면 전환은 진행 중인 폼을 유지한다. 다른 프로젝트로의 이동이나 폐기된 폼의 늦은 응답은 재사용하지 않는다. 일반 모달/다른 프로젝트의 창을 유지하는 예외로 확대하지 않았다.
- 프로젝트별 배치·해제, 전역 후보와 실제 Agent 소속, 서버의 기존 plan/apply 토큰·계정/동의/소유권 검사를 사용한다. 폼에서 고른 것만으로 서버 배치나 권한을 적용하지 않는다. 현재 프로젝트에 미배치인 전역 Helper는 sidebar에서 숨기되 배치 후보로 남는다.

## 실제 엔진 검사: 8건

`tests/web/v536_project_creation.py`, 최종 실행 세션 `68102` exit0. 자료는 `/tmp/confectory-create-responsive-3ks_vyd5/evidence.json`, 로그는 `/workspace/scratch/v536-reference/project-creation-4.log`이다.

실제 생성 엔진·프로필·파일 시스템·등록·배치 API와 Chromium을 사용했다. Linux에 없는 native 부모 선택 경계만 별도 복사한 테스트 호스트에서 승인된 임시 디렉터리로 공급한다. 생성은 실제 `NativeRequest` 계약을 호출하며 UI 성공을 흉내내지 않는다. `/fixture/native-create`는 테스트 복사본에만 있고 실제 `packs/browser-host/Serve.csbody`에는 없음을 확인했다. 실제 Windows 폴더 선택/더블클릭 실행이나 사용자 계정 검증은 아니다. Responses 설정은 폐쇄된 loopback 주소와 자격 증명 없는 fixture다. 모델/로그인/유료 호출은 실행하지 않았다.

1. 반복 제출 차단, 실제 생성 영수증, 등록 Agent 소속 Main Helper 배치. 생성 후 중앙 컨트롤·hover·overlay/inert 정리.
2. 실제 sidebar HTML 드롭/클릭으로 후보 선택. 그 단계에서 채팅/프로젝트 전환·Agent/배치 쓰기가 없음을 확인.
3. 실제 부모 선택, 고정 탭/하단 제어, 본문만 스크롤 및 탭별 위치 복원.
4. 생성 후 배치 plan 응답 실패 주입 → 같은 영수증 재시도. 프로젝트/Helper 중복 없음, 다른 프로젝트의 manifest와 전역 초안 보존. 새 화면도 배치 폼이 정확히 차단했다.
5. 현재 프로젝트 배치·해제·다시 배치, sidebar/미배치 후보 구분. 전역 Helper 두 개, Agent 소속 및 전역 입력 보존.
6. native 생성 전 실패와 native 취소. 프로젝트/Helper·배치를 추가하지 않고 취소 후 정상 반응.
7. 취소 후 입력 복구, native 부모 선택 취소 시 기존 경로 유지.
8. 실제 프로세스 재시작. 두 프로젝트·프로젝트별 배치·전역 Helper/Agent 소속·한글 전역 초안 복구. 자동/중복 생성 없음.

실제 native 호출은 `Owned Created`와 `Owned Selected` 각각 한 번이며 fixture에서 1129ms/1073ms였다. 사용자 Windows의 생성 시간 또는 오류 원인을 이 수치로 단정하지 않는다. `pageerror`/외부 요청은 0이다.

## 모달·입력 수명과 원본 비교

`tests/web/v536_project_surface_renderer.py` **8건 통과**, 최종 세션 `42359`, 자료 `/tmp/confectory-project-surface-renderer-65c6df8i`, 로그 `/workspace/scratch/v536-reference/project-surface-renderer-5.log`. 이 부분의 provider/생성 callback은 통제 fixture이며 실제 backend 증거로 합산하지 않는다.

- 선택적 차단·private selection·알 수 없는 Helper drop 차단.
- 이중 클릭/즐겨찾기 키보드 동작이 채팅/설정 변경으로 새지 않음, 종료 후 기존 키보드 동작 복구.
- 다른 모달로 교체 후 오래된 닫기가 새 소유자의 inert/DOM을 해제하지 않음.
- 이전부터 있던 inert 상태 보존.
- sidebar/model 갱신 뒤 새 후보 선택·제거·정리, 이전 draggable 상태 복구.
- scope 변경 시 mutation 없이 퇴장하고 미전송 입력 복구.
- 직접 DOM 제거·새 폼·오래된 닫기의 경합 정리.
- 닫은 폴더 선택기의 늦은 결과가 새 모달을 바꾸지 않음.

동일한 1440×1000 viewport에서 원본 v536과 현재 컴포넌트의 modal/head/tabs/body/footer x/y/width/height를 대조해 모든 항목 차이 1px 미만을 확인했다. modal은 x430/y16/760×820, footer는 y764다. 원본과 현재 컴포넌트/실제 엔진 캡처를 직접 열었다. 실제 엔진의 `v536-create-selected.png`는 탭별 본문 스크롤 복구 후 캡처여서 원본의 스크롤 0 화면과 입력 행의 y 좌표를 직접 비교하지 않는다. 실제 권한 안내는 기존 안내 자리에서 유지하며 원본 제목은 한 줄로 보존한다. 사용자 데이터에 없는 캐릭터 그림/프로토타입 사안은 복사하지 않았다.

마지막 이중 클릭/키보드 경계와 제목 줄 유지의 소규모 변경은 이 렌더러·치수 검사와 최종 Linux 빌드로 검증했다. 실제 8건의 생성/배치/restart 경로를 변경 없이 또 실행한 것으로 기록하지 않는다.

## 조사 중 발견과 검사 보완

실제 생성 첫 검사에서 프로젝트 파일은 만들어졌지만 Helper가 없었다. `drawWork`가 모든 모달을 퇴장시켜 자체 생성 전환까지 취소로 처리한 원인을 확인했다. 현재 폼과 정확한 생성 영수증에 맞는 전환만 유지하도록 수정한 뒤 첫 생성부터 배치 실패/재시도까지 완주했다.

검사 코드의 CSP 문자열 eval은 함수형 대기로 고쳤고 CSP를 완화하지 않았다. 빈 배치 slot과 tail이 같은 index0을 갖는 원본에서 locator가 모호했던 것은 실제 slot을 선택하도록 수정했다. 이 두 검사 오류를 제품 결함으로 보고하지 않는다. 이전 성공 로그와 실패 로그도 보존했다.

## 빌드·범위 한계

최종 생성 Linux 빌드 `3304` exit0. 리소스 59개/정규 텍스트 50개의 해시·크기, 변경 JS/Python 구문과 `git diff --check`를 확인했다. Core/SDK 계약은 변경하지 않았다. 전체 v536 회귀·Windows 교차 패키지·checkout·commit/push는 아직 미실행이다. 실제 Windows/WebView2/IME/DPI/native caption/OS picker와 사용자 계정·모델 성공도 미검증이다. 이미 native 생성이 진행 중인 모든 시점의 창 닫기·프로세스 중단 조합을 검사했다고 주장하지 않는다.

아직 남음: Helper 이미지 생성/저장·이력/폼 내 삭제, 모바일 shell/카드/터치, 탭 분리·다중 창/프로젝트별 저장, Blueprint/요소 Browser의 고정 잔여, 전투 로그/신문고/Yogi의 실제 계약, 창별 실행·내보내기, 전체 시각/통합 회귀 및 Windows 패키징/게시. 이후 순서는 `V536_UI_RESTORATION_SCOPE.md`를 따른다.
