# 새 copy의 첫 Save와 내부 흐름

기준은 고정 v666 ZIP의 `localImplementationDraft`와 선택 동작의 `openInternal(node,false)`다. 이미 저장된 copy의 M11을 새 기능으로 다시 구현하지 않는다. 기존 private copy 선택의 불변 snapshot 안에서 Root의 `next` C#을 같은 native `BlueprintNodeFlow`로 감싸고, 첫 Save에 copy·정보 배정·manifest·graph·새 내부 코드를 한 후보로 저장한다. 원래 팝오버·카드·버튼·레이아웃을 사용한다.

## 지원 경계

선택한 source/target 하나의 same-contract copy이며 기존 private graph 지원 profile을 사용한다. 아직 copy 파일이나 배정이 없는 때부터 내부 미리보기·본문 편집·Undo/Redo·Root 왕복·첫 Blueprint Save 및 부모 정보 Save를 연결한다. 새 공개 함수/계약을 만들거나 모든 target을 자동 선택하지 않는다. 최초 내부 미리보기에서는 원래 계약과 구조를 고정하고 선택한 본문만 편집한다. 기존 graph 안의 다른 private frame에서 첫 전환하는 경로와 실행 selector는 이번 Root `next` 단위에 합산하지 않는다.

새 `PrivateCopyNodeFlow`는 sealed seed·현재 guard·원래 node/definition/record hash·명시 nonce를 확인하고 기존 pure 래핑을 재사용한다. source path를 입력으로 받지 않는다. 원래 바깥 ID·signature·arguments·실행선·반환·표시 metadata와 copy 출처를 유지한다. 원문과 helpers를 내부 코드 한 개에 보존하며 본문을 사용자가 바꾼 경우에만 그 입력을 적용한다. this/재귀/import·whole-body/ref/out은 이미 확정된 native context/저장소 전달 규칙을 사용하며 자동 재작성·복사/초기화 추정을 추가하지 않는다.

기존 snapshot의 copy record는 아직 물리 파일로 만들어진 원본이 아니다. 선택한 가상 record를 새 내부 leaf로 옮기고 `retainedCode`에 원래 정의·ID·hash를 남긴다. donor의 실제 파일은 그대로 보존한다. 존재하던 C# 파일을 삭제하거나 덮어쓰는 처리가 아니며 `retainedCode`는 파일 접근 권한을 부여하지 않는다.

## 첫 저장과 기존 보호

첫 Save는 기존 `applySlots`의 격리 후보·전체 checkpoint CAS·영수증과 `settledSlots` 복구를 사용한다. 공개 계약/owner/원본 선택·binding이 바뀌면 전체를 거절한다. 부분 Review와 새 경로 충돌은 기존 보호를 따른다. 물리 파일 반영은 컴파일과 명시 Review→Confirm에서만 일어난다. 수락한 선택과 입력만 정리하고, 지연 응답 뒤 새로 들어온 본문은 같은 copy의 다음 Save용 입력으로 남긴다. copy 생성으로 소유 멤버십이 바뀐 뒤 이전 전환 Undo를 되살리지 않는다.

선택부터 첫 Save까지는 donor snapshot/관측 source 변경을 거절한다. 첫 Save 뒤 생성된 copy는 기존 copy 계약대로 독립된 저장 snapshot이다. 최종 파일 CAS는 owner·manifest·새 출력 등 실제 반영 대상을 보호한다. donor는 쓰기 대상이 아니며, 이미 복사한 뒤의 donor 본문을 새 copy가 묵시적으로 다시 읽거나 교체하지 않는다. 이 경계를 기존 source 편집의 원본 guard와 혼동하지 않는다.

## 구형 profile의 분류

`FeatureBlueprint.SupportsPrivateGraphs`와 기존 old-profile 회귀를 기준으로 한다. `sync-acyclic-ref-v1`, implicit/out/locals 계열 등 기존 형식의 읽기·실행 자체를 미구현으로 세지 않는다. 실제로 실행 가능한 구형 fixture를 만든 뒤 내부 전환을 요청하여, graph profile·코드·copy 선택·checkpoint가 바뀌지 않고 거절되는지 검증한다.

