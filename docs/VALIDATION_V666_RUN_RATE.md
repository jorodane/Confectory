# Run 소프트웨어 출력 FPS 검증

[지원·한계](V8_RUN_RATE.md) · [제품 delta](v666-run-rate-delta.json).
코드/검사/도구 동결 `bbf1370dbe28f2416ffe973f72ef29bd0f66703a` 이후는 문서만 변경했다.
**최종47단계: 신규42 / 동등 근거 재사용5**. LF20 · CRLF19 · 패키지/전체 복원/수명관리8.
독립 Git 객체·NuGet/home·빈 엔진 cache/출력과 기존 관리형 임시 공간을 사용했다.

- 실제 RunSurface/FrameControl과 CurrentUserOnly 인증 pipe에서 성공한 Present7회를
  세고 거절된 Present와 반복 조회가 수를 늘리지 않음을 확인했다. 협력 제어 frame/ACK는
  0인 상태에서도 발행은 집계됐으며, 실제 대기 후0으로 감소하고 새 publisher는 새 관측을
  시작했다. 별도 private state를 읽는 test double 없이 실제 출력 팩을 실행했다.
  기존1MiB/640축·면적/정규화·소유/resize·오디오 검사를 합해 native4개가 통과했다.
- 실제 native parser는 관측 순서·같은 관측의 변조·불가능한 수/구간·준비 역행·소실·
  canonical/missing 필드를 거절했다. private 추가 필드를 제거하고 새 legacy publisher를
  읽되 retired publisher는 거절했다. 이 변조 case의 출력 callback은 생성한 test producer다.
  정상 계측과 heartbeat 검사는 실제 RunSurface의 성공 발행을 사용했다.
- 반복 영상/rate 읽기는 metadata lease·ACK를 갱신하지 않았다. 실제 협력 owner가 lease
  만료로 멈춘 후 집계도0으로 줄었다. foreign view/lease/handle은 거절했다. 원래 SHA/픽셀/
  크기/순서·최대1MiB 프레임과 레거시 packet guard도 새로 통과했다.
- 실제 Run UI에서 성공 발행의 FPS, 일시 정지 후0, 명시 한 번 Step의 일시적 집계와
  다시0, Stop/새 Start·cold를 확인했다. unchanged 진단은 같은 pixels를 재사용하며
  실제 canvas putImageData 호출이 늘지 않았다. 원본/권한/실행 계약·새 chat 입력을 보존했다.
  실제 생성 프로젝트의 화면도 확인했다. 소프트웨어 출력60.4fps·최근927ms와 누적 제어71의
  한 관측은 서로 다른 값으로 표시됐으며 성능/하드웨어 보장값으로 쓰지 않는다.
- browser-only 잘못된 rate 응답 주입은 오래된 숫자/영상만 제거했고 실제 owner를
  중단/재시작하지 않았다. 다음 실제 관측은 새 입력을 유지하며 복구했다. 실제 읽기 응답을
  보류한 뒤 창을 닫고 해제해도 sibling의 숫자/owner/Start를 바꾸지 못했다.
  cold는 개인 창/입력만 복원하고 presentation에 rate/publisher 샘플을 저장하지 않았다.
- 기존640×360/preset·영역 제한·stale/foreign·잃은 응답/새 입력·닫기·cold와 실제 그리드
  정상/실패 수명, 계측 없는 기존 프로젝트의 FPS 미지원·제어/ACK 진단을 회귀 검사했다.
  prototype RAF·브라우저 poll·제어 frame을 FPS로 환산하거나 사용자 C#을 재작성하지 않았다.
- 새 Windows 교차 패키지의 구조/전체 SHA·누락/변조 거절과 관리형 엔진 실행을 확인했다.
  ZIP 전체 SHA/CRC·파일/디렉터리 mode 복원 뒤 FPS 실패/닫기/cold와 그리드를 검사했다.
  성공 반복·복사/UI 실패의 증거 보존과 소유 임시물 정리도 통과했다. Linux 관리형 엔진/
  Chromium 자동화이며 Windows apphost/WebView2·모바일/물리 GPU·오디오 검증이 아니다.

