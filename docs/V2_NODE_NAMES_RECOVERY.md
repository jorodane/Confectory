# V2: 기존 일반 동작 여러 개의 표시명 저장 복구

기준은 보관된 v666 `Confectory-v666/dist/blueprint.js` 926–943행의 노드 이름 편집과
1267·1291행의 저장·검토다. 기존 노드 여러 개의 제목을 바꾼 뒤 한 번 Save하는 흐름을
다룬다. 새 편집 UI나 식별자 변경·소스/계약 조합을 추가하지 않는다.

## 실제 재현

게시본 `1055fd0a0c083a00a52cabc71a9df145081d49f7`의 직접 소유 ordinary root에서
기존 code/next 동작 두 개의 제목을 원래 inspector로 입력했다. checkpoint 쓰기를
실패시키면 개인 입력 두 개가 모두 사라지고 live 이름만 바뀌었다. cold 재시작 뒤에는
이전 두 이름이 복원됐다. checkpoint·signature·C#/caller·ID·값·연결·물리 원본은
그대로였다. 생성 fixture의 실제 실행은 `body`, `after`, `10`과 exit 10을 유지했다.
수정 전 화면·traffic·before/after/cold와 실제 실행 결과를 보관한다.

## 닫힌 지원 경계

같은 직접 소유 root의 서로 다른 **기존 일반 code/next 노드들의 표시명만** 기존
원자 후보·checkpoint CAS·ownedRename receipt·공유 이력으로 저장한다. 기존 batch
예산 2–64개 안에서 노드별 입력 하나를 허용하고, 모든 노드 ID가 관측돼야 한다.
표시명은 식별자·함수 계약·C# 지역 이름이 아니다. 서로 같은 표시 문자열을 쓰더라도
정체성은 기존 node ID로 유지한다. 단독 이름 저장과 같은 노드의 2–3개 텍스트 저장은
이미 완료된 지원 범위를 그대로 유지한다.

중복 node ID·누락 노드·call/export·분기/문맥 전달 노드·private/copy/slot·부모/외부·
참조의 기존 보호를 유지한다. 다른 노드의 설명/본문, 인자·실행선·root 계약·생성/삭제를
표시명 묶음에 섞어 허용하지 않는다. 표시명 길이/문자·소유/권한 검증은 기존 규칙을
따른다. 공개/override 입출력 계약·C# bytes·핀·값·연결·profile·설명은 보존한다.

실패하면 모든 이름과 원래 시도를 보존한다. 같은 checkpoint·전체 source closure와
미적용 결과가 확인될 때만 같은 key/node/type의 수정 이름으로 명시 재시도한다.
다른 입력이 더해지면 모두 유지하고 legacy live 저장으로 우회하지 않는다. 응답 유실은
확정 receipt만 회수한다. 응답 보류 중 새 이름은 자신의 캡처 origin·같은 전체 소스
ID/해시를 대조한 뒤 별도로 저장한다. cold의 revision 차이를 다른 원본/누락 origin/
새 편집 권한의 근거로 사용하지 않는다. 소스 편집 권한이나 자동 C# 재작성은 없다.

writer·receipt 형식·공유 이력 planner·원래 레이아웃·Review→Confirm·최종 CAS와 실제
원본 쓰기 시점은 바꾸지 않는다. 최신/롤백 및 소유 임시물 수명 정책도 유지한다.
[정확한 delta](v666-node-names-recovery-delta.json)와
[검증 기록](VALIDATION_V666_NODE_NAMES_RECOVERY.md)을 따른다.

## 고정 잔여

다른 root·혼합 저장·직접 배치는 재현 기반 점검 후보이며 가능한 조합 전체를 새
필수 항목으로 늘리지 않는다. 완료 M11/M12/M4는 다시 열지 않는다. 고정 V2 후속·
V3–V9·팩/backend·종류 호환성 결정과 실제 Windows/모바일·전체 UI·Space 전달은 별도다.
3D/권한 별도 팩·이동 연출과 실행 분리·동기 caller의 명시 async 전환 원칙을 유지한다.
생성 fixture만 사용하며 live AI·계정/키·유료 호출·새 외부 접근을 사용하지 않는다.
