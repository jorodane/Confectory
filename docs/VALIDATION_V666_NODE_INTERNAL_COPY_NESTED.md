# M11 저장된 same-contract copy의 중첩 내부 흐름

## 원본 요구와 이번 경계

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)이다. `dist/app.js`의 `localImplementationDraft`는 내부 action을 재귀 복제하며 소유 compiled 문맥만 재배치하고, `moduleFunctionDefinition`은 공개 입출력 계약을 유지한다. `dist/blueprint.js`의 `openInternal`은 선택한 동작의 내부 흐름으로 들어간다. 앞서 마감한 저장 copy Root 지원을 중복 구현하지 않고, 이미 저장된 copy의 소유 중첩 graph에서 같은 진입을 연결한다.

이번 경계는 정보에 단독 직접 배정된 단일-target same-contract copy의 기존 private graph 안 **일반 next C# 동작**이다. 전체 private 경로·local node ID·qualified 원문 ID·정의/원문 hash·owner·배정/출처·물리 Root/implementation locator를 함께 검증한다. Root와 다른 frame의 동일 local ID로 저장 대상을 바꾸지 않는다. 새 깊이 제한을 추가하지 않으며 기존 native 깊이/노드/소스/경로 예산을 그대로 적용한다. 실행 검증 fixture는 프로젝트 소유 공개 함수의 copy이며, 등록 함수 copy의 M11 전환 전체를 새로 검증한 것은 아니다.

원래 source record는 guard로 보존하고 새 leaf를 기존 소유 경로에 따로 준비한다. 원문·helpers·공개 입출력 계약·copy ID·출처·조상/형제 graph·값/실행 연결·혼합 profile을 유지하며 C# 자동 재작성이나 부모/외부 원본 복제·수정은 하지 않는다. Root나 정확한 조상에서 Save해도 선택한 private frame과 원래 source binding으로 하나의 후보를 만든다. 기본/독립 정보 창의 기존 내부 버튼·팝오버·빵부스러기·Review→Confirm을 그대로 사용하고 HTML/CSS/JS 레이아웃을 바꾸지 않는다.

## 권한과 저장

기존 native `BlueprintCopyAbi`의 실제 소유/단독 배정/원계약 receipt를 물리 Root 전체에 다시 적용한다. 서버 내부 수명 동안만 사용하는 copy authority에 정확한 private 경로를 포함하고, 하위 멤버십 편집에서도 해당 경로·Root·implementation·owner source hash·copy 출처를 대조한다. 요청자가 만든 boolean이나 임의 frame 문자열은 권한이 아니다. 공개 override 계약 변경·owner 없는 copy·다른 owner에 공유된 copy 단독 변경·donor/부모/외부 쓰기는 기존 보호를 유지한다.

기존 `authorBatch` 전체 source closure·checkpoint CAS·재시도 receipt와 최종 Confirm 파일 CAS를 재사용한다. 원래 private C# guard와 새 leaf는 같은 atomic group이며 부분 Review를 거절한다. 실패/충돌에서는 저장된 입력과 물리 원본을 유지하고, 응답 유실은 같은 수락 receipt를 조회하여 이중 래핑을 막는다. cold의 process-local owner revision 재관측과 정확한 hash/receipt 보호는 앞선 Root 수정 그대로다. 저장 중 늦은 입력은 다음 Save에 남긴다.

## 고정 잔여 대조

| 사용자 흐름 | 이번 이후 분류 |
|---|---|
| 저장된 단독 copy의 Root 일반 C# 내부 진입 | 앞선 완료 지원. 이번 중첩과 함께 영향 회귀한다. |
| 저장된 단독 copy의 소유 private 일반 C# 내부 진입/조상 왕복/Save | 이번 연결·검증 대상. 가능한 깊이/타입 조합마다 새 필수 항목을 만들지 않는다. |
| 생성 중 copy의 내부 진입 | 별도 private copy selection/owner 첫 Save 수명을 가진 기존 M11 어댑터 잔여. 저장 copy 완료와 합치지 않는다. |
| copy의 ref/out·whole-body 문맥·실행 분기 선택기 | 기존 native 의미를 보존해야 하는 어댑터 경계. 이번 일반 동작 지원으로 모두 검증됐다고 하지 않는다. |
| 상속의 직접 소유 body와 상속/참조 원본 진입 | 실제 선언 owner와 선택한 편집 대상을 구분할 기존 M11 경계. readonly 참조를 자동 copy나 부모 쓰기로 바꾸지 않는다. |
| 공개 override 입출력 변경·독립 새 계약 copy·공유 copy 자동 대상 선택 | 정상 계약/소유 보호 또는 필수 범위 제외. 미구현 요구로 확대하지 않는다. |
| private 미지원 기존 profile·독립 편집한 C#/graph의 재활성화 | 기존 구현/정책 경계. 자동 profile 승격·본문 폐기를 추정하지 않는다. |

M4/M12, 고정 ABI 잔여, B2 다른 사용자/그룹 권한 backend, 종류의 C# 실행 표현/사용 중 항목 삭제 대응, 3D·권한 별도 팩은 별도다. 3D 이동 완료는 실행 조건이 아니다. 이 단위는 M11 전체나 전체 UI 완료가 아니다.

## 검증 기록

최종 코드와 집중/독립 LF·CRLF/새 패키지·압축 복원/수명관리 결과는 검증 뒤 구분해 기록한다. fixture 오류와 제품 오류, 신규와 과거 재사용 증거를 섞지 않는다. 생성한 테스트 자료만 사용하며 실제 Windows apphost/WebView2·모바일 기기·Library/Space 전달과 교차 패키지를 구분한다.
