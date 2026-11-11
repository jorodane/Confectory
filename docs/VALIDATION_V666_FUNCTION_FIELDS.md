# 정보 함수 필드 검증

[지원 범위](V666_FUNCTION_FIELDS.md)의 제품 구현 d9986adb15bc796821b4594071f7ed2b53782b48의 source를 유지하고,
fixture 경로 보정을 포함한 검증 기준을 `cad5653e603e5bd29ee2e3a5f3d0ffbfe4a46054`에 동결했다.
최종 **신규 24단계·동등 재사용 14단계·총 38단계·실패 0**을 통과했다. 후속 결과 문서 커밋은 제품·
실행·검사 코드를 바꾸지 않는다. `tools/verify_desktop.py --suite function-fields`, 공개 SDK
`/workspace/toolchains/dotnet-10.0.401`과 기존 NuGet seed를 사용했다.

| 최종 범위 | 신규 | 동등 재사용 |
| --- | ---: | ---: |
| LF 독립 checkout·빌드·native/API/UI·배열 및 이전 모듈 회귀 | 7 | 7 |
| CRLF 독립 checkout·빌드·native/API/UI·live compound 보호 회귀 | 7 | 6 |
| 관리 IPC 실패/수명 | 0 | 1 |
| 새 교차패키지·무결성·패키지 UI·전체 ZIP 복원·native/API/실패 수명·정리 | 10 | 0 |

native probe의 내부 14개 확인 및 UI 내부 체크를 단계로 부풀리지 않는다. 첫 동결의
LF/CRLF·패키지 등32단계 통과 뒤 전체 복원 native 검사가 패키지에 없는 tests/fixtures를
읽어 FileNotFoundError로 중단됐다. 원래 기록
`/workspace/artifacts/v536-verification-managed/runs/6c2809e083794512a5c02ce49719e677.json`
및 증거 ZIP SHA256
`a7faff7fe8c5b31f60d4db3b67bcb1fd835cbb20ae05a7b81cfa3eb7716c1798`을 보존한다.

fixture의 기준 파일 경로를 검증 checkout에서 명시 전달하도록 수정했다. 제품/다른
검사 source, 명령, SDK/NuGet/config/RID 및 passing import closure가 동일한14단계만
원래 독립 LF/CRLF 증거에서 재사용했다. exact source diff·기존 결과/ZIP·실패 지점과
변경 SDK/제품 거절을 `verification_function_fields_reuse.py`가 검사한다. 변경 native 검사,
모든 빌드·패키지·전체 복원·실패 수명은 새로 실행했다. 재사용 체크별 이전 source/record/
archive hash와 검증 근거를 새 증거의 `function-fields-reuse.json`에 보존한다. 실패한
검사는 재사용하지 않았다. 개발 25회는 최종 합계에 중복 합산하지 않는다.
개발 fixture 3회는 reflection nullable unboxing 경고와 CS0029/INFORMATION_CLR_CYCLE
예상 진단명 오류였다. 실제 거절은 기존 CS0266/STRUCTURAL_CYCLE 검사에서 발생했다.
fixture만 수정하고 엄격한 컴파일러·구조 검사를 유지했으며 모든 실패 로그를 보존했다.
제품의 자기 타입 callback 및 최종 native/UI 검사는 새 코드에서 통과했다. 개발 UI 뒤
함수 reference 타입 관찰 순서를 수정한 부분도 최종 LF/CRLF와 복원본에서 새로 검사했다.

게시본 155cbe58adb48e8db635fe0fbe5092d4b1482179의 함수 필드 생성 거절을 재현했다.
기존 live 접근 descriptor는 보관된 게시 runtime
f73f1b5098cb540dbb6e3a7fea9983320386df13의 실제 element-authoring host를 해시 검증 후
소유 임시 폴더로 추출해 새로 질의했다. 원래 ZIP·DLL 해시와 질의·golden을 개발 증거에
보존했다. 이 이전 버전 실행은 비교 입력이며 기존 통과 증거 재사용으로 합산하지 않는다.
함수를 담은 compound의 종전 unsupported descriptor는 byte-equivalent하게 유지한다.

