# V3 진행 중 I/O passive poll 최종 검증

[지원과 한계](V3_WORKSPACE_IO_POLL.md) · [닫힌 제품 delta](v666-office-io-poll-delta.json).
제품·검사·도구 동결 `a1e7d8cb87571ce34cde545c2c75c2cfac991b2d` 이후는 문서만 변경했다.
**신규 44단계 / 재사용 0**: 최종 suite43(LF18·CRLF17·패키지/복원/수명관리8)와
같은 코드의 원본100% 확대 가시성 보강1이다. 실패 재현은 통과 수에 포함하지 않는다.
독립 Git 객체·NuGet/home·빈 엔진 cache/출력을 사용했다.

## 실제 확인

- 원래 31434810 코드에서 실제 승인된 Worker의 읽기를 OS FIFO에서 보류했다.
  실제 EditWorkspace 잠금을 잡은 동안 3D의 진행 상태가 갱신되지 않는 실패를 재현했다.
  원래 코드와 수정 코드 모두 같은 생산 경로의 권한·도구·receipt·poll·3D projection을 사용했다.
- 검사 엔진은 두 pack의 **실행별 소유 복사본만** 계측했다. 도구 읽기 thread의 실제
  EditWorkspace lock 안에서 실제 OS pipe 읽기를 기다리게 했으며, 해제 뒤 원래 source 읽기를
  그대로 실행했다. 계측은 FIFO 스케줄링용이고 성공·진행 DTO나 browser 응답을 주입하지 않았다.
  일반 물리 디스크 지연/모든 I/O 경로의 성능을 검증한 것은 아니다. 계측 source·원본 SHA·
  build report·입력·화면·native 상태와 트래픽은 각 증거에 보관했다.
- LF에서는 실제 읽기를 보류한 채 pending 진행 상태와 새 입력을 유지했다. 3D 표시를
  껐다 켜도 실제 읽기는 끝나지 않았고, 검사 writer를 명시적으로 해제한 뒤 원래 도구 처리와
  검증 대기로 돌아왔다. 기존 명시 Review/컴파일/Confirm/adoption만 원본을 변경했다.
  다른 ready Worker 취소와 no-project 진입도 확인했다. 이동·도착이 실행 조건이 되지 않았다.
- CRLF에서는 실제 pipe 읽기 뒤 검사 전용 경계에서 IOException을 주입했다. OS 장치 고장을
  재현한 것은 아니다. 진행 receipt가 해제되고 원래 실패 상태로
  돌아왔으며 새 입력·원본을 유지했다. 재시작/재실행/성공 완료를 만들어내지 않았다.
- 원본90% 보기에서는 Worker 라벨을 숨기는 기존 정책이 있다. 보강 검사에서는 원본 확대
  메뉴로100%를 선택해 실제 Worker 버튼의 가시성과 해당 라벨의 ‘읽는 중’ 상태 전달을
  확인했다. compact 라벨의 기존 문구/접근성·확대/애니메이션 정책을 바꾸지 않았다.
- 기존 native 비차단 read/stage·오류/충돌/중복 호출·cold/닫기·origin/권한 격리와 완료 I/O,
  3D/B2 projection을 새로 회귀 검사했다. 별도 실제 Worker의 완료/이력·개인 배치의 실패/
  응답 유실/새 입력·하위 프로젝트 격리도 확인했다.
- 실제 C# 편집의 Undo/Redo·취소·cold·늦은 입력·원문 보존·stale 충돌·Review 취소·최종 CAS·
  실제 실행을 LF/CRLF에서 새로 확인했다. 제품 delta는 Model.Command의 passive pending
  조건과 설명 주석뿐이며 명시 편집/채택, public/override 계약·권한·UI 배치는 바꾸지 않았다.
- **계측하지 않은** 새 교차 패키지의 엔진에서 실제 완료 I/O·Review/Confirm·취소를 확인했다.
  전체 ZIP SHA/CRC·파일/디렉터리 mode 복원 후 cold의 진행 신호/실행 재생 거절과 배치 실패/
  응답 유실/프로젝트 격리를 검사했다. 패키지 실패·예외 시 증거 보존과 소유 임시물 정리도
  통과했다. Linux 관리형 엔진/Chromium/소프트웨어 WebGL이며 실제 Windows·모바일 검증이 아니다.

43단계 suite와 별도 가시성 검사1은 모두 같은 동결 코드에서 새로 실행했다.
표시가 느린 호출만을 위해 가짜 timer/진행률을 넣지 않았으며 빠른 호출은 관측 사이에 끝날 수 있다.

