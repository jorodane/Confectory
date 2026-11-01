# M12 정수 out와 공개 실행 분기 동시 반환 검증

## 지원 계약

원본은 저장소 v666 ZIP SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다. `dist/blueprint.js` 149–156행은 동기 출력의 `out` 매개변수와 별도 실행 `Result`를 함께 정의하고, 248행은 결과 분기 처리 뒤 연속 실행을 명시한다. [현재 M12 계약과 경계](BLUEPRINT_ROOT_EXECUTION.md).

이번 지원은 **직접 소유 동기 void 함수·기존 값 입력·정수 out 하나·단일 Blueprint target·명시한 직접 Blueprint 호출자 하나**다. 기존 `IInvoke(..., out int)`와 원래 C# record 바이트를 유지한다. 선택적 `IExecutionInvoke.InvokeExecution(..., out int)`가 같은 out 저장소를 전달하고 실행 enum을 별도로 반환한다. 생성된 public call에서 빠져 있던 `out` 수식어를 전달하며, 기존 export 카드는 같은 전체 후보/Review 그룹에 참여한다. 인터페이스·어댑터의 기존 매개변수 생성 규칙을 재사용했고 원문을 tuple/새 C# 본문으로 재작성하지 않았다.

호출은 한 번 실행하고 출력 값을 발행한 뒤 성공·실패 분기와 다음 동작을 처리한다. None은 분기 선택 없음이며 출력을 버리거나 실패로 바꾸지 않는다. 원래 출력 미배정 경고/기본값·예외 규칙은 유지한다. 타입·이름·순서·핀/연결·원본 부모/외부·권한·override 입출력 계약·기존 원본 레이아웃은 변경하지 않는다. out 타입 변경·복수 out·ref 입력·비void 반환은 이번에 일반화하지 않았다.

## 최종 신규 실행

동결 코드 source는 **`d29168242410d1a96f523057f53ba62756de4648`**다. `tools/verify_desktop.py --suite root-execution-out`에서 다음 **42단계 모두 신규 실행·통과**했다. 집중/이전 패키지의 성공을 최종 단계 수로 재사용하지 않았고 실패·skip을 통과로 세지 않았다.

| 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF clone/checkout·restore·Release/MCP/엔진·native·API/UI·영향 회귀 | 19 | 0 |
| 독립 CRLF의 같은 준비·native·API/UI·영향 회귀 | 17 | 0 |
| 새 Windows 교차 패키지·실행·전체 복원·실패 수명관리 | 6 | 0 |
| 합계 | 42 | 0 |

각 checkout은 `--no-hardlinks` 독립 clone과 별도 tool home·NuGet/compiler cache를 사용했다. 각각 공개 분기·기존 switch/중첩/whole-body/ref/out native **37개**, 소유 경계 **2개**, 최종 owned read CAS probe **4개**가 실패/skip 없이 통과했다. native 사례와 위 실행 단계는 다른 집계다.

새 native 사례는 성공 `10`·실패 `-10`을 분기와 다음 동작이 읽는 순서, None에서도 `-10`을 유지한 연속 실행, 기존 void Invoke의 한 번 실행과 out `30`, 원래 CRLF/Unicode C# 바이트 보존을 확인했다. ref 입력·다른 out 타입·복수 out·비void metadata는 거절했다. 기존 예외 전파·오래된 계약/삭제된 ID 거절, whole-body this/재귀/import와 ref/out 저장소 회귀도 새로 실행했다.

API는 기존 ordinary out 호출의 출력 소비, 정확한 루트/호출자 전체 후보·checkpoint CAS·cold·동일 요청 receipt 재조회, 잘못된 분기/값/증거와 부분 Review 거절, Save 전/Review 뒤 호출자 원문 경합의 전체 미적용·입력 보존, 전체 Confirm·실제 CLR 실행을 확인했다. 화면은 기존 분기 사이드바·출력/반환 카드·명시 caller·Undo/Redo·취소·쓰기 실패 복구·물리 충돌·응답 유실·늦은 입력·cold·Review 취소/Confirm·반영 후 재시작을 확인했다. 성공 분기에서 다음 줄을 건너뛰어도 먼저 발행한 out `10`을 기존 반환 카드가 읽어 실제 종료 코드 `10`이 됐다. 늦은 입력은 이전 receipt 확인 뒤 두 번째 명시 Save로 별도 반영한다.

기존 out 없는 M12 API(LF)·화면(CRLF), 기존 혼합 선언·헤더 이미지, M11 종료점 API(LF)·등록 외부 부모 API(CRLF)도 새로 실행했다. M11을 새 미완료 작업으로 열거나 권한/부모 소유 경계를 변경하지 않았다.

