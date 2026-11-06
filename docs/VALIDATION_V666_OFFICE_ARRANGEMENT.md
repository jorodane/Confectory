# V666 개인 3D 배치 검증

코드/검사 동결: `803610ea631000ccea333510ed1e8575efff2c79`. 이후 마감은 문서만 변경한다.
[지원 경계](V3_PRIVATE_ARRANGEMENT.md)와 [정확한 제품 delta](v666-office-arrangement-delta.json)를 따른다.

최종 **38단계: 신규 38 / 재사용 0** 통과.
LF 15 · CRLF 16 · 새 패키지/전체 복원/실패 수명관리 7.
독립 Git 객체·빈 엔진 캐시·SDK home/NuGet 복사본을 사용했다. 추가 디스크 예산144MiB
(안전64MiB 포함), RAM filesystem3GiB+512MiB 및 메모리7GiB+1GiB 안전 기준을 낮추지 않았다.

실제 관리형 엔진·생성한 두 프로젝트와 Chromium software WebGL에서 확인했다.

- 원본 배치 버튼/카탈로그, 실제 바닥 클릭·충돌 거절, 화분 배치의 지역 Undo/Redo·취소·확정.
  미확정 가구는 전체 private checkpoint에 들어가지 않고 변경한150% 카메라는 저장된다.
- 패널 왕복 중 미확정 메모리 유지·숨긴 Confirm callback 거절과 명시 취소. 확정 가구의
  동일 ID/geometry를 저장·새 엔진에서 복원하고, 저장 제외된 다음 미확정 가구는 복원하지 않는다.
- 실제 소유 검사 presentation 파일을 read-only로 바꿔 native 원자 쓰기를 거절시켰다.
  파일 bytes/기존 model 값은 유지되고 확정한 메모리는 남으며, fixture mode 복원 후 재시도가
  두 가구를 정확히 저장한다. 사용자 파일/권한을 변경한 검사가 아니다.
- 서버 checkpoint 뒤 성공 응답을 유실 오류로 바꾸고 더 늦은300% 카메라와 미확정 세 번째
  가구를 입력했다. 재시도는 최신 카메라와 두 확정 가구만 저장하고 세 번째는 넣지 않는다.
- 기존 child Workspace를 fixture 입력으로 만들고 실제 탭 왕복에서 root/child 배치의 소유
  격리를 확인했다. 미확정 child를 떠나면 확정 배치가 유지되고, 이전 child Confirm은 root를
  바꾸지 않는다. A/홈/같은 namespace의B/A에서도 이전 callback이 다른 owner를 바꾸지 않는다.
- 새 배치 검사에서는 C# source 파일 원본 bytes와 source/계약/Review/AI/Run 쓰기 호출이
  없음을 확인했다. 별도 기존 Worker 회귀는 명시 승인된 fixture source만 채택하는 기존 경로의
  승인 거절·실행·검토/채택·취소와 cold/비공개 기록 철회, B2 projection, 기존 배율·
  늦은 저장/프로젝트/재시작/WebGL 비지원 회귀. Worker 회귀의 HTTP는 소유 loopback fixture이며
  자격증명·라이브 AI/계정·유료 호출을 사용하지 않았다.
- 새 Windows 교차 패키지 구조/출처·패키지 엔진의 배치, 압축 전체 파일 SHA/CRC/디렉터리
  모드 복원과 복원 엔진의 쓰기 실패/응답 유실/owner 격리·WebGL 비지원, 실패 수명관리.

