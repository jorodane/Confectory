# v666 M4 정보 소유 함수 · 최종 검증

제품 동결 `4b18f79236e6380669821ec30663d7448f50eb54`를 `tools/verify_desktop.py --suite async-information`로 검증했다.
[지원 경계](M4_ASYNC_INFORMATION.md)는 기존 소유 정보의 자체 함수 생성·단독 배정·첫
구현/graph/C#을 물리 Confirm 전에 async 전환하고 전체 저장·확정하는 흐름이다.
다른 곳의 요구/참조 계약이나 공개 override IO를 바꾸는 권한을 추가하지 않는다.

**최종 51단계 모두 신규 통과, 재사용 0.** 독립 LF 22,
CRLF 20, 새 교차 패키지/전체 복원/실패 수명관리 9다.
Core/runtime은 각 18 passed, 0 failed, 0 skipped다. 개발 검사를
최종 수에 더하거나 과거 Core 검사를 신규로 계산하지 않는다.

## 확인한 흐름

- 정보 원본 hash·정확한 contain/provide·단독 구현과 새 함수/구현 등록/경로 부재를
  검증했다. 잘못된 owner·공유 구현·누락 contain·위조 원본·잘못된 creator·원본 ID
  재사용·관계없는 생성 그룹을 거절한다. 별도 Confirm한 자체 함수의 첫 구현 증명도
  순수 guard로 확인했다. 모든 타입/문맥의 UI 조합을 검사한 것으로 확대하지 않는다.
- 생성 그룹 전체와 첫 IO·정보 owner·물리 `missing`/원본 읽기 조건을 같은 receipt와
  checkpoint/CAS에 보존한다. 새 파일 없이 Save/own receipt 반복 조회/cold가 가능하다.
- 실제 API에서 부분 Review와 Review 뒤 정보 원본·프로젝트 등록 변경을 전체 거절했다.
  재시도 Confirm 뒤 같은 정보 scope의 명시 async Blueprint caller가 실제 await·stdout·
  반환값으로 실행했다. 원래 Entry/CRLF C#·다른 파일과 정보의 나머지 값은 그대로다.
  미전환 동기 C# caller의 비동기 진입은 실제 compiler가 거절한다.
- 실제 UI에서 기본/독립 정보 창의 Root/동작 메뉴, Undo/Redo·취소·반복 Save·코드 편집,
  저장 거절/새 경로 충돌·응답 유실·늦은 입력·여러 cold·전체 Review 취소/Confirm과 실제
  실행을 확인했다. own receipt 조회는 중복 저장하지 않고 늦은 입력은 다음 명시 Save로
  보존한다. 권한/현재 owner/view binding·원래 핀/ID/연결·공개 계약을 보존한다.
- 기존 전역 함수의 생성/Task·값/out/object 실제 컴파일, 완료 어댑터/receipt와 일반
  정보 자체 함수 생성/최종 CAS도 영향 회귀로 신규 확인했다. 템플릿은 `always` 포함과
  생성 원문 단언으로 실제 컴파일했다.

새 패키지와 전체 ZIP 복원본의 실제 에디터 UI·Task를 검사했다. 전체 파일 SHA/CRC·mode·
디렉터리 manifest와 원본 assembly 일치를 확인했다. 이는 Linux에서 실행한 관리 코드와
Windows 교차 패키지 검증이며 실제 Windows apphost/WebView2나 모바일 실행이 아니다.

## 발견·수정 및 검사 준비

서버 구현 뒤 최초 실제 UI에서는 정보 본문의 단일 `async-plan`이 기존 순차 입력 분기로
빠져 입력 보존 오류를 냈다. 서버가 확인한 직접 소유 정보 capability와 단일 async/
completion 입력에만 공통 원자 배치를 연결했고 pinned JS 자원 식별자도 갱신했다.
최종 source에서 해당 실제 UI를 모두 신규 검사했다.

초기 fixture는 cold 뒤 정보 재선택이 빠졌고, 실행용 caller에 async 표시만 붙여 기존
native C# 보호 규칙에 걸렸다. 각각 명시적 선택과 명시 async Blueprint caller로 고쳤다.
창 겹침으로 가려진 포인터 검사도 실패 기록을 보존했다. 최종 UI fixture는 입력 전에
본문 창만 실제 제목 드래그로 빈 공간에 배치한다(2600×1800, 배율 100%, 카드 크기 유지).
제품 레이아웃을 바꾸거나 강제 클릭으로 저장/권한 검사를 우회하지 않는다.

개발 record `c5506345d903444a8bd254951a5a0712`, 증거 SHA256
`5878fab5159ad4eec64e89bba9f602671d9535da0d70ebb1fe22fb4e403bb672`에 실패/수정·입력·
로그·이미지·정상/독립 창·실행 근거를 보존했다. 개발 검사는 최종 단계 수와 분리한다.

## 출처·지속 보관·공간

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/61075ed9e6624649ab354bddfc028f86.json`
- 전체 증거 `/workspace/artifacts/v536-verification-managed/runs/61075ed9e6624649ab354bddfc028f86.zip` · SHA256 `6ed863668d9ac49848731b4b63da3da3ab7e03957c88bd2d0d24627bb2da4454` · 6,293,593 bytes
- 최신 source `4b18f79236e6380669821ec30663d7448f50eb54` · ZIP `4ce1a0bf8ef2b4ea14df85015ad7ac1f899ae44e60290da6c97e82bcd8a8daba` · 51,492,547 bytes
- 전체 manifest `778ed53a5fa5cae6e1966f60d89b4667336b0d63d23cbe8dd227340bdf64cdab` · 파일 2,379/디렉터리 147
- 정상 rollback `675599b81e5c7bf19a3d5a0fbba7796eb5c1b06d` · ZIP `f7e7d18804b0b8a7095e2530fbb1decd01c82742de71ade1b00b35c021a962bf` · manifest `78cf2b1abfa15655c4ed07b07c178e28be1608c6332af3c3adedcf631ff40127`
- 최종 실행 전 1734.8 MiB, 종료 1727.6 MiB, stage 중 최소 1734.7 MiB.
  전체 작업 순증가 13.0 MiB; 다음 단위의 고정 증가량 보장은 아니다.

전체 증거·최신/rollback을 원자적으로 보관한 뒤 각 실행이 직접 만든 checkout·캐시·
패키지/복원본만 정리했다. 본 임시 root 제거 `True`. 기존 과거 자료는
삭제하지 않았고 64 MiB 안전 여유를 낮추지 않았다. 게시 후속은 검증 기록 문서만
다르며 패키지 source를 다른 HEAD로 표시하지 않는다. main은 사용자 검토/merge 영역이다.

## 유한한 잔여

M4의 직접 소유 private/internal Task 경계와 첫 생성 Save 전 입력 결합이 남는다.
새 정보 컨테이너와 결합 첫 입력도 같은 생성 경계에 속하며 별도 조합 행을 늘리지 않는다.
비소유 참조/부모 쓰기·override IO 변경·선택적 legacy 자동 migration은 미구현 요구가 아니다.
M11/M12는 마감 상태다. 고정 V1 검증/V2–V9·기존 ABI/고급 타입/표시명·팩/backend·종류
호환성 및 실제 기기/전체 UI/Space 전달은 별도 잔여이며 이번 단위 완료와 구분한다.
