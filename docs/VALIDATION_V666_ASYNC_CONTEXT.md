# v666 M4 소유 native whole-body · 최종 검증

동결 코드 `b3fa243c68d5ca58604e206f24a2168b466eb57a`를 `tools/verify_desktop.py --suite async-context`로 검증했다. 소유 Root의 명시적 함수 전환이 대상이며, 원래 같은 클래스의 동기 Invoke·this/직접 재귀·scoped import·파일/멤버 위치·CRLF·native/void 반환·out을 유지한다. [지원과 유한한 후속](M4_ASYNC_CONTEXT.md)을 따른다.

## 최종 결과

| 구분 | 신규 단계 | 동등 근거 재사용 |
|---|---:|---:|
| 독립 LF checkout·캐시 | 18 | 0 |
| 독립 CRLF checkout·캐시 | 15 | 0 |
| 새 패키지·전체 복원·실패 수명관리 | 9 | 0 |
| 합계 | 42 | 0 |

Core/runtime은 LF 18개·CRLF 18개가 각각 신규 통과했다(실패·skip 0). 서로 다른 검사 개수와 같은 검사의 양쪽 checkout 실행 횟수를 구분한다. 후보 전용 pending caller 검사는 구조·원문을 끝까지 검사하되, 일반 Describe와 Assemble은 기존 동기 caller 오류를 유지하고 inspector가 실행 본문을 만들지 못함을 확인한다. 다른 인자 오류도 그대로 거절한다.

실제 API는 원문/핀/연결·out 이름 위치 대응, 함수 sync/async 왕복, 미전환 caller의 오류와 Confirm 컴파일 거절/입력 보존, 이후 명시 전환·전체 Review·scoped provider의 Review 이후 경합·최종 CAS·확정 후 실제 실행/cold를 검사했다. UI는 원본 메뉴·native 개별 전환 보호·원문 표시/취소·Undo/Redo·미리보기·저장 권한 실패·다른 caller 원문 충돌·유실 응답 재조회·늦은 입력과 별도 Save·Review 취소/Confirm·재시작을 확인했다. 기존 native 문맥과 ordinary 완료 어댑터·정상/늦은 원본 CAS probe도 신규 회귀다.

새 Windows 교차 패키지의 구조·현재 Core/authoring assembly 일치와 실제 packaged-engine UI/Task 실행을 확인했다. ZIP 전체 파일 SHA/CRC·모드/디렉터리 manifest를 확인하고 RAM에 전체 복원한 뒤 같은 native UI의 늦은 입력·저장 실패 및 Task runtime을 검사했다. package 실패/예외 수명관리도 신규 통과했다. 실제 Windows apphost/WebView2·모바일 기기 실행은 하지 않았다.

## 발견과 수정 · 재사용 구분

앞선 개발/실패 기록은 최종 통과 수에 더하지 않는다. 첫 API 왕복 fixture는 뒤의 전환에 의해 대체된 영수증을 settled로 기대했다. 최신 영수증을 조회하고 옛 영수증의 미정착을 확인하도록 수정했다. 오래된 schema-only CAS probe는 이후 추가된 property observation 호출을 예상 밖 의존성으로 거절했다. 속성이 없는 이 fixture만 명시적 빈 checks를 제공하며 다른 예상 밖 metadata는 계속 실패한다. 원래 실패 재현과 실제 Review/Confirm/CommitPlan의 정상·늦은 충돌·누락 proof·경로 탈출 4개를 보존했다.

늦은 입력 fixture의 첫 cold Save는 이전 저장 결과만 조회하는 경계였다. 다음 별도 Save는 새 입력을 한 번 저장한다. 이를 구분한 뒤, 공개 완료 계약이 생긴 함수를 재활성화할 때 아직 동기인 caller의 Describe 때문에 후보 자체가 막히는 제품 결함을 확인했다. 후보/영수증 전용 `inspectPendingAsyncCaller`는 이 상태만 `pendingAsyncCallers`로 표시하면서 다른 구조/원문 검증을 계속한다. 기본 화면·Assemble·Confirm 컴파일은 계속 거절한다. 사용자 caller/C#을 자동 변경하지 않는다. Review는 diff/소유 범위 검토이고 후보 컴파일은 Confirm에서 수행한다.

