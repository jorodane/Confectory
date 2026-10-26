# v536 고정 7행: 하위 copy의 기존 값 입력 연결

기준 게시 `ad9ae444361215aa6abd9e5876fae288aa70cc51`, 원본 UI는 저장소 v536 `196c605`다. 이번 최소 단위는 **기존 private code next 노드의 값 입력에 상수·같은 프레임의 기존 local/입력을 명시적으로 선택하고, 기존 본문과 같은 후보로 저장하는 흐름**이다. 공개 함수나 private 핀 정의·수·역할·순서를 바꾸지 않는다. 새 동작/route/enum/callee ABI, 독립 계약 복제나 자동 C# 재작성은 이번 범위가 아니다.

## 원본 조작과 현재 경계

원본 Blueprint는 내부 action에도 기존 값/표현식 선택과 data link를 제공하며, `localImplementationDraft`는 전체 하위 Blueprint를 clone한다. 직전 단위는 nested copy의 기존 C# 본문 이동·편집을 연결했지만 qualified private edit와 독립 창 authorBatch는 source/intent만 받았다. 따라서 원래 입력 핀에서 선택한 값이 화면에 남아도 Save에서 거절됐다. 이번은 새 핀 UX를 만드는 작업이 아니라 그 기존 값 연결을 보존해 저장하는 어댑터다.

| 조작 | 분류 |
|---|---|
| 기존 private code next의 일반 값 핀에서 명시 상수·그 프레임의 local/input 선택 | 원래 요구의 실제 미연결. qualified 프레임·기존 signature와 전체 후보 검증으로 연결한다. |
| 공개 오버라이드 입력/출력 구조 변경, 부모/외부 쓰기 | 정상 보호. 미구현으로 세지 않는다. 새 공개 계약/ID·독립 계약 복제는 제외다. |
| ref/out·forwardCallerStorage를 값 입력으로 치환, 다른 그래프의 node/local을 추측해 연결 | 허용하지 않는다. 기존 저장소·명시 역할과 프레임 타입 규칙을 유지한다. |
| 새 private 핀/동작/실행선·callee ABI·enum 계약 편집 | 별도 고정 7행 잔여다. 가능한 조합 전체를 새 필수로 만들지 않는다. 내부 구현 편집과 공개 계약 변경 금지를 구분한다. |

## 연결

`ImplementationCopyEdits`는 전체 경로로 찾은 code next의 선언된 일반 값 입력만 `argument:` 계획으로 받는다. source/intent와 함께 original graph tree에 반영한 뒤 기존 전체 `FeatureBlueprint` 타입·scope·record/import/wrapper 검증으로 후보를 확인한다. 공개 signature와 원본/다른 프레임/route·source/helpers를 자동으로 바꾸지 않는다. 미완성·overflow·타입/범위 오류는 후보 전체를 반환하지 않는다.

저장된 copy는 서버가 묶은 project/view/정보 owner·exclusive assignment·provenance·private 경로를 검증한다. 기존 source/intent와 일반 argument만 authorBatch에 결합하며, ref/out/forwarded/context 노드는 차단한다. 전체 후보의 diagnostics가 유효할 때만 기존 checkpoint CAS를 한 번 수행한다. 한 번이라도 부적합하면 앞의 본문 편집도 live draft/checkpoint에 적용하지 않는다. source/checkpoint 증거·응답 조회·Review/Confirm 경계는 유지한다.

기존 핀 값 선택·연결 해제·입력/local 목록·원문 검색창과 canvas Undo/Redo를 사용한다. 하위 copy의 값 변경도 기존 프레임별 이력으로 묶어 다른 깊이의 입력을 지우지 않는다. invalid 숫자 원문은 기존 value-draft로 보관하며 취소는 사용자가 취소한 임시 입력만 되돌린다. 실제 입력 Map의 순회 순서와 graph/node/pin/실행선의 의미 있는 순서를 구분한다. 입력은 키별 원문 전체를 비교하고 실행선·반환·계약 순서는 따로 검증한다.

CSS/HTML·기존 배치·메뉴를 변경하지 않는다. WebBundle은 변경 JS의 정확한 UTF-8 LF identity만 갱신하며 strict resource 검증을 유지한다.

## 검증과 실패 기록

사용자 프로젝트나 유료 AI 대신 격리 fixture를 사용한다. 등록 함수의 원래 `(long,out long,out bool)->long`, common nested body와 별도 Windows 원문, 깊이1/2의 동명 body, 기존 local·공개 출력·도우미 원문을 보존한다. 정확한 `9223372036854775804` 값과 long overflow 원문, 같은 프레임 input/local 선택 및 다른 프레임 참조 거절을 검사한다.

