# 로컬 import를 보존한 여러 C# 본문 저장 검증

최종 runtime `2897f3709cd44cf10c954ed9dd6a578dd421ec3d`의 유효38단계는 **신규13·동등 증거 재사용25**다.
[원본 수용 근거·지원/호환 경계](V666_NATIVE_BODY_IMPORTS.md)를 따른다.

| 범위 | 실제 확인 |
|---|---|
| 변경 전 | 각 imported body 단일 후보는 유효하고 원래 프로그램은46 반환. 두 본문 그룹과 실제 정보 Save만 기존 native leaf guard로 거절됐다 |
| 본문 그룹 | 공개/native 서명·핀 identity·원래 import/header/helper/caller를 보존한 두 명시 본문만 한 후보/CAS로 저장했다. 후보 역순·원래 hash·linked body만 대조했다 |
| 편집 수명 | 원본 UI의 취소·private Undo/Redo·미저장 cold·원자 Save·저장 후 cold·Review 거절·Confirm, 기본/독립 정보 창·checkpoint 실패/재시도·lost response·충돌·프로젝트 왕복을 통과했다 |
| 실제 실행 | 공유 Blueprint caller가 편집한 두 native 본문과 원래 local helper를 호출하는 Linux 생성 프로그램을 컴파일·실행하여26을 반환했다. 미선택 원문·주석 CRLF·정확한64비트 값도 대조했다 |
| 의존 CAS | Save 전 helper 선언 변경은 전체 거절. Review 뒤 helper 선언/본문 변경 각각 sourceConfirmed=false·두 본문 미적용·peer/checkpoint 바이트 보존. 정확한 원문 복구·cold·새 Review 뒤 실행26 확인 |
| 거절 | 계약/핀/native/body·missing·외부 namespace·잘못된 kind/signature 8후보, receipt 전체/일부 누락·해시 형식·경로·추가 경로·소유자·버전 7후보 거절. 기존 import 없는 leaf 그룹 후보도 통과 |
| 최종 패키지 | 새 LF clone/checkout/restore/Release/MCP/빈 engine6단계와 새 Windows 교차 생성/구조·포함 Linux engine 정상 UI·전체 ZIP CRC/SHA/파일/디렉터리 mode 복원·복원 dependency CAS/lost response·실패 수명관리7단계를 새로 실행했다 |

제품 변경은6파일이며 frontend/CSS/HTML/JS·공개 ABI·code generation·Core·permission
backend·최종 Confirm source lease는 동일하다. 기존 version3 readGuards를 연결한다.
구 reader/checkpoint 교환 자체는 별도 실행하지 않아 호환 완료로 표현하지 않는다.

개발은27단계 중23통과·4실패다. 첫 dependency 실패는 실제 제품 결함으로 helper가
Review 뒤 바뀌어도 두 본문이 쓰인 증거다. 원래 실패 입력/물리 source를 보존하고
읽기 CAS를 구현했다. Metadata call의 기존 import alias 누락은 build에서 검출하여
연결 후 재검증했다. 나머지2실패는 cold/Review 전후 checkpoint 비교였으며 raw 대조로
history.epoch와 ProjectManifest.revision만 변함을 확인했다. 이 두 로딩 메타데이터만
Review 전후 분리하고 본문·계약·receipt·입력을 정확히 비교한다. Confirm 직전/직후는
checkpoint 바이트 전체가 같아야 한다. 실패 입력/로그/수정 전 검사도 보존했다.

