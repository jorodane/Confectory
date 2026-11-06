# V666 실제 도구 완료 신호 검증

코드/검사 동결 `cd56cbcfd63b0f2b0466fe811938e270af3e5161` 이후 마감은 문서만 변경한다.
[지원 경계](V3_WORKSPACE_IO.md), [정확한 제품 delta](v666-office-io-delta.json).
최종 **38단계: 신규 38 / 재사용 0** 통과.
LF 15 · CRLF 16 · 새 패키지/전체 복원/실패 수명관리 7.
독립 Git 객체·빈 엔진 캐시·독립 NuGet/SDK home과 기존 승인 수명관리를 사용했다.
추가 disk144MiB(안전64MiB 포함), RAM3GiB+512MiB 및 메모리7GiB+1GiB 기준을 낮추지 않았다.

- 실제 DevelopmentTools read·stage·no-op, 권한/프로젝트/namespace 거절, stale CAS,
  dedup replay, 실패/불확실 mutation, fresh capability와 bind 이전 read의 귀속 보호.
- DTO/actor projection의 잘못된 project/receipt/ordinal/target/kind/outcome 거절,
  명시 배정/현재 소유 경계, 복수 배정 자동 선택 없음, 불변 snapshot과 시각/active IO 추정 없음.
- 실제 관리형 엔진의 Worker와 production Responses HTTP/tool protocol을 사용했다.
  소유 loopback fixture의 응답을 read 전/read 후/stage 후에 각각 보류하고 실제 UI와 공개 관측을
  확인했다. 승인 전 거절/취소, 3D 비활성 실행, read/stage 후 원본 bytes 보존, 명시 Review와
  compiler Confirm/adoption, 두 번째 Worker의 취소와 원본 보존을 검사했다. 라이브 AI·자격증명·
  외부/유료 호출은 없다. 이 fixture는 AI 품질/실기기 실행 검증이 아니다.
- 새 엔진의 중단 Task journal에 가짜 IO 필드를 넣어도 신호를 복원하지 않는다. journal bytes를
  다시 쓰거나 owner를 복구하지 않으며 foreign owner/project/private Helper/잘못된 기록 철회,
  같은 namespace의 다른 프로젝트 왕복·홈의 신원 폐기를 검사했다.
- 기존 B2, 개인 배치 확정/취소/지역 Undo와 늦은 입력·쓰기에 실패한 private 저장/응답 유실,
  root/child owner 격리와 기존 배율·프로젝트/cold·WebGL 미지원 회귀.
- 새 Windows 교차 패키지 구조/출처 및 그 엔진의 실제 read/stage UI, 압축 전체 파일 SHA/CRC와
  디렉터리 mode 복원, 복원 엔진의 cold 가짜 신호 거절·소유/프로젝트 철회와 WebGL 비지원,
  실패 수명관리. 교차 패키지의 관리형 엔진은 Linux에서 실행했다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/6b4b3bdff5c846fb935127e33b86f142.json`.
증거 ZIP SHA-256 `71b55210bc10e45c7e12a31538052d2421ba01fc4d2b14e16077f7a698c35367`, 6147354 bytes.
전체 증거 manifest/무결성 및 cleaned·owned RAM root 제거를 확인했다.

| 보관 역할 | 출처 commit | ZIP SHA-256 | bytes / files / dirs | 전체 manifest SHA-256 |
|---|---|---|---|---|
| latest | `cd56cbcfd63b0f2b0466fe811938e270af3e5161` | `e87f39cfd1793784d7aa5504cc81019817988d36fd39854e30b38799f8c263f5` | 51782570 / 2405 / 150 | `c268a33b02fb93aeaa1f9e032f5d829b45e59fd6ec53cf580f1d82bd50fca01f` |
| rollback | `803610ea631000ccea333510ed1e8575efff2c79` | `43cce10fa8d6e2a6888974d81e4b2957d0f84cebc28a50173df06d2f03a54f03` | 51781067 / 2405 / 150 | `419e6a0b4c152c9370334ee2d10221813052d8a443499e0690d5cb264ea7e8bd` |

`/workspace/artifacts/v536-verification-managed/packages/`의 최신/롤백을 기존 승인된 원자 승격으로
보관했다. 과거 자료/원본/별도 로그·프로필·캐시·사용자 데이터는 추가 삭제하지 않았다.
최종 실행 disk 순증가 6.85MiB, checkpoint 전체 순증가
8.25MiB, 측정 시 여유 1466.32MiB.
검사 중 관측 최소 여유 1473.10MiB, peak 메모리 4593.92MiB.
이후 단위의 보장값은 아니다.

최종 통과에 합산하지 않은 이전 시도:
없음.

실제 Windows apphost/WebView2·모바일·하드웨어 GPU/DPI/IME·전체 UI·Space/Library 전달은
미검증/미완료다. native 진행 중 IO phase·Run 영상/오디오 backend도 구현 완료로 세지 않는다.
