# M12 공개 분기 갱신과 기존 ordinary 소비자 관측

기준은 저장소 v666 `dist/blueprint.js:135`의 참조 정의 기반 call 포트와 `:248`의 출력→분기→다음 실행이다. 공개 분기 계약을 갱신할 때 기존 native import나 legacy wrapper가 같은 함수를 ordinary `IInvoke`로 소비하고 있어도 그 소비 의미를 바꾸지 않아야 한다. `:1504–1512`의 명시 wrapper 계약 갱신과 `:1514–1519`의 OriginalResult 연결은 기존 NoBranch adapter의 자동 재해석과 구별한다.

실제 직접 call은 계속 명시 대응한다. 같은 소유 프로젝트에서 실제 함수 의존성이 있는 native 코드·ordinary wrapper는 전체 원본 문맥을 먼저 검증하고 관측 그룹에 포함한다. 사용하지 않는 import 선언만으로 새 공개 분기 caller를 만들지 않는다. 선언된 Blueprint target이 누락됐거나 원문·서명·문맥·receipt가 이미 낡았다면 거절한다. ordinary observer의 기존 profile은 바꾸지 않고 Core의 전체 원본 검증을 적용한다. 공개 분기를 직접 dispatch하는 target/caller의 기존 profile 보호는 유지한다. 부모·참조·외부 소유자·copy의 별도 경계나 override 계약을 열지 않는다.

native 코드 정의는 imported 함수의 전체 계약 hash를 포함한다. 기존 원문이 준비된 상태인지 확인하고, 후보 전후의 정의에서 해당 callee의 hash만 달라졌음을 증명한 뒤 생성 record의 `definitionHash`만 갱신한다. C# source/helpers, source identity, implementation context, 입력/출력·node ID·graph·연결은 보존한다. 다른 정의 변화나 stale record는 자동 수리하지 않는다. scope object와 선언의 읽기 전용 raw receipt도 checkpoint/Review→Confirm/최종 CAS에 결합한다.

집중 fixture는 원래 implicit-profile로 단일 래핑한 native consumer와 기존 NoBranch wrapper를 직접 caller 옆에 둔다. native C#의 CRLF·원래 파일명/CallerMemberName·scoped import와 출력20을 검증한다. legacy wrapper는 기존 NoBranch0을 받고 자신의 분기17·출력30을 계속 실행한다. 새 공개 결과를 받는 소비자로 조용히 바꾸지 않는다. 실제 public caller만 선택한 성공 포트로 반환하고 원래 out10은 먼저 발행돼야 한다. 생성 record 이외의 원문·graph·readonly0400 선언은 바이트와 mode를 대조한다.

검증은 누락/변조 observer·native record·source receipt, 잘못된 소유 문맥·legacy public 위장, Save 전/Review 뒤 원문·scope 경합, 원자 저장·반복·부분 Review 거절·cold·완료 후 그룹 퇴역과 후속 원문 입력을 포함한다. UI normal/cancel/Undo·저장 실패·충돌·응답 유실·늦은 입력, 독립 LF/CRLF·새 교차 패키지/전체 압축 복원 결과는 최종 동결 뒤 기록한다. 초기 집중 fixture가 이미 provider가 있는 함수에 새 provider 준비 API를 잘못 사용한 실패는 제품 실패와 구분해 보존한다.

CSS/HTML·원본 레이아웃·공개 IO·권한·원래 C#을 보존한다. 승인된 실행별 임시물 정리와 최신/롤백 보관만 사용한다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 별도 미검증이다. 원래 wrapper의 명시적 실제 공개 결과 연결, 같은 계약 copy·자식 전체 갱신과 등록 import 관측의 잔여는 [유한한 마감표](M12_CLOSURE.md)를 따른다.


## 최종 동결 검증 결과 — 2026-11-03

제품·검사 동결 source는 `7eea5369d684a1a33fa39342e3b318618c53aea2`다. 독립 LF 20단계·CRLF 16단계·새 Windows 내용 교차 패키지/전체 복원/실패 수명관리 6단계, 총 **42단계(신규 38·동등 근거 재사용 4)**가 통과했다. 변경한 ordinary 관측 후보/API와 UI normal/cancel/storage/conflict/loss/late, 기존 native 진입·private forwarding·별도 공개 계약 caller·비void 반환 회귀 및 최종 readonly CAS를 검증했다. 집중 단계에서는 최종 원래 implicit-profile API 7개·UI 8개 확인이 통과했고, 원래 call 포트·반환 카드와 명시 caller UI를 픽셀로 확인했다. 변경한 제품/API/UI·독립 빌드·패키지 검사를 이전 근거로 대체하지 않았다.

재사용 4단계는 직접 Core runtime 17개·소유 경계 2개씩 두 checkout의 합계 38개 검사다. 참조 source `e64dea66427b25d4413b5a52bb393a3977fc47f6`와 현재 `src`, `tests/Confectory.Tests`, `targets/dotnet` Git 객체 및 SDK/NuGet/configuration/RID를 대조했다. 해당 직접 검사는 변경한 element-authoring 후보/UI를 호출하지 않는다. informational-version 바이트 동일성을 주장하지 않으며 증거에 `core-source-equivalence.json`, 정확한 `reusedFrom` 단계와 참조 로그 SHA/controller를 보관했다. 기본 저장소 harness는 이 Core 단계도 새로 실행한다.

