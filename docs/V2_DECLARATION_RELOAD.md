# V2 선언 재조회에서 미적용 입력 버리기 확인

## 실제 누락과 기존 의미

현재 기준은 저장소 v666과 [고정 수용 목록](V666_ACCEPTANCE.md)의 V2 안내·입력 보존이다.
`declarations.js`의 고급 선언 폼은 native 어댑터이며 원본 Site에 같은 이름의 버튼이 있다는
뜻은 아니다. 기존 `현재 초안 다시 읽기`는 미적용 폼 입력을 버리고 공유 초안을 보여 주는
취소 경로로도 쓰였다. 이전 게시 엔진에서 이름을 입력한 뒤 이 읽기 버튼만 눌러 입력이
확인 없이 사라지는 것을 실제 UI로 재현했다.

## 지원 경계

- 입력 없는 재조회는 기존 readonly inspect/openEditorView를 바로 호출한다. 미적용 선언
  입력이 있으면 기존 공통 modal로 버릴 입력이 있음을 알리고 명시 확인/취소를 받는다.
  이 확인은 private 입력 버리기이며 최종 소스의 Review/Confirm이나 권한 승인이 아니다.
- 취소/Escape·닫기는 native 재조회나 입력 삭제를 하지 않는다. 명시 버리기는 성공한
  재조회 뒤 승인한 바로 그 창의 변하지 않은 입력 snapshot만 지운다. 기존 입력을 버리고
  독립 선언창을 해제하는 경로는 유지한다. 무조건 보존으로 바꿔 취소 경로를 막지 않는다.
- 현재 project·창 객체·owner·독립 view 연결을 전후 확인한다. 프로젝트/대상 변경·창 닫기와
  조회 실패·응답 유실에서는 입력을 지우거나 이전 창을 재개하지 않는다.
- 폼 편집의 transient epoch와 record/값 snapshot을 함께 비교한다. 같은 텍스트로 돌아온
  새 편집(ABA)도 확인 전이면 승인되지 않으며 조회 응답 중이면 보존한다. 새 입력의
  revision/hash를 현재 원본으로 자동 재기준화하지 않는다.
- 기존 Apply의 exact revision/hash CAS와 공유 초안·원자 Save·Review/Confirm·권한·부모/외부
  원본·ID/계약/연결·원래 C#·공유 Undo는 그대로다. 재조회가 새 공유 Undo나 source 쓰기를
  만들지 않는다. private 입력의 cold/프로젝트 격리는 기존 presentation 수명을 따른다.

일반 primary 선언 폼과 독립 declaration view의 공통 경로다. 명시 확인과 반복/실패/늦은
응답·cold/프로젝트 왕복, 독립 모듈 이름/미적용 계약 입력을 검증한다. 형식별 가능한 모든
입력 조합을 새 필수 항목으로 늘리지 않는다. 원래 버튼과 레이아웃/CSS를 바꾸지 않고
기존 modal/소유 cleanup을 재사용한다. [정확한 delta](v666-declaration-reload-delta.json)를 따른다.

## 우선순위와 고정 잔여

현재 Run은 실제 소유 process/프레임 제어 IPC를 제공하지만 내장 surface/audio provider는
없다. RenderInput은 native surface의 사각형/텍스트 Draw/Pump이며 Run으로 프레임을
전달하는 계약이 아니다. DISPLAY/Wayland/Xvfb·오디오 장치도 없어 모의 장면/소리를 실제
backend로 표시하지 않는다. V6/V7은 소유 자산 저장/권한/이력과 실제 자료 adapter가
선행한다. 이 단위는 그 저장/권한 정책을 임의로 만들지 않고, 이미 갖춰진 선언 계약에서
재현한 입력 손실을 먼저 막는다.

V3–V7 팩/backend·V8 실제 화면/오디오, V9 신원/가시성 adapter와 구체적 원본 근거가 있는
추가 읽기, 종류 C# 표현/사용중 삭제 대응·V1/V2 후속은 고정 잔여다. 깊은 graph 전체 검색을
새 필수 요구로 추가하지 않으며 M11/M12/M4는 구체적 회귀 없이 재개하지 않는다. 3D/권한
별도 팩·이동 연출과 작업 실행 분리·명시 async caller 규칙을 유지한다. 실제 Windows/
WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 교차 패키지와 구분한다.

최종 독립 LF/CRLF·패키지/전체 복원·실패 수명관리 결과는 검증 마감 기록에서 확정한다.
