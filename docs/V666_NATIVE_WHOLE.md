# 단일 코드 whole-body의 명시 고급 ABI 전환

고정 [정보 편집9행](V536_I5_6_REMAINING.md)의 정보 struct·종류 enum·모듈 interface
선택과 기존 [전체 C# 본문 계약](V536_I5_6_WHOLE_CONTRACT_SCOPE.md)의 명시 매개변수/본문
계획을 연결한다. 원본 v666 `dist/app.js::choosePropertyType`와 `blueprint.js`의 개별 동작
내부 흐름 진입을 따른다. 원본 ZIP SHA256은
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.

이번 지원은 직접 소유한 일반 동기 함수의 정확한 single-code whole-body lift다. 기존
C# 문맥 노드와 반환 writer만 있는 원래 구조를 증명하고 함수 입출력의 고급 타입, C#의
매개변수·반환 서명과 직접 작성한 본문, 영향받은 일반 C# 호출자 계획을 한 후보에 저장한다.
원래 whole-body 계약으로 공개/실제 native 매개변수의 이름 차이를 유지하고 각 위치의
타입·역할을 정확히 확인한다. 원래 노드/핀/entry/반환 writer/연결/좌표/소유/권한을 보존한다.

C# 편집기의 밝은 매개변수 영역은 기존 단일 식별자/배열과 생성된 canonical nominal
타입명을 인식한다. 다른 점 구분 타입명을 임의로 허용하거나 타입 선택 권한을 추가하지
않는다. 실제 서명은 선택한 공개 계약과 backend에서 다시 비교한다. 본문을 자동 변환하거나
새 출력·동작·형변환을 추정하지 않는다. 기존 변환 전 `.csbody` 보관 파일은 다시 쓰지 않고,
새 본문은 명시 선택한 기존 node record에만 적용한다. helpers나 별도 private 문맥은 이
최소 단위에서 새로 변환하지 않는다.

`native-information-function-whole-lift-v1`은 기존 header/manifest/graph/code 읽기 증거와
whole-body graph ID를 같은 v2 보호 초안에 결부한다. 기존 scope hash/문법은 유지한다.
원본 읽기 검증은 **물리 원본** 구현의 C# 문맥과 비교한다. 저장 후 새 헤더가 draft overlay로
보이더라도 원본 그래프와 혼동하지 않는다. 완성한 새 후보의 문맥·서명·원문은 별도의 순수
컴파일, compiler Review/Confirm·최종 CAS에서 검증한다. 이전 헤더나 code bytes가 바뀌면
기존 읽기 증거로 저장/확정하지 않는다. 보호를 빼거나 source hash를 새 값으로 자동 수락하지 않는다.

종료 기준은 위 정확한 whole-body에서 struct 입력/반환의 명시 source 계획을 원래 UI로
저장·복원·컴파일·실행하고 누락/오류/취소/Undo/Redo/재시작/충돌/응답 유실/늦은 입력을
검증하는 것이다. 별도 원문·등록 외부 타입·부모/참조 원본과 override 계약은 유지한다.
독립 code 노드 자체의 서명, private·독립 동작/별칭이 있는 retained whole 그래프,
copy/상속/참조 전환을 이 단위에 일괄 승격하지 않는다. M11/M12/M4를 새 회귀 없이 다시 열지 않는다.

살아 있는 참조의 객체/접근자·수명, 모듈 async/공개 실행 결과의 계약-only closure/DLL 순환,
multiple/함수 필드 native 생성은 같은 유한 잔여다. 선언 ID/$ref를 값 snapshot으로 바꾸지
않고 동기 호출자는 명시 async 전환 전 오류라는 확정 정책을 유지한다. 이번 전환에 추가
사용자 결정은 필요하지 않다. 구 nominal/enum parser·reader 비호환과 이전 scope의 거절,
자동 migration 없음은 유지한다. 실제 Windows/모바일·전체 UI는 미검증이고 초기 빈 화면
원인은 미확정이다. 원본·latest/rollback·증거의 기존 보관/정리 규칙을 유지한다.

이 한정 범위의 [최종 신규45단계·재사용0 검증과 보관](VALIDATION_V666_NATIVE_WHOLE.md)을 마쳤다.
