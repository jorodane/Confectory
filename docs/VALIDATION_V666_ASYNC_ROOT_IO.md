# v666 첫 Confirm 전 공개 IO 결합 최종 검증

최종 동결 `28b15b95609ea1b58d58503e7866ce828f9688d5`를 기준으로 한다. 이후 게시 마감은 문서만 바꾸며
runtime/source/tests/tools 동일성을 확인한다. [정확한 지원과 보호](M4_ASYNC_ROOT_IO.md)를 따른다.

## 신규 검사

독립 LF 21·CRLF 20·새 Windows 교차 패키지/전체 ZIP 복원/실패 수명관리
9, **총 50단계 통과**. 신규 50·재사용 0다.
양쪽 Core AsyncBlueprint/AsyncContext/BlueprintConversion 18개 검사도 새로 실행했다.
빌드/캐시·NuGet/home·Git 객체를 분리하고 LF/CRLF checkout을 확인했다.

- 새 직접 소유 전역 함수의 공개 입력/출력·값/연결·명시 C#·Task를 같은 첫 후보와
  checkpoint CAS로 저장했다. 같은 후보의 새 직렬 동작도 공개 입력을 실제로 읽는다.
- 첫 Save 뒤 Confirm 전 입력 이름을 명시 대응으로 바꿔도 지역 동작의 C#·매개변수는
  그대로이고 root 입력 연결만 바뀐다. 전체 Confirm 후 실제 async Blueprint 호출에서
  입력 3·out 출력 3·반환 11과 순서 `before:3 → fresh → reply:3`을 확인했다.
- 실제 신규 등록만 허용하고 기존 baseline/원문·다른 owner·경로 별칭·등록 누락·
  중복/뒤바뀐 그룹·copy 위조를 거절했다. ref async·중복 계약·없는 remap도 전체 거절했다.
- 원본 입력/출력 추가·이름·기존 값 팝오버의 상수와 입력 연결·실행 연결, Undo/Redo·
  코드 취소·미저장 선언 및 checkpoint 없는 cold를 UI에서 확인했다.
- 저장 실패·등록 충돌·응답 유실·생성 중/저장 중 늦은 C# 입력과 cold·반복 저장을
  확인했다. 부분 Review·Review 취소·최종 CAS·Confirm·확정 cold도 포함했다.
- Review 뒤 새 함수 목적지 파일과 manifest 충돌은 checkpoint/원문/입력과 충돌 자료를
  보존하며 전체 미확정했다. 명시 재시도만 확정한다. 기존 전역/정보/private 생성과
  동기 호출자 오류/명시 전환·receipt 변조 거절의 관련 회귀를 확인했다.

## 개발 중 실제 발견과 fixture 구분

새 root 계약을 기존 Confirm 원본처럼 막던 경계를 정확한 신규 등록 증명으로 연결했다.
새 함수가 Confirm 전에 IO를 다시 편집하면 이전 Task 생성 시점 서명을 영구 원본으로
고정하지 않고 검증된 현재 생성 그룹의 선언을 사용한다. 기존 원본·override·공유
계약에는 이 예외를 적용하지 않는다. 생성·명시 해제·공개 계획·지역 계획·원문·Task의
순서를 유지해 중간 source receipt나 새 노드 membership을 무효화하지 않는다.

실제 UI 결함은 아직 graph가 없는 미리보기의 값 선택기에서 `adaptiveOutput`이
없는 노드 배열을 조회하던 예외다. 미리보기/생성 출력은 기존 출력 타입 적응 대상으로
조회하지 않도록 했다. 원래 값 선택 팝오버와 배치는 유지했다.

