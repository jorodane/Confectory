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

집중 관리 실행: `/workspace/artifacts/v536-verification-managed/runs/dd6a678461034b0baca125b1dedcfdc3.json`. 합성 입력만 사용하며 원문과 실제 CLR 호출 결과를 따로 확인한다. Root 직접 전달·private 별도 출력·out-only·예외·배열의 5개 API 변형과 6개 UI 모드(normal/storage/loss/private late/conflict/project)가 통과했다. 강화한 out 미할당 검사도 실제 `CS0177` 및 입력 보존을 확인했다. 최종 코드의 신규/재사용/미실행 검사와 패키지·공간 결과는 최종 검증 뒤 기록한다.

실제 Windows apphost/WebView2·실제 모바일 기기·전체 UI·Library/Space 전달 완료를 뜻하지 않는다. B2 권한 backend, 종류 C# 표현/사용 중 삭제 대응, M4/M12 및 3D·권한 별도 팩은 기존 고정 잔여다. 3D 이동은 표시 연출이고 작업 실행 조건이 아니다.
