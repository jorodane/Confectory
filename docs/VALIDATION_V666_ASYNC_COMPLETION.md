# v666 M4 완료 일반 분기·Set 최종 검증

최종 제품·검사 소스는 `a24e3e294f80adadb97f6cd9bb580fd296f3d069`이다. `--suite async-completion`의 **신규 LF19·CRLF18·새 패키지/전체 복원/실패 수명관리10, 총47단계**가 모두 통과했다. 최종 증거 재사용은 0이다. 앞선 개발 반복 검사는 이 수치에 합하지 않는다. 종료 문서 commit 뒤에도 src/targets/packs/examples/tests/tools 트리를 동결 commit과 비교한다.

## 실제 지원과 검증

- 원본 `blueprintSetAsync`의 동기 복귀 시 완료를 일반 분기로 보존하는 의미를 직접 소유한 기존 ordinary root의 C# Result 동작에 연결했다. literal completion 포트/목적지·기존 Result ID/정수값/주 분기·IO·C# 원문을 보존한다. 분기 표시명과 유효한 C# 이름을 분리하며 같은 완료 ID로 반복 async 전환한다. 동기에서는 C#이 그 Result를 명시 선택할 때만 해당 줄을 실행한다.
- 각 독립 LF/CRLF checkout·캐시에서 async/switch 런타임 18개, 완료 순수 경계 8개, API 5개와 실제 UI 메뉴·순서/표시·Undo/Redo·cold·Save·Review 취소/Confirm·실행을 검사했다. 연결 삭제·변조·중복 포트·부분 Review·Review 뒤 원문 경합·미지원 공개 전환을 거절하고 입력을 보존한다. 저장 실패·호출자 물리 경합·응답 유실·늦은 입력/재조회도 새로 검사했다.
- ordinary async root의 기존 Set 계획/UI 게이트와 완료 연결을 연결했다. 타입 오류 전체 거절, 출력 핀 이름·미완성 문자열 Undo 보존/Redo·원자 Save·cold·Confirm을 확인했다. 실제 실행에서 await 뒤 게시된 out 값을 완료 영역의 Set이 읽고 결과 분기·continuation으로 진행한다. C# 원문·핀/저장소 ID·타입·영역/연결은 유지한다. 기존 async 명시 호출자 전환과 닫힌 M12 등록 관측/비void 실행 API도 새로 회귀 검사했다.
- 새 Windows 교차 패키지에서 완료 UI·Set·Task runtime, 전체 파일 SHA/manifest 압축 복원본에서 늦은 응답·저장 실패·Task runtime을 검사했다. 패키지 실패/예외/재시작의 증거 보존과 소유 임시물 정리도 검사했다. Linux에서 수행했으며 실제 Windows/모바일 실행이나 전체 UI 완료를 뜻하지 않는다. 소형 화면의 포트 projection은 연결했지만 실제 모바일 기기 검사는 하지 않았다.

## 지속 보관과 공간

- 실행 기록: `/workspace/artifacts/v536-verification-managed/runs/4f499020cab74e6fb8fd1b254ed81f2d.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/4f499020cab74e6fb8fd1b254ed81f2d.zip`
- 증거 SHA-256: `4f08be58607adc24065086fcd886b66cfceca7f350a540e3843f3f1ef5b4d391`
- 최신 package source: `a24e3e294f80adadb97f6cd9bb580fd296f3d069`; archive `ce0f0c79a4830128f89c14a6363ec1c30d84707bf87aa88714b2de7e964e2c92.zip`; SHA-256 `ce0f0c79a4830128f89c14a6363ec1c30d84707bf87aa88714b2de7e964e2c92`; 51439457 bytes.
- 최신 전체 manifest SHA-256: `2f0b58869144f416ba57838b88806f4bb02a5a1a7ab0ed8f5e75b9244f8c6428`
- 정상 rollback source: `73a83c820b48cf265c0a465c801a4a15318495f7`; archive `b757b872c59b18eeeb405aa6c3fa8f5bffdf76917cb0e9edc2b8c8881b807a01.zip`; SHA-256 `b757b872c59b18eeeb405aa6c3fa8f5bffdf76917cb0e9edc2b8c8881b807a01`.
- 보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`. 전체 파일/압축 무결성과 전체 복원·실행 뒤 원자 승격했다. 증거를 지속 보존하고 자식 종료·소유권을 확인한 뒤 이번 실행 소유 RAM 임시물만 정리했다. 기존 과거 자료는 추가 삭제하지 않았다.
- 최종 실행 자체 디스크 순증가 5.80MiB, 검증 종료 여유 1803.23MiB. 명령 관측 최소 여유 1808.96MiB, 최대 cgroup 메모리 4403.36MiB. 개발 증거·Git/최종 문서·게시까지 포함한 전체 작업 순증가는 최종 보고에서 별도 확인한다. 3–6MiB 목표는 보장하지 않는다.

## 정확한 잔여와 호환성

[M4 유한한 후속](M4_ASYNC_TRANSITION.md)의 공개 함수/호출자 완료 일반분기 어댑터, Result 없는 next/native/whole-body 원문 보존 어댑터, 새/내부 소유 본문의 전환과 property 보조 편집 연결은 남는다. 이번 지역 Result와 ordinary Set 완료를 새 잔여로 반복하지 않는다. 비소유 원본/override IO/ref/실제 await의 정상 거절과 선택적 legacy 자동 변환은 새 필수 조합이 아니다. M11·M12는 닫힌 상태를 유지한다. 기존 V2–V9, 팩·권한 backend/종류 호환성 결정, 실제 기기·전체 UI·Space 전달은 별도 잔여다.

`completionBranch` metadata와 literal 포트 대응을 이전 빌드가 동일하게 해석한다고 보장하지 않는다. 이전 정상본은 최신 편집 기능과 동일하지 않다. 소스 rollback과 프로젝트/초안 데이터 복구를 구분하고 원본·최신 보관본을 함께 보존한다.
