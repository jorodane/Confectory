# 동기 void의 typed out·ref와 공개 실행 분기

## 원래 요구와 지원 의미

저장소 v666 `dist/app.js:2469–2476`의 원계약 우선과 `dist/blueprint.js:248`의 출력 발행 → 결과 분기 → 다음 동작 순서를 따른다. 기존 `IInvoke`/`IExecutionInvoke`는 같은 value/ref/out 인수를 이미 타입 그대로 전달한다. 이번 변경은 정수 out 하나로 제한하던 수용 검사를 동기 void의 기존 value/ref/out 계약으로 확장한다. 공개 C# 원문을 다시 쓰거나 새로운 반환 tuple/타입을 도입하지 않는다.

직접 소유 함수와 명시한 Blueprint target·직접 호출자에 공개 분기를 정의하고, 여러 typed out과 실제 ref 저장소 변경을 분기 전에 전달한다. ref는 기존의 쓰기 가능한 정확한 타입 저장소만 허용하며 상수·타입 변환을 참조로 취급하지 않는다. 연결되지 않은 종료점은 기존 None/출력 기본값 규칙을 사용하고 예외를 실패 분기로 치환하지 않는다. 원본 ID/연결·배정·권한·Review/Confirm·최종 CAS와 레이아웃은 유지한다.

ordinary 비void 반환과 실행 분기를 함께 전달하는 어댑터, 복합 호출 계약 closure와 M4는 별도 실제 잔여다. 부모/외부 원본 쓰기와 override 계약 변경은 정상 보호이며 새 독립 계약 복제·구형 profile 자동 승격은 추가하지 않는다.

직전 패키지는 공개 분기 계약에서 정수 out 하나만 수용한다. 이번에 만든 ref/여러 typed out의 공개 분기 metadata를 그 롤백 실행기로 읽을 수 있다고 보장하지 않는다. 기존 원본을 재작성하거나 새 metadata를 지워 호환시키지 않으며, 최신·정상 롤백 패키지의 source와 manifest를 구별해 보관한다.

## 검증 상태

최종 코드 동결 후 직접 소유 함수의 ref int·out long·out string을 실제 저장/실행하는 API와 화면, 분기보다 먼저 보이는 typed 데이터·동일 셀의 두 ref 별칭·ordinary Invoke·None 기본값 native 검사와 관련 회귀를 검증한다. 검증 결과·실패·재사용 여부와 패키지/복원 보관 근거는 마감 시 기록한다. 실제 Windows/WebView2·모바일 실행이나 전체 UI/Space/Library 완료를 뜻하지 않는다.
