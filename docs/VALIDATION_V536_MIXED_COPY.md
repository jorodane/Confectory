# v536 새 복사본과 같은 객체 값의 최소 혼합 저장

전체 v536 복원이나 일반 혼합 저장의 완료 보고가 아니다. 원본 v536 객체 창의 임시 저장·변경 취소·확정 버튼을 유지하고, **새 복사본 하나 + 같은 소유 객체의 설명/기존 단일 기본값**만 한 후보에 연결했다. 새 HTML/CSS·패널·권한은 추가하지 않았다.

## 지원 및 저장 경계

- 동일 ProjectPack의 소유 객체와 명시적으로 선택한 source/target을 요구한다. 기존 단일 primitive 필드(`string/bool/int/long/float/double`, path 길이1)의 값과 설명을 지원한다. 상속 필드의 객체별 기본값 재정의는 가능하며 부모 정의를 수정하지 않는다. 새 필드/스키마·부모·모듈·복합/참조 값·unset·복수 혼합 슬롯은 계속 차단한다.
- 서버 `MixedOwnerCopyEdits`는 현재 effective schema/관측 소스와 타입을 검증한다. raw owner text를 받지 않는다. 설명/값을 staged workspace에만 적용하고, 선택한 복사본의 출처·import·graph·wrapper·모든 node record 및 최종 요구/제공 계약을 다시 확인한다. 원래 snapshot과 원래 checkpoint CAS를 재검사한 뒤 한 `WriteChecked`로 전체를 저장하고 live 상태를 반영한다. 각각의 Save를 차례로 호출하는 방식이 아니다.
- 현재 유효한 기존 wrapper/실행 enum과 export를 포함하는 Blueprint를 선택·복사하고, 복사본의 C# 본문/후처리를 편집할 수 있다. export를 물리 C# record로 오인하던 누락을 수정했다. 원본의 Windows 본문이 있어도 명시적으로 선택한 common만 새 복사본으로 만든다. 이는 공유 import의 다중 target ABI 갱신을 구현한 것이 아니다.
- stale ABI 갱신/임의 계약 수정은 허용하지 않는다. wrapper는 기존 contractHash/returnMapping과 최종 graph 검증을 요구한다. donor·부모·등록 소스나 다른 실행 대상을 자동 수정하지 않는다.
- receipt v2는 선언 계획과 선택한 copy 의도·편집 hash·변경 소스 closure를 함께 결부한다. 선언이 빠지거나 다르면 이미 저장된 요청으로 정리할 수 없다. 선언 없는 이전 receipt v1은 유지한다. 응답 유실 시 같은 계획의 receipt를 확인하며 무조건 최신 기준으로 재전송하지 않는다.
- UI는 캡처한 입력만 정리한다. 늦은 설명/동일 필드 입력에는 확인된 저장 결과의 hash와 타입/경로를 결부한다. 재시작 시 해당 hash·단일 writable 타입/경로가 같고 복원된 입력일 때에만 새 프로세스 revision을 채택한다. 같은 프로세스의 변경이나 실제 hash/타입 변경을 자동 승인하지 않는다. 알 수 없는 입력과 다른 객체 입력은 보존한다.
- Save는 작업 사본 저장이다. 원본 파일 반영은 기존 생성 그룹 선택 → Review → 명시적 compiler Confirm에서만 한다.

## 격리 검사

모든 실제 엔진 fixture는 임시 프로젝트·프로필을 생성한다. 사용자 프로젝트/계정/토큰·유료 추론·프로젝트 실행은 사용하지 않았다. 로그는 `/workspace/scratch/v536-mixed-copy/`에 보존한다. 공통 준비 PASS를 고유 시나리오로 중복 합산하지 않는다.

| 검사 | 실제 확인 |
| --- | --- |
| `v536_mixed_copy_backend.py` | 10종 owner/hash/타입/값/구조/중복/본문 위조 전체 미적용, 정확한 long `9007199254740993`, 선언/복사 source·import·본문 결합, receipt 선언 누락·변조 거절, cold 복원, 명시적 compiler Confirm. 최종 `backend-final.log`의 5개 PASS 묶음. |
| `v536_mixed_copy_ui.py` 정상/`storage` | 원본 UI에서 설명·상속 HP 입력 후 복사 대상 선택, copied body/wrapper 편집, 한 object Save, cold 복원·Review 취소·명시적 compiler Confirm. 실제 checkpoint 파일 쓰기 거절 후 두 종류 입력과 기존 checkpoint 보존, cold 재시도 성공. `ui5.log` 4개, `ui-storage.log` 공통을 포함한 6개 PASS 라벨. |
| `storage-cancel` | 실제 쓰기 거절·cold 후 원본 변경 취소, 다시 cold에서도 copy만/선언만 남지 않음. `ui-storage-cancel.log`. |
| `conflict` | 같은 owner에 동료가 먼저 설명을 저장한 뒤 오래된 혼합 Save 거절. 동료 checkpoint와 본인 입력을 cold에서도 보존. `ui-conflict-3.log`. |
| `wrapper-invalid` | 실제 UI의 applySlots 요청에서 wrapper 계약 지문만 위조해 실제 서버 거절을 확인한다. staging한 선언·copy·import·본문은 전체 미적용이고 입력/기존 checkpoint는 cold에서도 보존. `ui-wrapper-invalid.log`. |
| `response-loss` | 실제 서버 성공 update만 테스트 전송층에서 유실. 늦은 설명·long `9007199254740995`를 보존/재결부, cold 뒤 같은 owner의 다음 명시적 Save 성공, 중복 copy 없음. `ui-response-loss-3.log`. |
| `v508_elements_shell.py` | 일반 편집/취소 회귀와 복원된 늦은 입력의 hash/타입/경로/writable/복원 marker 및 같은 프로세스 경합 7개 경계. 다른 owner 입력 보존. `restore-renderer.log`. 제어된 렌더러 검사이며 실제 backend 검사를 대신하지 않는다. |
| `v508_copy_slots_backend.py` | 기존 비혼합 두 슬롯의 실패 전체 미적용·저장/cold/Review/명시 compiler Confirm. `nonmixed-slots.log` 4개 PASS 묶음. |
| `v508_copy_batch_late.py` | 기존 두 슬롯 UI에서 준비 중 입력 변경의 제출 전 거절, 실제 저장 성공 응답 유실과 늦은 copy 설명, cold 뒤 같은 복사본 재저장/중복 생성 방지. `nonmixed-late-6.log` 3개 PASS. |
| `v508_copy_draft_state.mjs` | 기존 복사 초안 취소/늦은 입력·다른 객체 보존 순수 검사. `copy-state-2.log`. |

