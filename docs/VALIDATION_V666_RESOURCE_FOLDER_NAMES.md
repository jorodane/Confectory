# v666 자료 카테고리 이름 변경 검증

최종 동결 `bcdc0ba41fd849233c79bdce0ea27b9f65891060`에서 LF **18**, CRLF **18**, 패키지/전체 복원/수명 **9**, 총 **45단계(신규 43·재사용 2)**를 통과했다. 이후 게시 문서 외 제품/검사 입력은 바꾸지 않았다.

- 원본 ZIP의 `dist/app.js::resourceContextMenu/renameResourceInline`을 따른다. 카테고리 카드/계층의 이름 변경, 원본 인라인 입력·Enter/포커스 해제 확정·Escape 취소를 연결했다. 파일 이름 변경/삭제/내용 복구를 함께 추가하지 않았다.
- 독립 실제 DSL 소비자에서 이름 metadata 읽기 무부작용·새 이름/같은 ID·원래 topology/생성 receipt 보존·정확한 재시도·후속 이름/이동·오래된 요청/다른 command intent/알 수 없는 대상/외부 owner/잘못된 이름·실제 쓰기 거절/복구·변조 거절 등 **30개**를 확인했다. 기존 Layout 소비자의 **29개**도 각 checkout에서 새로 실행했다.
- production Layout/Request/Snapshot/CommitPlan/WriteAtomic/LeasePath 몸체를 추출한 통제 harness로 이름 저장의 성공, manifest·identity·파일 목록·기존 layout·이름 파일 CAS 경합, 실제 write 경계 실패 **7가지**를 검사했다. 매 경우 원래 topology·bytes/owner/제출 입력을 보존했다. 기존 topology 저장의 **6가지**도 새 이름 의존 관측을 포함해 실행했다. harness만으로 DSL wiring을 주장하지 않으며 독립 소비자와 실제 native UI가 별도로 검증한다.
- 정확한 이전 `9ff34ddd`의 Layout 몸체를 함께 컴파일해 새 이름 파일이 존재해도 원래 v1 이름/ID/계층을 읽고 기존 파일을 다시 쓰지 않음을 확인했다. 이름 변경은 새 `resource-folder-names.v1.json`만 쓰며 `resource-layout.v1.json`·`resources.v1.json`·import receipt·C#·공개/override 계약·부모/외부 원본/권한은 변경하지 않는다. old reader 몸체 SHA를 증거에 기록했다. 이전 UI는 새 이름 편집과 pending 입력을 지원하지 않는다.
- 실제 UI에서 Enter·blur·Escape, 열린 카테고리의 제목 경로/계층 갱신, 실제 이름 파일 쓰기 거절/같은 요청 재시도, 실제 native 성공 응답 유실/중복 없는 확인, 편집 기준 캡처 뒤 peer 이름 변경/새로고침 후 오래된 재시도 거절, 입력만 취소, 퇴역 Enter 콜백과 새 검색·다른 입력 보존을 확인했다.
- 실제 cold engine에서 미확정 이름/고정 기준을 복원하고 자동 저장 없이 Escape로 취소했다. 제출 뒤 응답 유실의 exact command 입력도 별도로 cold 복원해 명시 재시도로 같은 결과를 추가 쓰기 없이 확인했다. 같은 namespace의 다른 프로젝트는 A의 이름/입력을 복원하지 않으며 A로 돌아오면 원래 소유 상태만 복원한다.
- 기존 생성/중첩/이동/실패·원래 파일 import·텍스트 관측/미리보기 수명 회귀는 양쪽 checkout과 해당 package/전체 복원 경계에서 새로 확인했다. C# source 복구 UI 두 검사는 기존 통과 증거를 재사용했다. source/runtime/모델·계약·권한 primitive와 해당 fixture/SDK/NuGet/명령은 같으며 resource 창/endpoint를 만들지 않는 해당 입력에서는 새 코드가 실행되지 않는다. workspace-host의 차이도 새 resource 전용 private 필드 하나만임을 검증했다. 재사용을 신규로 세지 않는다.
- 새 Windows-x64 교차 패키지와 전체 ZIP 복원본에서 실제 native HTTP/Chromium UI를 실행했다. 전체 SHA·CRC·파일/디렉터리 모드·실패 수명/증거 보존을 확인했다. Linux에서의 교차 패키지 검사이며 Windows apphost/WebView2·모바일·전체 UI 실행은 아니다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/6951d8d33b234ceca13a4dfac0b764c7.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/6951d8d33b234ceca13a4dfac0b764c7.zip` · 2,826,226 bytes
- 증거 SHA: `78d1c41e199b0d4582d3f374ec7b61807546ac41d4728c0a539c32ffde91138b`
- 최신 source: `bcdc0ba41fd849233c79bdce0ea27b9f65891060`
- 최신 ZIP: `b6c949f4ecf8c07eb263ab01037a6ee22f672b714a31902e1ed769c664e968c3.zip` · 51,911,166 bytes · 파일2495 / 디렉터리153
- 최신 전체 manifest SHA: `8b6bd6ee7a1a1304ecc110a73de21709a1969caff0b8364e32f2726174ce9841`
- 정상 롤백 source: `61102a4eda29c0fbc1f5db99441d22558152b576`
- 롤백 ZIP: `2325c8c69406b37c7acd6ff2f43d8d1b77c06400dfac47f3810cbf5767a3b8b2.zip`
- 롤백 전체 manifest SHA: `246bafaf60da0dbe7a9215e72afe504f8bc40b9396c23d6eeb1262d015406a33`

기존 `/workspace/artifacts/v536-verification-managed/packages/index.json`에서 검증된 최신/롤백 두 세대를 원자 승격했다.
전체 무결성과 복원을 확인하고 증거를 보존했다. 자식 종료·소유권 확인 후 해당 실행의 RAM 임시물만 정리했으며
기존 과거 자료의 추가 삭제는 없다. 미확정 입력/새 표시명 UI를 이전 패키지가 지원한다고 표현하지 않는다.

최종 실행 디스크 순증가 3.82MiB, 이번 단위 측정 구간
순증가 5.30MiB, 여유 1214.89MiB다.
단계 표본 최소 여유 1218.67MiB·peak memory 4937.34MiB를 확인했다.
기존 지속 공간144MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가 메모리7GiB+1GiB 기준을 유지했다.
이 증가량은 다음 실행의 보장값이 아니다.


원래 고정 잔여: 파일 이름/설명 변경·다중/큰 자료/현재 폴더의 첫 import 결합·삭제/내용 편집/backup 복구·다른 지원 형식의 미리보기 및 고정 ledger의 나머지 Run/native/권한 backend/UI 항목은 별도다. 초기화 간헐 빈 화면의 직접 원인은 미확정으로 유지한다. 전체 UI·실제 Windows/모바일·Space/Library 전달도 완료하지 않았다. 이름/경로/타입의 임의 조합을 새 필수 항목으로 늘리지 않는다.
