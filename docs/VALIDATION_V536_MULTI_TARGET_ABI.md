# v536 소유 Blueprint의 다중 target 호출 ABI 갱신

전체 v536 복원이나 모든 호출 형태의 완료가 아니다. **같은 소유 implementation의 모든 target이 Blueprint이고 같은 호출 하나의 값/ref 계약을 함께 갱신하는 단위**다. 새 비공개 복사 초안의 오래된 ABI와 넓은 혼합 Save는 여전히 별도 미완료다.

## 후보·저장·검토 계약

`BlueprintCallAbiGroup`은 2~8개 target의 정확한 locator, graph, 모든 code record와 소유 함수/implementation/import/callee를 하나의 원래 결부에 넣는다. 하나라도 없거나 stale하면 전체를 거절한다. 기존 `BlueprintCallAbi`의 이름·순서·타입·out·반환 보존과 값↔ref 제약을 각 target에서 검증한다. ref는 명시한 기존 storage binding만 허용하며 literal을 참조로 추측하지 않는다.

단일 본문용 선언 projection은 순수 검사 안에서만 사용한다. 최종 선언은 모든 원래 body를 유지하고 shared typed import 하나를 갱신한다. 각 graph의 현재 wrapper 코드/enum·핀·연결과 code record를 보존하며 최종 모든 body의 `source-ready`와 모든 record의 유효성을 확인한다. code record를 새 정의로 무조건 restamp하거나 불투명한 C#을 다시 쓰지 않는다.

서버는 읽었던 전체 source closure와 checkpoint를 `authorBatch`에 결부하고, 격리 candidate에서 갱신·그룹 검증·`EditBatch`를 수행한다. 한 `WriteChecked` CAS로 전체 후보를 저장한 뒤에만 live 상태를 반영한다. 기존 source proof/planHash/attempt/source closure receipt로 응답 유실과 재시도를 처리한다. 다른 저장본을 최신 기준으로 자동 덮어쓰지 않는다.

검토 그룹은 소유 공용 함수·implementation·import 함수들·모든 graph와 code record를 정확히 포함한다. 단순히 기존 3/4개 개수 검사만 풀지 않았다. 5개 이상 그룹은 별도의 `BlueprintCallAbiGroup.ValidateGroup`이 선언/body 전체 목록·ID·소유 namespace·path·record/계약·최종 source-ready·무관한 추가 항목 부재를 검사한다. 생성 그룹 조회·cold Restore·Review 선택·Confirm 후 checkpoint 정리가 이 검증을 사용한다. 기존 3/4 그룹 검증은 유지한다. 변경 없는 함수/record는 읽기·검토의 support row이며 내용을 다시 쓰지 않는다. 끝난 이전 그룹은 전체가 clean일 때만 조정 metadata를 함께 교체할 수 있고, 남은 다른 초안은 차단한다.

## 원본 UI와 실패 안내

기존 v536 갱신 버튼을 사용한다. shared import에 영향을 받는 target 목록을 기존 모달 틀에 표시하고 사용자가 취소 또는 **모든 대상 계약 갱신**을 선택한다. 수락은 초안 작성이고 최종 반영이 아니다. 새 상시 패널/HTML/CSS·레이아웃은 추가하지 않았다. 기존 C# 편집·Undo·Save·Review/명시적 compiler Confirm 흐름을 유지한다.

같은 그룹의 import 함수를 다른 생산자 그룹으로 오인해 불필요하게 manifest까지 검토에 추가하던 연결을 구별했다. Confirm 뒤에도 all-target source closure를 유지하여 정상 확인 후 창의 source proof가 불필요하게 축소되지 않게 했다. 이 경로의 일반 전송 오류에는 ‘공유 호출 저장을 마치지 못했어요. 저장 상태와 계약을 다시 확인해 주세요. 입력은 유지됩니다.’를 표시한다. 오류를 성공으로 바꾸거나 원인을 특정 저장 장치/사용자 환경으로 단정하지 않는다.

## 격리 검증

fixture는 `/tmp/confectory-multi-abi-*`에 프로젝트·프로필을 생성하고 실제 Linux 엔진/Chromium/작업 저장소를 사용한다. 사용자 프로젝트/계정/토큰/유료 추론/프로젝트 실행은 사용하지 않았다. 컴파일 Confirm은 명시적 fixture UI 동작이다. 로그는 `/workspace/scratch/v536-multi-abi/`에 보존한다. 각 모드의 공통 준비 라벨을 고유 시나리오처럼 합산하지 않는다.

