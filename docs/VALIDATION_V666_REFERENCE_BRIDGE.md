# 정보 인스턴스 bridge 검증

제품 동결은 `bf1479470f6f8beca48e4a9fd08d9dd85841278d`다. [지원 경계](V666_REFERENCE_BRIDGE.md)의 독립 최종 검증은
**신규 42단계·재사용 0·실패 0**이다. LF/CRLF checkout의 Release·MCP·실제 편집기,
native/API/UI와 기존 일반/ref/reference·함수·compound·모듈 회귀, 새 Windows 교차 패키지와
전체 압축 복원 및 실패 수명 검사가 포함된다. 기존 검사 코드를 다시 실행한 것과 과거
통과 증거 재사용은 구분한다. 개발 검사를 이 최종 단계에 합산하지 않는다.

실제 CLR에서 정보 계약과 호출자 소유 ObjectModel v1/v2를 연결하고 동일한 handle과 실제
owner를 반환하는지 확인했다. 원래 StrongBox·배열·reference·함수 handle, 별도 인스턴스,
같은 origin의 상속 필드와 Blueprint return/out 연결, GC 보유 및 self-cycle 해제를 검증했다.
값 입력100과 별도로 제공한 실제 receiver30에서 checked Set 후 같은 셀/값31을 확인했다.
메타데이터/BindReference는 필드 값·getter·provider를 읽거나 실행하지 않는다. unset 값이나
비지원 필드를 기본값으로 만들지 않으며, 기존 정보 struct의 reference 필드 거절을 유지한다.

다른 schema·ID/JSON/snapshot·알 수 없는 instance format·잘못된 profile/hash·중복 필드와
추가/삭제/타입 변경 계약은 원래 storage/alias를 보존하며 거절한다. exact 원문 복원 후
동일 계약 연결이 복구된다. 등록된 외부 정보는 기존 명시 dependency 없이는 거절하고,
외부 타입 변경과 오래된 실제 인스턴스의 불일치도 거절한다. 외부 source/pack은 보존한다.
계약은 명시적 버전 snapshot이며 runtime에서 현재 파일을 조회하거나 기존 alias를 취소하지
않는다. owner 출력은 권한 부여가 아니며 객체 ID에서 인스턴스를 찾는 registry도 없다.

기존 460px 직접 소유 본문 UI로 취소·Undo/Redo·cold 복원·저장 실패 후 입력/원문 보존과
재시도·중복 Save 비활성·실제 apply/settled 응답을 가린 재시작 복구·늦은 입력 및 두 번째
Save를 검증했다. 이미 관찰한 정보 타입과 import receipt의 Save 전·Review 후 변경은
전체 거절하고 정확 복원·새 Review/Confirm 후 실행했다. 별도 회귀로 로컬/등록 외부의
property source CAS와 누락/변조 receipt 거절을 다시 실행했다. C# 문자열 안의 schema ID를
자동 추론하는 source dependency나 새 권한은 만들지 않았다. 원래 provider 생성/호출
수명, public/override 계약, UI 배치, 부모/외부 source의 쓰기 경계와 final CAS를 유지한다.

개발은 24개 실행 중 1개 실패를 포함한다.
복사된 source의 보존된 timestamp가 기존 build보다 오래되어 incremental build가 갱신을
생략한 개발 workspace 문제였다. source SHA 일치를 확인하고 --no-incremental로 재빌드해
통과했다. 이 실패 때문에 제품 의미를 바꾸지 않았다. 후속 최종 source sync·native/API와
회귀가 통과했으며 실패 로그·원본·화면·hash와 최종 입력을 보관했다. 새 패키지와 전체
복원에서도 native/API/UI·저장 실패·응답 유실·늦은 입력 및 등록 타입 CAS를 새로 실행했다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/48ab29bf183644c1b21c7f2ca2dff845.json`
- 개발 증거 ZIP SHA256: `dc5d180036fb614a6ec22833721346b9de610bb6303e190165e2c584f54364e1`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/a4c0214b3caa4d978aa7f59287f83c96.json`
- 최종 증거 ZIP SHA256: `944a708c7208f5d5965e2fb6e82b81d2a1e6284c9be1cfdae4a18efa8caa8b35`
- latest runtime: `bf1479470f6f8beca48e4a9fd08d9dd85841278d`
- latest ZIP SHA256: `89088154ea553abe5dc116e96548cbb0a62bde0ff8d37faf463f69b22b0b0dd4` (54035239bytes)
- rollback runtime: `354716abd90701e34c7b89ec235be82691ed7591`
- rollback ZIP SHA256: `9f8adbd8ea25cf5f87bd8b59d345321679576534924a1b3dee3ed49882c553e4` (54031183bytes)

store는 `/workspace/artifacts/v536-verification-managed/packages`다. latest/rollback과 증거 무결성을 확인하고 이번 소유 임시 workspace만
정리했다. 보관 후 여유 공간은 25442963456bytes (23.70GiB)다. main과 원래 checkout
b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee를 보존하며 work/current만 게시한다.

이것은 opaque object bridge다. 정보별 typed reference ABI/struct reference 필드 및 타입
선택 연결은 같은 고정9행의 유한 잔여다. 새 API를 지원하지 않는 옛 authoring 도구에는
업데이트가 필요하며 기존 저장 형식이나 object/concept descriptor/hash는 변경하지 않는다.
M11/M12/M4는 회귀 근거 없이 다시 열지 않는다. Linux/.NET/Chromium 자동화 결과이며
실제 Windows 실행·물리 기기·전체 UI·모든 구 reader는 미검증이다. 초기 빈 화면의 원인은
미확정이다.
