# 새 copy의 중첩/실행 분기 최초 내부 흐름

고정 v666 ZIP의 `localImplementationDraft`와 `openInternal(node,false)`가 근거다. 기존 copy 선택 안의 직접 소유 동작에서 내부 흐름으로 들어가 편집한 뒤 첫 저장/배정을 완료하는 사용자 흐름을 연결한다. 저장된 copy 및 이미 완료한 Root next 전환을 별도 새 요구로 다시 구현하지 않는다. 원본 팝오버·카드·레이아웃을 유지한다.

## 지원 경계와 원문 보존

선택한 source/target 하나의 불변 same-contract snapshot에서, 기존 private graph의 next C# 또는 실행 selector 하나를 기존 pure native 래핑으로 감싼다. Root와 모든 기존 소유 조상 frame에서 같은 전체 경로/관측 원문 binding을 사용한다. 동일한 로컬 ID가 다른 frame에 있어도 바꿔 붙이지 않는다. 깊이별 새 제한이나 자동 의미 변환을 추가하지 않는다. 엔진의 기존 graph/후보 예산은 유지한다.

기존 바깥 node ID·signature·arguments·실행선·출처·profile과 Result ID/값/순서·반환 의미는 유지한다. 선택한 원문과 helpers는 내부 코드 하나에 보존한다. 본문/helpers를 사용자가 편집했을 때만 그 입력을 검증한다. 실행 enum 구조를 바꾸는 최초 저장 후보는 전체 거절하며 임의 기본 분기를 선택하지 않는다. C# Result는 실행 분기이며 정보 EnumValue 자료형이 아니다.

copy 파일이 아직 없는 상태의 전환·본문 입력·Undo/Redo·조상/Root 왕복·cold를 연결하고, 첫 Blueprint Save 및 부모 정보 Save는 기존 applySlots 단일 후보·checkpoint CAS·영수증으로 copy/owner 배정/manifest/graph/leaf를 함께 저장한다. 실제 파일은 Review→Confirm에서 반영한다. 미리보기 때 donor·checkpoint·등록·배정을 쓰지 않는다. 오류/충돌/취소/응답 유실·늦은 입력도 기존 거래 경계를 사용한다. 유효한 첫 저장 후 원본 snapshot을 묵시적으로 다시 읽지 않는다.

선택된 가상 코드 record만 내부 leaf로 이동하며 원래 definition/ID/hash는 retainedCode에 남긴다. 실제 donor 및 다른 copy/frame/source 파일은 보존한다. 부모·외부/참조 원본에 직접 쓸 권한을 부여하지 않는다. 공개 override 입출력 계약 변경은 정상 보호이고 독립 공개 계약 복제는 요구에서 제외한다.

## 유한한 잔여

이 단위는 새 copy의 기존 Root/중첩 next 및 실행 selector 최초 전환이다. 직접 상속/참조 M11 진입은 기존 원본 요구와 실제 소유 경계를 대조할 잔여다. 정상적으로 금지된 부모/외부 원본 쓰기를 미구현으로 세지 않는다. 임의의 target/type/프레임 조합이나 그래프 생성·마이그레이션을 새로운 필수 목록으로 늘리지 않는다.

private graph 미지원 legacy profile의 자동 승격 거절은 호환성 보호이며 새 필수 마이그레이션이 아니다. 기존 읽기·실행/명시 profile 도구는 유지한다. B2 타 사용자/그룹 backend, 종류 C# 표현/사용 중 항목 삭제 대응, M4/M12 및 고정 V2–V9·별도 3D/권한 팩은 기존 잔여다. 3D 이동은 시각적 연출이며 작업 실행 조건이 아니다.

## 검증 원칙

`tools/verify_desktop.py --suite node-internal-copy-frames`는 독립 LF/CRLF, 새 교차 패키지, 전체 파일 SHA/ZIP CRC/모드 복원 및 복원본 실행, 실패 수명관리 검사를 순차 수행한다. 원문 편집·소유 보호·기존 private snapshot checkpoint·저장 whole-body/실행 분기 copy를 영향 회귀로 유지한다. 집중 검사 진단 실패와 최종 동결 코드 통과를 구분하며 과거 통과를 새 실행 수에 합산하지 않는다.

