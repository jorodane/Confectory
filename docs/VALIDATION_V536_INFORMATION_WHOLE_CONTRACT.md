# v536 전체 본문의 타입·핀·out·반환 계약 검증

[고정 수용 범위](V536_I5_6_WHOLE_CONTRACT_SCOPE.md)의 직접 소유/import 없는 전체 본문과 일반 caller를 연결했다. 새 레이아웃이나 C# 자동 재작성은 없다. 함수 상세창에서 고른 계약, 직접 편집한 native 매개변수/본문, 기존 caller 바인딩과 출력 대응, graph/record/반환 경로를 한 후보/CAS로 검증한다.

## 실행한 검사

격리 fixture의 7시나리오를 사용한다: string 입력과 새 long 입력/출력 이름 및 bool 반환의 결합, out→값, 값→out, out→ref, ref→out, 반환→void, void→반환. 순수 후보는 각 2건(14 PASS), 실제 엔진 API/저장·cold·compiler Review/Confirm은 각 3건(21 PASS)이다. 잘못된 flow/hash/서명·본문·native 역할·caller·출력 대응과 기존 추가 노드/별칭은 전체 거절하고 실제 source를 유지한다. 64비트 정수 원문, 한글·이모지와 기존 native/public 이름 구별을 검사한다. 기존 출력 순서의 count→total 명시 대응도 확인했다.

실제 기본 화면의 타입·핀·반환 결합은 코드/함수 편집 취소, 불완전 매개변수/본문 cold 보관, 명시적 대응, Undo/Redo, 실제 checkpoint 쓰기 실패의 전체 미적용, 저장/receipt 응답 유실 후 cold/결과 조회(재적용 없음), Review 취소/재검토/명시 Confirm을 통과했다(4 PASS). 나머지 6시나리오의 독립 창 화면은 각 취소·불완전 cold·명시 대응·Undo/Redo와 정상 저장/cold·Review/Confirm을 통과했다(각 3 PASS). 타입 결합의 독립 창 충돌·변경 취소·동일 namespace 프로젝트 전환은 각 2 PASS이며 닫힌 편집창의 저장 callback도 다른 프로젝트를 바꾸지 않는다.

초기 simple 화면 검사의 두 번째 체크 문구가 공통 템플릿에서 ‘응답 유실’로 남아 있었다. 실제 해당 분기는 정상 저장/cold만 실행했으므로 검사 이름을 고쳤다. 이 6 simple 시나리오를 응답 유실 검사로 계산하지 않는다. 응답 유실은 별도 normal 타입 시나리오의 실제 transport/receipt 가림과 결과 조회에서 확인했다. 검사 동작이나 제품 보호는 완화하지 않았다.

## 재현하여 고친 결함

같은 함수를 두 번 연결하고 반환 타입/출력을 바꾸며 다음 호출의 입력을 해제할 때, 앞 호출의 출력 대응이 다음 호출의 원래 입력 해제 검증보다 먼저 적용되어 올바른 명시 계획도 거절했다. 입력 계획을 모두 원래 source에서 검증한 뒤 출력 대응을 적용하도록 순서를 고쳤다. 순수 회귀 2건은 출력 이름 변경과 삭제 출력의 마지막 사용처 해제를 확인한다. 해제 누락/남은 사용처는 계속 전체 거절한다. 두 호출의 실제 화면 저장/cold/Review/Confirm 3건도 통과했다. 실제 API 저장/cold/Review/Confirm 3건도 통과했다. 이 두 호출은 함수 둘을 함께 바꾸는 8행과 구분하여 같은 함수 하나의 호출 두 개를 검증한 것이다.

기존 6-field 전체 본문 계획/원래 저장소 검증 2건과 root 계약/legacy3·exact4 source group 5건, 혼합 Blueprint/C# target 후보 2건, 기존 실제 API 4건을 통과했다. 마지막 API는 자기 Confirm 이후 최신 증거로 ref→값을 재편집해도 native/out/source와 caller 저장소가 보존됨을 포함한다.

원인 미확정으로 보고했던 환경 연결 해제는 같은 환경에서 실제 명령·변경 파일·검사 결과를 회수하여 복구를 확인했다. 다른 환경이나 저장소로 이동하지 않았다. 최초 준비 중 JsonNode의 부모 중복은 후보 graph를 독립 clone하여 수정했다. void fixture는 실제 구현 파일을 새 C# 선언으로 저장하기 전에 conversion을 요청했던 검사 준비 오류를 고쳤으며 제품 stale-source 검사를 완화하지 않았다.

모든 쓰기/Confirm은 임시 fixture 프로젝트와 저장소에 한정한다. 사용자 계정·유료 AI·사용자 프로젝트 실행·영구 삭제는 없다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달과 전체 v536 UI 완료는 별도 미검증이다. 추가 callee 노드/별칭, whole-body caller/forwardCallerStorage·postCall 문맥과 고정 5·7·8·9행은 남아 있다.

[실제 편집 화면](evidence/v536-information-whole-contract/code-editor.png)에서 public의 `text/total/increment`와 native의 `message/nativeTotal/delta`, bool 반환·직접 작성한 본문을 확인했다. 기존 Script 창의 위치·크기·버튼/CSS를 유지했다. [선별된 검사 결과](evidence/v536-information-whole-contract/focused-checks.json)는 체크 이름과 격리 fixture 경로만 보관하며 실제 세션 토큰·인증정보·사용자 데이터는 포함하지 않는다.
