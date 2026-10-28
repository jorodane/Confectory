# copy wrapper 갱신과 다른 frame 본문의 결합 저장

기준은 게시 `d45f342`와 저장소 `196c605`의 v536 ZIP이다. 원본 `[data-wrapper-refresh]` handler는 선택한 호출의 최신 계약을 가져와 `remember()`하고, 내부 화면의 빵부스러기는 자식 definition/graph를 부모 graphDraft로 보관한다. Root `saveDefinition`은 그 전체 graph를 저장한다. 이 근거로 **내부 호출 원본 계약 갱신·명시 대응 → Root 일반 카드 설명/수동 C# 편집 → 기존 Save → Review/Confirm** 한 흐름을 연결했다. 원본이 조용히 link를 정리하는 동작은 가져오지 않고, 기존 명시 매핑과 부적합 전체 거절을 유지한다. 원본 ZIP/Git blob/JS SHA·실제 handler 위치는 evidence를 따른다.

## 실제 누락과 최소 연결

기존 UI의 다른 frame 입력 guard와 wrapper 단독 저장 제한, 서버의 ABI 단일 edit 및 private-only frame 제한, 독립 창 전달의 단일 ABI 분류 때문에 위 입력은 보관돼도 요청 전에 거절됐다. 기존 코드의 실제 UI에서 설명/본문과 wrapper를 보관한 뒤 요청 전 거절·원본/입력 보존을 재현했다.

기존 저장 single-target same-contract copy의 동일 author surface·정보 owner·소유 구현 입력만 수집한다. 한 wrapper ABI 계획과 ordinary next 코드 카드의 `source`/`intent`에 정확한 Root/private frame을 명시한다. 새 copy 생성·독립 계약 복제·모든 target 자동 선택은 추가하지 않았다. 일반 pin/node/route 및 다른 복합 계획까지 이 어댑터가 묵시적으로 허용하지 않는다.

모든 frame을 원래 전체 source closure·소유·출처·checkpoint와 대조한 뒤, 기존 wrapper/import/use 대응을 먼저 한 격리 후보에 적용한다. 이어 사용자가 직접 편집한 ordinary 설명/본문만 그 frame의 새 basis로 적용하고 전체 graph를 검사한다. 후속 frame의 설명 예산 오류처럼 후속 단계가 거절돼도 앞선 import/wrapper는 live나 checkpoint에 남지 않는다. 기존 `WriteChecked` 최종 CAS 한 번으로 전체 저장한다. 수동 C#은 그대로 저장·컴파일 검토하며 임의 재작성이나 값 변환을 추측하지 않는다.

receipt 확인도 ABI가 실제 존재하는 frame에서 계약·source/등록 receipt·copy binding을 확인한다. 교정 재시도는 미적용·원래 checkpoint/전체 source 불변에 더해 원래 ABI signature/source/receipt/use binding을 확인해야 한다. 실패 기록을 무조건 지우거나 실제 변경을 cold 버전 차이로 재적용하지 않는다. 같은 창의 새 입력과 다른 창/owner/프로젝트 입력은 채택하지 않는다.

원래 버튼·빵부스러기·카드·편집기·레이아웃은 변경하지 않았다. C# 편집기의 취소·Undo/Redo와 wrapper의 frame별 Undo를 유지한다. wrapper Undo는 Root의 다른 입력을 지우지 않으며 재시작에도 보관한다. Save는 초안 저장이고 물리 파일 반영은 명시 Review/Confirm이다. 공개 override의 원래 입출력 계약은 유지하고 구현만 편집한다.

## 실제 검사

격리 fixture의 기본 창 private Save 및 독립 창 Root 복귀 Save를 실제 엔진/렌더러로 검사했다. 입력 원문·정확한64비트 local·순서·실행선·두 호출별 명시 대응·공개/부모 계약·copy ID/출처·donor/callee/다른 객체를 보존한다. 실제 저장 요청의 한 ABI와 명시 frame, 후속 frame edit 오류의 전체 미적용, 실제 파일 쓰기 실패/cold 재시도, 성공 응답 유실/receipt/cold, 실제 peer checkpoint 경합, wrapper Undo/다른 입력 보존, 잘못된 매핑 거절→Undo→올바른 명시 선택의 재시도를 검사했다. 정상 경로는 컴파일 Review 취소·재검토·Confirm 및 최종 파일/graph 전체 대조를 완주했다.

