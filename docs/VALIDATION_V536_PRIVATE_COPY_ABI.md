# v536 새 비공개 복사 초안의 ABI 갱신

2026-10-23, `04a6b0a` 이후의 한정된 연결이다. UI 기준은 지정된 저장소 `196c605`의 v536이며 HTML/CSS 배치나 새 실행 의미를 바꾸지 않았다. 전체 v536 복원이나 Windows 실기기 수용을 뜻하지 않는다.

## 문제와 결과

이전 `readImplementationCopy`는 선택한 donor와 현재 callee를 매번 읽어 복사 내용을 다시 만들었다. callee가 바뀌면 미저장 copy의 fingerprint가 달라져 거절됐고, 저장된 직접 배치 copy용 `rebindCopyAbi`를 새 비공개 선택에 그대로 적용할 수 없었다.

이제 최초 명시적 선택의 원래 내용은 별도의 불변 snapshot으로 보관한다. 복사할 공개 기능·소유자·target·출처 네 필드·새 구현 선언·graph·모든 record·원래 계약과 관측 증거를 기존 작업 checkpoint의 private metadata에 묶는다. 실제 source 등록이나 다른 미저장 source의 Save는 하지 않는다. 현재 callee와 직접 등록 receipt는 별도로 읽는다. 기존 갱신 버튼을 명시적으로 눌렀을 때만 원래 snapshot과 현재 계약을 함께 검증한 새 후보를 준비한다. donor의 새 본문을 복사 초안의 원래 본문으로 바꾸지 않는다.

지원하는 갱신은 선택한 단일 Blueprint target의 단일 wrapped call, 같은 인자 이름/순서/타입/out/반환의 값↔ref이다. code에 whole-body implementationContext가 없어야 한다. 실제 수용은 common/long 반환, 값/ref 입력과 기존 out long/bool 공개 기능을 사용했다. 소유 callee와 직접 등록 callable 각각 실제 UI로 확인했다. 다른 타입/형태의 전체 지원이나 등록 all-target ABI 수용을 뜻하지 않는다. 기존 C#·등록 팩·상속 donor의 **현재 유효한 복사**는 보존한다. C# whole-body의 오래된 ABI를 자동 재작성하지 않는다.

## 원자성·복원 경계

- `PrivateImplementationCopy`는 원래 snapshot을 검증하고 현재 소스는 registry의 정상 source/target/접근 규칙으로만 관측한다. 저장 metadata에 든 임의 path를 직접 읽지 않는다. 현재 source·scope·owner·callee·직접 등록 receipt와 명시적 계획이 다르면 거절한다. source/typed import/wrapper/모든 record의 최종 후보를 함께 검사한다.
- 기존 `SlotBatch`/`Save.ApplySlots`의 후보·CAS·receipt로 새 copy 등록, owner 제공 관계와 최소 혼합 변경을 한 번에 저장한다. 하나라도 실패하면 모두 미적용이다. 성공 후보에서만 해당 private seed를 제거한다. `copySource` 네 필드는 불변이며 부모·등록 원본·다른 target을 쓰지 않는다.
- 초기 선택 metadata의 CAS는 **기존 저장 checkpoint**의 source/history를 그대로 보존한다. 다른 편집기의 서버 미저장 draft를 몰래 Save하거나 버리지 않는다. owner의 공유 draft는 먼저 저장된 상태여야 하고, owner의 화면 private 설명/기존 단일 primitive 값은 기존 최소 혼합 저장에 결부할 수 있다.
- 기존 사용자 선택을 새 동의나 권한으로 승격하지 않는다. seed가 없는 이전 copy 입력은 기존 content proof가 현재 내용과 일치할 때만 원래 snapshot을 처음 보관한다. 증거가 다르면 새 donor 내용을 이전 snapshot으로 간주하지 않고 입력을 보존한다.
- 취소는 저장 결과 확인·입력 동일성 검사를 거쳐 presentation의 취소를 보관한 **뒤에** 정확한 seed만 정리한다. 비동기 확인 중 새 입력이 생기면 취소를 거절한다. metadata 정리 실패 시 원본/source를 삭제하지 않고 임시 보관 정리 실패를 알린다. 이때 비활성 seed가 남을 수 있으며 자동 GC는 이번 범위가 아니다. 최대8개/합계16MiB, seed당2MiB의 보수적 제한을 유지한다.
- Review/Confirm, 실제 source 변경·소유권·등록 receipt·CAS 검사는 유지한다. 원래 donor 자체가 잘못된 경우를 새로운 copy 후보의 성공으로 숨기거나 원본을 자동 수리하지 않는다. 새 계정·Agent 동의·프로젝트 실행 권한은 추가하지 않는다.

