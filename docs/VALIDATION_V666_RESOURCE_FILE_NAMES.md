# v666 자료 파일 이름 변경과 현재 미리보기 metadata 검증

최종 동결 `ca011efde83606e63a81480177eca7556e2aa8c8`에서 LF **21**, CRLF **21**, 패키지/전체 복원/수명 **9**, 총 **51단계(신규 39·재사용 12)**를 통과했다. 이후 게시 문서 외 제품/검사 입력은 바꾸지 않았다.

- 원본 `dist/app.js::resourceContextMenu/renameResourceInline`을 따라 자료 카드/계층의 Enter·포커스 해제 확정과 Escape 취소를 연결했다. 확장자를 포함한 표시명만 바꾸고, 형식 재분류·bytes 변환·원본 파일 rename은 하지 않는다. 미리보기 파일명 설정란은 현재 읽기 전용이다.
- 독립 실제 DSL 소비자로 현재 표시명과 같은 ID/hash, 원본 copy/import receipt·카테고리/폴더 이름 보존, 원래 Request API의 원래 metadata 유지, 현재 `Layout.read`의 이름/검증 bytes/MIME/kind, stale hash/path/owner/대상 종류/명령 충돌/오래된 요청, 실제 write 거절/같은 입력 복구, 이동 후 이름/receipt, 손상 metadata의 읽기 거절을 실행했다. 기존 카테고리/이동·폴더 이름 소비자도 각 checkout에서 검증했다.
- production 원문을 추출한 통제 harness에서 파일 이름 저장의 성공·manifest/identity/파일 목록/계층/폴더 이름/파일 이름 CAS 경합·쓰기 실패 **8가지**를 실행했다. 현재 표시명/bytes의 정상 읽기와 실제 원문 읽기가 끝난 뒤 **6개 의존 파일 각각의 변경**을 검사해 읽기가 쓰기/CommitPlan 없이 거절되고 peer 데이터를 보존함을 확인했다. 별도의 독립 DSL 소비자와 실제 native UI로 wiring을 검증한다.
- 정확한 이전 `de22e3a0` Layout 몸체를 함께 컴파일해 새 파일 이름 파일이 있어도 이전 reader가 원래 이름·ID·bytes/topology를 읽고 다시 쓰지 않음을 확인했다. legacy 몸체 SHA를 증거에 기록한다. 새 파일 이름은 별도 `resource-file-names.v1.json`만 쓰며 기존 copy/topology/폴더 이름·원본 C#/공개 override 계약·권한·Review→Confirm은 보존한다.
- 실제 UI에서 전체 표시명의 인라인 Enter·tree blur·Escape, 같은 ID/hash의 새 이름으로 열기, 이미 열린 미리보기의 제목·읽기 전용 파일명·원래 내용 갱신, 쓰기 권한 거절/실패 입력 재시도, 실제 성공 응답 유실/정확한 receipt 재사용, 기준 캡처 뒤 peer 변경/새로고침 후 오래된 재시도 거절·입력만 취소, 새 검색/다른 입력 보존을 확인했다.
- 실제 native 읽기 완료 뒤 이전 성공 응답을 보류하고 파일을 새 이름으로 바꿨다. 현재 metadata가 이전 token을 취소하고 같은 ID/hash를 다시 읽으며, 늦은 이전 성공이 현재 제목/읽기 전용 이름/내용을 덮지 않음을 확인했다. HTML/코드는 기존 literal text renderer이고 외부 요청/실행은 없다.
- 실제 cold engine에서 파일 kind를 포함한 미확정 입력과 고정 기준을 복원해 자동 rename 없이 Escape로 취소했다. 제출 후 응답 유실의 exact command도 별도로 cold 복원해 명시 재시도가 추가 쓰기 없이 현재 이름을 확인했다. 같은 namespace의 다른 실제 프로젝트는 이름/입력을 채택하지 않으며 원래 프로젝트로 돌아오면 소유 상태만 복원한다.
- 기존 카테고리 이름·생성/이동·파일 import·readonly 관측/미리보기의 영향 회귀를 실행했다. C# source 복구 UI 두 검사는 해당 입력에 resource 창/endpoint가 없고 source primitive/fixture/SDK/NuGet/명령이 같은 근거로 재사용했다. 그 밖의 재사용은 수정된 CAS fixture 외 제품·선택한 검사 입력이 같은 이전 통과 증거를 따른다. 재사용을 신규로 세지 않는다.
- 새 Windows-x64 교차 패키지와 ZIP 전체 복원본에서 실제 native HTTP/Chromium UI를 실행하고 전체 SHA·CRC·파일/디렉터리 모드·실패 수명·증거 보존을 확인했다. Linux에서의 교차 패키지 검사이며 Windows apphost/WebView2·모바일·전체 UI의 실행 완료는 아니다.

