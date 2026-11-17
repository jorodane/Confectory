# Scalar 반환 UI의 원래 별칭 보존 검증

게시본 `6e3ad3d90cfe958848e3af2fc306591c5a9ecbeb`와 기존 증거를 보존하고 runtime `95b1464de743e7010234b20f98ef659e012ca42f`의 [유한 UI 흐름](V666_PRIVATE_RETURN_ALIAS.md)을 **최종 신규46·재사용0·실패0**으로 검증했다. LF24·CRLF13·새 패키지/전체 ZIP 복원9이다. Linux 실제 .NET/native 엔진과 Chromium 자동화를 사용했다. 별도 렌더러 검사는 모의 metadata 검사이며 물리 기기 검증과 구분한다.

- 온전한 이전 패키지 UI에서 공개 `amount/count`와 원래 native `nativeAmount/nativeCount`가 다른 함수의 long→double 반환 변경을 재현했다. 읽기 전용 헤더만 공개 이름으로 바뀌고 본문은 원래 별칭을 유지했다. 실제 trusted Save 한 번의 실패 응답, 입력·checkpoint·모든 원본 보존을 기록했다. 같은 이전 backend에 원래 별칭의 명시 계획을 제출하면 단독/공동 후보가 이미 유효했다. 이번 제품 변경은 UI에 한정한다.
- 수정 UI의 읽기 전용 헤더·선택 서명은 원래 native 인자명·타입·역할·수·순서를 유지했다. 사용자가 직접 작성한 C# 본문과 명시한 기존 반환→호환 out 대응을 private 본문/helpers 편집과 한 Save에 결합했다. 원래 caller40, 변경 뒤 caller20·실제 IInvoke double 반환25.5·기존 long out25를 확인했다. private ABI·정확한64비트 local·graph 연결/좌표·독립 원문 bytes/mtime를 유지했다.
- 실제 UI의 취소·Undo/Redo·cold 복원·쓰기 실패/재시도·Save/조회 응답 유실·중복 방지·늦은 입력/후속 Save·창/프로젝트 경계·Review 취소/Confirm을 검사했다. API의 cold와 후속 설명·함수·본문 Save도 최초 source/flow/반환/caller 관측을 유지했다. Review 뒤 private graph/node·독립 원문·caller graph·함수 원본 경합은 Confirm 전체를 거절했다. 복원 뒤 새 Review/Confirm으로20을 실행했다.
- 모의 metadata를 사용한 실제 DOM 편집기 검사는 읽기 전용 인자 문맥을 기존 `parameters` 필드로 보관하고 새 렌더러에서 복원했다. 기존 명시 별칭과 표식 없는 이전 초안의 공개 헤더 해석을 유지했고, 원문 hash 변경 시 초안을 보존했다. 본문을 바꾸지 않은 Code Save의 원래 CRLF 문자열도 확인했다. 이 검사를 실제 native 파일의 header-only 저장 또는 물리 기기 검사로 표현하지 않는다.
- 누락/잘못된 소비자 대응·input/out 변경·native 별칭/역할·private 반환·두 번째 계약·void·잘못된 C#·변조된 원본/flow/group/읽기 증거를 거절했다. 실제 물리 원본 충돌은 Review/최종 CAS로 확인했다. 기존 private out→값/값→out·struct·whole API·일반 native 반환·retained guard·등록 helper 회귀를 수정본에서 새로 실행했다.
- 새 패키지의 정상 native UI 저장/실행, 전체 ZIP 구조·파일/hash/mode와 별도 전체 추출본의 응답 유실·늦은 입력·독립 창/실행·렌더러 회귀를 확인했다. package 실패 주입도 기존 package/runtime을 보존했다.

제품 변경은 feature-authoring.js와 그 한 WebBundle 항목의 정규화 크기/hash다. backend·CSS·authored layout·workspace version1·receipt version3·nativeBodyContexts·원본 관측·권한·Review/Confirm·최종 CAS는 바꾸지 않았다. 새 schema/receipt/profile·자동 이름/본문 변환·migration·async caller 변환은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류 정책을 유지한다.

개발 16단계와 최종 신규46단계는 별도 증거다. 개발 실패/정정 기록 `{"dev-private-return-alias-renderer": "Fixture expected LF replacement, but the existing raw-section editor preserves the unchanged trailing CRLF. Product unchanged; assert preserved raw CRLF and persist actual draft evidence.", "dev-private-return-alias-renderer-corrected": "Renderer fixture compared Playwright object evaluation with pre-wire undefined mode properties to a JSON contract lacking those keys. Assert the actual JSON serialization used by transport; preserve evaluated and serialized evidence. Product unchanged."}`, 보조 준비 진단 0건이다. 최종 과거 검사 재사용은0이다. 경합 검사의 실제 trusted 클릭·편집 기준 거절·입력/checkpoint 보존은 conflict-activation-proof.json에 남겼다.

이전 runtime `5ded57368d850faad802f27bac06521f75b3ec86`의 온전한 archive와 모든 추출 파일/디렉터리/hash/mode를 다시 확인했다. 원래 별칭으로 작성한 pending은 이전 guard와 현재 guard에서 모두 수용했다. 전후 source hash/inode/mode/mtime가 같다. Confirm된 source만 별도 복사해 pending/output cache 없이 같은 이전 CLI/providers로 새 빌드·실행20도 확인했다. 이전 UI 결함과 backend 호환성은 구분한다. 더 오래된 Reference reader 제약은 기존 증거이며 이번에 일반 호환성이나 migration을 검증한 것이 아니다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 95b1464de743e7010234b20f98ef659e012ca42f | f3cd2a409ac1e96d3be115ccfa4c2a95a2663c70cb2b1b63f97ad0f763ff05f4 | 54151080 |
| rollback | 5ded57368d850faad802f27bac06521f75b3ec86 | 9e8901d90b115b734957a4f9080c7bf577f4a4a21ca36372ff14c36d149bf935 | 54150843 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/a2d3fc81a38f403aa81bb4176bdd4cd1.json`, evidence SHA256 `a18849183e1e554d4e2c200db98168671f698da38987108d53ce5bed3d89a1ee`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a2621affa62641f09d1cefa62d4bcc1e.json`, evidence SHA256 `d0a716ceaaf4f89328da3aaf01dc220de2afe1f759150786df3f0ac49c5d4322`.
두 package·두 evidence hash를 재확인했다. 원본 checkout·게시본·기존 증거와 미인증 IPC가 남은 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 24159051776bytes(22.50GiB).

이 단위는 원래 별칭의 scalar 반환 UI·명시 계획/초안 보존·private 공동 Save/복원/실행으로 닫는다. 다른 역할/반환 구조·private ABI·opaque/import 결합, 구 reader 전체 교환은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
