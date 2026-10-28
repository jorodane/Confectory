# v536 저장 복사본의 단일 대상 ABI 갱신

전체 복사 편집·다중 target·혼합 Save의 완료 보고가 아니다. 기존 v536 계약 갱신 버튼과 원본 레이아웃을 유지하며, 이미 저장·확정된 직접 배치 복사본의 한 Blueprint 본문만 연결한다.

## 지원 경계와 원자성

- 같은 ProjectPack의 소유 객체가 직접 제공하고 있는 저장 복사본, 소유 공용 함수/모듈 요구, 정확히 하나의 Blueprint 본문을 요구한다. 다른 객체의 직접 제공과 공유된 복사본, 미확정 생성 초안, 상속 소유자·외부 공용 슬롯 함수는 이 경로에서 지원하지 않는다.
- 기존 `BlueprintCallAbi`의 단일 동일 callee 호출 값↔ref 제한을 재사용한다. 이름·순서·타입·out·반환 및 명시한 storage binding을 추측해 바꾸지 않는다. 직접 등록 callee는 기존 함수/manifest receipt를 사용하며 등록 팩은 쓰지 않는다.
- 서버가 읽은 직접 배치·대상 locator·객체 선언 지문·요구/제공 슬롯과 복사 출처 4개 필드를 `copyAbiBinding`으로 결부한다. 원래 읽은 caller/graph/node record·선언 hash 및 checkpoint가 함께 검증된다. 현재 donor 본문을 복사본에 다시 적용하거나 donor 내용을 최신으로 강제하지 않는다. 저장 복사본은 독립된 이전 snapshot이다.
- `rebindCopyAbi`는 `authorBatch` 안에서만 가능한 배타적 작업이다. staged workspace에서 typed import·호출 서명·wrapper·graph를 갱신하고 출처 불변, 최종 전체 provider 계약, 모든 node record를 포함한 `source-ready`/`source-assembled` 상태를 확인한다. 그 뒤 한 `WriteChecked` checkpoint CAS/receipt로 전체를 저장하고 live 상태를 반영한다. legacy `rebindCallAbi`의 copy 차단과 Set/property·혼합 Save 차단을 제거하지 않는다.
- 편집 전의 정확한 `CONTRACT_MISMATCH`는 갱신 대상으로 살펴볼 수 있다. 공용 함수/모듈 서명은 그때에도 일치해야 하고, 후보 저장 시에는 전체 provider가 유효해야 한다. 다른 계약 오류나 마지막 컴파일 실패를 성공으로 바꾸지 않는다.
- Save는 초안이다. 원본 반영은 기존 Review와 사용자 명시적 compiler Confirm으로만 한다. 입력/저장 결과 조회는 동일 attempt·planHash·source closure·출처/배치 결부가 모두 일치해야 한다. peer 변경을 자동으로 최신 기준으로 재시도하지 않는다.

## 격리 검증

`tests/web/v536_saved_copy_abi.py`는 실제 Linux 엔진·Chromium 렌더러·저장소를 사용한다. fixture의 프로젝트/원본/copy/등록 팩은 모두 임시 디렉터리에 생성하며 사용자 프로젝트·계정·모델 호출·프로젝트 실행을 사용하지 않는다. 정상 fixture에서는 donor가 독립적으로 현재 ABI로 갱신되어 있고 copy만 이전 snapshot을 갖는다. donor 자체가 stale한 별도 검사는 compiler 거절을 요구한다.

최종 로그와 결과는 `/workspace/scratch/v536-atomic/`에 기록한다. 정상 common/long 소유 callee 9개 PASS 라벨(`copy-normal-4.log`, `/tmp/confectory-saved-copy-abi-cg_fumjl`), 직접 등록 callee 9개(`copy-registered-4.log`, `/tmp/confectory-saved-copy-abi-nqcsvc05`), stale donor 안전 거절 9개(`copy-stale-donor-4.log`)를 확인했다. 취소·peer 충돌·저장 거절·성공 응답 유실은 각각 공통 준비 3개+해당 시나리오 1개 PASS이며 `copy-cancel-3.log`, `copy-conflict-3.log`, `copy-storage-3.log`, `copy-response-loss-3.log`에 기록했다. 공통 준비나 순수 10개 거절을 서로 다른 고유 시나리오로 합산하지 않는다. 비복사 슬롯 회귀는 순수 경계 1개+실제 엔진 7개 PASS(`ordinary-slot-final.log`, `/tmp/confectory-slot-call-abi-1_vbg3ig`)다.

