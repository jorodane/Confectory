# v536 Browser 현재 지원 범위

게시 기준은 work/current `c08d08f`이며 이번 독립 Data·상속 참조 검증은 `VALIDATION_V536_STANDALONE_DATA.md`에 기록한다. 전체 v536 UI 복원 완료가 아니다.

| 범위 | 현재 지원/검증 | 남은 제한 |
|---|---|---|
| 소유 개념/카테고리 분류 | 별도 folder metadata, 카테고리 자체 중첩·복수 이동·Root, 원자적 stale 거절, 취소·Save·cold·Review/명시 compiler Confirm. 실제 부모·namespace·typed Contains/자손/다른 입력 보존 | 한 번에 유한 32 source/dependency, root 소유 namespace/같은 탭. 등록 팩/외부 namespace로 실제 source 재배치·개명은 안 함. 모든 source 종류/플랫폼 UI 조합을 검증한 것은 아님 |
| 실제 상속 변경 | 요소 부모 선택의 별도 경로와 기존 effective schema guard. private 취소·Save·cold·Review/명시 Confirm 회귀 | 분류 드롭을 parent=null로 해석하지 않음. 잘못된 상속 데이터는 자동 복사/삭제해 통과시키지 않음 |
| 이름·변형·Data | 앞선 F2/개념 부모·자손·inline 바리에이션·embedded 직접 셀 편집·그룹 확정 유지. 독립 소유 개념 Data의 실제 저장/취소/cold/참조 상세/명시 Confirm9건, embedded7건 검증 | 모든 source 종류의 Data 셀/일반 context·참조 정의·모든 이름 표면 및 마지막 전체 통합 대조는 남음 |
| 삭제·복구 | 참조된 대상 차단, 비파괴 등록 해제·원본/초안 archive·사용자 메뉴·다중 선택·취소/cold/명시 확정 및 복구 | 원본 물리 파일 영구 삭제 아님. declared reference만 검사하며 C# 문자열/자연어의 모든 사용처를 증명하지 않음. receipt import/commit check-path 집중 검사는 게시 전 잔여 |
| 원본 화면 | 창678×458, title/tabs/tools/pane/tree/items6 영역의 동일 viewport 실제 치수 일치, 주요 실제 캡처 확인. 독립 Data 행11영역 크기/글꼴/여백/모서리 및 실제 상속 Hover/Shift 역참조 검증 | 모든 아이콘·자식 수 뱃지·drag preview/모든 화면 pixel equality 미검증. 원본 demo 데이터/사용자 이름을 복사하지 않음 |
| 환경/게시 | Linux 생성 엔진·Chromium·portable compiler, 격리 자료만 사용 | 실제 Windows/Android/OS drag/touch/실계정·유료 inference 미실행. 이전 c08d08f 중간 package/checkout/게시 완료. 이번 Browser 단계의 별도 결과와 남은 전달 제한은 새 검증 문서에 구분 |

## 다음 고정 순서

1. Browser 잔여를 위 제한대로 유지하면서 다음 UI 영역인 Helper 이미지·이력·삭제를 원본 v536 흐름과 실제 backend 계약에 연결한다. 기존 대화·초안·Agent 등록/승낙/계정 자료를 임의 삭제하지 않는다.
2. 전투 로그·신문고/Yogi를 실제 상태/오류에 연결한다. mock/미지원 동작을 성공으로 표시하지 않는다.
3. 창별 실행 화면과 실제 프로젝트 문맥·출력·종료 상태를 연결한다. Helper에게 최종 반영/실행 권한을 자동 부여하지 않는다.
4. 고정된 모바일 Blueprint/호출 ABI/mixed Save 제한 및 Browser 정밀 잔여를 전체 수용 목록에서 확인한다. 관련 회귀 후 Windows 교차 package·resource/checkout·승인된 work/current 정상 게시와 remote 확인을 한다. 실제 native 실행과 cross build는 구분한다.

원본 v536 레이아웃 변경, main/Android/원본 ZIP/실사용자 자료 변경, 실제 계정 로그인·토큰 접근·유료 추론·권한 확대는 이 검증에 포함하지 않는다. 세부 실패/수정/검사 증거는 VALIDATION_V536_BROWSER_FOLDERS.md와 기존 각 Browser validation 문서를 따른다.
