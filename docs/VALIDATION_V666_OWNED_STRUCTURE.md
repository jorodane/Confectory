# 기존 소유 자식 구조·native 계약 공동 저장 검증

제품 동결 `6428374cc60109e17fe2eff04c66eb7d3c7b8209`의 [지원 범위](V666_OWNED_STRUCTURE.md)를 최종 **신규 48단계·재사용0·실패0**으로 검증했다. 개발 검사와 합산하지 않는다.

- 게시 a9576959에서 기존 소유 자식 편집과 두 native 계약·본문 그룹이 각각 유효하지만 결합만 거절되는 것을 metadata와 원래 UI에서 재현했다. 다섯 입력·원본·checkpoint를 보존했다. raw body/graph가 선언 registry에 들어가는 재현과 선언만 overlay한 대조를 보관했다.
- 원래 정보 창에서 기존 Stats.Power 표시·아이콘, Inner.Title 표시·기본값과 새 bool 멤버를 두 native out/return·직접 작성한 본문·공유 caller 대응 및 정보 설명·아이콘과 한 Save로 저장했다. 자식 두 source ID/경로·CRLF 한글/emoji 주석·명명 정의·원래 등록·선택 밖 C#과 정확한 64비트 값을 보존했다. Linux 실행40 및 실제 IInvoke double1.75/out double1.25·long35를 확인했다.
- 행 순서를 바꿔도 전체 owner 의미와 모든 자식/native/caller bytes가 같다. 변조된 owner/schema/contract/hash·누락/추가/stale sources·중복·잘못된 값/배열수·overflow·일반 named 소유권 주장·새 root/child 생성·전환·불완전 native/다른 body 계획을 적용 없이 거절했다.
- 저장 응답 중 입력한 자식 이름과 long9223372036854775803을 별도 입력으로 보존하고 cold 뒤 명시 Save했다. 같은 필드 ID·타입·계층의 값/표시만 원래 full validator로 다시 확인했다. 캡처된 원래 schema hash·자식 sources·readGuards/nativeBodyOwnerReads는 그대로 유지했다. peer 변경·stale 기준/출처·캡처 밖 필드/타입/계층·타입 proof·잘못된 값은 거절했다. 변경 없는 형제는 원래 Review/read 멤버로 남지만 dirty draft나 물리 쓰기를 만들지 않았다.
- receipt의 계획·관측·source member·경로/hash/소유 identity 변조를 거절했다. Review 뒤 helper 선언/본문·caller graph·native 선언/본문·기존 Leaf2·부모/자식 정보·참조 대상과 두 소유 자식 파일 등 11개 source 변경은 Confirm 전체 거절이었다. 정확한 복원과 cold 뒤 새 Review/Confirm은 통과했다.
- 정상/독립 창·취소·Undo/Redo·실패/재시도·응답/조회 유실·cold·경합·늦은 헤더와 자식 입력·후속 Save·프로젝트 A/B/A를 검사했다. 기존 standalone 소유 정의·새 compound 생성·field/typed-value/scalar receipt와 사용처 보호를 회귀 검증했다.
- LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet 새 restore·Release/MCP·빈 cache Linux 엔진, 새 Windows 교차 package·구조/무결성·packaged UI, ZIP 전체 추출본의 응답 유실/늦은 자식 입력·후속 Save/독립 창과 실패·반복 정리 수명을 새로 검사했다.

개발 기록 34단계에는 실패 9건을 보존했다. 3건은 결합 거절/후속 저장 거절과 읽기 집합 비교의 제품 결함 재현·진단이고, 5건은 검사 viewport·bool 입력 방식·cold 창 재진입·후속 receipt의 선언 행 및 변경 없는 Review/read 멤버 가정 문제다. 1건은 후속 수정의 C# 지역변수 이름 충돌(CS0136)로 실행 전 빌드 실패였다. 실패 당시 검사·요청·로그와 중간 제품 hash를 보관했다. 수정 후 목표 검사를 통과했고 최종 48단계는 동결한 제품·검사에서 전부 새로 수행했다.

제품 변경은 3개 authoring 파일의 원래 소유 행 분류·선언 registry overlay·owner 계획/읽기 검증이다. InformationDefinitions/FieldTypes·값/사용처·marker/독점 사용, ApplySlots·CommitPlan/Confirm/CAS·권한·authored UI·공개 override·C# 생성 계약은 바꾸지 않았다. version3 receipt의 기존 필드를 사용하며 이전 receipt를 자동 승격하지 않는다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

구 Reference reader 자료는 기존 증거의 해시 확인이며 신규 단계에 포함하지 않는다. 같은 게시 세대 authoring/runtime을 사용하며 구 reader downgrade는 보장하지 않는다. Linux 엔진·Chromium 자동화와 실제 Windows/WebView2·기기·OS IME·GPU/audio·전체 UI 전수는 구분한다. 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | 6428374cc60109e17fe2eff04c66eb7d3c7b8209 | f82df61c6de9022c58d91e31cf1b729637054eda192f914db395294c198b65fd | 54112293 |
| rollback | d3ac2d17423741d5b13bc514e40736bf221c3219 | b5946a7ad539aa2844775b626010654cc9130b6364ecc7b0a6c8e83ad5b44e51 | 54107021 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/b61b9f03caee4489b53e99dd37da9d33.json` · evidence SHA256 `bccf8bc1e7e16cb192a82c122c2b83429ccbdb6a1bf462e166f64fd7d1e6d444`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/da9dfc196cdc4fb3b4bdb8a9befb6ab1.json` · evidence SHA256 `6a04197294315f1a6105043e2bcbb23289224dac53415c6382803ae4aa10ae2b`.
두 package와 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대와 이번 등록 소유 임시물 정리만 수행했다. 원본 checkout·과거 증거·비관리 자료를 보존했다. 디스크 여유 24578535424bytes(22.89GiB)다.

이번 기존 소유 자식 구조·함수 공동 저장 단위는 닫는다. 새 자식 생성/등록·루트 전환·새 named 정의 결합, opaque/private 명시 계획, 소유 callee·기존 import와 등록 외부 원본 관측 결합은 원래 고정 잔여다. 임의 타입/문맥 조합으로 늘리거나 M11/M12/M4를 회귀 없이 다시 열지 않는다. 외부 쓰기·암묵적 값/C# 변환·grant/credential·과금·migration·main 변경은 없다.
