# C# import로 연결한 함수의 반환 계약·본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 다음 단위는 [scalar 입력 import 결합](V666_NATIVE_CHAIN.md)에 이어 두 직접 소유 함수의 반환 계약을 함께 바꾸는 흐름이다. 첫 C# 구현이 둘째 함수를 호출하며 두 함수의 long 반환을 double로 명시 선택한다. 공개/원래 native 입력과 out long count를 유지하고 기존 long 반환 소비자는 사용자가 count에 명시 대응한다. 두 C# 본문은 직접 작성한다. 원래 실제 반환42/40·out35/34·공유 caller52, 편집 후 double1.75/1.25·out38/34·명시 대응된 caller42가 이 단위의 기준이다.

기존 InformationFunctionNativeReturns의 원래 source·before/native signature·호환 out 소비 선택 검증을 유지한다. 내부 request-local joint 문맥을 이 기존 반환 계획에도 연결하고, 원래 caller 출력 계획을 기존 overlay의 합성에 사용한다. 선택된 미래 public/native import 계약만 컴파일 사전에 제공하며 source text를 변환하지 않는다. 모든 행은 원래 소스와 hash를 검증하고 native header/body는 최종 결과까지 staging하지 않는다. 같은 source의 결과는 byte 동일해야 한다.

저장 뒤 header/graph 발견과 후속 표시 Save는 기존 scalar 입력 또는 반환 전환인지와 캡처된 function/body/header hash, 원래 헤더에서 명시 signature/import만 바뀐 정확한 bytes를 확인한다. 새 JSON 우회 플래그·receipt 필드나 버전은 없다. 기존 source/read240·member64, 소유권·권한·Review/Confirm·최종 CAS를 유지한다. 원래 helper header/body는 읽기 관측이며 쓰기 대상이 아니다.

범위는 직접 소유 동기 함수2~8개·함수당 단일 C# target·기존 scalar 반환 계획·ordinary shared Blueprint caller다. 유효한 단독 편집에서 변경하지 않은 callee의 원래 계약을 사용하는 동작도 보존한다. 선택한 본문 누락·C# 반환/호출 오류·stale hash·호환하지 않는 소비 대응·임의 입력/out identity 변경·혼합 역할은 거절한다. 외부 반환 계약 수정·새 등록/권한·역할 전환·고급 타입·private/whole/상속·override 문맥으로 확대하지 않는다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

이 실제 반환/호출 흐름의 종료 기준은 원래 프로그램 재현, 순서 독립적 공동 후보와 명시 출력 소비·거절 검사, 기존 상세/타입/own source UI의 취소·Undo/Redo·cold·Save 실패/재시도·응답 유실·프로젝트 왕복·늦은 입력/두 번째 Save, 원본 경합·후속 metadata Save와 Review/Confirm·CAS, LF/CRLF 및 새 package/전체 ZIP 복원이다. 기존 반환 및 이전 입력 import 경로를 회귀로 구분하며 모든 타입/문맥 조합을 새 의무로 늘리지 않는다.

구 reader 수용은 intact package와 새 pending guard의 실제 진단으로 구분한다. 자동 migration/downgrade나 구 Reference parser 변경은 없다. 실제 Linux .NET/portable 실행·Chromium 자동화와 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI를 구분하며 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.

이 단위는 [최종 신규41·재사용0 검증](VALIDATION_V666_NATIVE_RETURN_CHAIN.md)을 마쳤다.
