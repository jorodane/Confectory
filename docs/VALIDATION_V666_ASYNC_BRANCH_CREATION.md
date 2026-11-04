# v666 분기선 첫 Task 결합 최종 검증

동결 `5f223d2db3b0cf62f6917d5113aaf40c5719b136`를 기준으로 한다. 이후 게시 마감은 문서만 변경하고
runtime/source/tests/tools의 동일성을 확인한다. [지원·원본 근거](M4_ASYNC_BRANCH_CREATION.md)를 따른다.

## 실제 연결과 검증

누락은 기존 async 첫 저장 거래가 `route:completion`·`route:case:` 개인 입력을
허용하지 않던 UI 경계였다. 두 종류를 기존 명시 거래에 포함했다. backend·권한·
실행 계약/코드 생성·원본 화면 배치는 변경하지 않았다. 자산 manifest는 해당 JS의
canonical 크기/SHA만 갱신하고 다른 자산 항목 동일성을 확인했다.

독립 LF 20·CRLF 18·새 교차 패키지/전체 ZIP 복원/실패 수명관리
9, **총 47단계 통과**다. 신규 47·재사용 0다.
양쪽에서 Core AsyncContext/AsyncBlueprint/BlueprintConversion 18개 검사도 새로 실행했다.
LF/CRLF·Git 객체·빌드/캐시·NuGet/home을 분리했다.

- 완료선·결과선의 새 직접 소유 동작, 출력 값 입력·연결·명시 C#·Task를 한 격리
  후보/checkpoint CAS로 저장했다. 분기 ID·소유 영역·기존 목적지는 유지했다.
- 첫 Save·동일 receipt 재조회·cold·부분 Review 거절, Review 뒤 manifest/원문
  충돌과 명시 재시도를 확인했다. 실패하면 기존 원본/checkpoint/입력과 충돌 자료를 보존했다.
- 실제 실행에서 `callee:1 → work:10 → completed:10 → after:10`(완료선),
  `callee:1 → completed:10 → work:10 → after:10`(결과선), out/최종 반환 10을 확인했다.
  실행용 복사본의 다른 결과 선택에서는 완료선 Task만 실행되며 선택되지 않은 결과선
  Task는 실행되지 않는다. 기존 caller·계약·C#은 원본에서 수정하지 않았다.
- 없는 분기·다른 실행 영역·소유자 위조·없는 Task/ref와 중복 Task·무관한 구조 입력을
  전체 거절했다. 자동 기본 분기 선택·호출자 자동 전환·동기 대기를 추가하지 않았다.
- 원래 화면의 분기선 선택·동작 생성·명시 목적지 연결·Task 메뉴·전환 Undo/Redo·
  코드 취소·저장 전 cold·반복 Save·Review 취소/Confirm·확정 cold를 검사했다.
- 저장 실패·등록 충돌·응답 유실·저장 중 늦은 C# 입력의 보존/재조회/별도 저장을
  검사했다. 기존 첫 Confirm 전 공개 Root IO의 API/UI와 최종 읽기 CAS도 회귀 검사했다.

## 개발 실패와 제품 변경의 구분

개발 첫 충돌 검사는 Review 전 checkpoint와 비교하는 fixture 오류였다. 실제 Confirm은
거절되고 원본/새 목적지가 보존되어 있었다. Review 직후 checkpoint 기준으로 수정해
다시 검증했다. 초기 UI fixture의 `body` 대신 실제 `choose` 선택, 수동 연결을
독립 Undo 항목으로 가정하던 기대, Confirm 뒤 사라진 초안 목록에서 경로를 다시
찾던 오류도 fixture에서 수정했다. 기존 Task Undo/Redo와 저장 전 확인한 파일 경로를
사용한다. 그 오류를 제품 결함 해결로 세지 않으며 실패/스크린샷/로그를 함께 보존했다.
개발 도우미의 조기 재진입은 기존 workspace 소유 프로세스가 살아 있어 실행 전 거절됐다.
중복 빌드나 권한 우회는 없었다. 제품 변경은 위 두 분기 입력과 자산 무결성 갱신뿐이다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/dd8e30a78f564a2391074e98551398bf.json`

개발 증거 ZIP SHA256 `f542e109a954ef5ef4cb3e9215750c823ae5dc12c87d33527d43f2db80453cad`.

## 지속 보관·공간

최종 record `/workspace/artifacts/v536-verification-managed/runs/fc6d1621531d43628fb38ded48d56b57.json`

증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/fc6d1621531d43628fb38ded48d56b57.zip`

SHA256 `abfbcb9d6a5efc38b6284ad96e6f51a93d80cc7f54472bcafd99b39c4b54d269` (4.50MiB).

최신/롤백은 `/workspace/artifacts/v536-verification-managed/packages/index.json`에 있다.

- latest: 출처 `5f223d2db3b0cf62f6917d5113aaf40c5719b136`, `7f336f37322a22067ee0969a2dc302aa0499c9e69e65364d39676f138975e245.zip`, 49.13MiB; 파일 2381·디렉터리 147, 전체 manifest `83af149a127ace824427bb7fa9ced1bf5f84f55cd0fc693054f313a809329208`.

- rollback: 출처 `28b15b95609ea1b58d58503e7866ce828f9688d5`, `41f019be0cb2f42d2067092db7386ed4a6f730a268c0203a8f5e37445516cb8c.zip`, 49.12MiB; 파일 2381·디렉터리 147, 전체 manifest `ed93e8cb3e3d342e287d5e1224b45914992b2f4541d5bcfd842c46b4d0d10dff`.

새 패키지와 전체 추출본에서 실제 엔진/UI·저장·실행을 새로 검사했다. ZIP CRC·전체
파일 SHA·모드를 확인하고 증거를 지속 보관한 뒤 소유 임시 작업공간만 정리했다.
최신/롤백 원자 승격·기존 승인 수명주기를 유지했다. 과거 자료·SDK·원본·사용자 데이터·
로그/프로필을 새로 정리하는 권한으로 확대하지 않았다.

단계 표본 최소 디스크 여유 1666.20MiB, 최대 cgroup 메모리
4671.03MiB. 최종 실행 순증가 5.75MiB, 개발/실패
증거와 코드·문서를 포함한 검증 정리 시점의 이번 단위 순증가
7.49MiB. 측정 여유 1660.53MiB.
3–6MiB를 고정 보장하지 않는다.

## 유한한 잔여와 검증 한계

첫 생성 저장에서 남겼던 공개 Root IO와 완료/결과 분기선 새 동작의 Task 결합을
연결했다. 정상 비소유 원본 쓰기·override IO 변경·ref async·선택적 legacy 자동 변환을
새 미구현으로 늘리지 않는다. M11/M12는 구체적 회귀가 없으면 닫힌 상태를 유지한다.
기존 V2–V9·별도 3D/권한 팩/backend·종류 C# 표현/사용 중 삭제 대응과 실제 기기·
전체 UI·Space 전달의 고정 잔여는 별도다. 3D 이동은 실행 선행 조건이 아니다.

이번 UI는 기본 Blueprint 창에서 검사했다. 독립 정보 창/다른 실제 프로젝트 왕복은
이 단위에서 새로 검사하지 않았다. 컨테이너 Chromium UI·실제 .NET Task 실행·Windows
교차 패키지를 실제 Windows apphost/WebView2·모바일 실행으로 계산하지 않는다.
live AI 자격증명·유료 호출·외부 접근 grant는 사용하지 않았다.