| 흐름 | 확인 수 |
|---|---:|
| 기본 창 정상 저장/확정 | 13 |
| 독립 창 Root 저장/확정 | 15 |
| 쓰기 실패/재시작/재시도 | 6 |
| 응답 유실/조회/재시작 | 6 |
| 실제 peer 경합 | 6 |
| wrapper Undo/다른 입력 보존 | 6 |
| 거절/Undo/새 명시 매핑/재시도 | 14 |

집중 66확인과 최소 영향 회귀 22확인이 통과했다. 기존 Root ordinary frame 저장, 등록 callee saved-copy ABI의 소유·nonce·외부 원본 보호, 실제 Review/Confirm/CommitPlan final CAS의 성공·late race·proof 누락·경로 이탈을 회귀로 유지했다. 74 WebBundle 리소스의 바이트·해시도 일치한다. 명령/종료코드·자원·source SHA와 실패 분류는 `evidence/v536-copy-wrapper-frame-save/focused-verification.json`에 기록했다. 로그·화면·프로필·fixture는 scratch 증거로 보관하며 Git에는 넣지 않는다.

## 원래 요구·안전 경계·제안의 구별

| 사용자 조작/조건 | 현재 근거와 판정 | 후속 경계 |
|---|---|---|
| 기존 wrapper 원본 계약 갱신과 다른 ordinary 카드의 설명/수동 본문을 함께 Save | 원래 remember·내부 graph 보관·전체 graph Save. 이번 기본/독립·Root/private 지원 경로 완료 | 한 wrapper/callee 명시 계획과 source/intent. pin/route 등 다른 계획 혼합은 이 검증 범위로 완료라 하지 않는다 |
| 기존 private 내부 계약 갱신으로 부모 계약/본문·forwarded 저장소도 실제 영향받음 | 일반 소유 문맥의 기존 명시 ABI 기반은 있으나 copy의 해당 영향 source closure 결합은 별도다 | 실제 영향을 주는 원래 내부 편집에서만 같은7행/A4–A6로 관리한다. 일반 wrapper 갱신에 항상 새 부모 기능이 필요하다고 추가하지 않는다. 공개 override 구조 변경이라면 정상 금지 |
| 같은 callee를 실제로 사용하는 opaque/whole-body C#·import와 wrapper 갱신 | 수동 본문·typed import·컴파일 검사 기반은 있다. `BlueprintCallAbiUses`/`BlueprintCallAbi`는 미대응 implementationContext/import/forwardCallerStorage를 거절해 입력을 지킨다 | 사용자가 수정한 본문/계약을 copy closure에 명시 결합하는 기존 잔여. 엔진 전체 부재로 분류하거나 C# 문자열 추측 재작성으로 우회하지 않는다. 실제 관련 사용처가 없는 이름상의 opaque 조합을 새 의무로 늘리지 않는다 |
| 원계약을 바꾸는 override·새 독립 계약 ID 복제·모든 target 자동 선택 | 원계약 보존은 사용자 확정 정상 보호. 독립 계약 복제/자동 선택은 필수 제외 | 정상 금지를 미구현으로 세지 않는다. 별도 새 기능·UI를 추가하지 않음 |

위 copy 영향 후보는 기존7행/A4–A6의 같은 항목으로 한 번만 관리한다. ref/out/타입/핀 수/순서의 모든 조합으로 새 수용 목록을 늘리지 않는다. 8행의 여러 함수 C#/중첩/copy 동시 문맥, 9행 고급 핀 타입·표시명/생성 식별자, I6 기호/이모지/로컬 이미지 아이콘·B2 실제 배지·M4 async/M11 C#→graph/M12 Root 분기는 별도 잔여다. 신규 이미지/협의/렌더 backend는 이 복원 묶음 밖이다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다.

## 독립 checkout·새 교차 패키지 확정 결과

실행 소스 커밋 `4fd13dd9f3c76ec449d22d746bc52f504a361e1b`의 변경 Git blob·기존 autocrlf·clean을 확인했다. 기존 독립 checkout에서 Native/CLI Release·새 Linux 엔진, wrapper 갱신·Root 일반 카드 결합의 독립 정보 창 15확인 및 생산 final CAS 4확인이 통과했다. 새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·패키지 자체 두 frame UI 15확인까지 6단계를 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL과 변경 제품 소스 바이트를 확인했다.

manifest SHA `6fd18cd9c7115b47b1cd470054040b21855da605ad9835f005b57007b44e373a`. 전체 manifest와 fixture/로그/프로필 증거 보관 뒤 이번 실행의 임시 패키지만 정리했고 기존 보관 패키지/SDK/원본/사용자 자료는 삭제하지 않았다. 최종 후속 커밋은 문서/evidence만 달라 실행 코드는 위 소스 커밋과 같다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달 및 전체 UI는 계속 미완료다.
