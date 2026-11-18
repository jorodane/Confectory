# Private C# 노드의 사용되지 않는 long→double 반환 공동 저장 검증

게시본 `4f8dee8ae3ea74e3fe466eccbd026bbfa2247551`과 기존 증거를 보존하고 runtime `121822df919d69012eb31184d836e47c6a7037a4`의 [유한 흐름](V666_PRIVATE_NODE_RETURNS.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9이다.

- 온전한 이전 package에서 계약 불변 private/native 후보와 원래40 실행은 유효했고 새 private 반환 후보는 거절됐다. 실제 이전 UI에서는 반환 타입이 보호됐고 원본·초안을 보존했다.
- 직접 소유한 qualified `inner/body`의 사용되지 않는 long 반환을 double로 명시했다. 구현 경계는 기존 스칼라 값 인자 1~32개이며 이번 실제 표본은 두 long 인자다. 매개변수 이름·타입·역할·수/순서·모든 인자 표현식·부모 frame/공개/native 계약·기존 caller·노드 ID/좌표·실행선·정확한64비트 local·선택 밖 원문 bytes/mtime를 보존했다. 본문/helpers는 직접 작성했다. 정·역순 후보를 대조했고 CLR의 원래40·편집 뒤20과 실제 private 본문의 long/double stderr marker를 확인했다. 편집된 본문은 소수30.5를 검사하고 double 값으로 반환한다. 반환이 사용되지 않으므로 공개 결과20은 함께 직접 편집한 다른 native 본문의 효과다.
- 반환을 exit, local 별칭 또는 다른 노드의 입력에서 사용하는 세 유효한 원본을 먼저 실제 실행하고, 새 반환 후보가 명시적인 사용처 보호 검사에서 거절되는 것을 확인했다. 원래의 같은 scope 전체에서 노드 입력·local source·exit를 검사하며 사용처·값·연결·C#·캐스트를 추측하거나 제거하지 않는다.
- 오래된 source/graph/before 서명, 반환+매개변수 타입/이름/역할/수/순서 혼합·미지원 반환·공개 계약·C# 오류·helpers 경계·마지막 native 본문 오류를 원자적으로 거절했다. receipt 또는 pending graph에 반환 사용처를 끼워 넣는 변조도 거절했다. 현재의 한 long→double 미사용 반환은 검증된 구현 경계이며 모든 반환 변경을 완료했다는 뜻이 아니다.
- 기존 C# Script에 명시적인 반환 타입 영역을 연결하고 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·미지원/혼합 입력 보존을 확인했다. 모의 metadata DOM과 실제 Linux 엔진/Chromium·CLR을 구분한다. 실제 화면의 부모 공개 계약·선택한 private double 반환·매개변수·수동 helpers와 Cancel/Code Save를 확인했다. 긴 본문은 기존 가로 스크롤 영역을 사용한다.
- 한 Save·기본/독립 창·cold·실패/재시도·응답 유실/중복 방지·늦은 입력·프로젝트/창 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 현재 node/graph receipt를 검증하고 최초 long 서명·source/graph 해시·읽기 버전을 유지했다. post-Review5경로 source 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·일반 값→ref·struct·whole API·native 반환·retained guard·등록 helper와 직전 private 인자 타입의 native/guard 회귀를 동결본에서 새로 실행했다. 모의 DOM은 앞선 인자 이름·타입 편집도 재검사했다. 새 Windows용 package의 구조/hash/mode 및 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창/실행·DOM과 package 실패 시 기존 runtime/package 보존을 확인했다. Windows 산출물 검사는 Windows 기기 실행 증거가 아니다.

제품은 InformationFunctionGraphs·Contracts·WholeBodies, feature-authoring.js와 WebBundle hash의5파일이다. 기존 단독/assembled compiler·소유권·Review/Confirm·최종 CAS가 권위다. workspace1·receipt3/nativeBodyContexts·원래 scope/권한·authored layout을 유지한다. 저장 schema/profile/receipt 필드는 추가하지 않고 현재 metadata에 사용되지 않는 반환의 편집 가능 여부만 추가했다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발16단계와 최종48단계는 별도 신규 실행이다. 개발 실패 0건·준비 진단 0건이며 동일 source 검사 재사용은 없다. 실제 UI 클릭 경합과 늦은 설명의 확정값을 개발1·최종2 보관 원문 path/hash로 대조했다. 앞선 인자 타입 단위에서 발생한 최초 복원480초 시간 초과와 과거60초 미응답·초기 빈 화면의 원인은 미확정으로 유지한다. 이번 통과를 그 원인 해결로 표현하지 않는다.

이전 runtime `0c9679de397e88f08ecb731395f26b707160960a`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. 원본 source hash/inode/mode/mtime를 유지했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행 및 double 실행 marker를 확인했다. 새 pending과 확정 source 호환성은 별개이며 더 오래된 Reference reader·일반 migration/downgrade는 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 121822df919d69012eb31184d836e47c6a7037a4 | 5464f9cdcaa0e51651b6ec296b0c889db5ec2a746e4e29a1c3752f53c37f5507 | 54159610 |
| rollback | 0c9679de397e88f08ecb731395f26b707160960a | 00d413a20282f66afbdfb1538d5870489b0eb2b1e36ed6777b0babb840d9210b | 54157206 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/034eaa0612d54a95acf5af08c6d30b19.json`, evidence SHA256 `f1245f6b7561ebed5ed144df671ebb3806f5a13a1f104fd4067ce4f945ecc2a6`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/a89057de64184734b73c2f4af304f223.json`, evidence SHA256 `f0424e8c867a6ec390b8cb29123a6d41fbadb69e41249ff3f76b69ab908881f9`.
두 package·두 evidence hash와 늦은 설명의 보관 원문을 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23879397376bytes(22.24GiB).

완료는 직접 소유 ordinary private next code의 사용되지 않는 long→double 반환과 수동 본문/helpers·다른 native 본문의 공동 저장이다. 사용되는 반환의 소비 대응·다른 반환/타입·ref/out·입출력 구조·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. main은 사용자 검토와 merge에 남긴다.
