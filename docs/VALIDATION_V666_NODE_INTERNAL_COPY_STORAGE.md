# M11 저장된 copy의 일반 ref/out 내부 흐름

## 원본 요구와 선택한 단위

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)이다. `dist/app.js`의 `localImplementationDraft`는 내부 동작을 재귀 복제하며 소유 compiled 문맥만 재배치하고 공개 입출력 계약을 유지한다. `dist/blueprint.js`의 `openInternal`은 선택한 동작으로 들어간다. 이미 지원한 저장 copy Root/중첩 일반 값 동작과 직접 소유 ref/out native 경로를 결합한다. 생성 중 copy의 별도 첫 owner Save 수명이나 상속/참조 원본 선택 정책을 먼저 바꿀 필요가 없는 다음 M11 어댑터 단위다.

대상은 프로젝트 소유 공개 함수를 구현하고 정보에 단독 직접 배정된 단일-target same-contract 저장 copy의 **일반 next C# 동작**이다. Root와 기존 소유 private graph에서 원래 ref/out 역할·바깥 저장소 배정·출력·반환·원문/helpers·ID·계약·copy 출처와 조상/형제·실행/값 연결을 유지한다. 생성 중 copy·whole-body `implementationContext`·실행 분기 선택기·상속/참조 전환을 함께 완료했다고 하지 않는다. 등록 함수 copy의 모든 실행 문맥도 새 검증 범위로 주장하지 않는다.

## 저장소와 소유 보호

앞선 단위가 값 입력만 허용하던 UI/native copy 진입 가드를 일반 ref/out까지 연결한다. 실제 native `BlueprintNodeFlow`의 기존 저장소 전달·할당 완료 규칙을 사용한다. `arguments`와 `forwardCallerStorage`를 추측해 교체하거나 out을 값 입력으로 만들지 않는다. 같은 변수를 여러 ref/out에 전달하는 경우, 별도 노드 출력에 보관하는 경우를 원래대로 구분한다. 기존 무쓰기 `SkipInit`/완료 규칙을 재사용하고 임의 초기값·값 복사·별칭 추정을 추가하지 않는다.

실제 owner·단독 배정·원계약·Root/implementation locator·전체 private 경로·선택 source/hash와 copy provenance receipt는 그대로 검증한다. 하위 멤버십 변경은 서버 내부 수명의 검증된 authority만 받으며 요청자 flag로 권한을 만들지 않는다. 공개 override 계약 변경·공유 copy 단독 갱신·donor/부모/외부 쓰기 거절을 유지한다. 새로운 공개 계약 ID나 핀 ID 체계를 발급하지 않는다.

기존 팝오버·고정 C# 선언·내부 버튼·빵부스러기·Review→Confirm을 재사용한다. HTML/CSS 레이아웃은 바꾸지 않는다. 사용자 입력을 단일 코드로 래핑하고 기존 전체 후보/checkpoint CAS·최종 물리 파일 CAS를 사용한다. 원래 record는 guard로 남고 새 leaf는 별도 소유 경로로 준비한다. 부분 Review·컴파일 오류·원문 충돌은 원본과 실패한 입력을 보존한다. Undo/취소·응답 유실 receipt·cold·늦은 입력은 기존 수명과 범위 키를 따른다.

## 유한한 수용 경계

검증은 기존 직접 소유 ref/out 수용 범주의 실제 관측 차이를 사용한다. 같은/다른 scalar 저장소의 alias, 명시적 별도 출력, out-only 순서, 배열 변수 교체, 예외 전 쓰기를 구분하며 타입·깊이·target의 모든 조합을 새 필수 항목으로 만들지 않는다. out 미할당 본문은 실제 C# 컴파일의 CS0177로 거절되어야 하며, 에디터가 기본값을 넣어 통과시키지 않는다.

