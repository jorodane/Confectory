# Private 구현의 원래 일반 helper 호출·import 검증

게시본 `e6939cdd95a8539ed5da7622e78e1177ded927bf`와 기존 증거를 보존하고 runtime `62851acc0d9c089f3d9c502ba12d40c18f7da09c`의 [유한 흐름](V666_PRIVATE_ROOT_IMPORT.md)을 **최종 신규46·재사용0·실패0**으로 검증했다. LF24·CRLF13·새 패키지/전체 ZIP 복원9이다. 실제 Linux .NET/native 엔진·Chromium 자동화와 모의 metadata 렌더러 회귀, 물리 기기 검증을 구분한다.

- 온전한 이전 패키지에서 원래 프로그램40과 각 단독 private/반환 계획은 유효했다. 원래 private 구현의 일반 helper 호출·typed import가 있는 공동 후보와 실제 trusted UI Save만 거절됐고 입력·checkpoint·모든 원본을 보존했다.
- private 공개/프레임/code ABI와 native 입력/out·별칭을 유지했다. 직접 작성한 C# 본문/helpers, long→double 반환과 명시한 이전 반환 소비자의 호환 out 대응을 한 후보/CAS에 결합했다. 정·역순 후보가 같고 실제 caller20·직접 double 반환25.5·long out25를 확인했다.
- private 구현의 고정 fg_call 별칭·정확한 typed 계약과 실제 ordinary call/next 노드를 검증했다. 원래 helper 호출은 private 계산 결과를 받아 원래 반환으로 전달한다. root header·graph 전체 bytes, 호출/연결/좌표·정확한64비트 locals와 모든 ABI를 유지했다. helper 함수·구현·BOM/CRLF 본문은 쓰기 그룹 밖의 읽기 의존성이며 bytes·inode·mode·mtime도 보존했다.
- root import 별칭/계약·선택 callee·호출 누락·호출 서명·retained 저장소 문맥 변조를 거절했다. 기존 helper 누락/외부/부모·native 별칭/역할·source/flow/group 변조도 거절했다. root import header와 helper 세 경로의 readGuards를 하나라도 누락하면 거절했다. 새 alias/호출/C#/연결/저장소를 추론하지 않았다.
- 실제 UI의 취소·Undo/Redo·cold·저장 실패/재시도·응답 유실·중복 방지·늦은 입력/후속 Save·창/프로젝트 경계·Review 취소/Confirm을 검사했다. 후속 metadata/private 본문·현재 반환 서명 본문 Save는 최초 source/flow/caller·읽기 버전을 유지했다. Review 이후 graph·root import header·독립/선택 본문·caller graph·함수 정의와 helper 세 파일의 실제 변경은 Confirm 전체를 거절하고 peer/checkpoint를 보존했다. 원본 복원 후 새 Confirm/실행도 통과했다.
- 기존 private out→값/값→out·struct·whole API·native 반환·retained guard·등록 helper를 수정본에서 새로 회귀 검사했다. 기존 별칭 편집기 draft/CRLF/legacy의 모의 metadata DOM 회귀를 native import 수용 증거와 구분한다. 새 패키지 정상 실행과 전체 ZIP 구조·파일/hash/mode, 별도 추출본의 응답 유실·늦은 입력·독립 창/실행·렌더러도 통과했다. 패키지 실패 주입은 기존 package/runtime을 보존했다.

제품 변경은 InformationFunctionWholeBodies 한 파일이다. 단독 Contracts/Graphs·assembled compiler·version3 nativeBodyContexts·전체 원본 readGuards·Review/Confirm·최종 CAS를 재사용한다. workspace version1·receipt version3, UI/CSS·authored layout·권한·소유권·예산을 유지한다. Core Blueprint 고정 import 별칭·graph 문법은 변경하지 않았다. 새 schema/receipt/profile·외부 등록/접근·C# 자동 변환·암묵적 async caller 전환은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 16단계와 최종 신규46단계는 별도 증거다. 개발 실패/정정 기록 `{"baseline-private-root-import": "New original ordinary-call fixture omitted mandatory intent. Definitions rejected GRAPH_FIELD intent with sourceWritten=false; add the original call label. Product and intact package unchanged.", "baseline-private-root-import-corrected": "Original fixture used an arbitrary Blueprint import alias. Actual old compiler required FeatureBlueprint.ImportAlias(helper), the existing SHA256-based fg_call alias. Correct only fixture; do not loosen Core import contracts."}` 및 보조 준비 진단 0건을 보존했다. 초기 fixture의 필수 intent와 Core 고정 import 별칭을 바로잡았으며 제품 계약을 느슨하게 바꾼 것이 아니다. 최종 과거 검사 재사용은0이다. 실제 UI 경합 클릭과 입력/checkpoint 보존은 conflict-activation-proof.json에 남겼다. 늦은 설명의 확정값은 개발1·최종2 사례의 보관 FreeInfo 원문을 JSON 문자열로 해석하여 추가 대조하고 path/hash를 late-description-audit.json에 남겼다.

이전 runtime `08bfae72ba9be1bf4d1003e982a2e89ffb2b52da`의 온전한 archive·모든 추출 파일/디렉터리/hash/mode를 확인했다. 새 private-root import pending은 현재 guard가 수용하고 이전 guard가 거절했다. 같은 입력 source의 hash/inode/mode/mtime는 같다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 같은 이전 CLI/providers로 새 빌드·실행20도 확인했다. 새 pending 수용 경계와 일반 source 호환성을 구분한다. 더 오래된 Reference reader 제약은 기존 증거이며 자동 migration/downgrade하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 62851acc0d9c089f3d9c502ba12d40c18f7da09c | efe3c42f807218670845fe318ba61625373cda831d89ccee6d34f648b3d3e84f | 54151973 |
| rollback | 08bfae72ba9be1bf4d1003e982a2e89ffb2b52da | a66ee148d9ecacaf57db3a5227c2dc7d288cb83d4002e099e3b6b1662192200e | 54149944 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/91d06faff02e4c1db845cc46e6715efc.json`, evidence SHA256 `9a3ef08786ba21793098acbd0121a6877bcf9f3d9dc7f7318cd40f368db1226e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/b036a31635c546f48f7b896b7d618144.json`, evidence SHA256 `19a981d134838ede2d6f7d38edda96603e886796cd3e0c7768808bf710a723d5`.
두 package·두 evidence hash를 다시 확인했다. 원본 checkout·게시본·기존 증거와 미인증 IPC가 남은 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 이번 인증된 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 24123326464bytes(22.47GiB).

이 단위는 private 구현의 원래 ordinary helper call/import와 수동 본문·반환의 공동 Save/원래 읽기/CAS/실행으로 닫는다. 선택 callee·다른 역할/반환 구조·private ABI·retained/opaque import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
