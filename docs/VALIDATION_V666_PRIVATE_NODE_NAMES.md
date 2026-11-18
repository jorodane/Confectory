# Private C# 노드 인자 이름의 공동 저장 검증

게시본 `b2d77306a929239b024e7b23d4e728c32f9ede01`과 기존 증거를 보존하고 runtime `80a6c90bb0f1ae9f9d4b23b7614ba38799a0ceaa`의 [유한 흐름](V666_PRIVATE_NODE_NAMES.md)을 최종 신규48·재사용0·실패0으로 검증했다. LF26·CRLF13·새 package/전체 ZIP 복원9이다.

- 온전한 이전 package에서 계약 불변 private/native 후보와 원래40 실행은 유효했고, private 노드 자체의 이름 변경은 거절됐다. 실제 이전 Linux 엔진 UI에서는 private 매개변수 헤더가 보호되어 직접 이름을 선택할 수 없었다. 아래 개발 fixture/빌드 수정 기록과 구분하며 시간 제한이나 제품 가드를 완화하지 않았다.
- 직접 소유한 qualified `inner/body`의 `firstNative`를 `deltaNative`로 명시하고 새 본문·helpers를 직접 작성했다. 원래 위치의 입력 표현식을 새 키에 보관하며 node 서명·인자 키·definitionHash를 새 계획에 대응시켰다. 부모 private frame·공개/native ABI·타입/값 역할/인자 수/순서/반환·호출자·노드 ID/좌표·정확한64비트 local·선택 밖 bytes/mtime를 유지했다. 정·역순 같은 후보, 원래40과 편집 뒤20을 CLR에서 실행했다. 결과 변화는 명시 본문 편집의 효과다.
- 오래된 source/graph/before 서명, 타입·역할·반환·인자 수·순열·중복/두 번째 이름·공개 계약 변경, 새 이름과 맞지 않는 원래 본문·helpers 경계·마지막 native C# 오류를 원자적으로 거절했다. 새 C#·바인딩 값·저장소·캐스트를 추론하지 않았다.
- 기존 C# Script의 매개변수·본문·helpers 영역, 취소·Undo/Redo·첫 owner Save 전 재진입과 fresh DOM 초안 복원을 검사했다. 실제 화면에서 별도 부모 공개 서명과 새 private 이름·본문·helpers 및 Cancel/Code Save가 보이는지 확인했다. 모의 metadata DOM 검사와 실제 Linux 엔진/Chromium·CLR 검사는 구분한다.
- 실제 한 Save·기본/독립 창·cold·실패/재시도·응답 유실과 중복 방지·늦은 입력·프로젝트/창 경계·후속 설명 및 명시 본문 Save·Review 취소/Confirm을 검사했다. 후속 본문 Save는 현재 node/graph 증거를 요구하면서 최초 서명/source/graph 해시·읽기 버전을 보존했다. 실제 post-Review5경로 경합은 전체 Confirm을 차단하고 peer/checkpoint/input을 유지했다. 원본 복원 뒤 새 Confirm과20 실행이 통과했다. receipt의 frame/source/plan/읽기 및 group 변조도 검사했다.
- 기존 private out→값 guard·struct·whole API·native 반환·retained guard·등록 helper·직전 callee 값→ref를 동결 수정본에서 새로 실행했다. 새 Windows용 package의 구조/hash/mode와 Linux 실행, 전체 ZIP 별도 복원본의 응답 유실·늦은 입력·독립 창/실행·DOM 검사 및 package 실패 시 기존 runtime/package 보존을 확인했다. Windows 산출물 검사는 Windows 기기 실행 증거가 아니다.

제품 변경은 InformationFunctionGraphs·Contracts·WholeBodies, feature-authoring.js와 WebBundle hash의5파일이다. 기존 단독/assembled compiler와 소유권·Review/Confirm·최종 CAS가 권위다. workspace1·receipt3/nativeBodyContexts·원본 scope/권한·authored layout을 유지하며, 저장 schema/profile/receipt 필드는 추가하지 않았다. 현재 metadata의 편집 가능 표시만 추가한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류는 유지한다.

