# M12: 여러 직접 소유 provider의 공개 분기 계약

## 원래 사용자 흐름과 이번 범위

저장소 v666 `dist/app.js:2469–2476`의 입출력/실행 분기 우선 정의와 `dist/blueprint.js:969–976`의 공개 분기·반환 편집을 따른다. 기존 함수의 공개 분기를 바꿀 때 같은 계약을 구현하는 직접 소유 ordinary Blueprint provider가 여럿이면, 특정 provider의 target만 바꾸어 나머지를 낡은 계약으로 남기지 않는다.

이미 저장된 동일 함수의 직접 소유 provider와 그 Blueprint target 전부, 실제 직접 Blueprint 호출 위치 전부를 기존 명시 대응 후보에 결합한다. provider별 target 표시에는 기존 구현 ID를 붙여 같은 `common`/`linux`를 구별한다. 모든 추가 target의 반환 ID/None과 모든 호출 위치는 사용자가 명시해야 하며 자동 선택하지 않는다. 실제 실행 provider는 기존 scoped provide/배정 계약으로 선택되고 이 편집이 배정을 변경하지 않는다. 기존 UI/팝오버/레이아웃/제품 JS·CSS·HTML을 바꾸지 않는다.

다른 provider의 imports도 readonly 관측으로 수집해 같은 Review/Confirm·receipt·최종 CAS에 포함한다. 원래 C# record, 함수 IO·branch ID/값, 다른 함수 헤더, 호출자의 다음 줄과 명시 연결을 보존한다. 전체 그룹 복원에서 provider 멤버 누락을 거절하며 부분 Review·누락/중복 대응·저장 전 원문 변경·Review 뒤 다른 provider 원문/import 변경은 전체 미적용이다. 이전 단일 provider/호출자 없는 흐름도 유지한다.

모든 provider가 같은 기존 ordinary switch-profile의 직접 소유 Blueprint일 때만 공개 계약 갱신을 허용한다. opaque C#·whole-body/중첩 native·same-contract copy provenance·override·부모/외부 원본의 의미를 추정해 바꾸지 않는다. canonical 물리 그래프를 공유하는 target은 모호한 소유 초안으로 거절한다. 이는 현재 지원 경계이며 자동 변환/독립 계약 복제를 필수 후속으로 추가하지 않는다. override 원계약과 권한을 완화하지 않는다.

## 검증 상태와 유한한 잔여

집중 검사와 최종 source-bound 결과는 완료 후 아래에 기록한다. 새 데이터 타입 행렬을 만들지 않고 원래 scoped provider를 다르게 배정한 두 호출자·두 provider의 실제 실행, 명시 대응과 동일 원자 그룹을 확인한다. 이전 ordinary 비void와 copy 데이터 보존은 관련 회귀로 유지한다.

M12의 남은 기존 흐름은 중첩/private·기존 native caller/provider와 등록 외부 import 관측을 공개 계약 갱신 후보에 명시 결합하는 일이다. 이미 올바른 비소유 원본 쓰기/override 계약 변경 거절, 구형 profile 자동 migration은 미구현으로 세지 않는다. M11은 구체적인 회귀가 없으면 닫혀 있다. 이어지는 M4는 확정된 동기 caller 오류 정책과 await→출력 발행→완료→결과 분기→다음 실행 순서를 따른다. 실제 Windows/WebView2·모바일/전체 UI·Space 전달은 별도 미검증이다.


## 최종 코드 검증과 보관

동결 제품/테스트/harness source는 `4e087d55098c4882f1cb670a173f048af89d7711`다. 이후 결과 문서 두 개만 갱신한다. 별도 no-hardlinks Git checkout·home/NuGet·빈 엔진 캐시의 **신규 LF20·CRLF18·패키지/전체 복원/실패 수명관리6, 총44단계**가 모두 통과했다. 최종 stage의 재사용은 없다. 각 EOL의 Root 반환 계약/runtime16·소유 경계2씩 **총36개**는 위 stage에 포함된다.

LF·CRLF 각각 두 provider/네 target/다섯 호출 위치의 API를 새 실행했다. 모든 대응의 명시 선택, opaque/override/물리 alias 거절, 복원 그룹 멤버 누락, 다른 provider의 C# 원문·readonly import의 최종 CAS, 부분 Review·원자 저장·cold/receipt·서로 다른 scoped provider 실행을 확인했다. 다른 provider의 linux Root에서 다시 이름/순서를 바꾸고 모든 ID/값·원문·배정을 보존해 재시작·실행했다.

