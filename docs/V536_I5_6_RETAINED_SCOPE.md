# 고정 6행의 추가 그래프·저장소·후처리 수용 범위

기준은 저장소 `196c605` v536과 고정 6행 C1~C4다. 새 조합이나 새 편집 화면을 추가하지 않는다. 기존 함수 상세창·구현 선택·보호된 C# Script·명시적 입력/출력 매핑을 사용하며, 임시 저장과 Review/Confirm은 분리한다.

| 고정 항목 | 원본 조작과 지원 경계 | 결과 |
|---|---|---|
| C1 추가 callee 노드·locals/별칭 | 직접 소유 함수의 전체 본문을 직접 편집하고 형식/값·ref·out/반환을 선택한다. 독립 노드·경로·ID·정확한 지역값·별칭을 유지하며 제거된 입력의 현재 저장소 및 이전 native 출력의 호환 출력에 명시 대응한다. 현재 공개 출력 writer도 같은 후보에서 선택한다. | 기존 단일 lift로 그래프를 재구성하지 않고 전체 그래프를 보존하는 후보에 연결했다. |
| C2 전체 본문 caller/import | caller 자신의 ABI·셀·노드는 유지하고 project-owned import의 현재 계약과 수동 호출 본문을 검증한다. | 이전 `8a1e122` 단위의 지원·회귀를 유지했다. |
| C3 별도 `forwardCallerStorage` | 코드는 자신의 현재 매개변수·본문·출력을 명시한다. call은 실제 callee ABI/원문을 유지하고 대응하는 root 셀 이름만 바꾼다. | 코드·call의 실제 저장소를 유지하며 같은 후보에 연결했다. 외부 callee 타입·역할을 자동 수정하지 않는다. |
| C4 postCall | 기존 serial After 또는 execution-enum의 후속 source·helpers를 직접 편집한다. 원래 wrapper/graph 증거와 현재 호출/공개 출력 계약을 결부하고 실행 enum/ports는 보존한다. | callee·import·caller의 입력/출력 대응·수동 후처리를 한 후보/CAS·Review 그룹에 연결했다. |

C1·C3의 원래 native/public 타입·역할·순서와 positional 저장소를 먼저 확인한다. 내부 검증을 마친 노드 ID만 root 준비기에 전달하며 공개 root 준비 operation은 임의 whitelist를 받지 않는다. 추가 코드의 C# 원문은 바꾸지 않는다. 별칭은 같은 정확한 타입의 현재 저장소만 선택하며 literal·새 임시 셀·값 스냅샷으로 치환하지 않는다. node 출력 소비자는 정확히 호환되는 현재 출력에 직접 대응한다. 호환 대응이 없으면 원래 연결/입력을 보존한 채 중단한다.

공개는 호출 뒤 `SourceContext`로 읽는 출력이라는 기존 의미다. 프로젝트 접근·외부 공유나 실행 권한이 아니다. C4의 source/helpers는 현재 인터페이스와 실제 생성 entry/members로 컴파일 검사한다. 바뀐 계약에 이전 확인을 자동 재사용하지 않는다. 기존 enum 결과와 native 데이터 반환 저장소는 별개이며 typed return mapping을 사용한다. copy provenance/등록 callable의 별도 receipt는 허용하지 않는다.

이 문서의 종료 조건은 위 직접 소유·일반 그래프/실제 셀·기존 serial/enum 후처리 경로의 정상/취소·Undo·저장 실패·충돌·응답 유실·재시작·명시적 Review/Confirm, 기본/독립 창·프로젝트 문맥, 기존 두 호출 회귀, clean checkout·교차 패키지다. 원래 직렬 출력 정의 삽입/삭제 규칙을 유지하며 분기별 새 출력 삽입·모호한 alias·C# 자동 재작성은 추측하지 않는다.

고정 6행의 위 직접 소유 수용 경계를 닫은 뒤 다음은 5행의 `BlueprintTree` private path·중첩 노드/record와 명시 ABI를 결합하는 작업이다. copy/등록 receipt는 7행, 외부 callee와 caller 등 둘 이상의 함수 계약을 한 번에 바꾸는 작업은 8행, 고급 타입/표시명은 9행이다. 외부 callee 타입·역할을 바꾸면서 caller의 forwarded public 저장소도 동시에 바꾸는 조작은 이 8행에 속하며 현재 전체 거절한다. 이것을 C3의 조용한 변환으로 처리하지 않는다. 실제 Windows/모바일·Library 전달과 전체 v536 완료 여부는 별도다.
