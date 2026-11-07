# V666 640×360 Run 출력 검증

[실제 지원·한계·호환](V8_RUN_WIDE.md) · [원본/제품 delta](v666-run-wide-delta.json).
최종 코드·검사 동결 `2ab45f985689eb2d764793ab4d3851dabace185b` 이후는 문서만 변경했다.
최종 **신규 55단계 통과**, 별도 보조 guard **2개 동등 증거 재사용**.
LF 24 · CRLF 24 · 패키지/전체 복원/실패 수명관리 7.
독립 Git 객체·NuGet/SDK home·처음 빈 엔진 cache/출력을 사용했다.
별도 개인 등록 decoder/자동 맞춤 상태 guard 두 개는 동일 환경에서 앞선 동결 코드로
통과한 보존 증거를 재사용했다. 해당 검사/모듈 바이트는 변경되지 않았으며 현재 파일 SHA와
원본 증거 ZIP/manifest를 대조했다. 이 두 개는 위 단계 수에 합산하지 않는다.
명령·입력 SHA·결과·원본 기록과 현재 동결 SHA의 연결은 최종 증거의
`wide-supplemental-guards.json`에 보존했다. 변경된 선택 목록 UI는 새로 검사했다.

- 원본 ZIP의640×360 옵션과 허용 제품 파일/리소스 핀을 대조했다. 기존 FrameControl
  인증·전송/heartbeat 구현과 프로그램 C#·스타일·공개 Invoke/override 계약·권한·source
  Review/Confirm·최종 CAS를 보존했다. 원래1MiB 픽셀/1.4MB packet 예산은 확대하지 않았다.
- 새 capability는 축640·총262144픽셀을 선언한다. 이전 max512도 읽으며 같은 publisher의
  cap 변경/소실·임의 확대를 거절한다. projection 검사는 실제640×360 전체 SHA/정확한
  길이·unchanged receipt·축/면적·pixel capability·legacy512/자동 맞춤 경계를 확인했다.
- 실제 native pipe/reader/WebUI에서640×360의921600bytes와 전체 SHA를 확인했다.
  생성한 provider의 maxPixels 확대/누락·동일 publisher max 변경·실제/요청 면적 초과·
  max1280 변조는 거절하고 기존 관측을 보존했다. 새 publisher의legacy512를 허용하며
  retired publisher는 거절했다. 예전 최대512×512 전체1MiB 및 SHA/길이/타입/순서/
  unobserved unchanged/foreign ownership/heartbeat 미갱신 회귀도 새로 실행했다.
- native RunSurface 검사는 기존 explicit opt-in/thread/copy/once/close와640×360
  초기 설정·실제 Present를 확인했다.640×410 면적과641px 축을 거절하고 실패가
  revision을 진행하지 않음을 검사했다. 실제 frame/WebUI 소유·취소·폐기 회귀도 실행했다.
- 원본 메뉴의PC640×360 선택은 paused64×36·frame을 보존하고 요청을 한 번 보낸다.
  실제 Step 뒤에만640×360 픽셀/ACK를 확인했다. 개인 등록과 cold 목록 복원,
  640×512 입력의 적용/등록 비활성화 및 입력 보존,640×409 실제 출력도 확인했다.
- native가 접수한 고정 해상도 응답을 유실 처리하면서 새600×400/name을 입력했다.
  읽기만으로 기존 receipt를 회수했고 늦은 입력을 보존하며 명령을 재전송하지 않았다.
  외부/stale/면적 초과 명령 거절, pending 닫기·retired form·형제 창/cold의 빈 runtime과
  기존 chat/layout 복원도 확인했다. 미저장 폼 전체의 cold 복원을 주장하지 않는다.
  UI만의 legacy publisher 교체는 생성한 정상 픽셀 응답을 주입한 검사로 구분한다.
  max512로 교체된 고정/개인 항목의 비활성화와 폼 한도 갱신·명령 미전송을 확인했다.
  native legacy 호환성 검사는 위 실제 pipe capability 검사로 별도 수행했다.
- 직접 크기·개인 preset CAS/충돌/실패/유실·프로젝트 왕복과 자동 맞춤의 최신 geometry/
  ACK/실패 latch·명시 재선택, PCM 오디오 정상/수명 회귀를 새로 실행했다. 범위 밖 입력은
  변경된 비활성화 상태를 확인하고 요청이 전송되지 않음을 검사했다.