새 교차 패키지 자체에서 out 정상 화면/저장/Confirm/실행을 검사했다. 전체 파일 SHA·ZIP CRC·파일/디렉터리 모드를 검증해 복원한 뒤, 복원본 기동과 out 늦은 입력 화면/실행을 다시 검사했다. 성공·실패·예외·변조 거절에서도 증거 보존과 자기 임시물만 정리하는 기존 수명관리 검사가 통과했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/3a483667cda844f88588c8d76ecdf1e1.json` (`cleaned`, 42/42).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/3a483667cda844f88588c8d76ecdf1e1.zip`, SHA-256 `95dfe28e5941a210a259e3065fafd0aed16abe7273f26cbbaeb057bef1886e66`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/69fd111c70da43df9b4f86ce4a6b917e.zip`, SHA-256 `e3a4a1a44316e55c9a7559643331258c60721338b229f34223ef81f0225bc496`.

집중 15단계 중 14통과·실패 1건을 보존했다. 초기 API fixture의 case 출력 카드에 기존 `branchOwner`가 빠져 `GRAPH_BRANCH_SCOPE`로 거절됐다. 테스트 자산을 기존 영역 규칙에 맞췄으며 제품 검증을 완화하지 않았다. 집중 native 뒤 추가한 None/out 소비 단언은 최종 양쪽 checkout에서 새로 실행했다. 집중 마지막 제품 overlay와 동결 Git blob의 전체 SHA 일치를 확인했다. 최종 42단계에는 이 초기 실패를 통과로 포함하지 않았다.

## 패키지 보관·공간

기존 관리형 index `/workspace/artifacts/v536-verification-managed/packages/index.json`에 다음 두 정상본을 보관했다.

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `d29168242410d1a96f523057f53ba62756de4648` | `3ef0a0eaceaa210ac1f77db04c5263862be2306c9b8d5c90e56522d5a8484c67` | 51,306,144 | `67e4a3ec8bbf7b17594822bb99a3504a839526f910f2b9dcabde2a15b8086dca` |
| 정상 롤백 | `92948003cc90f2e278bbe70ecd671742e569d3d2` | `a72fafc5810f6e97882715cfe1556f49b002cf9e9e2ac64a907f5603e7bb1510` | 51,305,693 | `0e2ee6b128ab8334702bd12d0c627d36993e1e27b63ed34e115b7996c6850f87` |

두 패키지 모두 2366파일·147디렉터리다. 최신은 이번 신규 생성·전체 복원·복원본 실행을 마쳤다. 롤백은 직전 정상본의 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 유일한 정상본을 먼저 제거하지 않는 기존 관리형 원자 승격/회전만 사용했으며 과거 비관리 자료는 삭제하지 않았다. 롤백 parser는 새 out+공개 분기 metadata를 지원하지 않으므로 새 자료를 구버전에서 실행할 수 있다고 보장하지 않는다.

최종 실행 여유는 **1975.20 → 1971.80 MiB**, 순증가 **3.39 MiB**였다. 집중 증거 순증가는 별도 **1.33 MiB**다. 최종 stage 샘플 최소 여유는 1975.15 MiB, cgroup 메모리 피크는 4537.40 MiB다. 추가 디스크 144 MiB(안전 64 MiB 포함), RAM 3 GiB+512 MiB, 메모리 7 GiB+1 GiB 예산을 낮추지 않았다. 집중/최종 소유 임시 root는 자식 종료·검증된 증거 보관 뒤 제거됐다. 미래 순증가를 보장하는 수치는 아니다.

## 고정 잔여와 미실행

이번 정수 out 하나의 승인 범위는 마감했다. 다른 데이터 계약(ref/다른 출력·비void), 여러 사용처/target의 공개 분기 계약 closure, same-contract copy·자식 소유 구현에서 기존 공개 분기를 반환하는 연결은 기존 유한한 M12 잔여다. 가능한 타입·문맥 순열마다 새 필수 행을 만들지 않는다. 공개 override 계약 변경·독립 새 계약 복제·비소유 원본 쓰기·legacy 자동 승격은 새 필수 요구가 아니다. 비void 데이터와 분기의 표현 선택은 이번에 결정하지 않았다.

M4는 시작하지 않았다. 기존 ABI/공유 호출자·타입/표시명, B2 타 사용자/그룹 backend, 종류 C# 표현·사용 중 삭제 대응, V2–V9·별도 3D/권한 팩은 고정 ledger대로 남긴다. 3D 이동은 시각 연출이며 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 전환·전체 UI·Space/Library 전달은 이번 신규 검사에 포함되지 않았다. Linux hosted UI/CLR 실행·교차 패키지를 실제 기기 검증으로 표현하지 않는다. 검증 뒤 결과 문서만 추가한 게시 HEAD와 위 source의 차이는 문서뿐이며 보고 commit으로 패키지를 재생성했다고 주장하지 않는다.
