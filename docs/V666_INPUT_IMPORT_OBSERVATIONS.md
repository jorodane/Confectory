# 입력 계약 변경과 기존 import 관측의 공동 저장

고정 [7/8행](V536_I5_6_REMAINING.md)의 한 정보 창에서 직접 소유 함수 둘의 실제 입력 타입·native C# 본문·공유 caller 대응을 명시하고, 기존 로컬/등록 helper import의 원래 관측과 한 Save로 결합하는 흐름이다. [필수 retained 계획 결합](V666_RETAINED_CODE_PLANS.md) 다음으로 실제 계약 변경과 등록 외부 읽기의 결합을 다룬다. 원래 소스 선택·상세창·타입 선택·본문 편집·정보 Save를 그대로 사용한다.

게시 기준에서 long→string 입력, 수동 본문과 명시 caller 값/기존 바인딩 해제 계획은 각각 단일 함수 후보로 유효했지만 두 함수를 함께 저장하면 거절됐다. 원래 프로그램 실행79도 확인했다. 한 함수는 소유 helper, 다른 함수는 등록된 helper와 그 부모 계약을 사용한다. 두 본문과 caller 값을 직접 작성한 뒤 실행27을 확인하는 것이 이번 한 흐름의 종료 기준이다.

기존 직접 소유 동기 native 입력 그룹2~8개·구현당 단일 target·ordinary Blueprint caller·원래 scalar 입력 계획을 유지한다. NativeInputs는 기존 선택적 dependencies 필드를 분류하고, 원래 InformationFunctionDependencies의 등록 proof·선언/부모 관측을 읽기 전용 계약 사전에 연결한다. 각 원래 단일 함수 계약·C#/호출·proof 검증은 그대로 수행하며 내부 overlay만 공유 caller를 합성한다. 외부 선언은 owned units/write group에 넣지 않는다. import 별칭·typed signature·helper 계약과 provider 본문을 자동 변경하지 않는다.

기존 version3 nativeBodyDependencies/nativeBodyDependencyReads와 소유 readGuards·Review/Confirm·최종 CAS를 재사용한다. 외부 함수·부모·등록 manifest와 소유 helper 관측은 원래 읽기 범위로 유지한다. provider 구현/본문은 등록 계약 조회의 관측 대상으로 확대하지 않는다. 후속 metadata Save·cold·늦은 입력/두 번째 Save는 원래 proof/read set을 이어받으며 현재 외부 파일을 새 기준으로 재수락하지 않는다. 읽기+쓰기240, 기존64-member/소유권·권한·source 예산을 유지한다.

완료 기준은 이 실제 계약 변경 흐름의 단독/공동 후보·순서 독립성·원래 source hash·타입/body/caller/등록 proof 거절, UI 취소·Undo/Redo·cold·checkpoint 실패/재시도·응답 유실·프로젝트 왕복·늦은 입력/후속 Save, 외부 선언/부모/등록 및 소유 helper의 최종 Confirm 경합이다. LF/CRLF 격리 restore/build, 새 package와 전체 ZIP 추출본을 검사하며 기존 입력 계약과 같은 계약 등록 본문 경로를 회귀로 구분한다. 새 타입별 조합을 완료 의무로 늘리지 않는다.

선택 함수의 native 구현이 다른 선택 함수의 변경되는 계약을 import하는 결합은 별도 유한 잔여다. 이 경우에는 실제 C# 호출과 import 계약을 함께 명시해야 하며 기존 callee+consumer 거절을 임의로 해제하지 않는다. opaque/private/whole 또는 override 계약 제한도 이번 입력/관측 경로로 바꾸지 않는다. 외부 계약 수정·새 등록·접근권한·C# 변환·암묵적 blocking/async 전환·새 schema/receipt version은 추가하지 않는다. 정보별 struct·종류 enum·모듈 interface를 유지한다.

이전 reader의 새 pending 후보 수용 범위는 실제 진단 결과와 구분해 기록한다. 자동 migration/downgrade와 구 Reference parser 수정은 없다. Linux 실제 엔진/portable 실행·Chromium 자동화와 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI를 구분하며, 과거 간헐 초기 빈 화면 원인은 미확정이다. main은 사용자 검토/merge에 남긴다.

최종 결과는 [검증 기록](VALIDATION_V666_INPUT_IMPORT_OBSERVATIONS.md)에 남긴다.
