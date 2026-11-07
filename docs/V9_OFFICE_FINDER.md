# V9 3D 작업실 찾기와 표시 이동

원본 v666 ZIP `dist/app.js::openWorkspaceFinder`의 office 분기에 있는 구역 바로가기,
Helper별 실제 Worker 목록, 요소/글자 찾기와 카메라 이동을 기존 표시 팩에 연결한다.
기존 패널 검색/원문 열기와 별개이며 원본 검색 CSS·레이아웃을 재사용한다.

3D 팩의 일시 scope는 현재 ProjectContext·Workspace·표시 소유 세대에서만 유효하다.
이미 허용된 직접 소유 요소와 현재 3D 관측에 들어온 Helper/Worker만 읽는다. 다른 멤버/
그룹·비공개 작업·연락처·대화를 조회하거나 권한을 만들지 않는다. 결과 선택 직전에
현재 source/actor membership을 다시 확인한다. 이름이 같아도 원래 ID를 사용한다.

구역/요소는 실제 방·station을 표시하고, Helper/Worker는 기존 선택/따라가기 카메라를
사용한다. 동작 시작/재실행·배정·권한 부여·Source Save/Review/Confirm은 하지 않는다.
캐릭터 도착과 실제 실행은 계속 독립적이다. 실제 native 상태·작업 설명으로 찾으며
진행/성공이나 시연 Worker를 만들지 않는다. 일부 기록 확인 실패는 일부 상태로 표시한다.

원본의 요소 제안·Helper 펼침·작업자/요소/글자 모드·구역 바로가기 UI를 사용한다.
기존 metadata/내용 읽기를 재사용하고 source·상속/부모·외부 원본을 새로 탐색하지 않는다.
일시 검색어/펼침/결과는 개인 presentation에 저장하지 않는다. Esc·닫기·표시/Workspace·
프로젝트 세대 전환은 callback을 폐기한다. retired 결과가 새 검색을 닫거나 이동시킬 수 없다.
입력/기존 개별 source 창·팝오버·C# 계약·권한·CAS·Review→Confirm은 보존한다.

V4/V5의 새 신원/권한·참여자/연락처/대화, V6/V7 자산, Run HD/GPU/native와 실제 기기/
전체 UI·Space 전달은 이번 범위가 아니다. 초기화 간헐 빈 화면은 원인 미확정으로 유지한다.
최종 신규/재사용·패키지/전체 복원·보관/공간은 별도 검증 기록에 확정한다.
