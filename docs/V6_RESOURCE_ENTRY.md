# 자료 빈 영역·ProjectPack 추가 메뉴

고정 v666 `app.js`의 `renderResourceItems` 마지막 `root.oncontextmenu`는 카드 밖에서
`resourceCreateMenu(w,event)`를 연다. `setupResourceTree`의 ProjectPack root도
`resourceCreateMenu(w,event,id)`를 연다. 두 메뉴는 기존 ‘자료 추가 / 새 카테고리’다.
이 진입점이 빠져 있던 현재 실제 자료 Browser에 같은 메뉴를 연결한다. 새 레이아웃이나
OS 폴더 탐색, 파일 자동 선택은 추가하지 않는다.

빈 목록/카드 밖의 빈 영역은 현재 카테고리, ProjectPack 트리는 항상 root를 가리킨다.
기존 추가 버튼·File chooser·카테고리 폼·원자 거래를 재사용한다. 카드·이름/설명 입력의
메뉴는 가로채지 않는다. catalogue가 준비되지 않았거나 작업/설명 저장/이름 편집 중이면
새 변경을 시작하지 않는다. 메뉴를 열 때 owner·화면 token·부모·layout/resource revision을
고정하며, 카테고리 폼도 그 부모와 기준 revision을 사용한다. File chooser 선택이나 비동기
읽기 중 탐색해도 다른 폴더로 바꾸지 않는다. 대상 삭제/다른 writer는 기존 최종 CAS에서
거절하고 명시 재시도/입력만 취소 경계를 유지한다. Home·창 닫기·프로젝트 교체로 폐기된
메뉴/chooser 콜백은 새 화면의 권한으로 실행하지 않는다.

새 공개/native API·자료/개인 schema·권한 정책·함수 계약은 없다. ProjectPack 표시는 현재
활성 ProjectContext의 소유 root이며 외부/부모 파일 경로를 받지 않는다. 실제 native 권한·
소유·원자 저장과 C# Review→Confirm/최종 CAS는 바꾸지 않는다. 기존 File당1MiB·선택
전체1MiB/64개·전체4MiB와 읽기/transport 한도를 유지한다. 큰 파일은 전송/보관/초안 예산
확장이 함께 필요한 별도 잔여다. 다른 원본 그림 형식과 권한 source가 필요한 멤버/Agent
기능도 별도이며 mesh renderer를 발명하지 않는다. 간헐 초기화 빈 화면은 원인 미확정이다.

실제 Windows 파일 선택기·모바일·전체 UI/Space 전달은 완료로 표시하지 않는다.
현재 Linux engine/Chromium의 실제 파일 선택 이벤트와 생성한 File 입력을 검증한다.
