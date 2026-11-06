# V9 직접 요구 기능 이름으로 소유 모듈 찾기

## 원본과 실제 누락

보관 v666 `dist/app.js:4000–4003`의 `workspaceSearchText`는 `methods[].name`을 검색하며,
2641–2643행은 모듈의 직접 기능을 실제 이름으로 표시한다. 원본 helper를 같은 저장 모양에
직접 실행해 확인했다. native에서는 그 인터페이스가 모듈의 직접 `require` 선언이다.

현재 게시 패키지에서 생성한 소유 모듈을 기능 이름으로 검색하면 기능 자체만 나오고
모듈은 빠졌다. 같은 모듈을 기존 인터페이스 편집기로 열면 그 직접 필요 기능 이름이
표시된다. 이미 있던 데이터/필드/함수 서명/종류 이름·C# 본문·정보 기본값 검색과 구분한다.

## 이번 지원 경계

- 기존 `finderContent`의 소유 모듈 정의 배열에 직접 선언한 `require`의 짧은 기능 이름만
  추가한다. 이미 관측한 원문과 `inspect.relations`를 재사용하며 파일이나 실행기를 새로
  읽지 않는다. 표시명 해석을 위해 다른 기능 정의를 가져오지도 않는다.
- `include`·부모·상속 요구 기능을 따라가지 않는다. 다른 선언의 본문/설명·외부 source·
  private ID·경로를 합치지 않는다. 같은 표시명의 모듈도 원래 qualified owner ID로 구별한다.
- 기존 source/owner/revision/hash 전후 확인과 20,000자 부분 색인 상태, 요청 ID 개수·
  종류/namespace·추가 필드 거절을 유지한다. 새 저장 타입이나 권한 정책은 없다.
- 현재 공유 초안의 바뀐 요구 이름과 Undo/Redo는 기존 전역 source-basis 색인 갱신을
  따른다. 찾기 자체는 커서·입력/초안·원본을 바꾸지 않고, 명시 결과 선택만 기존 소유
  모듈 인터페이스 열기를 호출한다. 검색어와 색인은 cold·다른 프로젝트로 재생하지 않는다.

제품 변경은 [정확한 delta](v666-finder-modules-delta.json)의 TableCommand 한 삽입뿐이다.
일반 Browser/Data API와 편집/실행 계약·권한·원본/부모/외부·C# bytes·ID/연결·UI/레이아웃·
Review→Confirm·원자 저장·최종 CAS·Undo는 유지한다. 검색을 위해 자동 Save/Confirm·
계약 보정·상속 원본 열기나 쓰기를 추가하지 않는다. 가능한 관계/타입 조합을 새 필수
검색 기능으로 늘리지 않는다.

## 고정 잔여와 검증 구분

V9 참가자/Helper/연락처는 V4/V5 실제 신원·가시성, office는 V3 팩이 선행한다. V3–V7
팩/backend·V8 실제 내장 surface/audio·종류 C# 표현/사용중 삭제 대응·V1/V2 후속은
고정 잔여다. RenderInput Draw/Pump·Run 제어 IPC는 내장 화면/오디오 전달 계약이
아니며 현재 provider/장치가 없어 모의 성공으로 채우지 않는다. 실제 Windows/WebView2·
모바일·DPI/IME·전체 UI·Library/Space 전달은 교차 패키지와 구분한다. M11/M12/M4와
완료된 보호는 구체적 회귀 없이 다시 열지 않는다. main은 사용자가 검토 후 병합한다.

최종 독립 LF/CRLF·새 패키지/전체 복원·실패 수명관리 결과는 마감 검증 문서에 남긴다.
