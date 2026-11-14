# 입력 계약 변경과 import 관측 공동 저장 검증

동결 runtime `d2f0f488634c2e01b1c7c96442752949bce3a04c`의 [입력 계약·import 관측 공동 저장](V666_INPUT_IMPORT_OBSERVATIONS.md)을 최종 **신규 41단계·재사용 0·실패0**으로 검증했다. LF20·CRLF13·package/전체 복원8이며 개발 진단은 통과 수에 합산하지 않는다.

- 기존 long 입력을 string으로 바꾸는 두 소유 함수의 native 선언·수동 C# 본문·공유 caller 값/명시 해제를 한 후보로 결합했다. 함수 순서를 바꿔도 후보와 원래 source hash가 같았다.
- 한 함수의 소유 helper와 다른 함수의 등록 helper/부모를 사용한다. 원래 실행79와 명시 편집 후 실행27을 확인했다. helper 별칭·typed import·계약·원문과 권한을 보존하고 외부 쓰기 멤버는 없었다.
- 누락/변조 registered proof·부모·읽기 경로/hash·body/caller/value/disconnect·foreign owned-unit 주장과 잘못된 마지막 본문은 전체 거절했다. 원본·checkpoint·입력을 유지했다.
- 실제 기존 상세창·타입/본문 편집 UI의 취소·Undo/Redo·미저장/저장 cold·한 Save·기본/독립 창·checkpoint 실패/재시도·응답 유실/조회 복구·프로젝트 왕복을 검사했다.
- cold와 owner/function metadata Save 및 늦은 설명/두 번째 Save 뒤에도 원래 외부 proof/read set과 소유 readGuards를 유지했다. 바뀐 외부 부모를 metadata-only Save의 새 기준으로 수락하지 않았다.
- Save 전 및 Review 뒤 외부 함수·부모·등록 manifest 변경은 Confirm을 차단했다. 소유 helper 본문 경합도 차단했다. 원문 복원 뒤 명시 새 Review/Confirm으로 실행27과 helper/외부 파일 bytes·mode·inode·mtime 보존을 확인했다.
- 기존 입력 변경 native/guard/API와 같은 계약 registered body native/guard를 회귀로 검사했다. 새 package 구조/probe·정상 UI, 전체 ZIP 추출/hash/probe·응답 유실·늦은 입력·독립 창·실패 수명을 검사했다.

제품 변경은 InformationFunctionNativeInputs.cs 한 파일이다. 원래 선택적 dependencies를 입력 그룹 분류에 허용하고 기존 등록 조회/부모 proof를 readonly 계약 사전에 연결한다. 각 원래 단일 함수의 완전한 계약·C#/caller·dependencies 검증은 그대로 수행한다. 외부 선언은 owned units/write group으로 넣지 않고 provider 구현/본문을 계약 관측 대상으로 추가하지 않는다.

기존 version3 nativeBodyDependencies/nativeBodyDependencyReads·readGuards·source/read240·member64, 소유권/권한·Review/Confirm·최종 CAS를 유지한다. UI/레이아웃·리소스·C# 생성·공유 caller overlay·등록 loader/guard·whole/retained/private 계획은 byte 동일하다. 자동 source/값 변환·새 등록/권한·schema/receipt version 변경은 없다. 정보별 struct·종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류와 override 계약을 유지한다.

개발 15단계·실패 0건의 로그/결과를 보존했다. 별도 pending guard 진단에서는 프로젝트 확장자를 .cpack으로 가정한 경로 선택이 한 번 실패했다. 실제 ProjectManifest의 .cproj 경로와 원래 baseline hash를 확인해 미실행 진단만 이어갔고, 이미 통과한 native/UI 검사는 반복하지 않았다. 이 fixture 진단 실패를 제품 검증 실패나 최종 통과 수로 합산하지 않았다. 게시 기준의 각 single 후보와 원래 실행79는 유효하지만 공동 후보만 거절됨을 먼저 재현한 뒤 구현했다. 동결 source의 최종 검사는 모두 신규다.

직전 package `ea57f92f3662f24de130936cd839510cb042487e`의 전체 파일/hash를 별도 추출했다. 각 single 후보와 실행79는 유효하지만 공동 input/import Save는 거절하며 UI 입력·checkpoint·외부 원문/권한을 보존한다. 직전 reader의 순수 pending guard 수용은 `False`였다. 이 guard 진단을 이전 전체 UI의 cold/Review/Confirm 교환 완료로 확대하지 않는다. 같은 세대 authoring/runtime을 사용하며 자동 migration/downgrade나 구 Reference parser 변경은 없다.

Linux 실제 .NET/portable 실행·Chromium 자동화다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증은 하지 않았다. 과거 간헐 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | d2f0f488634c2e01b1c7c96442752949bce3a04c | 24bb1710d9415e7e4f705e96ba556605f19307beab4c1c0f9f816501f387570f | 54132868 |
| rollback | ea57f92f3662f24de130936cd839510cb042487e | 1baf60e794bfc8d902527161a8464678bf2139e720529597380e74d49b06bebf | 54133144 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/9f08fdb895ca48cd863458691cf38a0c.json` · evidence SHA256 `7cb32b54e79c6e087b7a32c050659e7781eab49fc5cb9fa321035ba863be0314`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/9702aba536ad45c6a4da7e6136a5c63c.json` · evidence SHA256 `28a394fd8ea00f6ba335645b6c97b32758796c806b6930fcaff0a2efc0d08814`.
두 package와 두 evidence archive hash를 재확인했다. 등록된 이번 소유 임시물·기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·과거 증거를 보존했다. 디스크 여유 24417218560bytes(22.74GiB)다.

이 입력 계약·안정된 helper import/외부 관측 한 흐름을 닫는다. 선택 native callee가 다른 선택 callee의 변경되는 계약을 import하는 실제 source/계약 결합은 별도 유한 잔여다. 기존 callee+consumer·opaque/private/whole/override 보호를 임의 해제하거나 타입/문맥별 모든 조합을 새 의무로 늘리지 않는다. main은 사용자 검토/merge에 남긴다.
