# retained 문맥·native 본문 공동 저장 검증

동결 runtime `c5dbf1cbcd7a5dcf7cd0bc70fbb3cc137a950e7c`의 [한 원본 사용자 흐름](V666_RETAINED_BODY_GROUP.md)을 최종 **신규 41단계·재사용0·실패0**으로 검증했다. 개발 검사는 최종 통과 수에 합산하지 않는다.

- LF/CRLF 격리 checkout·seed restore·Release/MCP·빈 캐시 엔진 및 기존 공통 검사.
- retained root C#와 일반 C#의 두 단일 계획·공동 후보·순서 독립성, 원래 출력/caller identity와 source/hash/경로·별칭·정확한 local을 검증했다.
- 원래 상세창·C# 편집·출력/caller 확인·취소·Undo/Redo·한 Save·실패/재시도·cold·독립 창·프로젝트 경계와 응답 유실/조회 복원을 검사했다.
- 원래 version3 plan/read scope를 설명·함수 표시·후속 명시 본문 Save와 늦은 입력/두 번째 Save까지 유지했다. 독립 read 누락·helper/alias 변경·출력 해제·caller 재연결·member/receipt 변조는 거절한다.
- Save 전 caller와 Review 뒤 graph·선택 node·독립 helper 변경은 전체 적용을 막고 입력·원본·checkpoint를 보존한다. 정확한 복원 후 새 Review/Confirm으로 두 직접 작성 본문을 실행40→20으로 검증했다. 독립 code/helper bytes·mtime와 graph bytes·entry·배치·locals/alias를 유지했다.
- 기존 whole/native와 guard·등록 helper·실제 retained 고급 ABI 변경·단일 whole 전환은 별도 회귀다. 새 교차 package의 정상 UI·전체 ZIP 복원/무결성·응답 유실·늦은 입력·독립 창·실패 수명을 검사했다.

제품 변경은 두 파일이다. WholeBodies는 이미 있는 원래 retained output/caller 계획을 계약 불변 identity에 한해 허용하고 기존 단일 closure를 완전한 원본에서 검증한다. Retained는 원래 root/output/binding 검증을 모두 수행하고, 공개/native/출력/입력 계약이 같은 source-only 편집에서 유일한 차이가 추가된 null output exit일 때 원래 graph를 보존한다. 실제 ABI·writer 변경 처리와 독립 코드의 의미를 재작성하지 않는다. 기존 version3 `nativeBodyContexts`·readGuards·후보 검증·SlotBatch·CreationOwners·Review/Confirm·최종 CAS와 권한을 그대로 재사용한다. 새 문법/receipt version/권한·자동 source 변환은 없다. C# 생성·authored UI·원래 단일 Contracts·override·정보별 struct/종류 enum/모듈 interface·명시 async 전환 전 sync caller 오류는 byte 동일한 기존 경로다.

개발 18회와 1개 실패 기록을 보존했다. caller 검사에서 body plan과 지역 이름이 겹친 컴파일 오류를 `callerPlan`으로 고쳤고 재빌드 후 통과했다. API fixture의 finally 들여쓰기는 실행 전에 바로잡았다. 게시본의 단일 retained 후보가 빈 exits에 return:null을 추가하는 증거를 따로 남기고, 원래 검증 후 정확한 graph 보존으로 수정했다. 이후 최종 41단계를 전부 새로 수행했다.

직전 정상 package `a2a13d272436be9aac4f14d9eb053773765fd9fe`를 전체 파일/hash 검증 후 별도 임시 위치에 추출했다. 그 원래 UI에서 각 단일 계획은 유효하나 retained/native 공동 Save가 거절되고 입력/원본을 보존함을 새로 재현했다. 그 reader가 새 retained pending scope를 거절하는 것도 확인했다. 이 진단은 개발 증거이며 최종 41에 재사용하지 않는다. 같은 게시 세대의 authoring/runtime을 사용하고 자동 migration/downgrade를 하지 않는다. 기존 구 Reference parser 제약은 유지한다.

미등록 잔존 `.csbody`는 새 관측/감시 대상으로 주장하지 않고 byte 보존만 별도로 검사했다. Linux 실제 엔진/portable 실행과 Chromium 자동화는 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI 검증과 다르다. 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | c5dbf1cbcd7a5dcf7cd0bc70fbb3cc137a950e7c | 25507af5298d28f864459a0a24280bcd647271b9a05d0f96d871dcc38f95bc8f | 54129186 |
| rollback | a2a13d272436be9aac4f14d9eb053773765fd9fe | 6f203b0abf39ed151f7b51897a588e686568a909a31d8ce6d10fb8ee4349440f | 54128171 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/98f19662d81f495a8dedcc539fb606fa.json` · evidence SHA256 `8da1d699ac7bae05a2be0337b22884792569b1b678a277f315b0f9abd857c4bf`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/cabd4245c6dc46529e6c8939513feb37.json` · evidence SHA256 `4e8d30efb811f238df812c9fa2f41d962c8d335ad0566559e67643a41c16437d`.
두 package와 두 실행 증거 SHA를 재확인했다. 기존 latest/직전 정상 rollback 교대 및 이번 등록 소유 임시물만 정리했으며 원본 checkout·기존 보관·과거 증거를 보존했다. 디스크 여유 24488501248bytes(22.81GiB)다.

이번 retained root의 source-only 공동 저장 흐름을 닫는다. 남은 유한 갈래는 private/독립 node 자체 계획 결합과 실제 계약 변경 callee/import·등록 외부 관측 결합이다. 가능한 타입/문맥 조합을 새 의무로 늘리지 않고 해당 전체 완료로 과장하지 않는다. main은 사용자 검토/merge에 남긴다.