테스트의 native async caller는 기존 `ASYNC_PROVIDER` 보호로 거절됐다. 보호를 풀지 않고
실행용 복사본의 호출자를 명시 Blueprint async로 작성했다. 테스트 caller의 빠진
반환 종료선도 고쳤다. 지도와 겹친 카드 클릭은 원래 카메라 이동 조작으로 해결했다.
강제 클릭·DOM 상태로 값을 주입하거나 원본 레이아웃을 바꾸지 않았다.
개발 검사의 성공/실패와 runner 경로 오류는 최종 통과와 구분해 보존했다.
개발 record `/workspace/artifacts/v536-verification-managed/runs/9a4716e70ef84ad4ae88109759a42666.json`와 ZIP SHA256
`73345bd48cb5ef2f0e73ba886cdd015f9ceb9d504c4b23b393c9025f71f10037`를 따른다.

## 지속 보관·공간

최종 record: `/workspace/artifacts/v536-verification-managed/runs/6c57d964c8804e7fbc6d908272fae1b7.json`

증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/6c57d964c8804e7fbc6d908272fae1b7.zip`

SHA256 `2ac8dd6f925e5c6d7da7d53747566b37034812d5ef927271c8e7a024e8c11c61` (5.75MiB).
최신/롤백은 `/workspace/artifacts/v536-verification-managed/packages/index.json`에 있다.

- latest: 출처 `28b15b95609ea1b58d58503e7866ce828f9688d5`, `41f019be0cb2f42d2067092db7386ed4a6f730a268c0203a8f5e37445516cb8c.zip`, 49.12MiB; 파일 2381·디렉터리 147, 전체 manifest `ed93e8cb3e3d342e287d5e1224b45914992b2f4541d5bcfd842c46b4d0d10dff`.

- rollback: 출처 `2e58f5929f5887a9d78a02f9b4636614f2da2ae6`, `376b87627e6831f540322c986d76728fbb2323c3dd86428624f22ea256b1fc27.zip`, 49.12MiB; 파일 2381·디렉터리 147, 전체 manifest `aaacaba688846d0f1199ab5b040627690b2d445f5b3faa0d836f553686bee541`.

새 생성본과 전체 추출본에서 엔진/UI·저장·실행을 신규 검사했다. 보관 시 두 ZIP의
CRC·전체 파일 SHA·모드를 재확인했다. 롤백의 예전 UI/기기 실행을 신규로 세지 않는다.
자식 종료·증거 무결성·원자 승격 확인 뒤 해당 실행의 소유 임시물만 정리했다.
승인된 managed latest/rollback 승격·보관 수명 외에 과거 패키지·SDK·원본·로그·
프로필·사용자 데이터의 추가 삭제는 없다.

검사 단계에서 표본 측정한 최소 여유 1675.19MiB, 기록된 최대 cgroup 메모리
4593.50MiB. 최종 실행 순증가 7.18MiB, 개발/실패 증거와
코드·문서를 포함한 검증 정리 시점의 이번 단위 순증가 11.75MiB.
측정 여유 1668.11MiB. 3–6MiB를 고정 보장값으로 사용하지 않는다.

## 실제 잔여·미실행

완료/결과 분기선에 생성한 새 동작의 첫 Task 결합은 다음 단위로 남겼다. 기존 정보
owner/이미 있는 원본/복수 target의 계약은 공동 갱신 경계를 유지하며 이 새 전역 생성
검사로 그 문맥 전체의 추가 편집을 완료했다고 주장하지 않는다. ref·비소유 쓰기·
override 공개 계약 변경·legacy 자동 변환을 새 필수 조합으로 늘리지 않는다.

신규 UI는 기본 Blueprint 창에서 검사했다. 이 결합의 독립 정보 창/다른 실제 프로젝트
왕복은 새로 검사하지 않았다. M11/M12는 구체적 회귀가 없는 한 닫힌 상태를 유지한다.
V2–V9·팩/backend·종류 C# 표현/사용 중 삭제 대응 및 실제 Windows apphost/WebView2·모바일·전체 UI·Space
전달은 별도 잔여다.
컨테이너 Chromium UI·실제 .NET Task 실행·교차 패키지와 실제 기기 검증을 구별한다.
live AI 자격증명/유료 호출·외부 접근 grant는 사용하지 않았다.
