# v666 C# 편집 안내 최종 검증

동결 `7855881f17207f711673811dd9a29961c3fe3a76`를 기준으로 한다. 이후 마감 commit은 문서만 바꾸고
제품·검사·도구와 검증에 사용한 문구 목록 JSON의 동일성을 확인한다.
[범위·원본 근거](V2_CODE_EDITOR_GUIDANCE.md)와 [14개 문구/16개 표시 지점](v666-code-editor-copy.json)을 따른다.

## 변경과 신규 검사

고정 선언 보호·enum 형식·일반/전체 본문/래퍼 C# 안내의 지정 문자열을 v666의
“주십시오/습니다” 문체로 맞췄다. native의 1~32개 enum 제한·값/ref/out·원문 보존과
실제 컴파일/최종 반영 절차는 유지한다. 프로토타입의 컴파일러 미연결 문구는 채택하지 않았다.

줄바꿈을 LF로 정규화한 전체 JS에 허용 목록을 적용한 결과가 실제 source와 정확히
같고 자산 canonical byte 크기/SHA가 일치하는지 확인했다. JS 실행 로직·HTML
구조/선택자·backend/권한/계약은 바뀌지 않았다. WebBundle의 해당 JS canonical 크기/
SHA 이외 다른 자산 metadata도 그대로다. backend 원문 진단을 전역 치환하지 않았다.

독립 LF 12·CRLF 12·새 교차 패키지/전체 복원/실패 수명관리
7, **총 31단계 통과**. 신규 31·재사용 0이다.
Git 객체·빌드/캐시·NuGet/home을 분리하고 실제 LF/CRLF checkout을 확인했다.

- 실제 C# 창의 고정 선언 수정 거절·새 문체와 enum 형식 오류를 확인했다. 오류가 난
  입력을 남기고 원본/checkpoint를 유지하며 취소했다.
- 코드 Undo/Redo·취소·명시 편집의 cold 복원, checkpoint 쓰기 실패/명시 재시도를 확인했다.
- 의도적으로 잘못 작성한 C#의 실제 compiler Confirm에서 `CS0103`과 원래 기호 이름의
  진단 응답을 확인했다. 원본·초안은 유지되고 최종 소스가 반영되지 않는다.
  Review 자체를 실제 컴파일 완료로 세지 않는다. 기존 UI의 실패 안내를 유지했다.
- 사용자가 명시적으로 오류를 수정하고 주석만 추가한 뒤 원래 CRLF C#의 나머지 byte를
  보존했다. 반복 Save·Review 취소·최종 원문 충돌 거절·새 Review/Confirm·실제 CLR 실행·
  확정 cold를 통과했다. out/반환 10과 `callee:1 → after:10`을 확인했고 다른 원본 파일은 유지했다.
- 이미 완료한 분기선 첫 Task 결합도 LF의 정상 입력, CRLF와 전체 복원본의 늦은
  C#·응답 중단/cold/저장·Review/실행 회귀로 새로 실행했다. 안내 편집 흐름은
  새 패키지와 전체 복원본에서도 실행했다.

변경 영향에 맞춘 집중 검증이다. 이전 M4의 별도 Core 18개 suite와 기존 47단계를
이번 신규 검사로 합산하거나 재사용 통과로 세지 않았다. backend 무변경 증명과
현재 실제 컴파일·실행·UI 검사 범위를 구분한다.

## 개발 검사에서 고친 기대

처음 fixture는 compiler 진단을 Review 단계에서 기대했다. 기존 실제 컴파일은
Confirm에서 수행하므로 올바른 단계로 수정했다. 물리 충돌 거절의 실패 envelope를
성공 응답 형식으로만 읽던 도우미도 실제 UI Confirm과 파일/checkpoint 보존으로 수정했다.
ordinary C# 편집은 원문 충돌 중에도 개인 초안 작성을 허용하고 최종 Confirm에서 원본을
보호하는 기존 동작이다. 이를 새로 금지하지 않았다. 쓰기 실패 주입은 readonly checkpoint로
검증하고 물리 충돌은 최종 Confirm 경계에서 확인한다. 실패 근거를 숨기지 않고 보관했다.
제품 변경은 안내 문자열과 자산 무결성 값뿐이다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/00ae14efebb749f992cf1f87880eb758.json`

개발 증거 ZIP SHA256 `ccacf0e221597bd90553ee380c73acfaf91846752390d3c89972b2fcf8a26357`.

## 보관과 공간

최종 record `/workspace/artifacts/v536-verification-managed/runs/ccfb30c6af3d42ffa95443f013a1917e.json`

증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/ccfb30c6af3d42ffa95443f013a1917e.zip`

SHA256 `8f90be2d4e440585c789819b9d957ce43943b0e7601e6fcd70406a0c841def73` (2.39MiB).

최신/롤백 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다.

- latest: 출처 `7855881f17207f711673811dd9a29961c3fe3a76`, `f043e336b76651545c212db3fa339f3f15910fe8014b454dbce49dcc4713049b.zip`, 49.13MiB; 파일 2381·디렉터리 147, 전체 manifest `c42c17958c74dd5a2bbf0d7f96b0e66b20b4af19003ae6a812f8a2c4e4819a76`.

- rollback: 출처 `5f223d2db3b0cf62f6917d5113aaf40c5719b136`, `7f336f37322a22067ee0969a2dc302aa0499c9e69e65364d39676f138975e245.zip`, 49.13MiB; 파일 2381·디렉터리 147, 전체 manifest `83af149a127ace824427bb7fa9ced1bf5f84f55cd0fc693054f313a809329208`.

최신/롤백 ZIP CRC·전체 파일 SHA·모드와 신규 패키지의 전체 추출 후 엔진/UI·실행을
확인했다. 자식 종료와 증거
검증 뒤 이 실행의 소유 임시물만 정리하고 기존 승인된 latest/rollback 승격 수명을 유지했다.
과거 자료·SDK·원본·사용자 데이터·로그/프로필의 추가 정리는 없다.

단계 표본 최소 여유 1659.36MiB, 최대 cgroup 메모리 4730.41MiB.
최종 실행 순증가 3.28MiB, 개발 검증 시작부터 최종 보관 확인까지 측정 순증가
4.29MiB. 문서 마감 전 측정 여유 1656.14MiB.
이 측정을 매번의 3–6MiB 고정 보장으로 사용하지 않는다.

## 잔여와 미실행

V2 전체를 마감하지 않는다. 다른 노출 핀/값·일반 저장/검토·탐색/시스템 안내가 남는다.
아직 없는 V3–V9의 안내는 해당 화면 구현 때 원본과 대조한다. 기존 팩/backend·종류
C# 표현/사용 중 삭제 대응과 실제 Windows/모바일·전체 UI·Space 전달은 별도 잔여다.
M11/M12/M4를 다시 미구현으로 열지 않으며 3D와 권한 팩 분리·이동/실행 분리를 유지한다.

이 검사는 컨테이너 Chromium UI·실제 .NET 컴파일/실행·Windows 교차 패키지다.
실제 Windows apphost/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복을 새로
검증하지 않았다. live AI 자격증명·유료 호출·외부 접근 grant는 사용하지 않았다.
