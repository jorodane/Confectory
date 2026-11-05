# V2: 새 일반 동작 직접 배치의 첫 저장 복구

보관된 v666 `Confectory-v666/dist/blueprint.js` 1361행의 **동작 만들기**와 기존
설명·직접 C# 작성·실행선 연결·Save를 이어 사용하는 흐름이다. 새 UI나 공개 함수 계약을
추가하지 않는다. 직접 소유 root 그래프에서 새 일반 void 동작 하나를 만들고, 원래
일반 next 동작의 다음 줄에 명시적으로 삽입한 경우를 이번 최소 단위로 다룬다.

## 재현과 기존 계약

게시본 `f9d06b8bf99d6cee5823a6f8835978ff5bc4306c`에서 생성·이름·설명·본문·두 실행선을
입력한 뒤 checkpoint 쓰기를 실패시키면 `consumer_error`가 표시됐지만 개인 입력 6개가
모두 지워졌다. 새 동작은 live 작업 사본에만 있었고 checkpoint는 원래 그대로였다.
재시작 후 새 동작·본문·두 연결이 사라졌다. 물리 원본은 그대로이며 입력·traffic·실패
화면·checkpoint 관측을 보존한다.

기존 native `authorBatch`의 createNode/source/rename/intent/route 후보가 이미 이 여섯
입력을 한 checkpoint로 원자 저장하고 동일 attempt의 cold receipt를 회수한다는 것을
제품 수정 전에 확인했다. native 후보의 편집 허용·권한·최종 CAS·C# 생성 의미는 바꾸지 않는다. 일반 생성의 미적용
기준 관측이 없던 부분은 아래 같은 닫힌 범위의 읽기 증명으로 보완한다.

## 수정 경계

기존 UI의 원자 저장 선택에 직접 소유 root, 새로운 code/next/void/인자 없음 동작 하나,
생성·이름·설명·본문·route 두 개의 여섯 입력만 연결한다. 들어오는 연결은 기존 일반 next
동작이어야 하며, 나가는 연결은 그 원래 다음 목적지와 같아야 한다. 원래 실행선을 둘로
명시 분할하는 흐름이다. branchOwner·copy/slot/private·비소유·다른 계약/혼합 입력을
이 경로로 허용하지 않는다. 기존에 지원된 별도 경로는 유지한다.

미적용 관측은 같은 여섯 native edit의 모양·직접 소유 root·새 ID 부재·원래 next 목적지를
대조하고, checkpoint/live checkpoint 버전·전체 소스 ID/해시·물리 원본이 모두 같아야 한다.
새로 생긴 경로는 기존 후보/최종 expected-missing CAS가 다시 확인한다.

실패한 원래 시도는 native가 미적용/원본 동일임을 확인한 뒤, 같은 ID·생성 정의·두 연결·
입력 proof를 유지한 이름/설명/본문 수정에만 교체한다. 이전 시도 기록은 새 시도가 정착할
때까지 보존한다. 다른 입력이 섞이면 기존 live 변경 경로로 돌아가지 않고 모두 보존한다.
응답 유실은 정확한 receipt만 회수하며 ID·본문·실행선을 다시 생성하지 않는다. 적용 중
생긴 늦은 본문은 기존 receipt 복구 뒤 별도 source 후보로 저장한다.

원본 화면·문구·팝오버·레이아웃·공개/override 계약·기존 source/ID/핀/값/연결과 부모/외부
원본·권한을 보존한다. 명시한 graph 삽입과 새 본문 파일은 Review→Confirm/expected-missing
최종 CAS 뒤에만 물리 반영한다. 이전 C# 파일과 원래 caller는 변경하지 않는다.

[정확한 UI delta](v666-direct-creation-recovery-delta.json)와
[검증 기록](VALIDATION_V666_DIRECT_CREATION_RECOVERY.md)을 따른다.

새 본문 소유 ID가 생기면 기존 native의 `OWNERSHIP_CHANGED` 소스 이력 경계를 유지한다
(`packs/edit-workspace/README.md` 31행, `FEATURE_BLUEPRINT_ARCHITECTURE.md` 121행).
생성 전 개인 canvas Undo/Redo는 기존대로 사용한다. 생성 전체를 소스 전용 공유 Undo로
묵시 삭제/재생성하지 않는다. 이후 같은 소유 집합의 별도 본문 편집은 기존 공유 이력을
사용한다. 새 이력 정책을 추가하거나 기존 보호를 미구현으로 재분류하지 않는다.

## 별도 경계

다른 root 정의·혼합 계약·직접 배치의 다른 형태는 원래 요구와 현재 구현을 대조할 점검
후보다. 가능한 조합 전체를 새 필수 항목으로 늘리지 않는다. M11/M12/M4의 완료 범위와
V2 후속·V3–V9·팩/backend·종류 호환성 결정·실기기/전체 UI/Space 잔여를 유지한다.
