# M11 저장된 same-contract copy의 Root 내부 흐름

## 원본 요구와 이번 단위

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`이다. 원본 `dist/app.js`의 `localImplementationDraft`는 정의를 복제하고 내부 action을 재귀 방문하여 소유 compiled 문맥만 재배치한다. `moduleFunctionDefinition`은 원래 이름·입력·출력·매개변수·반환·실행 출력을 유지한다. `dist/blueprint.js`의 `openInternal`은 선택한 동작의 내부 편집으로 진입한다. 따라서 같은 계약을 유지하는 소유 copy 안의 기존 C# 동작에도 내부 진입을 연결하는 것이 원래 흐름이다. 새 공개 함수/계약/ID 발급이나 참조 donor 수정은 요구하지 않는다.

이번 지원은 정보에 단독 직접 배정된 저장된 단일-target copy의 **Root 일반 next C# 동작**이다. 기존 private 지원 profile과 값 입력·반환을 사용하며, 선택 동작의 ref/out·whole-body 문맥·switch 및 copy의 private 진입은 이번 새 검증 범위가 아니다. 일반 직접 소유 M11에서 이미 지원한 이들 기능은 계속 유지한다. 같은 공개 override 입출력 계약을 바꾸지 않는다.

## 소유 경계와 저장

기존 `BlueprintCopyAbi`/등록 계약 receipt로 실제 정보 owner, 현재 공개 함수·모듈 계약, 직접 배정 하나, implementation/graph locator, target, 완전한 소유 객체 집합과 네 필드 copy provenance를 다시 확인한다. 요청자가 보낸 boolean은 권한 증거가 아니다. 서버가 검증한 receipt를 내부 호출 수명 동안만 전달하고 낮은 수준의 membership 편집에서도 graph/implementation/owner/path/원문 hash/provenance를 확인한다. bare Root copy에 owner를 추정하거나 다른 배정 대상을 자동 선택하지 않는다.

미리보기는 격리된 복제 상태에서만 만든다. 원래 공개 함수/복사 implementation ID·target·노드 ID·서명·외부 실행선/값 연결·원문/helpers·copy 출처를 유지한다. 기존 단일 코드 래핑과 `retainedCode`/`nodeFlowOrigin`을 사용하며 새 native 실행 의미나 파일 형식을 추가하지 않는다. 원래 코드 record 파일은 guard로 남고 새 내부 leaf는 기존 소유 경로 규칙으로 별도 준비한다. 임의 C# 소스 재작성·별칭 추정은 하지 않는다.

Save는 기존 `authorBatch`의 원자 후보와 checkpoint CAS를 사용한다. 원래 코드와 owner/출처/관측 source closure가 달라졌으면 전체 거절한다. 이미 저장된 미확정 래핑의 본문 재저장도 원래 코드 guard를 확인한다. Review→Confirm과 최종 물리 파일 CAS는 별개이며, owner와 원래 코드 guard를 포함한 완전한 그룹을 유지한다. 다른 정보/부모/외부 원본을 쓰기 대상으로 바꾸지 않는다.

기존 정보의 편집 버튼·C# 팝오버·내부 버튼·Root 빵부스러기·Undo/Redo를 사용한다. slot/project/view/implementation/private frame을 포함한 입력 키와 원래 source proof를 보존한다. 내부 미리보기에도 owner receipt를 전달하고 독립 창은 기존 server-bound view/owner/hash/선택 source binding 검증을 그대로 적용한다. 표시 capability는 권한 부여가 아니며 서버가 Save 때 다시 확인한다. 응답 유실은 정확한 receipt를 조회하고, 저장 중 늦은 입력은 다음 Save를 위해 남긴다. cold 복원에서는 process-local owner revision만 다시 관측한다. owner hash·프로젝트/창 바인딩·전체 원본/수락 receipt 검증은 그대로 유지하며 변경된 소스를 새 기준으로 추정하지 않는다.

## 유한한 경계 대조

| 조작 | 분류 |
|---|---|
| 단독 배정된 저장 copy의 Root 일반 C#를 내부 흐름으로 열고 본문을 편집·저장 | 이번 연결 대상. 원계약·원문·출처·연결을 보존한다. |
| 기존 copy 생성/배정, 기존 Root/private C# 본문·아이콘·값 편집 | 이미 지원한 기능. 이번 M11 진입과 중복 잔여로 세지 않는다. |
| owner 없는 copy·다른 정보에도 공유된 copy를 단독 변경, donor/부모/외부 원본에 쓰기 | 현재 소유 범위의 정상 보호. 자동 owner 선택이나 전원 갱신 권한을 새로 만들지 않는다. |
| 공개 override의 입력/출력 계약을 바꾸기, 독립 새 계약 copy 생성 | 정상 계약 보호/필수 범위 제외. 미구현으로 확대하지 않는다. |
| copy 생성 초안 또는 저장 copy의 private/native 문맥에서 새 M11 래핑 | 기존 M11 어댑터 잔여. 본문 편집 전체가 금지된 것이 아니며 가능한 조합마다 새 항목을 만들지 않는다. |
| 상속 implementation의 직접 소유 body/참조 전환 | 실제 소유 body와 상속 참조를 구분해야 할 기존 M11 경계. 부모를 직접 수정하거나 자동 copy로 바꾸지 않는다. |
| call/wrapper 참조의 원본 내부 구현을 자동 변경 | readonly 참조 보호와 원본 선택 흐름을 구분한다. 임의 변환을 새 필수 작업으로 만들지 않는다. |
| private graph가 없는 기존 profile·독립적으로 편집된 C#/graph 재활성화 | 기존 구현/정책 경계로 유지하며 자동 승격·본문 폐기를 추정하지 않는다. |

M4/M12, 고정 8/9행, B2 다른 사용자/그룹 권한 backend, 정보 종류 C# 표현/사용 중 삭제 대응과 3D·권한 별도 팩은 별도 고정 잔여다. 3D 이동은 표시이며 실행 조건이 아니다. 이번 단위는 전체 M11·전체 UI 완료가 아니다.

## 검증 기록

격리 fixture와 생성한 자료만 사용한다. 초기 fixture의 element 등록명, schema receipt 위치, cold 선택 복원 누락은 검사 준비 오류로 구분한다. 실제 UI 미리보기의 slot receipt 전달 누락과 독립 창 동작 허용 누락은 제품 연결을 보완했다. 응답 유실 후 cold에서 이전 owner revision을 그대로 재사용해 읽기가 거절되던 실제 복원 누락도 위 hash/receipt 보호를 유지하여 보완했다. copy의 기존 상태 문구를 일반 “저장됨” 문구로 기대한 검사 오류는 상태 문구를 바꾸지 않고 실제 checkpoint graph/leaf·입력 해제·Confirm/호출 결과 검사로 바로잡았다. 실패를 통과에 합산하지 않는다.

## 최종 결과

실행 코드 commit은 `233ecb6cdb7ad3de3cb2b04428d2f78e10b0cfac`다. 최종 소스의 새 독립 LF **18단계**, CRLF **14단계**, 새 Windows 교차 패키지·전체 압축 복원·실패 수명관리 **8단계**, 총 **40단계**가 모두 통과했다. 양쪽 checkout의 소유/상속 compiler 보호 **각 2개**도 skip·실패 없이 통과했다. 기존 직접 소유 일반/void API, 직접 소유 늦은 입력 화면, 독립 창 copy root/private 아이콘과 공통 선언·헤더·원문 편집 회귀를 해당 실행에서 새로 검사했다.

신규 copy API는 owner 누락/위조·donor 재지정·공개 계약 변경 거절, 미리보기 무쓰기, 전체 후보/CAS, 반복 시도 receipt·cold, Review 뒤 물리 원문 경합의 최종 CAS 거절과 명시 복구/Confirm, 동일 copy ID·출처·원문·helpers·공개 계약·기존 연결과 실제 호출 결과를 확인했다. 다른 정보에 공유된 copy의 단독 변경도 새로 거절 검증했다. 화면은 기존 정보 편집→내부 진입→C# 취소/편집→Undo/Redo→Root Save→Review 취소/Confirm→재진입/cold를 기본·독립 창에서 확인하며 쓰기 실패·원문 충돌·응답 유실·늦은 입력을 포함한다. 생성 패키지의 기본 copy 흐름과 전체 복원본의 독립 창 응답 유실 흐름도 새로 실행했다.

40단계는 과거 실행을 재사용해 통과로 합산하지 않았다. 집중 단계별 제품/입력 해시·수정 전 실패와 통과는 별도 증거에 남긴다. 변경하지 않은 Core의 이전 M11 중첩/ref-out/whole-body/실행 분기 전체 compiler 결과는 이력 참고이며 이번 새 소스의 재실행 수에 포함하지 않는다. 이번 copy 내부 전환의 실제 프로젝트 왕복은 새로 실행하지 않았으며, 앞선 직접 소유 흐름의 왕복 결과는 이력 참고로만 유지한다. 실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI·Library/Space 전달은 미실행이다.

- 최종 관리 record: `/workspace/artifacts/v536-verification-managed/runs/f4c27a2ebeb24813a300f8dba89cc22c.json` (40단계, cleaned).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/f4c27a2ebeb24813a300f8dba89cc22c.zip`, SHA-256 `e048205bf90bcbf1476933fca4399e3ae62903c9034b0db557110bddbdff2c89`.
- 집중 record: `/workspace/artifacts/v536-verification-managed/runs/81313effec3643288037032046857275.json`, 증거 `/workspace/artifacts/v536-verification-managed/runs/81313effec3643288037032046857275.zip`, SHA-256 `bbdedc73c43b5d4d521afd0af3a94aed126c1669db316658b5c73b0a58a4ecd4`.