| 사용자 흐름 | 이번 이후 분류 |
|---|---|
| 저장 copy의 Root/소유 private 값 입력 일반 C# | 앞선 완료 지원. 관련 API/UI·원문 편집을 영향 검증한다. |
| 저장 copy의 일반 ref/out 내부 진입·편집·Save | 이번 연결·검증 대상. 원래 caller/local 저장소 배정을 유지한다. |
| 생성 중 copy의 내부 진입 | 기존 private selection/첫 owner Save 어댑터 잔여. 새 복제 정책을 만들지 않는다. |
| copy의 whole-body 문맥·실행 분기 선택기 | 다른 native 문맥 어댑터 잔여. 일반 ref/out 지원과 구분한다. |
| 상속의 직접 소유 body/참조 진입·private 미지원 기존 profile·독립 C#/graph 재활성화 | 기존 M11 구현/정책 경계. readonly 원본의 자동 복제·부모 쓰기·profile 자동 승격·본문 폐기를 추정하지 않는다. |
| override 공개 계약 변경·독립 새 계약 copy·공유 대상 자동 선택 | 정상 보호 또는 필수 범위 제외. 미구현으로 확대하지 않는다. |

M4/M12·고정 ABI 잔여·B2 다른 사용자/그룹 권한 backend·종류 C# 표현/사용 중 삭제 대응·3D와 권한 별도 팩은 별도다. 3D 이동은 실행 선행 조건이 아니다. 이번 단위는 전체 M11·전체 UI 완료가 아니다.

## 검증 기록

생성한 fixture만 사용하며 실행 소스·입력·결과·스크린샷과 실패 진단을 보존한다. UI 전에는 브라우저의 whole-body 경계 가드와 번들을 순차 갱신했다. API 단계에서 쓰지 않는 브라우저 자산만 바뀌었고 native 저장소 코드는 동일하다. 갱신 두 단계의 결과는 대기 전 controller의 오래된 상태 기록을 복구하기 위해 원래 result/completion 파일의 SHA·종료/자식 회수를 확인해 관리 record에 되돌렸으며 재실행이나 추정 통과로 세지 않는다.

## 최종 결과

실행 코드 commit은 `2ab948e69dcacd543320ede92eb059a1434fcb87`다. 최종 소스의 새 독립 LF **18단계**, CRLF **16단계**, 새 Windows 교차 패키지·전체 압축 복원·실패 수명관리 **8단계**, 총 **42단계**가 통과했다. 양쪽 checkout에서 기존 native 저장소/문맥 compiler **각 11개**, 소유/상속 보호 **각 2개**도 skip·실패 없이 통과했다. 이전 저장 copy 값/중첩 단위의 48단계는 이력 참고로 유지하며 이번 소스에서 모두 재실행했다고 합산하지 않는다. 기존 suite의 검사를 삭제하지 않고 이번 변경의 영향 suite를 추가했다.

신규 copy 저장소 API는 Root caller 전달·private/local 출력·out-only·배열 교체·예외 전 쓰기를 해당 fixture에서 실제 CLR 실행으로 비교했다. 같은 변수/서로 다른 변수의 alias와 반환/out 순서를 변환 전후 확인했다. out 미할당 본문은 CS0177로 거절하고 실패한 입력과 물리 원문을 보존한 뒤 명시 수정으로 복구했다. 잘못된 owner·bare/donor 재지정·공개 계약 변경·부분 Review·Review 이후 원래 C# 경합도 거절했다. 반복 저장 receipt·cold·원자 Confirm은 copy ID·출처·공개 계약·원문/helpers·기존 저장소/실행/값 연결을 유지한다.

최종 LF는 일반 ref/out 화면의 정상 저장·private/local 독립 창 쓰기 실패·기본 화면 원문 충돌을, CRLF는 응답 유실·private/local 독립 창 늦은 입력을 새로 실행했다. 기본/독립 창의 C# 고정 ref/out 선언·취소·Undo/Redo·cold·Root Save·Review 취소/Confirm과 실제 편집 결과를 확인했다. 기존 값 입력 copy API는 LF Root·CRLF 중첩 경로에서, 공통 선언/헤더·원문 편집 회귀는 양쪽에서 새로 검사했다. 생성 패키지는 ref/out 정상 흐름, 전체 복원본은 private/local 독립 창 응답 유실을 새로 실행하고 기존 직접 소유 일반/쓰기 실패 화면도 확인했다.

