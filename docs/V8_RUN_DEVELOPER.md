# V8 Run 개발 메뉴와 실제 프레임 진단

이 문서는 최초 메뉴 단위의 검증 기록이다. 이후 선택적 실제 영상·출력 크기 표시와
미보관 읽기 전환은 [소프트웨어 출력 경계](V8_RUN_SOFTWARE_OUTPUT.md)를 따른다.

저장소 v666 ZIP `Confectory-v666/dist/app.js`의 `setupRunDeveloperMenu`와
`openRunViewport`에 노출된 개발 버튼·디버그 정보 선택·출력 영역을 현재 Run 창에 연결한다.
같은 ZIP의 toolbar/popover/debug CSS를 그대로 추출했다. 별도의 새 화면을 설계하지 않는다.
원본의 모의 장면·브라우저 재생 시계·WebAudio 테스트를 실제 프로젝트 renderer/audio로 채택하지 않는다.

개발 메뉴의 디버그 정보를 켜면 현재 정확한 Run view의 상태와 이미 검증된 FrameControl
관측을 표시한다. 실제 연결이 있을 때만 실행 프레임·running/paused·명령 ACK/sequence와
대기 명령을 읽는다. 프레임은 기존 협력 실행 경계의 완료 횟수이며 렌더 FPS가 아니다.
Int64 프레임 문자열을 부동소수점으로 바꾸지 않아 큰 값도 정확하게 표시한다.
공개 화면에 handle/lease/runtime 식별자·프로세스 secret·원문을 추가하지 않는다.

렌더 FPS·해상도·오디오는 미지원으로 명시한다. 현재 native Run의 내장 surface/audio
backend가 없으므로 해상도 선택·경계/그리드·사운드/테스트는 비활성이고 실행 처리기도 없다.
DOM의 disabled 값을 바꿔도 새 native 권한이나 해당 명령을 만들 수 없다. 해상도 preset
생성/저장·영상 프레임 전달·오디오 출력/제어를 구현 완료로 세지 않는다.

표시 선택은 같은 Run 창의 생존 기간에만 속한다. sibling 창에는 적용하지 않고 탭 왕복은
선택을 보존한다. 실행 상태를 확인하지 못하거나 연결이 사라지면 지난 프레임을 현재 값으로
표시하지 않는다. 실패 전에 예약된 자동 읽기도 오류 여부를 다시 검사해 멈춘다. 기존 명시 재확인만 같은
owner/handle을 다시 관측하며 Start를 재실행하지 않는다.
메뉴는 화면 크기에 맞게 위치하고 최대화/접기/숨김/프로젝트 이탈에 정리한다. 최대화에서
Esc는 열린 개발 메뉴를 먼저 닫고 다음 Esc가 원래 창 크기를 복원한다. 취소된 창의 오래된
checkbox callback은 새 창을 변경하지 못한다. 실제 닫기 성공 뒤 observer/menu를 폐기하고,
닫기 거절은 창·표시 선택·실행·새 입력을 유지한다. 재시작은 개인 창/입력만 복원하며
디버그 선택·lease·프로세스를 복원하거나 자동 실행하지 않는다.

표시 코드는 원본 Run의 실제 query/재시도·소유권/명령 ACK 호출 경계를 그대로 사용한다.
새 API·public/override 계약·권한·C# source·Review→Confirm·최종 CAS 변경이 없다.
3D는 별도 표시 팩이며 Worker 이동은 실행 조건이 아니다. M11/M12/M4는 재개하지 않는다.

남은 고정 범위는 실제 Run surface/render/FPS·해상도/preset의 실행 연결·audio backend,
V3 진행 중 IO의 실제 관측 경계, V4/V5 신원/권한·가시성, V6/V7 자산 저장/미리보기와
V9 참여자/대화다. 기존 검증 한계나 가능한 조합을 별도 필수 기능으로 늘리지 않는다.
실제 Windows apphost/WebView2·모바일·하드웨어·전체 UI·Space/Library 전달은 미완료다.

[검증·보관·공간 기록](VALIDATION_V666_RUN_DEVELOPER.md)과
[정확한 제품 변경](v666-run-developer-delta.json)을 따른다.
