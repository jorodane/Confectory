# 공개 분기 본문의 소유 import 호출

## 원래 흐름과 지원 범위

v666 `dist/blueprint.js:248`의 원래 동작 실행·출력 발행·결과 분기·후속 동작 순서에 대응한다. 공개 분기를 정의하는 직접 소유 동기 void Blueprint 본문에서도 다른 직접 소유 함수의 기존 호출과 반환값 소비를 보존한다. 원래 import/provider 선택·함수 IO·C#·노드 ID/연결·레이아웃을 바꾸지 않는다.

앞선 복합 호출의 readonly 계약 관측을 본문 import에 적용한다. 본문과 호출자가 같은 계약을 사용하면 qualified ID로 한 번만 관측한다. 추가 계약은 원자 그룹·최초 관측 영수증·복원·Review·최종 CAS에 포함되며 이 거래로 편집하지 않는다. 독립적으로 수정 중인 계약, 누락/변조 관측, 원문 경합은 전체 입력을 보존하며 거절한다. 외부 등록/권한을 새로 만들거나 provider를 자동 선택하지 않는다.

## 최종 검증

제품 source는 `f43c9caaf3ca823c4d435c3b09dc7c117b4728fd`이며 이후 수정은 결과 문서뿐이다. 독립 no-hardlinks LF/CRLF checkout·별도 home/NuGet·빈 엔진 캐시에서 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계**를 통과했다. 최종 실행의 검사 재사용은 없다. Core/runtime39·소유 경계2씩 총82개도 양쪽에서 새 실행했으며 위 단계에 포함된다.

- 의존성을 본문에만 둔 실제 프로젝트에서 원래 호출·int 반환값 소비·ref int/out long/out string·분기와 후속 실행을 확인했다. 원문 C#/import·ID/연결·0400 readonly 헤더/provider/C# 파일 모드를 유지한다. 추가 헤더의 누락·draft 변경·누락/변조 영수증·Save 전/Review 이후 원문 경합은 전체 미반영과 입력/체크포인트 보존을 확인했다.
- 정상·취소/Undo/Redo·쓰기 실패·충돌·응답 유실·저장 중 늦은 입력·cold 재시작과 Review 취소/Confirm을 API/실제 화면에서 검증했다. 이 본문 import Root의 별도 독립 창은 새 검증하지 않았다. 기존 caller import API/화면, 등록 외부 새/저장 copy, M11과 실제 최종 읽기 CAS도 새 회귀로 실행했다.
- 집중 8단계는 실패 없이 통과했다. 집중 source overlay의 코드·테스트·harness를 최종 동결 blob과 대조했다. 최종 검사는 전부 새 실행했으며 집중 결과를 최종 통과 단계로 재사용하지 않았다. 레이아웃/권한/override 계약이나 원문을 재작성하지 않았다.
- 새 Windows 교차 패키지·생성본 normal, 전체 SHA/CRC·파일/디렉터리 모드 복원·복원본 late와 실패/예외 수명관리를 새 검증했다. 실제 Windows apphost/WebView2·모바일 실행·전체 UI/Space/Library 검증은 아니다.

## 지속 보관과 공간

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `f43c9caaf3ca823c4d435c3b09dc7c117b4728fd` | `7a3258ec60b3e3882cfc24d849e88660d4e0ef33271da1b077803b60ba086ef1` | `a2ab88e4421d9828dab3f3af960f302c269fe027e3f5780a0f2536b3796adcf4` | 51337618 / 2370 / 147 |
| 정상 롤백 | `af2786571ecb04b1665566174806b1fc7118bf14` | `8d6197de7c33661b8c8f926eea905abd499b6631567cc867b273a1b2bd7bae62` | `cb8ca0cf42837d3f6f0284835680b0498889292b0b52d6479e753717b1f8ab4c` | 51337355 / 2370 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 실행/복원은 신규 검증이며 롤백 실행은 이전 정상 근거를 재사용하고 압축 SHA를 재확인했다. 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/5e4f55105eb347609b6a0ed02f18131e.zip`(SHA256 `8f13e8959a2624cc6bfd4df4db1696b65e618ddbfcddcae407d03b2dcd34e8d4`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/1c2a2f9a430448dabfb40b0233e14c1f.zip`(SHA256 `ff706227b41d8d8704a6e432b4146ecab997433b777bcfea20eb6174d7a9d50f`)와 입력·로그·프로필·스크린샷·manifest를 지속 보존했다. child 종료·보관 무결성·소유권 확인 뒤 이번 두 RAM 공간만 정리했다. 승인된 관리 최신/롤백 승격 외에 과거 자료·SDK·원본·캐시·사용자 데이터 삭제는 없다.

집중 디스크 1908.32→1907.76MiB(순증가 0.56MiB), 최종 1907.55→1903.10MiB(순증가 4.46MiB), 수집 시 여유 1903.10MiB다. stage 표본 최소 여유 1907.50MiB, 관측 cgroup memory peak 4135.27MiB다. 기존 persistent144MiB(안전64MiB 포함), RAM3GiB+512MiB, memory7GiB+1GiB 기준을 낮추지 않았다. 다음 실행의 증가량을 보장하지 않는다.

## 실제 잔여와 호환성

ordinary 비void의 값+공개 분기 전달, 중첩/private·등록 외부 import receipt·여러 provider의 공개 계약 변경을 포함한 완전한 복합 closure는 같은 고정 M12 잔여다. 공개 override 계약 변경과 부모/참조 원본 쓰기는 정상 보호이며 구형 profile 자동 승격이나 독립 새 계약 복제를 추가하지 않는다.

M4의 기존 동기 호출자 처리 정책은 사용자 답변 대기로 유지한다. 이 단위에는 새 정책 결정이 필요하지 않다. 이전 authoring의 미확정 본문 import 그룹 편집/복원은 보장하지 않으며 최신/롤백과 원본 checkpoint를 보존한다. 실제 Windows/WebView2·모바일 실행·전체 UI·Space/Library 전달은 교차 패키지/hosted UI 검증과 별개다.
