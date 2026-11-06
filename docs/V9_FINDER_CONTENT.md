# V9 배치하지 않은 소유 선언의 내용 찾기

기준은 보관한 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/app.js`다. `openWorkspaceFinder`는 글자 검색에서 배치되지 않은
`project.objects`에도 `workspaceSearchText(object)`를 적용한다. 현재 구현은 시연 객체 대신
활성 프로젝트의 기존 소유 선언 목록과 Browser Data 읽기 표현을 연결한다.

## 이번 사용자 흐름

- 검색 버블 → 글자 → 검색어 입력으로 소유 선언의 설명과 Browser Data가 노출하는 값을 찾는다.
  현재 탐색기가 허용한 qualified ID만 기존 `browserElements` 읽기에 64개씩 전달한다.
  객체의 상속된 유효 값과 복합 문자열도 기존 Describe 표현을 사용한다.
- 문자열은 Unicode를 복원하고 정수는 JSON 숫자의 원래 표기를 유지한다. 큰 정수를
  JavaScript Number로 반올림하지 않는다. 깊이 4/20,000자 경계와 이미지 payload 제외를
  적용한다. 결과는 텍스트 DOM으로 표시한다.
- 동일한 표시명의 서로 다른 선언도 ID를 유지한다. 결과 선택은 기존 정의/속성 열기
  경로를 사용한다. 값 조회만으로 현재 선택이나 개인 입력을 바꾸지 않는다.
- 실제 draft/목록 기준이 바뀌면 이전 색인을 폐기한다. 읽는 중에는 결과 활성화와 Enter
  재생을 막고, 실패/미지원/일부 확인을 구분한다. 실패는 검색어를 보존하며 명시적으로
  다시 불러올 수 있다. 확인되지 않은 내용을 전체 일치 없음으로 보고하지 않는다.
- 닫기/빈 검색/모드 변경/프로젝트·Workspace·view 세대 변경은 일시 색인을 폐기한다.
  늦은 응답과 남은 배치가 이전 검색을 복원하지 않는다. 검색어·검색 결과·읽은 값은
  개인 presentation 저장에 추가하지 않는다. 프로젝트가 같은 namespace/ID를 써도 격리한다.

## 저장·권한 경계

`packs/editor-home-model/TableCommand.csbody`의 기존 `browser-elements`는 활성 프로젝트 namespace,
1~64개 ID와 지원 종류를 검증한다. 직접 소유한 `object/schema/function/implementation/
module/category/concept`의 기존 Data/metadata 표현만 읽는다. `Confectory.AISettings`는
기존 설정 내용 조회 거절을 유지하며 새 자격증명이나 접근 권한을 만들지 않는다.
등록 외부·부모 원문이나 디스크 경로를 직접 읽지 않는다.

새 native endpoint/캐시 저장/프로젝트 쓰기는 없다. 검사는 생성 fixture의 별도 기존
`editBrowserElement` 호출로 실제 draft 변경과 stale CAS 거절을 확인하되 Confirm하지 않는다.
UI 검색 요청에 편집/Review/Confirm/실행 endpoint가 없는 것과 원본 bytes 보존을 확인한다.
원래 팝오버·CSS·배치 Ctrl+F·C# bytes·override 계약·권한·최종 CAS·M11/M12/M4·완료된
저장 복구·Run 제어는 그대로다. 정확한 변경은 [delta](v666-finder-content-delta.json)로 제한한다.

## 유한 잔여

이번 범위는 기존 Browser Data 표현이다. 원문 C#/그래프 구조의 전체 검색과 기존
`browserElements`가 받지 않는 종류(Enum 등)의 내용은 별도 adapter 경계이며 일부 확인으로
표시한다. 기존 이름/종류 검색은 유지한다. 참가자/Helper·연락처/대화는 V4/V5 실제 신원과
가시성, office 검색/방 이동은 V3 표시 팩을 선행으로 한다. 이동 완료는 작업 실행 조건이 아니다.

Run 내장 surface IPC와 audio provider는 아직 없다. 이 환경에는 DISPLAY/Xvfb/오디오
장치도 없어 모의 화면·음성을 실제 backend 성공으로 기록하지 않는다. V8 렌더/오디오,
V6/V7 자산·편집, 기타 고정 팩/backend·종류 결정·V1/V2 잔여는 확대하지 않고 유지한다.
Linux .NET/Chromium·Windows 교차 패키지/복원 검사와 실제 Windows/WebView2·모바일·
DPI/IME·전체 UI·Library/Space 전달을 구분한다.

[최종 39단계 검증(신규 39·재사용 0)](VALIDATION_V666_FINDER_CONTENT.md)을 통과했다.
