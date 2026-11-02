# 동기 void의 typed out·ref와 공개 실행 분기

## 원래 요구와 지원 의미

저장소 v666 `dist/app.js:2469–2476`의 원계약 우선과 `dist/blueprint.js:248`의 출력 발행 → 결과 분기 → 다음 동작 순서를 따른다. 기존 `IInvoke`/`IExecutionInvoke`는 같은 value/ref/out 인수를 이미 타입 그대로 전달한다. 이번 변경은 정수 out 하나로 제한하던 수용 검사를 동기 void의 기존 value/ref/out 계약으로 확장한다. 공개 C# 원문을 다시 쓰거나 새로운 반환 tuple/타입을 도입하지 않는다.

직접 소유 함수와 명시한 Blueprint target·직접 호출자에 공개 분기를 정의하고, 여러 typed out과 실제 ref 저장소 변경을 분기 전에 전달한다. ref는 기존의 쓰기 가능한 정확한 타입 저장소만 허용하며 상수·타입 변환을 참조로 취급하지 않는다. 연결되지 않은 종료점은 기존 None/출력 기본값 규칙을 사용하고 예외를 실패 분기로 치환하지 않는다. 원본 ID/연결·배정·권한·Review/Confirm·최종 CAS와 레이아웃은 유지한다.

ordinary 비void 반환과 실행 분기를 함께 전달하는 어댑터, 복합 호출 계약 closure와 M4는 별도 실제 잔여다. 부모/외부 원본 쓰기와 override 계약 변경은 정상 보호이며 새 독립 계약 복제·구형 profile 자동 승격은 추가하지 않는다.

직전 패키지는 공개 분기 계약에서 정수 out 하나만 수용한다. 이번에 만든 ref/여러 typed out의 공개 분기 metadata를 그 롤백 실행기로 읽을 수 있다고 보장하지 않는다. 기존 원본을 재작성하거나 새 metadata를 지워 호환시키지 않으며, 최신·정상 롤백 패키지의 source와 manifest를 구별해 보관한다.

## 최종 검증

제품 source는 `1326a19cc7e32fa0c0b15e520d153324ec2f60dc`이며 이후 수정은 결과 문서뿐이다. 독립 no-hardlinks LF/CRLF checkout·별도 home/NuGet·빈 엔진 캐시에서 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계**를 통과했다. 이번 최종 실행의 검사 재사용은 없다.

- Core/runtime 39개와 소유 경계 2개씩, 총82개를 양쪽에서 새로 실행했다. 같은 셀을 가리키는 두 ref와 out long/string이 성공/실패 분기·다음 동작보다 먼저 반영되고, None은 임의 분기를 선택하지 않으며 ordinary Invoke·원래 C# 바이트를 보존한다. 빈 Root의 long/string 기본값과 ref 보존, 상수/다른 타입 ref 거절, 비void 거절·기존 예외 전파도 실제 실행/진단으로 확인했다. 위 44단계에 포함된다.
- 새 ref int/out long/out string의 직접 소유 함수와 명시 직접 호출자는 원자 후보 저장, 부분 Review 거절, 물리 원문/최종 CAS 경합, 반복 receipt 조회, cold 재시작, 출력 카드·기존 C# 바이트 보존을 API로 검증했다. 화면 normal/cancel/storage/conflict/loss/late는 실제 클릭·명시 분기 선택·호출자 연결·Undo/Redo·입력/늦은 입력 보존·Review 취소/Confirm·실행을 새 검증했다. 이 typed-root의 별도 독립 창은 새 검증하지 않았다.
- 기존 int out API/화면, 등록 외부 새 copy/저장 copy, M11 종료점/등록 부모와 실제 Review/Confirm/CommitPlan 읽기 CAS도 관련 회귀로 새 실행했다. M11의 선택적 확장이나 새 문맥 조합을 추가하지 않았다.
- 집중 실행 13단계의 실패 포함 증거를 보존했다. 실패 `native-data, data-ui-normal`은 최종 통과에 섞지 않았다. 첫 거절 검사는 바인딩 검증 전 introspection 단계에서 진단을 요구한 테스트 오류였으며 실제 records를 제공한 describe 검증으로 수정했다. 화면의 고정25% 클릭은 늘어난 출력 카드가 사이드바 뒤에 놓여 실패했고 원본 전체 보기 동선으로 검증했다. force click·레이아웃·제품 코드는 이 두 진단으로 바꾸지 않았다. 집중 native 11개·API·화면 통과 뒤 제품을 동결했다.
- 새 Windows 교차 패키지와 전체 SHA/CRC·파일/디렉터리 모드 복원, 생성본 normal/복원본 late hosted UI, 실패/예외 수명관리도 새 검증했다. 실제 Windows apphost/WebView2·모바일 실행이나 전체 UI/Space/Library 검증은 아니다.

## 패키지·증거·공간

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `1326a19cc7e32fa0c0b15e520d153324ec2f60dc` | `75e7f77c5d990894c10d0264c9692ce53b6edaab00553b87cb321815898b1c78` | `8b5fab7097c0100edffde538eaefdc18e9ef70387d6494b90872d29cc8f34f51` | 51337765 / 2370 / 147 |
| 정상 롤백 | `9df807847f259e77e1788a2a2cfa6346cdd4e66b` | `130fdd42a44c1834b007d1adac1cdf908a3907b01a53c27edf2fdca38f988d53` | `47674b9919454f0341f891fd594405f8cf63e817e803a4e54db1240660ff44e5` | 51335454 / 2370 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 실행/복원은 신규 검증이고 롤백 실행은 직전 정상 근거를 재사용하며 압축 SHA를 다시 확인했다. 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/6aa116ffe9b0402e8256e5f62da55fe9.zip`(SHA256 `99c56a3584610103c4ad43747753168b6e5cfb22f4a562905ac69a7f97c56626`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/262140b803e3403995f674f7f7dcf1f6.zip`(SHA256 `59581d3afa374f62e4fc6dd6af385a84457fe7926d7dcb87c5bfb2087397e443`)와 실패 입력·로그·프로필·스크린샷·manifest를 지속 보존했다. 자식 종료·증거 보관·소유권 확인 뒤 이번 두 RAM 작업공간만 정리했다. 승인된 관리 패키지의 최신/롤백 승격 외에 과거 자료/SDK/원본/캐시/사용자 데이터 삭제는 없다.

집중 디스크 1918.77→1918.18MiB(순증가 0.59MiB), 최종 1918.03→1913.78MiB(순증가 4.25MiB), 수집 시 여유 1913.78MiB다. stage 표본 최소 여유 1917.96MiB, 관측 cgroup memory peak 4092.80MiB다. 추가 persistent144MiB(안전64MiB 포함), RAM3GiB+512MiB, memory7GiB+1GiB 기준을 낮추지 않았다. 다음 실행의 순증가를 보장하는 값은 아니다.

## 실제 잔여

ordinary 비void의 값과 공개 분기를 함께 전달하는 어댑터, 복합 호출 계약의 완전한 명시 대응, 별도 M4는 [유한한 ABI/비동기 경계](M12_DATA_ABI_AND_M4_BOUNDARIES.md)에 남긴다. 이번 동기 void 전달에는 새 사용자 정책 결정이 필요하지 않다. 정보 종류의 CLR 표현과 동기 IInvoke 소비자/async provider의 실제 호환 선택은 별도 검토 대상이며 임의 확정하지 않았다. 부모/참조 원본 쓰기·공개 override 계약 변경은 정상 보호다.
