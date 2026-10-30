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

- 실행 코드·검사 commit은 `6174389ca1a8cc300f40cae80a23d439a029fe85`이다. 최종 보고 커밋은 문서만 바꾸며 실행 코드 동등성을 별도 확인한다.
- 최종 실행 `/workspace/artifacts/v536-verification-managed/runs/6668afd9437f4ebfb2370585da88c645.json`의 **48단계 전부 통과**: LF 22, CRLF 18, 새 교차 패키지/전체 ZIP 복원/실패 수명관리 8. 독립 Git 객체·캐시·의존 저장소로 두 checkout을 새로 만들었다.
- 양쪽에서 Root 일반 반환/void API와 원본 화면, 중첩 API/화면, private/copy 아이콘 회귀를 새로 실행했다. native 중첩/변환 13개와 상속 소유권 2개도 **각 checkout에서 모두 통과했고 skip은 0**이다. LF는 깊이 2·7·8과 normal/storage/conflict/project, CRLF는 깊이 2와 loss/late를 실행했다.
- 새 패키지 및 전체 파일 SHA/모드 manifest로 압축을 복원한 패키지에서 Root/중첩 UI를 실제 managed 엔진으로 다시 실행했다. 복원본의 storage/loss 및 패키지 실패 수명관리도 새 검사다. 이전 패키지의 결과로 대체하지 않았다.
- 기존 `node-internal` 107단계 suite는 그대로 남겼다. 이번에는 영향 범위를 고른 `node-internal-nested` suite를 추가했다. 종류·작업자 배지·기타 무변경 기능의 이전 107단계 결과는 앞선 Root commit에 대한 재사용 근거이며, 최종 코드에서 107개 전체를 다시 실행했다고 집계하지 않는다. 집중 검사는 최종 production 파일 해시 일치를 확인해 보존했다.
- 최종 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/6668afd9437f4ebfb2370585da88c645.zip`, SHA-256 `62e548df6be0c9e9fbb031f301c5dd383d6dd1f4ca779c4b666a407d5c73eb53`. 집중 증거 ZIP SHA-256은 `d0a8e4e8682cb7461b2c66303d23ea5d53d7cb60cb055cba5b271bbf56750713`이다. 초기 빌드 진단 실패도 보존하며 정상 통과로 바꾸지 않았다.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | 크기 | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `6174389ca1a8cc300f40cae80a23d439a029fe85` | `e3ed67225865cf735b0f4cb0477feb6ad02b9615e16cde40d7c1f9357dedb137` | 51,243,792 bytes | `96c012aac675bb97f33933eb979b8970ddab034b9a0c0e3842e553bf832bdc9a` |
| 정상 롤백 | `8269dd7270a2cd5754fd6d0131322f717077b4da` | `6d5dc695a9f2982849e5a37ca75aeebec5e4c2baf48d31e12d149b74796d5766` | 51,242,377 bytes | `dff8ef0f926d79db5201cd7e2915bc72c8d63c98eab71d96a9d1ab067020ee27` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신/롤백 ZIP 모두 SHA를 재확인했고 각 manifest는 2510개 항목(2363 파일/147 디렉터리)을 기록한다. 최신은 새로 전체 복원/실행했고 롤백은 직전 107단계 검증본을 유지했다. 롤백 UI로 미반영 중첩 전환 초안을 편집/확정하는 호환성은 검증하지 않았으며 현재 검증본을 사용한다.

최종 관리 실행의 디스크 여유는 시작 2105.93 MiB → 정리 후 2100.43 MiB로, 순증가 **5.50 MiB**다. 실행 중 단계 샘플의 최소 여유는 2105.88 MiB, cgroup 메모리 피크는 4604.56 MiB였다. 이 수치는 해당 실행의 실측이며 이후 증가량 보장은 아니다. 집중/최종 실행의 소유 RAM root는 증거 보존 후 제거했고 최신/롤백과 로그·스크린샷·합성 입력·재생성 출력 manifest는 지속 공간에 남겼다. 기존 비관리 산출물·원본·사용자 데이터는 정리하지 않았다.

## 중첩 단위 종료 당시 경계

후속 [일반 ref/out 저장소 지원](VALIDATION_V666_NODE_INTERNAL_STORAGE.md)은 별도 단위에서 마감했다. 아래는 이 중첩 최초 검증 시점의 경계이며 현재 지원은 [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md)를 따른다.

이번 완료 대상은 저장된 직접 소유 Root/private graph의 일반 next C# 진입이다. whole-body `implementationContext`/this/import, ref/out 저장소, 분기/실행 enum, copy/상속/참조 전환은 별도 M11 경계이며 모든 가능한 조합을 새 필수 작업으로 늘리지 않는다. 공개 override 원계약 보호와 독립 계약 복제 미채택은 유지한다. 구형 profile 자동 승격이나 임의 본문의 관측 가능한 모든 C# 의미의 동등성을 주장하지 않는다.

독립 슬롯 창의 새 전환·M11 모바일 viewport 진입·실제 Windows apphost/WebView2·실제 모바일 기기·전체 UI·Library/Space 전달은 이번 단위의 검증 완료 대상이 아니다. B2 다른 사용자/그룹 권한 backend, 종류 C# 실행 표현/사용 중 삭제 대응, M4/M12와 3D·권한 별도 팩은 고정된 별도 잔여다. 3D 이동은 표시 연출이고 실행 조건이 아니다.
