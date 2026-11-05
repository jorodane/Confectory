# V2: 일반 설명 저장의 실패 복구와 안내

보관한 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 313–317·1267·1291행에 대응하는 저장·확인 흐름이다.
지정한 native 안내 11개/기존 표시 13곳을 “습니다/주십시오” 문체로 맞춘다.
[정확한 변경 허용 목록](v666-description-recovery-delta.json)은 원본 문장의 복제와
native 저장·실패 조건의 문체 적용을 구분한다. backend 진단을 전역 번역하지 않는다.

## 재현한 누락과 지원 범위

수정 전 `d63e8f7`에서 생성한 소유 프로젝트로 다음 손실을 재현했다.

- 직접 소유 root code 동작의 설명(intent): 일반 Save가 live 초안을 먼저 수정하고
  개인 입력을 지운 뒤 checkpoint 쓰기에 실패하면, 재시작 시 이전 설명만 남았다.
- 직접 소유 함수의 설명 단독 편집: 동일한 쓰기 실패 손실이 발생했다. 설명을 가진 채
  기존 Blueprint 직접 편집에 진입하면 checkpoint 저장 없이 입력을 지우는 경로도 있었다.

root code의 설명과 기존 인자 값은 기존 authorBatch의 후보/checkpoint CAS/receipt로
저장한다. 함수 설명 단독 입력은 원래 revision/hash를 그대로 기존 소유 표시 입력으로
옮겨 applySlots의 원자 저장과 정확한 receipt 복구를 이용한다. 혼합 계약 입력은 자동
이관하거나 재기준화하지 않는다. 두 경로 모두 실패·응답 유실·늦은 새 입력·재시작을
구분하고, 확인된 입력만 제거한다. failed root intent 시도를 새 설명으로 대체하려면
원래 checkpoint·전체 source proof와 물리 원본이 미변경이고 이전 쓰기가 미반영임을
확인해야 한다. 미확정/peer 변경은 기존 입력과 시도를 보존하며 거절한다.

설명 수정 전후의 공유 초안 Undo/Redo도 유지한다. 기존 기록기를 후보 snapshot에만
적용하고 checkpoint 성공 후 함께 승격한다. root intent 또는 함수 description-only이고
unit ID/kind/path가 그대로인 경우로 제한한다. 구조·소유권 변경의 history boundary와
기존 32개/용량 제한은 유지하며 새 공개 API나 권한 계약을 만들지 않는다.

동작 intent는 의미를 갖는다. 수정 뒤 원래 C#은 `needs-implementation` 상태이며,
사용자가 기존 C#을 명시적으로 확인·적용해야 Review/Confirm할 수 있다. 원문을 자동
변환하거나 준비 상태를 자동 승인하지 않는다. 함수의 표시 설명은 실행 계약을 바꾸지
않는다. 일반 Save는 물리 원본을 쓰지 않으며 최종 Confirm의 원본 CAS를 유지한다.

## 별도 잔여와 검증 한계

코드/rename/route/root 핀·export와 함수 signature+description 혼합 등 다른 레거시
일반 Save는 읽기 점검 후보이며 이번 실패 주입·수정 완료에 포함하지 않는다.
소유 원시 편집/독립 창의 기존 snapshot·receipt 보존 경로도 읽기 점검했지만 이번에
전체 UI를 재검증한 것은 아니다. 이미 완료한 C# 14개/16곳과 값·핀 15개 안내는 보존한다.

[최종 검증 기록](VALIDATION_V666_DESCRIPTION_RECOVERY.md)에 신규·재사용·미실행,
개발 실패와 테스트 보완, 패키지/복원과 수명 정리 범위를 구분한다. V2의 나머지 계약/
일반 검토·탐색·시스템 안내 및 V3–V9, 기존 팩/backend·종류 호환성 결정과 실제 기기·
전체 UI·Space 전달은 고정 잔여로 유지한다. M11/M12/M4를 새 조합 잔여로 다시 열지 않는다.
