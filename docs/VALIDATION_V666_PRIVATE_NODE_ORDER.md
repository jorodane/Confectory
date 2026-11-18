# Private C# 값 인자 순서와 공동 저장 검증

게시본 `aacf4c110ef289aae77d94181d54f13efdb8d307`와 기존 증거를 보존하고 runtime `22f1e9a868399096ee267869e0efd7aa8b544812`의 [유한 순서 변경](V666_PRIVATE_NODE_ORDER.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9이다.

- 직접 소유 qualified `inner/body` next code의 두 long 값 인자 선언을 firstNative,secondNative에서 secondNative,firstNative로 명시했다. 단일 입력 읽기와 타입 없는 정확한 int32 상수 연결을 각 원래 이름에 그대로 보존했다. 원래 값·이름·타입·값 역할·수·long 반환·부모 frame/public/native ABI·caller·노드 ID/좌표·실행선·정확한64비트 local·선택 밖 bytes/mtime를 유지했다. 요청의 정·역순도 대조했다.
- 원래 C# 본문/helpers와 다른 native 본문을 그대로 둔 순서 변경을 실제 Review/Confirm으로 적용해40을 유지했다. CLR reflection은 원래 firstNative,secondNative와 확정 후 secondNative,firstNative를 각각 확인했다. 별도로 직접 편집한 private 본문/helpers와 다른 native 본문을 한 후보로 저장하고20을 실행했다. 후자는 수동 본문 편집의 효과이며 순서 변경이 값을 서로 바꾸거나 계산을 자동 변환한다는 뜻이 아니다.
- 온전한 이전 package에서 원래40·실제 선언 순서와 계약 불변 후보는 유효했고 순서 변경 후보는 거절됐다. 이전 UI도 명시 입력을 보존한 채 Code Save를 거절했다. 유효한 typed literal 원본은40, wide/local 원본은 정확한 값 검사 뒤0을 실행하고 이번 순서 변경 후보를 거절했다.
- 오래된 source/graph/before 서명, 이름/타입/ref 역할/반환·인자 수 혼합·중복 이름·공개 계약·잘못된 C#·helpers 경계·마지막 native 본문 오류를 원자적으로 거절했다. 원래 연결 값과 frame·소스·receipt/read 증거 변조도 거절했다. 원래 이름/타입/반환/상수 인자 삭제 기능은 별도의 기존 명시 흐름으로 유지했다.
- 기존 매개변수·본문/helpers 영역의 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·미지원/혼합 입력 보존을 검사했다. 실제 Linux engine/Chromium 화면에서 부모 계약과 명시한 선언 순서·수동 본문/helpers·Cancel/Code Save를 확인했다. 모의 metadata DOM을 실제 엔진·CLR 또는 전체 UI 검증으로 합산하지 않는다.
- 한 Save·기본/독립 창·cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 입력·프로젝트/창 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 현재 node/graph receipt를 검증하면서 최초 선언 순서/source/graph 해시·물리 읽기 버전을 유지했다. post-Review5경로 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·값→ref·struct 입력·whole API·native 반환·retained guard·등록 helper와 직전 private 인자 삭제 후보/guard를 새로 실행했다. 이전 삭제·반환·인자 타입·이름 DOM도 검사했다. 이 회귀를 모든 private ABI·retained/opaque 조합 또는 전체 UI 검증으로 표현하지 않는다.
- 새 Windows용 package의 구조/hash/mode와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창/실행·DOM을 확인했다. package 실패 주입에서 기존 runtime/package가 보존됐다. Windows 산출물 사전검사는 Windows 기기 실행 증거가 아니다.

제품 변경은 InformationFunctionGraphs·InformationFunctionContracts·InformationFunctionWholeBodies·feature-authoring.js·WebBundle hash·ApplySlots.csbody의6파일이다. 현재 metadata에 순서 편집 가능 표시만 추가했다. workspace1·receipt3/nativeBodyContexts와 기존 원래 path/hash/whole·읽기 관측·소유권·권한·Review/Confirm·최종 CAS를 재사용하며 저장 schema/profile/receipt·권한은 추가하지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 실행22건 중 정상 종료17·실패5와 최종48단계는 별도 신규 실행이다. 첫 baseline은 runner가 직전 인자 삭제 검사를 잘못 지정해 metadata 기대값에서 실패했다. 다음 baseline은 재현용 reflection C# 변수의 누락된 nullable 표기 때문에 compiler CS8600으로 원래 실행 전에 실패했다. runner 경로와 test Main의 string? 표기만 바로잡고 같은 Workspace·온전한 이전 package에서 원래40·선언 순서와 API/UI 거절을 확인했다. 실패 로그·수정 전 runner/fixture를 보존했으며 두 준비 진단은 이 두 검사 오류의 분류다. 별도로 실제 저장에서는 선택했지만 내용이 그대로인 두 번째 native 본문이 atomic 검토 그룹에서 빠지는 제품 결함을 재현했다. 기존 guard는 전체 Save를 거절하고 checkpoint·원본을 보존했다. 동일 후보의 선택 소스 증거를 완성하면 엄격한 guard가 통과하는 순수 진단도 보관했다. ApplySlots는 원본 검증을 거친 기존 context의 선택 함수·본문을 같은 atomic 그룹에 포함하며 원래 kind/path·읽기 관측·그룹 예산·guard·최종 CAS를 유지한다. 첫 보완 빌드는 기존 지역 변수와의 이름 충돌(CS0128/CS0165)로 실패했고 새 변수 이름만 바로잡았다. 새 엔진에서 명시한 불변 소스의 cold 복원·post-Review 경합 거절과 원래 본문 그대로40 실행을 다시 확인했다. 이어진 DOM 검사는 공통 순서 규칙이 private 선언 대신 부모 공개 인자 이름을 비교해 입력을 거절하는 UI 오류를 드러냈다. 기존의 정확한 private 선언/capability 검증을 유지하면서 private 분기에서는 전달받은 부모 계약의 보존을 확인하고 일반 native 순서 규칙의 동작을 유지했다. 수정 DOM 검사를 한 번 실행하고 동일 파일 hash를 확인해 중복 실행하지 않았다. 그 뒤 새 엔진에서 API·실제 UI를 검사했다. 진단 단계는 실패 원인을 확인한 것이며 제품 성공 검사로 합산하지 않는다. 최종48단계는 고정한 source·수정한 검사에서 모두 새로 실행했고 재사용·실패0이다.

최종 trusted UI 클릭 경합 증거를 대조했고 늦은 설명의 확정값은 개발1·최종2 보관 원문 path/hash로 확인했다. 초기 빈 화면·과거60초 미응답·최초 복원480초 시간 초과 원인은 미확정이다. 이번 통과를 그 원인 해결로 표현하지 않는다. 이번 최종 CRLF 검사 중 읽기 전용 monitor 명령 생성이 exec-server transport disconnected로 한 번 실패했다. 이후 새 pwd·git·상태 확인 명령과 기존 검증 PID/start identity·고정 커밋·clean 상태가 확인됐고, 같은 백그라운드 검증은 재시작 없이 계속됐다. 이 전송 관측과 검증 실패를 구분하며 연결 오류의 근본 원인은 미확정이다.

이전 runtime `625f850db61b49e84205865946d6041ef00bbf2e`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. 이전 package의 원본 source hash/inode/mode/mtime를 유지했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행과 뒤바뀐 실제 선언 순서를 확인했다. pending과 확정 source 호환성은 별개이며 일반 migration/downgrade나 더 오래된 Reference reader 지원은 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 22f1e9a868399096ee267869e0efd7aa8b544812 | f894b7cd07b72384d05332c5ed57e79d03f1f4686b78b099688149d1a3e16632 | 54158475 |
| rollback | 625f850db61b49e84205865946d6041ef00bbf2e | 138a99288d3aa1f359dabfc455a03ef9f0807e2d018a29b2ecbbb2c45dbde7a3 | 54160032 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/fb0d392b049e4accbd0d3fbcbe864045.json`, evidence SHA256 `320d19c6d577976f3c77f35768047311d6facf018d21bb9eae901112c16590df`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/ee13cca72c444c96a3e538e4e51fcc64.json`, evidence SHA256 `9f0bfbffb7f404106e9599ab4dd7edcdd436ff86a9fdd3f59df2ca8762618c7d`.
두 package·두 evidence hash와 확정 설명 원문을 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23820193792bytes(22.18GiB).

완료는 두 long 값 인자의 명시 순서 변경·이름별 연결 보존·수동 본문/helpers·다른 native 본문의 공동 저장이다. 단순 input/int32 literal 조건은 이번 검증된 구현 경계이며 일반 순서 편집의 영구 UX 정책으로 확정하지 않는다. 다른 인자 수/연결·타입/ref-out·반환/입출력 구조·사용되는 반환 소비 대응·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. main은 사용자 검토와 merge에 남긴다.