## 재현 실패와 검사 수명관리

기준 실패 기록: `/workspace/artifacts/v536-verification-managed/runs/7dcca433dc3048e8885b13e873b8977b.json`
· 증거 SHA `734f1fd91edeb10b263eefb4143694c0522bbfab8d2303e453a942916f166829`.
이 실행의 UI exit1은 의도한 회귀 재현이며 최종 통과 수에서 제외한다. 이후 증거 봉인 과정에서
새 검사 FIFO의 종료 정리 누락을 guard가 거절했다. 자식 전체 종료를 인증하고 그 실행에서
직접 만든 FIFO만 type/UID/link·경로·해제 증거를 확인해 정리했다. 원본·과거 자료는 삭제하지 않았다.
수정 검사는 생성 inode와 host 종료를 확인한 뒤 자기 FIFO만 제거한다. 빌드 실패 전에는
FIFO 자체를 만들지 않는다. 일반 IPC 정리 guard나 FD/maps 접근 제한은 완화하지 않았다.

## 최종 증거와 지속 보관

- suite 기록: `/workspace/artifacts/v536-verification-managed/runs/b79bd18bbab6477c8d1e3927900a98eb.json`
- suite ZIP: `/workspace/artifacts/v536-verification-managed/runs/b79bd18bbab6477c8d1e3927900a98eb.zip` · 41,992,673 bytes
- suite SHA-256: `6d02e866f129d3c0c73fa84e48e77a02effeda5f0e62cefaa0dedde2aceff23f`
- 실제 가시성 보강: `/workspace/artifacts/v536-verification-managed/runs/9929550591aa40f48a29708a38420cd4.json`
- 보강 증거 SHA-256: `769ae1f6eab680decbf5d50081e5d2a2863e5b8286e7fe41172b1edcea65c477`
- 최신 source: `a1e7d8cb87571ce34cde545c2c75c2cfac991b2d`
- 최신 ZIP: `1a8b7a702f276f5c2e750fa1060d1b41dc194116a6d0683ddb3fc995b8dc7de4.zip` · 51,861,663 bytes · 파일2475 / 디렉터리152
- 최신 전체 manifest SHA: `55687e03fe4ced8ecc906b3186492f34824a2c1d36bfac3f1d9c60c1552d5cac`
- 정상 롤백 source: `6c742c738ae975e267655f55a46476fe305df419`
- 롤백 ZIP: `c8f682fa06591ce2f5cc738b3909957c2d60d2d1235d5afe0ddb326051956dc4.zip` · 전체 manifest SHA `888684f51b84e392398dedf2887a5a4933ecfebce9e2f82309395022f7c30706`

패키지는 `/workspace/artifacts/v536-verification-managed/packages/`의 기존 index로 추적한다.
최신/롤백과 모든 증거의 전체 SHA/CRC·파일 mode manifest를 확인했다. 최신/정상 롤백 두 세대의
기존 원자 승격 규칙만 사용했고 과거 자료의 추가 삭제/보관정책 변경은 하지 않았다.
세 실행의 소유 RAM root는 모두 제거됐다.

suite 실행 디스크 순증가 41.54MiB, 재현·가시성 보강까지 단위 전체
순증가 77.43MiB, 측정 시 여유 1267.2MiB다.
suite 표본 최소 여유 1326.3MiB, peak memory 5050.9MiB.
최초160MiB 지속 공간 계획의64MiB 안전 여유를 유지했다. 이번 증거의 큰 부분은 계측 엔진
복사본에 함께 보존된 원본 UI 자산이다. 이후 단위의 증가량 보장으로 쓰지 않는다.

## 남은 한계

현재 수정은 **관측된 pending 도구 I/O**에서 passive 상세 갱신이 같은 잠금을 다시 기다리는
경로다. 일반 FileStream/사용자 C#·provider 대기·최종 파일 채택과 모든 경합 시점/디스크 지연/
전 UI의 비차단 성능을 완료로 표시하지 않는다. 초기화 간헐 빈 화면은 별개이며 원인 미확정이다.
V4/V5 실제 신원·권한/공유 adapter, V6/V7 자산 기반, Run HD/GPU/native·장치 오디오와
실제 Windows/모바일·전체 UI·Space/Library 전달은 기존 고정 잔여다. 새 권한·계약 변환·조합을
추가하지 않았고 M11/M12/M4 완료 범위를 다시 열지 않는다. main은 사용자 검토/merge용으로 보존한다.
