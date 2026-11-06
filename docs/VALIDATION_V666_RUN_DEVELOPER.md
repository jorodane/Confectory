# V666 Run 개발 메뉴 검증

코드/검사 동결 `81b6dbcfb8d28b3049010e0ec0725de3da5a6c48` 이후 마감은 문서만 변경했다.
[지원 경계](V8_RUN_DEVELOPER.md) · [제품 변경 허용 목록](v666-run-developer-delta.json).
최종 **36단계: 신규 36 / 재사용 0** 통과.
LF 14 · CRLF 14 · 새 패키지/복원/IPC·실패 수명관리 8.
독립 Git 객체·빈 엔진 캐시·독립 NuGet/SDK home을 사용했다.

- 원본 ZIP의 toolbar/popover/debug CSS 일치와 제품 3개 파일/리소스 전체 SHA·크기 검사.
  native Run 소유/lease/ACK와 공개·override 계약/권한/Review→Confirm/CAS·완료된 편집은 변경하지 않았다.
- 디버그 사실 함수의 큰 Int64 프레임·불변 값·미지원 표시, 오류/중단/연결 없음/잘못된
  counter에서 현재 값 숨김. handle/lease/runtime secret을 화면에 추가하지 않았다.
- 실제 관리형 엔진과 생성한 frame-loop 프로젝트의 Run에서 메뉴 반복 열기/닫기,
  디버그 선택, 실제 Pause와 한 프레임 Step ACK, 정확한 프레임/명령 관측, 명시 Stop.
  선택은 실행이나 source Confirm을 만들지 않고 해상도/영상 debug/audio 제어는 비활성이다.
- 최대화 위의 메뉴·Esc 순서, sibling 창의 표시 격리·입력 보존,390px viewport의 원본 메뉴.
- 실제 read 응답 유실로 현재 counter를 숨기고 명시 재확인으로 같은 handle을 회수했다.
  닫기 lease 거절 뒤 창·표시·프로세스·새 입력을 유지하고 재시도로 해당 창만 종료했다.
  폐기 callback은 새 창을 바꾸지 않으며 cold에서 개인 창/입력만 복원하고 실행하지 않는다.
- 기존 native Run backend 및 전체화면 정상/미지원/지연/소유 프로젝트·새 엔진/내보내기 메뉴 회귀.
- 새 Windows 교차 패키지 출처·구조와 패키지 엔진의 새 메뉴, 전체 압축 SHA/CRC/파일·디렉터리
  mode 복원과 복원 엔진의 실패/재시작·기존 내보내기, IPC socket/실패 증거 보존·정리.

검사는 Linux의 관리형 엔진·Chromium에서 실행했다. 실제 Windows apphost/WebView2·모바일·
하드웨어/DPI/IME·전체 UI·Space/Library 전달은 미검증이다. Run surface/render/audio backend와
V3 진행 중 IO를 완료로 세지 않는다. 라이브 AI·자격증명·계정/권한 변경·유료 호출은 없다.

기록 `/workspace/artifacts/v536-verification-managed/runs/cb9e425bc3464c8ab73f38d2ce9d4906.json`.
증거 ZIP `f86d756bc458e6c996352b6b731d576cd22d93a14086bf807ffdce57a4762ddd` (5200128 bytes).
전체 evidence manifest와 SHA/CRC를 검증했고 owned RAM 작업공간 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA-256 | bytes / files / dirs | 전체 manifest SHA-256 |
|---|---|---|---|---|
| latest | `81b6dbcfb8d28b3049010e0ec0725de3da5a6c48` | `63cc42c80e4aa7d9bbeb1e67310858a3dca8952862571515432ebfcfde910fa9` | 51785245 / 2405 / 150 | `aa2f3297d249b2e19c26bb781f81dc9e3eadc6436108bc058d7f87f66d1bf8be` |
| rollback | `cd56cbcfd63b0f2b0466fe811938e270af3e5161` | `e87f39cfd1793784d7aa5504cc81019817988d36fd39854e30b38799f8c263f5` | 51782570 / 2405 / 150 | `c268a33b02fb93aeaa1f9e032f5d829b45e59fd6ec53cf580f1d82bd50fca01f` |

`/workspace/artifacts/v536-verification-managed/packages/`에 최신/이전 검증 롤백을 기존 승인된
원자 승격으로 보관했다. 롤백은 새 개발 메뉴·예약 읽기 오류 보강 이전의 검증 기능 세트다. 과거 원본/패키지/로그/프로필/캐시/사용자 데이터는 추가 삭제하지 않았다.
추가 disk144MiB(안전64MiB 포함), RAM3GiB+512MiB와 메모리7GiB+1GiB 기준을 유지했다.
최종 실행 순증가 5.76MiB, 단위 전체 순증가 14.76MiB,
측정 시 여유 1451.44MiB. 검사 중 최소 여유 1457.16MiB,
peak 메모리 4612.96MiB. 이후 실행의 보장값이 아니다.

초기 응답 유실 검사에서 예약된 자동 읽기가 오류 상태를 덮을 수 있는 경로를 확인했다.
예약 callback의 오류 재검사를 추가했고, 최종 검사는 실제 응답 변조 counter와 두 번 이상의
기존 poll 간격 뒤에도 오류/재확인 표시가 유지되는지 확인한다.
그 뒤 닫기 검사에서 숨긴 document 창 제목 버튼 대신 실제 노출된 탭 닫기를 사용하도록
fixture locator를 바로잡았다. 이 수정은 제품 코드/레이아웃 변경이 아니다.

최종 통과에 합산하지 않은 이전 시도:
- `/workspace/artifacts/v536-verification-managed/runs/dd164150741346d28a36c021cccf34aa.json`: 25 통과 / 1 실패; SHA `35d3a1d46b533bc9c6d3fc0d7d0acf4d023ec0469542776bcc94fa88fcde8115`.
- `/workspace/artifacts/v536-verification-managed/runs/1c1d1a221aa04284aa3660c64e508a3a.json`: 25 통과 / 1 실패; SHA `3bc06bb80580988f567336cc40a39d5325d3bd5239b594cdb99b969be189f5f2`.
