# M12: 소유 본문·copy의 기존 데이터와 분기 반환

## 원래 요구와 이번 연결

저장소 v666 `dist/app.js:2469–2476`은 입출력/실행 분기 정의를 구현보다 우선한다. `dist/blueprint.js:969–976`은 readonly 정의의 기존 분기 반환 배치를 제공하며, `:248`은 데이터 발행→결과 분기→후속 실행 순서를 정한다. 이미 지원된 ordinary switch-profile 본문 반환에 기존 비void 값·typed out/ref를 함께 보존한다.

직접 소유 정보의 저장/새 same-contract copy, 자식이 직접 선언한 Blueprint target, 등록 외부 함수의 로컬 ordinary provider와 저장/새 copy를 연결한다. 공개 함수/override IO·기존 분기 ID/None·provider 선택·donor/부모/외부 원본은 그대로다. 독립 새 계약 복제·원문 재작성·새 외부 권한을 추가하지 않는다. 부모에게서 빌린 본문은 읽기 전용이며 자신의 본문만 편집한다.

`{executionBranch, value}`를 공통 검증에 연결한다. 비void의 기존 직접 종료점 데이터 연결과 export-return/default는 유지하고 실행 선택·선만 바꾼다. 데이터 누락·치환과 잘못된 ID는 전체 후보를 거절한다. 새 copy의 sealed preview/첫 Save, 저장 copy의 복원 guard, 자식/등록 본문의 원자 그룹·원시 읽기 lease·최종 CAS에서 같은 규칙을 적용한다. void/private의 기존 한 필드 종료점 형식은 유지한다. C# 생성/Invoke 계약이나 원본 팝오버·CSS·HTML·제품 JS는 변경하지 않는다.

## 검사와 지원 경계

최종 동결 source와 검사·보관 결과는 아래에 기록한다. 동일한 int 반환·ref int·out long/string 프로젝트를 기존 소유 흐름에서 실행한다. 타입/역할/문맥의 모든 곱을 새 필수 검사 목록으로 만들지 않는다. 반환 계획과 무관한 데이터/본문 편집은 기존 별도 계약을 따른다.

`__fg_` 호출 노드 매개변수는 기존 NODE_RESERVED_NAME 규칙의 정상 거절이다. 유효한 일반 함수의 IInvoke 매개변수와 그래프 노드의 내부 예약 경계를 구분한다. 진단 입력이 이 보호에 걸린 근거와 정상 거절 검사를 보존하며 새로운 migration/이름 재작성 요구로 추가하지 않는다. 큰 데이터 그래프의 UI fixture는 기존 전체 맞춤 조작을 사용하고 강제 클릭이나 제품 레이아웃 변경을 하지 않는다.

이전 authoring의 해당 비void 반환 계획 편집/복원을 보장하지 않는다. 최신/정상 롤백, 기존 원문/checkpoint 및 재현 입력을 보존하고 자동 승격·삭제를 하지 않는다. 실제 Windows/WebView2·모바일 실행·전체 UI·Space/Library 전달은 교차 패키지/hosted UI 검사와 구분한다.

## 유한한 다음 흐름

M12의 ordinary 데이터 반환 연결은 기존 소유/등록 경계에 적용했다. 남은 계약 갱신은 두 사용자 흐름이다.

1. 중첩/private·기존 native 호출 문맥 또는 등록 외부 import를 사용하는 실제 caller/provider를 공개 계약 후보에 명시적으로 결합하기. 원래 코드/프레임 의미와 readonly 외부 관측을 보존하며 자동 의미 변환을 하지 않는다.
2. 여러 직접 소유 ordinary provider의 모든 target 반환과 실제 caller를 하나의 공개 계약·원자 후보에 결합하기. 자동 provider/target 선택이나 override 계약 변경은 하지 않는다.

구형 profile 자동 변환·부모/참조 원본 쓰기·독립 계약 복제는 필수 잔여가 아니다. M11은 구체적 회귀가 없으면 닫힌 상태다. M4는 확정된 규칙(동기 caller는 명시 async 전환 전 호환되지 않는 호출을 오류로 거절, 자동 blocking/전환 금지)에 따라 실제 async 저장·호출·await→출력→완료→분기→후속 실행을 연결하는 다음 고정 항목이다.


## 최종 동결 검증과 보관

제품/테스트/harness source는 `8d72a78b9947e88f1d8233d8d214adfc7a47c848`이며 이후 변경은 결과 문서뿐이다. 독립 no-hardlinks checkout·별도 home/NuGet·빈 엔진 캐시에서 **신규 LF20·CRLF19·패키지/전체 복원/실패 수명관리6, 총45단계**가 모두 통과했다. 최종 단계의 재사용은 없다. 각 checkout의 반환 계약/runtime16·소유 경계2씩 **총36개**는 위 단계에 포함된다.

