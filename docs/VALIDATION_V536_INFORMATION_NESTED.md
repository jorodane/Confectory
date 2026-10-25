# 중첩/private graph 계약 대응 검증

고정 지원 경계와 정확한 잔여는 [V536_I5_6_NESTED_SCOPE.md](V536_I5_6_NESTED_SCOPE.md)에 기록했다. 실제 계정·권한·유료 AI·사용자 프로젝트 실행 없이 격리 fixture만 사용한다.

## 확인한 경로

- 순수 후보: 깊이 2와 서로 같은 leaf ID의 별도 호출을 구분하고 부모/형제·정확한 64비트 값·원문을 보존한다. 일반 코드, 명시 C# import, serial/enum 후처리와 고정 private ref 전달을 검사한다. 누락/flat leaf/다른 private 경로/stale graph·source·정의 해시는 전체 거절한다.
- 실제 API: qualified source·후처리와 부모 인자 교체를 한 후보/CAS로 저장하고, 재시작과 실제 compiler Review/Confirm 뒤 원문·다른 소스·local·부모/자식을 확인한다.
- 실제 렌더러: 원본 정보 상세창/구현 선택/Script/호출 대응 창을 사용한다. 코드 취소·불완전 입력 재시작·Undo/Redo, 장치 오류·충돌·응답/receipt 유실 후 결과 조회, 두 프로젝트 전환·닫힌 편집창 저장 차단, 기본/독립 창의 저장·재시작·Review 취소·재검토·명시 Confirm을 확인한다.
- 영향 회귀: 기존 root 저장소/별칭과 추가 노드·serial/enum 후처리의 후보 및 stale/copy 거절을 확인한다. 무관한 통과 검사는 반복하지 않는다.

## 수정·검사 해석

이전 owner 경로는 nested caller 자체를 거절했다. 현재 qualified private ID와 각 frame의 의미 바인딩으로 대응하며, 단순 재귀 JSON 치환으로 부모·형제·자식의 같은 leaf ID를 함께 바꾸지 않는다. 전체 private source 정의 해시와 실제 조립 C#을 확인하고 원래 한 거래/CAS를 유지한다.

초기 fixture의 없는 definition 필드, serial post profile 및 enum case의 branch owner 문법을 기존 계약에 맞게 바로잡았다. API fixture의 `child` 변수 shadow와 Confirm 뒤 JSON 재직렬화 바이트 비교도 수정했다. 실제 source 문자열/CRLF·계약·정확한 값 비교는 유지했다. 이를 사용자 제품 결함이나 보호 완화로 보고하지 않는다.

원본 v536 `dist/blueprint.js`의 Script/backdrop/source/status/error 및 wrapper 구조를 재사용하며 CSS를 변경하지 않는다. 전체 screenshot pixel 일치는 주장하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 이번 지원 단위는 5행 전체/I5-6 전체/v536 전체 UI 완료와 구별한다.

집중 결과는 **38 check**다(순수 후보 10·실제 API 6·실제 렌더러 20·영향 회귀 2). 실패한 fixture 시도나 같은 검사 재실행은 합산하지 않았다. [선별 결과](evidence/v536-information-nested/focused-checks.json), [고정 private C#](evidence/v536-information-nested/scoped-code.png), [모바일 폭 내부 탐색](evidence/v536-information-nested/private-navigation.png), [독립 창 최종 상태](evidence/v536-information-nested/independent-final.png) 및 [원본 구조/CSS 근거](evidence/v536-information-nested/layout-evidence.json)를 보관한다. Native Release는 0 warning/0 error, Linux 빌드 stderr는 0이다.

탐색 검사는 cold 복원 직후 준비 전 상위 이동 클릭으로 한 번 실패했다. 실제 공통 준비 상태(`.brand` 활성)를 기다린 뒤 깊이 2/상위 이동과 원문·미적용 입력 보존을 완주했다. 임의 시간 지연이나 강제 click을 넣지 않았다. 그 실패 snapshot의 `Schema unavailable` 알림은 함수로 primary 선택을 바꾼 뒤 기존 정보창 복원과 함께 관측됐으며, 이 별도 표시 문제를 해결했다고 주장하지 않는다. 원인과 정확한 재현 범위는 후속 확인 항목이다.
