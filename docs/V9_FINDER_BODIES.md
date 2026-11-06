# V9 직접 소유 C# 본문 검색과 정확한 대상 열기

저장소 v666 ZIP의 `Confectory-v666/dist/app.js`에서 `workspaceSearchText(object)`는
`object.functionDefinition.body`도 글자 검색에 포함한다. 기존 정의 구조 검색에는 실제
구현 본문이 빠져 있었다. 이번 단위는 이미 등록된 직접 소유 C# target 본문을 검색하고
사용자가 선택한 바로 그 target을 기존 원문 편집 창으로 여는 흐름이다.

## 지원과 읽기 수명

- 구현의 C# target마다 별도 결과를 표시한다. 자동 target 선택·C# 실행·소스 재작성은 하지
  않는다. 기존 요소/설명/Data/필드·서명/종류 항목 검색과 배치 Ctrl+F를 유지한다.
- 기존 active ProjectContext·namespace·소유 unit 등록을 사용한다. native `bodyDeclarations`는
  선언된 소유 C# locator만 해석하며 본문을 읽지 않는다. 새 `ReadBoundedBody`가 등록 unit의
  예상 locator·프로젝트 경계·링크 보호를 확인하고 기존 bounded snapshot으로 읽는다.
- 파일/구현 요청당 최대 1MiB, 최대 64개 읽기 시도 안에서 성공한 본문 전체를 검색한다.
  구현별 요청을 분리해 다른 구현이 예산을 소진하지 않는다. 20,000자 뒤의 유효 본문도
  검색한다. 초과·누락·관측하지 않은 locator·Blueprint 본문은 부분 결과임을 표시한다.
- 원본 `Read`와 같이 최초 읽기는 baseline/original/draft를 지연 적재할 수 있다. UTF-8 BOM과
  CRLF를 포함한 raw baseline을 보존하며, 검색은 현재 working-copy draft를 사용한다.
  외부 파일을 실시간 재스캔하지 않는다. 외부 변경은 기존 source conflict·최종 CAS에서
  확인한다. 읽기로 source 파일·이력·Review/Confirm을 저장하지 않는다.
- 읽기 전후 owner/body revision·hash를 확인한다. 대상 열기는 owner/target/본문 receipt를
  다시 검증하고 기존 명시 선택 경로를 사용한다. stale·변조·다른 프로젝트 receipt는 거절한다.
  경로 인자를 클라이언트에서 받지 않으며 private 미적용 원문 입력을 덮어쓰지 않는다.
- 필터/페이지 밖에서 수정한 본문도 기존 History의 가벼운 readonly version 관측으로 색인을
  갱신한다. 열린 검색의 수정·Undo·Redo와 동일 내용으로 돌아온 ABA를 revision으로 구분한다.
  검색을 닫거나 프로젝트 세대가 바뀌면 본문 색인을 폐기한다.

## 보존 경계와 검증

`ReadBoundedBody` 계약과 Main/Verify/VerifyShell의 명시 provider 연결을 추가했다. 기존
공개 실행/override 계약·원래 C# bytes·핀/연결·권한·부모/등록 외부 원본·Review→Confirm·
원자 저장/최종 CAS는 유지한다. 기존 HTML/CSS/팝오버·레이아웃·Run과 완료 M11/M12/M4는
변경하지 않는다. [정확한 변경 seal](v666-finder-bodies-delta.json)을 따른다.

개발 중 실제로 필터 밖 본문 변경 후 열린 색인이 남는 결함을 재현해 위 version 관측으로
수정했다. 수정·Undo·Redo·ABA 거절을 집중 확인했다. entry provider 누락과 검사 등록/인자
문제도 고쳤으며 개발 실패를 최종 통과 근거로 계산하지 않는다. 최종 동결 코드의 독립
LF/CRLF·패키지/전체 복원·실패 수명관리 결과는 검증 마감 기록에서 확정한다.

## 유한 잔여

직접 등록한 소유 C# 본문 흐름의 완료이며 검색 전체 완료는 아니다. 원본의 graph 등 다른
본문 표현은 기존 깊이/예산 내 읽기 adapter 잔여다. 임의 파일 전체 탐색·모든 graph 깊이·
새 타입/문맥 조합을 필수 작업으로 늘리지 않는다. 참가자/Helper·연락처/대화는 V4/V5의
실제 신원/가시성, office 검색은 V3 표시 팩에 의존한다. V6/V7 소유 자산과 V8 내장 surface/
audio provider도 고정 잔여다. 현재 DISPLAY/Xvfb/오디오 장치와 해당 내장 provider가 없어
모의 화면/사운드를 실제 renderer/backend 성공으로 기록하지 않는다.

3D/권한 별도 팩·이동 연출과 실제 실행 분리·명시 async caller 규칙을 유지한다. 종류 C#
표현/사용중 항목 삭제 대응은 별도 정책 잔여다. 실제 Windows/WebView2·모바일·DPI/IME·
전체 UI·Library/Space 전달은 교차 패키지/Chromium 검사와 구분한다.
