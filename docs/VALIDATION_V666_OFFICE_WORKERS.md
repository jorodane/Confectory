# V666 실제 Worker 표시 검증

코드/검사 동결: `80c2c8731ddea990ceed56db1d1a0a64fb4598b6`. 이후 마감은 문서만 변경한다.
[지원 경계](V3_WORKSPACE_WORKERS.md), [정확한 runtime delta](v666-office-workers-delta.json)를 따른다.

최종 **34단계: 신규 34 / 재사용 0** 통과.
LF 13 · CRLF 14 · 패키지/전체 복원/실패 수명관리 7.
독립 Git 객체·빈 엔진 캐시·SDK home·NuGet 복사본과 기존 승인된 owned RAM 수명관리를 사용했다.
추가 디스크 예산 144MiB(64MiB 안전 포함), RAM filesystem 3GiB+512MiB와 추가 메모리
7GiB+1GiB 안전 기준을 낮추지 않았다. 정상/실패 증거와 최신/롤백은 지속 공간에 보관한다.

실제 관리형 엔진·생성 프로젝트·Chromium software WebGL과 순수 projection 검사에서 다음을 확인했다.
8개 native 상태/대상 필터/불변 snapshot은 순수 실행 검사로 모두 확인했고, 아래 실제 UI
흐름은 배정 대기·running·검토 대기·완료·취소·cold 중단을 사용했다.

- 빈 3D 읽기는 Task owner/journal·시연 Helper/Worker를 만들지 않는다. 기존 명시 배정의
  공개 ID와 현재 프로젝트 Helper를 표시하고 다른 프로젝트/위조 활동 이벤트는 채택하지 않는다.
- 실제 native Worker의 승인 없는 시작 거절/preview 취소 후 source와 배정이 보존된다.
  자격증명 없는 소유 loopback HTTP fixture에서 기존 Responses tool protocol을 수행했다.
  HTTP를 정지시켜 실제 running 상태를 관측하며 이동/도착·가짜 write 이벤트와 분리했다.
- 3D를 끈 동안 기존 Worker가 실행되고 완료 검증 대기로 바뀐다. 기존 명시 compiler Review/
  Confirm/채택만 정확한 fixture node/graph를 변경한다. 별도 ready 취소는 다른 완료 Worker를
  바꾸거나 모델 호출을 재생하지 않는다. fixture는 실제 원격 AI가 아니며 유료 호출이 없다.
- 소유 journal의 running crash 조건을 주입한 새 엔진에서 interrupted/needsCheck를 읽는다.
  화면 읽기는 owner 열기/복구·dispatch·journal 재저장을 하지 않는다. Helper/Worker의
  움직이는 메뉴를 실제 키보드로 열고 객체형 상태·전체 ID/짧은 표시 이름을 확인했다.
- 소유 검사 journal의 다른 owner/project/private Helper와 malformed 조건을 각각 주입했다.
  기존 native 관측대로 actor/오래된 메뉴·상세 내용을 철회하고 partial 안내 또는 기존 조용한
  비공개 Helper 필터를 유지했다. private canary가 노출되지 않고 입력 journal bytes가 유지된다.
  같은 namespace/ID의 다른 프로젝트·A 복귀·홈·cold 관측을 검증했다.
- 기존 B2 projection·3D 보기의 카메라/배율·반복 전환/취소·늦은 응답/새 입력·프로젝트/재시작·
  WebGL 비지원 경계를 최종 코드에서 새로 실행했다. 변경하지 않은 source 저장/CAS/권한 전체
  행렬을 이 단위에서 재검증했다고 주장하지 않는다.
- 새 Windows 교차 패키지 구조/출처·패키지 엔진 실제 로컬 Worker 흐름, 압축 전체 파일 SHA/
  CRC/디렉터리 모드 복원과 복원 엔진의 cold/철회/비지원, 실패 수명관리를 확인했다.