| 검사 | 확인 내용 |
| --- | --- |
| 순수 metadata 경계 | 단일 저장 copy binding 및 대상/locator/다중 본문/출처 불일치/외부 소유/공유 제공/요구 누락/provider 오류/외부 공용 함수 등 10개 거절. 각 fixture 시작에서 같은 경계를 반복하며 고유 70개처럼 합산하지 않는다. |
| 소유 callee 실제 화면 | 기존 갱신→저장 전 cold→Save→receipt 재조회/재시도→저장 후 cold→Review 취소→명시 compiler Confirm. Copy 선언/graph만 반영하고 donor·callee·객체·모듈·node 본문 byte 보존. legacy 우회·binding 누락/위조·owner 누락·혼합 요청 6개는 전체 미적용. |
| 직접 등록 callee | 같은 흐름에 기존 함수/manifest receipt를 결부하고 등록 팩 byte 보존. |
| 저장 장치 거절 | fixture checkpoint 파일만 읽기 전용으로 만들어 실제 쓰기 거절. caller/import/graph 전체 미적용, 기존 checkpoint·UI 입력 보존, cold 후 같은 시도 재저장. 하드웨어 정전 시험이 아니다. |
| peer 저장 충돌 | 다른 객체의 명시적 설명 편집/Save 후 오래된 copy ABI를 전체 거절. 상대 저장 내용/checkpoint와 본인 입력을 재시작에서도 보존. |
| 성공 응답 유실 | 실제 저장 성공 update를 테스트 전송층에서 유실시킨다. receipt로 결과를 확인하고 cold에서 중복·부분 반영이 없음을 확인. |
| 사용자 취소 | 명시적 갱신 Undo 후 cold에서 입력 취소/기존 계약과 모든 파일 보존. |
| 기존 비복사 슬롯 | `v536_slot_call_abi.py`의 실제 경로와 소유자 변경 차단 회귀. 두 테스트 fixture에 현재 Linux host용 빌드 대상 mapping을 추가했다. 기존 슬롯 변경 검사는 고정된 상태 caption 대신 실제 변경 안내/요청 거절, 유지된 입력과 소스 및 별도 위조 요청의 서버 거절을 확인한다. 화면 세대가 먼저 바뀌어 전송 전에 거절하면 존재하지 않는 author-attempt를 요구하지 않으며, 기록이 있으면 캡처 범위를 엄격히 확인한다. 없는 빌드 대상을 성공으로 처리하지 않았다. |

검사 중 fixture 문제를 구별했다. 원본과 copy가 같은 물리 node 파일을 가리키던 초기 fixture를 분리했고, copy 상태 caption을 `저장됨`이라고 기대하던 assertion을 실제 저장 응답/입력 정리 검사로 바꿨다. 재조회는 제출하지 않은 임의 attempt 대신 실제 접수된 UI attempt를 사용한다. `MISSING_TARGET linux`는 fixture에 정상 mapping을 추가했다. donor 자체의 stale import는 전체 compiler가 차단하며 이 경로가 donor를 자동 고치지 않는다. 보호 조건을 삭제해 통과시키지 않았다.

실제 화면 캡처: 정상 fixture의 `copy-abi-explicit-refresh.png`. 새 HTML/CSS/패널을 추가하지 않았고 캡처를 열어 기존 창/갱신/복사 출처 상태를 확인했다. 전체 v536 pixel equality나 모든 모바일/네이티브 문맥을 재수용한 것은 아니다.

## 잔여

비공개 새 복사 초안의 wrapped call/ABI 계획과 `ImplementationCopyEdits` 결합은 아직 없다. 여러 target/body가 공유하는 import의 모든 영향 후보·Review 그룹, 복수 동일 callee 사용, 외부 공용 슬롯 함수, 동일 owner 선언/스키마·복사 intent 혼합 Save도 계속 차단한다. 다음은 새 copy 계획의 callee receipt·관측 source/provenance를 함께 결부한 뒤 다중 body, 혼합 Save 순서다. 임의 일반 ABI 대응·원본 계약 수정·프로젝트 실행 권한을 추가하지 않는다.

## 빌드와 마무리 기록

C# 솔루션 Release 0 warning/0 error(`solution2.log`) 및 최종 Linux 엔진(`engine3.json`) 빌드 통과. JS 문법·Python 구문·diff 공백 검사 통과. 변경 13개(구현5/테스트2/문서6)의 경로·파일/비밀 패턴 검토에 검토 필요 패턴이나 생성물·프로필·인증 파일이 없었다. 패턴 검토는 모든 비밀 부재의 절대 증명이 아니다.

Windows x64 교차 패키지: `/workspace/artifacts/Confectory-v536-saved-copy-abi/Windows-x64/Confectory.exe`. 전체 폴더를 유지하고 exe를 연다. .NET Desktop Runtime10 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다. 선언 파일2308개/marker 포함2309개, UI68개다. marker SHA256 `d3fbf4fe668384351307bf02c8cad8a344f2ec1390f3d60e1f8ff8e776634f44`, 전체 파일 목록 checksum `95399e25df214239cd017f38e6a70e50f4a2d47a50acc0236968caa4704997b9`이며 목록은 scratch의 `review/PACKAGE_SHA256SUMS`에 보관했다.

`desktop_package.py` 통과(`/tmp/confectory-desktop-package-km2s2cfi`, `package-probe.log`): 구성/리소스 hash, 변조·의존성 누락 거절, 다른 cwd, SDK 없는 실제 packaged managed 웹 시작, fixture 프로필 재사용/override, 최소 연결 화면 렌더를 확인했다. exe·WebView2·OS 더블클릭은 실행하지 않았다. 코드 커밋 `9cf2fd65ebf31a4ad0a88e3218e7a9abb9e124b5`의 깨끗한 별도 checkout에서 솔루션 Release 0 warning/0 error, 새 Linux 엔진 빌드, 실제 CRLF 속성 pull 이후 retained 창과 fresh LF 창의 68개 canonical/exact 리소스 및 내용/encoding/BOM/binary/budget 변조 거절을 확인했다(`checkout-solution.log`, `checkout-engine.json`, `checkout-resources.log`). 두 작업 트리가 깨끗하며 원본 바이트를 보존했다. 패키지에 든 변경 구현 소스 5개는 이 코드 커밋과 바이트 동일하다(`package-code-proof.json`). 이 마무리는 검증 문서만 갱신하므로 통과한 코드 검사를 반복하지 않았다. 실제 Windows apphost/WebView2·native 입력, 사용자 로그인·유료 추론은 하지 않았다. 기존 Library discovery 네트워크 실패에 새 복구 근거가 없어 업로드를 재시도하지 않았으며 로컬 exe는 사용자에게 전달된 첨부가 아니다.