실패 구분: 첫 CAS harness의 폴더 이름 경합 항목은 상대 변경 주입 전에 변경 후 상태를 기대해 assertion에서 실패했다. 이전 reader 확인은 주입 전 원본을 비교하도록 고쳤다. 해당 기록을 보존하고 실패 실행은 최종 통과 수에서 제외했다. 제품 코드는 바꾸지 않았다. 다음 UI 실행은 접힌 미리보기 제목줄 뒤 검색칸의 포인터 클릭이 차단되어 멈췄다. 제품 레이아웃은 변경하지 않고 실제 Tab 포커스 이동으로 같은 blur를 검사하도록 fixture를 고쳤다. 다음 실행에서는 브라우저 뒤에 가려진 미리보기의 닫기 클릭이 막혀 기존 Enter 열기로 같은 창을 앞으로 가져온 뒤 닫도록 fixture만 수정했다. 제품 코드는 그대로다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/0595abcbe5a14c6180ca8702c11b24ec.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/0595abcbe5a14c6180ca8702c11b24ec.zip` · 3,047,449 bytes
- 증거 SHA: `a2929099dc5d9056a538c8f53e974f71ee33edd68c39dccc3088cc8303cc89a1`
- 최신 source: `ca011efde83606e63a81480177eca7556e2aa8c8`
- 최신 ZIP: `a9e2894b0c5adad4e20449b86b73c256665bfbb2c744bb6b7a457c7af3780499.zip` · 51,910,585 bytes · 파일2495 / 디렉터리153
- 최신 전체 manifest SHA: `7541e575f692e71737bddc3fdbb313cd514e7013455b8079f380281a15423897`
- 정상 롤백 source: `bcdc0ba41fd849233c79bdce0ea27b9f65891060`
- 롤백 ZIP: `b6c949f4ecf8c07eb263ab01037a6ee22f672b714a31902e1ed769c664e968c3.zip`
- 롤백 전체 manifest SHA: `8b6bd6ee7a1a1304ecc110a73de21709a1969caff0b8364e32f2726174ce9841`

기존 `/workspace/artifacts/v536-verification-managed/packages/index.json`에서 검증된 두 세대를 원자 승격했다.
전체 무결성/복원과 증거를 보존한 뒤 자식 종료·소유권 확인 후 해당 실행의 RAM 임시물만 정리했다.
기존 과거 자료 추가 삭제나 계정/접근권한 변경은 없다. 이전 UI는 새 이름 편집/미확정 입력을 지원하지 않는다.

최종 실행 디스크 순증가 4.07MiB, 실패/fixture 수정 기록을 포함한 이번 구간
순증가 8.00MiB, 여유 1206.72MiB다.
단계 표본 최소 여유 1210.73MiB·peak memory 4955.14MiB를 확인했다.
기존 지속 공간144MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가 메모리7GiB+1GiB 기준을 낮추지 않았다.
이 증가량은 다음 실행의 보장값이 아니다.

이전 실패 실행(최종 통과 수에서 제외):
- `/workspace/artifacts/v536-verification-managed/runs/f5c1dc92fbf24254a15d4eb9f6a997b6.json` · SHA `e3efaf54823a59c61e21eef136d7810cc63a78f1c7b3e9592adcea1650d8e027` · 완료15/실패1
- `/workspace/artifacts/v536-verification-managed/runs/d8d61f56433e473a8d641c25fd245e40.json` · SHA `1b7b7121244f331a7206c8952c7e23a2570af16895f295f5319a7a872a2b35c6` · 완료7/실패1
- `/workspace/artifacts/v536-verification-managed/runs/5702f5d49bb24d76aadf5dacb46a0ea7.json` · SHA `f972c42cb48b7314fde9b014cf57c66ddad07fbcfe03141d04c10fdc709ac71a` · 완료6/실패1


고정 잔여: 파일/카테고리 삭제·설명/내용 편집·backup 복구·다중/큰 자료·현재 폴더의 첫 import 결합·다른 형식의 미리보기 및 기존 Run/native/권한 backend/UI 항목은 별도다. 초기화 간헐 빈 화면의 직접 원인은 미확정이며 실기기·전체 UI·Space/Library 전달도 미완료다. 확장자/타입/문맥 조합을 새 필수 항목으로 늘리지 않는다.
