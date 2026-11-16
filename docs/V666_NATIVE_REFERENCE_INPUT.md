# 선택 C# import 함수의 정보 참조 배열 입력

고정 v666 정보7/8행의 기존 함수 계약·본문 결합을 원래 정보 참조/여러 개 선택에 연결한다.
사용자가 결정한 정보별 C# 구조체와 [typed reference 계약](V666_TYPED_REFERENCES.md),
[정보 배열 입력](V666_NATIVE_ARRAY_INPUT.md)의 명시 계획·한 후보/최종 CAS를 따른다.

종료 기준은 Main→선택 A→선택 B의 두 scalar 입력을 같은 정보의 readonly 참조 struct
배열로 바꾸고, 네 명시 선택으로 세 고유 C# 원문을 정확히 저장·실행하는 한 흐름이다.
기존 public 인자 `amount`, native 별칭 `nativeAmount`, scalar 반환, Main ABI, import 별칭,
인자 수·순서·값 전달 역할을 유지한다. 단일 참조 입력도 같은 원소 proof 경로를 사용한다.

Main의 직접 작성한 C#은 기존 ObjectModel의 실제 인스턴스 두 개를 만들고 정확한 계약으로
`Bind`해 배열에 넣는다. A의 checked Read/Set과 B의 Read가 같은 handle/셀을 관측한다.
배열 순서·동일성과 원래 참조 carrier의 Target/Owner를 유지하며 `null`, 빈 배열, `default`
carrier를 객체나 editor 기본값으로 정규화하지 않는다. 정보 ID 조회·자동 binding·provider
선택·소유 이전·암묵적 변환은 없다. 복사한 carrier의 기존 CLR strong reference/GC 수명이다.

기존 각 함수의 원소 타입 proof와 원본 출처 관측을 검증하고 배열 여부는 함수·native 선언과
captured source에 결합한다. 기존 ObjectModel import의 함수별 등록 receipt와 읽기 관측도 기존 dependencies 필드로
그대로 검증한다. 같은 소스의 두 명시 계획은 원래 hash와 최종 원문이 정확히
같을 때만 한 번 결합한다. 등록 외부 정보의 참조 입력도 별도 원래 proof가 필요하며,
사용자 C#이 같은 실제 handle을 다른 적용 정보에 명시적으로 Bind하는 경우만 검증한다.
Owner는 접근 주소이며 이 편집이 새 권한을 부여하지 않는다. 외부 원본 쓰기는 없다.

원래 함수 상세창의 정보 참조와 여러 개 선택, C# 선언의 native 이름을 연결한다. 본문은
사용자가 직접 작성하고, 취소·Undo/Redo·재시작·저장 실패/충돌·응답 유실/늦은 입력·후속
metadata Save는 기존 receipt/Review/Confirm 경계를 사용한다. 새 profile/receipt 필드,
권한·화면 배치·CSS·공개 override·async 정책 변경은 없다.

참조 반환과 입출력 혼합 전환은 이 단위 밖의 기존 잔여다. jagged 배열은 거절 경계로만
검사하며 필수 조합 목록으로 추가하지 않는다. private/whole·override·비소유 쓰기의 기존
제한을 확대하지 않는다. 구 reader의 Reference 타입 거절, 실제 Windows/기기·전체 UI와
초기 빈 화면 원인 미확정도 유지한다. 검증과 게시 결과는
[검증 기록](VALIDATION_V666_NATIVE_REFERENCE_INPUT.md)에 구분한다.

이 유한 흐름은 [신규47·재사용0 최종 검증](VALIDATION_V666_NATIVE_REFERENCE_INPUT.md)을 마쳤다.