집중 검증의 private/local 프로젝트 왕복·기본/독립 화면과 공유 copy 보호는 해당 단계의 소스 및 최종 실행 입력을 대조한 별도 증거로 유지하며 42단계에 합산하지 않는다. 이번 단위가 생성 중 copy·whole-body/실행 분기 copy·상속/참조·기존 profile 재활성화 전체를 닫지는 않는다. 최종 실행 중 환경 연결 알림 뒤에도 같은 VM의 원래 runner·RAM root·로그가 살아 있었고 검사를 중복하지 않았다. 터미널 핸들은 소실되어 관리 record·원래 완료/결과 파일과 마지막 passed 로그로 결과를 회수했다. 새 정책 결정은 필요하지 않았다. 실제 Windows apphost/WebView2·모바일 기기·DPI/IME·전체 UI·Library/Space 전달은 미실행이다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/fbaf0b735bcb433bab1aff3d7237b1d8.json` (42단계, cleaned).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/fbaf0b735bcb433bab1aff3d7237b1d8.zip`, SHA-256 `63ccded7b653ac91a1987ef4519cbb8b7c5d532ac7bdf2dfad5ced42d58a5bd4`.
- 집중 record: `/workspace/artifacts/v536-verification-managed/runs/7a2fd07d35294a0e91828c34998fbb25.json`, 증거 `/workspace/artifacts/v536-verification-managed/runs/7a2fd07d35294a0e91828c34998fbb25.zip`, SHA-256 `6723457908d889324a85ab8c7dde1344c4e6322e94094502f7d3203d504ac6a1`.

| 지속 보관본 | 코드 commit | ZIP SHA-256 | bytes | 전체 manifest SHA-256 |
|---|---|---|---|---|
| 최신 | `2ab948e69dcacd543320ede92eb059a1434fcb87` | `ad5f2783f2bd9486cfed273a08ee22f1c294b0c8b74dbc9e73c49b5570ca723c` | 51,263,257 | `17ea4cde5a8e8b189105e188eb69d93c79abe27ddc11922c9549661e2e042914` |
| 정상 롤백 | `51bab27cdfdab54ad384580ea12f8e6f08671833` | `ccdee4ac07b5481305d03e98273901042b5fc1cc5d17113b948665dbbc612570` | 51,263,161 | `2738d9922eeffb214f93bcdefe069e3bfd28372b3de1f6df6df2c1a43033f093` |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 최종 코드에서 새로 생성하여 전체 SHA/CRC/파일·디렉터리 모드를 복원하고 복원본을 실행했다. 롤백은 앞선 정상 검증 증거를 재사용하고 ZIP SHA를 재확인했다. 최신 2363파일·147디렉터리 / 롤백 2363파일·147디렉터리. 이후 결과 보고 commit과 실행 코드의 차이는 문서뿐이며 보고 commit에서 다시 패키징했다고 주장하지 않는다.

집중 여유 2047.01→2044.01 MiB, 최종 여유 2043.71→2039.21 MiB였다. 최종 순증가 **4.50 MiB**, 단계 샘플 최소 2043.66 MiB, cgroup 메모리 피크 4875.51 MiB였다. 기존 추가 디스크 예산 144 MiB(안전 여유64 MiB 포함) 및 RAM/메모리 기준을 낮추지 않았다. 집중/최종 소유 임시 root는 증거를 검증·보관한 뒤 정리했고 승인된 최신/롤백 회전 외 과거 자료를 삭제하지 않았다. 이번 순증가는 미래 보장값이 아니다.