정상/저장 실패 fixture는 원본 Slime·project 등록 외의 부모/원본 wrapper/다른 Windows 본문 byte를 보존한다. 실패/취소에서는 원본을 전혀 반영하지 않는다. 스크린샷 `mixed-copy-owner-before-save.png`를 실제로 열어 1280×900의 원본 객체/Blueprint 배치와 새 상시 패널 없음에 대해 확인했다. 전체 v536 pixel equality를 재수용한 검사는 아니다.

검사 중 실제 결함과 fixture 문제를 구별했다. 실제 복사 경로의 export 누락·wrapper enum 미투영과 혼합 성공 후 늦은 입력의 재시작 revision 오탐은 수정했다. 초기 fixture의 객체 직접 field 문법은 schema/use로 수정했고, 현재 Browser의 검색/행 Enter/준비 상태와 실제 창 포커스를 사용하도록 오래된 테스트를 갱신했다. 응답 유실 재시도 검사는 매 polling마다 임시 View를 만들던 방식 대신 실제 UI 결과/오류를 기다린다. 실패 결과를 통과로 집계하거나 CAS/Review 보호를 제거하지 않았다.

## 미완료와 실행 한계

비공개 새 복사 초안의 **stale ABI 재연결**, 모든 영향 body/다중 target ABI, 복수 혼합 copy 및 넓은 스키마/구조/복합 값 혼합 Save는 다음 별도 묶음이다. 기존 차단을 유지한다. 현재 wrapper 복사 성공을 이들의 완료로 표현하지 않는다. 실제 Windows apphost/WebView2·OS 더블클릭·네이티브 입력·하드웨어 정전은 이번 Linux fixture 검사로 확인하지 않았다.

## 빌드와 패키지

Release 솔루션 0 warning/0 error(`solution2.log`), 최종 metadata helper 빌드 0 warning/0 error(`metadata-bounded.log`) 및 실제 Linux 엔진 `engine6.json` 통과. 변경 JS/Python 구문과 diff 공백 검사 통과. UI 리소스는 기존 68개이며 변경된 4개 JS의 canonical pin을 갱신했다.

Windows x64 교차 패키지는 `/workspace/artifacts/Confectory-v536-mixed-copy/Windows-x64/Confectory.exe`다. 전체 폴더를 유지하고 exe를 연다. .NET Desktop Runtime10 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다. 선언 파일2309개/marker 포함2310개, 총131537534byte. marker SHA256 `40f0abf8d7dd051382f51a5e9989629ee6bf1d232d3dcb53712c235bece1d9f3`, 전체 파일 목록 checksum `fd1dfb95921d4bc1e907ba5230742e64fdcc447fd975d9d5e6bf84ad90714d65`. 파일별 목록은 `review/PACKAGE_SHA256SUMS`에 보관했다.

`desktop_package.py`는 실제 패키지 managed 엔진을 SDK 없는 환경/다른 cwd에서 시작하고, fixture 프로필 재사용/override, 68리소스, 최소 연결 화면, 변조/의존성 누락 거절을 확인했다(`package-probe.log`, `/tmp/confectory-desktop-package-bmxhn09a`). Windows exe/WebView2는 실행하지 않았다. Library discovery 장애에 새 복구 근거가 없어 업로드를 반복하지 않았으며 로컬 경로는 사용자에게 전달된 첨부가 아니다.

코드 커밋 `01432cf299879d3acc06170af7c46cdd46d009e2`의 깨끗한 별도 checkout에서 Release 솔루션 0 warning/0 error, 새 Linux 엔진 빌드가 통과했다(`checkout-solution.log`, `checkout-engine.json`). 실제 Git CRLF 속성 pull 후 retained 창과 fresh LF 창 모두 68개 canonical/exact 리소스를 확인하고 내용/encoding/BOM/binary/budget 변조를 거절했으며 원본 byte를 보존했다(`checkout-resources.log`). 두 작업 트리는 깨끗했다. 패키지에 포함된 변경 구현 소스 12개는 이 코드 커밋과 byte 동일하다(`package-code-proof.json`).

게시 대상으로 검토한 20개 파일은 구현12/테스트5/문서3이며 생성물·로그·프로필·인증 파일은 포함하지 않았다. 비밀 패턴 검토에서 추가 검토 대상 패턴이 없었으나 모든 비밀 부재의 절대 증명은 아니다. 이 마지막 기록은 문서만 갱신하며 통과한 코드 검사를 불필요하게 반복하지 않는다. 원격 대상은 승인된 `https://github.com/jorodane/Confectory.git`의 `work/current`이고 main/Android/원본 v536 ZIP은 변경하지 않는다.