backend/원본 renderer 재사용은 검사 재사용으로 세지 않는다. source CAS/권한/계약 backend의
전체 옛 행렬을 다시 검증했다고 주장하지 않는다. 화분과 이 private 수명 흐름을 집중 검증했으며
전 가구·모든 변형/충돌 모양·터치/실기기·전체 하위 Workspace 조작은 미검증이다.
Run backend의 surfaceSupported/fpsSupported는 false이며 검사 환경에/dev/snd가 없다.
작업실 WebGL을 실제 Run 영상·오디오 backend의 완료로 표현하지 않는다.

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/b0614b0822eb4e7f902f96f13c21e9e4.json`

증거 ZIP SHA-256: `386fd8f7751b253a576eda08adf7ccda9c0ce6294292ae138b555ca7e8ccd676` (8263686 bytes).
전체 증거 manifest/압축 무결성을 검증했고 cleaned 및 owned RAM root 제거를 확인했다.

| 보관 역할 | 출처 commit | ZIP SHA-256 | bytes / files / dirs | 전체 manifest SHA-256 |
|---|---|---|---|---|
| latest | `803610ea631000ccea333510ed1e8575efff2c79` | `43cce10fa8d6e2a6888974d81e4b2957d0f84cebc28a50173df06d2f03a54f03` | 51781067 / 2405 / 150 | `419e6a0b4c152c9370334ee2d10221813052d8a443499e0690d5cb264ea7e8bd` |
| rollback | `80c2c8731ddea990ceed56db1d1a0a64fb4598b6` | `7d094502d6ac26024cb04d72f8263f4c97c97a167828cf0ce753a586176d5134` | 51780511 / 2404 / 150 | `6554eebe34f5ca4d1ef089f7d2248a1115ca13db560ee95f20e267bfd377abd6` |

보관 위치 `/workspace/artifacts/v536-verification-managed/packages/`. 최신/롤백 승격은 기존
승인된 owned transaction만 사용했고 원본 MIT 라이선스도 전체 manifest에 남았다.
과거 원본·별도 패키지·로그·프로필·사용자 데이터는 임의 삭제하지 않았다.
최종 실행 디스크 순증가 8.85MiB, checkpoint 전체 순증가
21.03MiB, 측정 시 여유 1475.23MiB.
검사 중 관측 최소 여유 1483.99MiB, peak 메모리 4761.73MiB.
이후 단위의 보장값은 아니다.

개발 중 검사에서 원본의 배치 중 dock 숨김, 확대 시 방 라벨 숨김, 실제 tab 역할과 렌더링
프레임 대기를 반영했다. 이를 제품 레이아웃/권한 변경으로 우회하지 않았다. 다음 실패 증거는
모두 보관/정리했으며 최종 통과나 재사용에 합산하지 않는다.

- `/workspace/artifacts/v536-verification-managed/runs/cb046cf38c4c4fbbb3b64b5620ab0bdd.json` (`084d0eb081f3fccd5f4fbb85965caf7a8b62759275aceea7f42af738a686c655`): 10 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/3e977e1eb26e4fce9617f64008f9f54b.json` (`89aa34b47d5fe1765bc62d466ffbef5f09e17d847452b99850c6f3346c5d847c`): 10 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/743c5a1b90c6484eb0c73432348a7ef1.json` (`283225cbf6532ce3f538cb4a3f78d7be63de3f2c8f16dfffa3b3fb13116dab6e`): 10 통과 / 1 실패.

반복 전체 빌드에 앞서 같은 소유 독립 진단 작업공간에서 두 UI 모드의 남은 조건을 확인했다:
`/workspace/artifacts/v536-verification-managed/runs/5d89c0b25a734516a4d619f138adf5c2.json` (`0f35538dd77197680b837bf3948eaedbaf407e3f4e9ba34548fbd5ad22b3710f`), 12 진단 단계. 원본/검사 SHA를 보존했고 계획 종료 후 cleaned 및 RAM root 제거를 확인했다. 패키지를 승격하지 않았고 최종 수에 합산하지 않는다.

실제 Windows apphost/WebView2·모바일/하드웨어 GPU/DPI/IME·전체 UI·Space/Library 전달은
미검증/미완료다. 현재 source/권한/입력 보호와 별도 팩 경계는 유지한다.
