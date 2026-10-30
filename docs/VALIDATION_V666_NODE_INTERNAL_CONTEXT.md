# M11 whole-body 인스턴스 문맥의 내부 흐름

## 원본과 지원 범위

저장소 v666 `dist/blueprint.js`의 `data-function-write-direct` → `openInternal(node,false)` → `api.internal`을 따른다. 기존 직접 소유 next C# 동작의 단일 코드 래핑을 whole-body 멤버에 연결한다. 원문을 분석하여 별도 의미 그래프로 변환하지 않는다. 기존 private 지원 profile을 유지하며 구형 profile을 자동 승격하지 않는다. 공개 override의 입출력 계약 유지와 독립 계약 복제 제외 합의도 유지한다.

기존 whole-body 계약의 `implementationContext`를 실제 소유 구현·namespace-qualified 함수 ID·입출력 signature·scoped import와 대조한다. 원래 `public Invoke`를 같은 생성 구현 클래스에 한 번만 둔다. 내부 leaf와 그 조상은 같은 인스턴스로 연결되며, ref/out은 기존 native 규칙으로 동일 저장소를 명시 전달한다. `this.Invoke` 재귀, `this.calls`와 `IImports`, 원문 파일의 `sourceIdentity`를 바꾸지 않는다. scoped import를 canonical import 매개변수로 바꾸지 않는다. 다른 target 본문은 그대로 둔다.

관측되지 않은 다른 receiver, 변경된 scoped binding, 트리 안의 중복 인스턴스 멤버는 전체 거절한다. derived `contextBoundary`는 래핑 후 Root 계약·alias·노드 이름 보호를 유지한다. 이는 저장 문법이나 새 권한이 아니다. 기존 C# 편집기는 실제 whole-body의 고정 `Invoke` 선언을 표시하며 본문만 편집한다.

부분 본문 편집에서 textarea의 LF 정규화가 편집하지 않은 CRLF verbatim 문자열까지 바꾸던 결함을 수정했다. 정규화된 편집 위치를 원문 위치에 대응하여 바뀐 구간만 적용하고, Undo/Redo도 원문 구간을 복원한다. C# 문자열 치환이나 자동 소스 재작성이 아니다. 사용자가 실제로 바꾼 텍스트는 그대로 컴파일 검증한다.

전환 Save는 기존 `authorBatch` 후보·원문 guard·새 leaf와 최종 CAS를 재사용한다. 취소·컴파일 오류·충돌·응답 유실·cold·늦은 입력 보호를 유지하며 활성 구현은 Review→Confirm에서만 반영한다. 원래 record/C# 파일은 보존한다.

## 검증 자료

`tests/web/v666_node_internal_context_fixture.py`는 실제 `blueprintConversion`이 만든 직접 소유 property profile whole-body를 사용한다. scoped provider는 +3, 잘못 선택할 canonical provider는 +30을 반환한다. 실제 호출 전후의 재귀·동일 ref/out 별칭과 서로 다른 저장소·void·CRLF literal·CallerFilePath/CallerMemberName·IImports 소유 type·별도 Linux target 결과를 비교한다. qualified leaf probe는 컴파일만 하고 실행하지 않는다. 반복 내부 진입도 같은 receiver를 보존해야 한다.

`v666_node_internal_context_api.py`는 위 의미와 문맥 위조/중복 거절, 부분 Review, 컴파일 오류 입력 보존, Review 이후 원문 경합의 최종 CAS, cold와 원래 계약 보호를 확인한다. `v666_node_internal_context_ui.py`는 원본 화면의 미리보기/Undo/Redo·본문 취소/편집·Root Save·실패/재시도·응답 유실·늦은 입력·프로젝트 왕복·Review 취소/Confirm을 검증한다. `v666_script_raw_edits.mjs`는 부분 편집/Undo/Redo와 고정 선언 보호에서 CRLF·혼합 줄바꿈 및 Unicode 원문을 확인한다.

최종 독립 LF/CRLF checkout과 새 Windows 교차 패키지/전체 SHA·모드 복원 검증은 `tools/verify_desktop.py --suite node-internal-context`로 수행한다. 해당 실행의 결과·보관 commit/manifest·공간 실측은 검증 후 아래에 기록한다. 일반 Root/중첩/ref-out 회귀와 native 중첩·whole-body·소유 경계 검증을 함께 수행한다. 이전 단위의 통과를 이번 코드의 신규 통과로 계산하지 않는다.

## 남은 경계

M11 전체 완료는 아니다. private 미지원 기존 profile, 실행 분기/enum, copy·상속·참조 문맥 전환과 독립 슬롯 창/모바일 진입은 이번 지원 완료로 집계하지 않는다. 임의 C#의 stack trace·reflection 등 모든 관측 결과의 완전 동등성을 주장하지 않는다. 본문 자동 재작성이나 새 핀/계약 ID 정책도 추가하지 않는다.

B2 다른 사용자/그룹 권한 backend, 종류 C# 표현과 사용 중 항목 삭제 대응, M4/M12 및 3D/권한 별도 팩은 고정 잔여다. 3D 이동은 표시 연출이며 작업 실행 조건이 아니다. 실제 Windows apphost/WebView2·실제 모바일·전체 UI·Library/Space 전달은 교차 패키지 검증과 구분한다. 미반영 전환 초안을 구버전 롤백 UI로 확정하는 호환성은 별도로 보장하지 않는다.