중간 복구 실행은 당시 코드가 동일한 LF 9단계 근거를 재사용했지만, 그 뒤 실제 Core/authoring 수정이 생겼다. **이번 최종 42단계에는 그 재사용을 적용하지 않고 전부 신규 실행했다.** 개발/중간 실패/진단 archive는 삭제하지 않았다.

## 보존 증거와 공간

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/bcef86b2bfa4408eb69a25ab79d4019b.json`
- 전체 증거: `/workspace/artifacts/v536-verification-managed/runs/bcef86b2bfa4408eb69a25ab79d4019b.zip` · SHA256 `832404e70fae207c972af03f5f58a9dcca007649b42e9f658592efb8a144f34d` · 3,974,096 bytes
- 최신 package source: `b3fa243c68d5ca58604e206f24a2168b466eb57a` · ZIP SHA256 `0c7326bd0b3ebd5fd9cefb23ee5a6ddb02040650c926d4e758bfe6a22ad171d8` · 51,480,284 bytes
- 최신 전체 manifest SHA256: `28c97486836c6f6efd1b56cef242dc9030468ff340bf394ff11e3931fe8b525e` · 파일 2,377개/디렉터리 147개
- 정상 rollback source: `76f9837d16bf8df822acbe2aa96d2e81de627aa7` · ZIP SHA256 `719fefc5f8222b28cbd1f09242aea990203b41b6132f97e2f372d813ca82a156` · manifest SHA256 `1c81cea88791ca30d329eeb0833f9cc6a2ad2568a54545a40e72a30ba4c60c39`
- 최종 실행 전 여유 1762.51 MiB, 종료 시 1757.64 MiB, stage 중 최소 1762.45 MiB. 필수 안전 여유 64 MiB는 낮추지 않았다.
- 이번 작업 전체 시작 여유 1769.58 MiB 대비 순증가 11.94 MiB. 실패 증거와 진단/개발 archive·Git 변경도 포함하며 이후 단위의 고정 증가량을 보장하지 않는다.

최신/rollback은 전체 검증 후 기존 관리 store의 원자 승격 규칙으로 보관했다. 로그·스크린샷·manifest·fixture 입력과 재생성 출력 목록을 지속 보존한 뒤 이 실행이 소유한 임시 checkout·캐시·패키지·복원본만 정리했고 임시 작업공간이 더 이상 존재하지 않음을 확인했다. 관리 store의 승인된 최신/rollback 교체 외에 기존 과거 패키지/캐시/원본·사용자 자료는 추가 정리하지 않았다.

## 경계와 다음 항목

기존 async metadata를 사용하지만 이전 runtime은 새 native async 조합을 거절할 수 있다. 코드 rollback과 프로젝트/초안 복구를 구분하고 원본을 함께 보존한다. 원래 native Invoke 자체를 async로 재작성하거나 Task.Run/동기 대기를 추가하지 않았다. 공개 override IO·권한·부모/참조/외부 원본·원래 layout을 변경하지 않았다.

다음 유한한 M4는 새 본문/노드의 첫 확정 전 전환과 직접 소유 내부/private frame의 명시 전환이다. 이미 전환·확정한 일반 Root를 중복 구현하지 않고, 내부로 옮긴 원래 native 문맥도 별도로 대조한다. M11/M12·완료한 속성/Set을 조합별 새 잔여로 열지 않는다. 기존 V1 검증 잔여/V2–V9·별도 팩/backend·종류 호환성 결정 및 실제 기기/전체 UI/Space 전달은 별도다. main은 사용자가 검토·merge하며 이 단위는 work/current만 게시한다.
