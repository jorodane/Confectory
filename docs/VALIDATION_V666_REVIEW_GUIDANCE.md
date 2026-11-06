# V666 검토·확정 안내 검증

제품·검사·도구 동결 `6033c5eb0bfffad4733527fefa3c272e24e07e57` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V2_REVIEW_GUIDANCE.md)와 [19개 문구/24곳 허용 목록](v666-review-guidance-copy.json)을 따른다.
보관 v666 `dist/app.js:3484`의 안내 문체를 native Review→Confirm에 대응하며 demo의
객체 저장/권한 의미는 채택하지 않는다. 검토 준비와 최종 반영·실패를 구분한다.

## 실제 지원과 보존

남아 있던 영어 완료 안내·구어체와 전후 소스 제목을 바꿨다. 검토 선택 안내는 같은 객체
변경의 묶음 선택과 Confirm에서만 최종 소스를 반영함을 명시한다. source-ready를 자동
승인하거나 compiler/CAS/거절 의미를 바꾸지 않는다. 제품 변경은 v508-runtime.js의
정확한 문자열·runtime.css의 canvas 쌓임 분리 한 곳·WebBundle의 canonical 크기/SHA
세 파일이며, 나머지 JS 실행 코드·선택자/HTML 구조·나머지 CSS/기하 레이아웃·
Core/targets/packs·C# bytes/ID/공개 및 override 계약·
부모/외부 원본·권한·Review token/target·원자 저장·최종 CAS·입력 수명·Undo는 그대로다.
backend 원문 진단/오류 코드와 동적 값은 번역하지 않는다.

## 재현된 반복 검토 계층 결함

최초 LF native 검사에서 반복 Review의 고급 검토 클릭을 Blueprint 포트가 가로막았다.
canvas 내부의 증가하는 포커스 값이 고정 플로팅 부모 80을 넘어선 제품 결함이었다.
배포 CSS의 동일 기하 fixture에서 이전/수정 후 hit target과 픽셀을 확인했고 canvas만
`isolation:isolate`로 분리했다. 포커스 81/1000/100000·재클릭·viewport 변경을 검증했다.
전역 z-index 숫자를 임의로 높이거나 force click으로 회피하지 않았다. 실패 단계와 개발
fixture는 별도 보존하며 최종 통과 합계에 넣지 않는다. 최종 CSS가 바뀌어 독립 빌드와 관련 UI는
새로 검사했다. 이어진 CRLF late Task에서 첫 생성 저장과 늦은 새 C# 저장이 정확히
한 번씩 이루어졌으나, 검사 횟수 단언이 information 문맥에서만 두 번을 허용해 멈췄다.
제품 변경 없이 late의 별도 source Save 두 번을 검사하도록 수정했다. 서로 다른 attempt,
단 한 번의 async 전환, 두 번째 source-only 편집·정확한 새 본문 보존 단언은 유지한다.
이 검사 실패와 통과한 나머지 단계의 증거를 구분해 보존한다.

## 최종 검사

독립 LF 13·CRLF 15·새 패키지/전체 복원/실패 수명관리 7,
**총 35단계(신규 32·재사용 3)** 통과했다. Git 객체와 EOL,
NuGet/home·엔진 cache를 독립시켜 최종 동결 코드를 새로 빌드했다. 재사용은 `d1ed0f4`의
성공한 LF/CRLF 검토 UI와 LF normal Task 세 단계에만 한정한다. 제품·SDK/NuGet·검사
호출을 봉인된 증거와 대조하고, fixture 변경은 늦은 입력의 두 번째 별도 source Save
횟수 단언 한 곳뿐임을 확인한다. 실패 단계와 새 패키지/전체 복원은 재사용하지 않는다. 이번 변경에 무관한 전체 테스트는 재실행했다고 하지 않는다.

- 실제 Linux .NET/Chromium에서 변경 안내·전후 소스와 빈 선택 거절을 확인했다.
  재선택 뒤 고급 검토 확인이 초기화되어 Confirm이 차단되고 명시 확인 뒤 허용됐다.
- 실제 compiler Confirm의 CS0103와 심볼 원문을 보존하고, 실패한 원본·checkpoint를
  바꾸지 않았다. 검토 취소·반복, 물리 원본 변경 후 최종 CAS 거절, 복구 뒤 새 검토와
  명시 Confirm·실제 C# 실행을 확인했다. 저장 실패/cold와 코드 Undo/Redo도 확인했다.
