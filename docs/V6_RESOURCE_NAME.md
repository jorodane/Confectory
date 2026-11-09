# V6 자료 목록 파일명 활성화

고정 v666 ZIP의 `app.js::renderResourceItems`는 Compact/Preview/Data 모두 파일명에 `data-resource-name`을 부여한다. 첫 클릭은 선택, 하나만 선택된 파일명의 다음 클릭은 260ms 뒤 기존 인라인 이름 편집이며, 수정키 선택·더블클릭 열기를 유지한다.

게시 cd60e4a3의 실제 native UI에서 Compact/Preview 재클릭 누락을 재현했다. F2·우클릭 이름 변경은 이미 지원한다. 이번 변경은 기존 Data 공통 이름 처리의 연결 위치만 모든 자료 행으로 옮기고 원본의 비버튼 파일명 tabstop을 연결한다. 태그/배치/CSS와 Data 버튼·설명·열기는 유지한다.

기존 native alias ID·원문·파일 hash·권한·CAS·pending command/private 복구를 재사용한다. 검색·종류·보기·메뉴·창 수명 변경은 늦은 타이머를 무효화한다. 실패/충돌 요청은 기존 동일 command/revision 재시도 또는 입력 취소를 사용한다. 새 이름 저장 형식이나 실행 계약은 없다.

수용 경계는 세 목록의 선택/수정키/재클릭/취소/이름 저장, 폴더 더블클릭, Compact/Preview 키보드, Preview 초안 cold 복원, Compact 실제 쓰기거절/cold retry, Preview 실제 동료 변경/CAS/cold 취소, 닫힌 창의 오래된 핸들러다. 기존 Data·정렬·키보드·배치 회귀를 포함한다. 독립 LF/CRLF·새 교차 패키지/전체 복원과 보관 기록에서 마감한다.

큰 자료 보관/backend·정보 종류 미결정 정책·초기 빈 화면 및 Agent 일시 대기 원인 미확정·실기기/전체 UI 검증은 이번 범위와 별도다.