## 실제 검사

모든 자료는 별도 `/tmp` 프로젝트/profile/등록 팩이다. 실제 사용자 계정·자격 증명·유료 추론·사용자 프로젝트 실행은 하지 않았다. 아래 PASS 수는 스크립트의 검사 묶음 수이며 공통 준비를 중복 합산한 독립 시나리오 수가 아니다.

| 검사 | 결과와 범위 |
| --- | --- |
| `v536_private_copy_metadata.py` | 4 PASS 묶음. 원래 snapshot·명시적 후보·JSON cold identity, 잘못된 owner/project/identity/seed/계획/현재 source 변경 등10개 거절. 파일 쓰기 없는 helper 및 실제 compiler validate의 donor `CONTRACT_MISMATCH` 거절 검사 |
| `v536_private_copy_ui.py` normal | 실제 엔진/Chromium5 PASS. 선택 metadata only, 원래 본문·정확한64비트 입력의 cold 복원, donor와 callee가 독립 변경된 뒤 명시적 갱신+최소 혼합 Save, 저장 뒤 cold·Review 취소·실제 compiler Confirm. 기존 source 변경은 owner와 manifest뿐이며 donor/부모/Windows 본문 보존 |
| registered-callee | 실제5 PASS. 직접 등록 callable의 함수/manifest receipt를 계획에 결부하고 같은 전체 흐름 및 등록 팩 bytes 보존 |
| storage | 실제5 PASS(공통 준비 포함). checkpoint 쓰기 거절·전체 미적용·원래 seed/입력 cold 보존, 다음 명시적 재시도 수용 |
| response-loss | 실제4 PASS. 실제 성공한 Save 응답 유실, receipt 한 번 확인, 늦은 owner 입력 보존·cold 후속 Save·copy 중복 없음 |
| owner-conflict / callee-conflict | 각각 실제4 PASS. peer owner Save 또는 검토 뒤 실제 callee source 변경이면 전체 거절, peer checkpoint와 원래 seed/입력 cold 보존. 후자는 유효한 현재 선언의 변경을 사용하며 잘못된 fixture를 정상으로 만들지 않음 |
| cancel / cancel-late | 각각 실제4 PASS. 원본 취소·cold 원상태, 취소 확인 중 새 copy 입력이 생기면 취소 거절·원래/새 입력 cold 보존 |
| seed-storage / seed-response-loss | 각각 실제2 PASS. 최초 metadata 쓰기 실패는 반쪽 seed 없음. 실제 성공 응답 유실 뒤 동일 copy identity로 재시작 재시도, 원래 snapshot 한 개와 owner 입력 보존 |
| `v536_private_copy_checkpoint.py` | 실제 엔진3 PASS. 다른 서버 미저장 draft와 기존 checkpoint source/history 보존, 정확한 seed 정리, legacy content proof 일치만 migration/불일치는 생성 전 거절 |
| 기존 최소 혼합 API / 등록 팩 C# 복사 | 각각 실제5 PASS. 정확한64비트·10개 위조 거절·receipt·cold·Confirm, 등록 원본/외부 scope 보존·등록 변경 거절·cold 재시도·Confirm. 등록 팩 테스트는 현재 v536의 검색/Enter 열기 동작으로 진입하고 실패 시 checkpoint/새 membership도 검사 |

증거는 `/workspace/scratch/v536-private-copy/`의 각 로그와 checkpoint에 구분해 보존한다. 원본 비교 캡처는 정상 UI fixture의 `private-before-callee-change.png`, `private-explicit-abi-refresh.png`이며 배치 재설계를 하지 않았다. 이번은 기능 연결 수용으로 전체 화면 pixel equality 검사를 대신하지 않는다.

개발 중 실제 엔진에서 snapshot owner hash의 불일치를 재현했다. helper의 `Digest(string)`은 JSON 문자열 hash인데 기존 pack의 owner proof는 raw UTF-8 hash였다. snapshot owner hash를 기존 raw byte 계약에 맞춘 뒤 정상/기존 경로를 완주했다. 새 snapshot 검증의 namespace 조건도 원래 지원하던 등록 팩 공개 기능 복사를 유지하도록 고쳤다. 테스트의 화면 밖 refresh는 기존 overview로 이동한 뒤 클릭했고, 취소 경합은 원래 접기/펼치기로 두 창에 접근했다. 선택/소유권 검사를 우회하거나 force click으로 통과시키지 않았다. 초기 실패 로그도 남겼다.

