# Private 본문·선택 callee 값→out 검증 및 연결 복구

구현 `40adeddfa67c528810c6c1828c0890053b1f6339`와 게시본 `f26ab5a522e8d80844ab8e166fddee36b1a3908e`를 보존하고, 검사 경로와 증거 재사용 도구만 수정한 `9b67cb77f25620e66e255ae33497c909eca43db9`를 검증했다. **총48: 신규21·검증된 재사용27·실패0**이다. LF26은 신규6/재사용20, CRLF13은 신규6/재사용7, 새 package/전체 ZIP 복원9는 모두 신규다. 실제 Linux .NET·Chromium과 모의 renderer 검사를 구분하며 실제 Windows 기기·전체 UI는 미검증이다.

callee의 long 값 입력 count 하나를 out으로 직접 전환하고 nativeAmount/nativeCount·원래 long 타입/순서/반환·private/frame/code ABI를 유지했다. private ordinary call의 상수0과 공유 caller의 기존 count 바인딩을 각각 명시 해제하고 기존 반환 대응은 identity로 유지했다. 두 수동 C# 본문/helpers, 정·역순 같은 후보와 실제 실행15, 직접 native 반환25/out5를 확인했다. 새 C#·out 할당·바인딩·형변환을 추론하지 않는다.

기존 구현 선택기·매개변수 영역은 scoped caller가 있는 이 경로에서도 원래 값 입력 하나의 out만 허용한다. ref·추가 역할·native 이름/타입 변경을 거절한다. 첫 owner Save 전 C# 재진입에서 헤더에는 native 이름이 보이지만 계획은 공개 이름으로 바뀌던 결함을 수정했다. 같은 원본 hash/path·서명과 명시 plan에 한해 native out 서명·본문을 유지하며 readonly draft에도 기존 parameters marker를 보관한다. 범용 native available·권한은 유지한다.

취소·Undo/Redo·한 Save·cold·독립 창·저장 실패/재시도·응답 유실/중복 방지·늦은 입력·후속 Save·프로젝트/창 경계·Review 취소/Confirm을 검증했다. 누락·잘못된 두 caller 입력 해제/출력 대응, native/private ABI 변조와 할당 없는 out C#을 거절했다. 원본9경로의 post-Review 경합은 Confirm 전체를 차단하고 원본/peer/checkpoint를 보존했다. 원본 복원 뒤 새 Confirm·실행을 통과했다. 후속 source Save는 현재 ABI/receipt를 사용하면서 최초 값→out·원래 source/flow/import·물리 읽기 버전을 유지했다. 기존 out→값/값→out·struct·whole·retained/helper와 직전 callee scalar 반환 회귀도 보존됐다.

연결이 끊긴 동안 기존 검증은46단계를 통과한 뒤 복원 renderer의 이전 회귀 파일을 `restored/content/tests`에서 찾아 실패했다. 새 renderer8개 자체 검사는 통과한 상태였으며, package가 테스트 파일을 포함하지 않는 검사 경로 문제였다. `/workspace/artifacts/v536-verification-managed/runs/a6a12a6c49ba4e97b564daffa64c1df9.json`와 원래 실패 로그/ZIP을 변경하지 않았다. lookup 한 줄을 runner의 sibling 파일로 바꿨다. LF에서는 두 경로가 같은 파일임을 증명하고, 모든 제품/다른 fixture/test bytes·SDK/NuGet/configuration·명령·LF/CRLF checkout 사실·기존 archive 전체 hash/mode를 검증해27개 성공 사실만 재사용했다. 실패/미실행 검사와 빌드/package는 재사용하지 않았다. 기존 임시 산출물은 원래 검증 도구의 실패 정리로 없어진 상태여서, 필수 checkout·복원·빌드12단계와 package/복원9단계를 새로 실행했다. 새 package에서 정상 Save·전체 ZIP 복원·응답 유실·늦은 입력·독립 창 실행·수정 renderer·package 실패 보존이 모두 통과했다.

제품 변경은 InformationFunctionWholeBodies·feature-authoring.js·WebBundle hash 세 파일이며 `40adeddfa67c528810c6c1828c0890053b1f6339` 이후 동일하다. 기존 ValueOut·단독 Contracts/Graphs·assembled compiler가 원래 두 계획과 결합 후보를 검증한다. 해당 그룹은 같은 원래 snapshot에서 검증·결합하며 receipt를 overlay에 rebase하지 않는다. unchanged 관측은 한 명시 변경과 결합하고 서로 다른 변경 결과는 거절한다. schema/workspace1·receipt3/nativeBodyContexts·예산·소유권·권한·authored layout·Review/Confirm·최종 CAS, 정보별 struct·종류 enum·모듈 interface 및 명시 async 전환 전 sync caller 오류를 유지한다.

개발18단계와 독립 진단3건은 최종48과 별도다. 개발 실패/정정 사유는 `failure-causes.json`과 원래 로그에 보존했다. JS undefined mode의 검사 도구 표현 차이, caller별 해제 컨트롤 선택 오류, 초기 진단 fixture 계약 참조 오류와 실제 재진입 결함을 구분했다. 호환성 스크립트의 이전 UI 로그 선택 오류도 완료된 guard를 재실행하지 않고 정정했다. 이전 runtime `23092cef8cb9bf4eda102bbd412954b49a880202`는 새 pending을 거절하지만 확정 일반 source는 그 이전 runtime의 CLI/providers로 새 build·실행15에 성공했다. 더 오래된 Reference reader 일반 호환성이나 자동 migration/downgrade는 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 9b67cb77f25620e66e255ae33497c909eca43db9 | 4d6f12cfd3c4e474ea9d99387076bb8f120572360ce0cc581881a0f0e38358a9 | 54156088 |
| rollback | 23092cef8cb9bf4eda102bbd412954b49a880202 | a8eb14491b2ca84278e8e18ff2fe1b96c74010d1a36505c2915ced911b05107e | 54152185 |

복구 record `/workspace/artifacts/v536-verification-managed/runs/b69e6c3287be413ea14985685374a110.json`, evidence SHA256 `b36f3b6a2e8f4927912338497883ed7785d7b777062f0b9cf87f1b763c9cc63a`.
이전46 성공/경로 실패 record `/workspace/artifacts/v536-verification-managed/runs/a6a12a6c49ba4e97b564daffa64c1df9.json`, evidence SHA256 `761bfc4c865ec9fa43a1b04dcf769d87bdb619cb15f672eb25b367f5e84301a3`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/6f85abe0e54348218a27e3e426e9b5a2.json`, evidence SHA256 `0dc3cc3b454150699191afe4842e267d8880b819bb8762d6bbac4a0184b7a6f5`.
두 package·세 evidence hash와 늦은 설명의 개발1·이전 최종2·새 복원1 확정 원문 path/hash를 대조했다. 원본 checkout·증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 유지했다. 정리는 인증된 검증 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 24035737600bytes(22.39GiB).

다른 callee 타입·역할·반환 구조·private ABI·retained/opaque import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
