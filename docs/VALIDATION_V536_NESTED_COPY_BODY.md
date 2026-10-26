# v536 고정 7행: 중첩 copy의 기존 내부 본문 연결

기준 게시 `84f7382e9349f7be7100605f27122b62211d3cb4`, UI 기준은 저장소 v536 `196c605`다. 이번 최소 단위는 **원래 공개 함수 계약과 선택 target을 유지한 Blueprint 복사에서 기존 내부 흐름으로 들어가고, qualified C# leaf 본문을 편집·저장하는 경로**다. 새 전역 함수 계약/ID, 독립 계약 복제, 자동 C# 재작성은 추가하지 않는다.

## 원본 대조와 정상 보호

원본 `dist/app.js`의 `localImplementationDraft`는 정의를 structuredClone한 후 내부 action을 재귀 방문하여 compiled owner만 재배치한다. `moduleFunctionDefinition`은 원래 이름·입출력·매개변수·반환·실행 출력을 유지한다. 따라서 기존 하위 Blueprint와 본문을 보존해 복사/편집하는 것은 원래 요구이며, 부모/외부 원문이나 공개 계약을 바꾸는 권한이 아니다. 기존 구현 선택에는 nested source/target이 표시됐지만 Native의 flat 노드 검사·평면 record ID와 화면의 slot/private 이동 차단이 이 경로를 막았다.

| 조작 | 판정 |
|---|---|
| 같은 공개 계약·선택 target을 복사하고 하위 graph/기존 leaf 본문을 열기 | 실제 원본 요구의 미연결. 이번에 bounded graph tree·snapshot·원자 저장·기존 화면 이동으로 연결한다. |
| 오버라이드 공개 입력/출력의 타입·수·역할·반환 구조 변경, 부모/외부 쓰기 | 정상 금지. 거절을 미구현으로 세지 않는다. 독립 계약 복제는 필수 제외다. |
| 복사본의 내부 code node Result enum 계약·분기 편집 | 내부 실행 분기와 공개 함수 계약을 구분한다. 공개 입출력을 유지하는 내부 편집은 오버라이드 구조 변경과 같은 금지가 아니며 기존 후보 어댑터의 별도 잔여다. 공개 계약 자체를 바꾸는 경우에는 원래 보호를 유지한다. 이번에 branch 계약을 자동 갱신하지 않는다. |
| 새 alias/import 전용 UI·legacy bool 시각 분기·전체 target 자동 복제 | 새 필수 요구로 늘리지 않는다. 원본 조작/형식 경계와 기존 alias/import 보존 지원을 구분한다. |

## 구현 범위

기존 `BlueprintTree`의 깊이·노드 수·ID/경로 예산을 사용하여 graph 안의 code/call/export/graph와 기존 code switch/call enum 후처리를 재귀 검사한다. 허용하지 않은 property/Set/legacy bool 형태를 일괄 허용하지 않는다. leaf의 **전체 graph 경로**로 새 파일명을 만들고, 실제 저장 ID는 `/node:left/node:body`와 같이 기존 qualified 규칙을 따른다. `record.node`는 local `body`로 유지한다. 실제 source owner와 body target을 포함해 원본 정의 해시를 검증하고 복사본의 private owner 해시를 계산한다. 공개 함수 FQN/서명, graph/leaf ID·순서·route·값·원문·helpers·donor/다른 target은 유지한다. private generated owner는 기존 엔진 규칙이며 새 공개 계약을 발급하는 기능이 아니다.

미등록 copy의 immutable snapshot에 모든 qualified leaf를 넣고, private preview 이동도 같은 snapshot·현재 readonly 관측·scope/owner/target으로 검증한다. 이번 새 하위 편집 어댑터는 기존 C# `source`/`intent`만 받는다. 모호한 graph 경계 이동이나 핀/계약 재작성을 추정하지 않는다. 잘못된 leaf·경계넘기·graph 본문·지원하지 않는 계약 계획은 원문을 보존하고 거절한다.

저장 전 다른 하위 화면에 보관한 leaf 입력은 원래 scoped 키에서 qualified 계획으로 묶어 기존 copy/선언/본문 저장의 **한 후보/CAS**에 결합한다. 저장된 copy의 내부 source-only 저장은 기존 observed information owner·exclusive assignment·정확한 provenance·root graph와 모든 source/checkpoint 증거를 유지한 authorBatch만 허용한다. 독립 창의 project/view/owner binding은 서버에서 검증한다. 응답 조회·명시 Review/Confirm과 실패 입력 보존을 우회하지 않는다.

