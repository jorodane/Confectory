# M12 공개 루트 실행 분기 검증

## 원본과 지원 범위

고정 저장소 v666 ZIP SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의 `dist/blueprint.js` 실행 의미(248행), branch-exit 선택(718–739행), 루트 계약 패널(969–976행)을 따른다. [구현 계약과 경계](BLUEPRINT_ROOT_EXECUTION.md).

직접 소유한 동기 `void` 함수·값 입력·단일 Blueprint target과 사용자가 명시한 직접 Blueprint 호출자 하나를 연결했다. 기존 분기 사이드바의 추가/이름/삭제, 캔버스 반환 카드와 기존 분기 ID 선택, 호출자 실행 포트와 반환 카드 연결을 사용한다. 함수·구현·그래프·원래 C# record와 호출자 전체가 하나의 후보/Review 그룹이다. 원문·헤더 및 관측 closure도 checkpoint Save와 최종 Confirm commit lease의 읽기 CAS로 검증한다.

기존 `IInvoke.Invoke`와 사용자 C#을 유지하며 별도의 `IExecutionInvoke.InvokeExecution` 결과로 명시한 분기를 전달한다. 이름과 순서를 바꾸어도 ID/값이 유지된다. 미연결 일반 종료는 `None`이고 성공·실패를 추정하지 않는다. 원래 예외는 그대로 전파한다. 공개 enum metadata는 정보 `Enum/EnumValue` 또는 M11 private 실행 enum과 다르다. 부모·외부·참조 원본, override 입출력 계약, 권한과 원본 레이아웃을 확장하지 않았다.

## 최종 코드 신규 검증

검증 source는 **`92948003cc90f2e278bbe70ecd671742e569d3d2`**다. `tools/verify_desktop.py --suite root-execution`의 **40단계 전부 신규 실행·통과**했다. 이전 집중/과거 package의 통과를 이 수에 재사용하지 않았으며 실패·skip을 통과로 세지 않았다.

| 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF clone·checkout·restore·Release/MCP/엔진·영향 회귀·API/UI | 18 | 0 |
| 독립 CRLF의 같은 준비·영향 회귀·API/UI | 16 | 0 |
| 새 Windows 교차 패키지·실행·전체 복원·실패 수명관리 | 6 | 0 |
| 합계 | 40 | 0 |

두 checkout은 `--no-hardlinks` 독립 clone과 별도 SDK home·NuGet/compiler cache를 사용했다. 각각 공개 분기·기존 switch/중첩/whole-body/ref/out native **35개**, 소유 경계 **2개**, 기존 최종 owned read CAS probe **4개**가 실패/skip 없이 통과했다. 기존 혼합 선언·헤더 이미지, LF의 M11 종료점 API와 CRLF의 등록 외부 부모 API도 새로 실행했다. native 사례 수와 위 단계 수는 다른 집계다.

API는 원문/일반 void 호출의 실제 실행, 명시 후보·대응 누락/잘못된 분기/낡은 증거 거절, 다른 caller frame 원문 경합, 전체 후보 checkpoint CAS, 같은 요청 receipt 재조회·cold 복원, 부분 Review 거절, Review 취소, Review 뒤 caller 변경의 최종 CAS 거절과 전체 Confirm·실제 실행을 확인했다. 성공/실패·다음 줄은 한 번 실행되며 기존 void 진입도 한 번 실행한다. 잘못된 metadata·삭제/미선택 반환 ID·불완전 종료·opaque provider는 묵시적 변환 없이 거절한다.

화면은 분기 추가·Undo/Redo·한글 이름·반환 ID 선택·명시 caller 선택, caller 미선택 거절 시 입력 보존, 취소·저장 권한 실패 복구·원문 충돌·응답 유실·늦은 입력·cold, caller readonly 분기 포트 연결, Review 취소/Confirm·실제 CLR 실행·반영 뒤 재시작을 확인했다. 늦은 입력이 이전 in-flight 저장을 넘어서면 첫 재시도는 기존 receipt만 해결하고 새 입력은 미저장 상태로 유지한다. 두 번째 명시 Save가 새 입력을 별도 반영한다. 이를 자동 중복 저장으로 바꾸지 않았다. 원래 창에서 실제 25% 배율 메뉴로 반환 카드를 조작했으며 강제 click이나 레이아웃 수정으로 통과시키지 않았다.