| 지속 보관본 | 코드 commit | ZIP SHA-256 | bytes | 전체 manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `233ecb6cdb7ad3de3cb2b04428d2f78e10b0cfac` | `69d926992060a8ab7b8b099f1bc7155b9b3be8e249bb2f16b378dc4738027967` | 51,262,952 | `077b511da59e3a9bccd1b8e0b0debf731e2de6543475535ae93f4aa770e50c49` |
| 정상 롤백 | `dae566a1fecc0fcdb0fa80120603b13c3dfdf120` | `2c44b766588b73fc6fa2aff84e52e0cf8ea59e77d4be42656a5f2885bd8ea58a` | 51,261,730 | `2b3cd6aa50d404db196aa432ddccd5325ccc2faf2cf1ff9a2520273ce5cd72a9` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 최종 코드에서 새로 생성하고 전체 SHA/CRC/파일·디렉터리 모드를 복원한 뒤 복원본을 실행했다. 롤백은 이전 정상 검증 증거를 재사용하고 ZIP SHA를 재확인했다. 최신 2363파일·147디렉터리 / 롤백 2363파일·147디렉터리. 이후 보고서 commit과 위 실행 코드 commit의 차이는 문서뿐이며 보고서 commit에서 다시 패키징했다고 주장하지 않는다.

집중 검증 여유 2064.60→2061.31 MiB, 최종 검증 여유 2060.99→2056.68 MiB였다. 최종 실행 순증가 **4.31 MiB**, 단계 샘플 최소 2060.93 MiB, cgroup 메모리 피크 4735.34 MiB였다. 기존 추가 디스크 예산 144 MiB(64 MiB 안전 여유 포함)과 RAM/메모리 예산을 유지했다. 집중/최종 소유 임시 root는 증거를 검증·보관한 뒤 정리했고 승인된 최신/롤백 회전 외 과거 자료를 삭제하지 않았다. 이번 순증가는 향후 보장값이 아니다.

이번에 검증한 copy는 프로젝트 소유 함수를 구현하는 정보의 단독 배정 copy다. 등록 함수·다른 native 계약/target·상속/참조·private/생성 중 copy의 M11 전환 전체 검증을 뜻하지 않으며 위 유한한 경계표로 유지한다. 정상 보호와 실제 미구현·미검증을 구분하고 새로운 C# 조합을 필수 잔여로 추가하지 않는다.
