# 공통 아이콘 창의 조합 취소 키 보호

고정 v666 `app.js::editIconValue`의 기호·생성 이미지 선택은 적용에서만 owner 입력에
반영한다. 일반 Escape·닫기는 팝오버 복사본을 취소한다. 현재 native의 공통
`glyph-popover.js::openGlyphPopover`가 완료된 선언/속성/함수/동작/노출 핀 아이콘에
이 흐름을 재사용한다. 기존 아이콘 구현을 다시 만들거나 새 노출 위치를 추가하지 않는다.

게시 4ef098e4의 실제 소유 분류 헤더에서 기호 입력/생성한 로컬 이미지 선택 각각에
`isComposing` 또는 legacy `keyCode=229` Escape를 전달하면 선택창이 닫히고 미적용
복사본을 잃는 네 경우를 재현했다. 원본·체크포인트·적용된 아이콘은 변경되지 않았다.
기호 입력창에 남아야 할 조합 취소가 편집 전체 취소로 잘못 처리되는 별도 결함이다.
이미 마감한 함수 상세/타입 검색의 두 listener는 바꾸지 않는다.

공통 아이콘 창의 Escape listener 한 곳에 기존 UI와 같은 IME guard를 적용한다.
조합 중 기본 동작·포커스를 가로채지 않으며 기호/선택 이미지 복사본을 보존한다.
일반 Escape·명시 닫기·기호 검증/적용·이미지 decode sequence/수명·pointer/scroll/resize·
owner 검증과 레이아웃·콜백은 유지한다. native backend·공개/override 계약·권한·저장
문법·Review/Confirm·최종 CAS와 원본 C#은 바꾸지 않는다.

실제 Chromium DOM에서 네 경우의 입력/미리보기/포커스와 일반 Escape, 반복 닫기·cold,
명시 기호/생성 이미지 Apply·private Undo/Redo·Save·cold·Review 취소/Confirm을 검증한다.
실제 UI 표본은 직접 소유 분류 헤더이며 다른 공통 진입점 전체를 개별 실행했다고
주장하지 않는다. 고정 helper와 call site/저장 경계 불변은 정확한 소스 대조로 확인한다.

이미지는 테스트 canvas에서 생성한 PNG만 사용하며 사용자 개인 파일·외부 자료를
업로드하지 않는다. 조합/키 이벤트는 생성한 DOM 이벤트이며 실제 OS IME·물리 입력·
Windows/WebView2/모바일/전체 UI 검증과 구분한다. 초기 빈 화면과 과거 Agent 준비 지연
원인은 미확정이다. 핀 표시명/native 식별자·고급 ABI·기존 혼합 계약·신원/권한 backend·
종류 표현/사용중 삭제 정책의 별도 잔여를 유지하고 M11/M12/M4를 재개하지 않는다.

[최종 신규29단계·재사용0과 보관/검증 한계](VALIDATION_V666_GLYPH_IME.md)를 따른다.
