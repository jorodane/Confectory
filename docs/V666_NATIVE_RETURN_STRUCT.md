# 함께 변경하는 C# import 함수의 정보 값 반환

[고정 7/8행](V536_I5_6_REMAINING.md)의 다음 유한 단위는 Main→선택 A→선택 B에서 두 함수의 scalar 반환을 기존 선택기의 정보별 C# 구조체 단일 값으로 바꾸고, 두 구현과 소비자 Main의 본문을 명시 작성하여 공동 저장하는 흐름이다. 원래70·편집73을 실제 실행 기준으로 둔다. 함수별 네 선택은 세 고유 source이며 A의 자기 계획과 B caller 계획은 같은 원래 path/hash/before/after 선언/text를 인증한다.

입력의 이름·수·순서·자료형·값 역할은 그대로 둔다. 기존 nominal 입력 전환 모드와 이 반환 전환 모드를 구분하고, 이번 범위에서 한 그룹은 한 방향을 유지한다. 입력 전환과 반환 전환을 섞거나 한 함수의 입력/반환을 동시에 바꾸는 계획은 입력을 보존하며 거절한다. 이는 이번 지원 경계이며 복합 편집 전체를 영구 금지하는 새 정책이 아니다. void·ref/out·참조/배열 반환·async·private/whole 결합은 별도 구현/검증 범위다. 오버라이드 공개 계약 구조 변경은 기존 금지 정책을 유지하고 외부 수정 권한을 확장하지 않는다.

기존 내부 미래 함수/타입 사전·명시 source buffer·원래 import alias와 native 입력 별칭·미선택 Main ABI·함수별 source/type proof를 유지한다. C# source를 추측·변환하거나 caller를 자동 변경하지 않는다. 반환만 바꿀 때 기존 코드 편집기는 원래 native 입력 별칭을 유지한 선언을 표시하고, 보관된 readonly 인자 draft가 이 선언을 덮지 못하게 한다. 공개 입력명과 C# 입력 별칭이 다른 실제 경로도 검증한다. 각 선택은 자기 원래 증거를 검증하며 공유 source의 최종 결과가 같을 때만 한 번 합친다. 저장 후에도 before/after의 한 방향과 정확한 캡처 hash/선언/import delta를 검사한다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류, version2 workspace/version3 receipt·native-type-source-guards-v1·read240/member64/type64·Review/Confirm·최종 CAS를 유지한다.

종료 기준은 원래 실행/이전 planner 거절·순서 독립 후보, 누락/교차 type/source proof·상충 A 계획·잘못된 C#·혼합 방향 거절, 원래 반환 선택 UI의 취소/Undo/Redo·정상/역순 재개방·cold·쓰기 실패/재시도·응답 유실·늦은 입력·프로젝트 전환, 후속 설명 저장·Main/A/type의 Review 후 충돌과 새 Confirm, 서로 다른 소유/기존 등록 구조체 반환의 readonly 경계, LF/CRLF·새 패키지/전체 ZIP 복원이다. 기존 nominal 입력/shared caller·단일 타입/증거 경계·scalar 반환 그룹은 회귀로 구분하며 무한 타입 조합을 새 요구로 늘리지 않는다.

이번 실제 반환은 정보별 구조체 값이다. enum/interface 반환, 참조/배열 및 기타 복합 반환 조합 전체를 검증 완료로 분류하지 않는다. 구 reader의 새 pending 수용은 온전한 이전 package에서 측정하며 자동 migration/downgrade하지 않는다. Linux .NET/Chromium 검증과 실제 Windows/WebView2·물리 기기·전체 UI 검증은 구분하고 초기 빈 화면 원인은 미확정으로 유지한다.
