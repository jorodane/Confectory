# 정보별 native 참조 검증

제품 동결은 `0437c3911d2d2f740199c3e2b921120606c9775b`다. [지원 경계](V666_TYPED_REFERENCES.md)의 최종 독립 검증은
**신규 49단계·재사용 0·실패 0**이다. LF/CRLF의 Release·MCP·실제 편집기/native/API/UI,
기존 opaque bridge·일반/ref/reference·함수/compound/module 회귀, 새 Windows 교차 패키지와
구조/무결성 검사·전체 압축 복원 및 실패 수명 검사가 포함된다. 기존 검사 코드의 신규
실행과 과거 통과 증거 재사용을 구분한다. 개발 단계는 최종 단계에 합산하지 않는다.

실제 CLR에서 정보별 readonly 참조 struct의 명시 Bind, 원래 receiver/owner·StrongBox·
배열·함수 handle 동일성, native 입력/반환/out과 참조 필드, 값 필드의 복사, GC 보유/해제를
검증했다. 값 입력100/200과 실제 객체10/21을 구분한 두 등록 pack의 상호 참조도 실제 DLL로
연결해 실행31을 확인했다. 양방향 dependency가 빠지면 거절하며 외부 source/pack은 그대로다.
다른 정보 ID의 대입, 잘못된/변경된 binding 계약, 실제 inline 값 순환을 거절하고 정확한
source 복원으로 원래 artifact/실행을 복구했다. 기본 unbound carrier는 객체를 만들지 않는다.
조회/binding은 getter·값·provider를 실행하거나 ID/$ref/snapshot을 실제 객체로 바꾸지 않는다.

기존 460px 카드/420px 상세창에서 정보 값과 참조·참조 배열을 별도로 선택하고 원래 label과
C# 타입 정체성을 구분했다. Hidden 등록-only namespace와 구 enum 보호, 선언/관측 source
proof를 유지한다. 본문 편집과 새 함수 생성의 정상/취소/Undo·Redo·cold 복원·저장 실패 후
입력 보존/재시도·중복 Save 비활성·실제 apply/receipt 응답 유실·늦은 입력/두 번째 Save를
개발에서 실행했다. 최종 독립 코드로 LF/CRLF 및 패키지/전체 복원에서 해당 본문·선택·실패
경로를 새로 실행했다. 원문/외부 source와 public/override 계약·UI 배치·권한은 유지한다.

처음 Confirm 전 본문 없는 생성 함수의 이름 후속 저장에서 빈 original을 native 원문으로
파싱하던 실패를 재현했다. 정확한 missing baseline·본문 없는 원래 생성 그룹·같은 계약만
native 본문 파싱 대상에서 제외하고 기존 타입 proof/read scope는 유지한다. 변조 baseline·
계약 변경·본문 포함 그룹은 거절하며 draft를 원문으로 채택하지 않는다. 로컬/등록 source의
Save 전·Review 후 변경, 누락/변조 proof 및 final CAS 거절과 exact 복원·새 Review/Confirm을
확인했다. 기존 opaque descriptor와 hash, reference 포함 live compound의 안전한 거절도
유지했다. 새 타입/field profile을 모르는 구 parser/authoring/accessor는 지원 범위 밖이며
기존 저장 format이나 원문을 자동 migration하지 않는다.

개발은 44개 실행 중 9개 실패를 포함한다.
import 이름/관측되지 않은 자식 타입/재시작 schema 조회/원래 본문 문자열은 fixture 문제였다.
계획기의 generated-reference→원래 schema 연결, 변경 JS 세 파일의 canonical manifest,
본문 준비의 nested 참조 선택 조회와 위 빈 original 분류는 제품 연결 누락으로 수정했다.
일시적 starting 뒤 같은 환경의 작업 트리·프로세스·로그/입력 SHA를 확인했으며 UI 시간
초과는 nested 조회 누락으로 별도 재현했다. 진단용 복제본의 예외 logging만 추가했다가
원본 SHA로 복원하고 정상 engine을 재생성했다. 진단 binary는 완료/패키지 근거가 아니다.
실패 로그·원문·화면·최종 source와 hash를 보관하고 영향받은 검사를 다시 통과시켰다.

- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/01d0c0479a5b49fbadc9d37a88b289d9.json`
- 개발 증거 SHA256: `cdcab4e461d319f393c8f69ea226c8c267eed7dad6fccd92e965b22ed8691f2d`
- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/8b9c0d1cd06b426bb3c90114a2663c47.json`
- 최종 증거 SHA256: `534a0e1f1ae98c9bad48bdee0042ec24ec5f9b99d27fd839e084bd545301982f`
- latest runtime: `0437c3911d2d2f740199c3e2b921120606c9775b`
- latest ZIP SHA256: `768084e39197be3b9c8981c3a933e01da137a122d9cec3adb0749d8930adec84` (54060948bytes)
- rollback runtime: `bf1479470f6f8beca48e4a9fd08d9dd85841278d`
- rollback ZIP SHA256: `89088154ea553abe5dc116e96548cbb0a62bde0ff8d37faf463f69b22b0b0dd4` (54035239bytes)

store는 `/workspace/artifacts/v536-verification-managed/packages`다. 승인된 latest/정상 rollback 두 세대의 원자 교대와 이번 소유 임시물
정리만 적용했다. 개발/최종 증거 ZIP과 현재 두 보관본을 SHA로 확인했다. 교대된 세 번째
관리 패키지까지 보관한다고 주장하지 않는다. 과거 비관리 자료와 원래 checkout/main은
건드리지 않았다. 보관 후 여유는 25427365888bytes (23.68GiB)다.

이 단위는 생성 가능한 정보의 명시적 ObjectModel typed reference ABI·단일/배열 reference
필드·같은 source proof를 사용하는 타입 선택이다. custom 객체 자동 binding·ID 조회·
live compound profile 자동 승격·저장 data migration을 새 필수 잔여로 만들지 않는다.
M11/M12/M4를 회귀 근거 없이 다시 열지 않으며 전체 I5-6/다른 정보 속성/모든 문맥/전체 UI
완료로 합산하지 않는다. Linux/.NET/Chromium 자동화이며 실제 Windows 실행·물리 기기·
모든 구 reader는 미검증이고 초기 빈 화면의 원인은 미확정이다.
