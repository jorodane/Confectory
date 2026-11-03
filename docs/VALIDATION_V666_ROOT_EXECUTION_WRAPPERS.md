# M12 명시적 공개 결과 wrapper

원본 v666 ZIP의 `dist/blueprint.js:1503–1519`는 원본 핀·분기·공개 출력을 wrapper 계약에 고정하고, 원본을 한번 호출한 뒤 `OriginalResult`를 자체 `Result`에 명시 대응한다. 원본이 바뀌면 계약 갱신을 요구한다. 이번 흐름은 기존 `IInvoke`·NoBranch adapter를 자동 전환하지 않고 이 공개 결과 연결을 추가한다. 원본 소유권·IO·override·권한·레이아웃·Review→Confirm은 유지한다.

새 공개 결과 wrapper는 기존 `execution-enum` post-call에 명시적인 `originalExecution` receipt를 추가한다. receipt는 실제 함수의 공개 계약과 출력 snapshot을 함께 고정한다. 생성된 별도 `IExecutionInvoke` 캡처를 한번 호출해 ref/out·native 반환과 공개 출력을 보존한 뒤 원래 실행 결과를 자체 C# 분기로 전달한다. 알 수 없는 원본 enum 값을 묵시적 기본값으로 바꾸지 않는다. 기존 receipt가 없는 legacy wrapper는 계속 ordinary `IInvoke`·NoBranch로 실행한다. 새 wrapper의 ID·원래 case 연결과 main continuation을 보존한다.

직접 소유한 동기 caller의 기존 참조 카드에서 원본 버튼·enum/C# 편집기·private 입력·Undo/Redo·Save를 사용한다. 원본 분기 ID/값을 자체 enum 초기값에 유지하고 기존 C# 이름 검증과 32개 예산을 재사용한다. 사용자가 편집 가능한 enum/body/helpers와 고정된 원본 호출/OriginalResult/출력 문맥을 구별한다. 원래 C#·부모/외부 원본을 쓰거나 override의 독립 계약을 만들지 않는다.

새 공개 wrapper의 저장은 기존 단일 후보·전체 소스 proof·checkpoint/CAS·응답 receipt 수명관리에 연결한다. 이를 우회하는 순차 public-wrapper 저장은 거절하며 legacy 경로는 유지한다. 저장·cold 복원·Review 뒤 원본/소유 문맥·scope의 읽기 의존성이 같은 최종 파일 CAS에 참여한다. 새 wrapper 변경의 checkpoint receipt가 누락·변조되면 거절한다. 확정 뒤에는 marker를 퇴역시켜 독립된 후속 편집과 혼동하지 않는다. 기존 wrapper의 다른 편집도 실제 원본 계약·소유 문맥의 최종 읽기 가드를 유지한다.

공개 원본의 분기 계약을 갱신할 때 실제 public-wrapper 전체를 명시 선택해야 한다. 새 original receipt와 원래 함수·target/caller를 하나의 checkpoint/Review/최종 CAS에 결합하며 wrapper 자신의 enum·C#·연결은 자동 변경하지 않는다. 삭제한 원본 멤버를 C#에서 참조하는 등 불완전한 코드는 검토/컴파일에서 고치도록 남기며 임의 fallback이나 소스 재작성을 추가하지 않는다. source/Node ID·공개 IO·native 데이터 반환은 유지한다.

집중 검사는 정수 out 및 기존 비void/ref/out 함수에서 실제 호출 횟수·출력 snapshot·실행 분기와 반환선을 확인한다. 위장/누락 receipt·잘못된 primary·전체 wrapper 선택 누락·checkpoint/Review 뒤 경합·cold와 중복 응답을 구분한다. UI는 원본의 고정/편집 영역·잘못된 enum/취소·Undo/Redo·저장 실패·중단/응답 유실/늦은 입력과 원본 계약의 명시 선택을 확인한다. 최종 동결 LF/CRLF·기존 legacy/compiler 회귀·새 패키지/전체 복원·실패 수명관리 결과는 검증 후 아래에 기록한다.

현재 지원은 직접 소유한 일반 Root caller와 이미 공개된 동기 함수의 기존 데이터 ABI다. wrapper를 독립 계약 복제나 비소유 부모/참조 편집으로 확장하지 않는다. 같은 계약 copy·자식 소유 본문의 정의 전체 갱신과 등록된 외부 import 관측은 [유한한 M12 표](M12_CLOSURE.md)의 남은 두 흐름이다. 가능한 타입/문맥 조합마다 새 필수 작업을 만들지 않는다. M4의 동기 caller 오류 정책과 실제 async 실행은 별도다.

승인된 실행별 임시물 정리와 최신/정상 롤백 보관만 사용한다. UI 이미지는 생성한 테스트 자산/fixture이며 계정·live AI·유료 호출은 없다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 교차 패키지 검사와 별개다. 구버전은 새 `originalExecution`/checkpoint receipt를 처리하지 못하므로 새 거래를 구버전에서 이어가는 자동 migration은 제공하지 않는다.


## 최종 동결 검증 — 2026-11-03

제품·검사 source는 `7cbc199b1170d94a48d9b47f49bcf92aba00c8c6`다. 독립 LF 20·CRLF 16·새 Windows 내용 교차 패키지/전체 압축 복원/실패 수명관리 6, 총 **42단계(신규 42·재사용 0)**가 모두 통과했다. Core가 변경되어 공개 반환 runtime 17개와 소유권 2개를 두 checkout에서 새로 실행했다. 기존 검증 로그를 최종 성공 단계로 대체하지 않았다. legacy enum wrapper·후처리 compiler, ordinary 관측/NoBranch adapter·비void 반환과 최종 읽기 CAS도 영향 회귀에 포함했다.