LF의 boundary·rate/RGBA/legacy 진단 projection3개·native4-case 묶음, 총5단계만
봉인된 직전 통과 결과에서 재사용했다. 제품·선택 검사·명령과 SDK/NuGet/구성/대상은
동일하며 차이는 독립된 fault producer의 base64url 인코딩 수정 한 파일뿐임을 Git으로
확인했다. 전체 증거 SHA/CRC·manifest와 해당 결과/명령을 대조했다. 실패한 API 검사,
빌드/패키지는 재사용하지 않았다. CRLF와 새 패키지/전체 복원은 모두 신규다.

최종 기록 `/workspace/artifacts/v536-verification-managed/runs/1c3e2e8b1056483899614a2a94f31ceb.json`.
증거 ZIP `/workspace/artifacts/v536-verification-managed/runs/1c3e2e8b1056483899614a2a94f31ceb.zip` · SHA256 `58ec5e69faa82dad31075fcd1a602e2094ca4ed8c7cf4c3f28fef4d51e57d0fc` · 2013830bytes.
전체 manifest/CRC/파일 mode와 실행 소유 RAM root 제거를 확인했다.

| 역할 | 출처 commit | ZIP SHA256 | bytes / files / dirs | 전체 manifest SHA256 |
|---|---|---|---|---|
| latest | `bbf1370dbe28f2416ffe973f72ef29bd0f66703a` | `456a92006dcca36f18d2cef361f2e05fa6ca9371975eade773d0c014f16a6222` | 51856790 / 2471 / 152 | `d9928b4bb41c82ff5419cbc3a66879ee083a028c610026f946904c25c8053c9e` |
| rollback | `89337ae84959a5f7200acf56e32e41968ec36cac` | `6c3b07935b44e180eb956672993f56f0dbc99d8b53a26f78469b45975b9608c4` | 51855586 / 2471 / 152 | `262108c2535f7b7e7bbbb4495850f878d34f0067550c79c3c7b924cfae05f4cd` |

승인된 managed 최신/직전 검증본2세대 승격과 자체 임시물 수명관리만 사용했다. 과거 자료·
원본/SDK·사용자 데이터·기존 로그/프로필은 추가 삭제하지 않았다. 계획160MiB(안전64MiB 포함),
RAM3GiB+512MiB·추가 메모리7GiB+1GiB 기준을 유지했다.
최종 실행 순증가 2.85MiB, 단위 순증가 4.71MiB, 측정 여유 1349.50MiB,
단계 표본 최소 여유 1352.22MiB, peak 메모리 4755.32MiB다. 이후 증가량의 보장값이 아니다.

집중 실패 기록 `/workspace/artifacts/v536-verification-managed/runs/71cd6de0415446c8858532c301664f43.json` · SHA `457c16490d9757ce0b8682c31388ee5f543539132bb0a1a9920769f8034ecb97`를 보존했다.
native4-case와 projection/boundary는 통과했으나 생성한 API fault producer가 표준 base64의
슬래시를 base64url로 바꾸지 않아 픽셀이 먼저 거절됐다. 제품의 올바른 거절과 fixture 오류를
구분하고 인코딩만 고쳤다. 최종47단계에 실패/개발 검사를 중복 합산하지 않았다.

이번 마감은 명시 소프트웨어 producer의 발행 빈도다. 보고된 발행의 형식/순서 검증이며
임의 출력 구현 내부의 성능 attestation이 아니다. GPU/모니터 표시 FPS·요소 경계·HD 이상·
물리 오디오, 진행 중 OS I/O/공유 잠금의 전체 UI, 신원/권한·자산/참여자/대화와 실제 기기·
전체 UI·Space/Library 전달은 기존 고정 잔여다. 초기화 간헐 빈 화면의 직접 원인은 미확정으로
유지한다. M11/M12/M4를 다시 열거나 새 조합/자동 migration을 필수로 늘리지 않았다.
라이브 AI/자격증명·과금·새 외부 grant·main 변경은 없다.
