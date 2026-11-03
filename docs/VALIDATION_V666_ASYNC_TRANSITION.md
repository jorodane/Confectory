# v666 M4 명시 전환 UI 최종 검증

최종 제품·검사 소스는 `73a83c820b48cf265c0a465c801a4a15318495f7`이다. 최종 문서 기록 뒤에도 src/targets/packs/examples/tests/tools 트리와 이 commit을 비교한다. `tools/verify_desktop.py --suite async-transition`의 신규 LF 16·CRLF 15·새 패키지/전체 복원/실패 수명관리 9, 총 **40단계**가 모두 통과했다. 최종 증거 재사용은 0이다. 개발 중 진단/수정 검사는 이 수치에 합하지 않는다.

## 실제 확인

- 독립 checkout·독립 캐시·빈 엔진 캐시로 Release/MCP/실제 편집기를 빌드하고 줄바꿈과 clean 상태를 확인했다.
- 각 LF/CRLF에서 async/switch 런타임 18개, 영수증/주 receipt/멤버/원본/관측 변조 거절 및 전환 API를 실행했다. 기존 enum C# 편집·완료 continuation·동기 호출자 오류·명시 호출자 전환·완전 Review·Review 뒤 원본 경합의 최종 CAS와 실제 Task 실행을 확인했다.
- 원본 메뉴·시계/완료 포트·Undo/Redo·cold·Save·Review 취소/Confirm, 저장 권한 실패·다른 호출자 원문 충돌·응답 유실·늦은 입력을 검사했다. 저장 후 C# 선언 표시와 취소의 원문 보존도 확인했다. M12 등록 외부 관측 및 비void 계약 API 회귀를 새로 실행했다.
- 새 Windows 교차 패키지와 전체 압축 복원본에서 실제 편집기 UI·Task 출력/완료/결과/continuation 순서, 반복·원래 Task 예외·자식 중단/재시도·동기 호출자 오류를 실행했다. 복원본의 늦은 응답과 저장 실패, 패키지 실패/예외/재시작 수명관리도 확인했다. Linux 실행이며 실제 Windows/모바일 실행 검증이 아니다.

## 지속 보관과 공간

- 실행 기록: `/workspace/artifacts/v536-verification-managed/runs/c038b63afece4084a8cd6e6a619f15f3.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/c038b63afece4084a8cd6e6a619f15f3.zip`
- 증거 SHA-256: `978cc368ee63034f75db1b8c03e0a7b441377e0451836197a2520cb4abab6055`
- 최신 package source: `73a83c820b48cf265c0a465c801a4a15318495f7`, archive `b757b872c59b18eeeb405aa6c3fa8f5bffdf76917cb0e9edc2b8c8881b807a01.zip`, SHA-256 `b757b872c59b18eeeb405aa6c3fa8f5bffdf76917cb0e9edc2b8c8881b807a01`, 51427131 bytes.
- 최신 전체 manifest SHA-256: `c07dac6822aa97547dc64b740897c5205f17303fd144ed8c4faddbb634000380`
- 정상 rollback source: `671d477f104aea37522f21d21f53a3dce46fc189`, archive `df85fbb43ac67533e63198c9484b6dba651d9422912ddcd80bd0128f7390d808.zip`, SHA-256 `df85fbb43ac67533e63198c9484b6dba651d9422912ddcd80bd0128f7390d808`.
- 보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`. 전체 파일 SHA/압축 무결성·전체 복원·실행 후 원자 승격했다. 증거를 지속 보존하고 자식 종료/소유권을 확인한 뒤 이번 실행의 RAM 임시물을 정리했다. 기존 과거 자료는 추가 삭제하지 않았다.
- 작업 시작 여유 1823.06MiB, 검증 종료 여유 1813.70MiB, 작업 순증가 9.37MiB. 최종 실행 자체 순증가 5.18MiB, 각 실행 명령에서 관측한 최소 디스크 여유 1818.81MiB, 관측 최대 cgroup 메모리 4126.43MiB. Git 문서/게시 후 수치는 최종 보고에서 확인한다. 3–6MiB 목표는 보장값이 아니다.

## 실제 남은 범위

[명시 전환 지원과 유한한 M4 잔여](M4_ASYNC_TRANSITION.md)를 따른다. 연결된 완료 포트의 동기 복귀 시 일반 분기 보존과 새/내부 소유·native 문맥의 원문 보존 전환은 남는다. 새 async profile에서 Set 등 기존 보조 편집 UI의 연동은 이번 화면 검사 범위가 아니며, 기존 profile whitelist의 남은 연결을 완료로 표시하지 않는다. 현재 연결 삭제를 강요하는 거절을 영구 UX 정책이나 완료로 바꾸지 않는다. ref 입력·비소유 원본/공개 override 계약 변경의 정상 거절과 구별한다. M11·M12는 닫힌 상태이며 V2–V9·별도 팩/권한 backend·종류 C# 표현/사용 중 항목 처리·전체 UI/실제 기기/Space 전달은 기존 고정 항목이다.

기존 M12 rollback에서 새 async profile을 읽고 실행할 수 있다고 보장하지 않는다. 이번 정상 rollback은 이전 async runtime commit이며 최신 전환 UI와 동일한 편집 기능을 의미하지 않는다. 소스 rollback과 프로젝트/초안 데이터 복구를 구분하고 원본과 최신 보관본을 함께 보존한다.