새 패키지 자체에서 정상 UI/실행을 검사했다. 전체 파일 SHA·ZIP CRC·파일/디렉터리 모드를 검증해 복원한 뒤 복원본 기동과 늦은 입력 UI/실행을 다시 검사했다. 정상·실패·중간 예외·변조 거절에서도 증거를 보존하고 해당 실행이 만든 임시 복사본만 제거하는 기존 수명관리 probe가 통과했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/0aa1bf33e84a4218b11022dc569fd8b9.json` (`cleaned`, 40/40).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/0aa1bf33e84a4218b11022dc569fd8b9.zip`.
- 증거 SHA-256: `d2b4330057bfe9c7dfb03c1b4b2e7250dc4deba5bb03194e56c8e726f1da3e74`.
- 별도 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/aa7f5eefda0749b1b85f635ff4170b36.zip`.
- 집중 증거 SHA-256: `781b69811e35949d7cab6ca6248e877e46ab0694fb2cfa590f308e17519da218`.

## 집중 진단과 재사용 구분

집중 실행은 67단계 중 49통과·진단 실패 18건을 그대로 보존했다. 초기 컴파일·pack 지역변수 충돌, 루트 schema/공개 종료와 private 종료 검증 경계, UI 배포 hash, 원문/CAS 누락, JSON 노드 소유, 공개 caller 표시/반환 연결의 제품 오류를 수정했다. transport 성공과 semantic Confirm 거절의 구분 및 Review 뒤 checkpoint 기준을 바로잡은 검사 진단도 포함한다. legacy bool 시각 분기 fixture는 이번 원본 UI 범위 밖이라 기존 지원 enum selector fixture로 바꾸었으며 bool UI를 새로 추가하지 않았다.

마지막 늦은 입력 실패는 첫 post-cold Save가 이전 receipt만 해결한다는 기존 복구 규칙을 검사가 새 저장으로 잘못 기대한 사례다. 입력·backend 상태·authorBatch 미발생·두 번째 Save의 별도 반영을 각각 단언해 수정했다. 실패 로그/스크린샷/재현 입력을 지우거나 거절 검사를 약화하지 않았다. 집중 마지막 제품 overlay와 최종 Git blob의 전체 SHA 일치를 확인했다. 집중의 이전 동등 회귀는 진단 근거이며 최종 40단계를 대체하지 않는다.

## 지속 패키지와 공간

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다.

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `92948003cc90f2e278bbe70ecd671742e569d3d2` | `a72fafc5810f6e97882715cfe1556f49b002cf9e9e2ac64a907f5603e7bb1510` | 51,305,693 | `0e2ee6b128ab8334702bd12d0c627d36993e1e27b63ed34e115b7996c6850f87` |
| 정상 롤백 | `ccfb03452bb2654153ab510cc399a9f607cb2cad` | `2b5440224bcb3b39fa5b1e8fec8fbc1b029aba22b60e30d002d1134e118466ae` | 51,279,519 | `5d565f2ba001b740c1d109b79e29c0f90586eb0450b70dd18b547dfa1066da96` |

최신은 2366파일·147디렉터리, 롤백은 2365파일·147디렉터리다. 최신의 새 생성·전체 복원·복원본 실행은 위 신규 검사다. 롤백은 직전 정상본의 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 유일한 정상본을 먼저 제거하지 않는 기존 관리형 원자 승격/최신→롤백 회전만 사용했다. 과거 비관리 패키지·원본·로그·사용자 데이터는 정리하지 않았다.

최종 실행의 여유는 **1979.91 → 1976.78 MiB**, 순증가 **3.13 MiB**였다. 집중 증거 순증가는 별도 **3.54 MiB**다. 최종 stage 샘플 최소 여유는 1979.85 MiB, cgroup 메모리 피크는 4511.76 MiB다. 추가 디스크 144 MiB(64 MiB 안전 여유 포함), RAM 3 GiB+512 MiB 및 메모리 7 GiB+1 GiB 예산은 낮추지 않았다. 집중/최종 임시 root는 자식 종료 확인과 검증된 증거 보관 뒤 제거됐다. 미래 단위의 순증가를 보장하는 수치는 아니다.

## 남은 고정 경계

이번에 승인된 직접 소유 동기 void/단일 target/명시 직접 호출자 흐름을 마감했다. 전체 M12의 다른 원래 함수/호출 문맥이나 ordinary 값 출력·ref/out 결합까지 완료로 표시하지 않는다. M4 비동기 계약/완료 순서는 시작하지 않았다. 공개 override 계약 변경과 독립 새 계약 복제, legacy 자동 승격은 새 필수 잔여가 아니다. ABI 영향 closure/공유 호출자·고급 타입/표시명, B2 타 사용자/그룹 backend, 종류 C# 표현·사용 중 삭제 대응, 고정 V2–V9와 별도 3D/권한 팩은 기존 ledger대로 남긴다. 3D 이동은 표시 연출이며 실행 조건이 아니다.

새 공개 metadata/루트 schema를 과거 parser/롤백이 읽는다고 보장하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·DPI/IME·독립 창/프로젝트 전환 전체·전체 UI·Space/Library 전달은 이번 신규 검사에 포함되지 않았다. Linux hosted UI/CLR 실행과 교차 패키지를 실제 기기 실행으로 표현하지 않는다. 검증 뒤 결과 문서만 추가한 게시 HEAD는 위 컴파일/패키지 source와 문서만 다르며 보고 commit으로 실행 패키지를 재생성했다고 주장하지 않는다.
