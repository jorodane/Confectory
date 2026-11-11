# standalone 인자 표시명 검증

제품 동결 `462f9ac50112c260af2934e7bdea4731948d0b94`의 [한정 지원 경계](V666_STANDALONE_LABELS.md)를 **신규 41단계·재사용0·실패0**으로 검증했다.
독립 no-hardlinks Git 객체·HOME/NuGet·빈 엔진 cache의 LF/CRLF Release/MCP·실제 엔진,
새 Windows 교차 패키지의 구조·무결성 및 전체 ZIP 복원을 실행했다. 개발 실행과
최종 실행을 합산하지 않으며 기존 테스트 코드의 새 실행과 과거 결과 재사용을 구분한다.

- 같은 카드/상세창에서 명시적 표시 모드·빈 표시명 거절·취소·로컬 Undo/Redo·cold를
  확인했다. 표시명과 설명을 기존 owner 후보/CAS로 저장하고 native 인자 이름·타입·역할,
  함수 ID·실행 연결·원래 C# bytes를 보존했다. 저장 이력 Undo/Redo·명시적 표시 초기화·
  metadata 제거와 다시 저장도 통과했다. 설명/아이콘을 포함한3개 native 후보도 검사했다.
- peer 체크포인트 충돌·실제 체크포인트 쓰기 실패·재시도·cold와 수명 경계를 확인했다.
  실제 native apply가 접수된 뒤 응답을 잃거나 새 표시명을 입력하는 검사는 영수증과 새
  cell을 구별했다. cold 후 이전 apply를 재실행하지 않으며 새 입력만 한 번 저장한다.
  Review 취소·Review 뒤 physical peer 변경의 최종 CAS 거절·명시적 재검토/Confirm·실제
  원래 결과10 실행까지 확인했다. 단계별 원문·checkpoint·요청/결과 기록을 보존했다.
- native 후보는 알 수 없는 키·잘못된 원본 map·null/숫자/배열·길이/공백/control·추가/중복
  cell·잘못된 owner/kind를 거절한다. 별칭 없는 기존 서명 요청과 그대로인 별칭은 보존하고,
  별칭이 가리키는 인자의 제거/rename은 현재 요청으로 조용히 유실시키지 않는다.
  입력·본문·호출자의 명시 대응을 자동으로 생성하거나 C#을 치환하지 않는다.
- constructor/toString/__proto__ 식별자는 native 후보와 실제 standalone UI에서 확인했다.
  공통 상세창·카드는 자체 JSON 키만 사용한다. UI 표본의 기본 실행 함수는 int 값 입력
  하나와 int 반환이며, 추가 식별자 표본은 draft/native 후보 경계다. 모든 타입·문맥이나
  추가 식별자의 실제 C# 실행을 전수 검증했다는 뜻은 아니다.
- 기존 standalone native 편집/IME Escape와 정보 카드 표시명·Review/Confirm/실행을 새로
  회귀 검사했다. 현재 실제3D에서 느린 이미지 소켓·부분 POST 중 reload8회와 단절·
  child/root·프로젝트 왕복·cold가 통과했다. 과거 간헐적 빈 화면의 원인은 미확정이다.
  이전 bootstrap 오류 복구의37개 전체 결과를 이번에 재사용/재실행했다고 세지 않는다.

개발 28단계의 실패3건을 보존했다. 첫 fixture는 invalid native 텍스트가 popup에
남는다고 잘못 가정했으나 실제로는 pending signature에 보관돼 Save에서 거절됐다. 제품은
설명 단일 cell만 허용한 이력 분류 때문에 표시명 Save 뒤 Undo가 끊기는 결함을 수정했다.
후속 fixture는 이전 엔진 보고서 경로를 읽었으며, 완료된 빌드/native 검사를 보존하고 새
보고서로 영향 UI만 다시 실행했다. 모든 최종 검사는 동결 코드에서 새로 실행했다.

새 Reference를 모르는 구 reader의 TYPE 거절과 문자열 metadata 호환은 별도다.
구 바이너리 비교는 [기존 보관 근거](VALIDATION_V666_ARGUMENT_LABELS.md)를 참고했으며 이번
최종 수에 포함하지 않았다. 구 reader 자체를 소급 수정하거나 자동 migration/downgrade를
제공하지 않는다. 현재 패키지의 일치하는 reader/authoring을 사용하고 실제 버전·선언을 확인한다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 462f9ac50112c260af2934e7bdea4731948d0b94 | 0dfb32b2a20d1c8d32b642ae25222d3efcb9ccdcfe71a4b2468e497130622b18 | 54069010 |
| rollback | 67663dc8f36060cb1f424f5ae5e2f7b7f7705db9 | 15b7f952c245e8df261d6b842804ba48ccb89497fb145f0a94dfa025e0e60a67 | 54066392 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/64ad2a984ad14342b87603139863065b.json` · evidence SHA256 `e73e87210f7c306baaf3a8386bf215dc34c151b072b5ef5f36ef2c46af770792`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/0c30af7e84244b7ba654ec8aa792d39e.json` · evidence SHA256 `d462f195e791ecfc21a4ffaab7bf3f4407c023a5cd36ab1d7b244ec86022b7e5`.
증거와 두 관리 package를 SHA로 재확인했다. 승인된 latest/정상 rollback2세대 교대와 이번
소유 RAM 임시물 정리만 적용했다. 과거 비관리 자료·원래 checkout/main을 보존하며 교대된
세 번째 관리 package 전체도 계속 보관한다고 주장하지 않는다. 여유 25359360000bytes (23.62GiB)다.

다른 표시·고정7/8행의 실제 명시 계약/본문 closure는 [기존 유한 잔여](V666_STANDALONE_LABELS.md)에
유지한다. M11/M12/M4는 다시 열지 않는다. 실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·
전체 UI는 미검증이다. 새 자격증명/외부 grant·라이브 AI/과금·main 변경은 없다.
