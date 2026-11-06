# V2: void root 값 입력 이름 저장 복구

기준은 보관된 v666 `Confectory-v666/dist/blueprint.js` 1196행 `offerIdentifier`와
기존 native `rootParameters`/`blueprintRootContract`의 명시 remap이다. 입력 이름 편집은
반환값이 없는 함수에도 노출된다. 반환 형태를 바꾸는 기능이 아니라 같은 이름 변경의
저장 실패 복구에서 빠진 void 경계를 연결한다.

## 실제 재현

게시본 `da5e0eee3260f268f28df628d35b2e666872ca1a`에서 두 int 값 입력을 가진 직접
소유 동기 void 함수의 `scale`을 `multiplier`로 바꾸었다. 쓰기 실패 뒤 개인 계획 하나가
사라지고 live 이름만 바뀌었으며 cold에서는 원래 이름이 복원됐다. checkpoint·출력 없음·
반환 타입·물리 원본·C#/caller bytes는 같았다. 원래 `Pair.Invoke(7,3)` 호출은
`body`, `10`, `done` 출력과 exit 0을 유지했다. 생성 fixture의 실행·화면·traffic·
before/after/cold를 보관한다.

## 닫힌 지원 경계

직접 소유한 동기 ordinary root의 기존 1–64개 **값 입력 중 이름 하나만** 명시 remap으로
바꾸거나 같은 이름을 다시 저장한다. 기존 nonvoid 지원을 유지하며 void도 같은 원자
후보·checkpoint CAS·ownedRootInputName receipt·함수/구현/graph 묶음과 공유 이력으로
연결한다. 모든 입력의 타입·mode·순서·개수와 나머지 이름, 원래 반환 타입을 보존한다.
void는 출력 순서가 빈 배열이어야 하고, 기존 nonvoid는 원래 return 핀 하나를 그대로
유지해야 한다. 반환값/출력 생성·삭제나 함수의 void/nonvoid 변환을 허용하지 않는다.

두 이름 동시 변경·중복 이름·타입/위치/개수 변경·ref/out 전환·새 public 출력·본문/실행선/
다른 private 입력 혼합을 이 경로에 포함하지 않는다. private/copy/slot·공유 함수·부모/
외부/참조·async·공개 실행 분기·native 문맥의 기존 보호와 override 입출력 계약을
유지한다. 기존 이름/명시 대응 검증과 Review→Confirm·최종 CAS를 그대로 사용한다.

실패 후에는 같은 checkpoint·전체 source closure와 미적용 결과가 확인될 때만 같은
key/종류의 새 이름으로 명시 재시도한다. Undo 취소·Redo·수정·cold에서도 입력과 원래
시도를 보존한다. 무관한 입력이 추가되면 모두 유지하며 legacy live 저장으로 우회하지
않는다. 응답 유실은 확정 receipt만 회수한다. 늦은 이름은 정확한 자기 원본에서 같은
입력 위치를 명시 대응하며 다른 작성자의 이름에 대응을 합성하지 않는다.

원래 C#·위치 기반 IInvoke 계약·caller·node ID·핀·값·실행선·profile을 보존한다.
사용자가 명시한 root 식별자와 그 참조만 기존 metadata로 갱신한다. 자동 C# 재작성이나
새 소스/외부 접근 권한은 없다. writer·receipt 형식·그룹/이력 planner·원본 레이아웃·
원본 저장 시점·최신/롤백/임시물 수명 정책을 바꾸지 않는다.

[정확한 delta](v666-root-void-name-recovery-delta.json)와
[검증 기록](VALIDATION_V666_ROOT_VOID_NAME_RECOVERY.md)을 따른다.

## 고정 잔여

다른 root·혼합 저장·직접 배치는 재현 기반 점검 후보이며 가능한 반환/인자 조합마다
새 필수 항목을 만들지 않는다. 완료 M11/M12/M4는 다시 열지 않는다. 고정 V2 후속·
V3–V9·팩/backend·종류 호환성 결정과 실제 Windows/모바일·전체 UI·Space 전달은 별도다.
3D/권한 별도 팩·이동 연출/실행 분리·동기 caller의 명시 async 전환 원칙을 유지한다.
생성 fixture만 사용하며 live AI·계정/키·유료 호출·새 외부 접근을 사용하지 않는다.
