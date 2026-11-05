# V2: 여러 값 입력 중 하나의 이름 저장 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 1196행 `offerIdentifier`와 기존 native
`rootParameters`/`blueprintRootContract`의 명시 remap이다. 원래 입력 이름 편집은
입력이 둘 이상인 함수에도 노출되지만, 이전 원자 저장 진입은 입력이 정확히 하나일
때만 허용했다. 입력 개수별 새 기능을 만드는 대신 이 기존 이름 편집 한 동작의
저장 실패 복구를 연결한다.

## 재현과 지원 경계

게시본 `8649dbdb9216d14bdf03a37b5b5e53099eaef92d`에서 두 int 입력 `amount`,
`scale` 중 두 번째 이름을 `multiplier`로 바꾸고 checkpoint 쓰기를 실패시켰다.
live에는 새 이름이 남고 개인 계획은 사라졌으며, cold 복원에는 원래 `scale`만
돌아왔다. checkpoint·물리 원본·C# 본문/호출자 bytes는 그대로였다. 기존 함수 실행은
`Pair.Invoke(7,3)`의 결과 10을 유지했다. 이 실패를 수정 전 증거로 보관한다.

직접 소유한 동기 ordinary nonvoid root에서 기존 1–64개 값 입력 중 **하나의 이름**만
바꾸는 단일 계획을 원자 후보·checkpoint CAS·receipt·공유 Undo/Redo에 연결한다.
변경 없는 같은 이름 Save도 기존 receipt 의미를 유지한다. 전체 입력의 이름/타입과
모든 기존 이름을 포함한 명시 remap을 검증하고, 입력 수·위치·타입·mode·반환 타입·
출력 순서를 보존한다. 이름은 기존 ASCII 식별자/길이 규칙을 따른다. 다른 입력은
identity remap이어야 하며, 두 이름 변경·중복 이름·순서/타입/개수 변경은 거절한다.

본문의 인자명과 C# 원문·호출자 bytes를 다시 쓰지 않는다. 기존 위치 기반 실행 계약과
원래 node ID·값·연결을 유지하고 root 참조만 기존 명시 remap으로 옮긴다.
private/slot/copy·부모/외부 원본·공개 실행 분기/async·문맥 전달·다중 body·다른 구현
공유·override 계약의 기존 보호를 유지한다. 새 핀 ID·타입 마이그레이션·표시명 정책을
추가하지 않는다.

## 실패·늦은 입력·검토

원자 저장 실패 전에는 live나 물리 원본을 쓰지 않는다. 미적용 receipt·같은 checkpoint·
전체 원본 proof가 확인된 경우에만 개인 입력을 명시 재시도한다. 실패 뒤 개인 Undo로
취소한 이름은 Save가 재적용하지 않는다. 응답 유실은 확정 receipt를 회수하며 저장을
재생하지 않는다. 늦은 입력은 자신의 원래 전체 remap을 역으로 대조하고 현재 전체
이름/타입이 확정 요청과 일치할 때만 새 기준으로 연결한다. 예를 들어 `scale`에서
`multiplier`를 저장하는 동안 입력한 `factor`는 다음 계획의 `multiplier → factor`로
남고, 첫 입력 `amount → amount`도 보존한다. 동료 변경·불완전 대응은 허용 근거가
아니며 입력을 유지한 채 거절한다.

함수·구현·그래프 세 멤버의 zero-dirty 묶음, 이후 별도 본문 저장 receipt, 공유
Undo/Redo·cold 복원은 기존 그룹 계약을 따른다. Review 취소와 Confirm 직전 물리
그래프 충돌을 검사하고 새 Review→Confirm 뒤에만 원본을 반영한다. 기존 팝오버·
레이아웃·안내·권한·writer·receipt 형식·보관 수명 정책을 바꾸지 않는다.

[정확한 delta](v666-root-value-rename-recovery-delta.json)와
[최종 검증 기록](VALIDATION_V666_ROOT_VALUE_RENAME_RECOVERY.md)을 따른다.

## 남은 고정 범위

다른 root 정의·혼합 계약·직접 배치 형태는 실제 재현을 확인할 점검 후보이며 조합마다
새 필수 항목을 만들지 않는다. 완료 M11/M12/M4를 다시 열지 않는다. 나머지 V2 안내·
V3–V9·기존 팩/backend·종류 호환성 결정·실제 Windows/모바일·전체 UI·Space 전달은
고정 수용 표의 별도 잔여다. 생성 fixture만 사용하고 실제 계정/외부 접근·live AI는
사용하지 않는다.
