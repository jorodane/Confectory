# 고급 입력 계약과 공유 C# 호출자 공동 저장

[고정 7/8행](V536_I5_6_REMAINING.md)의 다음 한 흐름은 같은 정보의 두 함수 입력을 기존 명목 타입으로 바꾸면서, 두 함수를 호출하는 하나의 C# 본문을 명시 작성해 함께 저장하는 것이다. 기존 [겹치지 않는 타입 전환](V666_NATIVE_TYPE_GROUP.md)의 함수별 타입·출처 proof를 유지한다. 두 구현과 공유 호출자라는 세 소스에 네 명시 선택 계획이 대응하며, 공유 소스는 같은 원래 경로·해시·before/after 선언·직접 작성한 text여야 한다. 원래 실행70과 새 실행73이 기준이다.

컴파일 사전에 모든 명시 선택의 미래 함수 계약과 검증된 타입 헤더를 읽기 전용으로 제공한다. 공유 호출자는 원래 ABI를 유지하며, 각 함수의 원래 소스 계획을 따로 검증한다. 공유 계획에서 다른 함수의 contract만 재사용하거나 source text를 추측·변환하지 않는다. contract 항목은 해당 함수별로 검증하고, 같은 소스의 나머지 계획이 다르면 전체 거절한다. native header/body는 마지막까지 기존 내부 buffer에 두며 같은 후보 결과만 한 번 합친다.

직접 소유 동기 함수2~8개·기존 scalar 값 입력→명시 선택한 nominal 단일 타입·원래 인자 이름/순서/역할·scalar 반환과 기존 직접 C# caller 범위다. 서로 호출하는 선택 native 함수, reference/array 인자·out/ref·async·반환 구조 변경·private/whole/override·별도 소스 ID의 같은 물리 경로는 분리 차단한다. 외부 타입은 원래 등록/의존성의 정확한 선택 proof로만 읽고, 여러 선택의 읽기 증거가 다르면 거절한다. 외부 header/manifest는 쓰기 대상이 아니다.

저장 후에는 기존 함수별 type scope와 캡처된 function/header/body hash, native 인자 별칭·caller ABI, 원래 import alias·명시 signature 외 header bytes를 확인한다. 후속 owner/function metadata Save·cold 발견·Review/Confirm·최종 CAS에도 같은 검사를 쓴다. 새 receipt 필드·버전·권한·등록이 없고 version2 workspace/version3 slot receipt·read240/member64를 유지한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류, 원래 UI/layout을 보존한다.

이 단위의 유한 종료 기준은 원래 실행·이전 planner 거절 재현, 순서 독립 후보·충돌하는 공유 계획·누락/교차 proof·소스/선언 변조 거절, 기존 UI의 두 선택·네 명시 계획·세 소스·취소/Undo/Redo/cold·쓰기 실패/응답 유실/늦은 입력/프로젝트 왕복, metadata Save·Review 후 caller/type 경합·새 Confirm, 서로 다른 소유/등록 타입의 읽기 경계, LF/CRLF·새 package·전체 ZIP 복원이다. 기존 disjoint·단일 nominal·incremental 경계와 역할 import는 별도 회귀로 구분하며 문맥별 무한 조합을 새 의무로 늘리지 않는다.

선택 함수 간 고급 import·고급 반환·reference/array·private/whole/override 결합은 별도 고정 잔여다. 구 reader의 pending 수용은 온전한 이전 package에서 실제 측정하며 자동 migration/downgrade하지 않는다. Linux .NET/portable 실행·Chromium 자동화와 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증을 구분한다. 초기 빈 화면 원인은 미확정이며 main은 사용자 검토/merge에 남긴다.

이 단위는 [최종 신규43·재사용0 검증](VALIDATION_V666_NATIVE_TYPE_SHARED.md)을 마쳤다.