| 기존 사용자 흐름 | 신규 LF API | 신규 CRLF 화면 |
|---|---|---|
| 저장된 소유 same-contract copy | 저장/실행/반복/복원/읽기 CAS/변조 거절 | 취소·Undo/Redo·저장·실행 |
| 새 소유 copy | 미리보기/첫 Save·미확정 반복·등록/배정/원문 보존 | 쓰기 실패·재시작·첫 저장/실행 |
| 직접 선언한 자식 본문 | 등록 외부 부모의 원시 receipt·부모 변경·실제 실행 | 로컬 부모 경합·입력 보존 |
| 등록 외부 함수의 로컬 provider | readonly 두 헤더·등록/경로/권한/누락/변조 거절·실행 | 응답 유실·cold receipt 재조회 |
| 등록 외부 함수의 저장 copy | provenance·readonly 계약·저장/반복/실행 | 늦은 입력·재시작·명시적 재저장 |
| 등록 외부 함수의 새 copy | origin·첫 관측·생성/등록/배정·실행 | 같은 ID의 다른 프로젝트 왕복·첫 Save |

실제 fixture는 int 반환·ref int·out long/string과 원래 직접 종료점 값/export-return을 사용한다. 코드·IO·branch ID·데이터 연결·donor/부모/외부 원본과 mode를 보존한다. 데이터 누락/치환은 후보와 저장 copy/자식/등록 본문의 복원 guard에서 거절한다. 기존 void 저장 copy API·void 자식 화면과 직접 Root의 비void API도 새 회귀다. 각 소유 문맥의 모든 수명 조합을 새 필수 행렬로 만들지는 않는다.

M11 구현/생성의 이전 근거는 source-equivalence.json(17개 동일 파일과 기존 Branches 메서드 동일성) 및 이전 게시 a58b0274/검증 record264c3445의 근거를 별도로 재사용했다. 이를 이번 신규45/36개로 세지 않는다. 제품 JS/CSS/HTML/리소스 manifest와 C# 생성기는 이전 게시본과 같다. 집중에서는 내부 예약 이름을 일반 호출로 기대한 진단의 실패가 기존 NODE_RESERVED_NAME 보호임을 확인했고, 25% 화면 밖 카드의 실제 클릭 실패를 기존 전체 맞춤 조작으로 바로잡았다. 실패/수정 후 통과 로그를 보존하며 강제 클릭·제품 레이아웃 변경·생성기 변경·검증 완화는 없다.

새 Windows 교차 패키지의 외부 새 copy normal과 전체 SHA/CRC·파일/디렉터리 mode 복원 후 외부 저장 copy late를 실행했고 실패/예외 수명관리도 새 검증했다. 실제 Windows apphost/WebView2·모바일 실행·전체 UI·Space/Library 전달은 미검증이다. 이 데이터 흐름의 별도 독립 창은 새 실행하지 않았다.

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `8d72a78b9947e88f1d8233d8d214adfc7a47c848` | `b57d1248f148ac161ca1b66b8890211391682e1cd3422176dff934ea83c77300` | `e891fcd10eb480256cc68ee49a0784100dedd2f5b557710c5828c59e089a798b` | 51345523 / 2370 / 147 |
| 정상 롤백 | `e38ba0620d2e62e6f83f250ad55bb6d15e01acf5` | `c2d877c95f0e36644b816c861cc54df0c3a560170119a6e90de69c958b1a4162` | `08be998131ed4cfa574828e3d75541bbaf978bcd06bad04af1843be4c845cb10` | 51342620 / 2370 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 실행/복원은 신규이며 롤백 실행은 이전 정상 근거를 재사용하고 archive SHA를 재확인했다. 최종 `/workspace/artifacts/v536-verification-managed/runs/ede4c4c643bb4d61ab2cfb08ecc7c7b5.zip`(SHA256 `600b649a9baa215ed7ca88dcfb9b455edce5751a76977823eae9f202870b1b63`), 집중 `/workspace/artifacts/v536-verification-managed/runs/cc4348c77b2d45bbafdc337609021256.zip`(SHA256 `84cd970a6bf5848fdf447e7b8f32b38f54595f19bd6a9df5373bc4ab8c077d44`)와 입력·로그·프로필·스크린샷·전체 manifest를 지속 보관했다. 자식 종료·보관 무결성·소유권 확인 뒤 이번 두 RAM 공간만 정리했다. 승인된 관리 최신/롤백 승격 외 기존 자료 삭제는 없다.

집중 여유 1897.31→1896.19MiB(사용 순증가 1.12MiB), 최종 1895.88→1891.00MiB(사용 순증가 4.88MiB)다. 수집 시 여유 1891.00MiB, stage 표본 최소 여유 1895.79MiB, 관측 cgroup memory peak 4172.12MiB다. 기존 persistent144MiB(안전64MiB 포함)·RAM3GiB+512MiB·memory7GiB+1GiB 예산을 낮추지 않았고 다음 증가량을 보장하지 않는다.
