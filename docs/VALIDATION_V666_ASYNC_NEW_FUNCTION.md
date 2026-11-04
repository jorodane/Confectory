# v666 M4 새 전역 함수 · 최종 검증

제품 동결 `675599b81e5c7bf19a3d5a0fbba7796eb5c1b06d`를 `tools/verify_desktop.py --suite async-new-function`로 검증했다.
[지원 범위](M4_ASYNC_NEW_FUNCTION.md)는 새 전역 함수/구현/graph/코드를 첫 물리
Confirm 전에 명시 async 전환·편집·Save·전체 Review→Confirm하는 흐름이다.

**최종 본 검사 48단계와 컴파일 보완 3단계가 모두 신규 통과했다. 재사용 0.**
본 검사는 LF 21, CRLF 18, 새 패키지/전체 복원/실패
수명관리 9다. Core/runtime은 각
18 passed, 0 failed, 0 skipped이며 단계 수에 중복 가산하지 않는다.

## 확인한 사용자 흐름과 보호

- 기존 프로젝트 등록 원본 hash·namespace와 새 함수/구현의 ID·경로 부재를 확인했다.
  위조/누락 등록·기존 ID/경로 재사용·다른 소유/record·기존 body locator alias는 거절한다.
  동일한 정규 소유 경로는 허용하며 경로 탈출·별도 ID의 alias는 계속 거절한다.
- 새 전역 템플릿의 일반 값/out/object와 ref 보호를 확인했다. 실제 Task 인터페이스와
  세 typed 본문을 컴파일했다. 기존 Entry·소스 바이트·실행 결과와 ref forwarding은 유지한다.
  기존 legacy는 자동 변환하지 않는다.
- 생성 API의 새 네 파일은 Confirm 전 모두 부재한다. 첫 전환 계약·receipt를 cold에서
  복원하고 변조된 IO origin·등록 관측·부분 Review를 거절한다. int 본문이 비면 실제
  compiler Confirm이 실패하고 새 파일을 하나도 쓰지 않는다.
- 실제 UI의 Root/동작 메뉴·Undo/Redo·취소·cold·반복 Save·Review 취소/Confirm,
  저장 실패·상대 파일 충돌·응답 유실·늦은 새 입력을 검증했다. own receipt 조회는 중복
  쓰기를 만들지 않고 새 입력은 별도 명시 Save로 반영한다.
- Review 뒤 기존 manifest가 바뀌면 새 함수/구현/graph/코드 전체를 최종 CAS에서 거절한다.
  재시도 Confirm 뒤 새 함수는 명시 Entry 검증 복사본에서 await·stdout·반환값으로 실제
  실행했다. 원래 프로젝트의 Entry·C#·다른 데이터·실행 결과는 그대로다.
- 이전 새 leaf API·완료 adapter·원본/receipt/CAS·새 기능 대화상자도 신규 회귀했다.

새 Windows 교차 패키지의 구조/assembly 일치·UI·Task 실행을 확인했다. ZIP 전체 파일
SHA/CRC·mode/디렉터리 manifest와 RAM 전체 복원본의 늦은 입력·저장 실패·Task도 확인했다.
실제 Windows apphost/WebView2·모바일 기기 실행은 하지 않았다.

## 검사 보완과 출처

본 검사 진행 중 생성물을 확인하니 최초 템플릿 smoke는 Entry가 호출하지 않는 함수를
planner가 제외해, 그 세 본문을 실제 컴파일했다는 근거로 사용할 수 없었다. 검사를
`always`로 강제 포함하고 생성 C#에 세 원문이 모두 존재하는지 단언하도록 보강했다
(`65bb1c2faaa4aaf85450d93341f4badf87070908`, 검사 파일만 변경).
**동일 제품 assembly의 독립 LF/CRLF 빌드와 지속 ZIP의 전체 복원본에서 보완 검사를
각각 신규 실행해 모두 통과했다.** 최초 smoke를 본문 컴파일 근거로 대신 세지 않는다.

- LF record `0cdf4eae5aa34415aa4850d1d35c78d6` · 증거 SHA256 `dd5f1092296b95ddcc7ddb5d9bb3ba8a64e342e20204da9550e0b043cf24be7f`
- CRLF record `cd4e6c6de0ec406f8a04c702a0bc0fe6` · 증거 SHA256 `3465afb3bbc297c47339d3fd0442e4bbd9fee1f512300c9fe9fee0bf3e1d3c7e`
- 지속 ZIP 전체 복원본 record `92ee14f198544130965d370116558050` · 증거 SHA256 `ca887329cfe07253a7d7783192f553ed44fe9028eabe59e34f7081f4e53438d6`

보완 fixture의 초기 Python 문자열 오류는 제품 실패와 구분하여
`34f0bce95b7f4f819165b85b1187401b`에 보존했고, 수정 후 위 검사들을 통과했다.
개발 record `7274d8c8e0844b069cac14d1947227d2`의 API·정상/늦은 UI·소유/IO/경로
검사도 보관했으며 최종 단계 수에는 더하지 않는다.

보관 패키지의 실제 source는 제품 동결 commit이다. 게시 후속은 보완 검사 파일·문서만
다르며 `src/targets/examples/packs/tools` 차이는 없다. 패키지 출처를 게시 HEAD로
바꾸거나 실행하지 않은 재빌드를 주장하지 않는다.

## 지속 보관과 공간

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/2d9428ffdac44d8b94442ac8ce36e460.json`
- 전체 증거 `/workspace/artifacts/v536-verification-managed/runs/2d9428ffdac44d8b94442ac8ce36e460.zip` · SHA256 `c3031a064d0e8acf949954325019d2fabe26937ad447d0cb03da95864e7212fa` · 4,604,064 bytes
- 최신 source `675599b81e5c7bf19a3d5a0fbba7796eb5c1b06d` · ZIP `f7e7d18804b0b8a7095e2530fbb1decd01c82742de71ade1b00b35c021a962bf` · 51,487,152 bytes
- 전체 manifest `78cf2b1abfa15655c4ed07b07c178e28be1608c6332af3c3adedcf631ff40127` · 파일 2,378/디렉터리 147
- 정상 rollback `981d28824aa91eeca03a8a5881e3be52c116affd` · ZIP `3637d9fa0c7702dfdaf57e3732be61747ad1a1e04870c88240d1944575441c7f` · manifest `3703c16e0e6bba9e58fc6c5f719af5e545695ce7f96b2b7388584ff670bf5622`
- 본 검사 실행 전 1746.8 MiB, 본 검사/보완 검사 종료 1740.7 MiB, 본 stage 중 최소 1746.4 MiB.
  전체 작업 순증가 8.0 MiB; 다음 단위의 고정 증가량 보장은 아니다.

최신/rollback을 원자 승격하고 전체 증거를 지속 보관한 뒤 이번 실행들이 소유한 임시
checkout·캐시·패키지·복원본만 정리했다. 본 임시 root 제거 `True`.
안전 여유 64 MiB를 낮추거나 다른 기존 자료를 삭제하지 않았다.

## 유한한 잔여

정보 소유 함수의 생성/slot 배정, private/internal Task 경계와 첫 생성 Save 전 입력
결합은 실제 잔여다. 이 단위의 `creationOwner` 거절을 영구 UX 정책으로 정하지 않는다.
기존 override IO·부모/참조/외부 source 보호와 미전환 동기 caller 오류를 유지한다.
M11/M12는 마감 상태를 유지한다. 고정 V1 검증 잔여/V2–V9·팩/backend·종류 호환성,
실제 기기·전체 UI·Space 전달은 별도 미완료다. main은 사용자가 검토·merge한다.
