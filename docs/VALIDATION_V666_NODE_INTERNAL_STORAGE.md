# M11 일반 C# ref/out 내부 흐름과 whole-body 경계

원본은 저장소 v666 ZIP의 기존 개별 동작 `openInternal` 진입과 C# 고정 선언 편집이다. 새 배정 방식·핀·레이아웃이나 C# 역변환은 추가하지 않는다. [지원 경계](BLUEPRINT_NODE_INTERNAL_FLOW.md)의 직접 소유 일반 next Root/private 동작을 따른다.

## 지원 의미

- private graph를 이미 지원하는 원래 frame profile에서 일반 ref/out 동작을 단일 코드로 감싼다. 기존 바깥 ID·signature의 이름/타입/역할/순서·인자 binding·실행선·본문/helper·활성 물리 소스를 보존한다.
- 바깥의 호출자 직접 out 전달 여부는 그대로다. 원래 별도 node out을 사용하던 graph를 호출자 직접 out으로 바꾸지 않는다. 새 private 함수의 입력/출력 이름은 선택한 동작 signature와 같고 ref는 동일 변수, out은 기존 native 직접 저장소 전달로 연결한다. 반환 내보내기도 기존 원문 호출의 결과를 사용한다.
- 새 초기값이나 값 변환을 추측하지 않는다. native의 `SkipInit`는 definite assignment 표시이며 저장소에 값을 쓰지 않는다. 정상 종료에서 미할당 graph out 처리, 실제 C# out 할당 검사와 예외 전 alias 쓰기 규칙은 기존 엔진을 그대로 따른다.
- 미리보기·창별 입력·Undo/취소·author 후보와 최종 checkpoint/file CAS·원문 guard·cold·Review→Confirm은 앞선 지원과 동일한 거래다. 공유/부모/외부 원본을 변경하지 않는다.

확인한 합성 호출의 구체적 결과는 다음과 같다. 같은 변수를 여러 ref/out에 넘긴 경우를 별도 저장소 호출과 함께 전환 전후 비교한다.

| 기존 저장소 의미 | 같은 변수 호출의 전환 전/후 결과 |
|---|---|
| 호출자 ref/ref/out 직접 전달 | 반환 120, 최종 변수 40 |
| 별도 node out 뒤 명시 export | 반환 80, 최종 변수 40 |
| out/out의 같은 변수 | 반환 20, 최종 변수 20 |
| ref 배열 변수 교체 | 반환 24, 원소 12 |
| out 할당 전 예외 | 먼저 쓴 ref 값 10 유지; 별도 out 초기값 17 보존 |

이 결과의 차이를 새 래핑이 하나로 통일하지 않는다. 사용자 본문을 명시적으로 편집한 경우에만 그 반환 결과가 바뀐다.

## whole-body: 확정 의미와 실제 미구현

기존 whole-body 전환은 `implementationContext`와 `sourceIdentity`를 통해 원래 인스턴스 `Invoke`, this 재귀, this.calls/IImports, scoped import와 원문 위치를 유지한다. 일반 static/private 함수의 본문과 다르다. `FeatureBlueprint.Context.cs` 및 `BlueprintConversion.cs`의 계약이 근거이며 새 의미 결정을 요구하는 미정 상태로 분류하지 않는다.

현재 `FeatureBlueprint.Nested.cs`의 private 요청은 이 implementation 문맥을 전달하지 않는다. 이를 단순히 leaf로 옮기거나 외부 context 표시를 지우면 원래 receiver/재귀/호출 경계를 잃는다. 이번에는 유효한 whole-body 계약을 명시적으로 거절하고 원본/초안을 유지한다. 기존 whole-body 변환·본문 편집은 계속 사용할 수 있다. 다음 native 연결은 원래 메서드 경계를 명시적으로 전달하는 방식이 기준이며 this/calls 문자열 치환이나 자동 decompile은 대안으로 채택하지 않는다. 기존 계약을 보존하는 기술 구현이 남은 것이며 이번 단위에 새 사용자 정책 선택은 필요하지 않다.

`sync-acyclic-ref-v1`처럼 private graph가 없는 기존 profile도 자동 변경하지 않는다. frame profile 보존 지시를 따른 현재 경계이며 ref/out 자체의 금지나 새 영구 UX 정책은 아니다. 분기·copy/상속/참조·독립 계약 복제는 이번 단위에 추가하지 않는다.

## 검증 및 보관

집중 관리 실행: `/workspace/artifacts/v536-verification-managed/runs/dd6a678461034b0baca125b1dedcfdc3.json`. 합성 입력만 사용하며 원문과 실제 CLR 호출 결과를 따로 확인한다. Root 직접 전달·private 별도 출력·out-only·예외·배열의 5개 API 변형과 6개 UI 모드(normal/storage/loss/private late/conflict/project)가 통과했다. 강화한 out 미할당 검사도 실제 `CS0177` 및 입력 보존을 확인했다. 집중 증거 ZIP은 `/workspace/artifacts/v536-verification-managed/runs/dd6a678461034b0baca125b1dedcfdc3.zip`, SHA-256은 `4d05e0a2cc9438c9ffccb041e0f099b2b10d4ab9eafe0ff5fc537ce79d172904`다.

