# Private 본문·scalar 반환 공동 저장 검증

게시본 `6c8f578`과 기존 증거를 보존하고 runtime `5ded57368d850faad802f27bac06521f75b3ec86`의 [유한 흐름](V666_PRIVATE_SCALAR_RETURN.md)을 **최종 신규44·재사용0·실패0**으로 검증했다. LF23·CRLF13·새 패키지/전체 ZIP 복원8을 모두 새로 실행했다. Linux 실제 .NET 실행·Chromium 자동화이며 실제 Windows/WebView2·물리 기기·전체 UI 검사와 구분한다.

- 직전 온전한 패키지에서 private C#/helpers와 다른 소유 함수의 scalar 반환 계획은 각각 유효하고 실제 이전 반환 소비자로 원래40을 실행하지만, 공동 제출만 원본 쓰기 없이 거절되던 경로를 재현했다.
- private 공개/프레임/code ABI는 유지했다. 다른 native 함수의 long→double 반환, 직접 작성한 C# 본문과 실제 기존 long 반환 소비자의 호환되는 기존 long out 선택을 한 후보에 결합했다. 기존 입력·out identity와 native 인자명/타입/역할/수/순서를 유지했고 편집 정·역순 후보가 같다. 실제 caller20·IInvoke double 반환25.5·기존 long out25를 확인했다. 정확한64비트 local·graph 연결/좌표·독립 원문의 bytes/mtime도 보존했다.
- 기존 상세창 반환 선택·출력 대응·C# 본문/helpers 편집기의 취소·Undo/Redo·cold·쓰기 실패/재시도·Save/조회 응답 유실·중복 방지·늦은 설명/후속 Save·창/프로젝트 경계·Review 취소/Confirm을 검사했다. UI/CSS·리소스·권한은 변경하지 않았다. 이 UI 사례는 native 원래 인자명이 공개 인자명과 이미 같다. 다른 native 별칭의 반환 UI 정책/결합은 미검증 잔여이며 암묵적인 이름 변경을 허용한 것이 아니다.
- 누락/잘못된 이전 반환 대응·out identity 변경·기존 입력 교체/해제·native 별칭/역할·private 반환·두 번째 계약·void·잘못된 C#은 원본 쓰기 없이 거절했다. 캡처 반환·source/flow/locator/group/읽기 경로·caller와 source proof 동시 변조도 거절했다. 실제 물리 읽기 해시는 Review/최종 CAS의 책임으로 구분했다.
- cold와 후속 설명·함수 메타데이터·현재 native 반환 서명으로 명시한 본문 Save는 최초 function/source/flow/반환/caller 증거와 읽기 버전을 유지했다. 이미 적용한 caller 대응은 재제출하지 않았다. Review 뒤 private graph/node·독립 원문·caller graph·함수 원본 경합은 Confirm 전체를 거절하고 peer와 checkpoint를 보존했다. 복원 뒤 새 Review/Confirm으로20을 실행했다.
- 기존 private out→값 native/guard·값→out·struct 입력·whole API·일반 native 반환·retained guard·등록 helper 회귀를 수정본에서 새로 실행했다. 새 패키지 정상 저장/실행과 전체 ZIP 구조/파일/hash/mode, 별도 추출본의 응답 유실·늦은 입력·독립 창/실행도 검사했다. package 실패 주입에서도 원래 package/runtime을 보존했다.

제품 변경은 InformationFunctionWholeBodies 한 파일이다. 기존 단독 검증기·assembled compiler·nativeBodyContexts·전체 원본 읽기·Review/Confirm·최종 CAS를 재사용한다. workspace version1·receipt version3를 유지하고 새 schema/receipt/profile·권한·형변환/본문/소비자 생성·async 변환은 없다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류 정책을 유지한다.

개발 12단계도 모두 통과했으며 최종 신규44단계와 별도 증거로 보존했다. 최종 검증에서 과거 검사를 재사용하지 않았다. 경합 검사에는 기존 trusted 클릭 관측을 사용하며 실제 클릭과 요청이 모두 없을 때만 한 번 다시 활성화한다. 실제 trusted 클릭·편집 기준 거절·입력과 checkpoint 보존을 확인했고 이벤트 원문은 보관 ZIP의 conflict-activation-proof.json에 남겼다.

직전 `bff259ad4806771c68c91f9610f38dc64a25ef78` package의 archive와 모든 추출 파일/디렉터리/hash/mode를 확인했다. 같은 온전한 추출본의 구 pending guard는 새 결합을 거절하고 현재 guard는 수용했다. 전후 원본 source hash/inode/mode/mtime가 같다. Confirm된 source만 별도 복사해 pending/output cache 없이 같은 구 CLI/providers로 새 빌드·실행20을 확인했다. 새 pending 검증기 경계와 일반 기존 source 실행은 구분한다. 더 오래된 Reference parser 제약은 이전 증거이며 이번 새 측정에 포함하지 않는다. 자동 migration/downgrade는 없다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 5ded57368d850faad802f27bac06521f75b3ec86 | 9e8901d90b115b734957a4f9080c7bf577f4a4a21ca36372ff14c36d149bf935 | 54150843 |
| rollback | bff259ad4806771c68c91f9610f38dc64a25ef78 | d6c529fd990a866fe30e8a45c5b8671cfbb497139fdcb6f195d45e766ffacf99 | 54151729 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/403af22ea29348c0afeba33c44443860.json` · evidence SHA256 `82e02a466457d5f9bd0e32d84670dd09d1a439caaca840c7e414a4cb4949735e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/68d20824d166458da05bc5acf6f6e935.json` · evidence SHA256 `23633c394acba1127a7bea0c9f922f9911548052401497f9ef6d417faea0f211`.
두 package·두 evidence hash를 재확인했다. 원본·게시본·보관 증거와 미인증 IPC가 남은 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 이번 인증된 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 24176840704bytes(22.52GiB).

이번 단위는 private ABI·native 입력/out 유지·명시 scalar 반환과 이전 소비자의 호환 out 대응·한 Save/복원/실행으로 닫는다. 다른 역할/반환 구조·private ABI·별칭 UI·opaque import·구 reader 전체 UI 교환은 잔여이며 조합별 필수 매트릭스를 추가하지 않는다. 실제 Windows/WebView2·기기·IME/GPU/audio·전체 UI는 미검증이고 과거 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.
