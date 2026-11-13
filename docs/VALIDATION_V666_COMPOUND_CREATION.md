# 새 복합 속성·native 계약 공동 저장 검증

제품 동결 `d3ac2d17423741d5b13bc514e40736bf221c3219`의 [지원 범위](V666_COMPOUND_CREATION.md)를 최종 **신규 44단계·재사용0·실패0**으로 검증했다. 개발 검사와 합산하지 않는다.

- 게시 a3e36fc4의 새 복합 속성 생성과 두 native 계약·본문 그룹이 각각 유효하지만 결합만 거절되는 것을 metadata와 원래 UI에서 재현했다. 다섯 입력·원본·checkpoint를 보존했다.
- 수정 후 기존 Add/타입 선택기로 명시한 새 단일 compound 필드의 ID·표시명·Count/Note 값과 두 native out/return·본문·공유 caller 대응·정보 설명·아이콘을 한 Save로 저장했다. Count 9223372036854775804와 기존 정확한 정수·필드/참조 ID·named 정의·선택 밖 C#을 보존했다. Linux 실행40 및 실제 IInvoke double1.75/out double1.25·long35를 확인했다.
- 행 순서를 뒤집어도 완전한 owner 필드/기본값/표시 의미와 native/caller bytes는 같다. 새로 작성하는 metadata의 삽입 순서는 명시 행 순서를 따른다. 중복 ID·이름·잘못된 종류/배열수·stale/없는/변조/미선언 타입 증거·부적합 기본값·정수 overflow·값 예산 초과·불완전 native 계획은 적용 없이 거절했다.
- 원래 full validator로 전체 명시 owner 계획을 재생했다. 기존 version3 nativeBodyOwnerEdits/nativeBodyOwnerReads와 readGuards는 후속 정보 설명·함수 표시 저장과 cold에서도 정확히 유지했다. 계획·관측 누락/추가/경로/hash/증거 변조를 거절했다.
- Review 뒤 helper 선언/본문·caller graph·native 선언/본문·선택 Leaf2·부모/자식 정보·참조 대상의 변경은 Confirm 전체 거절이었다. 정확한 복원과 cold 뒤 새 Review/Confirm이 통과했다. 기존 등록 의존성의 같은 구조 타입을 프로젝트 밖 private fixture에서 선택한 경우도 기존 최종 읽기 lease를 확인했다. 실제 외부 원본 쓰기나 새 production 등록/권한은 없다.
- 새 필드 타입 선택 직후의 Undo/Redo·포커스와 이후 멤버 편집 뒤 stale 속성/함수 history 거절을 구별했다. 정상/독립 창·취소·실패/재시도·응답/조회 유실·저장 전후 cold·경합·늦은 입력/후속 Save·프로젝트 A/B/A를 검사했다. 기존 필드 타입·receipt, typed 값 receipt, scalar 생성과 사용처 보호도 회귀 검증했다.
- LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet 새 restore·Release/MCP·빈 cache Linux 엔진, 새 Windows 교차 package·구조/무결성·packaged UI, ZIP 전체 추출본의 유실/늦은 입력/독립 창과 실패/반복 정리 수명을 새로 검사했다.

개발 기록 31단계 중 실패 2건은 검사 가정 문제였다. 첫 실패는 신규 metadata의 삽입 위치까지 owner 원문 동일성을 요구한 비교였고, 두 번째는 나중 값 입력으로 stale이 된 property snapshot에 멤버 Undo를 기대한 검사였다. 실제 의미/native bytes 및 원래 key handler·보존 입력을 대조한 증거, 실패 당시 검사 파일과 요청/로그를 보관했다. 각 기대값 수정에는 제품 변경이 없었다. 수정 후 정상·거절·UI·수명 검사를 통과했고, 최종 44단계는 동결한 최종 제품·검사에서 전부 새로 수행했다.

제품 변경은 생성 행 분류와 기존 owner 계획 포착의2개 파일이다. InformationDefinitions/FieldTypes·값/사용처, ApplySlots·기존 CommitPlan/Confirm/CAS, 64행/2..8 계획과 Review/read 예산·공개 override·소유권/권한·authored layout은 바꾸지 않았다. receipt 필드/버전·저장 문법을 추가하거나 이전 scalar/typed 값 receipt를 자동 승격하지 않았다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류 정책을 유지했다.

구 Reference reader 자료는 기존 증거의 해시 확인이며 신규 단계에 포함하지 않는다. 같은 게시 세대 authoring/runtime을 사용하며 이 새 조합의 구 reader downgrade는 보장하지 않는다. Linux 엔진·Chromium 자동화와 실제 Windows/WebView2·기기·OS IME·GPU/audio·전체 UI 전수는 구분한다. 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | d3ac2d17423741d5b13bc514e40736bf221c3219 | b5946a7ad539aa2844775b626010654cc9130b6364ecc7b0a6c8e83ad5b44e51 | 54107021 |
| rollback | 4c5403f148b8dde081f1c014987daae513cddfe7 | e02718ffb7d25ea20d95d2f271bc3b5780dd573c039ca951e78239a0ce9dd7b7 | 54106271 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/9e9ac69a611640bbb978e2b07486c218.json` · evidence SHA256 `2ebe6a9607fcc728631da11288c91c283e62a47425967b0de69f15f97e7365a9`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/18c7b5a8cd2c4f02ab9cfbf486389f3c.json` · evidence SHA256 `29732c4de6c0570e59391fa07a384c48f5fe28c1d6cd2c7eefb0301d6bf1e182`.
두 package와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대와 이번 등록 소유 임시물 정리만 수행했으며 원본 checkout·과거 증거·비관리 자료는 보존했다. 여유 24610430976bytes(22.92GiB)다.

이번 기존 타입 선택의 새 단일 복합 필드 생성은 닫는다. 새 named 정의·자체 소유 자식 생성/구조 결합, opaque/private 명시 C# 계획, 소유 callee·기존 import 변경 그룹과 등록 외부 읽기 원본 결합은 별도 잔여다. 타입/문맥의 임의 조합을 새 의무로 늘리지 않고 M11/M12/M4를 회귀 없이 다시 열지 않는다. 외부 쓰기·암묵적 값/C# 변환·grant/credential·과금·migration·main 변경은 없다.
