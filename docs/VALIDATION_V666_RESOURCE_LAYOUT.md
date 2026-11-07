# v666 자료 카테고리·계층 탐색·이동 검증

최종 동결 `61102a4eda29c0fbc1f5db99441d22558152b576`의 LF **15**, CRLF **15**, 패키지/전체 복원/수명 **8**, 총 **38단계(신규 34·동등 근거 재사용 4)**를 통과했다. 이후 게시 문서 외 제품/검사 입력은 바꾸지 않았다. 실패·수정 전 실행은 최종 통과 수에서 제외한다.

- 원본 ZIP의 `dist/app.js::resourceCreateMenu/resourceNameDialog/navigateResources/moveResources`를 따른다. 원본 이름 폼·계층/경로·드래그를 재사용했다. 선택한 파일/카테고리의 ID와 부모만 별도 native 목록에서 변경한다. 파일 내용/확장자/ID/hash, import receipt, 원본 manifest·C#·프로젝트 식별자·실행 계약/override·부모/외부 원본은 그대로다.
- 독립 실제 DSL 소비자로 빈 읽기 무부작용, 중첩 생성, 파일/폴더 이동, 선택 부모+자식의 root 이동, exact receipt replay, self/descendant/unknown/foreign/path 거절, stale basis/다른 command intent, 실제 쓰기 실패/재시도, 손상 topology 거절, 이전 flat reader 호환과 원본 bytes 보존 29개를 확인했다.
- production Layout/Request/Snapshot/CommitPlan/WriteAtomic/LeasePath 원문을 추출한 통제 harness에서 성공·manifest/identity/file-store/layout 최종 CAS 경합·쓰기 실패를 실행했다. 이 harness만으로 실제 DSL wiring을 주장하지 않으며 독립 소비자와 native UI가 별도로 검증한다.
- 실제 생성한 File과 원본 이름 폼·취소/확인·중첩 경로·카테고리 계층·브라우저/ProjectPack drag를 조작했다. 이동 후 같은 ID/hash의 기존 텍스트 창에서 원래 CRLF/Unicode를 읽었다. self drop, 실제 권한 쓰기 거절, 응답 유실/같은 요청 재시도, Confirm 전 peer 변경/새로고침 뒤 오래된 요청 재거절, 입력만 취소와 외부 MIME 위조를 확인했다. 새 검색과 다른 입력은 보존한다.
- 실제 engine cold restart에서 폴더/파일 관계와 private pending intent만 복원했다. 자동 mutation은 없으며 명시 같은 요청 retry가 이미 저장한 ID를 중복 생성하지 않는다. Home 왕복·동일 namespace의 다른 실제 프로젝트·원래 프로젝트 복귀에서 소유 경계를 확인했다.
- 기존 V6 import 실패/취소/응답 유실·V7 읽기 전용 관측/원본 내용·C# 본문 저장 실패/기존 Undo 보호를 영향 회귀로 실행했다. 자산 전용 공유 Undo나 파일 삭제/내용 복구를 새로 구현했다고 주장하지 않는다.
- 두 checkout 모두 독립 Git/cache/NuGet 복사본에서 Release/MCP/engine을 생성한다. 새 Windows-x64 교차 패키지의 실제 packaged engine과 ZIP 전체 복원본에서도 native UI를 실행한다. SHA·CRC·전체 파일/디렉터리 모드와 실패 수명/증거 보존을 검사한다. Linux에서 이 검사를 실행했으며 Windows apphost/WebView2·모바일·전체 UI 검증은 아니다.

실패 구분과 재사용:

