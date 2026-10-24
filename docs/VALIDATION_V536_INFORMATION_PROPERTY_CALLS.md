# v536 I5-6 1행: property 수신자와 기존 특수 호출

[고정한 네 조작](V536_I5_6_ROW1_SCOPE.md)을 기존 함수 상세창·입력 연결 선택창과 후보/CAS에 연결했다. property 수신자는 같은 타입의 현재 입력을 고르고, 쓰기 값은 명시 값/호환 입력을 고른다. 기존 bool branch, 실행 enum code, 소유 call의 branch·serial After·enum After에서도 값 인자를 대응한다. 다른 ref/out 인자, wrapper/enum·출력·경로와 C# 본문/helpers는 그대로 둔다.

## 확인한 원인과 변경

이 경로의 `InformationFunctionContracts`는 Core graph 검증에 property descriptor와 고정 accessor 계약을 전달하지 않았다. 입력 사용처 조회도 `next`와 wrapper 없는 call만 받아 기존 branch/enum/After의 값 인자를 제외했다. 이는 기존 명세로 결정되는 미연결 구현이며 새 사용자 설계 결정이 아니다.

`InformationFunctionProperties`는 기존 `RuntimeObjectContracts`로 소유 object/concept와 schema/상속 선언을 읽고, 원래 선언 초안을 같은 타입 경계에서 적용한다. Core의 필드 hash·소유·SafeFieldRef·타입 검사를 그대로 사용한다. `Confectory.ObjectModel::Read/Set/RefCell`의 **선언**과 기존 typed import 하나가 일치해야 한다. accessor/provider 구현 본문이나 실제 getter·runtime 값을 읽거나 실행해 계약을 추측하지 않는다.

선택 시 property 의존 선언·등록 manifest·accessor 선언의 관찰 해시를 `contracts` 증거로 묶는다. 같은 graph의 선택 바인딩은 이 증거를 포함해야 하며 저장에서 다시 계산한다. graph 원문/hash와 함께 원래 기준을 검사하므로 같은 ABI의 주석 변경이어도 선택 후 원본 변경을 조용히 수용하지 않는다. 기존 관찰/CAS 및 receipt에 묶어 전체 성공/전체 미적용을 유지한다. 증거가 없는 이전 property 선택은 자동으로 새 동의/선택으로 승격하지 않는다.

수신자에는 object 리터럴/null을 추정하지 않고 기존 object 입력만 표시·허용한다. 타입이 다른 입력, 위조/누락 receipt, 필드/등록 변경은 전체 거절한다. 원래 v536 CSS와 창 배치는 유지하고 기존 선택창에서 처리한다. 상세창의 명시적 저장으로 같은 편집의 선택창을 다시 열 수 있으며, 기존 값은 보관한다. property receipt가 없는 legacy form을 새 의존 계약에 자동 재사용하지 않는다.

특수 호출은 **callee와 node 매개변수 계약이 그대로인 값 바인딩**이다. `branch/switch`의 기존 의미와 source/enum/branchOwner/연결을 보존한다. wrapper는 원래 public output hash·serial/enum 모드·native return mapping을 검증한다. 자기 호출은 기존 생성 API가 거절하므로 새 지원 기능으로 추가하지 않는다. callee 서명을 바꾸어 C# After의 형식 매개변수 자체가 달라지는 경우, 전체 본문/ref 역할 변경, 중첩·등록/복사 문맥은 고정 4~7행의 별도 계약 편집이다. 원본에 없는 분기/반복을 추가하지 않는다.

## 실제 검증

사용자 자료가 아닌 격리 fixture를 사용했다. property fixture는 Read→Set→Read→RefCell의 같은 필드/수신자 계약과 C# 소비자를 갖는다. ObjectModel 팩은 격리 복사본이며 충돌 주입도 그 복사본과 fixture 선언에만 한다. 특수 호출 fixture는 code bool branch, call bool branch, code 실행 enum, serial After, enum After와 각 기존 지역/계속 경로를 갖는다. callee에 변경하지 않는 ref/out 인자가 있는 경우도 포함한다.

현재 API: property 수신자 삭제 3·쓰기 값 삭제 3·특수 호출 3·다른 ref/out을 보존하는 특수 호출 3 check가 통과했다. property 보호 3 check는 receipt 변조/누락·null/다른 타입 수신자, 선택 후 accessor/등록 manifest/필드 선언 변경의 전체 거절과 peer/checkpoint 보존을 확인했다. Native 관찰 경로에서 외부 provider body를 읽지 않은 것도 확인했다. 초기 fixture에서 이미 provide가 있는 함수에 새 함수 생성 API를 호출한 가정은 정확한 원래 서명 해시로 수정했고 제품 보호를 완화하지 않았다.

UI: 독립 property 타입 변경·쓰기 실패/재시도 3, property 저장·조회 응답 유실/cold 2, 기본 창 변경 취소 2, ref/out 보존 특수 호출의 타입 변경·쓰기 실패/재시도 3, 거절→같은 세션 Undo→새 선택→Save/Confirm/cold 3, 동시 편집 거절 2 check가 통과했다. 화면에서 원문/다른 입력·정확 64비트 값과 모달 inert 정리도 확인한다. 같은 편집의 명시적 재선택·취소/수락·Save/Confirm/cold 3 check도 통과했다. 새 UI 합계는 18 check다. 최종 renderer 소스의 프로젝트 전환/오래된 form 거절 2 check와 Native 계약 7·기존 call 보호 2·기존 수식/별칭 API 3·ABI 어댑터 3·값 표시 2·Set/별칭 후보 보호 3을 합친 영향 회귀 22 check가 통과했다. 재선택 테스트의 초기 즉시 표시 판정은 비동기 modal 표시 완료 대기로 바로잡아 검사했다. clean checkout·패키지 결과는 아래에 마감한다.

근거는 `/workspace/scratch/v536-information-property-calls`다. 실제 Windows apphost/WebView2·모바일 기기·계정 로그인/유료 추론·사용자 프로젝트 Run·Library 전달은 이 검증이 아니다. 전체 solution/full suite를 실행했다는 뜻도 아니다.

## 다음 3행의 경계

1행의 위 지원 문맥을 마감한 뒤 3행으로 진행한다. 첫 최소 후보는 원래 단일 소유 함수의 일반 직렬 출력에서 `BlueprintRootContract.adaptOutput`의 명시 새 값/타입과 caller `remap.outputs`를 결합하는 것이다. 이어 `outputCreates/removeOutputs/outputRoutes`를 같은 후보/CAS로 연결한다. 출력·반환 소비자의 타입/핀 식별성이 맞지 않으면 전체 미적용과 원문 보존으로 처리한다. C# 문자열 치환이나 위치별 추측, 자동 연결 삭제는 하지 않는다. 기존 9행을 늘리지 않는다.


[수신자 선택](evidence/v536-information-property-calls/property-picker.png), [기존 특수 호출의 값 선택](evidence/v536-information-property-calls/special-picker.png)을 실제 renderer에서 확인했다. 저장/확정 후 원래 정보 화면과 CSS 세 파일의 baseline 9962759 byte 일치 근거도 같은 evidence 디렉터리에 있다. 스크린샷은 전체 pixel 일치나 Windows native 조작 검증을 의미하지 않는다.