- stale admission의 단순 재시도와 revision/text/선택/project/target 변경 후 재시도 거절은
  실제 production 함수를 추출한 로컬 projection 검사다. native UI 검사와 구분한다.
- 기존 첫 생성 Task의 정상 및 늦은 응답/cold/재시도·명시 async caller 회귀와 CRLF의
  독립 선언 재조회/취소/입력 버리기 및 Run 최대화 회귀를 실행했다. 새 정책을 추가하지 않았다.
- 새 Windows 교차 패키지 구조·무결성, 패키지 엔진의 검토/확정과 전체 SHA/CRC/모드
  복원본의 저장 실패·검토/확정·늦은 Task 응답을 확인했다. 이는 Linux에서 packaged
  managed engine을 실행한 것이며 실제 Windows apphost/WebView2 실행이 아니다.
- 생성한 fixture·로컬 주입을 사용했다. 실제 계정/AI/키·유료 호출·외부 권한 부여는 없다.
  실패/예외에서도 증거 보존·자식 종료·소유 임시물 정리 수명을 확인했다.

최종 record `/workspace/artifacts/v536-verification-managed/runs/aa76cc0a60dc4e65a325c63556febd88.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/aa76cc0a60dc4e65a325c63556febd88.zip`

SHA `5822a83491986d8f95d36d32fdc3dc7afacad80dfe7aec484f90508a0c093b79` (3.20MiB).

## 보관·공간·고정 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

별도 실패/개발 record `/workspace/artifacts/v536-verification-managed/runs/24b9f8337679426ea94a92949e0691bc.json`, 증거 SHA `6ec910cb704756565e7ff85a1a225ae5a52e54b687baafbf738c2de7589f4d17`.

별도 실패/개발 record `/workspace/artifacts/v536-verification-managed/runs/6edd784256dd49fa966c7fa3eb78818b.json`, 증거 SHA `058000ad3d6d95a9be4f38fb5f908544f8f0c2ed111fdd2b201bba739abe8d2b`.

별도 실패/개발 record `/workspace/artifacts/v536-verification-managed/runs/857f8d8983744e9e96bb3fecadd5056d.json`, 증거 SHA `7fbe64c4b9302abc5257fdeddf317292072d5c763da0bf3a4b61e55ae09ff001`.

- latest: `6033c5eb0bfffad4733527fefa3c272e24e07e57`, `b4ebc2e6a2efc61432ac9ac275e68f84c056a96ecb501cd8a68f56cd10a50046.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `68597e2752695cd08ba57fe5fc3cf7b3b57d4c590366a8ecd55d9c3beb057978`.

- rollback: `ed0575776752d51bef6b8a7f3bcda0e06e6ca59b`, `9855adba833598d15ddfaec8674e6080fa6546b5ffa56c0cb833d9f301493b0e.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `3a20d65be2adcb009b96e606d8ce1376692e6a74acb7a591ab29d3218c2c11eb`.

두 보관본과 증거의 전체 SHA/manifest를 확인했다. 기존 승인된 저장소의 원자 승격·2세대
수명만 적용했고, 해당 실행이 만든 임시물은 소유/자식 종료 확인 뒤 정리했다. 다른 과거
자료·원본·로그·프로필·SDK/캐시 추가 삭제나 보관정책 변경은 없다.

표본 최소 디스크 여유 1429.48MiB, 최대 cgroup 메모리 5089.77MiB.
최종 실행 순증가 4.04MiB, 단위 시작부터 보관 확인까지 6.54MiB,
문서 마감 전 여유 1425.49MiB. 이후 증가량은 보장하지 않는다.

이 단위는 V2의 실제 검토·확정 안내다. 다른 V2 노출 안내와 V1 검증 잔여·V3–V7 팩/backend·
V8 실제 내장 surface/audio·V9 실제 신원/가시성·종류 C# 표현/사용중 삭제 대응은 기존
고정 잔여다. Run 제어 IPC·RenderInput Draw/Pump는 렌더/오디오 전달 provider가 아니다.
현재 DISPLAY/Wayland/Xvfb·오디오 장치와 provider가 없어 모의 성공으로 채우지 않았다.
실제 Windows/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 미완료다.
M11/M12/M4는 구체적 회귀 없이 재개하지 않고, 3D/권한 별도 팩·이동 연출/실행 분리·
명시 async caller 합의를 유지했다. main은 보존하고 work/current만 게시한다.