| 검사 | 확인 결과 |
| --- | --- |
| 순수 후보/그룹 | `v536_multi_target_abi_metadata.py`, `metadata-final.log` 4개 PASS 묶음. 전체 target 결부·shared import/두 wrapper 갱신·입력 불변, 누락/opaque/부모/중복 path/record/계약/잘못된 ref storage/출처/공용 계약 등14개 거절, 그룹의 누락/무관 항목/stale/locator6개 거절. 값→ref literal은 실제 ref-storage 검사에서 거절한다. |
| 실제 정상 화면 | `ui2.log` 5개 PASS 라벨, `/tmp/confectory-multi-abi-4zau52_2`. 두 target/모든 record/callee 관측 → 명시적 모달 취소·수락 → 저장 전 cold → 한 Save → 두 target source-ready/정확한7개 그룹 → 저장 후 cold → Review 취소 → 명시 compiler Confirm. |
| 실제 저장소 거절 | `ui-storage.log` 공통 포함6개 PASS, `/tmp/confectory-multi-abi-82k_m3m6`. fixture checkpoint만 쓰기 거절하여 두 graph·import 전체 미적용, 두 target의 원래 ref ABI·이전 checkpoint·사용자 계획 보존, cold 재시도 및 Confirm. 하드웨어 정전 검사가 아니다. |
| 성공 응답 유실 | `ui-response-loss.log` 공통 포함6개 PASS, `/tmp/confectory-multi-abi-5_vx5x8c`. 실제 서버 성공 update만 fixture 전송층에서 유실한다. receipt로 동일 요청의 전체 완료를 한 번 확인하고 cold/Review/Confirm을 완주한다. |
| 동시 수정 | `ui-conflict2.log` 공통 포함3개 PASS. 동료가 implementation 설명을 먼저 Save한 뒤 오래된 target 계획을 거절하고 양쪽 원래 ABI·동료 checkpoint·본인 입력을 cold에서도 보존한다. peer 저장을 되돌리지 않는다. |
| 취소 | `ui-cancel.log` 공통 포함3개 PASS. 모달 취소와 실제 원본 Undo 뒤 cold에서도 wrapper 계획이 사라지고 모든 원래 graph/핀/소스가 유지된다. |
| 두 번째 target 오류 | `ui-invalid.log` 공통 포함6개 PASS, `/tmp/confectory-multi-abi-kw2qc2qe`. 실제 전송한 windows 계획의 계약 지문만 위조하여 common/import도 전체 미적용임을 확인하고, 올바른 원래 입력으로 cold 재시도·Confirm을 완주한다. |
| 기존 계약 회귀 | `legacy-root.log` 5개, `legacy-call.log` 4개 순수 PASS. 기존 3/4 그룹과 단일 호출의 보호를 유지한다. `legacy-saved-copy2.log` 실제 엔진/화면9개 PASS(`/tmp/confectory-saved-copy-abi-7lbzlgub`): 기존 단일 저장 copy의 갱신/거절/cold/receipt/Review 취소/명시 compiler Confirm. |

정상 및 재시도 Confirm에서 기존 파일 중 변경은 `Caller.celem`, `common.graph.json`, `windows.graph.json` 세 개뿐이다. 함수·공유 callee·두 code record·다른 소스 byte는 유지한다. 모든 Save/실패/취소/Review 취소에서 원본은 반영하지 않는다. 화면 캡처 `explicit-all-targets.png`는 실제 갱신 입력을 가진 기존 Blueprint 창이다. 전체 v536 pixel equality나 모든 모바일/네이티브 문맥을 재검증한 것은 아니다.

초기 fixture의 PrepareFeature는 이미 provide가 있는 함수 생성을 거절했고, 함수와 새 body의 원본 문법을 수정했다. 초기 all-target read가 자신의 공유 그룹을 다른 생산자 그룹으로 취급하던 문제는 실제 source/group 검사로 수정했다. conflict의 `consumer_error`는 실제 거절과 상태 보존을 확인한 뒤 위 안내로 연결했으며 검사를 제거하지 않았다. 기존 저장 copy fixture는 필요한 `CONFECTORY_DOTNET` 환경을 지정해 실행했다. 중간 실패를 최종 통과로 집계하지 않는다.

## 정확한 미지원 범위와 다음 단계

