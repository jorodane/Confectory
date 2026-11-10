# module interface의 공개 실행·async 계약

모듈 require가 가리키는 함수의 기존 C# 계약을 그대로 호출한다. 직접 소유하거나 이미
등록된 읽기 전용 정의를 관찰하며, interface 생성은 provider/default를 선택하거나 실행하지
않는다. 요구 함수·정보 정의·모듈 원문과 원래 함수 IInvoke를 재작성하지 않는다.

`module-interface-flow-v1`은 기존 `Call_<function symbol>` native 메서드를 유지한다.
공개 실행 분기가 있으면 `Call_<symbol>Execution`을 추가한다. 반환 타입은 그 함수의 기존
`ExecutionResult`이며 원래 ref/out과 비void 반환용 별도 out capture를 유지한다. async
요구에는 `Call_<symbol>Async`를 추가하며, 반환 타입은 기존
`Task<FunctionResult>`이고 입력 및 결과 DTO는 `BlueprintAsync`와 같다. 분기 번호·ID와
None=0, 결과 데이터 이름 충돌 회피도 기존 생성기를 사용한다. 별도 복제 enum/DTO,
임의 변환, 동기 대기나 caller 자동 전환을 넣지 않는다. async 요구의 native/동기 실행
메서드는 기존 직접 함수 계약처럼 Obsolete(error=true)로 거절한다. 호출자는 명시적으로
async 호출과 await를 작성해야 한다.

primitive-only/basic 및 기존 nominal-only 모듈의 profile/source/shape는 유지한다. 새 flow
shape에는 요구 함수의 생성 계약 hash와 async completion ID를 포함한다. 분기 표시명은
CLR 심벌·번호를 바꾸지 않는다. 실제 원문 해시는 기존 읽기 receipt와 최종 CAS가 별도로
관찰하므로 ABI가 같은 표시명 변경도 검토 이후 임의로 덮어쓰지 않는다.

공개 결과 DTO가 정보 struct를 쓰고 모듈 interface가 그 DTO를 쓰면 pack DLL들이 서로
참조한다. 빌더는 선택된 모듈의 공개 함수 선언 closure를 모으고 다음과 같이 컴파일한다.

1. 같은 assembly/type 이름과 struct/enum/interface 종류의 임시 nominal 선언을 만든다.
2. 이 선언을 참조하여 원래 전체 함수 계약 DLL을 컴파일한다.
3. 실제 정보·모듈 source를 실제 함수 계약 DLL에 대고 컴파일한다.
4. 실제 정보 DLL과 함수 DLL만 구현 컴파일·링크·catalog에 전달한다.

임시 선언은 캐시 입력이며 실행 패키지에 포함하지 않는다. assembly 이름과 public type
identity를 합치거나 바꾸지 않는다. 실제 정보/source와 함수 source 전체, 도구 identity를
캐시 키에 넣으므로 깊은 shape 변경도 양쪽 실제 DLL을 갱신한다. 이미 거절하던 inline
정보 타입/pack 순환을 임의로 허용하지 않는다. Check/Build가 고른 전체 계약 범위 밖으로
컴파일된 flow pack을 사후 확장하는 요청은 기존 CONTRACT_SELECTION 경계에서 거절한다.

기존 소유 C# 본문 후보 검증도 관찰된 모듈의 공개 함수 선언을 같은 Roslyn 컴파일에
포함한다. 원래 입력·본문 및 read guard, Review/Confirm과 최종 CAS는 유지한다. 새로운
picker/provider UI, 권한, override 계약, 참조 객체 조회나 자동 수명 정책은 추가하지 않는다.

이 단위의 종료 기준은 실제 동일/분리 pack의 nominal 결과·분기·Task dispatch, 동기 호출
거절, 기존 ordinary module golden 및 등록 권한 거절, 본문 저장의 중단·충돌·재시작 경로,
최종 LF/CRLF와 새 패키지/전체 복원을 검증하는 것이다. 정보 참조 bridge/수명과
reference/function 필드 생성은 같은 고정 9행의 별도 잔여다. 이번 연결만으로 9행 전체나
실제 기기/전체 UI 수용을 완료로 세지 않는다. 구 reader는 flow module 생성을 거절하며
자동 downgrade/migration은 하지 않는다. 초기화 빈 화면의 원인은 여전히 미확정이다.
