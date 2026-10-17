# v480 Home 포함 팩과 저장된 편집 기록

`work/current@943629c`의 Home object 집계와 전용 설정 저장에서 이어진다. v480 원본 ZIP은 변경하지 않는다. 카드의 나머지 두 요약을 실제 빌드 계획과 성공한 소스 저장에 연결한다.

## 포함 팩

확정 ProjectPack의 현재 `entry`와 **선언된 각 타깃**에 기존 `Planner.Plan()`을 적용한다. `Reached`에 속한 선언의 namespace 집합은 `Builder.Build()` 보고서의 `includedPacks`와 같은 정의다. ProjectPack 자체도 도달하면 포함한다. 등록만 한 팩, 단순 dependency, 빌드 도구의 등록만으로는 수를 늘리지 않는다. 컴파일 성공이나 설치 상태를 뜻하지 않는다.

모든 타깃의 개수가 같으면 그 수를 표시한다. 개수가 다르면 `타깃별`로 표시하고 tooltip에 각 타깃의 수와 실제 집합을 제공한다. 임의의 기본 타깃이나 타깃 간 합집합을 선택하지 않는다. entry/타깃이 없는 일반 Pack은 `unsupported`, 파싱·해결·권한·읽기 예산 실패는 `unavailable`이다. 오류를 0으로 표시하지 않는다. object 선언 수는 별도 조회이므로 포함 집합 조회가 실패해도 유지한다.

`SemanticCatalog.Query(action=inclusion)`은 타깃 선언과 도달한 선언의 메타데이터를 읽는다. 구현 본문·도구 바이너리·provider·프로젝트 코드를 실행하지 않는다. `Documents`의 선택적 byte reader로 관측한 원본을 보관하고 조회가 끝날 때 같은 바이트인지 검사한다. 이 경로는 mtime이나 persistent cache를 관측 근거로 쓰지 않으며 프로젝트 폴더에 캐시나 편집 세션을 만들지 않는다. 기존 빌드의 기본 Documents 캐시는 그대로다.

한 조회는 registry 256개(루트 포함), 선언 locator/실제 읽기 16,384개, 타깃 16개, 파일 1MiB·총 32MiB·응답 64KiB로 제한한다. namespace는 256자, 타깃 이름은 64자로 제한한다. 소스 symlink와 관측 중 변경은 거부한다. Home의 기존 32개 카드 제한과 카드별 실패 격리를 유지한다. 조회 시점의 스냅샷이며 파일 변경 구독은 아니다.

## 마지막 편집

이 기록의 편집은 **달라진 초안의 Save 성공 또는 원본 변경의 Confirm 성공**이다. 브라우저의 미적용 입력, 메모리 초안, 열기/조회, 동일 내용 재저장, 검토 닫기/취소, 거부된 CAS·컴파일·저장은 시각을 만들거나 갱신하지 않는다. 저장된 초안을 원래 내용으로 되돌려 Save하는 것도 실제 저장 내용 변경이다. 채팅·Helper 선택·Home 설정·private presentation은 소스 편집 사건이 아니다.

기존 `Save.Write`와 `ChangeSet.ConfirmReviewed`가 쓰려는 파일 목록에 `Save.Activity`가 준비한 receipt의 경로·원래 hash·새 JSON을 추가한다. 같은 `FileStream.Commit`의 소유 경로 검사, lease, CAS와 rollback에 포함한다. 따라서 기록만 성공하거나 기록 실패 뒤 원본만 변경되는 별도 쓰기를 두지 않는다. 성공 후 Accept/Acknowledge에서 문제가 생긴 `confirmed-with-warning`은 원본이 이미 커밋된 실제 Confirm이므로 기록도 유지한다. 경합은 원래 변경·초안을 보존한 채 거부하며 자동으로 새 baseline에 적용하지 않는다.

저장 위치는 프로젝트 root의 `.confectory/project-activity/<SHA256(정규화된 절대 manifest 경로)>.json`이다. 고정 7필드/version 1, 최대 UTF-8 4KiB, 최신 사건 하나만 저장한다. `manifest`, 있으면 기존 durable `projectId`, `kind(save/confirm)`, UTC `at`, 증가하는 `sequence`, 고정 `scope`를 검증한다. 같은 폴더의 다른 manifest나 다른 projectId에 기록을 재할당하지 않는다. 아직 durable ID가 없는 일반 EditWorkspace는 manifest 소유 정체성으로 기록하며, 이후 같은 manifest의 ID가 생기면 다음 사건에 붙인다. 시각은 해당 성공 쓰기를 준비한 호스트의 UTC wall clock이며 sequence로 사건 순서를 구분한다. 시스템 시계가 바뀌었을 때 경과 시간을 추측하지 않는다.

파일이 없으면 `none`/`기록 없음`이다. 예전 편집 시각을 현재 시각·파일 mtime으로 채우지 않는다. 잘못된 자료나 다른 소유자의 receipt는 `unavailable`이고 Save/Confirm에서도 기존 바이트를 자동 덮어쓰지 않는다. receipt 쓰기가 실패하면 해당 Save/Confirm도 실패하고 살아 있는 초안은 유지된다. Home은 `at/kind/sequence`만 공개하고 저장 경로·projectId·예외는 카드에 노출하지 않는다. 새 프로세스와 새 브라우저 context는 이 파일을 다시 읽는다.

## 검증과 남은 경계

새 모델 검사는 실제 빌드 보고서와 포함 집합 일치, 미사용 팩/본문 제외, 도달한 선언 오류, entry 없는 Pack/Project 구분, Save/Confirm·취소·외부 충돌·receipt 읽기 전용/손상 거부·실제 프로세스 재시작을 검사한다. 공통 Chromium 검사는 실제 필드 Apply/Save·검토 취소·compiler Confirm 뒤 Home의 사건 종류·sequence·정확한 timestamp와 새 호스트/브라우저 context 복원을 검사한다. 기존 Home 설정 실패/재시도·손상 보존·41개 object 집계도 같은 흐름에 유지한다. 초기 조회를 실제로 대기시킨 상태에서 pagehide를 일으켜, 닫힌 소유 뷰의 초기화 취소가 미처리 오류로 빠지지 않는지도 검사한다. 최종 실행과 고정 원본은 [검증 JSON](validation/v480-home-inclusion-edit-events.json)에 기록한다.

이 후속의 포함 팩 조회는 desktop authoring host에서 검증한다. Android/browser의 기존 owned metadata adapter는 이 registry 계획 조회를 제공하지 않아 카드에 조회 불가를 유지한다. 관리 프로필 컴파일과 실제 OS·기기 실행을 구분한다. 프로젝트 정보의 팩 요구/유형 편집·Helper/프로필 선택 조합, native 설치·실계정·유료 호출, 계산식 overflow 정책은 이번 요약 범위 밖이다. 새 정책 답변이 필요한 내부 저장/API 질문은 없다. main·원본 ZIP·Android 설정을 보존한다.
