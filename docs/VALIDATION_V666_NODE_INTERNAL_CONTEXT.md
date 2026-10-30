# M11 whole-body 인스턴스 문맥의 내부 흐름

## 원본과 지원 범위

저장소 v666 `dist/blueprint.js`의 `data-function-write-direct` → `openInternal(node,false)` → `api.internal`을 따른다. 기존 직접 소유 next C# 동작의 단일 코드 래핑을 whole-body 멤버에 연결한다. 원문을 분석하여 별도 의미 그래프로 변환하지 않는다. 기존 private 지원 profile을 유지하며 구형 profile을 자동 승격하지 않는다. 공개 override의 입출력 계약 유지와 독립 계약 복제 제외 합의도 유지한다.

기존 whole-body 계약의 `implementationContext`를 실제 소유 구현·namespace-qualified 함수 ID·입출력 signature·scoped import와 대조한다. 원래 `public Invoke`를 같은 생성 구현 클래스에 한 번만 둔다. 내부 leaf와 그 조상은 같은 인스턴스로 연결되며, ref/out은 기존 native 규칙으로 동일 저장소를 명시 전달한다. `this.Invoke` 재귀, `this.calls`와 `IImports`, 원문 파일의 `sourceIdentity`를 바꾸지 않는다. scoped import를 canonical import 매개변수로 바꾸지 않는다. 다른 target 본문은 그대로 둔다.

관측되지 않은 다른 receiver, 변경된 scoped binding, 트리 안의 중복 인스턴스 멤버는 전체 거절한다. derived `contextBoundary`는 래핑 후 Root 계약·alias·노드 이름 보호를 유지한다. 이는 저장 문법이나 새 권한이 아니다. 기존 C# 편집기는 실제 whole-body의 고정 `Invoke` 선언을 표시하며 본문만 편집한다.

부분 본문 편집에서 textarea의 LF 정규화가 편집하지 않은 CRLF verbatim 문자열까지 바꾸던 결함을 수정했다. 정규화된 편집 위치를 원문 위치에 대응하여 바뀐 구간만 적용하고, Undo/Redo도 원문 구간을 복원한다. C# 문자열 치환이나 자동 소스 재작성이 아니다. 사용자가 실제로 바꾼 텍스트는 그대로 컴파일 검증한다.

전환 Save는 기존 `authorBatch` 후보·원문 guard·새 leaf와 최종 CAS를 재사용한다. 취소·컴파일 오류·충돌·응답 유실·cold·늦은 입력 보호를 유지하며 활성 구현은 Review→Confirm에서만 반영한다. 원래 record/C# 파일은 보존한다.

## 검증 자료

`tests/web/v666_node_internal_context_fixture.py`는 실제 `blueprintConversion`이 만든 직접 소유 property profile whole-body를 사용한다. scoped provider는 +3, 잘못 선택할 canonical provider는 +30을 반환한다. 실제 호출 전후의 재귀·동일 ref/out 별칭과 서로 다른 저장소·void·CRLF literal·CallerFilePath/CallerMemberName·IImports 소유 type·별도 Linux target 결과를 비교한다. qualified leaf probe는 컴파일만 하고 실행하지 않는다. 반복 내부 진입도 같은 receiver를 보존해야 한다.

`v666_node_internal_context_api.py`는 위 의미와 문맥 위조/중복 거절, 부분 Review, 컴파일 오류 입력 보존, Review 이후 원문 경합의 최종 CAS, cold와 원래 계약 보호를 확인한다. `v666_node_internal_context_ui.py`는 원본 화면의 미리보기/Undo/Redo·본문 취소/편집·Root Save·실패/재시도·응답 유실·늦은 입력·프로젝트 왕복·Review 취소/Confirm을 검증한다. `v666_script_raw_edits.mjs`는 부분 편집/Undo/Redo와 고정 선언 보호에서 CRLF·혼합 줄바꿈 및 Unicode 원문을 확인한다.

최종 독립 LF/CRLF checkout과 새 Windows 교차 패키지/전체 SHA·모드 복원 검증은 `tools/verify_desktop.py --suite node-internal-context`로 수행한다. 해당 실행의 결과·보관 commit/manifest·공간 실측은 검증 후 아래에 기록한다. 일반 Root/중첩/ref-out 회귀와 native 중첩·whole-body·소유 경계 검증을 함께 수행한다. 이전 단위의 통과를 이번 코드의 신규 통과로 계산하지 않는다.

## 남은 경계

M11 전체 완료는 아니다. private 미지원 기존 profile, 실행 분기/enum, copy·상속·참조 문맥 전환과 독립 슬롯 창/모바일 진입은 이번 지원 완료로 집계하지 않는다. 임의 C#의 stack trace·reflection 등 모든 관측 결과의 완전 동등성을 주장하지 않는다. 본문 자동 재작성이나 새 핀/계약 ID 정책도 추가하지 않는다.