Native Release와 순수 후보는 정상 결합과 마지막 값의 타입/프레임/overflow/미선언 핀·local/미완성 연결이 잘못됐을 때 전체 거절을 구분한다. 실제 UI/API는 본문을 먼저 편집한 뒤 마지막 값에 오류를 주어 checkpoint·live source·입력이 모두 유지되는지 확인한다. 값과 본문 재편집, Undo/Redo·취소·cold·저장 실패·경합·응답 유실·실제 프로젝트/독립 창·다른 창 입력·명시 Review/Confirm을 실제 경로로 구분한다. 최종 수·명령·해시는 결과 기록에 남긴다.

미완성 값을 서버가 거절한 뒤 값을 고친 경우에는 이전 요청의 미적용, 원래 checkpoint·전체 source closure와 실제 물리 원본 파일 불변을 조회로 확인한다. 같은 키/노드/증거와 본문 원문을 유지한 명시 값 수정만 새 attempt로 만들며 이전 실패 요청은 previousAttempts에 보관한다. 적용 여부가 불명하거나 실제 source가 바뀌면 이 경로를 열지 않는다. 응답 유실의 성공 receipt 조회·중복 방지는 기존 경로를 유지한다.

처음 Undo 검사는 기존 값 변경이 canvas 이력에 들어가지 않는 실제 결함을 재현했다. 기존 structuralEdit을 하위 copy 값 선택에 연결했다. 그다음 키/원문이 같아도 Map 순회 순서가 달라 검사에서 거절되던 비교 문제를 바로잡았으며, 원래 graph/pin/route 순서 검사는 유지했다. 수정 전 기본 UI 통과와 이 실패 시도는 최종 결과와 별도로 보관한다. 창 전환 검사 중 report-2 엔진의 재시작에 개발 중 갱신한 JS가 섞여 strict canonical size mismatch가 난 실행도 미통과로 보존한다. 최종 엔진/리소스 버전을 일치시켜 해당 흐름을 재검증하며 resource 검증을 완화하지 않는다.

## 실제 잔여와 플랫폼 한계

기존 하위 값 연결의 이 단위와 7행 전체 완료를 구분한다. private 핀/계약·새 동작/실행선·callee ABI·내부 enum 편집은 별도 어댑터 경계다. 공개 오버라이드 구조 변경 거절과 독립 계약 복제 제외는 그대로다. 새 alias/import 전용 UI·legacy bool 시각 분기·전체 target 자동 복제를 필수로 늘리지 않는다.

8행의 기존 지원 leaf/call 밖 계약/수동 C#/nested/private/whole/wrapper·출처 closure 결합 및 다른 속성과의 혼합, 9행 고급 함수 타입·표시명/native 식별자, I6 아이콘/로컬 이미지, B2 실제 작업자 배지, A4~A6/M4/M11/M12는 별도다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다. 이미지 생성·협의/승자/shared Confirm·내장 렌더/FPS 새 backend는 구현하지 않는다.

기존 사용자 자료·원본·보관 빌드·로그·스크린샷은 삭제하지 않는다. 이번 검사의 정확한 소유 복사본만 증거 ZIP/해시를 확인한 뒤 승인된 수명관리로 정리한다.

수정 전 실제 독립 창에서 미완성 값 Save 거절→올바른 input 선택→Save가 막히는 결함을 재현했다. 이전 authorBatch는 미적용이었지만 조회가 baselineUnchanged=false만 반환해 새 명시 값이 제출되지 않았다. 이를 최종 성공으로 집계하지 않고 retry-before 증거로 보관한다.

최종 재시도 guard의 닫는 괄호 누락으로 브라우저 초기 진입이 실패한 시도도 기록한다. 실제 제공된 57개 스크립트와 CDP exception 위치(feature-authoring.js 621행)를 대조해 원인을 수정했다. 정적 Node check만으로 이 시도를 통과로 분류하지 않았으며 실제 Chromium/엔진 검증을 다시 수행한다.

## 집중 검증 완료

Native Release 0경고/오류와 순수 후보 6확인, 실제 엔진/렌더러 및 영향 회귀 11흐름 91확인을 통과했다. 정상·독립 창 값 Undo/Redo·cold·취소·저장 실패·다른 창 경합·응답 유실 조회·원래 source의 실제 물리 변경 거절·거절 후 명시 값 수정 재시도·프로젝트/창 문맥·Review/Confirm을 구분했다. 첫 네 흐름은 좁은 재시도 수정 전의 동일 정상/receipt 경로 결과를 재사용하며, 수정 분기와 앞서 실패한 창 전환 및 영향 회귀는 최종 엔진으로 확인했다. 이전 실패 시도는 합계에서 제외했다. [명령·결과·제품 해시](evidence/v536-nested-copy-values/focused-verification.json)에 기록했다. 다음 checkout/새 교차 패키지 결과는 별도 추가한다.