입력·로그·프로필·스크린샷·manifest와 최신/정상 롤백 패키지를 지속 보관한 뒤 소유 프로세스 종료와 소유권을 확인해 이번 임시물만 정리한다. 과거 비관리 자료 삭제나 보관정책 변경은 하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·전체 UI·Library/Space 전달은 교차 패키지와 구분해 미완료다.

## 집중 진단

첫 실행 분기 API에서 native 후보의 `executionForwarded`가 새 copy 미리보기 projection에 전달되지 않는 실제 제품 누락을 확인했다. 미리보기도 기존 definition의 실행 전달/실행 source/소유 문맥 경계와 노드의 caller-storage 표시를 그대로 전달하도록 수정한다. 원본 graph·실행 계약 자체나 검사 판정은 바꾸지 않는다. 실패 로그와 수정 전 제품 source를 보존하고 최종 동결 코드 검사를 새 실행한다.

중첩 화면 진단에서는 아직 물리 ID가 없는 copy frame을 Root로 관측하는 제품 누락도 확인했다. 기존 graphIdentity의 전체 private 경로를 전환 제안에 사용하도록 수정한다. 첫 화면 검사의 조상 이동은 기존 비동기 작업 완료를 기다린 뒤 다음 동작을 수행하며 기능 검증 조건은 유지한다. 오류 발생 시 브라우저 종료 전에 DOM·스크린샷·입력을 보존한다.

집중 화면 실패 중 busy 작업이 끝나기 전의 조상 이동과, 이미 Root에 있는 부모 Save 준비에서 breadcrumb를 다시 선택한 경우는 검사 순서 문제로 구분했다. 각 동작은 기존 busy 종료 후 한 번만 수행하고 최종 Root 표시를 명시적으로 확인한다. 입력·파일·실행 결과·CAS 판정과 timeout을 완화하거나 자동 재클릭으로 덮지 않는다. 각 실패도 증거에 남긴다.

최종 CRLF 늦은 입력 검사에서, 검사 도우미의 helpers 확인용 `f.pending()`이 의도적으로 보류한 applySlots 응답까지 flush하려고 기다리는 교착을 확인했다. 실제 checkpoint는 첫 저장까지 완료됐으며 제품 코드 오류로 집계하지 않는다. 이 테스트는 첫 편집 때 helpers 입력을 한 번 확인하고, 같은 helpers를 쓰는 늦은 본문 편집 중에는 추가 flush를 요청하지 않도록 고친다. 늦은 입력/실행/저장 결과의 판정은 유지한다. 멈춘 실행 소유 worker만 종료하고 입력·로그·36개 통과 결과·실패 증거를 보관한 뒤 임시 root를 정리했다.

재개 검증은 제품 파일의 Git blob 동등성과 도우미의 한 조건 변경을 확인한다. 이전에 완료한 비지연 테스트만 source/명령/로그 SHA와 함께 명시적으로 재사용하고, 독립 LF/CRLF 준비·남은 UI·새 패키지/전체 복원/실패 수명관리는 새로 실행한다. 지연 검사의 실패를 통과나 skip으로 바꾸지 않는다. 신규/재사용 개수 및 패키지 provenance는 최종 결과에 별도로 적는다.

## 최종 코드와 신규/재사용 검증

최신 패키지 source는 `3d91ba6acea42354afdc48b9f0c2a08887e2b8d9`다. 제품 구현은 `c474cb28a8b2e20825293955815448c643a21c94`와 Git blob 전체가 같고, 차이는 위 검사 도우미의 단일 조건과 이 결과 문서뿐이다. 최종 **47단계 통과 = 새 실행 23 + 동등 증거 재사용 24**이며 실패/skip을 통과로 바꾸지 않았다.

| 검증 묶음 | 총 단계 | 새 실행 | 동등 결과 재사용 |
|---|---:|---:|---:|
| 독립 LF | 20 | 6 | 14 |
| 독립 CRLF | 19 | 9 | 10 |
| 새 교차 패키지/전체 복원/실패 수명관리 | 8 | 8 | 0 |
| 합계 | 47 | 23 | 24 |

LF/CRLF의 clone·checkout·restore·Release·MCP·새 엔진은 모두 새 실행했다. native 분기/중첩/whole-body/ref/out 28개 및 소유 보호 2개는 각각 앞선 `c474cb2` LF/CRLF에서 통과했으며, 제품·실제 검사 harness·SDK/NuGet의 전체 파일 hash 동등성을 검증해 결과를 재사용했다. 기존 checkpoint·저장 copy 문맥/반복 실행 분기·새 copy API·정상/취소/쓰기 실패/충돌/응답 유실의 완료 결과도 같은 명령/소스/로그 SHA로 연결한다. 실패했던 늦은 입력 결과는 재사용하지 않았다. 재개 archive의 `equivalent-reuse.json`, `equivalent-dependencies.json`, `equivalent-reuse-driver.py`가 그 근거다.

