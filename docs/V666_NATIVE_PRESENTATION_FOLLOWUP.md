# 여러 표시 편집 뒤 native 읽기 범위 보존

고정7/8행의 기존 공동 저장을 후속 편집하는 실제 안전 결함을 다룬다.
게시54dc2992에서 native ABI/body/caller 그룹을 저장한 뒤 정보 설명·아이콘과 두 함수 설명을
한 번에 저장하면 원래60개 readGuards가0개가 됐다. 이후 helper 원문을 바꿔도 Review가 ready였다.
재현에서는 Confirm하지 않았고 바꾼 helper bytes를 정확히 복원했다.

이미 캡처한 그룹의 함수 집합과 현재 계약을 그대로 유지하는 표시 편집을 한 번에 보존한다.
설명·아이콘은 각각 최대 하나, 함수 표시는 최대8개, 합계 최대10행이다.
각 함수는 직접 소유·현재 signature·기존 identity map 및 캡처한 source id/path를 유지한다.
표시의 exact-key·중복·설명 길이·이미지/기호와 함수 표시명 검증은 기존 InformationDefinitions가 수행한다.
기존 readGuards를 그대로 이어받고 원본 hash나 읽기 기준을 새로 만들지 않는다.

이미 읽기 범위가 있는 그룹에서 인식하지 못하는 선언이나 캡처 밖 함수는 빈 legacy receipt로
바꾸지 않고 입력 보존 오류로 거절한다. 구조/새 계약·새 출처는 그에 맞는 완전한 명시 계획이
필요하며 이번 변경으로 추정하지 않는다. 실제 빈 읽기 범위의 기존 단순 leaf/Blueprint 경계는 유지한다.
같은 판정을 준비·cold 헤더/graph 읽기·후속 receipt 검증과 Review/Confirm에 연결한다.

최초 명시 그룹의 ABI·본문·caller 및 예정한 실행 결과40은 표시 편집으로 바뀌지 않는다.
저장 실패·응답 유실·반복·취소·Undo/Redo·cold·owner 경합·늦은 입력·후속 저장 직전 경합과
누락/변조 receipt, Save/Review/Confirm 사이 helper·caller·선택 소스 변경의 전체 거절을 검사한다.
수정 전후의 기록과 미확정 staged 데이터, 실제 Linux 실행·Chromium 및 Windows 교차 패키지를 구분한다.

원래 C# bytes·소유권·권한·공개/override 계약·authored layout·한 checkpoint CAS·최종 source lease를 유지한다.
새 문법·receipt 버전·타입 표현·자동 migration은 없다. 정보별 struct·종류 enum·모듈 interface를 따른다.
같은 게시 세대의 저장/재편집 기준이며 이전 authoring과 새 조합 receipt의 교환을 보장하지 않는다.
남은 고정7/8행은 다른 실제 복합 계약/본문·속성 구조 편집, opaque/private 명시 C# 계획,
선택 native 의존성과 기존 import/등록 외부 관측 결합을 원래 조작의 재현·회귀 증거로 대조한다.
타입/문맥의 모든 조합을 새 필수 항목으로 늘리지 않으며 M11/M12/M4는 회귀 없이 다시 열지 않는다.
초기 빈 화면 원인은 미확정이며 실제 Windows/WebView2·물리 기기·전체 UI 전수 검증은 자동화와 구분한다.
