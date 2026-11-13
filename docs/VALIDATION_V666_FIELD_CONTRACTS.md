# 기존 필드 정의·native 계약 공동 저장 검증

제품 동결 `4c5403f148b8dde081f1c014987daae513cddfe7`의 [지원 범위](V666_FIELD_CONTRACTS.md)를 최종 **신규 43단계·재사용0·실패0**으로 검증했다. 개발 단계와 최종 단계를 합산하지 않는다.

- 게시3e70b85a에서 복합 Tree Leaf→Leaf2 및 참조 Peer LeafChild→Leaf의 기존 선택과 두 native/header 묶음이 각각 유효하지만 결합만 거절되는 것을 metadata와 원래 UI에서 재현했다. 당시6개 입력·원본·checkpoint를 보존했다.
- 수정 후 두 명시 native out/return·본문·공유 caller 대응과 정보 설명·아이콘, Tree의 새 Note 값 명시 입력 및 Peer의 타입 선택을7개 입력의 한 Save로 저장했다. 필드 ID·정확한64비트 Count/Power·기존 참조 ID와 비선택 C#을 유지했다. Linux 실행40 및 IInvoke double1.75/out double1.25·long35를 확인했다.
- 변경한 필드의 타입·기본값 및 행 순서의 동일성, owner 행 추가 전후의 native/caller 후보 bytes를 검사했다. stale/foreign schema/hash/contract·없는/변조된/미선언 타입 증거·잘못된 종류/배열수·중첩/중복 정의·부적합 기본값·불완전 native 계획을 전부 거절했다.
- 같은 원래 validator로 정의와 값을 함께 재생했다. version3 receipt의 선택적 nativeBodyOwnerEdits/nativeBodyOwnerReads와 기존 readGuards는 후속 정보 설명·함수 표시 저장과 cold에서도 정확히 유지했다. 누락·추가·경로·hash·계획 변조는 적용 없이 거절했다.
- Review 뒤 helper 선언/본문·caller graph·native 선언/본문·선택 타입 Leaf2·부모/자식 타입·참조 대상의 변경은 Confirm 전체 거절이었다. 정확한 복원과 cold 뒤 새 Review/Confirm이 통과했다. 기존 등록 의존성의 같은 구조 타입을 프로젝트 밖 private fixture에 두고 선택했을 때도 같은 최종 읽기 lease를 확인했다. 실제 외부 원본을 쓰거나 새 production 등록/권한을 부여하지 않았다.
- 원래 타입 선택·Undo/Redo/포커스와 거절된 함수 history, 기본/독립 창·취소·실패/재시도·응답/조회 유실 복구·미저장/저장 cold·원본 경합·늦은 입력/후속 Save·프로젝트 A/B/A를 검사했다. 기존 scalar·typed 값 receipt와 사용처 보호를 회귀 검증했다.
- LF/CRLF 독립 no-hardlinks checkout, 격리 HOME/NuGet 새 restore·Release/MCP·빈 cache의 Linux 엔진을 검사했다. 새 Windows 교차 package·구조/무결성, packaged UI와 ZIP 전체 추출본의 UI/유실/늦은 입력 및 실패/반복 정리 수명을 새로 확인했다.

개발 기록 29단계의 실패는 0건이다.6개 입력의 기준본 재현·첫 수정 검증과, 기존 타입 선택 UI가 제공하는 새 멤버 값의 명시 입력을 포함한 최종7개 입력의 검증은 각 입력/해시/로그로 구별해 보관했다. 최종 43단계는 동결한 최종 제품·검사에서 모두 새로 수행했다.

제품 변경은 분류·원래 owner 계획/읽기 증거 보관의3개 파일이다. 전체 InformationDefinitions/FieldTypes·값/사용처 검증,64행/2..8 native 계획 제한, 기존 CommitPlan/CAS·공개 override·소유권/권한·authored layout은 그대로다. 이전 scalar/typed 값 receipt를 자동 승격하거나 버전을 바꾸지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류 정책을 유지했다. 새 정의/소유 자식 생성·참조 소유자 편집·암묵적 값/C# 변환·grant/credential·과금·migration·main 변경은 없다.

구 Reference reader 자료는 해시 확인한 기존 증거이며 신규 단계에 포함하지 않는다. 새 조합의 구 reader downgrade는 보장하지 않는다. Linux 엔진·Chromium 자동화와 실제 Windows/WebView2·기기·OS IME·GPU/audio·전체 UI 전수를 구별한다. 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 4c5403f148b8dde081f1c014987daae513cddfe7 | e02718ffb7d25ea20d95d2f271bc3b5780dd573c039ca951e78239a0ce9dd7b7 | 54106271 |
| rollback | b6149e32569dbcf200ac55fd575c8e141fff4477 | 53524bb4fe41e89be7c68503bdda8a62268d6b8d1c29c1b1a27dab0165313e11 | 54106801 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/6e46744254f549c094d2832cca00b32c.json` · evidence SHA256 `8a331430940b6b56c390b8b44d95268853fd9d14c2371ca195010d2cedd74663`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/ae48a4bc57bc45c3a822011f57f13b20.json` · evidence SHA256 `279f5bc40b913311c07e52dff4185cc8d99ff2beac4bea28bcca974304675987`.
두 package와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대와 이번 등록 소유 임시물 정리만 적용했고 원래 checkout·과거 증거·비관리 자료는 보존했다. 여유 24640208896bytes(22.95GiB)다.

남은 다른 복합 구조/새 정의·소유 자식 결합, opaque/private 명시 C# 계획, 선택 소유 callee·기존 import 변경 그룹과 등록 외부 읽기 원본 결합은 별도다. 타입/문맥의 임의 조합을 새 의무로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다.
