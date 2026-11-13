# 속성 타입 Undo/Redo의 포커스 복원

게시 `1a021f63`의 기본 정보 창에서 기존 속성과 새 속성 초안의 타입 Undo가 필드를 다시 그린 뒤
BODY로 포커스를 옮겼다. 버튼을 다시 지정하지 않고 Ctrl+Y를 누르면 소유 창에 전달되지 않아
Redo가 실행되지 않았다. 원문·checkpoint와 Undo가 남긴 입력은 보존됐으며 재현에서 Save/Confirm하지 않았다.

기존 아이콘 Undo/Redo의 포커스 복원에 타입 버튼을 함께 연결한다. 기존 속성은 같은 소유 창의
정확한 property path, 새 초안은 정확한 definition key를 먼저 사용한다. UI를 다시 그린 뒤
연속 Ctrl+Z/Ctrl+Y/Ctrl+Shift+Z가 같은 컨트롤에서 이어진다. 첫 포커스 지정 뒤에는 다시 클릭하거나
focus를 호출하지 않는 실제 Chromium 키 입력으로 확인한다.

지연된 포커스 복원은 현재 프로젝트·소유 창 인스턴스·schema 인스턴스와 연결된 DOM을 재확인한다.
닫힌 창이나 바뀐 소유 문맥에 포커스를 넘기지 않는다. 기존 composing/input/busy·hash/revision·입력 집합
검사를 유지한다. 아이콘 버튼의 기존 동작과 텍스트 입력/조합 중 키 경계를 별도로 확인한다.
조합 경계의 DOM 이벤트는 모의 검사이며 실제 OS IME를 검증했다는 뜻이 아니다.
창 닫기 경합은 capture 단계에서 닫기가 먼저 처리되면 오래된 키를 거절하고 입력을 유지하는지 확인한다.

변경은 elements.js와 그 파일의 명시 canonical size/SHA256 pin에 한정한다. 다른 resource pin·원래
CSS/레이아웃·리소스 pin 이외 C# 동작 본문·타입/필드/함수 계약·권한·Review/Confirm·CAS와 저장/취소 의미는 바꾸지 않는다.
정보별 struct·종류 enum·모듈 interface와 이전 reader 제약을 유지하며 serialization/receipt 버전이나 migration은 없다.

기본/독립 정보 창의 실제 속성/native 계약 공동 저장, 새 초안의 취소·cold와 기존 아이콘,
저장 실패/재시도·응답 유실·owner/프로젝트 경합·늦은 입력을 해당 흐름으로 검사한다.
새 패키지와 전체 복원, LF/CRLF 결과는 별도 검증 기록을 따른다. 같은 타입 버튼이 없는 다른 창·에디터의
일반 포커스 관리 전체를 완료로 세지 않는다. 실제 Windows/WebView2·기기·IME·전체 UI 전수 검증은 구별한다.
초기 간헐 빈 화면 원인은 미확정이다.

남은 고정7/8행의 다른 복합 계약·속성 구조 편집, opaque/private 명시 C# 계획,
선택 native 의존성과 기존 import/등록 외부 원본 결합은 원래 사용자 조작 단위로 유지한다.
가능한 모든 타입/문맥 조합을 새 필수 항목으로 늘리지 않는다.