개발17단계(통과14·실패3)와 독립 준비 진단1건은 최종48과 별도다. 개발 실패와 정정은 다음과 같다.

- 첫 fixture가 공개 변수 `base`를 복사하면서 가져온 모듈 참조를 덮어썼다. 제품 실행 전의 검사 코드 오류였으며 `_base` 참조로 고친 뒤 원래 package의 순수 검사가 통과했다.
- UI fixture가 비동기 구현 선택창이 열리기 전에 코드 편집기를 확인했다. 실제 DOM에 원래 선택창이 있음을 확인하고 그 창을 기다리도록 고친 뒤 이전 UI 검사가 통과했다.
- 새 `Text` 인자를 기존 retained 문맥의 bool 인자 앞에 넣어 Release 빌드가 거절됐다. 기존 bool 인자 위치를 유지하고 새 선택 인자를 뒤에 추가해 수정했다. 이후 Release와 retained 회귀가 통과했다.

준비 스크립트의 문자열 치환 assertion도 제품이나 파일을 쓰기 전에 거절됐으며, 정정 기록을 보존했다. 최종48은 모두 새 실행이고 개발 성공을 최종 결과로 재사용하지 않았다. 실제 경합의 trusted activation과 늦은 설명 확정값은 개발1·최종2의 보관 원문 path/hash로 대조했다. 대기 호출 중단 뒤에도 같은 검증 프로세스 식별자와 깨끗한 작업 트리를 확인했으며 재실행하거나 환경을 초기화하지 않았다.

이전 runtime `59ea11363d2f992f1c6d91544407b359e117a915`의 온전한 archive와 모든 추출 file/directory/hash/mode를 확인했다. 새 pending은 현재 guard가 수용하고 이전 guard는 거절했다. 원본 source hash/inode/mode/mtime를 유지했다. Confirm된 일반 source만 별도 복사해 pending/output cache 없이 이전 CLI/providers로 새 build·20 실행을 확인했다. 새 pending의 수용 경계와 확정 source 호환성은 별개이며, 더 오래된 Reference reader·일반 migration/downgrade 호환성을 주장하지 않는다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 80a6c90bb0f1ae9f9d4b23b7614ba38799a0ceaa | fb51cc185af8e3a5a4456a175bb8c7121000ea4af4f9754bdd78df0791c8716d | 54156129 |
| rollback | 59ea11363d2f992f1c6d91544407b359e117a915 | c4aecb30c827be9745bc8b8237a8f2a2deed6c75f344e81016f8c0196b4ff4c5 | 54157992 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/3bf32c3b496a44da905a2f0f44076912.json`, evidence SHA256 `a99d6a6d0f0426f6054345d30bf517b22aa1b943eb9846224bb9d9f0a47aafe3`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/1db1f12e7c734934ae6c3ae5c64621c7.json`, evidence SHA256 `6e0e9fccac5f9a10c56f61b99977007e346f0c8d18fd6c853e86e356f8b61759`.
두 package·두 evidence 해시와 늦은 설명의 보관 원문을 대조했다. 원본 checkout·기존 증거·미인증 IPC 보관본 `/tmp/cv-5xgaibtx`를 유지했다. 정리는 인증된 이번 임시물과 기존 latest/rollback 교대 범위다. 디스크 여유 23922946048bytes(22.28GiB).

완료 범위는 private code 자체의 값 인자 이름 하나다. private 타입·ref/out 역할·반환·입출력 구조·부모 frame ABI와 추가 retained/opaque/copy/import·외부 관측 결합은 잔여다. 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 초기 빈 화면 및 과거60초 미응답의 원인은 미확정이다. main은 사용자 검토와 merge에 남긴다.
