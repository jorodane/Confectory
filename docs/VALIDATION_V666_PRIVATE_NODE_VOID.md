# Private C# 노드의 미사용 long→void 전환 공동 저장 검증

게시본 `5a7e03efa3e3eda5f9778989b5267b15fef3d0f9`와 기존 증거를 보존하고 runtime `8af6f656d2d33bf4c37c4c6fe756c37647bc9530`의 [유한 흐름](V666_PRIVATE_NODE_VOID.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9이다.

- 온전한 이전 package에서 원래40 실행과 계약 불변 후보는 유효했고 새 void 반환 후보는 거절됐다. 실제 이전 UI는 void 입력을 보존한 채 Code Save를 거절했다.
- 직접 소유한 qualified `inner/body`의 사용되지 않는 long 반환을 void로 명시했다. 기존 스칼라 값 인자 1~32개가 구현 경계이며 실제 표본은 두 long 인자다. 인자 이름·타입·역할·수/순서·모든 입력 표현식·부모 frame/공개/native 계약·caller·노드 ID/좌표·실행선·정확한64비트 local·선택 밖 bytes/mtime를 보존했다. 본문/helpers는 직접 작성했다. 정·역순 후보를 대조했고 원래40·편집 뒤20을 CLR에서 실행했다. void 본문의 실행 marker와 명시적인 return;을 확인했다. 공개 결과20은 함께 직접 편집한 다른 native 본문의 효과다.
- 이전 값 반환 C# 본문과 helpers를 그대로 둔 void 후보는 실제 compiler의 CS0127로 거절됐다. 반환식·본문을 삭제하거나 void용 문장을 생성하지 않았다. 반환을 exit/local 별칭/다른 노드 입력에서 사용하는 세 유효한 원본도 먼저 실행하고 새 후보의 명시적인 사용처 보호 거절을 확인했다. 원래 사용처는 제거하거나 자동 재연결하지 않는다.
- 오래된 source/graph/before 서명, 반환+인자 이름/타입/ref 역할/수/순서 혼합·미지원 반환·공개 계약·C# 오류·helpers 경계·마지막 native 본문 오류를 원자적으로 거절했다. pending graph/receipt에 반환 사용처를 끼워 넣는 변조도 거절했다.
- 기존 반환 타입·매개변수·본문/helpers 영역을 사용해 취소·Undo/Redo·첫 owner Save 전 재진입·fresh DOM 초안 복원·미지원/혼합 입력 보존을 검사했다. 모의 metadata DOM과 실제 Linux engine/Chromium·CLR을 구분한다. 실제 화면의 부모 계약·void 반환·원래 long 인자·수동 helpers·Cancel/Code Save를 확인했다. 긴 본문은 기존 가로 스크롤 영역을 사용한다.
- 한 Save·기본/독립 창·cold·쓰기 실패/재시도·응답 유실/중복 방지·늦은 입력·프로젝트/창 경계·후속 설명/본문 Save·Review 취소/Confirm을 검사했다. 현재 node/graph receipt를 확인하고 최초 long 서명/source/graph 해시·읽기 버전을 유지했다. post-Review5경로 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 보존했다. 원본 복원 뒤 새 Review/Confirm과20 실행이 통과했다.
- 기존 private out→값·일반 값→ref·struct·whole API·native 반환·retained guard·등록 helper와 직전 private long→double 후보/guard 회귀를 새로 실행했다. 기존 double DOM의 부정 사례였던 void는 이번에 명시적으로 지원하므로 미지원 int로 바꾸고 double 선택·초안·보호 검사를 유지했다. 앞선 인자 타입·이름 DOM도 재검사했다. 이 회귀를 기존 전체 UI 재검증으로 합산하지 않는다.
- 새 Windows용 package의 구조/hash/mode와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창/실행·DOM을 확인했다. package 실패 주입에서 기존 runtime/package도 보존됐다. Windows 산출물 검사는 Windows 기기 실행 증거가 아니다.

제품 변경은 InformationFunctionGraphs·feature-authoring.js·WebBundle hash의3파일이다. 이전 WholeBodies·Contracts와 compiler·소유권·Review/Confirm·최종 CAS 파이프라인은 원문을 유지한다. 기존 metadata 편집 가능 여부와 workspace1·receipt3/nativeBodyContexts를 재사용하고 새 schema/profile/receipt/metadata 필드·권한을 추가하지 않는다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류도 유지한다.

개발14단계와 최종48단계는 별도 신규 실행이다. 개발 실패 0건·준비 진단 0건이며 같은 source 검사 재사용은 없다. trusted UI 클릭 경합과 늦은 설명의 확정값은 개발1·최종2 보관 원문 path/hash로 대조했다. 앞선 최초 복원480초 시간 초과·과거60초 미응답·초기 빈 화면 원인은 미확정이다. 이번 통과를 그 원인 해결로 표현하지 않는다.

이전 runtime `121822df919d69012eb31184d836e47c6a7037a4`의 온전한 archive와 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. 원본 source hash/inode/mode/mtime를 유지했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행 및 void marker를 확인했다. pending과 확정 source의 호환성은 별개이며 일반 migration/downgrade나 더 오래된 Reference reader 지원은 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 8af6f656d2d33bf4c37c4c6fe756c37647bc9530 | fac13f9cee334a0c67a7c1160b4fd4806b5d2953a8cce70c8dfc07b99e3fd1ac | 54159397 |
| rollback | 121822df919d69012eb31184d836e47c6a7037a4 | 5464f9cdcaa0e51651b6ec296b0c889db5ec2a746e4e29a1c3752f53c37f5507 | 54159610 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/ab4fa1c4428c4ac0a686906471bafcb9.json`, evidence SHA256 `4a2af73e9dab69dd6b94cfe99e2ace215624392df5ce174dea32c0e2d8680b7e`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/3c71a6d21a3c4377a9142f1f49f7fbaa.json`, evidence SHA256 `597194ca7b76f540710ad39c8cc797ae5f655cd8201e79ca968feb015fd97a6c`.
두 package·두 evidence hash와 확정 설명 원문을 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 보존했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23860195328bytes(22.22GiB).

완료는 직접 소유 private next code의 미사용 long→void 전환·수동 본문/helpers·다른 native 본문의 공동 저장이다. 다른 타입·ref/out·반환/입출력 구조·사용되는 반환 소비 대응·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이다. main은 사용자 검토와 merge에 남긴다.