화면 신규 LF normal/cancel/storage/conflict와 CRLF loss/late는 호출자/target 누락 입력 보존, 실제 수동 선택·Undo/Redo·쓰기 실패·경합·응답 유실/cold receipt 조회·늦은 입력의 별도 명시 저장, Review 취소/Confirm, 분기 포트 연결과 실행을 확인했다. 두 EOL에서 호출자 없는 단일 provider API·ordinary 비void Root API·비void saved-copy API/LF 및 cancel 화면/CRLF·최종 read-CAS도 새 회귀했다. 집중 API/응답 유실 화면의 선행 근거는 `/workspace/artifacts/v536-verification-managed/runs/df43fb0eb9c44f96b5bf668336695e59.zip`(SHA256 `de159990e101fd4d41ece0c492b0c8e947666058729bb3d0b1de3ee6145dd82c`)다. 최종44와 중복 합산하지 않는다.

제품 JS/CSS/HTML/리소스 manifest·C# 생성기·M11 소스는 직전 게시 fa4664c와 같다. M11의 더 넓은 기존 문맥은 이전 근거와 구분하며 이번 신규44단계나 실기기 검증으로 표시하지 않는다. 이번 provider 데이터 실행 fixture는 기존 value+int out 계약이며 CLR 타입별 모든 조합을 새 필수 행렬로 만들지 않는다. native/whole-body·copy provenance·override를 포함한 공개 계약 갱신은 이 단위의 지원 밖이며 의미를 추정한 자동 변환을 하지 않는다. 공개 계약 갱신에 기존 copy provenance가 포함되는 경계도 다음 실제 caller/provider closure 대조에 묶으며, 타입/소유 조합별 필수 행렬이나 독립 새 계약 복제로 확대하지 않는다. 원문 비소유 편집과 override 원계약 변경은 정상 거절이다.

새 Windows 교차 패키지에서 여러 provider의 normal 화면과 전체 SHA/CRC·파일/디렉터리 mode 복원 뒤 late 화면을 실행했다. 실패/예외 package 수명관리도 신규다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space/Library 전달 및 이 흐름의 별도 독립 창은 새 실행하지 않았다.

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `4e087d55098c4882f1cb670a173f048af89d7711` | `26dadada9e9d0d374e8fec48a903017e84367b90978eb6b595c4bae8bf1d18f1` | `7b489a2e4a225611f623fdf6686fd2cdb02ace90e0f228b3866c79aebb815bb2` | 51346011 / 2370 / 147 |
| 정상 롤백 | `8d72a78b9947e88f1d8233d8d214adfc7a47c848` | `b57d1248f148ac161ca1b66b8890211391682e1cd3422176dff934ea83c77300` | `e891fcd10eb480256cc68ee49a0784100dedd2f5b557710c5828c59e089a798b` | 51345523 / 2370 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 패키지/복원은 신규이며 롤백의 실행은 이전 정상 근거를 재사용하고 archive SHA를 확인했다. 최종 `/workspace/artifacts/v536-verification-managed/runs/7a73c731cbff47fdb8f697591958a047.zip`(SHA256 `03bca833c08980a17c2929eb7a30323fb335960c520f3df98b82ea64a2976c63`)와 집중 로그·프로필·스크린샷·원본 입력·전체 manifest를 지속 보관했다. 자식 종료·소유권·보관 무결성을 확인한 뒤 이번 두 RAM root만 정리했다. 승인된 관리 latest/rollback 승격 외 기존 자료 삭제는 없다.

집중 여유 1889.79→1889.30MiB(사용 순증가 0.49MiB), 최종 1889.16→1885.22MiB(사용 순증가 3.95MiB)다. 수집 시 여유 1885.22MiB, stage 표본 최소 여유 1889.09MiB, 관측 cgroup memory peak 4155.36MiB다. persistent144MiB(안전64MiB 포함)·RAM3GiB+512MiB·memory7GiB+1GiB 예산을 낮추지 않았으며 향후 증가량을 보장하지 않는다.