최종 기록: `/workspace/artifacts/v536-verification-managed/runs/0058fd5cb2514934a6642cfbb844e400.json`

증거 ZIP SHA-256: `c15439d63a71c80dbfbac5ea6a24d7fa420c3d8dbce65958fecdd0ee32e8af09` (3711648 bytes).
전체 증거 manifest를 검증했고 최종 상태 cleaned와 owned RAM root 제거를 확인했다.
분리 renderer 진단도 증거에 보존했다. backend 구현 재사용을 검사 재사용으로 계산하지 않는다.

| 보관 역할 | 출처 commit | ZIP SHA-256 | bytes / files / dirs | 전체 manifest SHA-256 |
|---|---|---|---|---|
| latest | `80c2c8731ddea990ceed56db1d1a0a64fb4598b6` | `7d094502d6ac26024cb04d72f8263f4c97c97a167828cf0ce753a586176d5134` | 51780511 / 2404 / 150 | `6554eebe34f5ca4d1ef089f7d2248a1115ca13db560ee95f20e267bfd377abd6` |
| rollback | `6ad5b5d45dd88bea3a2fa177cd55ec486fde4a67` | `74c7d1a03f3bb6998d36eb420d77f2775137703a0bbded236a1d53829c542293` | 51778143 / 2403 / 150 | `438571943abcb3fdd3922f8e81ef80afd3f226a5af015718855dd679f8211514` |

보관 위치 `/workspace/artifacts/v536-verification-managed/packages/`. source-bound 최신/롤백
승격은 기존 승인 transaction만 사용했다. 원본 MIT 라이선스와 전체 파일 무결성을 확인했다.
별도 과거 원본·로그·프로필·사용자 데이터·기존 패키지를 임의 삭제하지 않았다.
최종 실행 순증가 4.72MiB, checkpoint 전체 순증가
11.61MiB, 측정 시 여유 1496.80MiB.
검사 중 관측 최소 디스크 여유 1501.44MiB, peak 메모리 4563.29MiB.
다음 단위의 보장값은 아니다.

개발 중 공개 관측 철회 뒤 메뉴 내용이 남는 문제와 새 객체형 Worker를 배열로 읽는 Helper
상세 오류를 수정했다. 원본의 움직이는 메뉴에서 Playwright가 정지를 기다린 시간 초과는
fixture 문제로 분리하고 실제 키보드 버튼 조작으로 검증했다. 이 상세창 검사에서는
레이아웃/이동을 정지시키거나 강제 click/DOM handler로 우회하지 않았다. 이전 실패/계획 중단은 최종 통과나
재사용 단계에 포함하지 않으며 전체 증거를 보존한다.

초기 계획 중단: `/workspace/artifacts/v536-verification-managed/runs/93413575ef3c44cd914968991bed2107.json` (`3d2b664be6dfe57eada5797752dc7c23fb37e6f91d5a76596b0902166dba0d29`),
18 통과 뒤 product 보완을 위해 중단/보관/owned 정리.
이전 실패:

- `/workspace/artifacts/v536-verification-managed/runs/e3387a0ea535457a8aa40c6bae24c020.json` (`3db6568322a170496b03c40b1842bdb75e85e015e27af44784d1466229a32f90`): 24 통과 / 1 실패.
- `/workspace/artifacts/v536-verification-managed/runs/57b86c314cc7419c851b4718664de8e5.json` (`cd8707a9cf604fdca9f0dc56232d77266ea8c690c7b3051b55443aedee1101b2`): 24 통과 / 1 실패.

실제 Windows apphost/WebView2·모바일·하드웨어 GPU/DPI/IME·전체 UI·Space/Library 전달과
Run 영상/오디오 backend는 미검증/미완료다. 새 credentials·권한 grant·실계정·라이브 AI/유료
호출을 사용하지 않았다. read/write 신호와 배치/자식 Workspace·다른 고정 잔여는 지원 문서를 따른다.