- 새 Windows 교차 패키지의 구조/전체 SHA/누락·변조 거절/관리형 엔진과640 출력 UI,
  전체 ZIP SHA/CRC·파일/디렉터리 mode 복원·복원 엔진의 실패/늦은 입력/닫기/cold를
  확인했다. 실패 증거 보존과 해당 실행 소유 임시물 정리도 통과했다. Linux 관리형
  엔진/Chromium 검사이며 실제 Windows 기기 실행이 아니다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/1a87036542094c888755ca7f6def6e95.json`.
증거 ZIP SHA256 `38469d0d9e386f1620b36b0aed9ad6b75ef0b711625d6addec7ec2208e98a872` · 2155095bytes.
전체 evidence manifest/ZIP을 검증했고 owned RAM root가 제거됐음을 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `2ab45f985689eb2d764793ab4d3851dabace185b` | `a6e191903493e38526c04766293ca07fe902366c6f43eccc19fe07b57a406a92` | 51845294 / 2467 / 152 | `27e9135e10688b90b1bc4a28e37ab46373576354ce1d171c907f5c2c320cd69c` |
| rollback | `ecf4b013ac41ec1a372dd10359ee3557a1dc76af` | `73eaa48b91852c5134d9f490171b24a7140016ecc3d45e6609c38dcec3bf87f8` | 51845090 / 2467 / 152 | `4a58b3d6b695ff3f2f13c893ed17e3c5d1d8acb673bb04cda4e01f5e127c6df4` |

기존 승인된 managed 최신/롤백 두 세대와 자체 임시물 수명관리만 사용했다. 과거 자료·
원본·SDK·로그·프로필·사용자 데이터는 추가 정리하지 않았다. disk 추가160MiB(안전64MiB
포함), RAM3GiB+512MiB·메모리7GiB+1GiB 기준을 유지했다. 최종 실행 순증가
2.96MiB, 단위 순증가 8.63MiB,
측정 시 여유 1392.01MiB. 표본 최소 여유 1394.92MiB,
peak 메모리 4695.75MiB. 이후 실행 증가량의 보장값이 아니다.

집중 진단 `/workspace/artifacts/v536-verification-managed/runs/11966e2060a84013b715db26b0fe91c1.json` (SHA `199247ef7c789771707ef4d3055f0f6c358b85016daf108fb652f2630d46e1e0`)은 정상/수명 UI·capability 변조·
실제 pipe·native 검사 뒤 의도적으로 종료해 증거 보존/정리하고 패키지를 승격하지 않았다.
최종 수치에 재사용/합산하지 않았다. 변경된 입력 비활성화의 검사 조건도 수정해 최종
코드에서 새로 실행했다. capability 변경이 선택 목록의 비활성화 표시를 갱신하도록
보완했고, 앞선 최종 시도는 결과 보존 후 중단했다. 옵션 matcher의 시간 초과는
원본과 같은 label/select/optgroup 안에서 disabled 옵션을 enabled인 select로 판정하는
검사 조건에서 재현했다. 브라우저 option.disabled와 실제 주입 도착을 직접 확인하도록
수정했다. 아래 중단/실패 실행의 단계는 신규55단계에 합산하지 않았다. 앞에서 설명한
변경 없는 보조 guard 두 개만 별도 증거/입력 일치 확인을 거쳐 재사용했다.

- `/workspace/artifacts/v536-verification-managed/runs/b618cbd87cb645bcadfe570f6777825c.json` · SHA `5fe948e3ab0c70356e2fcd92ce03ff314e796ee9ab6b5778a3aa0fa0ecfb71fa` · 통과 30 / 실패 0
- `/workspace/artifacts/v536-verification-managed/runs/709d8a771f744079a67f559b22cd0a68.json` · SHA `7af6f6b50a258a6c3cad5843abe0393b6a78b0782389f89ce5ddbcc7c8c6e9a4` · 통과 11 / 실패 1

현재 축640·262144픽셀 provider 범위다. HD/FHD/4K 등 더 큰 원본 해상도는 추가 전송/
메모리/수명 설계·검증을 필요로 한다. 진행 중 I/O의 비차단 제공 경계와 신원/권한·자산·
참여자/대화의 기존 고정 잔여는 별도다. 실제 Windows WebView2·모바일·장치/DPI/IME·
전체 UI·Space/Library 전달은 미검증이다. 계정·외부 권한·자격증명·유료/라이브 AI는
사용하지 않았고 main은 보존했다.