첫 최종 동결 `7eb45e235cb7fdcbc3e4a683a4f16c4fb7c60059`은 신규33통과·1실패였다. 패키지에 없는 테스트 파일을
runtime content 안에서 찾는 FileNotFoundError가 첫 packaged UI 시작에서 발생했다.
드라이버를 자기 script 옆에서 찾는 경로만 수정했다. LF/CRLF source checkout에서는
수정 전후 같은 파일·같은 코드로 해석됨을 정확한 대체식·Git blob/제품·다른 테스트·
SDK/NuGet/config/RID 및 no-hardlinks/EOL 증거로 검증했다. 봉인된 IPC1·LF9·CRLF15,
총25단계만 재사용했다. 실패한 UI와 과거 패키지2단계는 재사용하지 않았다. 새 LF
준비6단계와 패키지/복원7단계를 실행해 최종13신규+25재사용=38로 마감했다. 개발/첫
최종의 중복 실행을 모두 새로운 검사처럼 합산하지 않는다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 2897f3709cd44cf10c954ed9dd6a578dd421ec3d | 6cfb44aec836c6f235b40ac705f92f9ac0f64deb590367b91bcabdeb11582a8c | 53,860,668 |
| rollback | fe3d35dd441a1dccc5ca7d9b3bb6e14eb25b0e3d | 1a883216f5399c36b45cf146f04fcb123f81ca466b9d0ac5320c04d94d35ba0a | 53,856,046 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/3f48e01622bc4fd3a689818e1bb14d4f.json`, evidence `5434edacc535c7962bcc8b6e782964ce474c25f4f12574e6fefc9dcf97ba10d7` (2,613,177B).
첫 최종 record `/workspace/artifacts/v536-verification-managed/runs/c77da467b74a4627b34650803b645b2a.json`, evidence `77946c791dd00b1bdd17eb8ba34c38f35559ac259016d1751d7060cda0ef9936` (5,748,565B).
개발 evidence `2af37665b66025a4cb2a37eeaf209f89fd9704dca3a0b6459c69cc0960be42c7` (6,316,397B).
세 archive manifest와 두 보관 ZIP을 재검증했다. 시작 index `94a5fabd83c2f439e2cb5f091db0fe7dcbc1cafa3c72c07cbe4fd45bf790a652`,
종료 sidecar `8b9a320f89530b3daf34b6b9ad79ac1ee1cfa3e2dd7e0bf0e721da91e916c29a`. 최종 preflight 원본은 덮어쓰지 않았고 개발 사전검사와
실패/경로 수정 증거는 따로 보존했다. 첫 수집기의 파일 저장 후 콘솔 results 키 조회
오류도 제자리 SHA 검증 기록으로 보존하며 최종 검사 단계 실패와 구분한다.

latest/rollback 두 ZIP만 승인된 관리 절차로 교대하고, 기존 rollback
`ecb47f0acd220c617281374d6db42594e5e74d33`의 관리 ZIP만 교체했다. 과거 증거·사용자 데이터·별도 원본
checkout을 보존했다. 개발/두 최종 RAM 작업공간은 evidence 봉인 뒤 소유 identity를
확인해 정리했다. 이 단위의 새 owned bytecode만 해시 기록 후 제거했다. 재생성 가능한
build outputs는 정확한 해시 목록으로, 원문·checkpoint·실패 로그는 archive로 보존한다.

단위 시작 여유 25,877,512,192B, 마감 25,857,372,160B(24.0816GiB), 순증가
20,140,032B(19.2070MiB). 관측 최대 cgroup memory 9,142,472,704B,
최종 stage 최소 디스크 25,859,624,960B다. 추가9GiB+safety1GiB·RAM4GiB+
reserve512MiB·최종 evidence512MiB의 예산을 변경하지 않았다.

copy/상속/등록·private/whole/wrapper·계약 변경의 실제 다중 closure와 고급 타입/표시명은
기존 유한7/8/9행 잔여다. 종류 CLR 표현/사용 중 삭제와 실제 identity/group backend의
미결 정책도 유지한다. M11/M12/M4를 회귀 근거 없이 다시 열거나 타입/문맥의 모든 조합을
새 필수로 늘리지 않는다. frontend와 기존 late-input 보호는 소스가 동일하며 별도 늦은
입력 행렬 전체를 이번에 새로 실행했다고 주장하지 않는다.

실제 검증은 Linux native engine·Chromium·생성한 격리 fixture다. Windows 교차패키지는
실제 Windows/WebView2 실행이 아니며 모바일·물리 IME/GPU/audio·사용자 프로젝트·전체
UI·Space/Library 전달은 미검증이다. 초기 빈 화면 원인은 여전히 미확정이다.
