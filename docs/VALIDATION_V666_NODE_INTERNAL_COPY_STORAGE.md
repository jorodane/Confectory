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

최종 코드·집중/독립 LF·CRLF·새 패키지/전체 압축 복원·수명관리 결과를 신규/재사용/미실행으로 구분해 기록한다. 생성한 fixture만 사용하며 실제 Windows apphost/WebView2·모바일 기기·DPI/IME·Library/Space 전달과 교차 패키지를 구분한다.