- 첫 동결의 새 bridge 지역 변수 `action`이 기존 outer 변수와 충돌했다. 실행 전 compile 오류로 수정했다.
- 다음 native 독립 소비자는 29개 검사를 통과하고 정상 종료했지만 wrapper의 `>=30` 개수 assertion에서 실패했다. 정확한 29개로 수정했으며 제품 실패와 구분한다.
- 실제 dragstart에서 별도 채팅/개인 화면 자동 저장의 global busy가 자료 드래그를 막는 것을 재현했다. 명시한 ID·대상·revision은 즉시 보존하고 실제 native 저장은 기존 idle/work 대기열을 거치도록 수정했다. 자산 자체 pending·소유/수명/최종 CAS 거절은 그대로다.
- 첫 충돌 fixture는 상대 저장 뒤 폼을 열어 최신 기준의 정상 저장을 잘못 실패로 기대했다. 폼이 기준을 캡처한 뒤 Confirm 전 상대 저장으로 순서를 고쳐 실제 충돌을 검사했다. 제품 수정과 구분한다.
- 실제 cold 복원에서 private metadata는 보존됐지만 창 생성 뒤 metadata를 다시 붙이는 두 단계 복원 때문에 runtime pending이 연결되지 않는 누락을 찾았다. resource render에서 같은 소유자의 보존 입력만 hydrate하고, 자동 재실행 없이 명시 retry/cancel을 표시하도록 수정했다.
- 재사용 4개는 owned IPC/수명 검사, LF 독립 Layout 소비자, LF 최종 CAS harness, LF C# source 복구 UI다. native 두 검사는 native/CLI/fixture 입력이 같으며 마지막 복원 수정은 resource UI에만 있다. C# 회귀의 재사용은 resource 창이 없는 해당 입력에서 새 hydrate 분기가 실행되지 않는 한 줄 차이를 검증했다. 실제 record의 source/test/SDK/dependency/command 동등성 증거를 따른다. 필요한 빌드·새 UI/저장·패키지 복원은 새로 수행한다. 재사용한 검사를 신규로 세지 않는다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/fd839b7a88e3495b91ae44d16135902d.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/fd839b7a88e3495b91ae44d16135902d.zip` · 2,476,942 bytes
- 증거 SHA: `79074d3f5c504c40568394a1a96d0db9f71528b051bdf492a0e5dddfc1717a17`
- 최신 source: `61102a4eda29c0fbc1f5db99441d22558152b576`
- 최신 ZIP: `2325c8c69406b37c7acd6ff2f43d8d1b77c06400dfac47f3810cbf5767a3b8b2.zip` · 51,907,518 bytes · 파일2495 / 디렉터리153
- 최신 전체 manifest SHA: `246bafaf60da0dbe7a9215e72afe504f8bc40b9396c23d6eeb1262d015406a33`
- 정상 롤백 source: `2fca9f30a894cf7c1ea64d7d9f35bef25ad5675c`
- 롤백 ZIP: `6be52fa22fd271dae2a6b1db35c001eedf3b3fcc13bbb7bcce87a622806f7cb2.zip`
- 롤백 전체 manifest SHA: `661cfe284919748aa83cb6b320367b5a471bdbf0db87a18defbd5445b245316e`

기존 `/workspace/artifacts/v536-verification-managed/packages/index.json`에서 최신/롤백을 원자 승격했다.
전체 SHA·CRC·모드·복원을 확인한 두 세대와 실패/재사용 증거를 보존한다. 자식 종료·소유권 확인과
증거 보존 후 해당 실행이 만든 RAM 임시물만 정리했다. 과거 자료 추가 정리는 없다.

최종 실행 디스크 순증가 3.36MiB, 실패/수정 기록을 포함한 이번 구간
순증가 8.62MiB, 측정 시 여유 1220.30MiB다.
단계 표본 최소 여유 1223.62MiB·peak memory 4905.31MiB를 확인했다.
기존 지속 공간144MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가 메모리7GiB+1GiB 기준을 낮추지 않았다.
증가량은 다음 단위의 보장값이 아니다.

이전 실행 기록(최종 통과 수에서 제외):
- `2bd2952c314d41fa9479e9b3bd57ef58.json` · SHA `bbc45ecdb6f7c0847ea3203e98f10344fef9472664ab3e126f8f2b95dafb895c` · 완료6/실패1
- `2f39417f085f4be2828c84181250115a.json` · SHA `eec882d4a72d983c3babe99acbaea22c0479bb1d2ad85ccb66a53678204083b0` · 완료10/실패1
- `304a74007aaa45148b508889454fbe56.json` · SHA `09eabbc624e23884cdb7341b0c63cf88a583b6aabca915604c3b5ad247fdfd69` · 완료8/실패1
- `ca57264da1ba4838885da6457f3b2256.json` · SHA `115c44c4ecda83c290ed77dffb399e68f74c05dfd5c2ed7a02e46f2eeb42b914` · 완료6/실패1
- `1a0ecbb5d7c74b2da4ee317817976685.json` · SHA `c96e43bc6633cf5b32b7e6e7f097360a5916aac5942dc9ca819d59955c7845f2` · 완료9/실패1
- `4aa9ee89de234ff7a1632ac080d44ca5.json` · SHA `c194bc07ce233984e88410502ebdd4453e4e082f621eddaf83ce12b476386dc5` · 완료21/실패1


원래 고정 잔여: 파일 추가의 다중/큰 자료·현재 폴더와 첫 import 원자 결합, 카테고리/자료 이름·설명/삭제·내용 편집/backup 복구, image/audio/video/mesh 등 지원되지 않는 미리보기와 Run/native·권한 backend 및 다른 고정 항목은 완료하지 않았다. 임의 type/context 조합을 새 필수 항목으로 늘리지 않는다. 초기화 간헐 빈 화면의 직접 원인은 여전히 미확정이다. 실제 Windows·모바일·전체 UI·Space/Library 전달도 미완료다.
