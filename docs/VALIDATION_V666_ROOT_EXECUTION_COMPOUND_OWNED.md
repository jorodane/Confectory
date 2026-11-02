# 다른 소유 함수를 함께 호출하는 M12 거래

## 원래 흐름과 변경 경계

v666 `dist/blueprint.js:248`은 한 동작의 결과 분기를 처리한 뒤 원래 다음 동작으로 이어 간다. 따라서 다른 직접 소유 함수가 같은 호출자의 import에 있다는 이유만으로 공개 분기 편집 전체를 막는 것은 원래 사용자 흐름의 누락이다.

직접 소유한 동기 void 함수의 기존 target·명시 직접 호출자 거래를, 다른 직접 소유 함수 계약을 함께 사용하는 ordinary caller에 연결한다. 추가 계약 헤더는 변경하지 않는 관측 멤버다. 같은 qualified namespace·기존 import와 provider 선택을 사용하며 자동 대상 선택이나 새로운 권한을 만들지 않는다. 독립적으로 수정 중인 추가 계약은 먼저 확인하도록 거절하고, 영수증·원문·기존 호출/핀/연결·C#과 readonly 파일 모드를 보존한다.

추가 헤더를 포함한 완전한 그룹과 최초 관측 해시를 저장·복원·Review·최종 CAS에 결합한다. 누락/변조 영수증이나 추가 계약의 draft 변경은 거절한다. 기존 다른 호출의 결과·후속 동작은 원래 순서대로 유지하고, 사용자가 명시한 공개 분기 반환 연결만 실행 경로를 바꾼다. 레이아웃·공개 IO·override 계약은 바꾸지 않는다.

## 최종 검증

제품 source는 `af2786571ecb04b1665566174806b1fc7118bf14`다. 이후 수정은 결과 문서뿐이다. 독립 no-hardlinks LF/CRLF checkout·별도 home/NuGet·빈 엔진 캐시에서 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계**를 통과했다. 이번 최종 실행의 검사 재사용은 없다.

- Core/runtime 39개와 소유 경계 2개씩, 총82개를 양쪽에서 새로 실행했다. 이전 제품의 Core 파일 SHA만 같은 것을 native 실행으로 세지 않는다. 이 검사들은 위 44단계에 포함된다.
- ref int/out long/out string과 다른 int 반환 함수를 함께 사용하는 실제 owned 프로젝트의 추가 import·명시 caller·원자 후보/전체 Review·취소/Undo/Redo·storage/conflict/loss/late·cold 복원/실행을 확인했다. 이 복합 Root의 별도 독립 창은 새 검증하지 않았다.
- 추가 헤더의 그룹 누락·draft 변경·관측 영수증 누락/변조, Save 전 원문 변경과 Review 이후 헤더 변경은 입력/체크포인트/원본을 보존하며 거절했다. readonly 헤더/provider/C#의 0400 모드와 원문을 보존한다. 결과 분기의 명시 반환과 연결되지 않은 분기 뒤 원래 다른 호출·typed 데이터 소비를 실제 실행으로 구별했다.
- 기존 추가 import 없는 typed out/ref API/화면, 등록 외부 새 copy/저장 copy와 M11·실제 CommitPlan 읽기 CAS도 신규 회귀로 확인했다. 소유/외부/override 경계와 레이아웃을 완화하지 않았다.
- 집중 10단계의 원본 증거와 진단 실패 `release, compound-api`를 보존했다. Hash helper 누락을 수정했고, 두 번째 Review의 실패 checkpoint를 첫 Review 기준과 비교한 fixture 오류는 그 Review 직후 IDs/체크포인트를 고정해 수정했다. 후자는 제품 코드 변경 없이 집중 API·화면에서 재검증했다. 실패를 최종 통과에 섞지 않았다. 집중 증거와 동결 source를 대조할 때 호환성 안내 한 문장의 추가만 문서 차이로 확인했다. 코드·테스트·harness는 동일하며 최종 독립 검사는 그 안내를 포함한 동결 commit에서 새 실행했다.
- 새 Windows 교차 패키지·생성본 normal, 전체 SHA/CRC·파일/디렉터리 권한 복원·복원본 late와 실패/예외 수명관리를 새 검증했다. 실제 Windows apphost/WebView2·모바일 실행, 전체 UI/Space/Library 검증은 아니다.

## 지속 보관과 공간

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `af2786571ecb04b1665566174806b1fc7118bf14` | `8d6197de7c33661b8c8f926eea905abd499b6631567cc867b273a1b2bd7bae62` | `cb8ca0cf42837d3f6f0284835680b0498889292b0b52d6479e753717b1f8ab4c` | 51337355 / 2370 / 147 |
| 정상 롤백 | `1326a19cc7e32fa0c0b15e520d153324ec2f60dc` | `75e7f77c5d990894c10d0264c9692ce53b6edaab00553b87cb321815898b1c78` | `8b5fab7097c0100edffde538eaefdc18e9ef70387d6494b90872d29cc8f34f51` | 51337765 / 2370 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 복원/실행은 신규 검증이고 롤백 실행은 이전 정상 근거를 재사용하며 압축 SHA를 재확인했다. 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/057e686e94824dc69aa4a76813c7fc52.zip`(SHA256 `0e19497c426c01ecd3009869eafbbaeb15c6f462bb1df802947effc592048311`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/3323a4df866043dc86d29c5e0b092395.zip`(SHA256 `d504ae35ef67bba41053cd667377d50b57bdcfd8d8f0a81beda35f699af670bb`)와 입력·로그·프로필·스크린샷·manifest를 지속 보존했다. child 종료·증거 보관·소유권 확인 뒤 이번 두 RAM 공간만 정리했다. 승인된 관리 최신/롤백 승격 외의 과거 자료·SDK·원본·캐시·사용자 데이터 삭제는 없다.

집중 디스크 1913.70→1913.09MiB(순증가 0.61MiB), 최종 1912.85→1908.39MiB(순증가 4.46MiB), 수집 시 여유 1908.39MiB다. stage 표본 최소 여유 1912.79MiB, 관측 cgroup memory peak 4113.39MiB다. 기존 persistent144MiB(안전64MiB 포함), RAM3GiB+512MiB, memory7GiB+1GiB 기준을 낮추지 않았다. 다음 실행의 증가량을 보장하는 값이 아니다.

## 유한한 잔여

이 단위는 다른 import의 모든 문맥을 자동 지원한다는 뜻이 아니다. 중첩/private 호출, 등록 외부 import의 readonly receipt와 여러 provider의 계약 변경을 포함한 완전한 복합 closure는 같은 기존 M12 항목의 잔여다. 부모/참조 원본 직접 쓰기·공개 override 계약 변경은 정상 보호다.

비void의 값 반환은 별도 저장/표시 연결이 필요하다. 기존 private 호출의 `native-return-out-v1`처럼 원래 Invoke와 C#를 보존하는 별도 결과 어댑터는 내부 구현 선택이며, 임의로 반환 값을 버리거나 본문을 enum/tuple 반환으로 다시 쓰지 않는다. M4의 동기 IInvoke 소비자/async provider 호환성은 사용자 결정 대기이며 이 동기 거래와 독립적이다.

이전 authoring 패키지는 이 추가 import 그룹의 미확정 checkpoint 편집/복원을 지원한다고 보장하지 않는다. 최신/롤백의 source와 전체 manifest를 보관하고 기존 checkpoint를 자동 삭제·승격하지 않는다.
