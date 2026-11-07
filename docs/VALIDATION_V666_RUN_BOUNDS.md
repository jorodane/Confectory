# v666 Run 요소 경계 최종 검증

[지원과 한계](V8_RUN_BOUNDS.md) · [닫힌 제품 delta](v666-run-bounds-delta.json).
제품/검사/도구 동결 `6c742c738ae975e267655f55a46476fe305df419` 이후는 문서만 변경했다.
**최종 50단계: 신규 50 · 재사용 0**. LF 21 · CRLF 21 · 패키지/전체 복원/수명관리 8.
독립 Git 객체·NuGet/home·빈 엔진 cache/출력을 사용했다.

- 실제 RunSurface/FrameControl의 동일 사용자 인증 pipe에서 최대 1MiB 픽셀과 16개
  경계·resize·rate가 기존 packet 예산 안에 들어감을 확인했다. 호출자 배열의 사후 변경은
  발행본을 바꾸지 않았다. 잘못된 좌표/개수/픽셀은 기존 revision·픽셀·경계를 보존했다.
  기존 Present의 명시적 opt-out, 빈 scene, 소유/크기/수명과 기존 오디오를 포함해
  각 LF/CRLF에서 native 5개 사례가 통과했다.
- 실제 native parser는 음수/범위 밖/불완전/소수/초과 개수/잘못된 좌표 공간/누락을
  거절했다. 같은 프레임의 경계 변경·소실도 거절하고 이전 유효 기준을 보존했다.
  private 추가 필드는 제거했으며 새 legacy 프레임은 경계를 생략할 수 있었다.
  거절 검사는 생성한 malformed producer, 정상 픽셀 검사는 실제 RunSurface 예제를 사용했다.
- 실제 사각형 안/밖의 RGBA와 전체 SHA가 발행 좌표와 일치했다. 반복 관측은 heartbeat를
  연장하지 않아 실제 owner가 lease 만료로 멈췄으며 foreign view/lease/handle을 거절했다.
- 원본 개발 메뉴의 경계 체크박스, 점선 accent, 실제 contain/letterbox 정렬과
  pointer-events:none을 확인했다. On/Off·좁은/넓은 viewport·sibling 선택 격리,
  명시 Step 한 번·Stop·cold 및 입력 보존을 검증했다. 실제 생성 프로젝트의 두 사각형과
  경계가 맞는 스크린샷도 직접 확인했다. 모의 scene이나 GPU 렌더 완료 증거로 쓰지 않는다.
- browser-only 좌표 변조는 오래된 픽셀/경계를 제거하고 실제 owner의 frame/Start를
  바꾸지 않았다. 다음 유효 관측에서 새 입력을 유지하며 복구했다. 실제 읽기 응답을
  보류하고 창을 닫은 뒤 해제해도 sibling에 그리거나 publisher/Start를 되살리지 못했다.
  cold는 개인 창/입력만 복원하고 geometry/선택/publisher를 presentation에 저장하지 않았다.
- 기존 최대 픽셀·SHA·순서, FPS의 실제 성공 발행/일시 정지/Step,
  해상도·ACK/새 입력/닫기·그리드·출력 없는 레거시 개발 메뉴를 새로 회귀 검사했다.
  기존 C#·공개 Invoke/override·오디오·FrameControl·transport·권한과 원본 레이아웃은
  닫힌 source delta로 보존했다. 기존 source 저장/Review→Confirm/CAS 코드는 바꾸지 않았으며
  모든 편집기 저장 UI를 이번에 다시 검증했다는 뜻은 아니다.
- 새 Windows 교차 패키지의 구조·누락/변조 거절과 관리형 엔진 실행을 확인했다.
  ZIP 전체 SHA/CRC·전체 파일과 디렉터리 mode 복원 뒤 같은 실패/닫기/cold 및 그리드를
  검사했다. 정상/실패/예외 수명관리와 증거 보존·자식 종료·소유 임시물 정리도 통과했다.
  Linux 관리형 엔진/Chromium 자동화이며 실제 Windows apphost/WebView2·모바일 검증이 아니다.

최종 선택 검사 50개는 모두 새 실행이다. 이전 UI/저장 검증은 이 범위 밖의 기존 증거이며
신규 50개에 합산하지 않았다. 첫 projection 검사의 부동소수 연산 순서 차이는 검사 허용 오차
1e-12로 고쳤고 제품 좌표 변환은 바꾸지 않았다. 첫 독립 LF 편집기 빌드는 신규 manifest의
개행 때문에 C# 한 줄 raw string이 깨져 실패했다. 원래 한 줄 형식으로 수정한 뒤 최종 전체
50개를 다시 통과했다. 실패 기록도 보존하며 실패를 통과 수에 포함하지 않는다.

## 증거와 지속 보관

- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/bc04fb3c64f6428a817aedf97f0c28e4.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/bc04fb3c64f6428a817aedf97f0c28e4.zip`
- 증거 SHA-256: `f43c64e39ae974596198c43a9f50d61f5dd2a155c0ff41f3dcd7c4cae5043fb3`
- 앞선 빌드 실패: `/workspace/artifacts/v536-verification-managed/runs/4b38c1e5fcaf46bba08be01614038f87.json`
- 최신 source: `6c742c738ae975e267655f55a46476fe305df419`
- 최신 ZIP: `c8f682fa06591ce2f5cc738b3909957c2d60d2d1235d5afe0ddb326051956dc4.zip` · 51,862,936 bytes · 파일 2475 / 디렉터리 152
- 최신 전체 manifest SHA: `888684f51b84e392398dedf2887a5a4933ecfebce9e2f82309395022f7c30706`
- 정상 롤백 source: `bbf1370dbe28f2416ffe973f72ef29bd0f66703a`
- 롤백 ZIP: `456a92006dcca36f18d2cef361f2e05fa6ca9371975eade773d0c014f16a6222.zip` · 전체 manifest SHA `d9928b4bb41c82ff5419cbc3a66879ee083a028c610026f946904c25c8053c9e`

패키지는 `/workspace/artifacts/v536-verification-managed/packages/`의 기존 index로 추적한다.
최신/롤백 모두 전체 SHA/CRC와 파일/권한 manifest를 재확인했다. 기존 최신본을 정상 롤백으로
유지하고 검증된 후보만 원자적으로 승격했다. 해당 실행 소유 임시 root는 제거됐으며
과거 보관 자료의 추가 삭제는 하지 않았다.

최종 실행 디스크 순증가 2.95MiB, 이번 checkpoint 전체 순증가
4.73MiB, 증거 봉인 뒤 여유 1344.7MiB다.
단계 중 최소 여유 1347.5MiB, 관측 peak memory 4767.4MiB.
최초 160MiB 지속 공간 계획 안에서 64MiB 안전 여유 조건을 유지했다.

## 고정 잔여

초기화 간헐 빈 화면은 원인 미확정으로 유지한다. 진행 중 OS I/O의 UI end-to-end,
HD 이상/GPU/native Window 출력·하드웨어 FPS·장치/다채널 오디오와 실제 기기/전체 UI/
Space 전달은 완료하지 않았다. 자동 scene 탐지 같은 새 조합을 필수 잔여로 추가하지 않는다.
M11/M12/M4의 완료 범위는 이번 표시 기능 때문에 다시 열지 않는다.
