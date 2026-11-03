# M4 비동기 실행의 현재 경계

기준은 저장소에 보관한 v666 `js/blueprint.js`의 비동기 전환(120–176), 실행 순서(248), 컨텍스트 메뉴(949)다. 호출자의 비동기 상태를 자동 추론하는 원본의 동작(113–118)은 사용자 합의로 대체한다. 동기 호출자가 비동기 함수를 호출하면 명시적으로 호출자를 바꾸기 전에는 오류다. 동기 blocking이나 자동 소스 재작성은 하지 않는다.

## 이번 런타임 단위

직접 소유 함수의 명시적인 `blueprintAsync` metadata(`schema:1`, 고유 `completion` ID)와 `async-acyclic-switch-v1` graph를 연결했다. 일반 C# 동작을 명시적으로 async로 표시하여 실제 Task/await를 실행하고, Blueprint 호출자도 명시적으로 async인 경우에만 그 호출을 실행한다. 값 입력·out·native 반환과 기존 공개 실행 분기의 ID/숫자값을 유지한다. ref 입력과 호환되지 않는 호출은 거절한다.

기존 `IInvoke`의 메서드 모양은 남기고 비동기 계약에서만 오류로 표시한다. 새 `IAsyncInvoke.InvokeAsync`는 native 반환·out·실행 결과를 가진 Task 결과 객체를 돌려준다. 동기 C# 구현의 import에는 IInvoke만 노출하여 InvokeAsync에 바로 접근할 수도 없다. 생성된 동기 어댑터도 기다리지 않고 명확한 오류를 낸다. 기존 동기 계약에는 이 확장을 적용하지 않는다. 이름이 Branch/Return/FunctionResult인 출력과 충돌하지 않도록 생성 이름을 배정한다.

실행 순서는 await 완료 → 결과의 out/native 값 게시 → completion 영역 → 정확한 결과 분기 → 다음 동작이다. 완료 영역이 비어 있거나 결과가 None이어도 다음 단계가 누락되거나 암묵적인 성공 분기가 선택되지 않는다. 원래 Task 예외는 그대로 전파하며 실패 분기 값으로 바꾸지 않는다. 동작의 C# source/헬퍼는 재작성하지 않고 Execute 이름과 source marker를 유지한다.

새 직접 소유 async 정의의 scaffold와 일반 direct Blueprint caller는 metadata/소스 API에서 생성·검증·빌드할 수 있다. 이 단위는 기존 화면/레이아웃이나 저장 권한을 바꾸지 않는다. 현재 async metadata는 부모가 없는 직접 선언에 한정한다. 기존 opaque/native instance 본문을 자동으로 Task로 바꾸거나 override의 공개 계약을 바꾸지 않는다. 다른 target에 opaque 본문이 남아 있는 계약도 묵시적으로 변환하지 않는다.

## 유한한 남은 사용자 흐름

1. 직접 소유 ordinary Root의 원본 메뉴·함수/동작 플래그·시계/완료 포트·checkpoint·전체 Review/Confirm 연결은 [명시 전환 지원 경계](M4_ASYNC_TRANSITION.md)를 따른다. 연결된 완료 포트의 동기 복귀 처리와 새/내부 소유 본문의 실제 연결은 남는다. 전체 M4/UI 완료로 표현하지 않는다.
2. 그 전환에서 실제 기존 C#·내부/소유 본문을 보존해야 하는 경로를 확인한다. 기존 native/whole-body 문맥, 상속·참조 및 등록 외부 계약을 자동 편집하지 않는다. 실제 소유 편집과 정상 비소유 거절을 구분하여 원래 전환 흐름만 닫는다. 타입/문맥 조합마다 새 필수 항목을 추가하지 않는다.

M12는 [고정 마감표](M12_CLOSURE.md)에서 닫혔다. 종류 C# 표현·사용 중 항목 삭제 대응, V2–V9 및 기존 별도 UI/팩/backend와 실제 Windows/모바일·Space 전달은 기존 수용 표의 별도 항목이다. 권한과 3D 표시는 별도 팩이며 이동 완료는 실행 조건이 아니다.

## 검증

`tools/verify_desktop.py --suite async-runtime`은 독립 LF/CRLF checkout에서 async/기존 switch·M12 실행 및 소유 경계, 기존 M12 저장·중단·취소·Undo·cold restart·응답 유실·늦은 입력·외부 충돌을 새로 실행한다. 새로운 async 전환 UI의 검사로 부르지 않는다.

`tests/probes/async_runtime.py`는 checkout·새 교차 패키지·전체 압축 복원본 각각의 실제 Core/CLI/metadata/컴파일러로 생성한 테스트 프로젝트를 빌드·실행한다. await와 출력/완료/분기 순서, 반복, 원래 Task 오류, 실행 중 자체 child 중단·재시도, 동기 호출자 거절 및 원문 보존을 검증한다. 최신/롤백·전체 manifest/SHA·복원 검증·실패 수명관리와 소유 임시물 종료 정리는 기존 절차를 유지한다. Linux에서 수행한 검사이며 실제 Windows 실행을 뜻하지 않는다.

## 보관본/호환성

최종 신규 LF22·CRLF20·패키지/전체 복원/실패 수명관리8, 총50단계가 통과했다. [전체 기록과 지속 패키지·공간](VALIDATION_V666_ASYNC_RUNTIME.md)을 따른다. 보조 pure metadata 3개는 별도 증거이며 50단계와 중복 계산하지 않는다.

롤백 M12 패키지는 기존 동기 자료의 정상본이다. 새 async metadata는 기존 value 문법을 사용하지만 구버전 compiler/editor는 새 async graph profile을 지원하지 않으므로 새 자료의 실행/편집을 보장하지 않는다. 코드 rollback만으로 새 async 프로젝트를 자동 변환하지 않는다. 최신 패키지·원본/초안 증거를 함께 보존하며 필요한 데이터 복원과 정상 보유 원본을 구별한다.

명시 전환 UI의 후속 최종 검증은 [별도 기록](VALIDATION_V666_ASYNC_TRANSITION.md)의 신규 40단계·재사용 0을 따른다. 이전 런타임 50단계와 중복 계산하지 않는다.