구형 profile의 암시 종료·출력/저장소 의미를 다른 profile로 자동 승격하지 않는 것은 **호환성 보호**다. v666 원본은 native 구형 저장 형식의 마이그레이션 정책을 정하지 않는다. 자동 또는 새 일괄 마이그레이션은 이번 고정 필수 잔여가 아니며 추가하지 않는다. 현대 profile의 M11 실제 미구현과 구분한다. 이 설명은 기존 함수 편집이나 명시적 기존 profile 도구 전체를 금지하는 정책이 아니다.

## 검증과 진단

`tools/verify_desktop.py --suite node-internal-copy-creating`는 독립 LF/CRLF·새 패키지·전체 SHA/CRC/모드 복원·복원본 실행·실패 수명관리를 순차 검증한다. 신규 first-save API/화면과 기존 private snapshot checkpoint, 저장 copy context/실행 분기, native 중첩/whole-body/ref-out·소유 보호 및 원문 편집을 다룬다. 최신/정상 롤백과 입력·로그·프로필·스크린샷·manifest를 지속 보관한 뒤 해당 실행 소유 임시물만 정리한다. 최종 신규/재사용 검사와 수치는 아래에 기록했다.

집중 실행의 첫 두 실패는 fixture 모듈에 명시 default source가 없어 선택할 source가 없었던 문제였다. 이를 실제 기존 module 규칙에 맞게 고쳤다. 다음 미리보기의 JSON node 이중 parent 오류는 제품 후보를 `DeepClone`으로 분리해 수정했다. 첫 Save 뒤 donor 본문 경합을 최종 쓰기 CAS 대상으로 잘못 가정한 검사도 실패로 보존하고, 기존 독립 snapshot 의미와 대조해 owner 경합을 검사하도록 바로잡았다. 원본 선택 시 donor 경합 검사와 실제 쓰기 대상의 최종 CAS 검사를 모두 유지한다. 늦은 C# 입력은 저장됐지만 마지막 본문 receipt 뒤 accepted copy 선택이 남아 완료를 막는 제품 오류도 수정했다. 정확한 copy/출처와 수락된 receipt를 확인하고 같은 copy의 입력·미확정 시도가 모두 없을 때만 선택을 해제한다. 대기 조건이나 실제 기능 검사를 약화하지 않는다. 실패 로그·입력·수정 전 source를 보존하며 실패를 최종 통과 수에 합산하지 않는다.

## 고정 잔여

M11 전체 완료는 아니다. 생성 중 copy의 기존 중첩 문맥과 실행 selector, 직접 상속/참조 내부 진입은 실제 기존 원본 요구/소유 경계와 대조할 잔여다. 가능한 타입/target/프레임의 모든 조합을 새 필수 작업으로 만들지 않는다. 공개 override 입출력 구조 변경 거절은 정상 보호이며 독립 공개 계약 복제는 필수에서 제외한다. 부모·외부/참조 원본을 직접 쓰지 않는다.

B2 타 사용자/그룹 backend, 정보 종류 C# 표현/사용 중 삭제 대응, M4/M12 및 3D/권한 별도 팩과 고정 V2–V9는 기존 잔여다. 3D 이동은 표시 연출이며 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달은 교차 패키지와 구분해 미완료로 유지한다.

## 최종 코드의 검증 결과

실행 코드 commit은 `8b6bb4d2dabf051855959b8c8a4f053a09f50512`다. 독립 LF **19단계**, CRLF **19단계**, 새 교차 패키지·전체 압축 복원·실패 수명관리 **8단계**, 총 **46단계**를 모두 새 실행했고 실패/skip 없이 통과했다. 양쪽에서 native 분기/중첩/whole-body/ref-out **28개** 및 상속/소유 보호 **2개**가 각각 통과했다. 기존 private copy snapshot/checkpoint와 저장 copy의 whole-body·실행 분기 영향 회귀도 새 실행했다. 검사 정의를 재사용했지만 이 단계 수에 과거 실행 결과를 합산하지 않았다.