UI normal/storage/conflict/loss/late에서 private Undo/Redo·잘못된 enum/취소·저장 전 cold·checkpoint 쓰기 실패·Save 전 원본 변경·저장 응답 유실/재조회·저장 중 새 C# 입력 보존·Review 취소/Confirm·확정 후 cold를 확인했다. normal은 원본 계약의 모든 wrapper 명시 선택 누락 거절과 선택 후 Save/cold/전체 Review/CAS도 확인했다. 실제 원본 한번 호출→native 데이터 snapshot→자체 분기→기존 반환 실행을 검증했다. 새 생성 패키지의 normal 및 전체 복원 패키지의 late 흐름을 다시 실행했다. 최종 스크린샷도 기존 창·카드·반환선 배치를 확인했다. 독립 창·프로젝트 왕복·실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 이번에 새로 실행하지 않았으며 다른 근거로 완료라 표시하지 않는다.

집중 최종 API 7개·비void/ref/out API 7개·UI 6개 확인이 먼저 통과했다. 그 이전 반복에서 실제 제품의 wrapper 원본 읽기 의존성이 최종 CAS에서 누락된 결함을 찾아 checkpoint·복원·최종 CAS receipt 검증으로 보완했다. 누락/변조 marker·계약·소스·경로와 Review 뒤 원본 변경을 거절한다. 초기 컴파일/번들 pin 수리와 테스트 요청 스키마·빈 reviewIds·textarea LF 기대 수정, 진단 성공 빌드의 잘못된 예상 종료코드는 각각 보존된 로그에 구별한다. 최종 집중/동결 성공 수에 과거 실패를 통과로 포함하지 않는다. 원본 분기 이름/추가 변경은 새로 확인했으며 원본 멤버 삭제 후 사용자의 C# 대응 편집 UI 전체를 이번 성공 검사로 주장하지 않는다. 삭제된 멤버 참조는 원래 compiler 검토 오류로 남긴다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/81d92fd5fb0640b194b46d707ad082be.json`
- 최종 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/81d92fd5fb0640b194b46d707ad082be.zip`, SHA-256 `cc83838a3a0ba104bdee1fdef21d763b466b9091f3a7201698f99eaa35cafc9b`.
- 집중 지속 증거: `/workspace/artifacts/v536-verification-managed/runs/2710b118dd9c44a19da89dcd3b98e834.zip`, SHA-256 `a37cf716c31ae655eb4356162706a66b97e6cffb9ae9e1659aed868ae62973f2`.
- 최신 source `7cbc199b1170d94a48d9b47f49bcf92aba00c8c6`, archive/SHA `e346972caa5f54e9d580792cc62dd74d1c4d63311e215cf1c1231b7bd6ce2207`, 2371파일·147디렉터리, 51,363,342 bytes, manifest SHA `cb3931fbf1897269db1477296ba3f2df94856f74c2665a61427f4ccd234eb0ec`.
- 정상 롤백 source `7eea5369d684a1a33fa39342e3b318618c53aea2`, archive/SHA `9381d4837d28e76efddaf8df0c66da05a8a91cd9b9e6b6c01fc5da6f27d0b44a`, manifest SHA `3e0e228ab3cfcd450da9ff5fb6f1510ffa5d96bf5456307a0980121dd6186013`.

전체 파일·디렉터리 mode/크기/SHA 및 압축 복원을 확인하고 최신/정상 롤백 두 세대를 원자 승격했다. 구버전은 새 `originalExecution`/public-wrapper receipt를 처리하지 못하므로 새 거래를 구버전에서 이어갈 수 있다고 보장하지 않는다. 자동 역변환이나 구버전 보호 약화는 추가하지 않았다. 현재 버전의 원문/입력 보존과 복원을 검증했다.

집중/최종 실행의 직접 생성 임시물은 자식 종료·지속 증거 검증 뒤 정리했다. 승인된 최신/롤백 승격 외 기존 자료 삭제는 없었다. 최종 전 여유 1849.34MiB, 정리/승격 후 1846.09MiB, 신규 단계 표본 최소 1849.29MiB·cgroup 메모리 표본 최고 4512.61MiB다. 표본은 보관 모든 순간의 최소/최대를 보장하지 않는다. 지속 예산144MiB(안전64MiB 포함)·RAM3GiB+512MiB·추가메모리7GiB+1GiB는 낮추지 않았다. 단위 시작→최종 종료의 디스크 순증가는 5.15MiB이며 코드/Git·집중/최종 증거·관리 보관본 차이를 포함한다. 보고/게시 쓰기는 이후 별도로 측정한다.

M12의 유한한 남은 흐름은 같은 계약 copy·자식 소유 본문이 포함된 공개 정의 전체 갱신, 등록 외부 import/manifest/scope의 readonly 관측 두 항목이다. 완료한 copy/자식의 기존 분기 반환 편집은 중복 잔여가 아니다. 이후 M4의 명시 async caller 정책과 실제 await→출력→완료→결과 분기→다음 실행 및 고정 V2–V9/UI 잔여를 따른다. M11은 실제 회귀가 없어 닫혀 있다. 새 타입/문맥 곱·자동 migration·비소유 쓰기·새 권한을 필수 요구로 추가하지 않는다.

후속 보고 문서 커밋은 동결 제품·검사 트리를 유지한다. work/current만 정상 게시하고 원격 SHA/clean·main 보존을 별도 확인한다.
