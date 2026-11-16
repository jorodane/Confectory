# 선택 C# import 함수의 입출력 혼합 전환

고정 v666 정보7/8행의 원래 상세창 입출력 편집과 명시 C# 본문을 한 후보/최종 CAS에
연결한다. [참조 입력](V666_NATIVE_REFERENCE_INPUT.md)·[참조 반환](V666_NATIVE_REFERENCE_RETURN.md)의
함수별 원본 scope·타입 proof와 [typed reference ABI](V666_TYPED_REFERENCES.md)를 유지한다.

유한한 종료 기준은 Main→선택 A→선택 B의 네 명시 선택·세 고유 source에서 다음 원래
흐름을 저장·실행하는 것이다. 단순 조합별 매트릭스를 새 필수 목록으로 늘리지 않는다.

- A의 반환 전환과 B의 입력 전환을 결합한다. A가 실제 객체를 명시 Bind해 만든 같은 배열을
  B가 받아 셀40→71을 바꾸고73을 반환한다. A가 같은 셀에73을 기록해 배열을 Main에 반환한다.
- A의 입력 전환과 B의 반환 전환을 반대 방향으로 결합한다. A는 두 경계의 독립적인 실제
  객체를 명시적으로 읽고 쓴다. 같은 handle로 병합하거나 값을 자동 변환하지 않는다.
- A에서 입력·반환을 동시에 바꾸고 B의 반환과 결합한다. A가 받은 원래 배열을 그대로
  Main에 반환하며 실제 Target/셀·배열 동일성·원소 순서를 확인한다.
- 같은 계약 경로의 단일 정보 값에서는 B의 값 복사가 A의 원래 값을 바꾸지 않으며,
  A가 직접 작성한 반환값73만 Main이 소비한다.

모든 함수는 원래 scalar 값 계약에서 이미 지원된 정보 값·정보 참조의 단일/일차원 배열로
명시 선택한다. 변경하지 않은 입출력, 인자 수·순서·이름·값 역할, public amount/native
nativeAmount, Main ABI와 import alias는 유지한다. 한 함수의 입력·반환 동시 선택도 각각
원소 타입 proof가 필요하다. 다른 scalar 타입으로의 동시 변경·새 역할/핀·부모/override·
async 변환을 추론하지 않는다. sync caller의 기존 오류 정책도 유지한다.

그룹 전체의 방향 제한 대신 각 함수의 정확한 before/after·원래 pin mapping을 독립적으로
검증한다. 한 source를 두 scope가 공유하면 원래 hash·최종 본문·native signature가 정확히
같아야 한 번만 결합한다. read240/member64/type64와 기존 등록 receipt/read set, 전체 본문
계획·컴파일·Review/Confirm·최종 CAS를 유지한다. 새 schema/profile/receipt 필드는 없다.
타입 선택이 binding·객체/provider 생성·ID lookup·자동 C# 재작성을 수행하지 않는다.

등록 외부 정보 입력과 소유 정보 반환의 다른 view도 같은 실제 handle을 사용자가 명시
Bind하는 경우만 확인한다. 외부 선언은 읽기 관측이며 새 권한·외부 쓰기는 추가하지 않는다.
null·빈 배열·default/unbound도 직접 작성한 C#이 그대로 전달한다. 배열과 carrier의 기존
CLR 의미를 따르며 수명 registry·소유 이전·암묵적 변환을 추가하지 않는다.

원래 타입 선택기와 C# 편집기의 이름/readonly 선언, 취소·Undo/Redo·정상/역순 재개방·cold·
쓰기 실패/재시도·응답 유실·늦은 입력·프로젝트 격리·후속 Save를 검증한다. CSS/배치와
원본 C# bytes를 유지한다. jagged 배열·새 private/whole 문맥과 구 reader 전체 UI 교환을
완료로 세지 않는다. 실제 Windows/기기·전체 UI는 미검증이고 초기 빈 화면 원인은 미확정이다.
자동 migration/downgrade는 없으며 최종 결과는 [검증 기록](VALIDATION_V666_NATIVE_IO_MIXED.md)에 구분한다.

이 유한 흐름은 [신규48·재사용0 최종 검증](VALIDATION_V666_NATIVE_IO_MIXED.md)을 마쳤다.
