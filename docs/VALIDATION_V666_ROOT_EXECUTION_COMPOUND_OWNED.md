# 다른 소유 함수를 함께 호출하는 M12 거래

## 원래 흐름과 변경 경계

v666 `dist/blueprint.js:248`은 한 동작의 결과 분기를 처리한 뒤 원래 다음 동작으로 이어 간다. 따라서 다른 직접 소유 함수가 같은 호출자의 import에 있다는 이유만으로 공개 분기 편집 전체를 막는 것은 원래 사용자 흐름의 누락이다.

직접 소유한 동기 void 함수의 기존 target·명시 직접 호출자 거래를, 다른 직접 소유 함수 계약을 함께 사용하는 ordinary caller에 연결한다. 추가 계약 헤더는 변경하지 않는 관측 멤버다. 같은 qualified namespace·기존 import와 provider 선택을 사용하며 자동 대상 선택이나 새로운 권한을 만들지 않는다. 독립적으로 수정 중인 추가 계약은 먼저 확인하도록 거절하고, 영수증·원문·기존 호출/핀/연결·C#과 readonly 파일 모드를 보존한다.

추가 헤더를 포함한 완전한 그룹과 최초 관측 해시를 저장·복원·Review·최종 CAS에 결합한다. 누락/변조 영수증이나 추가 계약의 draft 변경은 거절한다. 기존 다른 호출의 결과·후속 동작은 원래 순서대로 유지하고, 사용자가 명시한 공개 분기 반환 연결만 실행 경로를 바꾼다. 레이아웃·공개 IO·override 계약은 바꾸지 않는다.

## 검증 상태

readonly 추가 계약·provider/C# 파일, ref int/out long/out string의 기존 데이터 연결, 다른 int 반환 호출을 사용하는 실제 프로젝트 fixture로 API·화면과 원자 실패·복구·실행을 검증한다. 최종 동결 LF/CRLF·새 패키지/전체 복원·실패 수명관리와 신규/재사용 구분은 마감 시 기록한다. 실제 Windows/모바일 실행·전체 UI·Space/Library 전달을 뜻하지 않는다.

## 유한한 잔여

이 단위는 다른 import의 모든 문맥을 자동 지원한다는 뜻이 아니다. 중첩/private 호출, 등록 외부 import의 readonly receipt와 여러 provider의 계약 변경을 포함한 완전한 복합 closure는 같은 기존 M12 항목의 잔여다. 부모/참조 원본 직접 쓰기·공개 override 계약 변경은 정상 보호다.

비void의 값 반환은 별도 저장/표시 연결이 필요하다. 기존 private 호출의 `native-return-out-v1`처럼 원래 Invoke와 C#를 보존하는 별도 결과 어댑터는 내부 구현 선택이며, 임의로 반환 값을 버리거나 본문을 enum/tuple 반환으로 다시 쓰지 않는다. M4의 동기 IInvoke 소비자/async provider 호환성은 사용자 결정 대기이며 이 동기 거래와 독립적이다.

이전 authoring 패키지는 이 추가 import 그룹의 미확정 checkpoint 편집/복원을 지원한다고 보장하지 않는다. 최신/롤백의 source와 전체 manifest를 보관하고 기존 checkpoint를 자동 삭제·승격하지 않는다.
