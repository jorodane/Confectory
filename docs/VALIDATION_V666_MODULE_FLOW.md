# 모듈 공개 실행·async 연결 검증

[지원 경계](V666_MODULE_FLOW.md)의 제품·검사를 `f73f1b5098cb540dbb6e3a7fea9983320386df13`에 동결했다.
최종 **신규 38단계·동등 재사용 0·실패 0**을 통과했다. 후속 결과 문서 커밋은 제품·
실행·검사 코드를 바꾸지 않는다. `tools/verify_desktop.py --suite module-flow`, 공개 SDK
`/workspace/toolchains/dotnet-10.0.401`과 기존 NuGet seed를 사용했다.

| 최종 범위 | 신규 | 동등 재사용 |
| --- | ---: | ---: |
| LF 독립 checkout·빌드·native/API/UI·ordinary nominal golden·module core | 14 | 0 |
| CRLF 독립 checkout·빌드·native/API/UI·기존 named-type golden | 13 | 0 |
| 관리 IPC 실패/수명 | 1 | 0 |
| 새 교차패키지·무결성·패키지 UI·전체 ZIP 복원·native/API/실패 수명·정리 | 10 | 0 |

native probe의 내부 10개 확인과 각 UI 체크를 별도 최종 단계로 부풀리지 않는다. 이전
검사를 새로 실행한 경우와 이전 실행 증거를 가져오는 재사용을 구분한다. 이번에는
이전 실행 증거를 재사용하지 않았다. 이전 독립 상호 참조 실험은 제품 검사에 합산하지
않는다. 개발 19회 중 첫 native fixture 1회는 Task/LINQ namespace 누락과
기존 Branch 심벌 prefix 오류로 실패했다. 원본·컴파일러 로그를 보존하고 fixture만
수정했으며, 수정된 실제 native/등록 실행과 최종 동결 검사 모두 통과했다. 개발 실행은
최종 단계 합계에 중복 합산하지 않는다. 게시본의 MODULE_CLR_PROFILE 예상 거절도
보존된 baseline 재현이며 제품 성공 실행으로 바꾸어 표현하지 않는다.

실제 CLR에서 caller-owned module provider의 async Task 완료 전 결과 미발행, 완료 후
정확한 정보 struct 반환/out·원래 실행 분기, 동기 공개 실행의 enum out 및 비void 반환
capture를 검사했다. 동일 pack과 등록된 분리 value/method pack의 nominal assembly
identity와 실제 DLL 해시, 원문 보존, 공급자 미선택 및 기존 dependency 부재 거절을
확인했다. runtime에는 실제 Information/Contracts DLL만 들어가며 임시 선언을 링크하지
않는다. async 요구의 native/동기 실행 호출은 CS0619로 거절했다. 깊은 정보 변경으로
양쪽 DLL이 무효화되고 정확한 원문 복원으로 기존 캐시 키를 회수했다. branch 표시명
변경은 심벌·번호·shape를 바꾸지 않는다. 기존 basic/ordinary nominal source/profile/hash와
module 기본 계약·권한 회귀도 새로 검사했다.

기존 460px 본문 편집 UI에서 명시적으로 입력한 module execution 호출을 저장했다.
취소·Undo/Redo·실패 입력 보존·cold restart·중복 Save 비활성, 실제 Review/Confirm 실행을
검사했다. 요구 함수의 공개 branch 변경은 Save 전 및 Review 후 최종 CAS에서 거절하고
원문/peer/후보를 보존했다. 정확 복원 후 새 Review/Confirm은 실행31을 냈다. Save와
settled receipt 응답을 실제로 가린 검사는 재시작 후 기존 저장 결과를 회수하면서 두 번째
apply를 발행하지 않았다. 응답 중 늦은 이름 입력도 보존·재시작·명시적 두 번째 Save를
검사했다. 새 패키지와 전체 ZIP 복원본에서도 해당 native/API/UI 실패 수명을 새로 실행했다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/8d989e60bbba4dfaa8122bc3526121dc.json`
- 개발 증거 ZIP SHA256: `ca110a45412a2fd4f7402407e074f48aab2eb3daa58ae50e25234e591f9965c3`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/afc5b44b62274277a060bdcdb8e8a0a2.json`
- 최종 증거 ZIP SHA256: `24ac4168453443c650cded72c9088b1a2de8514ce833099cd938441b83d5dd35`
- latest runtime: `f73f1b5098cb540dbb6e3a7fea9983320386df13`
- latest ZIP SHA256: `4bbf6b9a9d7f7813c9684c8157a72abc80270e3a148fb9d9b6422ee239fb99b8` (54008934bytes)
- rollback runtime: `6e5f3e03ea53209f00edb4fae014185bb3a3a599`
- rollback ZIP SHA256: `e52561803d328fdb507562db1fa3011fb0fbfe03a8d53d5bb33c8e03bfe0d509` (53988947bytes)

store는 `/workspace/artifacts/v536-verification-managed/packages`다. 검증 후 기존 2세대
보관 계약으로 latest/rollback을 승격하고 증거 ZIP 및 무결성을 확인한 뒤 이 단위가
소유한 임시 workspace만 정리했다. 보관 직후 공간은 25480712192bytes (23.73GiB)다.
원래 checkout `b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee` 및 main
`0d2459b463798d11031c20f46a6c8d1a4ecc35dd`를 보존한다.

실제 실행은 Linux/.NET/Chromium 자동화다. Windows 패키지는 교차 생성이며 실제
Windows·물리 기기·화면/오디오·전체 UI 및 모든 구 reader 실행은 미검증이다. 초기화
빈 화면 원인은 미확정이다. 구 reader의 flow 생성 거절 경계는 baseline에서 확인했으며
자동 downgrade/migration을 추가하지 않았다. 정보 참조 bridge/수명과 reference/function
필드는 기존 고정9행의 유한 잔여다. 새 권한·provider 선택·C# 원문 재작성·
살아 있는 AI 자격증명·유료 호출을 추가하지 않았다.
