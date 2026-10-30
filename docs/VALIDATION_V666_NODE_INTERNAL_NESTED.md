# M11 직접 소유 중첩 C# 동작의 내부 흐름

기준은 저장소 v666 ZIP의 기존 개별 동작 ‘직접 작성’/내부 흐름 진입이다. [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md)의 Root 지원을 직접 소유한 private graph까지 연결한다. 새 버튼·레이아웃·공개 계약·자동 C# 의미 변환은 추가하지 않는다.

## 구현 범위와 발견 결함

- 선택한 전체 frame과 qualified source ID, 정의/본문 해시를 함께 확인한다. 같은 local ID가 형제 frame에 있어도 저장 대상을 추정하지 않는다. 중첩 Save는 명시 binding이 필수이며 기존 Root 요청의 호환 경계는 유지한다.
- 코드 노드 하나와 반환 내보내기를 준비하고 기존 ID·핀·인자·실행선·활성 물리 구현을 유지한다. Root와 선택 frame의 profile이 다른 경우 새 child가 Root profile을 잘못 물려받던 부분을 선택 frame 기준으로 수정했다. CRLF 본문과 helper는 그대로 보존한다.
- 창별 입력은 전체 private 경로로 분리한다. 모든 정확한 조상/Root 왕복과 그 위치에서 Save, 전환 Undo/Redo, 대화상자 취소·cold를 같은 후보에 연결한다. 미리보기에서 다른 조상 코드나 구조를 함께 편집하지 않는다.
- Save는 기존 author 후보/체크포인트 CAS를 사용한다. 원문 guard·물리 Root·새 leaf·기존 계약은 같은 원자 그룹이며 부분 Review를 거절한다. 최종 파일 CAS 뒤에만 Confirm한다. 원문 물리 파일은 Confirm 뒤에도 바이트 그대로 남는다.
- 새로운 깊이 한도는 없다. 기존 엔진의 깊이·전체 노드·qualified 경로 예산을 그대로 적용하며 초과는 전체 미적용한다.

## 집중 검사

관리 실행 기록은 `/workspace/artifacts/v536-verification-managed/runs/d794162b358c4445951e224f2b58714e.json`이다. 혼합 profile, 중첩 부모와 동일 local ID 형제, helper가 있는 합성 프로젝트를 사용한다. API는 깊이 2·7에서 전환/Confirm 후 실제 CLR 결과를 확인하고 깊이 8에서 기존 최대 예산을 넘는 래핑을 거절한다. 최대 예산 검사는 임의 UI 깊이 정책이 아니다.

실제 브라우저는 원본 버튼·코드 취소/편집·전체 조상 왕복·Undo/Redo·Root Save·Review 취소/Confirm·cold를 검사한다. checkpoint 쓰기 실패, 원문 경합, 저장/조회 응답 유실과 receipt 복구, 늦은 입력의 다음 Save, 동일 namespace/ID의 다른 실제 프로젝트 왕복을 별도 실행한다. 초기 nullable 빌드 진단 로그도 보존하며 실패를 통과로 집계하지 않는다.

## 최종 독립 검사와 보관

최종 실행 결과·source commit·전체 manifest·최신/롤백 패키지 및 공간 실측은 검증을 마친 뒤 이 절에 기록한다. 기존 `node-internal` 107단계 suite는 변경하지 않으며 중첩 확장의 영향 검사는 별도 `node-internal-nested` suite로 선택한다. 이전 통과 결과와 새 실행을 구분한다.

## 남은 경계

이번 완료 대상은 저장된 직접 소유 Root/private graph의 일반 next C# 진입이다. whole-body `implementationContext`/this/import, ref/out 저장소, 분기/실행 enum, copy/상속/참조 전환은 별도 M11 경계이며 모든 가능한 조합을 새 필수 작업으로 늘리지 않는다. 공개 override 원계약 보호와 독립 계약 복제 미채택은 유지한다. 구형 profile 자동 승격이나 임의 본문의 관측 가능한 모든 C# 의미의 동등성을 주장하지 않는다.

독립 슬롯 창의 새 전환·M11 모바일 viewport 진입·실제 Windows apphost/WebView2·실제 모바일 기기·전체 UI·Library/Space 전달은 이번 단위의 검증 완료 대상이 아니다. B2 다른 사용자/그룹 권한 backend, 종류 C# 실행 표현/사용 중 삭제 대응, M4/M12와 3D·권한 별도 팩은 고정된 별도 잔여다. 3D 이동은 표시 연출이고 실행 조건이 아니다.