- 이번 실제 UI 수용은 **소유 ordinary root, 두 Blueprint target, 각 target당 같은 callee 호출 하나, context 없는 code node, common/long 값↔ref**다. 후보는 최대8개 target을 검증하지만 실제8-target/모든 native type 조합을 검사한 것은 아니다.
- opaque C# target, 상속 implementation, private/nested/copy root, implementationContext를 가진 whole-body code, target마다 다른/여러 동일 callee 사용, 이름·순서·타입·out·반환 변화, 외부/등록 callee의 all-target receipt는 계속 차단한다. 단일 target의 기존 등록 callable/저장 copy 지원과 구별한다. 미검증 slot 문맥을 이번 ordinary-root 화면 통과로 대표하지 않는다.
- 새 비공개 copy의 stale ABI는 `ImplementationCopy`가 선택 source/target과 현재 관측 closure를 재구성하고 `copyPreview`가 fingerprint 차이를 차단하는 별도 경로다. 과거 private snapshot의 provenance/원래 graph·record와 현재 callee receipt를 분리해 결부하는 seed/후보 계약이 필요하다. 기존 source 재독해 가드를 삭제하거나 stale donor를 자동 수정하는 방식으로 해결하지 않는다. 원본 donor가 실제로 invalid하면 최종 compiler 거절도 유지해야 한다.
- 넓은 혼합 Save는 `V536_ATOMIC_REMAINING_COMBINATIONS.md`의 고정 목록으로 분리한다. 이번 계약으로 그 차단을 해제하지 않는다.

## 빌드·패키지

Release 전체 솔루션 0 warning/0 error(`solution.log`), metadata helper 0 warning/0 error(`metadata2.log`), 실제 Linux 엔진 `engine4.json` 빌드가 통과했다. JS 문법·Python 구문·diff 공백 검사를 통과했고 변경 JS 하나의 canonical pin을 갱신했다. UI 리소스는 기존 68개다. 게시 후보 14개는 구현9/테스트2/문서3이며 생성물·로그·사용자/인증 파일을 포함하지 않는다. 패턴 검토에서 추가 검토 대상 비밀 패턴은 없었지만 모든 비밀 부재의 절대 증명은 아니다.

Windows x64 교차 패키지: `/workspace/artifacts/Confectory-v536-multi-target-abi/Windows-x64/Confectory.exe`. 전체 폴더를 유지하고 exe를 연다. .NET Desktop Runtime10 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다. 선언 파일2310개/marker 포함2311개, 131586202byte. marker SHA256 `08094781241ad9e149340bf4feacb10c7af730f696da8689fa2fd224039a0a41`, 전체 파일별 목록 checksum `5e81af1ff5be3fc5d67fe024609579efd43753a4c130983ff94cb01f5677177d`. 목록은 scratch의 `review/PACKAGE_SHA256SUMS`에 보관했다.

`desktop_package.py`는 SDK 없는 managed runtime/다른 cwd에서 실제 packaged 엔진 웹을 시작하고 fixture 프로필 재사용/override·68리소스·최소 연결 화면·변조/의존성 누락 거절을 확인했다(`package-probe.log`, `/tmp/confectory-desktop-package-xzkj3rwc`). Windows apphost/WebView2/네이티브 입력·사용자 계정/유료 추론은 실행하지 않았다. Library discovery 장애에 새 복구 근거가 없어 업로드를 반복하지 않았으며 로컬 산출물은 전달된 첨부가 아니다.

코드 커밋 `b64145e3038043c299e2822c78265b85da427a33`의 깨끗한 별도 checkout에서 Release 솔루션 0 warning/0 error, 새 Linux 엔진 빌드가 통과했다(`checkout-solution.log`, `checkout-engine.json`). 실제 Git CRLF 속성 pull 후 retained 창과 fresh LF 창에서 68개 canonical/exact 리소스 및 내용/encoding/BOM/binary/budget 변조 거절·원본 byte 보존을 확인했다(`checkout-resources.log`). 두 작업 트리가 깨끗했고 패키지의 변경 구현 소스9개는 코드 커밋과 byte 동일했다(`package-code-proof.json`). 이 마무리는 문서만 갱신하므로 통과한 코드 검사를 반복하지 않았다. 원격 게시 대상은 승인된 `https://github.com/jorodane/Confectory.git`의 `work/current`만이며 main/Android/원본 reference ZIP은 변경하지 않는다.
