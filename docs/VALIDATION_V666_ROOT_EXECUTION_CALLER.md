# M12 호출자의 별도 공개 계약 보존

원본 v666 `dist/blueprint.js:135`의 call 포트는 참조한 함수의 공개 분기를 사용하며 `:248`의 분기 dispatch 후 연속 실행과 함수 반환을 구별한다. 호출자 자신에게 공개 분기와 반환값이 있는 경우에도 피호출자 계약 갱신은 호출자 계약을 재정의하지 않는다. 이번 단위는 직접 소유한 기존 switch-profile Root끼리의 이 실제 사용자 흐름이다. 새로운 타입/소유 조합이나 독립 계약 복제를 추가하지 않는다.

후보 준비에서 호출자의 공개 metadata를 이유로 전체 거래를 거절하던 제한을 해제한다. `executionExitMode` 허용은 그 호출자의 실제 공개 Root에 한정한다. private forwarded frame·자기 재귀·비소유/override 입력·출력 변경은 이 단위에서 확장하지 않는다. 호출자 함수 선언·분기 ID/값·자체 반환 선택과 native 데이터, 기존 C#·IO·핀/연결 및 권한을 보존한다. 영향받는 실제 호출은 계속 전부 명시 대응하며 하나의 체크포인트/CAS/Review→Confirm으로 저장한다.

UI는 공개 call의 분기 선을 기존 branch-exit 반환 카드에도 연결한다. 다른 Root의 활성 거래가 해당 호출을 포함할 때에는 서버의 기존 ordered Review 그룹·관측한 Root 종류·정확한 calledFeature가 일치하는 경우에만 그 그룹의 경로 편집을 사용한다. 호출자 자신의 별도 계약 거래를 암묵적으로 시작하지 않는다. 이 정보는 UI 분류에만 쓰며 저장 권한이나 CAS를 대체하지 않는다. 레이아웃·스타일·팝오버를 새로 설계하지 않았고, 수정된 JS의 정확한 canonical 크기/SHA만 WebBundle의 기존 엄격한 리소스 목록에 갱신한다.

집중 fixture는 먼저 기존 API로 호출자에게 `caller_done=17` 공개 분기와 int 반환을 정의한 저장 상태를 구성한다. 별도 Driver가 그 호출자의 기존 실행 결과 인터페이스를 실제 사용한다. 피호출자의 성공/실패/None과 연속 실행을 바꾸어도 호출자의 `17`과 데이터 `10`, readonly 함수 헤더·자체 종료점·C#가 그대로인지 실행한다. 다른 함수의 분기 ID 혼용·metadata 누락·불완전 반환, Save 전/Review 후 호출자 헤더와 본문 경합·cold 복원·응답 유실/늦은 입력·취소/Undo/실패를 검증한다.

검사·최신/롤백·증거는 기존 승인된 수명관리로 보존한다. 과거 자료 삭제·main 게시·새 접근권한이나 계정/유료 호출은 없다. 기존 M11은 회귀 없이 유지하며, copy/자식 전체 갱신·등록 import·private forwarding/postCall의 실제 남은 범위는 [유한한 M12 표](M12_CLOSURE.md)를 따른다. M4의 명시 async 호출자 전환 정책은 유지하며 실제 async 구현은 이 단위와 별개다. Windows 내용 교차 패키지/전체 복원은 실기기·전체 UI·Space 전달 검증을 뜻하지 않는다.

## 최종 동결 검증 결과 — 2026-11-03

제품·검사 동결 source는 `d0b954a3146cbec25c3c0e4697ba11e30cd8563e`다. 독립 LF 19단계·CRLF 16단계·새 Windows 내용 교차 패키지/전체 복원/실패 수명관리 6단계, 총 **41단계(신규 37·동등 근거 재사용 4)**가 통과했다. 변경된 후보/API 13개·UI normal/cancel/storage/conflict/loss/late와 LF native UI·private caller API, CRLF ordinary 비void API, 최종 readonly CAS를 새로 검사했다. 모든 checkout·빌드·패키지/복원 검사는 새로 실행했다.

