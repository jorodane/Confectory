# C# import로 연결한 함수의 값→ref 계약·본문 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 다음 단위는 두 직접 소유 함수의 같은 값 입력을 ref로 명시 전환하는 흐름이다. 첫 C# 구현이 둘째 함수를 import로 호출하며 사용자가 호출부에 ref를 직접 작성한다. 기존 공유 Blueprint caller의 ref 입력 셀을 두 함수의 동일 입력에 명시 연결한다. 원래 실제 caller 반환46·셀5, 편집 후 반환79·셀79가 이 단위의 기준이다. 공개 amount/count 이름과 nativeAmount/nativeCount 별칭, 순서·타입·반환·원래 helper 계약을 유지한다.

기존 InformationFunctionNativeRoles의 방향·입력/출력 대응·원래 before/native signature·source hash 검증에 request-local joint 컴파일 문맥을 연결한다. 선택된 함수의 미래 계약을 컴파일 사전에 함께 제공하고 원래 caller 출력 대응을 기존 overlay 합성에 사용한다. 사용자가 검토한 둘째 본문이 원문과 같아도 기존 atomic proof의 읽기 멤버로 유지하며 물리 파일은 다시 쓰지 않는다. 그래서 둘째 C# 본문의 BOM·CRLF를 보존한다. 첫 본문의 ref 호출은 직접 작성한 텍스트이며 생성·추론한 source rewrite가 없다. 부분 native header/body staging도 없다.

후속 metadata Save·cold/header/graph 발견은 선택한 함수 모두의 동일 역할 전환 방향, 원래 public 입력/반환 identity와 native 별칭·타입·순서, 캡처된 function/header/body hash, 명시 signature/import 외 헤더 bytes를 검증한다. 변경 방향 혼합·별칭 변경·캡처 변조를 거절한다. 새 JSON bypass·receipt 필드/버전·권한/등록은 없다. 원래 helper는 읽기 관측이고 기존 source/read240·member64, 소유권·Review/Confirm·최종 CAS를 유지한다.

범위는 직접 소유 동기 함수2~8개·함수당 단일 C# target·기존 scalar 역할 계획·ordinary shared Blueprint caller다. 이 단위의 실제 종료 기준은 원래 실행 재현, 순서 독립 공동 후보·명시 ref 저장소와 호출부·부적합 입력/출력·partial/stale/hash 거절, 기존 UI의 취소·Undo/Redo·cold·Save 실패/재시도·응답 유실·프로젝트 왕복·늦은 입력/두 번째 Save·원본 경합·후속 metadata Save 및 Review/Confirm·CAS, LF/CRLF·새 package·전체 ZIP 복원이다. 기존 값→ref와 반환 import 흐름은 별도 회귀로 검증한다. 다른 역할 방향·고급 타입·async/private/whole/override·외부 계약 변경의 지원을 이 흐름의 결과로 대신하지 않는다.

정보별 struct·종류 enum·모듈 interface, 명시 async 전환 전 sync caller 오류를 유지한다. 구 reader의 pending 수용은 온전한 이전 package에서 따로 측정하며 migration/downgrade하지 않는다. Linux .NET/portable 실행·Chromium 자동화와 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI를 구분한다. 초기 빈 화면 원인은 미확정이며 main은 사용자 검토/merge에 남긴다.
