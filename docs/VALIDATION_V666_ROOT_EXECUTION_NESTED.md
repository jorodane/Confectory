# M12: 소유 private frame의 공개 함수 호출 결합

## 원래 사용자 흐름과 지원 경계

저장소 v666 `dist/blueprint.js:135`의 call 포트는 참조한 함수 정의에서 나온다. `:969–976`의 공개 분기/반환 편집과 `:248`의 결과 분기 뒤 다음 동작 규칙을 기존 소유 private graph에도 연결한다. 물리 Blueprint Root 안의 일반 switch-profile frame에서 공개 함수를 호출할 때도 전체 호출 경로를 명시 대응하고 한 후보로 저장한다.

호출 위치는 물리 graph ID와 `frame/invoke` 같은 qualified node key로 식별한다. 실행선/반환 대상은 그 호출이 실제로 속한 local frame에서만 찾고 갱신한다. private 반환은 그 frame을 끝내며 부모 함수의 기존 다음 동작이나 반환값을 묵시적으로 바꾸지 않는다. 같은 local ID의 형제 코드도 다른 source ID로 수집한다. `/node:frame/node:after`는 실제 leaf 관측 ID이고 `/graph:frame` author view와 구별한다. 기존 implementation+body target의 sourceOwner를 전달해 private 함수 ID·definitionHash를 재발급하지 않는다.

공개 계약·물리 graph·소유 구현·재귀적으로 읽은 모든 C# leaf·기존 import 관측은 같은 원자 그룹과 Review/Confirm·최종 read-CAS에 포함한다. 형제의 readonly 원문도 단순히 같은 local ID라는 이유로 누락하지 않는다. 원래 C# record의 bytes/mode·인수/출력·노드/핀·부모/형제 연결·권한을 유지한다. 임의 깊이 제한·자동 별도 함수/계약 복제나 새 권한을 추가하지 않는다. 기존 BlueprintTree의 전체/깊이 안전 예산을 재사용한다.

이번 실행 fixture는 직접 소유 동기 void+int out 공개 함수와 기존 ordinary switch-profile private caller다. caller 자체의 공개 분기/전달 중인 private 분기 계약, native whole-body/this, postCall wrapper, copy provenance와 등록 외부 import는 기존 복합 closure의 다른 경계다. 구형 private profile을 자동 승격하거나 전달 중인 실행 계약을 새 공개 enum으로 치환하지 않는다. 이런 보호를 새 필수 migration이나 무한 타입/소유 조합으로 확대하지 않는다. override 원계약·부모/참조 원본 보호는 그대로다.

## 검사 상태

집중 API에서 잘못된 frame·unqualified ID·낡은 증거·암묵적 profile 변경 거절, cold/receipt, 형제 C# 원문 변경의 최종 CAS와 실제 frame 반환→부모 continuation을 확인했다. 화면 검사에서는 Main 전환 대기 전에 private frame을 찾던 fixture 순서를 고쳤고, 작은 배율의 창 밖 반환 카드는 기존 전체 맞춤으로 조작한다. 실패 로그/DOM/픽셀을 보존하며 강제 클릭·제품 UI/레이아웃 변경은 하지 않는다. 기본 view/독립 창/프로젝트 왕복의 전체 검증을 완료로 표시하지 않는다.

최종 코드의 신규 LF/CRLF·패키지/전체 복원·수명관리 결과는 완료 후 아래에 기록한다. C# 생성기와 M11의 기존 소유/원문 보호를 재작성하는 단위가 아니다. 실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달은 별개 미검증이다. 남은 M12는 실제 복합 caller/provider·native/whole-body·기존 copy provenance 및 등록 외부 import의 계약 결합이며 M4의 확정된 async 호환 정책은 유지한다.