Core runtime 17개·소유 경계 2개씩 두 checkout의 합계 38개 검사에 해당하는 4단계만 이전 native 최종 실행의 근거를 재사용했다. `e64dea66427b25d4413b5a52bb393a3977fc47f6`와 동결 코드의 `src`, `tests/Confectory.Tests`, `targets/dotnet` Git 객체 및 SDK/NuGet/configuration/RID 입력이 같다. 해당 직접 Core 검사는 수정된 element-authoring·UI를 호출하지 않는다. 이 동등성은 생성 바이너리의 informational-version 바이트까지 같다는 주장이 아니다. 원래 harness는 계속 Core 검사도 새로 실행하며, 이 실행의 별도 controller·입력 비교·원본 로그 SHA·참조 증거를 보존했다.

- 최종 실행 기록: `/workspace/artifacts/v536-verification-managed/runs/720ba9f7c8114e18b6ce9e01bf896565.json`
- 최종 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/720ba9f7c8114e18b6ce9e01bf896565.zip`, SHA-256 `23395023518de354b8898316dca4a53085149016a66f8883bb46935c3d652410`
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/e15f9a031d4346379d235bcb5691ff72.zip`, SHA-256 `88b1d43b993de7e09fc4099ad18075a84cd3f7aebbe8228c72c904e088d81945`. 최종 API 13개·늦은 입력 UI 9개 성공과 진단 실패 6개를 함께 보존했다. 두 실패는 fixture의 C# 생성 심볼 digest·예상 stdout 기본값 문제였다. 두 실패는 JS를 바꾼 뒤 기존 엄격한 WebBundle identity가 startup을 거절한 정상 보호였으며 최종 의도된 리소스 identity를 갱신했다. 나머지는 public case를 기존 반환 카드에 연결하지 못하던 guard와 다른 Root 거래의 caller 경로를 별도 계약 변경으로 분류하던 실제 UI 누락이었다. 두 실제 누락을 좁게 고친 뒤 API·UI·패키지를 최종 코드로 다시 확인했다.
- 최신 패키지 source `d0b954a3146cbec25c3c0e4697ba11e30cd8563e`, archive/SHA `4f8829bd87966c167ec941103768617571e5f9da7e2750bb088bb3032e39cfd4`, 2370파일·147디렉터리, 51,346,687 bytes, manifest SHA `a51d39234bb5948e10e45d30e3d2f3834b7b43c2823e8822296584ac7361f5fd`.
- 정상 롤백 source `e64dea66427b25d4413b5a52bb393a3977fc47f6`, archive/SHA `e27850905958a9397cf020c4de87deb9ccb275a318fe51c95979e6fabd834cd0`, manifest SHA `099051460d68279b4dba20a444deb301b707b8000e380d91309dfd89f85cd94b`.

새 생성본과 전체 압축 복원본에서 호출자 자신의 공개 분기·기존 반환을 보존하는 UI를 실행했다. 전체 파일·디렉터리 모드·크기·SHA와 복원 무결성을 검증한 뒤 승인된 두 세대 보관소에 승격했다. Windows용 내용은 Linux dotnet/Chromium에서 검사했으며 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달 검증을 뜻하지 않는다. 독립 편집 창·프로젝트 왕복은 이번 집중 단위에서 새로 실행하지 않았으며 이전의 다른 흐름 증거로 완료를 대신 주장하지 않는다.

집중 및 최종 실행이 직접 만든 임시 작업공간은 자식 프로세스 종료·지속 증거 검증 후 모두 정리했다. 다른 기존 자료는 삭제하지 않았다. 최종 실행 전 여유 1868.40MiB, 정리/승격 후 1863.59MiB, 신규 단계 표본 최소 1868.32MiB였다. 지속 공간 144MiB(안전 64MiB 포함), RAM 작업공간 3GiB+512MiB, 추가 메모리 7GiB+1GiB 예산은 낮추지 않았다. 이 단계 표본 최소값은 보관/승격 중 모든 순간의 사용량을 뜻하지 않으며 해당 구간은 별도 추가 공간 예산으로 확인했다. 신규 단계 cgroup 메모리 표본 최고는 4225.97MiB였다. 집중 실행 기록 순증가 1.75MiB, 최종 실행 기록 순증가 4.81MiB이며 별도 코드/Git·보고 기록은 구분한다.

이후 보고 문서 전용 커밋은 동결 제품·검사 트리를 유지한다. main을 게시하지 않으며 work/current의 최종 원격 SHA·clean은 게시 뒤 별도로 확인한다.