최초 집중 API는 fixture가 provider를 이미 가진 선언을 새 provider 준비 API에 잘못 넣어 편집 거래 전에 실패했다. 실제 제품 실패가 아니며 실패 로그와 입력을 보존했다. fixture가 단순 선언에서 원래 hash를 준비하도록 수정한 뒤 API/UI가 통과했다. 그 후 native observer의 원래 implicit profile을 유지하도록 후보 경계와 fixture를 보완하고 해당 API/UI를 다시 실행했다. 최종 코드에서는 profile migration 없이 일반 Core 원본 검증을 통과해야 한다. 이 이전 성공/실패 기록은 최종 동결 검증 수에 섞지 않았다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/4362b483828041e4bec03af0a2074147.json`
- 최종 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/4362b483828041e4bec03af0a2074147.zip`, SHA-256 `795d3427a6a2bf0b73bee20a751209bf607a4c5a94353e444404c642195f80d1`
- 집중 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/59e6ca3972ef497ab75f431b6d2ce424.zip`, SHA-256 `8e07b715a2e50bcdf4ef6c886df6440a51b6617820702daf815c6fc2cb5d3f70`
- 최신 패키지 source `7eea5369d684a1a33fa39342e3b318618c53aea2`, archive/SHA `9381d4837d28e76efddaf8df0c66da05a8a91cd9b9e6b6c01fc5da6f27d0b44a`, 2371파일·147디렉터리, 51,348,933 bytes, manifest SHA `3e0e228ab3cfcd450da9ff5fb6f1510ffa5d96bf5456307a0980121dd6186013`.
- 정상 롤백 source `0f0ea8ca238e89d655065749d61eb4a36bddfd2c`, archive/SHA `1384cd7ceb013187e572dc45de358fd227d6f51a35747ebe087bb6f33c41b2db`, manifest SHA `9fe69780b223e71d3ba5fd133b4150ba4c5fcda5930b919d3516df55081578ed`.

새 패키지와 전체 압축 복원본의 같은 ordinary observer·직접 caller 저장/실행/cold 및 늦은 입력을 검증했다. 전체 파일·디렉터리 mode·크기·SHA를 대조한 뒤 최신/정상 롤백 두 세대 저장소에 원자 승격했다. 교차 검사는 Linux dotnet/Chromium이며 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달을 뜻하지 않는다. 독립 편집 창과 프로젝트 왕복은 이번 단위에서 새로 실행하지 않았다. 이전의 다른 흐름 증거로 대신 완료라 표시하지 않는다. 롤백판의 기존 Root 그룹 검증기는 이번 ordinary observer 그룹을 처리하지 못하므로 새 checkpoint 거래를 구버전에서 이어갈 수 있다고 보장하지 않는다(이전 소스 검증기 대조 근거이며 구버전 실행 검사는 새로 하지 않았다). 현재 버전의 전체 복원과 원시 입력·원본 보존을 검증하며 자동 역변환이나 구버전 검증 약화는 추가하지 않는다.

집중 및 최종 실행이 직접 만든 임시 작업공간은 자식 종료·지속 증거 검증 뒤 정리했다. 최신/롤백의 승인된 승격 외 기존 자료 삭제는 없었다. 최종 전 여유 1855.20MiB, 정리/승격 뒤 1851.32MiB, 신규 단계 표본 최소 1855.13MiB였다. 단계 표본은 보관/승격 모든 순간의 최소값을 보장하지 않으며 별도 지속 공간 144MiB(안전 64MiB 포함)를 확보했다. RAM 작업공간 3GiB+512MiB·추가 메모리 7GiB+1GiB 예산을 낮추지 않았다. 신규 단계 cgroup 메모리 표본 최고 4595.00MiB, 집중 기록 순증가 0.86MiB·최종 기록 순증가 3.88MiB다. 단위 시작부터 최종 종료까지 실제 디스크 순증가는 4.91MiB이며 증거·코드/Git·그 시점까지의 보관 기록을 포함한다. 이후 보고/게시 쓰기는 별도로 확인한다.

남은 M12는 기존 wrapper의 명시적 실제 공개 계약/OriginalResult 연결, 같은 계약 copy·자식 소유 본문이 포함된 정의 전체 갱신, 등록 외부 import/manifest/scope 관측이다. 이 유한한 원래 흐름이 닫히면 M4의 확정된 명시 async caller 정책과 실제 await→출력→완료→결과 분기→다음 실행을 진행한다. M11은 구체적 회귀가 없어 닫힌 상태다. 새로운 타입/문맥 조합·자동 migration·새 권한을 잔여로 추가하지 않는다.

후속 보고 문서 커밋은 동결 제품·검사 트리를 유지하며 work/current 게시 뒤 원격 SHA·clean·main 보존을 확인한다.
