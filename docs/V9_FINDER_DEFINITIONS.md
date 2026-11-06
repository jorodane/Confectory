# V9 소유 정의 구조와 종류 항목 검색

저장소 v666 ZIP의 `Confectory-v666/dist/app.js`에서 `openWorkspaceFinder`는 글자 모드에
배치되지 않은 `project.objects`의 `workspaceSearchText(object)`도 포함한다. 기존 설명·Data
읽기만으로는 정보의 필드/타입, 함수 서명과 종류 항목 이름이 빠진다. 이번 단위는 이 구조
정보를 같은 검색과 원래 소유 선언 열기 경로로 연결한다.

## 지원 범위

- 배치하지 않은 정보/선언의 직접 필드 이름·타입·카디널리티·종류, 함수의 매개변수 이름·
  타입·ref/out 표시·반환 타입, 정보 종류의 항목 이름을 검색한다. 원래 Data·설명·유효 상속
  값 검색과 정확한 큰 정수/Unicode·동일 표시명/qualified ID 처리는 유지한다.
- 새 `finderContent(ids)`는 기존 active ProjectContext와 `EditWorkspace.Read`의 직접 소유
  unit/경로 검사를 재사용한다. namespace·등록 종류·1~64개의 유일한 ID와 인자를 검증하고
  기존 Data 읽기에 parser가 확정한 구조 텍스트만 덧붙인다. 추가 임의 파일·별도 C# 본문·source
  location·등록 외부 원문을 읽지 않으며, 구조 투영에도 포함하지 않는다. 종류 항목 ID/아이콘 payload도 반환하지 않는다.
- 표시용 텍스트는 구조 JSON의 내부 key 대신 선언된 이름/타입만 담는다. 종류 항목 결과는
  원래 종류 정의 전체를 연다. 항목 ID·순서·값·원본 C#과 실행 분기 계약을 변경하지 않는다.
- 파싱할 수 없는 정의는 해당 row만 unavailable로 표시한다. 확인되지 않은 내용을 빈
  전체 결과로 취급하거나 검증되지 않은 원문을 fallback으로 검색하지 않는다.

## 기존 계약과 저장 경계

기존 `browserElements`와 `editBrowserElement`의 지원 종류·인자·편집 거절은 그대로다.
종류를 일반 Browser Data로 편집할 수 있도록 바꾸지 않는다. `Confectory.AISettings` 내용
조회 거절과 실제 프로젝트/소유권 검사를 유지하며 계정/권한 정책을 추가하지 않는다.

읽기 중 선택/편집 입력과 draft를 유지하고 source 재조회 전후의 revision/hash를 확인한다.
검색 전용 읽기는 PackSnapshot/선택/Review를 새로 만들지 않는다. 검색 결과는 기존 transient
색인 수명을 사용하며, 읽기 중 Enter·반복/닫기·응답 지연/실패·재시도·cold·다른 프로젝트
세대·Workspace 전환의 보호를 재사용한다. source/계약을 저장하는 새 경로는 없다.

정확한 변경은 [delta](v666-finder-definitions-delta.json)로 제한한다. 원본 CSS/팝오버·배치
Ctrl+F·source authoring·Run과 Core/targets 및 모든 `.celem` 계약은 그대로다. 기존
Review→Confirm·최종 CAS·권한·override 원계약·완료된 M11/M12/M4와 저장 복구를 보존한다.

## 유한 잔여와 환경

이번 경계는 직접 선언된 필드/서명/종류 항목과 기존 Data 표현이다. 원본 객체의
`functionDefinition.body`처럼 보관된 구현 본문의 깊이/문자 한도 내 검색은 별도 읽기 경계다.
임의 파일 전체 스캔·모든 graph 깊이를 새 필수 요구로 만들거나 타입/문맥 조합을 늘리지 않는다. 참가자/Helper·연락처/대화는 V4/V5 실제 신원/가시성, office 검색은 V3 표시 팩에
의존한다. 종류의 C# 실행 표현/사용중 삭제 대응 정책은 이번 읽기로 결정하지 않는다.

V6/V7 자산과 V8 내장 surface/audio provider는 고정 잔여다. 현재 Run의 소유 프로세스/제어
경계는 있지만 내장 화면 전달·오디오 provider 계약과 DISPLAY/Xvfb/오디오 장치는 없다.
시연 화면/사운드를 실제 renderer/backend 성공으로 기록하지 않는다. 3D/권한 별도 팩과
이동 연출/실행 분리·명시 async caller 규칙도 유지한다. 실제 Windows/WebView2·모바일·
DPI/IME·전체 UI·Library/Space 전달은 교차 패키지·Chromium 검사와 별개다.

[최종 43단계(신규 43·재사용 0) 검증](VALIDATION_V666_FINDER_DEFINITIONS.md)을 통과했다.