새 copy API는 미등록 copy의 무쓰기 미리보기·sealed seed/source binding·원자적 첫 생성/배정·반복 receipt/cold·C# 컴파일 오류 입력 보존/명시 수정·부분 Review/owner 최종 CAS·실제 copy/donor 실행을 확인했다. C#/Blueprint 출처와 this/재귀/import·ref/out, 실제 실행 가능한 구형 ref profile의 비승격 보호를 구분했다. 화면은 기본/독립 창·본문 취소/편집·전환 Undo/Redo·Root Save·부모 정보 Save·명시 취소/cold·쓰기 실패·donor 선택 경합·응답 유실 receipt·늦은 입력·동일 ID 프로젝트 왕복·Review 취소/Confirm·확정 cold를 확인했다. 생성 패키지는 직접 소유 및 새 copy 화면을, 전체 복원본은 저장 copy와 raw C#·ref/out 새 copy의 독립 창 응답 유실을 새 실행했다.

집중 실행의 fixture source 누락·잘못된 CAS 대상 가정과 제품의 JSON node parent/accepted 선택 정리 실패를 각각 보존했다. 제품 수정 전 source snapshot 및 단계별 입력/해시·프로필·로그를 남겼다. 늦은 본문이 실제 저장된 뒤에도 수락된 선택이 남던 오류는 정확한 copy/출처·receipt·남은 입력/미확정 시도를 확인한 뒤 해당 선택만 정리하도록 수정했다. 검사 대기 조건이나 원자 저장/소유 보호를 완화하지 않았다. 위 최종 동결 코드 검사는 모두 새 실행했으며 집중 실패를 통과 수에 합산하지 않았다.

- 최종 관리 record: `/workspace/artifacts/v536-verification-managed/runs/9674a911fcb44a66bcc4b54521e26c97.json` (cleaned).
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/9674a911fcb44a66bcc4b54521e26c97.zip`, SHA-256 `bb4047906ec2779c8fb6130cc39f9f557df68d708f1c57637fbd32b8a2392e26`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/54666151f76a412e9edb0989db36da16.zip`, SHA-256 `3161abe07277ceb3464dc0940357c3d94a7452d2128646f1988b96a6a43efbe5`.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `8b6bb4d2dabf051855959b8c8a4f053a09f50512` | `a5d633daa31a49db13d2bd238bf619b7e58090b9d65c771ba4f75011625a1e90` | 51,267,810 | `bf1d390f7a54acc20df9e6f10cd5930a8a6eb79d16ecf4d7d9b685d18d6937b8` |
| 정상 롤백 | `dc9e09ee7b63e764653b84d111e2b3c8ef38bdd0` | `8f22ab6241af3c1499fef36a9464798c112c1dc8396fc8864dc7234603ae3d6c` | 51,263,223 | `c4481e96f656f39a157cae35e0500ba61cd47ac480a8707104f3bbb131544f52` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 위 코드로 새 생성·전체 SHA/CRC/모드 복원·복원본 실행을 검증했다. 롤백은 직전 정상본의 검증 결과를 재사용하고 ZIP SHA를 다시 확인했다. latest: 2364파일·147디렉터리 / rollback: 2363파일·147디렉터리.

최종 관리 실행의 디스크 여유는 **2015.91 MiB → 2011.75 MiB**, 순증가 **4.16 MiB**다. 집중 실행의 증거 보존 순증가는 3.53 MiB이며 별도 집계다. 최종 단계 샘플 최소 여유 2015.85 MiB, cgroup 메모리 피크 4263.56 MiB였다. 기존 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함)과 RAM/메모리 사전 검사를 낮추지 않았다. 집중/최종 임시 root는 증거·패키지의 지속 보관 및 소유 프로세스 종료 확인 후 제거했다. 승인된 최신/롤백 회전과 실행별 자체 임시 정리만 적용했고 과거 비관리 자료를 추가 삭제하지 않았다. 이 실측은 이후 단위당 증가를 보장하지 않는다.

구형 profile 자동 승격은 호환성 보호이며 새 필수 마이그레이션으로 세지 않는다. 검증 결과를 기록한 게시 HEAD와 위 패키지 실행 코드의 차이는 문서뿐임을 확인한다. 실행 source/리소스는 동일하며 보고서 commit에서 다시 빌드했다는 뜻은 아니다. 남은 M11 생성 중 copy의 중첩/실행 selector와 상속/참조 경계, B2/M4/M12·종류·별도 팩·실제 Windows/WebView2/모바일/전체 UI/Library·Space 전달은 완료로 집계하지 않는다.