B2 다른 사용자/그룹 권한 backend, 종류 C# 표현과 사용 중 항목 삭제 대응, M4/M12 및 3D/권한 별도 팩은 고정 잔여다. 3D 이동은 표시 연출이며 작업 실행 조건이 아니다. 실제 Windows apphost/WebView2·실제 모바일·전체 UI·Library/Space 전달은 교차 패키지 검증과 구분한다. 미반영 전환 초안을 구버전 롤백 UI로 확정하는 호환성은 별도로 보장하지 않는다.

## 최종 코드의 검증 결과

실행 코드 commit은 `383863158de6b4e4efe8b505699b1cac614bd8bc`다. 새 독립 LF **23단계**, CRLF **20단계**, 새 교차 패키지·전체 압축 복원·실패 수명관리 **8단계**, 총 **51단계**가 모두 통과했다. 양쪽 checkout에서 native 중첩/whole-body/ref-out **21개**와 상속/소유 보호 **2개**가 각각 통과했고 실패/skip은 없다. 일반 Root·void·중첩·기존 ref/out 저장소, 공통 선언/아이콘의 영향 회귀도 새로 실행했다. 원래 검사 정의를 재사용한 것과 과거 실행 결과를 재사용한 것을 구별한다.

신규 whole-body API는 this/재귀/scoped import·원문 파일/멤버/type·다른 Linux target, ref/out의 동일/다른 저장소, void, 반복 진입, qualified 컴파일 probe, 위조/중복 문맥·부분 Review·컴파일 오류·최종 CAS·cold를 확인했다. 화면은 기본 편집·취소/Undo/Redo·Root Save·실패/재시도·충돌·프로젝트 왕복·응답 유실·늦은 ref/out 입력·Review 취소/Confirm을 확인했다. 새 생성 패키지와 전체 복원본의 Linux .NET 런타임에서도 Root와 whole-body 화면을 실행했다.

집중 진단의 초기 target/import·fixture 헬퍼 실패는 최종 통과에 합산하지 않았다. 수정 전/후 로그와 합성 입력을 보존한다. 다른 OS 전용 본문이 있는 화면에서는 기존 OS 본문 선택 규칙을 바꾸지 않고 common을 실제 선택할 수 있는 fixture를 사용했다. 별도 Linux 본문의 실행 전후 보존은 API에서 검증했다.

- 최종 관리 record: `/workspace/artifacts/v536-verification-managed/runs/b192c8ea105c44c9b878ba6586da5484.json` (cleaned).
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/b192c8ea105c44c9b878ba6586da5484.zip`, SHA-256 `64e4e5b634e1478ea1435572e8f81d065a72c901518568dbe70866968294fd48`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/5969db095b104b95b3d326a4c594773f.zip`, SHA-256 `74de365ab380b557974154d7be687abe867aa45ff2b0425556e9a133db7150bb`.

| 보관본 | 실행 코드 commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `383863158de6b4e4efe8b505699b1cac614bd8bc` | `931e6cd878e315a0387c46d3fdced726b029634dc0d3de9ad51aee1b4aad4c80` | 51,248,015 | `1c0ca5dedc75957363ce87dbadcfe843734a79e76380fe476eb8d918675a3008` |
| 정상 롤백 | `f7084302b15ecbf7de8e39f6d9554fdfd2e83d7d` | `aa300d0063df890fceb073bbc7f6020ddca396c35e5d8796f6ae9f323cd5438c` | 51,243,266 | `0e61fde0ecb5f1179c68f4c37d0c51e534d79dedb6a60948b8f6d3b3cb2d5b80` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 이번 코드로 새 생성·전체 파일 SHA/CRC/모드 복원 및 복원본 실행을 검증했다. 롤백은 직전 정상본의 검증 결과를 재사용하고 ZIP SHA를 다시 확인했다. 최신 2510항목(2363파일/147디렉터리) / 롤백 2510항목(2363파일/147디렉터리).

최종 관리 실행의 디스크 여유는 2090.82 MiB → 정리 후 2086.12 MiB, 순증가 **4.70 MiB**다. 단계 샘플 최소 여유 2090.75 MiB, cgroup 메모리 피크 4554.80 MiB였다. 기존 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함)과 RAM/메모리 사전 검사를 유지했다. 집중/최종 소유 임시 root는 증거 보존 후 제거됐다. 승인된 관리 저장소의 최신/롤백 회전과 해당 실행의 자체 임시 정리만 적용했고 과거 비관리 자료는 추가 삭제하지 않았다. 이 수치는 이번 실행의 실측이며 이후 순증가 보장이 아니다.

최종 결과 기록은 문서만 추가한다. 패키지 실행 코드 commit과 이후 게시 HEAD의 차이가 문서뿐임을 확인한다. 실행에 관여하는 source/리소스는 동일하며 보관 패키지는 위 코드 commit에서 만든 바이트 그대로다. 보고서 commit으로 다시 빌드했다는 뜻은 아니다. 실제 Windows/WebView2·모바일·전체 UI·Library/Space 전달과 위 미지원 문맥은 완료로 집계하지 않는다.
