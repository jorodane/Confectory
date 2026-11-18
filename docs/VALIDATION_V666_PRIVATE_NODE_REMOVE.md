# Private C# 노드의 마지막 상수 값 인자 제거 공동 저장 검증

게시본 `937e5adc6731c9a37e1eb7020ddb9f19cc02a9b6`와 기존 증거를 보존하고 runtime `625f850db61b49e84205865946d6041ef00bbf2e`의 [유한 흐름](V666_PRIVATE_NODE_REMOVE.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9이다.

- 직접 소유 qualified `inner/body` next code의 원래 두 스칼라 값 인자 중 마지막 long 인자를 명시적으로 제거했다. 제거되는 원래 연결이 타입을 명시하지 않은 정확한 int32 정수 상수인 범위다. 실제 CLR reflection에서 private 인자 수2→1, 원래40·편집 뒤20 실행을 확인했다. 원래 literal5 하나만 해제하고 첫 인자·long 반환·부모 frame/public/native ABI·나머지 입력 표현식·caller·노드 ID/좌표·실행선·정확한64비트 local·선택 밖 bytes/mtime를 보존했다. C# 본문/helpers와 함께 저장한 다른 native 본문은 직접 작성했다. 후보의 정·역순도 대조했다.
- 삭제된 secondNative를 사용하는 원래 본문/helpers를 그대로 둔 후보는 실제 compiler CS0103으로 거절됐다. 원래 parent-input·타입 명시 literal 프로그램은40, 넓은 long literal 프로그램은0을 먼저 실행하고 삭제 후보 거절을 확인했다. 첫 인자 제거·이름/타입/ref 역할/반환 혼합·여러 인자 제거·다른 바인딩을 자동 변환하거나 재연결하지 않는다.
- 온전한 이전 package에서 원래40·실제 private 인자2개와 계약 불변 후보는 유효했고 새 삭제 후보는 거절됐다. 실제 이전 UI도 입력을 보존한 채 Code Save를 거절했다.
- 오래된 source/graph/before 서명, 남은 인자 변경·역할/반환/수/순서 혼합·공개 계약·C# 오류·helpers 경계·마지막 native 본문 오류를 원자적으로 거절했다. pending graph/receipt에 제거된 인자 바인딩을 다시 끼우는 변조도 거절했다.
- 기존 매개변수·본문/helpers 영역을 사용해 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·미지원/혼합 입력 보존을 검사했다. 모의 metadata DOM과 실제 Linux engine/Chromium·CLR을 구분한다. 실제 화면의 부모 계약·남은 첫 long 인자·수동 helpers·Cancel/Code Save를 확인했다. 긴 본문은 기존 가로 스크롤 영역을 사용한다.
- 한 Save·기본/독립 창·cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 입력·프로젝트/창 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 현재 node/graph 증거를 검증하면서 최초2인자 서명/source/graph 해시·읽기 버전을 유지했다. post-Review5경로 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·일반 값→ref·struct·whole API·native 반환·retained guard·등록 helper와 직전 private long→void 후보/guard 회귀를 새로 실행했다. 앞선 private 반환·인자 타입·이름 DOM도 함께 검사했다. 이 회귀를 기존 전체 UI 재검증으로 합산하지 않는다.
- 새 Windows용 package의 구조/hash/mode와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창/실행·DOM을 확인했다. package 실패 주입에서 기존 runtime/package도 보존됐다. Windows 산출물 검사는 Windows 기기 실행 증거가 아니다.

제품 변경은 InformationFunctionGraphs·InformationFunctionContracts·InformationFunctionWholeBodies·feature-authoring.js·WebBundle hash의5파일이다. 현재 metadata에 제거 가능한 원래 마지막 인자 목록만 추가하고 workspace1·receipt3/nativeBodyContexts와 기존 source/graph/path/hash·읽기 관측·소유권·권한·Review/Confirm·최종 CAS를 재사용한다. 저장 schema/profile/receipt·권한은 추가하지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발15단계 중14통과·1실패와 최종48단계는 별도 신규 실행이다. 개발의 첫 baseline 검사는 제품 실행을 담은 어셈블리 대신 호출 proxy 어셈블리에서 reflection을 수행해 private metadata를 찾지 못했다. 원래 생성된 두 인자 C# 원문과 실패 로그를 보존하고 fixture만 Assembly.GetExecutingAssembly()로 바로잡았다. 같은 원본과 온전한 이전 package를 사용한 수정 baseline에서40·인자2개를 확인했다. 준비 진단 1건과 개발 실패 1건은 이 동일한 fixture 문제의 기록이며 별개 제품 실패로 세지 않는다. 최종48단계는 수정된 fixture와 고정 source에서 모두 새로 실행해 실패0·재사용0이다.

최종 trusted UI 클릭 경합 증거를 대조했고, 늦은 설명의 확정값은 개발1·최종2 보관 원문 path/hash로 확인했다. 앞선 최초 복원480초 시간 초과·과거60초 미응답·초기 빈 화면 원인은 미확정이다. 이번 통과를 그 원인 해결로 표현하지 않는다.

이전 runtime `8af6f656d2d33bf4c37c4c6fe756c37647bc9530`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. 이전 package의 원본 source hash/inode/mode/mtime를 유지했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행 및 private 인자1개 marker를 확인했다. pending과 확정 source의 호환성은 별개이며 일반 migration/downgrade나 더 오래된 Reference reader 지원은 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 625f850db61b49e84205865946d6041ef00bbf2e | 138a99288d3aa1f359dabfc455a03ef9f0807e2d018a29b2ecbbb2c45dbde7a3 | 54160032 |
| rollback | 8af6f656d2d33bf4c37c4c6fe756c37647bc9530 | fac13f9cee334a0c67a7c1160b4fd4806b5d2953a8cce70c8dfc07b99e3fd1ac | 54159397 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/86e8aa9020f542dca0452b205ca8ffd0.json`, evidence SHA256 `6aa112b531be31f6f3ee47634b39a746152f0c3a058bc8ac94f9bcb23f85e775`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/544e2e5cf72a49ab9c67c84974d7ba63.json`, evidence SHA256 `71f42c7cbf895bf62a6eeb4f51c73d22a26865593a337285ef04f34977718c51`.
두 package·두 evidence hash와 확정 설명 원문을 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23840784384bytes(22.20GiB).

완료는 직접 소유 private next code의 마지막 상수 값 인자 삭제·수동 본문/helpers·다른 native 본문의 공동 저장이다. 원래 두 인자의 마지막 untyped int32 literal long이라는 조건은 이번 검증된 구현 경계이며 일반 삭제의 영구 UX 정책으로 확정하지 않는다. 다른 인자 수/바인딩·타입/ref-out·반환/입출력 구조·사용되는 반환 소비 대응·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. main은 사용자 검토와 merge에 남긴다.