기존 action의 직접 작성, 모바일 내부 흐름 버튼, 부모 버튼/빵부스러기를 사용한다. private view는 공개 owner/function과 하위 signature를 혼동하지 않는다. graph별 입력·화면 상태·Undo/Redo를 구분하며, cold 복원 전에 하위 경로를 복사해 복원 과정의 meta 갱신에 잃지 않도록 한다. CSS/HTML과 다른 UI73파일은 기준 게시와 바이트가 같다. Blueprint850×600·원래 카드/미니맵/입출력 배치를 재설계하지 않는다. WebBundle은 변경 JS의 정확한 canonical size/SHA만 갱신하며 strict 검증을 유지한다.

## 검증과 실패 분류

검증 수·최종 명령/체크·파일 SHA·checkout/패키지는 아래 최종 결과로 구분한다. 사용자 자료/유료 AI 대신 격리 fixture를 사용한다. 등록 함수의 공개 `(long,out long,out bool)->long`, common nested Blueprint와 별도 Windows 원문, 깊이1 `left/body`와 깊이2 `right/deep/body`의 동명 leaf, 정확한64비트 local/정보 값, CRLF helpers와 한글/이모지 원문을 보존한다.

개발 중 qualified ID를 평면 저장 ID로 조합한 결함과 private preview에서 최상위 node만 조회한 누락을 수정했다. 최초 fixture는 helpers를 지원하지 않는 profile이어서 기존 엔진에 거절됐고 실제 Methods profile로 바로잡았다. 또한 JS 리소스 pin을 계산할 때 문자열의 개행 표기까지 정규화한 검사 준비 오류는 실제 파일 LF 바이트 기준으로 수정했다. strict resource·타입/코드/소유권·CAS 검증을 완화하지 않았다. 수정 중 Native를 사용한 첫 화면 시도는 최종 통과에 포함하지 않는다.

저장 전 독립 창 재시작에서 입력과 snapshot은 보존되지만 하위 화면이 부모로 복원되는 실제 결함도 확인했다. 같은 meta 객체가 초기화되는 동안 privatePath를 잃던 원인이었으며, 복원 전에 경로를 별도로 보관하고 private preview의 전체 경로를 기존 영속화 `blueprintGraph` 항목에 유지하도록 수정한다. 새 저장 항목/형식을 추가하지 않는다. 이 실패/증거는 성공과 분리한다.

## 실제 잔여

이번은 같은 공개 계약의 기존 nested graph **복사·이동·C# 본문 편집** 단위다. 7행 전체 계약 편집 완료가 아니다. copy 내부의 핀/계약·callee ABI 대응 및 실행 enum 계약/새 분기 편집은 기존 명시 후보/readonly 원본 receipt와 함께 닫아야 할 별도 어댑터 경계다. 모호한 leaf/별칭을 추정하거나 공개 오버라이드 구조를 바꾸지 않는다. flat whitelist 밖 kind는 실제 원본 진입과 구분하며 모든 C# 조합을 필수화하지 않는다.

8행의 기존 지원 leaf/call 밖 여러 계약·수동 C#/nested/private/whole/wrapper 및 출처 closure 결합, 9행 고급 함수 타입·표시명/native 식별자와 I6 기호/이모지/로컬 이미지, B2 실제 작업자 배지, A4~A6/M4/M11/M12는 별도다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다. 이미지 생성·협의/승자/shared Confirm·내장 렌더/FPS 새 backend는 구현하지 않는다.

기존 사용자 자료·보관 빌드·로그·스크린샷·원본은 삭제하지 않는다. 이번 실행이 만든 검사 복사본만 전체 증거 ZIP/해시를 검증·보관한 뒤 승인된 종료 cleanup을 사용한다.

## 최종 집중·영향 결과

최종 집중 UI5흐름과 영향6검사, 총11흐름 66확인을 통과했다. 별도 순수 후보4확인은 clone·immutable seed/중간/깊이2 preview·cold JSON·qualified leaf 편집과 5거절 경계를 구분한다. 영향검사는 enum copy UI·실제 프로젝트 전환, 기존 직접 소유 내부 흐름 UI, private ABI 순수 후보/실제 compiler 거절, 독립 창 소유 가드 API, 오버라이드 계약 보호다. 개발 중 기본 창7확인과 수정 전 실패는 최종 합계와 구분해 보관했다. [상세 명령·체크·해시](evidence/v536-nested-copy-body/focused-verification.json)를 남긴다.
