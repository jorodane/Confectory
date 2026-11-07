# V6 프로젝트 자료 사본과 목록

기준은 검증된 v666 ZIP의 `app.js::resourceDatabase`, `importResourceFiles`,
`resourceItems`, `renderResourceItems`, `renderResourceBrowser`다. 원본은 프로젝트
소유 ID로 실제 선택한 File의 사본을 저장하고 원본 파일을 이동/삭제하지 않는다.
브라우저 IndexedDB를 native 권한으로 채택하지 않고 별도 ProjectResources 팩에 연결한다.

첫 단위는 활성 로컬 ProjectContext의 자료 탭·명시적 파일 선택/드롭·목록·이름 검색·
Compact/Data/Preview 표시 크기·선택과 성공 보관본의 재시작 복원이다. 파일명은 표시
metadata이며 실제 경로로 사용하지 않는다. 기존 프로젝트 ID, FileStream CommitPlan의
최종 CAS와 원자 실패/원문 복구를 재사용한다. 저장 위치/역할과 명시 예산은
[팩 계약](../packs/project-resources/README.md)을 따른다.

원본 파일 경로, 다른 프로젝트 ID, 부모/외부 원본·계정/접근권한은 받지 않는다.
선택 파일의 bytes는 메모리에서 확인한 뒤 한 개의 원자 요청으로 보관한다. 소유 선언/C#,
공개/override 계약·실행·Review→Confirm을 바꾸지 않는다. 목록 읽기는 저장소를 만들지 않는다.
원본의 자료 추가는 파일 사본 보관이며 C# 소스의 확정 버튼으로 위장하지 않는다.

실패/응답 유실이면 현재 창의 선택 File과 동일 요청을 유지하고 명시 재시도를 제공한다.
stale CAS를 자동으로 새 기준에 맞추지 않는다. 선택 입력 취소는 이미 저장한 사본의 삭제가
아니다. 임시 bytes/command는 개인 presentation이나 Git에 게시하지 않으며 실제 프로세스
재시작 후 자동 재전송하지 않는다. 아직 보관하지 못한 파일은 재시작 후 직접 다시 선택한다.

현재 공급자의 한 번에1개/파일1MiB·전체4MiB/64개 한계를 표시한다. 원본 자료 폴더·이름 변경/
이동/삭제·복구와 V7의 내용 미리보기/편집은 별도 잔여다. 풍부한 파일 형식을 glyph만으로
지원했다고 표시하지 않는다. V4/V5 권한 backend·Run 고급 출력·초기화 빈 화면 원인 미확정과
실제 Windows/모바일·전체 UI·Library/Space 전달은 이 단위와 구분한다.

현재 최종 코드 검증 전이다. 독립 native 팩31개 예비 검사와 실제 엔진 UI/최종 LF·CRLF/
새 패키지·전체 복원 검증은 완료 후 별도 기록으로 확정한다.