수정한 CRLF 늦은 입력, 동일 ID 프로젝트 왕복, 독립 창 부모 Save/Review/Confirm/cold는 새로 통과했다. 새 패키지의 기존 직접 소유 흐름 및 새 copy 중첩 분기 화면, 전체 SHA/ZIP CRC/모드 복원, 복원본의 저장 whole-body copy 및 새 copy 중첩 ref/out·독립 창 응답 유실, 성공/실패/예외 수명관리도 모두 새 실행했다. 보존 입력과 원문·실제 실행 결과·최종 CAS 판정은 유지한다. 실제 Windows apphost/WebView2·모바일 기기·전체 UI·Library/Space 전달은 미완료다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/81fb00f0f38344479de5ff0d1fa5e6de.json` (cleaned).
- 최종 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/81fb00f0f38344479de5ff0d1fa5e6de.zip`, SHA-256 `13a478065ebd186826b6aa9e6832c3e49b0c429199244266872118ac4cb27bbd`.
- 중단한 진단 실행: `/workspace/artifacts/v536-verification-managed/runs/6d8499b1c6314f0bb1ca8291b78981f8.zip`, SHA-256 `0542d0eecacc0f7a17e23bc8b79296e190e606f69383fc79c9f5767b6446567f`. 36개 통과와 소유 worker 종료 `-15`를 그대로 보존한다.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/bedd25ff383549749c13e96a8f097444.zip`, SHA-256 `b44fe896fb4686cf3887b460499d2c78c92c7563fc47f4a43a6db9ed6f439aaf`. 제품 projection/가상 frame 오류와 검사 순서 실패도 포함한다.

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `3d91ba6acea42354afdc48b9f0c2a08887e2b8d9` | `067f332da31eb0e6877026b072bf03309408359933165a73f4687f417ba9e074` | 51,266,676 | `841791b87360f67b8338f21cc316825cc8d68a1f52c2c5d77d9e7f35a6b4e62a` |
| 정상 롤백 | `8b6bb4d2dabf051855959b8c8a4f053a09f50512` | `a5d633daa31a49db13d2bd238bf619b7e58090b9d65c771ba4f75011625a1e90` | 51,267,810 | `bf1d390f7a54acc20df9e6f10cd5930a8a6eb79d16ecf4d7d9b685d18d6937b8` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 양쪽 모두 2364파일·147디렉터리다. 최신은 새 생성·전체 복원·복원본 실행을 검증했고, 롤백은 직전 정상본의 검증 결과를 재사용하며 archive SHA를 다시 확인했다. 유일한 정상본을 먼저 제거하지 않는 기존 관리형 승격/회전만 사용했다. 과거 비관리 패키지/캐시/원본/사용자 데이터는 추가 삭제하지 않았다.

재개 검증의 디스크 여유는 **2002.55 → 1998.74 MiB**, 순증가 **3.80 MiB**다. 집중 증거 증가는 4.42 MiB, 중단 진단 증거 증가는 4.29 MiB로 별도 집계한다. 새 단계 샘플의 최소 여유 2002.50 MiB 및 cgroup 피크 4554.71 MiB를 기록했다. 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함)과 기존 RAM/메모리 예산은 낮추지 않았다. 세 실행의 자체 임시 root는 증거 보관·소유 자식 종료 인증 후 제거됐다. 이 실측은 이후 증가량을 보장하지 않는다.

검증 후 결과 문서만 추가한 게시 HEAD와 위 패키지 source의 차이는 문서뿐임을 확인한다. 실행 source/리소스는 같고 보고서 commit으로 패키지를 다시 생성했다는 뜻은 아니다. 이번 단위는 새 same-contract copy의 기존 Root/소유 중첩 next 및 실행 selector 최초 전환/첫 Save를 닫는다. 직접 상속/참조 M11 소유 경계와 나머지 고정 수용 항목은 잔여이며 legacy 자동 승격·공개 override 계약 변경·독립 공개 계약 복제를 새 필수 작업으로 추가하지 않는다.