## 최종 독립 검사: 신규/재사용 구분

- 실행 코드·검사 commit: `f7084302b15ecbf7de8e39f6d9554fdfd2e83d7d`. 최종 보고 커밋은 문서만 바꾸며 실행 코드 동등성을 확인한다.
- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/0d5106bd52034ba58943f53e5803411a.json`. **43단계 전부 통과**: LF 18, CRLF 17, 새 교차 패키지/전체 ZIP 복원/실패 수명관리 8. 두 checkout의 Git 객체·엔진 캐시·의존 저장소는 독립이다.
- Root 일반/void API와 원본 화면, 새 저장소 API 5변형, ref/out UI normal/storage/loss/private late 및 기존 중첩 값 API를 최종 코드로 새로 실행했다. 모든 변형에서 실제 `CS0177` 및 입력 보존을 확인했다. native `ExternalRefTests` 8개와 private helper·whole-body this/재귀/scoped import 회귀 3개, **총 11개를 양쪽에서 각각 통과했고 skip은 0**이다.
- 생성본은 Root/일반 ref/out 화면을, 전체 manifest SHA/모드로 복원한 패키지는 Root 쓰기 실패와 private 별도 출력의 응답 유실을 새로 검사했다. 이전 패키지 결과로 대체하지 않았다. 실제 Windows apphost를 실행한 검사는 아니다.
- 집중 검사의 conflict/project 및 전체 UI 모드는 최종 production 파일 해시 일치로 재사용한다. 이전 중첩 단위의 48단계와 앞선 107단계의 무변경 기능 근거는 역사적 재사용이며, 이번 최종 코드에서 그 전체 suite를 다시 실행했다고 집계하지 않는다. 기존 suite나 거절 assertion을 없애지 않았다. 미관측 ref/out/forwarded receipt 거절은 유지하고 유효한 계약의 긍정 검사를 추가했다.
- 최종 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/0d5106bd52034ba58943f53e5803411a.zip`, SHA-256 `116633222cc7f01b2c83d69830f92a8d19423ab94387a39d27df0cbbd2df802e`. 로그·스크린샷·합성 입력·재생성 출력 manifest를 지속 보관한다.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | 크기 | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `f7084302b15ecbf7de8e39f6d9554fdfd2e83d7d` | `aa300d0063df890fceb073bbc7f6020ddca396c35e5d8796f6ae9f323cd5438c` | 51,243,266 bytes | `0e61fde0ecb5f1179c68f4c37d0c51e534d79dedb6a60948b8f6d3b3cb2d5b80` |
| 정상 롤백 | `6174389ca1a8cc300f40cae80a23d439a029fe85` | `e3ed67225865cf735b0f4cb0477feb6ad02b9615e16cde40d7c1f9357dedb137` | 51,243,792 bytes | `96c012aac675bb97f33933eb979b8970ddab034b9a0c0e3842e553bf832bdc9a` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 두 ZIP SHA를 재확인했고 각 manifest는 2510개 항목(2363 파일/147 디렉터리)을 기록한다. 최신은 새로 전체 복원/실행했고 롤백은 직전 검증 정상본을 보존했다. 미반영 ref/out 전환 초안을 구버전 UI로 편집/확정하는 호환성은 별도 보장하지 않으며 현재 검증본을 사용한다.

최종 관리 실행의 디스크 여유는 시작 2097.13 MiB → 정리 후 2093.28 MiB, 순증가 **3.86 MiB**다. 실행 중 단계 샘플 최소 여유는 2097.09 MiB, cgroup 메모리 피크는 4575.85 MiB였다. 집중/최종 소유 RAM root는 증거 보존 뒤 제거됐다. 이 값은 해당 실행의 실측이며 이후 증가량 보장은 아니다. 과거 비관리 자료·원본·사용자 데이터를 정리하지 않았다.

## 남은 범위와 미실행

이번 완료는 private 지원 profile의 직접 소유 일반 next C# ref/out 래핑이며 M11 전체 완료는 아니다. whole-body의 원래 receiver/메서드 경계를 전달하는 native 연결, private 미지원 기존 profile, 분기·copy/상속/참조 전환은 위 경계대로 남는다. 새 독립 계약 복제나 공개 override 계약 변경은 추가하지 않는다. 정책을 추정해 확정하지 않았다.

M11 독립 슬롯 창의 새 전환, 모바일 viewport 진입과 ref/out의 모든 타입/profile/제어 조합은 이번 UI 검사 완료로 집계하지 않는다.

실제 Windows apphost/WebView2·실제 모바일 기기·전체 UI·Library/Space 전달 완료를 뜻하지 않는다. B2 권한 backend, 종류 C# 표현/사용 중 삭제 대응, M4/M12 및 3D·권한 별도 팩은 기존 고정 잔여다. 3D 이동은 표시 연출이고 작업 실행 조건이 아니다.

이 문서는 일반 ref/out 단위 게시 당시의 경계다. 이후 직접 소유 whole-body의 this·재귀·scoped import 연결은 [문맥 지원 검증](VALIDATION_V666_NODE_INTERNAL_CONTEXT.md)에서 별도로 다룬다. 기존 검사의 whole-body 거절 사례는 관측되지 않은 다른 구현 receiver로 좁혀 기존 보호를 검증한다.
