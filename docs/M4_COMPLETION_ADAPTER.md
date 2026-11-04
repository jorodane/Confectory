# M4 · Result 없는 ordinary C# 완료 복귀

기준은 저장소 v666 `blueprint.js`의 명시적 비동기 전환과 완료 줄이다. 동기 호출자는 명시적으로 async로 바꾸기 전까지 오류로 막는 사용자 결정을 유지한다. 동기 대기나 호출자 자동 전환은 추가하지 않는다.

이번 단위는 직접 소유한 기존 ordinary Root 안의 `next` C# 동작이다. 값 인자·out 출력과 void/native 반환을 유지하며, 연결된 async 완료를 같은 ID·정수·literal 포트의 일반 분기로 복귀한다. 원래 Execute 본문·helper·소스 marker를 재작성하지 않는다. `Result`라는 원래 helper도 별도 선택기와 충돌하지 않는다.

`completionAdapter: {schema:1, source:...}`는 원문과 다른 클래스에서 실행되는 지역 선택기다. 원래 코드가 먼저 한 번 실행되고, 입력·out·native 반환을 readonly `SourceContext`로 전달한다. 참조 값은 기존 객체 정체성을 유지하며 복제하지 않는다. 선택기는 기본 `Result.None`이다. 일반 완료는 명시적으로 그 멤버를 반환할 때만 실행하고 이후 기존 다음 줄을 계속한다. async 재활성화는 같은 완료 ID를 사용하며 제거된 일반 완료 멤버를 참조한 사용자 코드를 자동 고치지 않는다. 잘못된 선택기는 컴파일 오류로 표시한다.

원본 C# 팝업의 레이아웃을 재사용한다. 밝은 원문·별도 선택기 영역을 편집하고 고정 서명/helper·snapshot 선언을 표시한다. 선택기만 편집하면 원문 CRLF도 유지한다. 기존 원문을 편집한 경우에는 사용자가 입력한 C#만 반영한다. selector source도 기존 Roslyn body 검사와 독립 진단 marker를 거쳐 generated 영역 탈출·예약 이름·위치 remapping을 차단한다.

전환 후보와 이후 선택기 편집은 전체 소유 target/code 및 실제 호출자 관측을 포함하는 원자 저장·Review→Confirm·최종 CAS 그룹을 사용한다. 별도 선택기 편집은 공개 함수/implementation header를 바꿀 수 없다. 취소·실패·응답 유실·늦은 입력·재시작은 기존 입력 보존 규칙을 따른다. 비소유/부모·외부 원본, override 계약, ref 및 legacy profile 보호를 완화하지 않는다.

이 metadata를 모르는 구버전 parser/runtime으로 새 그래프를 읽는 호환성은 보장하지 않는다. 최신/롤백 패키지의 출처와 전체 복원 검증을 유지하며 유일한 데이터의 구버전 변환을 하지 않는다.

유한한 M4 후속은 instance/native whole-body의 소유 문맥 보존과 새/직접 소유 내부 본문의 명시 전환이다. 이번 ordinary adapter는 그 완료를 주장하지 않는다. 기존 Result/공개 완료·Set·속성 편집은 완료 범위를 유지한다. M11/M12를 새 조합별 잔여로 다시 열지 않으며 V2–V9·팩/backend·종류 호환성·실기기/전체 UI/Space 전달은 기존 고정 잔여다.

최종 검증 중 cold에서 남은 새 선택기 입력의 proof가 이전 프로세스 revision을 가진 채 남는 결함을 확인했다. 같은 저장 영수증을 두 번 확인하고 전체 원본 ID/bytes가 일치한 경우에만, 원래 입력 key·node·종류·proof로 묶인 늦은 입력을 현재 수락 기준에 연결한다. 원문이 다른 peer/누락/변조 proof로 재기준화하지 않으며, 새 텍스트 자체는 바꾸지 않는다. 이전 결과 확인은 새 입력의 자동 저장이 아니다. 별도로 누른 Save가 새 입력을 한 번 저장한다.

최종 동결 `76f9837`의 [48단계 검증·신규/재사용·보관 기록](VALIDATION_V666_COMPLETION_ADAPTER.md)을 마감했다.