실제 CLR에서 IInvoke/IAsyncInvoke 필드·배열을 호출자 소유 provider로 명시적으로
초기화했다. struct 복사·배열 공유·원래 struct를 제거하고 GC를 수행한 뒤에도 같은 함수
객체 및 provider의 호출 상태를 유지한다. 기본 필드·배열 및 배열의 null 원소는 원래
C# 의미다. 반환/out·원래 공개 실행 분기와 async DTO를 보존하고 async 완료 전에는
결과를 발행하지 않았다. 동기 native/명시 base 호출은 CS0619, 다른 함수의 암시적 handle
대입은 CS0266으로 거절했다. 자기 struct를 인자·결과로 쓰는 async callback도 실제 실행37과
반환 handle·배열 정체성을 확인했다. 실제 inline compound 순환은 STRUCTURAL_CYCLE로
거절한다. provider 선택·구현 ID 로딩·소유/Dispose/lease 정책은 추가하지 않았다.

같은 pack과 등록된 분리 정보/함수/value pack에서 실제 assembly identity 및 링크 DLL
해시를 확인했고, 임시 선언 DLL은 실행본에 넣지 않았다. 깊은 정보 변경으로 함수·정보
산출물이 무효화되고 정확한 복원으로 이전 캐시 키를 회수했다. 표시명·분기 번호/ID와
기존 배열·모듈 source/profile/hash 및 live compound의 값 복사/참조 보호 회귀도 새로
검사했다. 등록 dependency 부재를 거절하고 외부·부모·원본 C# bytes를 보존했다.

기존 460px 본문 UI에서 명시 함수 필드 호출을 편집·저장했다. 취소·Undo/Redo·미저장
cold 복원·실패 입력 보존·재시도·중복 Save 비활성 및 Review/Confirm 후 실행31을 확인했다.
함수 계약 원문을 Save 전 및 Review 후 변경하면 최종 CAS가 후보·원문·peer를 보존하며
거절한다. 정확 복원과 새 Review/Confirm은 성공했다. 실제로 apply/settled 응답을 가린
검사는 재시작 후 저장 결과를 회수하고 중복 apply를 내지 않았다. 응답 중 늦은 이름도
재시작 및 명시적 두 번째 Save까지 보존했다. 새 패키지와 전체 ZIP 복원본에서도 해당
native/API/UI·실패 수명 검사를 새로 수행했다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/e179088199fd4d658d2569089faaf608.json`
- 개발 증거 ZIP SHA256: `dc3b3583d25a3d5b4ce1a08844451aec9eb07f76dd631d26d32234cea5c25be0`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/b798d13afdc8406db3f42f03e3886d13.json`
- 최종 증거 ZIP SHA256: `24378383ac8c1ff812740e71b57cc5a7d5d9e7e621e98453a4957de49c3d5588`
- latest runtime: `cad5653e603e5bd29ee2e3a5f3d0ffbfe4a46054`
- latest ZIP SHA256: `2441ac98ab1dfb9bdfe7da28776472a48133190263c2e1ad5af8efbfbb9e4528` (54017825bytes)
- rollback runtime: `f73f1b5098cb540dbb6e3a7fea9983320386df13`
- rollback ZIP SHA256: `4bbf6b9a9d7f7813c9684c8157a72abc80270e3a148fb9d9b6422ee239fb99b8` (54008934bytes)

store는 `/workspace/artifacts/v536-verification-managed/packages`다. 검증 후 기존 2세대
보관 계약으로 latest/rollback을 승격하고 증거 ZIP·무결성을 확인한 뒤 소유 임시 workspace만
정리했다. 보관 직후 공간은 25468080128bytes (23.72GiB)다. 원래 checkout
b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee 및 main
0d2459b463798d11031c20f46a6c8d1a4ecc35dd를 보존한다.

Linux/.NET/Chromium 자동화 결과다. Windows 패키지는 교차 생성이며 실제 Windows·
물리 기기·화면/오디오·전체 UI 및 모든 구 reader 실행은 미검증이다. 초기 빈 화면 원인은
미확정이다. 정보의 live reference bridge/수명·reference 필드 및 선언 구현 ID와 실제
함수 handle의 명시적 live 속성 연결은 같은 고정9행의 유한 잔여다. 새 권한·자동 provider
선택·원문 재작성·살아 있는 AI 자격증명·유료 호출을 추가하지 않았다.