## 빌드·산출물·한계

Release 전체 솔루션과 helper는 0 warning/0 error, 실제 Linux 생성 엔진이 통과했다. Windows x64 교차 패키지의 exe/apphost·WebView2 의존 파일·runtime/packs·68개 canonical/exact UI를 구성했다. `desktop_package.py`는 별도 cwd·설치 SDK 없는 managed 웹 시작, 변조/누락 의존성 거절, 기존 profile 재사용과 명시적 경로 override 보존을 통과했다. **실제 Windows apphost/WebView2/드래그/DPI/IME/더블클릭은 미검증**이다.

로컬 산출물: `/workspace/artifacts/Confectory-v536-private-copy-abi/Windows-x64/Confectory.exe`. 전체 폴더를 함께 둔다. .NET Desktop Runtime10.0 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않았다. 프로젝트 빌드에는 별도 .NET10 SDK가 필요하다. 로컬 산출물은 Library 첨부 전달 성공을 뜻하지 않는다. 기존 Library discovery 네트워크 장애에 새 복구 근거가 없어 반복하지 않았다.

넓은 혼합 Save는 `V536_ATOMIC_REMAINING_COMBINATIONS.md`, 전체 UI 잔여는 `V536_UI_CONNECTION_STATUS.md`의 최신 구분을 따른다. 원본 v536 레이아웃과 main/Android/원본 ZIP/사용자 데이터는 보존한다. 게시 대상은 승인된 `https://github.com/jorodane/Confectory.git`의 `work/current`만이며 정상 commit/push와 원격 SHA·깨끗한 checkout 결과를 최종 기록에 구분한다.

## 최종 재현 기록

코드 커밋은 `f426fcffc0d014a549873247701b0954bc65c2c4`다. 별도의 깨끗한 checkout에서 Release 솔루션 0 warning/0 error와 새 Linux 엔진 빌드가 통과했다(`checkout-solution.log`, `checkout-engine.json`). 실제 Git 속성 pull 뒤 retained CRLF와 fresh LF 양쪽의 68개 canonical/exact 리소스·내용/encoding/BOM/binary/budget 변조 거절을 확인했다(`checkout-resources.log`). 패키지의 변경 구현 source11개는 이 코드 커밋과 byte 동일하고 helper DLL도 최종 검증한 Release와 동일했다. 후속 변경은 검증 문서와 wrapper-only 갱신 시 원래 record가 그대로임을 검사하는 통과한 metadata assertion뿐이며 C#/UI/리소스는 바꾸지 않았다.

Windows 패키지는 선언 파일2,311개+marker로 총2,312개, 131,645,375 bytes다. marker SHA-256은 `fd2b4d4eaa8e458a62f4a326e82bc0477343f0d66da65531f581dd30ca1f623c`, 파일 목록 checksum은 `ffc52f1d70e44eac7e6981420ae7d82a65cd65e6f50407bbe47d2ce4e865c8c0`이다. `desktop_package.py`의 실제 managed 웹 시작 증거는 `/tmp/confectory-desktop-package-fu4j0n4e`다. Windows apphost/WebView2 실기기 검사는 아니다.

최종 검토 대상20개는 구현11/테스트4/문서5다. 비밀 패턴 추가 검토 항목0, 외부 임시 fixture를 필수 전제로 쓰는 테스트0이며 생성물·로그·profile·인증 파일은 Git에 넣지 않았다. 패턴 검사는 모든 비밀 부재의 절대 증명이 아니다. 진단용 임시 StartupHook도 scratch에만 있고 코드·패키지에는 포함하지 않는다.

부가적인 invalid-donor UI 실험은 이미 잘못된 프로젝트에서 정상 editor 재진입 hook을 기대하여 실패했다. 이를 정상 UI 복원 통과로 세지 않는다. 최종 검사는 해당 경계를 별도로 나누어 실제 compiler `validate`의 `CONTRACT_MISMATCH`와 donor 파일 위치, private 순수 후보가 원본을 쓰지 않는다는 점을 확인했다. 초기 로그를 지우거나 invalid 원본을 자동으로 고쳐 통과시키지 않았다. 최초 pure와 정상/등록 UI·저장·경합·취소 통과 기록과 구별한다.

정상 remote 게시 SHA와 두 checkout의 clean 상태는 완료 결과/checkpoint에서 직접 확인한다. 이 마지막 기록은 앞서 통과한 코드 검사를 불필요하게 반복한 결과가 아니다. 전체 UI 복원·일반 ABI·넓은 혼합 저장은 여전히 미완료다.
