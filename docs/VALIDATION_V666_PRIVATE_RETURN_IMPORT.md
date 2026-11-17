# Private 본문·반환 변경과 기존 소유 import 검증

게시본 `394ed40ba1f742a0a9f78d7118b18a5da0eb07b4`와 기존 증거를 보존하고 runtime `08bfae72ba9be1bf4d1003e982a2e89ffb2b52da`의 [유한 흐름](V666_PRIVATE_RETURN_IMPORT.md)을 **최종 신규46·재사용0·실패0**으로 검증했다. LF24·CRLF13·새 패키지/전체 ZIP 복원9이다. 실제 Linux .NET/native 엔진·Chromium 자동화와 모의 metadata 렌더러 회귀, 물리 기기 검증을 구분한다.

- 온전한 이전 패키지에서 원래 프로그램40과 각 단독 private/반환 계획은 유효했으나, 기존 소유 helper import가 있는 공동 후보와 실제 trusted UI Save는 거절됐다. 입력·checkpoint·원본/helper 파일을 보존한 실패 응답과 클릭을 기록했다.
- 기존 private 공개/프레임/code ABI와 native 입력/out·별칭을 유지했다. 직접 작성한 C# 본문/helpers, long→double 반환과 실제 이전 반환 소비자의 호환 out 대응을 원래 helper 호출과 한 후보/CAS에 결합했다. 정·역순 후보가 같고 실제 caller20·IInvoke double 반환25.5·long out25를 확인했다.
- helper는 이미 읽은 같은 프로젝트 함수의 원래 typed 계약이며 선택 함수/부모/외부 계약이 아니다. 원래 import 별칭·typed signature와 서명 이외 native header bytes를 유지했다. helper 함수·구현·BOM/CRLF 본문은 쓰기 그룹에 없으며 bytes·inode·mode·mtime를 보존했다. 세 helper 경로가 원래 readGuards에 포함되고 하나라도 누락하면 거절했다.
- 누락/외부/선택 callee/stale import·부모 helper·맞지 않는 import 별칭을 거절했다. 기존 계약/소비 대응·별칭/역할·source/flow/group 변조도 거절했다. 직접 소유 단일 C# target의 원래 안정된 helper import만 허용하며 private/whole 구현 import와 함께 변경하는 선택 callee는 별도 계획의 경계로 남긴다.
- 실제 UI의 취소·Undo/Redo·cold·저장 실패/재시도·응답 유실·중복 방지·늦은 입력/후속 Save·창/프로젝트 경계·Review 취소/Confirm을 검사했다. 후속 metadata/private 본문·현재 반환 서명 본문 Save는 최초 source/flow/caller·읽기 버전을 유지했다. Review 뒤 private graph/node·독립 원문·caller graph·함수 정의와 helper 함수/구현/본문의 실제 변경은 Confirm 전체를 거절하고 peer/checkpoint를 보존했다. 원본 복원 후 새 Confirm/실행도 통과했다.
- 기존 private out→값/값→out·struct·whole API·native 반환·retained guard·등록 helper를 수정본에서 새로 회귀 검사했다. 기존 별칭 편집기 draft/CRLF/legacy 경계는 모의 metadata를 쓰는 실제 DOM 회귀이며 이번 native import 수용 증거와 구분한다. 새 패키지 정상 실행과 전체 ZIP 구조·파일/hash/mode, 별도 추출본의 응답 유실·늦은 입력·독립 창/실행도 통과했다. 패키지 실패 주입은 원래 package/runtime을 보존했다.

제품 변경은 InformationFunctionWholeBodies 한 파일이다. 단독 Contracts/assembled compiler·version3 nativeBodyContexts·전체 원본 readGuards·Review/Confirm·최종 CAS를 재사용한다. workspace version1·receipt version3, UI/CSS·authored layout·권한·소유권·예산을 유지한다. 새 schema/receipt/profile·외부 등록/접근·C# 자동 변환·암묵적 async caller 전환은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

개발 15단계와 최종 신규46단계는 별도 증거다. 개발 실패/정정 기록 `{"baseline-private-return-import": "New fixture copied an inherited public base symbol over its traversal module. Use a private _alias module binding; product and intact baseline package unchanged."}` 및 보조 준비 진단 0건을 보존했다. 최종 과거 검사 재사용은0이다. 실제 UI 경합 클릭과 입력/checkpoint 보존은 conflict-activation-proof.json에 남겼다. 늦은 설명의 최종 확정값은 optional callback과 독립적으로 개발1·최종2 사례의 보관된 FreeInfo 원문을 JSON 문자열로 해석하여 추가 대조했고 path/hash를 late-description-audit.json에 남겼다.

이전 runtime `95b1464de743e7010234b20f98ef659e012ca42f`의 온전한 archive·모든 추출 파일/디렉터리/hash/mode를 확인했다. 새 helper-import pending은 현재 guard가 수용하고 이전 guard가 거절했다. 같은 입력 source의 hash/inode/mode/mtime는 같다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 같은 이전 CLI/providers로 새 빌드·실행20을 확인했다. 새 pending 수용 경계와 일반 source 호환성을 구분한다. 더 오래된 Reference reader 제약은 기존 증거이며 자동 migration/downgrade하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 08bfae72ba9be1bf4d1003e982a2e89ffb2b52da | a66ee148d9ecacaf57db3a5227c2dc7d288cb83d4002e099e3b6b1662192200e | 54149944 |
| rollback | 95b1464de743e7010234b20f98ef659e012ca42f | f3cd2a409ac1e96d3be115ccfa4c2a95a2663c70cb2b1b63f97ad0f763ff05f4 | 54151080 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/481f4fc53ba449f0be496461bdbae5ac.json`, evidence SHA256 `b5f6f9fdbaeb0a698a787d5282895e9267c826273b30e9d396798b6a5c808748`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a9dff93c80b84a23a7f664c2a8f988d4.json`, evidence SHA256 `f9ccf39135a2d02031aa708a46a7c4f11b4e74e6f34f116e969dfe4fa79976ed`.
두 package·두 evidence hash를 다시 확인했다. 원본 checkout·게시본·기존 증거와 미인증 IPC가 남은 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 이번 인증된 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 24141213696bytes(22.48GiB).

이 단위는 private 본문·native 반환과 안정된 소유 helper import의 한 Save/원래 읽기/CAS/실행으로 닫는다. 다른 역할/반환 구조·선택 callee/import·private 구현 import/ABI·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
