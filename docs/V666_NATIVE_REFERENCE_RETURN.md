# 선택 C# import 함수의 정보 참조 반환

고정 v666 정보7/8행의 명시 계약·본문 결합에 기존 정보 참조·여러 개 반환 선택을 연결한다.
[정보별 참조 ABI](V666_TYPED_REFERENCES.md)와 [참조 입력](V666_NATIVE_REFERENCE_INPUT.md),
[기존 배열 반환](V666_NATIVE_RETURN_ARRAY.md)의 원소 증거·한 후보/최종 CAS를 따른다.

종료 기준은 Main→선택 A→선택 B에서 두 scalar 반환을 같은 정보별 readonly 참조 struct
배열로 바꾸고 네 명시 선택·세 고유 C# 원문을 저장·실행하는 한 흐름이다. scalar 값 입력,
public `amount`·native `nativeAmount`, 입력 수/순서/역할, Main ABI와 import alias를 유지한다.
같은 원소 proof 경로의 단일 참조 반환도 확인한다. 입력/반환 혼합 전환은 별도 잔여다.

직접 작성한 B 본문이 기존 ObjectModel 실제 인스턴스 둘을 만들고 정확한 정보 계약으로
명시 Bind한 carrier를 반환한다. A는 같은 Target/Owner와 셀을 checked Read/Set으로 읽고
변경한 뒤 같은 배열을 Main에 반환한다. Main은 실제 셀73·둘째 셀1, carrier 사본의 Target,
배열 길이/순서와 다른 두 객체를 확인한다. caller가 carrier를 보유한 채 GC를 수행해도
기존 CLR strong reference 의미를 유지한다. null·빈 배열·default/unbound 반환도 원래대로
전달하며 객체 생성·ID lookup·provider 선택·자동 binding/변환·소유 이전을 추론하지 않는다.

원래 함수별 source scope, 원소 CLR 타입 proof, 등록 ObjectModel import receipt와 read set을
독립적으로 검증한다. 배열 여부는 공개/native 선언과 capture에 결합하고 같은 source를
두 계획이 공유하면 원래 hash·최종 원문이 정확히 같아야 한 번만 반영한다. 등록 외부
정보 반환은 별도 proof와 사용자가 직접 작성한 Bind를 사용한다. 다른 적용 정보의 view도
같은 실제 handle을 명시 Bind하는 경우이며, Owner는 접근 주소일 뿐 새 권한이 아니다.
외부 선언은 읽기 관측이며 쓰기 대상이 아니다.

원래 함수 상세창의 참조/여러 개 반환 선택, readonly C# 선언과 native 인자 이름을 연결한다.
본문을 자동 변환하지 않고 취소·Undo/Redo·정상/역순 재개방·cold·저장 실패/재시도·응답
유실·늦은 입력·프로젝트 격리·후속 Save·Review/Confirm·최종 CAS의 기존 경계를 유지한다.
새 schema/profile/receipt 필드·권한·CSS/배치·공개 override 또는 async 정책은 만들지 않는다.

jagged 배열은 거절 경계이며 새 필수 조합으로 추가하지 않는다. 입력/반환 혼합과 기존
opaque/private/whole·비소유 쓰기 범위는 이 단위의 완료로 세지 않는다. 구 reader의 새
pending 수용은 별도 측정하고 자동 migration/downgrade하지 않는다. 실제 기기·전체 UI와
초기 빈 화면 원인은 각각 미검증·미확정으로 유지한다. 최종 결과는
[검증 기록](VALIDATION_V666_NATIVE_REFERENCE_RETURN.md)에 구분한다.

이 유한 흐름은 [신규47·재사용0 최종 검증](VALIDATION_V666_NATIVE_REFERENCE_RETURN.md)을 마쳤다.
