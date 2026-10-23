# v536 호출 ABI 갱신 범위

최신 실제 결과는 `VALIDATION_V536_GENERAL_ABI.md`다. 공개 출력은 호출 뒤 SourceContext 읽기이며 외부 공유/프로젝트 접근 권한이 아니다. 원래 계약 갱신 진입점에서 명시적으로만 시작하고 callee 원본은 자동 수정하지 않는다.

| 문맥 | 현재 연결 범위 / 제한 |
| --- | --- |
| 소유 일반 Blueprint root/객체 소유 슬롯 | 기존 단일 callee 값↔ref에 더해 명시적 이름·순서·타입·새 입력 값·출력/return 대응을 연결했다. 기존 native binding/alias/scope와 owner hash/provide를 재검사하고 전체 typed 소비자/record를 검사한다. |
| 저장된 직접 배치 복사본 | 독점 owner·요구/제공·불변 출처의 단일 Blueprint target에서 같은 general mapping을 한 `rebindCopyAbi` 후보/CAS로 검사한다. 직접/등록 callee 기존 지원 경계를 유지하며 donor를 다시 복사하거나 쓰지 않는다. 실제 general fixture는 소유/직접 등록 callee 각각4 PASS이며 두 경우 모두 donor/외부 원본을 보존했다. |
| 새 비공개 복사 초안 | immutable seed의 원래 graph/본문과 현재 소유/직접 등록 callee receipt를 분리한다. 단일 context 없는 Blueprint target에서 명시 general mapping을 전체 새-copy 후보/CAS에 결부했다. 실제 owned/registered 각각 UI5 PASS. |
| 직접 등록 callable | 함수/manifest receipt·bodyReads=0을 유지한다. 단일 소유 caller target의 명시 mapping과 typed import/graph/소비자를 바꾸며 외부 팩은 쓰기 대상이 아니다. 전이 의존성/자동 provider 선택/all-target receipt는 미지원. |
| 여러 target | owned ordinary root의 모든 Blueprint target·code record·공유 import를 한 후보/CAS/필수 Review 그룹에서 갱신한다. target별 명시 mapping을 확인한다. 실제 common/windows2target 검증,8target 전수 아님. opaque/상속/copy/whole-body context/등록 all-target은 미지원. |
| 이름·순서·타입/out/반환 변경 | 명시된 기존 핀 또는 새 비-ref primitive literal과 출력 대응으로만 처리한다. 사용 중인 입력 제거·소비자 있는 출력 제거·duplicate/unknown/unmapped/incompatible binding은 전체 거절한다. 기존 정밀도/타입 규칙만 따르고 임의 cast/C# 본문 재작성은 하지 않는다. |
| 같은 callee의 여러 호출·nested·외부 소유/whole-body C# | 여전히 미지원. source closure/공유 import/record와 소유 문맥을 함께 표현하기 전에는 연결이나 원본을 조용히 바꾸지 않는다. |

모든 ABI Save는 임시 초안이며 최종 source는 기존 명시적 compiler Confirm으로만 반영한다. 실패/취소/cold/응답 유실과 이전 값/ref·소유권 보호는 유지한다. 기존 schema 편집/별도 Save 결합과 모바일 최종 수용은 다음 범위다.
