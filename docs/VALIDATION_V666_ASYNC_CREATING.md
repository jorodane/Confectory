# v666 M4 새 ordinary leaf · 최종 검증

동결 `981d28824aa91eeca03a8a5881e3be52c116affd`를 `tools/verify_desktop.py --suite async-creating`로 검사했다.
[지원 경계](M4_ASYNC_CREATING.md)는 기존 소유 Root에 새 ordinary C# 동작을 만든 뒤
첫 물리 Confirm 전 명시 async 전환·코드 편집·저장·전체 Confirm하는 흐름이다.

최종 **총 45단계(신규 39, 동일 입력 재사용 6): LF 19, CRLF 17,
새 패키지/전체 복원/실패 수명관리 9**가 통과했다.
Core/runtime은 LF·CRLF 각
18 passed, 0 failed, 0 skipped이며 실제 CLR 실행을 포함한 동일 C# 근거를 재사용했다.

- 새 record의 원래 ID/경로 부재·기존 graph/함수 소유·원본 hash와 정확한 경로를 검사한다.
  기존 ID/경로 재사용, 원본 위조, missing 헤더/graph, alias·누락/변조 영수증을 거절한다.
- 실제 생성 API의 빈 record와 definition hash placeholder를 C# 작성 없이 명시 전환한다.
  missing source CAS와 cold 영수증을 보존하며 부분 Review를 거절한다.
- 실제 UI의 메뉴·Undo/Redo·편집 취소·cold·반복 Save·Review 취소/Confirm,
  저장 권한 실패·상대 파일 충돌·응답 유실·늦은 입력의 독립 보존을 확인했다.
- Review 뒤 새 파일 경로를 상대 파일이 차지하면 전체 Confirm을 거절한다.
  상대 파일·모든 기존 파일·초안 입력이 그대로이고 제거 후 명시 재시도가 성공한다.
- 사용자 작성 `await Task.Yield()` 뒤 새 동작→기존 동작의 stdout 순서와 반환값을
  실제 생성 앱에서 실행했다. 원래 C#의 CRLF/문자·함수 계약/ID·다른 원본은 보존한다.
- 이전 확정 native-context/ordinary-adapter API는 신규 회귀이며, receipt·최종 read CAS는 동일 입력의 검증 근거를 재사용했다.

새 Windows 교차 패키지의 구조/현재 assembly 일치와 packaged-engine UI·Task를 검사했다.
압축 전체 파일 SHA·CRC·mode/디렉터리 manifest를 검증하고 RAM 전체 복원본에서
늦은 입력·저장 실패·Task를 실행했다. 실제 Windows apphost/WebView2·모바일은 미실행이다.

## 개발 실패와 재사용 구분

개발 record `858209ba315f406db97c57e0a4dd5a4a`와 전체 증거를 보존했다.
Root 생성 배치에 지원하지 않는 entry/source 전용 작업을 섞은 검사 입력을 기존 API
절차로 수정했다. Confirm 뒤 비워진 changes에서 경로를 찾던 검사는 관측한 경로를
유지한다. 새 카드의 sidebar 가림/창 초점 문제는 기존 overview 및 caption 조작으로
검사했다. 강제 클릭이나 제품 레이아웃 변경으로 통과시키지 않았다.
이 개발 실패/집중 통과는 최종 신규 단계 수에 더하지 않는다.

첫 최종 record `d4af0190ec2845e6bada50c2d6b4fb2b`의 LF 18단계와 CRLF
응답 유실은 통과했으나 늦은 async-plan의 cold 후 명시 Save가 거절됐다. 생성 작업
뒤의 process-local revision은 바뀌었지만 origin cell과 전체 ID/hash는 같은 경우였다.
기존 두 번 확인된 자체 settled receipt 조건에서 async-plan만 epoch 복원을 허용했다.
타입/node/origin 누락·다른 ID/hash·불완전 목록·일반 source는 계속 거절한다.
실패 archive를 보존했고 새 proof 검사와 모든 UI·독립 빌드·패키지/복원은 신규 실행했다.

재사용은 Core/metadata/최종 CAS 전용 6단계다. prior archive 전체 SHA/manifest,
SDK/NuGet/RID/configuration과 전체 Git diff를 검사했다. 변경은 browser predicate와 대응 WebBundle 고정 resource descriptor,
Node proof 검사, 검증 recipe와 설명뿐이며 선택된 Core/authoring/pack/probe의
입력 bytes는 같다. 이 단계는 EditorHome/WebBundle/browser JS를 실행하지 않는다.
리소스 manifest 갱신 누락을 시작 검사가 거절한 두 번째 실패 record
`faf8a86865644c15b31b7858dddbf726`도 보존했다. pin을 갱신한 뒤 엔진·API·UI는
모두 신규 실행하며 무결성 검사를 낮추지 않았다. 정확한 이전 commit·명령·
log hash와 read set을 `reuse-audit.json`에 보관했다. 실패 단계는 재사용하지 않았다.

## 보관과 공간

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/2efb1c7d38524aa5bf85df9cc7959851.json`
- 전체 증거: `/workspace/artifacts/v536-verification-managed/runs/2efb1c7d38524aa5bf85df9cc7959851.zip` · SHA256 `cbd4abde9dd66334e74fc251d064e28fc3e3c293eb4368b7373d332038ffcf1f` · 3,250,827 bytes
- 최신 source `981d28824aa91eeca03a8a5881e3be52c116affd` · ZIP SHA256 `3637d9fa0c7702dfdaf57e3732be61747ad1a1e04870c88240d1944575441c7f` · 51,482,398 bytes
- 전체 manifest SHA256 `3703c16e0e6bba9e58fc6c5f719af5e545695ce7f96b2b7388584ff670bf5622` · 파일 2,377개/디렉터리 147개
- 정상 rollback `b3fa243c68d5ca58604e206f24a2168b466eb57a` · ZIP SHA256 `0c7326bd0b3ebd5fd9cefb23ee5a6ddb02040650c926d4e758bfe6a22ad171d8` · manifest `28c97486836c6f6efd1b56cef242dc9030468ff340bf394ff11e3931fe8b525e`
- 최종 실행 전 1752.9 MiB, 종료 1748.8 MiB, stage 중 최소 1752.9 MiB.
  작업 전체 시작 대비 순증가 8.8 MiB; 다음 실행의 고정 증가량 보장은 아니다.

필수 안전 여유 64 MiB를 낮추지 않았다. 최신/rollback 원자 승격 후 전체 증거를 지속
보관하고 이번 실행 소유 임시 checkout·캐시·패키지·전체 복원본만 정리했다.
임시 root 제거는 `True`다. 다른 과거 자료는 삭제하지 않았다.

## 남은 유한한 경계

새 함수/구현/graph의 전환, 직접 소유 private/internal Task 경계와 첫 생성 Save 전
혼합 입력 제한은 별도다. 이번 예외를 새 헤더·원본이 있는 ID나 parent/reference에
확대하지 않았다. 동기 호출자는 명시 전환 전 오류이며 자동 대기/변환하지 않는다.
기존 async/record 문법은 유지한다. 이전 rollback은 아직 파일이 없는 새 record의
전환 초안을 거절할 수 있어 코드 rollback과 해당 초안 복구를 구분한다. 자동 migration을
새 필수 요구로 만들지 않는다. M11/M12는 마감 상태를 유지하고 고정 V1 검증 잔여/V2–V9·팩/backend·종류 호환성
결정·기기/전체 UI/Space 전달은 미완료로 구분한다. main은 사용자가 검토·merge한다.
